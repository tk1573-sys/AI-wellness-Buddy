# AI Emotional Wellness Buddy 🌟

An AI-powered emotional wellness support system that provides **personalized text-based emotional support**, tracks emotional patterns over time, predicts emotional trends, and triggers multi-level alerts when sustained distress is detected.  Built as a six-module agent-based architecture with a multi-tab analytics dashboard.

---

## 🎯 What Does This Project Do?

| Capability | Description |
|---|---|
| 🗣️ Personalized Support | Empathetic replies tuned to your exact emotion (sadness, anxiety, anger, joy) and addressed by your name |
| 📊 Multi-Emotion Analysis | Classifies every message into five emotion categories with confidence scores |
| 📈 Trend Monitoring | Time-weighted sliding window detects whether your mood is improving, stable, or worsening |
| 🔮 Predictive Model | OLS linear-regression temporal model predicts your next emotional state and issues early warnings |
| 🚨 Smart Alerts | Five-level severity (INFO → CRITICAL) with auto-escalation and a consent-based guardian notification |
| 📉 Analytics Dashboard | Six-tab Streamlit UI with live charts: sentiment line, emotion pie, weekly bar, forecast chart, alert log |
| 🔒 Privacy & Security | AES-256 encryption, password protection, session timeout, account lockout, local-only storage |

---

## 🏗️ Architecture — Six Agent Modules

