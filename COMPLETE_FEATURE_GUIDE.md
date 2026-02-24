# AI Wellness Buddy — Complete Feature Guide

> **Version**: 3.0 — Feb 2026  
> Reflects the current six-module agent architecture with password-protected profiles,
> multi-emotion classification, time-weighted distress monitoring, OLS temporal prediction,
> context-aware response generation, severity-based guardian alerts, and a six-tab analytics UI.
>
> Quick links: [README](README.md) · [Setup Guide](DETAILED_SETUP_GUIDE.md) · [Security](SECURITY.md) · [Data Retention](DATA_RETENTION.md)

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [Module 1 — Emotion Analysis Agent](#2-module-1--emotion-analysis-agent)
3. [Module 2 — Distress Monitoring Agent](#3-module-2--distress-monitoring-agent)
4. [Module 3 — Pattern Prediction Agent](#4-module-3--pattern-prediction-agent)
5. [Module 4 — Response Generation Agent](#5-module-4--response-generation-agent)
6. [Module 5 — Guardian Alert Agent](#6-module-5--guardian-alert-agent)
7. [Module 6 — Visualization & UI Agent](#7-module-6--visualization--ui-agent)
8. [User Profile — Full Personal Details](#8-user-profile--full-personal-details)
9. [Password Protection & Security](#9-password-protection--security)
10. [Specialized Support for Women](#10-specialized-support-for-women)
11. [Data Management](#11-data-management)
12. [Configuration Reference](#12-configuration-reference)
13. [Testing & Research Metrics](#13-testing--research-metrics)
14. [Complete Feature Checklist](#14-complete-feature-checklist)

---

## 1. Project Summary

**AI Wellness Buddy** is a privacy-first emotional support application that:

- Builds a full personal profile for each user (name, age, occupation, concerns, guardian contacts)
- Password-protects every profile with SHA-256 hashing and account lockout
- Analyses the emotional tone of every message across **five emotion categories**
- Tracks multi-message trends with a time-weighted sliding window
- Predicts the next emotional state using an OLS temporal model
- Generates personalized, context-aware responses that address the user by name
- Alerts a designated guardian at the right **severity level** with full escalation policy
- Renders a **six-tab analytics dashboard** with live sentiment charts, pie charts, forecast charts, and an alert log

All data is processed and stored **locally only** — zero external API calls.

### Comparison: Before vs. After

| Capability | Old version | Current version |
|---|---|---|
| Emotion classification | positive / negative / neutral bucket | 5 categories: joy, sadness, anxiety, anger, neutral |
| Profile security | None — any profile opened freely | Password-protected with SHA-256, lockout, remove-password |
| Distress monitoring | Simple message count | Time-weighted sliding window + numeric severity score 0–10 |
| Response generation | Same template repeating | 4 variants per emotion category, deduplication, name + occupation context |
| Alert system | Binary on/off | 5 severity levels (INFO→CRITICAL) + escalation + consent + log |
| UI | Single-page chat | 6-tab dashboard: Chat, Trends, Weekly, Risk Prediction, Alerts, Profile |
| Prediction | None | OLS temporal model, MAE/RMSE metrics, 5-step forecast chart |

---

## 2. Module 1 — Emotion Analysis Agent

**File**: `emotion_analyzer.py`

### 2.1 Multi-Label Emotion Classification

Every message is scored across **five emotion categories** using a fusion of:
- Keyword-frequency counting (curated word lists per category)
- TextBlob polarity to weight the scores

| Category | Trigger words (examples) |
|---|---|
| 😢 Sadness | sad, depressed, hopeless, lonely, heartbroken, grief, crying, numb, despair, empty |
| 😰 Anxiety | anxious, worry, stressed, panic, scared, overwhelmed, insomnia, restless, racing thoughts |
| 😠 Anger | angry, furious, frustrated, rage, resentment, bitter, disgusted, fed up |
| 😊 Joy | happy, grateful, excited, wonderful, content, peaceful, relieved, optimistic, love |
| 😐 Neutral | Anything that does not match the above categories |

Keyword counts are scaled by TextBlob polarity (positive polarity boosts Joy; negative boosts Sadness + Anxiety) before normalising to a sum-to-1 distribution.

### 2.2 Full Output Schema

```json
{
  "emotion_scores": {
    "joy":     0.0,
    "sadness": 0.616,
    "anxiety": 0.384,
    "anger":   0.0,
    "neutral": 0.0
  },
  "dominant_emotion": "sadness",
  "severity_score":   7.79,
  "emotion":          "distress",
  "severity":         "high",
  "polarity":         -0.48,
  "subjectivity":     0.72,
  "distress_keywords":  ["hopeless", "can't take it"],
  "abuse_indicators":   [],
  "has_abuse_indicators": false,
  "timestamp": "2026-02-23T20:10:00"
}
```

The `emotion` and `severity` fields are the **legacy buckets** kept for backward compatibility.  
New code should use `dominant_emotion` and `severity_score`.

### 2.3 Severity Score (0–10)

```
severity_score = clamp((-polarity + 1) / 2 × 10 + keyword_bonus, 0, 10)
```

- `polarity` from TextBlob (`-1` = most negative, `+1` = most positive)
- `keyword_bonus` = `0.5 × len(distress_keywords) + 1.0 × len(abuse_keywords)`, capped at 3

Examples:
- Pure joy message → score ≈ 0–2
- Neutral message → score ≈ 4–5
- "I feel hopeless and trapped" → score ≈ 8–9

### 2.4 Distress & Abuse Keyword Detection

- **24 distress keywords**: hopeless, worthless, helpless, trapped, hurt, pain, abuse, victim, "can't take it", "give up", "end it", suicide, die, useless, burden, "tired of living", alone, suffering …
- **16 abuse keywords**: abuse, abused, controlling, manipulative, gaslighting, threatened, intimidated, belittled, humiliated, isolated, "toxic relationship", "emotional abuse", "verbal abuse", "domestic violence" …

### 2.5 Research Comparison (Rule-based vs. ML-based)

The current classifier is the **rule-based baseline** (keyword frequency + polarity fusion).  
To compare with an ML approach, replace `get_emotion_scores()` with a HuggingFace pipeline call — the output schema is identical:

```python
# Drop-in ML replacement example
from transformers import pipeline
clf = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-emotion",
               top_k=None)

def get_emotion_scores_ml(text):
    results = clf(text)[0]
    # map labels to {joy, sadness, anxiety, anger, neutral} and normalise
    ...
```

---

## 3. Module 2 — Distress Monitoring Agent

**File**: `pattern_tracker.py`

### 3.1 Time-Weighted Sliding Window

Recent messages are weighted more heavily using exponential decay:

```
weight_i = 0.85^(window_size − 1 − i)
weighted_sentiment = Σ(sentiment_i × weight_i) / Σ(weight_i)
```

`TIME_DECAY_FACTOR` (default 0.85) is configurable in `config.py`.

### 3.2 Severity Levels

| Level | Severity score threshold |
|---|---|
| LOW | score < 4.0 |
| MEDIUM | 4.0 ≤ score < 7.0 |
| HIGH | score ≥ 7.0 |

The score is the **time-weighted average severity score** over the last `SEVERITY_SCORE_WINDOW` (default 5) messages.

### 3.3 Sustained Distress Detection

Fires when `consecutive_distress >= SUSTAINED_DISTRESS_COUNT` (default 3).  
Consecutive distress counter resets when any non-distress message arrives.

### 3.4 Emotion Distribution

Aggregates `emotion_scores` from Module 1 across all messages in the window:
```json
{ "sadness": 0.55, "anxiety": 0.38, "anger": 0.0, "joy": 0.0, "neutral": 0.07 }
```
Used by the **Emotional Trends** tab pie chart.

### 3.5 Full Pattern Summary

```json
{
  "total_messages":          5,
  "distress_messages":       4,
  "distress_ratio":          0.8,
  "average_sentiment":      -0.44,
  "weighted_sentiment":     -0.52,
  "severity_score":          7.79,
  "severity_level":         "HIGH",
  "emotion_distribution":   { "sadness": 0.55, "anxiety": 0.38, ... },
  "trend":                  "declining",
  "consecutive_distress":    4,
  "sustained_distress_detected": true,
  "abuse_indicators_detected": false,
  "abuse_indicators_count":  0
}
```

---

## 4. Module 3 — Pattern Prediction Agent

**File**: `prediction_agent.py` *(introduced in the current version)*

### 4.1 What it does

Given a time-series of recent sentiment scores it:
1. Fits an OLS linear regression line over the window
2. Extrapolates to predict the **next** sentiment score
3. Classifies the trend: `improving / stable / worsening`
4. Estimates **confidence** (inversely proportional to variance)
5. Fires an **early warning** when predicted sentiment < −0.35
6. Generates a **5-step forecast series** for the Risk Prediction chart
7. Accumulates **MAE** and **RMSE** per session for research evaluation

### 4.2 Usage Example

```python
from prediction_agent import PredictionAgent

agent = PredictionAgent()
agent.add_data_point(sentiment=-0.25, emotion_label='anxiety')
agent.add_data_point(sentiment=-0.35, emotion_label='sadness')
agent.add_data_point(sentiment=-0.48, emotion_label='sadness')

result = agent.predict_next_state()
# {
#   "predicted_sentiment": -0.62,
#   "trend": "worsening",
#   "confidence": 0.94,
#   "early_warning": True,
#   "warning_message": "📊 Early warning: your emotional state is predicted to worsen..."
# }

metrics = agent.get_metrics()
# {"mae": 0.042, "rmse": 0.056, "n_predictions": 2, "trend": "worsening", "data_points": 3}

forecast = agent.get_forecast_series(steps=5)
# [-0.62, -0.72, -0.83, -0.93, -1.0]
```

### 4.3 Swapping to LSTM

The interface is LSTM-compatible. Replace the single private function:

```python
# prediction_agent.py — drop-in LSTM replacement
def _linreg_predict(values):
    import torch
    model = load_trained_lstm()
    x = torch.tensor(values).unsqueeze(0).unsqueeze(-1).float()
    return float(model(x)[:, -1, :].item())
```

The rest of the pipeline (metric accumulation, forecast rendering, early-warning logic) is unchanged.

### 4.4 Research Metrics

| Metric | Meaning | Good value |
|---|---|---|
| MAE | Mean Absolute Error on predicted sentiment | < 0.10 |
| RMSE | Root Mean Squared Error | < 0.15 |
| Confidence | 1 − variance of sentiment window | > 0.70 |
| Trend accuracy | Predicted direction vs. actual | > 70 % |

---

## 5. Module 4 — Response Generation Agent

**File**: `conversation_handler.py`

### 5.1 Emotion-Category Template Banks

Each emotion category has **4 distinct response templates** (no more repetition):

| Category | Sample |
|---|---|
| 😊 Joy | *"Your happiness is contagious Jordan! Keep nurturing those good feelings. 🌟"* |
| 😢 Sadness | *"I hear the sadness in your words Jordan. Let's take this one moment at a time together."* |
| 😰 Anxiety | *"Anxiety can be overwhelming Jordan as a M.Tech Student. You're not alone — I'm here to help you find calm."* |
| 😠 Anger | *"Anger often signals something important Jordan. Would you like to talk about what's driving it?"* |
| 😐 Neutral | *"I hear you Jordan. Would you like to explore what's on your mind a bit deeper?"* |
| 🆘 Distress | *"You reached out, and that takes courage Jordan. I'm right here. Let's get through this together. 💙"* |
| ➕ Positive | *"I'm so glad to hear you're feeling positive Jordan! That's wonderful. 😊"* |
| ➖ Negative | *"I hear how hard things feel right now Jordan as a M.Tech Student. You don't have to carry this alone."* |

### 5.2 Personalization

- **Name**: every reply uses the user's preferred display name (e.g. "Jordan")
- **Occupation context**: injected into anxiety and negative templates  
  → *"…overwhelming Jordan as a M.Tech Student…"*
- **Abuse-indicator override**: appends a specialized safety message when abuse keywords are detected
- **Consecutive-response deduplication**: never repeats the same template twice in a row in a session

### 5.3 Template Selection Logic

```
dominant_emotion → look up in _TEMPLATES
  if found → use that bank
  else     → fall back to legacy emotion bucket
pick candidate ≠ last_response
fill {name} and {occupation_context} placeholders
append abuse-safety note if has_abuse_indicators
```

---

## 6. Module 5 — Guardian Alert Agent

**File**: `alert_system.py`

### 6.1 Five Severity Levels

```
INFO ──→ LOW ──→ MEDIUM ──→ HIGH ──→ CRITICAL
```

| Level | Trigger | Icon |
|---|---|---|
| INFO | Minor concern, low severity score | 🟢 |
| LOW | Mild sustained negativity | 🟡 |
| MEDIUM | Moderate distress | 🟠 |
| HIGH | Sustained high distress (score ≥ 7) | 🔴 |
| CRITICAL | Sustained HIGH + abuse indicators | 🚨 |

Severity is computed from `pattern_summary`:
1. Start from `severity_level` (LOW/MEDIUM/HIGH) from Module 2
2. +1 level if `abuse_indicators_detected`
3. → CRITICAL if `sustained_distress_detected` AND already HIGH

### 6.2 Escalation Policy

Unacknowledged alerts auto-escalate after:

| From | Escalates after |
|---|---|
| INFO | 60 minutes |
| LOW | 30 minutes |
| MEDIUM | 15 minutes |
| HIGH | 5 minutes |
| CRITICAL | No further escalation |

```python
escalated = alert_system.escalate_pending_alerts()
```

### 6.3 Alert Log

Every triggered alert is persisted in a structured log (capped at 100 entries):

```json
{
  "timestamp": "2026-02-23T20:51:18",
  "severity": "HIGH",
  "type": "distress",
  "severity_score": 7.79,
  "sustained_distress": true,
  "abuse_indicators": false,
  "notify_guardians": true,
  "acknowledged": false,
  "user": "jordan_22"
}
```

The log is displayed in the **Guardian Alerts** tab and is CSV-exportable via Streamlit's built-in dataframe toolbar.

### 6.4 Consent Mechanism

Guardian details are **never shown without explicit user approval**:

```
1. Alert fires → notify_guardians=True, guardian_consent=False
2. User sees guardian details in "Pending Alerts" expander
3. User clicks "✅ Consent to notify guardians"
4. guardian_consent → True
5. User clicks "✔ Acknowledge"
```

```python
alert_system.grant_guardian_consent(alert)
alert_system.acknowledge_alert(alert)
```

### 6.5 Guardian Contacts

Stored in `UserProfile`, set during profile creation or added from the Profile tab:

```python
profile.add_guardian_contact(
    name="Dr. Sharma",
    relationship="Counsellor",
    contact_info="+91-98765-43210"
)
```

---

## 7. Module 6 — Visualization & UI Agent

**File**: `ui_app.py`

### 7.1 Welcome & Authentication Screen

Before the main interface is shown, the user either:
- **Creates a new profile** — full form with optional password
- **Loads an existing profile** — gated by password prompt if the profile is protected

Password-protected profiles show:
> 🔒 Password Required for **username**  
> [Enter password] [🔓 Unlock Profile] [← Back]

Wrong passwords: attempt counter + lockout message after 3 failures.

### 7.2 Tab Overview

#### 💬 Chat Tab
- **Personalized greeting**: "🌟 Hi, Jordan!"
- **Live metrics bar**: Messages (count) · Trend (improving/declining/stable) · Severity (LOW/MEDIUM/HIGH) · Weighted Sentiment (−1 to +1) — updates after every message
- **Chat history**: full conversation display with user and assistant bubbles
- **Personalized placeholder**: "Share how you're feeling, Jordan…"
- **Inline alerts**: early-warning and distress alert messages appear in chat flow

#### 📈 Emotional Trends Tab
- **Sentiment line chart**: polarity per message, markers color-coded green→red, hover shows emotion label
- **Emotion distribution donut pie**: aggregate joy/sadness/anxiety/anger/neutral for current session
- **Long-term session bar chart**: average sentiment per session for the last 30 sessions

#### 📅 Weekly Summary Tab
- **Daily sentiment bar**: color-coded bar chart for last 7 days
- **Session message-count grouped bar**: total vs. distress messages per session
- **Week-at-a-glance metrics**: Sessions · Average Sentiment · Positive Days
- Falls back to current-session summary when < 7 days of history

#### 🔮 Risk Prediction Tab
- **Forecast chart**: observed sentiment (blue) + 5-step forecast (red dashed) + early-warning threshold line
- **Metric cards**: Confidence · Trend · Predicted Sentiment · MAE
- **Early warning banner** (orange) when threshold breached
- **Model Metrics panel**: data points, MAE, RMSE, predictions evaluated, current trend
- **Research note** explaining the OLS→LSTM migration path

#### 🚨 Guardian Alerts Tab
- **Guardian contact card**: name, relationship, phone/email
- **Alert log table**: timestamp, severity, type, score, sustained, acknowledged — sortable + CSV export
- **Pending alert expanders**: full details + consent button + acknowledge button
- **Severity guide**: table explaining each level and escalation interval

#### 👤 Profile Tab
- Full profile display: name, username, age, occupation, gender, primary concerns, session count
- Trusted contacts list · Guardian contacts list
- **Manage section**: Add Trusted Contact · Add Guardian Contact · Set/Change Password · Remove Password · Delete All My Data
- Password-protection status banner: *"🔒 This profile is password-protected."* or *"🔓 No password set."*

### 7.3 Sidebar (always visible in main interface)

- User name, occupation, age
- Session number
- Focus areas (primary concerns, as bullet list)
- 📞 Help & Resources button — triggers crisis resources message in chat
- ⚙️ Manage Profile button — opens sidebar management menu
- 🚪 End Session button — saves and returns to welcome screen

---

## 8. User Profile — Full Personal Details

**File**: `user_profile.py`

### 8.1 Profile Fields

| Field | Setter | Description |
|---|---|---|
| `user_id` | (set at creation) | Private username — never displayed to others |
| `name` | `set_name(name)` | Preferred display name used in every message |
| `age` | `set_age(age)` | Integer age (optional) |
| `occupation` | `set_occupation(occ)` | Job / student status — used in responses |
| `primary_concerns` | `set_primary_concerns(list)` | Reasons for using the app (multi-select) |
| `gender` | `set_gender(gender)` | Enables specialized women's resources if female |
| `trusted_contacts` | `add_trusted_contact(...)` | Safe people to contact |
| `guardian_contacts` | `add_guardian_contact(...)` | Emergency contacts for alerts |
| `unsafe_contacts` | `add_unsafe_contact(...)` | Contacts to avoid in alerts (toxic situations) |
| `emotional_history` | (auto) | Up to 365-day rolling session snapshots |
| `session_count` | `increment_session_count()` | Increments each session |
| `password_hash` | `set_password(pw)` | SHA-256 + salt hash; `None` if no password |

### 8.2 Primary Concerns (multi-select options in UI)

Stress & Anxiety · Depression / Low Mood · Loneliness · Relationship Issues ·
Work / Academic Pressure · Family Problems · Grief / Loss · Self-esteem ·
Trauma · General Wellbeing · Other

### 8.3 Guardian Contact Schema

```python
{
  "name": "Dr. Sharma",
  "relationship": "Counsellor",
  "contact_info": "+91-98765-43210",
  "added_at": "2026-02-23T20:10:00"
}
```

---

## 9. Password Protection & Security

**Backend**: `user_profile.py` + `data_store.py`  
**UI gate**: `ui_app.py`

### 9.1 Password Methods

| Method | Description |
|---|---|
| `set_password(password)` | Generates random 64-hex salt; stores SHA-256(password+salt); raises `ValueError` if < 8 chars |
| `verify_password(password)` | Returns `True` if hash matches; increments `failed_login_attempts` on failure; locks out after 3 failures |
| `is_locked_out()` | Returns `True` if `lockout_until` is in the future |
| `remove_password()` | Clears hash, salt, and `security_enabled` flag |
| `reset_lockout()` | Clears lockout timestamp and resets attempt counter |

### 9.2 Account Lockout

```
3 failed attempts → locked for 15 minutes
after lockout expiry → counter automatically resets
```

All lockout state is persisted to disk so it survives browser refresh / app restart.

### 9.3 Login UI Flow

```
"Load Profile" → _initiate_login(username)
  ├─ No password stored → load_profile() directly (backward-compatible)
  └─ Password stored → set pending_username → _show_login_form()
       ├─ Locked out → show lockout message, "← Back"
       ├─ Wrong password → increment attempts, show remaining counter
       └─ Correct password → persist reset, load_profile()
```

### 9.4 Storage Security

| Feature | Implementation |
|---|---|
| AES-256 encryption | Fernet symmetric encryption; key at `~/.wellness_buddy/.encryption_key` |
| Password hashing | SHA-256 with 64-hex random salt; passwords never stored in plaintext |
| File permissions | `chmod 600` on every data and key file |
| Automatic backups | Timestamped `.json` backup before every save |
| Data integrity | `get_data_integrity_hash()` returns SHA-256 of file |
| Local-only storage | `~/.wellness_buddy/` — zero external API calls |
| Session timeout | Auto-logout after 30 min of inactivity (configurable) |
| Full deletion | Delete all data from Profile tab at any time |

---

## 10. Specialized Support for Women

When a user's gender is `female` and family/guardians are marked unsafe:

1. **Alert routing modified** — guardian section replaced by women's organization resources
2. **Trusted contacts prioritized** — user's own trusted friends shown prominently
3. **Women's resource pack** in every distress alert:
   - National Domestic Violence Hotline: 1-800-799-7233
   - RAINN: 1-800-656-4673
   - National Women's Law Center: 202-588-5180
4. **Government resources** appended (HHS, DOJ, NIMH, legal aid)
5. **Abuse-indicator detection**: 16 keywords trigger specialized response regardless of alert severity
6. Safe-support tips: *"Reach out to trusted friends outside your household"* etc.

---

## 11. Data Management

### Storage Location
```
~/.wellness_buddy/
├── .encryption_key           (owner-only, chmod 600)
├── username.json             (encrypted profile + 365-day history)
└── username_backup_YYYYMMDD_HHMMSS.json
```

### Key DataStore Operations

```python
data_store.save_user_data(user_id, profile_data)
data_store.load_user_data(user_id)
data_store.list_users()
data_store.delete_user_data(user_id)
data_store.create_backup(user_id)          # → backup file path
data_store.get_data_integrity_hash(user_id)  # → SHA-256 hex
```

### Data Retention
- Emotional history: **365 days** rolling window
- Conversation archive: 180 days (then summarized)
- Max snapshots: 365
- Alert log: 100 entries (capped)

---

## 12. Configuration Reference

**File**: `config.py`

### Emotion Analysis (Module 1)
```python
DISTRESS_THRESHOLD = -0.3          # Sentiment below this → distress
SUSTAINED_DISTRESS_COUNT = 3       # Consecutive distress messages to alert
PATTERN_TRACKING_WINDOW = 10       # Rolling window size for Module 2
```

### Distress Monitoring (Module 2)
```python
SEVERITY_SCORE_WINDOW = 5          # Messages averaged for severity score
TIME_DECAY_FACTOR = 0.85           # Exponential weight decay (recent = higher)
SEVERITY_HIGH_THRESHOLD = 7.0      # Score ≥ 7 → HIGH
SEVERITY_MEDIUM_THRESHOLD = 4.0    # Score ≥ 4 → MEDIUM
```

### Prediction Agent (Module 3)
```python
PREDICTION_WINDOW = 7              # Data points for OLS fit
EARLY_WARNING_THRESHOLD = -0.35    # Predicted score to fire early warning
PREDICTION_CONFIDENCE_MIN = 0.50   # Min confidence to display prediction
```

### Guardian Alerts (Module 5)
```python
ALERT_SEVERITY_LEVELS = ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
ESCALATION_INTERVALS = {'INFO': 60, 'LOW': 30, 'MEDIUM': 15, 'HIGH': 5, 'CRITICAL': 0}
MAX_ALERT_LOG_ENTRIES = 100
ENABLE_GUARDIAN_ALERTS = True
AUTO_NOTIFY_GUARDIANS = False      # Always ask user first
```

### Security
```python
ENABLE_PROFILE_PASSWORD = True
SESSION_TIMEOUT_MINUTES = 30
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 15
ENABLE_DATA_ENCRYPTION = True
```

### Data Retention
```python
EMOTIONAL_HISTORY_DAYS = 365
CONVERSATION_ARCHIVE_DAYS = 180
MAX_EMOTIONAL_SNAPSHOTS = 365
MAX_CONVERSATION_HISTORY = 50
```

---

## 13. Testing & Research Metrics

### Running Tests

```bash
python -m pytest test_wellness_buddy.py -v
```

### Test Coverage (12 tests)

| # | Test | What it covers |
|---|---|---|
| 1 | `test_emotion_analysis` | Legacy classifier, polarity, keywords |
| 2 | `test_pattern_tracking` | Consecutive distress, trends, sustained detection |
| 3 | `test_alert_system` | Alert trigger, format, women's resources |
| 4 | `test_conversation_handler` | Response generation, no errors |
| 5 | `test_user_profile` | Profile fields, trusted contacts, safety settings |
| 6 | `test_data_persistence` | Save / load / list / delete |
| 7 | `test_full_workflow` | End-to-end abuse detection and alert |
| 8 | `test_multi_emotion_classification` | 5-category scores, dominant emotion, severity_score |
| 9 | `test_time_weighted_distress` | weighted_sentiment, severity_level, emotion_distribution |
| 10 | `test_prediction_agent` | Predictions, MAE/RMSE, forecast series |
| 11 | `test_alert_severity_escalation` | 5 severity levels, acknowledge, alert log |
| 12 | `test_password_protection` | set/verify/lockout/remove/reset with pytest.raises |

### Research Evaluation Metrics

| Metric | Source | Purpose |
|---|---|---|
| Sentiment polarity | `emotion_data['polarity']` | TextBlob baseline |
| Emotion scores (5 categories) | `emotion_data['emotion_scores']` | Multi-label accuracy |
| Severity score (0–10) | `pattern_summary['severity_score']` | Distress quantification |
| MAE | `prediction_agent.get_metrics()['mae']` | Temporal model quality |
| RMSE | `prediction_agent.get_metrics()['rmse']` | Temporal model quality |
| Trend accuracy | predicted vs. actual trend | Module 3 evaluation |
| Alert detection accuracy | alert log vs. ground truth | Module 5 evaluation |
| Response latency | session timing | System performance |

---

## 14. Complete Feature Checklist

### ✅ Emotion Analysis (Module 1)
- [x] TextBlob polarity (−1 to +1) and subjectivity
- [x] 5-category emotion classification (joy, sadness, anxiety, anger, neutral)
- [x] Per-category confidence scores (normalized 0–1, sum = 1)
- [x] Dominant emotion detection
- [x] Numeric severity score (0–10)
- [x] 24 distress keywords detected
- [x] 16 abuse indicator keywords detected
- [x] Legacy emotion bucket (positive/negative/neutral/distress) for backward compatibility

### ✅ Distress Monitoring (Module 2)
- [x] Sliding window of last N messages (default 10)
- [x] Exponential time-decay weighting (0.85 decay factor)
- [x] Consecutive distress counter with auto-reset
- [x] Sustained distress detection (3 consecutive messages)
- [x] Weighted average sentiment
- [x] Named severity level (LOW/MEDIUM/HIGH)
- [x] Emotion distribution aggregated across window
- [x] Trend classification (improving/stable/declining)

### ✅ Pattern Prediction (Module 3)
- [x] OLS linear regression temporal model
- [x] Predicted next sentiment score (clamped to [−1, +1])
- [x] Trend classification (improving/stable/worsening)
- [x] Confidence estimate (1 − variance)
- [x] Early-warning threshold (−0.35 default)
- [x] 5-step forecast series for chart
- [x] MAE metric accumulation
- [x] RMSE metric accumulation
- [x] LSTM-compatible interface (single function replacement)

### ✅ Response Generation (Module 4)
- [x] 8 emotion-category template banks
- [x] 4 variants per category (32 total templates)
- [x] Personalized name address in every reply
- [x] Occupation context injection
- [x] Consecutive-response deduplication
- [x] Abuse-indicator override safety message
- [x] Legacy emotion bucket fallback

### ✅ Guardian Alert System (Module 5)
- [x] 5 severity levels (INFO/LOW/MEDIUM/HIGH/CRITICAL)
- [x] Severity computation from pattern summary
- [x] Abuse-indicator severity escalation (+1 level)
- [x] Sustained distress → CRITICAL escalation
- [x] Time-based auto-escalation of unacknowledged alerts
- [x] Structured alert log (JSON + CSV export)
- [x] Consent mechanism (guardian_consent flag)
- [x] Acknowledge mechanism with timestamp
- [x] Women's specialized resources in alerts
- [x] Guardian contact details in alert message
- [x] `format_guardian_notification()` for external messaging
- [x] `format_alert_message()` for UI display

### ✅ Multi-Tab UI (Module 6)
- [x] Welcome screen with Load / Create profile
- [x] Password gate for protected profiles
- [x] Chat tab with live 4-metric bar
- [x] Sentiment line chart (color-coded markers)
- [x] Emotion distribution donut pie chart
- [x] Long-term session sentiment bar chart
- [x] Weekly daily sentiment bar chart
- [x] Session message-count comparison bar chart
- [x] Risk Prediction tab with 5-step forecast chart
- [x] Early-warning threshold line on forecast chart
- [x] Model metrics panel (MAE, RMSE, confidence)
- [x] Guardian Alerts tab with alert log table (CSV export)
- [x] Pending alert expanders with consent + acknowledge
- [x] Severity guide table
- [x] Profile tab with full profile display
- [x] Inline add trusted/guardian contact forms
- [x] Set / Change Password action
- [x] Remove Password action (requires current password)
- [x] Delete All Data action

### ✅ User Profile
- [x] Username (private identifier)
- [x] Preferred display name
- [x] Age
- [x] Occupation / student status
- [x] Gender
- [x] Primary concerns (multi-select, 11 options)
- [x] Trusted contacts
- [x] Guardian / emergency contacts
- [x] Unsafe contacts (toxic family situations)
- [x] 365-day emotional history
- [x] Session count

### ✅ Password Protection & Security
- [x] Optional password at profile creation
- [x] SHA-256 password hashing with 64-hex random salt
- [x] Account lockout after 3 failed attempts (15 min)
- [x] Attempt count and lockout state persisted to disk
- [x] Remaining-attempts counter shown in UI
- [x] Set / Change Password from Profile tab
- [x] Remove Password with current-password confirmation
- [x] AES-256 (Fernet) encryption of all stored data
- [x] Session timeout (30 min inactivity)
- [x] File permissions: chmod 600
- [x] Automatic timestamped backups
- [x] Data integrity hash (SHA-256)
- [x] Full user-controlled deletion

### ✅ Interfaces & Deployment
- [x] Streamlit Web UI (`streamlit run ui_app.py`)
- [x] CLI (`python wellness_buddy.py`)
- [x] Network UI (`bash start_ui_network.sh`)

---

*"Your emotional wellbeing journey matters. AI Wellness Buddy is here to support you every step of the way, privately and securely."* 💙🌟
