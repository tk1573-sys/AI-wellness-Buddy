# AI Wellness Buddy — Complete Feature Guide

> **Last updated**: Feb 2026 — reflects the six-module agent-based architecture.
> 
> Quick links: [README](README.md) · [Security](SECURITY.md) · [Data Retention](DATA_RETENTION.md) · [Deployment](NETWORK_DEPLOYMENT.md)

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
9. [Security & Privacy Features](#9-security--privacy-features)
10. [Specialized Support for Women](#10-specialized-support-for-women)
11. [Data Management](#11-data-management)
12. [Configuration Reference](#12-configuration-reference)
13. [Testing & Research Metrics](#13-testing--research-metrics)
14. [Complete Feature Checklist](#14-complete-feature-checklist)

---

## 1. Project Summary

**AI Wellness Buddy** is a privacy-first emotional support application that builds a personal profile for each user, analyses the emotional tone of every message they type, tracks trends across sessions, predicts future emotional states, and can alert a trusted guardian when sustained distress is detected.

### Why it is different from a simple chatbot

| Ordinary chatbot | AI Wellness Buddy |
|---|---|
| Replies to one message at a time | Tracks patterns across the entire conversation and across sessions |
| Generic replies | Personalized replies using your name, occupation, and primary concerns |
| One emotion (positive / negative) | Five emotion categories with confidence scores |
| Fixed alert (on/off) | Five-level severity with auto-escalation and consent mechanism |
| No prediction | Predicts your next emotional state with early-warning |
| No dashboard | Six-tab analytics UI with live charts |

---

## 2. Module 1 — Emotion Analysis Agent

**File**: `emotion_analyzer.py`

### 2.1 Multi-Label Emotion Classification

Every message is scored across **five emotion categories** using a fusion of:
- Keyword-frequency counting (curated word lists per category)
- TextBlob polarity to weight the scores

| Category | Trigger words (examples) |
|---|---|
| 😢 Sadness | sad, depressed, hopeless, lonely, heartbroken, grief, crying, numb, despair |
| 😰 Anxiety | anxious, worried, stressed, panic, overwhelmed, scared, insomnia, racing thoughts |
| 😠 Anger | angry, furious, frustrated, resentment, rage, disgusted, fed up |
| 😊 Joy | happy, grateful, excited, wonderful, content, peaceful, relieved, elated |
| 😐 Neutral | Anything that doesn't match the above |

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

### 2.3 Severity Score (0–10)

```
severity_score = clamp((-polarity + 1) / 2 * 10 + keyword_bonus, 0, 10)
                 ↑ 0 = very positive, 10 = extreme negative
```

Keyword bonus: +0.5 per distress keyword, +1.0 per abuse keyword, capped at +3.

### 2.4 Research Comparison

The module uses a **rule-based approach** (keyword + polarity fusion) as the baseline.  
Replace `get_emotion_scores()` with a `transformers` pipeline call (e.g. `cardiffnlp/twitter-roberta-base-emotion`) to compare ML-based detection — the output schema is identical.

---

## 3. Module 2 — Distress Monitoring Agent

**File**: `pattern_tracker.py`

### 3.1 Time-Weighted Sliding Window

Unlike simple averages, recent messages count more:

```
weight_i = decay^(window_size - 1 - i)   where decay = TIME_DECAY_FACTOR (default 0.85)
weighted_sentiment = Σ(sentiment_i × weight_i) / Σ(weight_i)
```

### 3.2 Severity Levels

| Level | Score threshold |
|---|---|
| LOW | score < 4.0 |
| MEDIUM | 4.0 ≤ score < 7.0 |
| HIGH | score ≥ 7.0 |

The score is the **weighted average severity score** over the last `SEVERITY_SCORE_WINDOW` (default 5) messages.

### 3.3 Emotion Distribution

Aggregates `emotion_scores` from Module 1 across all messages in the window:
```json
{
  "sadness": 0.55,
  "anxiety": 0.38,
  "anger":   0.0,
  "joy":     0.0,
  "neutral": 0.07
}
```
Used by the **Emotional Trends** tab pie chart.

### 3.4 Full Pattern Summary

```json
{
  "total_messages":          3,
  "distress_messages":       3,
  "distress_ratio":          1.0,
  "average_sentiment":      -0.48,
  "weighted_sentiment":     -0.52,
  "severity_score":          7.79,
  "severity_level":         "HIGH",
  "emotion_distribution":   { "sadness": 0.55, "anxiety": 0.38, ... },
  "trend":                  "declining",
  "consecutive_distress":    3,
  "sustained_distress_detected": true,
  "abuse_indicators_detected": false,
  "abuse_indicators_count":  0
}
```

---

## 4. Module 3 — Pattern Prediction Agent

**File**: `prediction_agent.py`  *(new file — not present in older versions)*

### 4.1 What it does

Given a time-series of recent sentiment scores it:
1. Fits an OLS linear regression line
2. Extrapolates to predict the **next** sentiment score
3. Classifies the trend as `improving / stable / worsening`
4. Estimates **confidence** (inversely proportional to variance)
5. Fires an **early warning** when predicted sentiment < −0.35
6. Generates a **5-step forecast series** for the Risk Prediction chart

### 4.2 How to use

```python
from prediction_agent import PredictionAgent

agent = PredictionAgent()

# Feed one data point per user message
agent.add_data_point(sentiment=-0.25, emotion_label='anxiety')
agent.add_data_point(sentiment=-0.35, emotion_label='sadness')
agent.add_data_point(sentiment=-0.48, emotion_label='sadness')

# Predict
result = agent.predict_next_state()
# {
#   "predicted_sentiment": -0.62,
#   "trend": "worsening",
#   "confidence": 0.94,
#   "early_warning": True,
#   "warning_message": "📊 Early warning: your emotional state is predicted to worsen..."
# }

# Research metrics
metrics = agent.get_metrics()
# {"mae": 0.042, "rmse": 0.056, "n_predictions": 2, "trend": "worsening", "data_points": 3}

# Chart data
forecast = agent.get_forecast_series(steps=5)
# [-0.62, -0.72, -0.83, -0.93, -1.0]
```

### 4.3 Swapping to LSTM

The prediction interface is LSTM-compatible.  Replace the single function `_linreg_predict(values)` with an LSTM forward-pass:

```python
# prediction_agent.py  — drop-in replacement
def _linreg_predict(values):
    # Replace this with:
    import torch
    model = load_lstm_model()         # your trained model
    x = torch.tensor(values).unsqueeze(0).unsqueeze(-1)
    return float(model(x)[:, -1, :])
```

### 4.4 Research Metrics

| Metric | Meaning | Good value |
|---|---|---|
| MAE | Mean Absolute Error on predicted sentiment | < 0.10 |
| RMSE | Root Mean Squared Error | < 0.15 |
| Trend accuracy | Predicted trend vs. actual direction | > 70 % |
| Confidence | 1 − variance of recent window | > 0.70 |

---

## 5. Module 4 — Response Generation Agent

**File**: `conversation_handler.py`

### 5.1 Emotion-Category Templates

Each emotion category has **4 distinct response templates**:

| Category | Sample response |
|---|---|
| Joy | *"Your happiness is contagious {name}! Keep nurturing those good feelings. 🌟"* |
| Sadness | *"I hear the sadness in your words {name}. Let's take this one moment at a time together."* |
| Anxiety | *"Anxiety can be overwhelming {name} as a {occupation}. You're not alone — I'm here to help you find calm."* |
| Anger | *"Anger often signals something important {name}. Would you like to talk about what's driving it?"* |
| Neutral | *"I hear you {name}. Would you like to explore what's on your mind a bit deeper?"* |
| Distress | *"You reached out, and that takes courage {name}. I'm right here. Let's get through this together. 💙"* |

### 5.2 Personalisation

- **Name**: every reply uses the user's preferred display name
- **Occupation context**: injected into anxiety and negative templates
  - *"…overwhelming {name} as a M.Tech Student…"*
- **Abuse-indicator override**: appends a specialised safety message when abuse keywords are detected
- **Deduplication**: never repeats the same template twice in a row within a session

### 5.3 Occupation Context

Set via profile → automatically appears in relevant responses:
```
"Anxiety can be overwhelming Alex as a M.Tech Student."
"I hear how hard things feel right now Alex as a Graduate Student."
```

---

## 6. Module 5 — Guardian Alert Agent

**File**: `alert_system.py`

### 6.1 Five Severity Levels

```
INFO  ──→  LOW  ──→  MEDIUM  ──→  HIGH  ──→  CRITICAL
  (minor)  (mild)  (moderate)  (sustained)  (severe + abuse)
```

Severity is calculated from the pattern summary:
- Base level comes from `severity_level` (LOW/MEDIUM/HIGH) from Module 2
- **+1 level** if abuse indicators are detected
- **→ CRITICAL** if `sustained_distress_detected` AND level is already HIGH

### 6.2 Escalation Policy

Unacknowledged alerts auto-escalate after:

| From severity | Escalates after |
|---|---|
| INFO | 60 minutes |
| LOW | 30 minutes |
| MEDIUM | 15 minutes |
| HIGH | 5 minutes |
| CRITICAL | No further escalation |

```python
# Check and apply escalations
escalated = alert_system.escalate_pending_alerts()
```

### 6.3 Alert Log

Every triggered alert is recorded in a structured log:

```json
{
  "timestamp": "2026-02-23T20:51:18",
  "severity": "CRITICAL",
  "type": "distress",
  "severity_score": 7.79,
  "sustained_distress": true,
  "abuse_indicators": false,
  "notify_guardians": true,
  "acknowledged": false,
  "user": "demo_user"
}
```

The log is visible in the **Guardian Alerts** tab and exportable as CSV.

### 6.4 Consent Mechanism

Guardian details are **never shown without explicit user approval**:

```python
# UI flow:
# 1. Alert fires → notify_guardians=True, guardian_consent=False
# 2. User sees guardian details in "Pending Alerts" expander
# 3. User clicks "Consent to notify guardians" button
# 4. guardian_consent is set to True
alert_system.grant_guardian_consent(alert)

# 5. User acknowledges the alert
alert_system.acknowledge_alert(alert)
```

### 6.5 Guardian Contacts

Stored in the user profile, collected during profile creation:
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

### 7.1 Tab Overview

#### 💬 Chat Tab
- **Greeting**: personalized "🌟 Hi, Alex!"
- **Live metrics bar**: Messages (count) · Trend (improving/declining/stable) · Severity (LOW/MEDIUM/HIGH) · Weighted Sentiment (−1 to +1, updates after every message)
- **Chat history**: full conversation display
- **Personalized input placeholder**: "Share how you're feeling, Alex…"
- **Inline alerts**: early-warning and distress alert messages appear inline in the chat

#### 📈 Emotional Trends Tab
- **Sentiment line chart**: polarity per message, markers colour-coded green→red, hover shows emotion label
- **Emotion distribution donut pie**: aggregate joy/sadness/anxiety/anger/neutral across the session
- **Long-term bar chart**: average sentiment per session for the last 30 sessions (if history exists)

#### 📅 Weekly Summary Tab
- **Daily sentiment bar**: colour-coded bar chart for last 7 days
- **Session message-count grouped bar**: total vs. distress messages per session
- **Week-at-a-glance metrics**: Sessions · Avg Sentiment · Positive Days
- Falls back to current-session summary when < 7 days of history

#### 🔮 Risk Prediction Tab
- **Forecast chart**: observed sentiment (blue line) + 5-step forecast (red dashed) + early-warning threshold line
- **Confidence, Trend, Predicted Sentiment, MAE** shown as metric cards
- **Early warning banner** (orange) when threshold breached
- **Model Metrics panel**: data points, MAE, RMSE, predictions evaluated, current trend
- **Research note** explaining the OLS→LSTM migration path

#### 🚨 Guardian Alerts Tab
- **Guardian contact card**: name, relationship, phone/email
- **Alert log table**: timestamp, severity, type, score, sustained, acknowledged (sortable, searchable, CSV export)
- **Pending alert expanders**: full alert details + consent button + acknowledge button
- **Severity guide**: table explaining each severity level and escalation timing

#### 👤 Profile Tab
- Full profile display: name, username, age, occupation, gender, primary concerns, session count
- Trusted contacts list
- Guardian contacts list
- Inline "Manage" section: add trusted contact, add guardian contact, delete all data

### 7.2 Sidebar (always visible)

- User name, occupation, age
- Session number
- Focus areas (primary concerns)
- Help & Resources button (triggers crisis resources message in chat)
- Manage Profile button (opens sidebar management menu)
- End Session button

---

## 8. User Profile — Full Personal Details

**File**: `user_profile.py`

### 8.1 Profile Fields

| Field | Method | Description |
|---|---|---|
| `user_id` | (set at creation) | Private username |
| `name` | `set_name(name)` | Preferred display name |
| `age` | `set_age(age)` | Integer age |
| `occupation` | `set_occupation(occ)` | Job / student status |
| `primary_concerns` | `set_primary_concerns(list)` | Reasons for using the app |
| `gender` | `set_gender(gender)` | Enables specialised resources |
| `trusted_contacts` | `add_trusted_contact(...)` | Safe people to contact |
| `guardian_contacts` | `add_guardian_contact(...)` | Emergency contacts for alerts |
| `unsafe_contacts` | `add_unsafe_contact(...)` | Contacts to avoid in alerts |
| `emotional_history` | (auto) | Up to 365-day session snapshots |
| `session_count` | (auto) | Increments each session |

### 8.2 Guardian Contact Schema

```python
{
  "name": "Dr. Sharma",
  "relationship": "Counsellor",
  "contact_info": "+91-98765-43210",
  "added_at": "2026-02-23T20:10:00"
}
```

### 8.3 Primary Concerns (multi-select options)

Stress & Anxiety · Depression / Low Mood · Loneliness · Relationship Issues ·
Work / Academic Pressure · Family Problems · Grief / Loss · Self-esteem ·
Trauma · General Wellbeing · Other

---

## 9. Security & Privacy Features

**File**: `data_store.py` + `config.py`

| Feature | Implementation |
|---|---|
| AES-256 encryption | Fernet symmetric encryption; key stored in `~/.wellness_buddy/.encryption_key` (chmod 600) |
| Password hashing | SHA-256 with per-profile unique salt; passwords never stored in plain text |
| Session timeout | Configurable — default 30 min; checked on every message |
| Account lockout | 3 failed login attempts → 15-min lockout (configurable) |
| Data integrity | `get_data_integrity_hash(user_id)` returns SHA-256 of file |
| Automatic backups | `create_backup(user_id)` runs before every save; timestamped filename |
| Local-only storage | All data in `~/.wellness_buddy/`; zero external API calls |
| Owner-only permissions | `os.chmod(file, 0o600)` on every data and key file |

### Encrypted file structure
```json
{
  "encrypted": true,
  "data": "gAAAAABh3k4p..."
}
```

---

## 10. Specialized Support for Women

When a user identifies as female and marks family/guardians as unsafe:

1. **Modified alert routing**: guardian alert section is replaced by women's organization resources
2. **Trusted contacts prioritized**: user's own trusted friends shown prominently
3. **Women's resource pack** added to every distress alert:
   - National Domestic Violence Hotline: 1-800-799-7233
   - RAINN: 1-800-656-4673
   - National Women's Law Center: 202-588-5180
4. **Government resources** appended (Office on Women's Health, Violence Against Women Office, Legal Services)
5. **Safe support tips**: how to build a safe network outside the household
6. **Abuse-indicator detection**: 16 keywords trigger specialized response even outside the main alert

---

## 11. Data Management

### Storage Location
```
~/.wellness_buddy/
├── .encryption_key          (owner-only)
├── username.json            (encrypted profile + 365-day history)
└── username_backup_YYYYMMDD_HHMMSS.json
```

### Key Operations

```python
# Save
data_store.save_user_data(user_id, profile.get_profile())

# Load
data = data_store.load_user_data(user_id)

# List users
users = data_store.list_users()

# Delete
data_store.delete_user_data(user_id)

# Backup
backup_path = data_store.create_backup(user_id)

# Integrity check
hash1 = data_store.get_data_integrity_hash(user_id)
```

### Data Retention
- Emotional history: **365 days** rolling window
- Conversation archive: 180 days (then summarised)
- Max snapshots: 365

---

## 12. Configuration Reference

**File**: `config.py`

### Emotion Analysis
```python
DISTRESS_THRESHOLD = -0.3         # Sentiment below this → distress
SUSTAINED_DISTRESS_COUNT = 3      # Consecutive distress messages to alert
PATTERN_TRACKING_WINDOW = 10      # Rolling window size
```

### Distress Monitoring (Module 2)
```python
SEVERITY_SCORE_WINDOW = 5         # Messages averaged for severity score
TIME_DECAY_FACTOR = 0.85          # Exponential weight decay
SEVERITY_HIGH_THRESHOLD = 7.0     # Score ≥ 7 → HIGH
SEVERITY_MEDIUM_THRESHOLD = 4.0   # Score ≥ 4 → MEDIUM
```

### Prediction Agent (Module 3)
```python
PREDICTION_WINDOW = 7             # Data points for OLS fit
EARLY_WARNING_THRESHOLD = -0.35   # Predicted score to fire early warning
PREDICTION_CONFIDENCE_MIN = 0.50  # Min confidence to show warning
```

### Guardian Alerts (Module 5)
```python
ALERT_SEVERITY_LEVELS = ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
ESCALATION_INTERVALS = {'INFO': 60, 'LOW': 30, 'MEDIUM': 15, 'HIGH': 5, 'CRITICAL': 0}
MAX_ALERT_LOG_ENTRIES = 100
ENABLE_GUARDIAN_ALERTS = True
AUTO_NOTIFY_GUARDIANS = False     # Always ask user first
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
MAX_CONVERSATION_HISTORY = 50     # In-session message buffer
```

---

## 13. Testing & Research Metrics

### Running Tests

```bash
python -m pytest test_wellness_buddy.py -v
```

### Test Coverage (11 tests)

| Test | What it covers |
|---|---|
| `test_emotion_analysis` | Legacy classifier, polarity, keywords |
| `test_pattern_tracking` | Consecutive distress, trends, sustained detection |
| `test_alert_system` | Alert trigger, format, women's resources |
| `test_conversation_handler` | Response generation, no errors |
| `test_user_profile` | Profile fields, trusted contacts, safety settings |
| `test_data_persistence` | Save / load / list / delete |
| `test_full_workflow` | End-to-end abuse detection and alert |
| `test_multi_emotion_classification` | 5-category scores, dominant emotion, severity_score |
| `test_time_weighted_distress` | weighted_sentiment, severity_level, emotion_distribution |
| `test_prediction_agent` | Predictions, metrics (MAE/RMSE), forecast series |
| `test_alert_severity_escalation` | Severity levels, acknowledge, alert log |

### Research Evaluation Metrics

| Metric | API | Research purpose |
|---|---|---|
| Emotion classification F1-score | Compare rule-based vs. ML `get_emotion_scores()` | Module 1 accuracy |
| Sentiment polarity | `emotion_data['polarity']` | Baseline |
| Severity score distribution | `pattern_summary['severity_score']` | Distress quantification |
| MAE / RMSE | `prediction_agent.get_metrics()` | Temporal model quality |
| Trend classification accuracy | Predicted vs. actual | Module 3 evaluation |
| Alert detection accuracy | Alert log vs. labelled ground truth | Module 5 evaluation |
| Response latency | Session timing | System performance |

---

## 14. Complete Feature Checklist

### ✅ Emotion Analysis
- [x] TextBlob polarity (−1 to +1)
- [x] Subjectivity score
- [x] 5-category emotion classification (joy, sadness, anxiety, anger, neutral)
- [x] Per-category confidence scores
- [x] Dominant emotion detection
- [x] Numeric severity score (0–10)
- [x] 24 distress keywords detected
- [x] 16 abuse indicator keywords detected

### ✅ Distress Monitoring
- [x] Sliding window (last N messages)
- [x] Exponential time-decay weighting
- [x] Consecutive distress counter
- [x] Sustained distress detection
- [x] Weighted average sentiment
- [x] Named severity level (LOW/MEDIUM/HIGH)
- [x] Emotion distribution across window
- [x] Trend classification (improving/stable/declining)

### ✅ Prediction Agent
- [x] OLS linear regression temporal model
- [x] Predicted next sentiment score
- [x] Trend classification (improving/stable/worsening)
- [x] Confidence estimate
- [x] Early-warning threshold
- [x] 5-step forecast series
- [x] MAE metric accumulation
- [x] RMSE metric accumulation
- [x] LSTM-compatible interface (drop-in replacement)

### ✅ Response Generation
- [x] 6 emotion-category template banks (4 variants each)
- [x] Personalized name address in every reply
- [x] Occupation context injection
- [x] Consecutive-response deduplication
- [x] Abuse-indicator override message
- [x] Legacy bucket fallback (positive/negative/neutral)

### ✅ Guardian Alert System
- [x] 5 severity levels (INFO/LOW/MEDIUM/HIGH/CRITICAL)
- [x] Severity computation from pattern summary
- [x] Abuse-indicator severity escalation
- [x] Time-based auto-escalation of unacknowledged alerts
- [x] Structured alert log (JSON + CSV export)
- [x] Consent mechanism (guardian_consent flag)
- [x] Acknowledge mechanism
- [x] Women's specialised resources in alerts
- [x] Guardian contact details in alert message

### ✅ Visualization UI (6 tabs)
- [x] Chat tab with live metrics bar
- [x] Sentiment line chart (colour-coded markers)
- [x] Emotion distribution donut pie chart
- [x] Long-term session sentiment bar chart
- [x] Weekly daily sentiment bar chart
- [x] Session message-count comparison bar chart
- [x] Risk Prediction tab with forecast chart
- [x] Early-warning threshold line on forecast chart
- [x] Model metrics panel (MAE, RMSE, confidence)
- [x] Guardian Alerts tab with alert log table
- [x] Pending alert expanders with consent/acknowledge buttons
- [x] Severity guide table
- [x] Profile tab with full profile display
- [x] Inline add trusted/guardian contact forms

### ✅ User Profile
- [x] Username (private)
- [x] Preferred display name
- [x] Age
- [x] Occupation / student status
- [x] Gender
- [x] Primary concerns (multi-select, 11 options)
- [x] Trusted contacts (name, relationship, contact info)
- [x] Guardian / emergency contacts (name, relationship, contact info)
- [x] Unsafe contacts (for toxic family situations)
- [x] 365-day emotional history
- [x] Session count

### ✅ Security & Privacy
- [x] AES-256 encryption (Fernet)
- [x] SHA-256 password hashing with salt
- [x] Session timeout (30 min default)
- [x] Account lockout (3 attempts, 15 min)
- [x] Data integrity hash
- [x] Automatic timestamped backups
- [x] Local-only storage (no external APIs)
- [x] Owner-only file permissions (chmod 600)
- [x] Full user-controlled deletion

### ✅ Specialised Support for Women
- [x] Women's resource pack in distress alerts
- [x] Unsafe family → routes away from guardians
- [x] 3 government resource categories (HHS, DOJ, NIMH)
- [x] Legal aid connections
- [x] Trusted contact network (non-family)
- [x] Abuse-keyword detection (16 indicators)
- [x] Safety planning resources

### ✅ Interfaces & Deployment
- [x] Streamlit Web UI (local)
- [x] CLI (`python wellness_buddy.py`)
- [x] Network UI (`bash start_ui_network.sh`)
- [x] Mobile-friendly (responsive Streamlit)

---

*"Your emotional wellbeing journey is important. AI Wellness Buddy is here to support you every step of the way."* 💙🌟