```
┌────────────────────────────────────────────────────────────────────────┐
│  wellness_buddy.py  ← orchestrates all modules                        │
│                                                                        │
│  Module 1          emotion_analyzer.py    Multi-emotion classifier    │
│  Module 2          pattern_tracker.py     Time-weighted distress mon. │
│  Module 3          prediction_agent.py    Temporal trend predictor    │
│  Module 4          conversation_handler.py  Context-aware responses   │
│  Module 5          alert_system.py        Severity-based guardian     │
│  Module 6          ui_app.py              Multi-tab analytics UI      │
│                                                                        │
│  Support layer     user_profile.py  data_store.py  config.py         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Feature Overview

### Module 1 — Emotion Analysis Agent

**Multi-label emotion classification** using keyword-frequency + TextBlob polarity fusion:

| Category | Keywords detected (examples) |
|---|---|
| 😢 Sadness | sad, depressed, hopeless, grief, lonely, heartbroken … |
| 😰 Anxiety | anxious, worried, stressed, panic, overwhelmed, insomnia … |
| 😠 Anger | angry, furious, frustrated, rage, resentment … |
| 😊 Joy | happy, grateful, excited, wonderful, content … |
| 😐 Neutral | everything else |

**Output per message:**
```json
{
  "emotion_scores": {"joy": 0.0, "sadness": 0.616, "anxiety": 0.384, "anger": 0.0, "neutral": 0.0},
  "dominant_emotion": "sadness",
  "severity_score": 7.79,
  "emotion": "distress",
  "severity": "high",
  "polarity": -0.48,
  "distress_keywords": ["hopeless", "can't take it"],
  "abuse_indicators": []
}
```

**Research comparison**: rule-based keyword+polarity fusion vs. ML-based approach.

---

### Module 2 — Distress Monitoring Agent

**Time-weighted sliding window** analysis with exponential decay:

- Recent messages weighted higher (`TIME_DECAY_FACTOR = 0.85`)
- **Numeric severity score 0–10** derived from weighted average
- Named severity level: `LOW` / `MEDIUM` / `HIGH`
- Emotion distribution aggregated across the window
- Consecutive distress counter triggers sustained-distress detection

**Pattern summary (new fields):**
```json
{
  "weighted_sentiment": -0.48,
  "severity_score": 7.79,
  "severity_level": "HIGH",
  "emotion_distribution": {"sadness": 0.55, "anxiety": 0.38, "anger": 0.0, "joy": 0.0, "neutral": 0.07},
  "trend": "declining",
  "sustained_distress_detected": true
}
```

---

### Module 3 — Pattern Prediction Agent *(NEW)*

**Temporal emotional-state prediction** — the publishable M.Tech research component:

| Feature | Detail |
|---|---|
| Model | OLS linear regression over sliding window (drop-in for LSTM) |
| Output | Predicted next sentiment score (−1 to +1) |
| Trend | improving / stable / worsening |
| Confidence | 0–1 variance-based estimate |
| Forecast | 5-step forecast series for chart rendering |
| Early warning | Fires when predicted sentiment < −0.35 |
| Metrics | MAE, RMSE (accumulated per session) |

**Research angle — temporal distress modelling:**
> Replace `_linreg_predict()` in `prediction_agent.py` with an LSTM `forward()` call when labelled training data is available. The rest of the pipeline (data ingestion, metric accumulation, forecast rendering) stays unchanged.

---

### Module 4 — Response Generation Agent

**Context-aware, personalized responses** — no more repetitive generic replies:

- Template banks per emotion category (4 variants each: joy, sadness, anxiety, anger, neutral, distress)
- Consecutive-response deduplication (never repeats the same template twice in a row)
- User's **preferred name** included in every reply
- **Occupation context** injected for distress/negative responses
- Abuse-indicator override appends specialised safety message

Example (anxiety + name "Alex" + occupation "M.Tech Student"):
> *"Anxiety can be overwhelming Alex as a M.Tech Student. You're not alone — I'm here to help you find calm."*

---

### Module 5 — Guardian Alert Agent

**Five-level severity system** with escalation, logging, and consent:

| Severity | Trigger | Escalates after |
|---|---|---|
| 🟢 INFO | Minor concern | 60 min |
| 🟡 LOW | Mild sustained negativity | 30 min |
| 🟠 MEDIUM | Moderate distress | 15 min |
| 🔴 HIGH | Sustained high distress | 5 min |
| 🚨 CRITICAL | Severe distress + abuse indicators | Immediate |

**New features:**
- Structured **alert log** with timestamps (CSV-exportable from UI)
- **Consent mechanism** — guardian contacts are only shared after explicit user approval
- Auto-escalation of unacknowledged alerts
- `acknowledge_alert()` + `grant_guardian_consent()` API

---

### Module 6 — Visualization Agent (Multi-Tab UI)

**Six-tab Streamlit dashboard:**

| Tab | Charts & Content |
|---|---|
| 💬 Chat | Live metrics bar (messages, trend, severity, weighted sentiment) + personalized chat |
| 📈 Emotional Trends | Sentiment line chart (colour-coded markers) + emotion distribution donut pie |
| 📅 Weekly Summary | Daily sentiment bar chart + session message-count comparison |
| 🔮 Risk Prediction | Forecast chart with early-warning threshold line + model metrics panel |
| 🚨 Guardian Alerts | Guardian contact card, alert log table, pending alert expanders with consent/acknowledge |
| 👤 Profile | Full profile view, trusted contacts, guardian contacts, inline management |

---

## 👤 Full Profile Creation

The profile form collects all relevant personal details:

| Field | Description |
|---|---|
| Username | Private identifier (never shared) |
| Preferred name | How the buddy addresses you in every message |
| Age | Optional — used for context |
| Occupation / student status | Injected into relevant responses |
| Gender | Enables women-specific resources if needed |
| Primary concerns | Multi-select: Stress, Depression, Loneliness, Relationship Issues, Work Pressure, Grief, Self-esteem, Trauma, etc. |
| Family safety (women) | Marks family/guardians as unsafe → routes alerts to trusted friends & women's organizations |
| Guardian name | Emergency contact shown in distress alerts |
| Guardian relationship | e.g. Parent, Counsellor, Friend |
| Guardian phone / email | Contact details shown in alert |

---

## 🔒 Security & Privacy

| Feature | Detail |
|---|---|
| AES-256 encryption | All profile data encrypted at rest using Fernet |
| Password protection | SHA-256 hashing with unique salt per profile |
| Session timeout | Auto-logout after 30 minutes of inactivity |
| Account lockout | 3 failed attempts → 15-minute lockout |
| Data integrity | SHA-256 file hash for tamper detection |
| Local-only storage | `~/.wellness_buddy/` — nothing sent externally |
| Owner-only permissions | `chmod 600` on data and key files |
| Automatic backups | Timestamped backups before every save |
| Full deletion | Delete all data from the Profile tab at any time |

---

## 🌐 User Interfaces

### Option 1 — Web UI (recommended)
```bash
streamlit run ui_app.py
# → http://localhost:8501
```
Full six-tab analytics dashboard (Module 6).

### Option 2 — CLI
```bash
python wellness_buddy.py
```
Commands:
- `help` — show crisis resources and your trusted contacts
- `status` — view current session and long-term emotional pattern summary
- `profile` — add trusted/guardian contacts, update safety settings, delete data
- `quit` — end the session and save your progress

### Option 3 — Network UI
```bash
bash start_ui_network.sh
# → http://YOUR-IP:8501  (accessible from any device on your network)
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download NLTK data (first time only)
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"

