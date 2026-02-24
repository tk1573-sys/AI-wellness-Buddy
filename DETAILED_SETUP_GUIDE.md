# AI Wellness Buddy — Complete Step-by-Step Setup Guide

> **Version**: 3.0 — Feb 2026  
> Covers the six-module agent architecture with password-protected profiles,  
> multi-emotion analysis, OLS prediction, severity-based guardian alerts, and the six-tab Streamlit UI.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Requirements](#2-system-requirements)
3. [Pre-Installation Checklist](#3-pre-installation-checklist)
4. [Installation](#4-installation)
5. [First Run — Creating Your Profile](#5-first-run--creating-your-profile)
6. [Using the Six-Tab Dashboard](#6-using-the-six-tab-dashboard)
7. [Password Protection Setup](#7-password-protection-setup)
8. [Guardian Alert Setup](#8-guardian-alert-setup)
9. [Configuration](#9-configuration)
10. [Advanced Usage](#10-advanced-usage)
11. [Testing Your Installation](#11-testing-your-installation)
12. [Troubleshooting](#12-troubleshooting)
13. [Uninstallation](#13-uninstallation)

---

## 1. Introduction

AI Wellness Buddy is a privacy-first emotional support application.  
All processing is **local** — no data is ever sent to external servers.

### What You Will Set Up

By the end of this guide you will have:

- ✅ Python 3.8+ and all dependencies installed
- ✅ The six-module agent system running
- ✅ A password-protected personal profile created
- ✅ Guardian / emergency contacts configured
- ✅ The six-tab Streamlit dashboard running
- ✅ All 12 automated tests passing

### Time Required

| Step | Time |
|---|---|
| Dependency installation | 5–10 min |
| Profile creation | 5 min |
| Guardian setup | 2 min |
| Testing | 5 min |
| **Total** | **~20 min** |

---

## 2. System Requirements

### Minimum

| Requirement | Value |
|---|---|
| Python | 3.8 or higher |
| RAM | 512 MB |
| Disk space | 100 MB |
| OS | Windows 10 / macOS 10.14 / Ubuntu 18.04 or later |
| Browser | Chrome, Firefox, Safari, or Edge (for Streamlit UI) |

### Recommended

| Requirement | Value |
|---|---|
| Python | 3.10+ |
| RAM | 2 GB |
| Disk space | 500 MB |

### Python Dependencies

All dependencies are listed in `requirements.txt`:

```
nltk>=3.8.1
textblob>=0.17.1
python-dateutil>=2.8.2
streamlit>=1.28.0
cryptography>=41.0.0
numpy>=1.24.0
pandas>=2.0.0
plotly>=5.15.0
scikit-learn>=1.3.0
```

---

## 3. Pre-Installation Checklist

Before you start, verify:

- [ ] Python 3.8+ installed: `python --version` or `python3 --version`
- [ ] `pip` available: `pip --version`
- [ ] Internet connection (for downloading packages — not needed after installation)
- [ ] ~100 MB free disk space
- [ ] A web browser for the Streamlit UI

---

## 4. Installation

### Step 1 — Get the Code

```bash
# Option A: Clone from GitHub
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy

# Option B: Download ZIP and extract, then:
cd AI-wellness-Buddy
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: On some systems use `pip3` instead of `pip`.

### Step 3 — Download NLTK Data (first time only)

```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

> TextBlob uses NLTK internally. This is a one-time download (~3 MB).

### Step 4 — Verify Installation

```bash
python -c "from emotion_analyzer import EmotionAnalyzer; print('✓ EmotionAnalyzer OK')"
python -c "from prediction_agent import PredictionAgent; print('✓ PredictionAgent OK')"
python -c "import streamlit; print('✓ Streamlit', streamlit.__version__)"
```

All three lines should print `✓` without errors.

---

## 5. First Run — Creating Your Profile

### Launch the Web UI

```bash
streamlit run ui_app.py
```

Your browser opens automatically at `http://localhost:8501`.  
If not, navigate there manually.

### Welcome Screen

You will see:
```
🌟 AI Wellness Buddy
Welcome! Let's set up your profile

[ Load Existing Profile ]  [ Create New Profile ]
```

Click **Create New Profile**.

### Profile Creation Form

Fill in the fields:

| Field | Notes |
|---|---|
| **Username *** | Private — never displayed to others. Choose something memorable. |
| **Preferred name** | How the buddy addresses you in every message (e.g. "Jordan") |
| **Age** | Optional. Spinner, defaults to 18. |
| **Occupation / Student status** | Injected into relevant responses (e.g. "M.Tech Student") |
| **How do you identify?** | Enables specialized women's support resources if Female |
| **What brings you here?** | Multi-select primary concerns — personalises the experience |
| **Do you feel safe with family?** | (Female users only) If No, guardian alerts are re-routed to trusted friends |
| **Guardian's name** | Person to be notified in a distress alert |
| **Relationship** | e.g. Parent, Counsellor, Friend |
| **Phone / Email** | Contact details shown in distress alerts |

### Password Section (new in v3.0)

```
🔒 Profile Password (recommended for privacy)
Set a password so only you can open this profile. Leave blank to skip.

[ Password (min 8 characters) ]  [ Confirm password ]
```

**If you set a password**:
- The password is never stored in plain text
- SHA-256 hashing with a random salt is applied
- 3 failed login attempts → 15-minute lockout
- You can change or remove it later from the Profile tab

**If you skip the password**:
- The profile opens with a single click (no password required)
- You can add a password later from the Profile tab → Manage → Set / Change Password

Click **✅ Create My Profile**.

---

## 6. Using the Six-Tab Dashboard

After profile creation (or after unlocking with a password), the main dashboard opens.

### 💬 Chat Tab (default)

- Type in the input box at the bottom: "Share how you're feeling, Jordan…"
- The buddy replies with a personalized, emotion-aware message
- The **live metrics bar** updates after every message:
  - **Messages**: total in this session
  - **Trend**: improving / stable / declining
  - **Severity**: LOW / MEDIUM / HIGH
  - **Sentiment**: weighted average, −1 to +1
- When sustained distress is detected, an inline alert appears with crisis resources

### 📈 Emotional Trends Tab

- **Sentiment line chart**: your polarity score per message, color-coded green→red
- **Emotion distribution pie**: proportion of joy/sadness/anxiety/anger/neutral this session
- **Long-term bar chart**: average sentiment per session (last 30 sessions)

### 📅 Weekly Summary Tab

- **Daily sentiment bar**: average mood per day for the last 7 days
- **Session comparison bar**: total vs. distress messages per session
- Falls back gracefully if you have fewer than 7 days of history

### 🔮 Risk Prediction Tab

- **Forecast chart**: your observed sentiment (blue) + predicted next 5 messages (red dashed)
- **Early-warning threshold line**: alerts you when your trajectory crosses −0.35
- **Model metrics**: MAE, RMSE, confidence — useful for research / M.Tech evaluation
- The prediction engine uses OLS linear regression over your last 7 messages
  (replace one function with an LSTM forward-pass for the advanced version)

### 🚨 Guardian Alerts Tab

- **Guardian contact card**: who will be contacted in a crisis
- **Alert log**: every alert this session — severity, score, timestamp
- **Pending alerts**: if an alert is waiting, you see the full details and two buttons:
  - **✅ Consent to notify guardians** — your guardian's contact details become actionable
  - **✔ Acknowledge** — marks the alert as seen and stops escalation
- **Severity guide**: explains each of the 5 levels (INFO → CRITICAL)

### 👤 Profile Tab

- Displays all your profile information
- **Password status badge**: 🔒 or 🔓
- **Manage** dropdown:
  - Add Trusted Contact
  - Add Guardian Contact
  - Set / Change Password
  - Remove Password
  - Delete All My Data

### Sidebar

Always visible while in the main dashboard:

- Your name, occupation, age, session number, focus areas
- **📞 Help & Resources** — crisis numbers injected into chat
- **⚙️ Manage Profile** — quick contact management
- **🚪 End Session** — saves your data and returns to the welcome screen

---

## 7. Password Protection Setup

### Setting a Password at Profile Creation

On the creation form, scroll to the **🔒 Profile Password** section and enter your chosen password (min 8 characters) twice.

### Setting a Password After Creation

1. Open the **👤 Profile** tab
2. In **Manage** dropdown, select **Set / Change Password**
3. Enter new password + confirm
4. Click **🔒 Save Password**

### Changing Your Password

Same as above — overwriting an existing password follows the same flow.

### Removing Your Password

1. Open the **👤 Profile** tab
2. In **Manage** dropdown, select **Remove Password**
3. Enter your **current** password to confirm
4. Click **🔓 Remove Password**

### What Happens at Login

When you click **Load Profile** for a password-protected profile:

```
🔒 Password Required for username

⚠️ 1 failed attempt(s). 2 remaining before lockout.  ← shows if any failures

[Enter your profile password]  [👁 show/hide]

[ 🔓 Unlock Profile ]   [ ← Back ]
```

After 3 failed attempts the account is locked for 15 minutes:

```
🔒 Account locked due to too many failed login attempts.
Please try again in 15 minutes.
```

---

## 8. Guardian Alert Setup

### Adding a Guardian Contact

**During profile creation** — fill in the Guardian section of the form.

**After creation** — use either:
- **Profile tab** → Manage → Add Guardian Contact
- **Sidebar** → Manage Profile → Add Guardian Contact

### How Alerts Work

```
User sends several distress messages
         ↓
consecutive_distress ≥ 3  (SUSTAINED_DISTRESS_COUNT)
         ↓
Alert triggered at severity: INFO / LOW / MEDIUM / HIGH / CRITICAL
         ↓
Alert appears inline in Chat + in Guardian Alerts tab
         ↓
User reviews guardian contact details in "Pending Alerts" expander
         ↓
User clicks "✅ Consent to notify guardians"
         ↓
guardian_consent = True  → guardians' details are actionable
         ↓
User clicks "✔ Acknowledge" → alert stops escalating
```

### Severity Levels

| Level | What triggered it | Auto-escalates after |
|---|---|---|
| 🟢 INFO | Minor distress detected | 60 min |
| 🟡 LOW | Mild sustained negativity | 30 min |
| 🟠 MEDIUM | Moderate distress | 15 min |
| 🔴 HIGH | Severity score ≥ 7/10 | 5 min |
| 🚨 CRITICAL | Sustained HIGH + abuse indicators | Never (immediate) |

---

## 9. Configuration

All settings are in `config.py`. Defaults work well for most users.

### Key Settings to Customize

```python
# How many consecutive distress messages trigger an alert
SUSTAINED_DISTRESS_COUNT = 3       # default: 3

# How long user session lasts without interaction
SESSION_TIMEOUT_MINUTES = 30       # default: 30

# Minimum password length
MIN_PASSWORD_LENGTH = 8            # default: 8

# Failed login lockout
MAX_LOGIN_ATTEMPTS = 3             # default: 3
LOCKOUT_DURATION_MINUTES = 15      # default: 15

# Prediction model window
PREDICTION_WINDOW = 7              # default: 7 messages

# Early warning trigger
EARLY_WARNING_THRESHOLD = -0.35    # default: -0.35 (negative = distress)
```

---

## 10. Advanced Usage

### CLI Mode

```bash
python wellness_buddy.py
```

Commands during CLI session:
- `help` — show crisis resources and trusted contacts
- `status` — current session and long-term pattern summary
- `profile` — add contacts, update safety settings, delete data
- `quit` — save and exit

### Network / LAN Mode

Allow access from other devices on your network:

```bash
bash start_ui_network.sh
# → http://YOUR-LAN-IP:8501
```

Or directly:

```bash
streamlit run ui_app.py --server.address 0.0.0.0 --server.port 8501
```

### Multiple Profiles

Any number of profiles can be created — each stored as a separate encrypted file.  
At the welcome screen, select any username from the **Load Existing Profile** dropdown.

### Encrypted Data Files

All data is stored in `~/.wellness_buddy/`.  
To inspect a raw file:
```bash
ls -la ~/.wellness_buddy/
```
Files are AES-256 encrypted — you cannot read them directly.

---

## 11. Testing Your Installation

```bash
python -m pytest test_wellness_buddy.py -v
```

### Expected Output (12 tests, all pass)

```
test_wellness_buddy.py::test_emotion_analysis           PASSED
test_wellness_buddy.py::test_pattern_tracking           PASSED
test_wellness_buddy.py::test_alert_system               PASSED
test_wellness_buddy.py::test_conversation_handler       PASSED
test_wellness_buddy.py::test_user_profile               PASSED
test_wellness_buddy.py::test_data_persistence           PASSED
test_wellness_buddy.py::test_full_workflow              PASSED
test_wellness_buddy.py::test_multi_emotion_classification PASSED
test_wellness_buddy.py::test_time_weighted_distress     PASSED
test_wellness_buddy.py::test_prediction_agent           PASSED
test_wellness_buddy.py::test_alert_severity_escalation  PASSED
test_wellness_buddy.py::test_password_protection        PASSED

12 passed in X.XXs
```

### What Each Test Validates

| Test | Validates |
|---|---|
| `test_emotion_analysis` | TextBlob polarity, distress keywords, severity label |
| `test_pattern_tracking` | Consecutive distress counter, trend detection, sustained distress |
| `test_alert_system` | Alert trigger, severity formatting, women's resources |
| `test_conversation_handler` | Response generation for all emotion categories |
| `test_user_profile` | All profile field setters, trusted contacts, gender-based support |
| `test_data_persistence` | Save / load / list / delete encrypted data |
| `test_full_workflow` | End-to-end: abuse keywords → HIGH alert → guardian notification |
| `test_multi_emotion_classification` | 5-category scores, dominant emotion, severity score 0–10 |
| `test_time_weighted_distress` | Time-weighted sentiment, severity_level, emotion_distribution |
| `test_prediction_agent` | OLS prediction, MAE/RMSE accumulation, 5-step forecast |
| `test_alert_severity_escalation` | 5 levels, escalation timing, acknowledge + log |
| `test_password_protection` | set/verify/wrong/lockout/remove/reset, `pytest.raises(ValueError)` |

---

## 12. Troubleshooting

### Port Already in Use

```
OSError: [Errno 98] Address already in use
```

Solution:
```bash
streamlit run ui_app.py --server.port 8502
# Navigate to http://localhost:8502
```

### NLTK Data Not Found

```
LookupError: Resource brown not found.
```

Solution:
```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### Cryptography / Fernet Error

```
ModuleNotFoundError: No module named 'cryptography'
```

Solution:
```bash
pip install cryptography>=41.0.0
```

### Streamlit Not Found

```
command not found: streamlit
```

Solution:
```bash
pip install streamlit>=1.28.0
# If still not found, try:
python -m streamlit run ui_app.py
```

### Charts Not Showing

```
Install pandas and plotly for charts: pip install pandas plotly
```

Solution:
```bash
pip install pandas plotly
```

### Profile Locked Out

If you are locked out of a profile (3 failed login attempts), wait 15 minutes and try again.  
The lockout expires automatically — you do not need to delete the profile.

### All Tests Failing

```bash
# Check your Python version
python --version

# Re-install all dependencies
pip install -r requirements.txt

# Re-download NLTK data
python -c "import nltk; nltk.download('all')"
```

---

## 13. Uninstallation

### Remove the Application

```bash
# Remove the application directory
rm -rf /path/to/AI-wellness-Buddy

# Remove user data (optional — this deletes all profiles permanently)
rm -rf ~/.wellness_buddy/
```

### Remove Python Packages

```bash
pip uninstall -r requirements.txt -y
```

---

## Quick Reference Card

```bash
# Start web UI
streamlit run ui_app.py

# Start CLI
python wellness_buddy.py

# Run all tests
python -m pytest test_wellness_buddy.py -v

# Network mode (accessible from LAN)
bash start_ui_network.sh

# Install / update dependencies
pip install -r requirements.txt

# Data location
ls ~/.wellness_buddy/
```

---

**You are not alone. Help is available 24/7.**

- Crisis Hotline: **988**
- Crisis Text Line: Text HOME to **741741**
- Emergency: **911**