# 3. Launch
streamlit run ui_app.py
```

Then in the browser:
1. On the **Welcome** screen: choose **Create New Profile** or **Load Existing Profile**
2. Fill in the **full profile form** (name, age, occupation, concerns, guardian contact) and click "Create My Profile"
3. Start chatting — the buddy addresses you by name immediately
4. Explore **Emotional Trends**, **Risk Prediction**, and **Guardian Alerts** tabs as your data grows

---

## 📞 Crisis Resources

### General Support
- **Crisis Hotline**: 988 (Suicide & Crisis Lifeline)
- **Crisis Text Line**: Text HOME to 741741
- **SAMHSA Hotline**: 1-800-662-4357
- **Emergency**: 911

### Women's Specialized Support
- **Domestic Violence Hotline**: 1-800-799-7233
- **Domestic Violence Text**: Text START to 88788
- **RAINN Sexual Assault Hotline**: 1-800-656-4673
- **Safety Planning**: thehotline.org

### Government Resources
- Office on Women's Health (HHS): 1-800-994-9662
- Violence Against Women Office (DOJ): 202-307-6026
- National Women's Law Center: 202-588-5180

---

## 🛠️ Configuration (`config.py`)

| Setting | Default | Description |
|---|---|---|
| `DISTRESS_THRESHOLD` | −0.3 | Sentiment below this = distress |
| `SUSTAINED_DISTRESS_COUNT` | 3 | Consecutive messages to trigger alert |
| `PATTERN_TRACKING_WINDOW` | 10 | Sliding window size |
| `TIME_DECAY_FACTOR` | 0.85 | Exponential weight for older messages |
| `SEVERITY_HIGH_THRESHOLD` | 7.0 | Score (0-10) for HIGH severity |
| `SEVERITY_MEDIUM_THRESHOLD` | 4.0 | Score (0-10) for MEDIUM severity |
| `PREDICTION_WINDOW` | 7 | Data points for prediction model |
| `EARLY_WARNING_THRESHOLD` | −0.35 | Predicted sentiment for early warning |
| `EMOTIONAL_HISTORY_DAYS` | 365 | Days of history to retain |
| `MAX_ALERT_LOG_ENTRIES` | 100 | Alert log size cap |

---

## 🏗️ Project Structure

```
AI-wellness-Buddy/
├── wellness_buddy.py       # Orchestrator — integrates all 6 modules
├── emotion_analyzer.py     # Module 1: multi-emotion classifier
├── pattern_tracker.py      # Module 2: time-weighted distress monitoring
├── prediction_agent.py     # Module 3: temporal prediction (OLS / LSTM-ready)
├── conversation_handler.py # Module 4: context-aware response generation
├── alert_system.py         # Module 5: severity-based guardian alert agent
├── ui_app.py               # Module 6: six-tab Streamlit analytics dashboard
├── user_profile.py         # Full profile (name/age/occupation/concerns/guardians)
├── data_store.py           # Encrypted local JSON storage
├── config.py               # All tunable parameters
├── requirements.txt        # Python dependencies
├── test_wellness_buddy.py  # 11 automated tests (pytest)
└── docs/
    ├── README.md                    ← this file
    ├── COMPLETE_FEATURE_GUIDE.md    ← detailed feature reference
    ├── SECURITY.md                  ← security deep-dive
    ├── DATA_RETENTION.md            ← 365-day tracking details
    ├── TECHNOLOGIES_AND_DATASETS.md ← libraries & datasets
    ├── MTECH_PROJECT_ASSESSMENT.md  ← academic suitability analysis
    └── NETWORK_DEPLOYMENT.md        ← cloud / LAN deployment
```

---

## 🧪 Testing

```bash
# Run all 11 tests
python -m pytest test_wellness_buddy.py -v

# Tests cover:
#  1. Emotion analysis          5. User profile management
#  2. Pattern tracking          6. Data persistence
#  3. Alert system              7. Full workflow (abuse detection)
#  4. Conversation responses    8. Multi-emotion classification
#                               9. Time-weighted distress
#                              10. Prediction agent (MAE/RMSE)
#                              11. Alert severity & escalation
```

---

## 📊 Research Metrics (M.Tech / Academic)

| Metric | Source | Purpose |
|---|---|---|
| Sentiment polarity | TextBlob | Rule-based baseline |
| Emotion scores (5 categories) | Keyword + polarity fusion | Multi-label classification accuracy |
| Severity score (0–10) | Time-weighted window | Distress quantification |
| MAE | `prediction_agent.get_metrics()` | Prediction quality (lower = better) |
| RMSE | `prediction_agent.get_metrics()` | Prediction quality (lower = better) |
| Trend classification accuracy | Predicted vs. actual trend | Temporal model evaluation |
| Alert detection accuracy | Alert log vs. ground truth | System performance |
| Response latency | Session timing | System performance |

---

## ⚠️ Disclaimer

This is a **support tool**, not a replacement for professional mental health care or emergency services.
- For mental health emergencies: call **988**
- For domestic violence emergencies: call **911** or **1-800-799-7233**
- Always consult qualified mental health professionals for ongoing care

---

**You are not alone. Help is available 24/7. You deserve support and care. 💙**

📖 **See [COMPLETE_FEATURE_GUIDE.md](COMPLETE_FEATURE_GUIDE.md) for the full feature reference with code examples.**
