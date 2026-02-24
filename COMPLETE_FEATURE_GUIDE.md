# Complete Feature Guide

## 🌟 AI Wellness Buddy - Complete Feature Documentation

This comprehensive guide covers ALL features available in the AI Wellness Buddy, from basic to advanced functionality.

## Table of Contents
1. [Overview](#overview)
2. [Core Features](#core-features)
3. [Multi-Emotion Detection & XAI](#multi-emotion-detection--xai)
4. [Risk Scoring & Trend Modeling](#risk-scoring--trend-modeling)
5. [Emotion Forecasting (Prediction Agent)](#emotion-forecasting-prediction-agent)
6. [Personal History & Context Awareness](#personal-history--context-awareness)
7. [Response Style & Personalization](#response-style--personalization)
8. [Gamification (Mood Streak & Badges)](#gamification-mood-streak--badges)
9. [Extended Tracking Features](#extended-tracking-features)
10. [Security Features](#security-features)
11. [Specialized Support Features](#specialized-support-features)
12. [Guardian Alert System](#guardian-alert-system)
13. [Government Resources for Women](#government-resources-for-women)
14. [User Interface Options](#user-interface-options)
15. [Data Management](#data-management)
16. [Advanced Configuration](#advanced-configuration)
17. [Feature Comparison](#feature-comparison)
18. [Frequently Asked Questions](#frequently-asked-questions)

---

## Overview

The AI Wellness Buddy is a comprehensive emotional support system with the following capabilities:

### Quick Feature List

✅ **Multi-Emotion Classification**
- 6 fine-grained emotions: joy, sadness, anger, fear, anxiety, crisis
- Keyword-driven detection with polarity fallback
- Crisis detection with immediate 988/911 escalation
- XAI keyword attribution in every response

✅ **Intelligent Risk Scoring**
- Formula-based Low / Medium / High / Critical risk level
- Emotional volatility and stability index (0–1 scale)
- Moving average smoothing of sentiment history
- Emotion distribution breakdown per session

✅ **Emotion Forecasting**
- OLS linear regression next-session mood prediction
- Risk escalation forecast (will risk worsen?)
- Displayed in `status`, Weekly Report, and Trends tab

✅ **Personal History & Awareness**
- Trauma history stored for extra-sensitive responses
- Personal triggers flagged for gentle acknowledgement
- Marital/relationship status used for life-transition empathy
- Family background for culturally-aware context

✅ **Response Style Personalization**
- Choose Short, Balanced (default), or Detailed replies
- All 6 emotion templates have 3 style variants

✅ **Gamification**
- Mood streak: consecutive positive-mood sessions
- 8 wellness badge types awarded at session end
- Weekly summary report with improvement suggestions

✅ **Extended Tracking**
- 365-day emotional history (up from 90 days)
- Long-term pattern analysis
- Seasonal trend detection
- Progress milestone tracking

✅ **Enhanced Security**
- Password-protected profiles
- AES-256 data encryption
- Session timeout protection
- Account lockout security
- Data integrity verification

✅ **Specialized Support**
- Women's safety features
- Trusted contact management
- Abuse detection and resources
- Personalized support networks

✅ **Guardian Alert System**
- Emergency contact notification during severe distress
- Configurable severity thresholds (low/medium/high)
- Privacy-respecting: asks before notifying guardians
- Multiple guardian contacts supported
- Formatted alert messages with crisis resources

✅ **Government Resources for Women**
- 15+ U.S. government agency contacts
- Legal aid and women's law resources
- Women-specific mental health services
- International women's health organizations

✅ **Multiple Interfaces**
- Command-line interface (CLI)
- Web browser UI (Streamlit) with 4-tab analytics dashboard
- Network-accessible UI
- Mobile-friendly design

---

## Core Features

### 1. Emotion Analysis

**Real-time sentiment and multi-emotion analysis** using NLP:

**Technologies:**
- TextBlob for sentiment analysis (polarity −1 to +1)
- NLTK for language understanding
- Custom keyword dictionaries per emotion
- OLS regression for trend forecasting

**What It Analyzes:**
```python
{
  # Coarse fields (backward-compatible)
  "polarity": -0.45,
  "subjectivity": 0.7,
  "emotion": "negative",        # positive / neutral / negative / distress
  "severity": "medium",
  "distress_keywords": ["sad"],
  "abuse_indicators": [],
  "has_abuse_indicators": False,

  # Fine-grained fields (new)
  "primary_emotion": "sadness", # joy / sadness / anger / fear / anxiety / crisis
  "emotion_scores": {"joy": 0, "sadness": 2, "anger": 0, "fear": 0, "anxiety": 0},
  "explanation": "Detected 'sadness' due to keywords: sad, hopeless",
  "is_crisis": False,
  "crisis_keywords": []
}
```

**Example Interaction:**
```
You: I feel so sad and hopeless today.
Wellness Buddy: I'm so sorry you're feeling this way. Your sadness is real and it
  matters — I'm here with you. 💙

  _(Analysis: Detected 'sadness' due to keywords: sad, hopeless)_
```

### 2. Pattern Tracking

**Monitors emotional patterns** over time with configurable windows:

**Session-Level Tracking:**
- Last 10 messages (configurable via `PATTERN_TRACKING_WINDOW`)
- Consecutive distress detection (now tracks fine-grained emotions)
- Trend analysis (improving, stable, declining)
- Moving average (3-message window smooths noise)
- Emotional volatility and stability index (0 = volatile, 1 = stable)
- Emotion distribution: counts per fine-grained emotion
- Formula-based risk score (see Section 4)

**Long-Term Tracking:**
- 365 days of emotional history
- Weekly, monthly, quarterly reviews
- Seasonal pattern detection

**Pattern Summary Example (updated):**
```
📊 Current Session Pattern:
  Messages analyzed: 5
  Emotional trend: DECLINING
  Average sentiment: -0.32 (negative)
  Risk level: HIGH (score: 0.68)
  Stability index: 0.81 (volatility: 0.19)

  Emotion breakdown:
    sadness: 3 message(s)
    anxiety: 2 message(s)

📊 Last 7 Days:
  Check-ins: 5
  Mood streak: 0 positive session(s)
  Overall sentiment: -0.15 (negative)

📡 Next-Session Forecast (medium confidence):
  Neutral to slightly low mood expected — extra self-care may help.
```

### 3. Distress Alert System

**Automatic alerts** when sustained distress is detected:

**Trigger Conditions:**
- 3+ consecutive distress messages (configurable)
- Sustained negative sentiment
- Multiple distress keywords

**Alert Response:**
```
⚠️ EMOTIONAL DISTRESS ALERT ⚠️

I've noticed you've been experiencing sustained emotional distress.
Your wellbeing is important, and you don't have to face this alone.

Please consider reaching out to professional support:

📞 General Support Resources:
  • Crisis Hotline: 988 (Suicide & Crisis Lifeline)
  • Crisis Text Line: Text HOME to 741741
  • Mental Health: SAMHSA National Helpline: 1-800-662-4357
```

**Specialized Alerts** (for women with abuse indicators):
```
🛡️ SPECIALIZED SUPPORT FOR WOMEN 🛡️

  • Domestic Violence Hotline: 1-800-799-7233
  • Domestic Violence Text: Text START to 88788
  • Sexual Assault Hotline: 1-800-656-4673 (RAINN)
  
💚 Your Trusted Contacts:
  • Emma (best friend): 555-1234
  • Sarah (colleague): 555-5678
```

### 4. User Profiles

**Persistent profiles** with personalized support:

**Profile Data:**
```python
{
  "user_id": "username",
  "created_at": "2025-03-01T10:00:00",
  "last_session": "2026-02-24T15:30:00",
  "gender": "female",
  "relationship_status": "single",
  "family_background": "Grew up in a single-parent household.",
  "trauma_history": [{"description": "...", "date": "2024-01-01"}],
  "personal_triggers": ["abandonment", "criticism"],
  "response_style": "balanced",    # short / balanced / detailed
  "mood_streak": 3,                # consecutive positive sessions
  "wellness_badges": ["first_step", "streak_3", "self_aware"],
  "session_count": 14,
  "emotional_history": [...]       # 365-day rolling snapshots
}
```

**Profile Features:**
- Create and load profiles
- Gender-specific support
- Personal history for trauma-aware, trigger-aware responses
- Response style preference (short/balanced/detailed)
- Mood streak and badge tracking
- Trusted contact management
- Safety preferences
- Password protection and session history

---

## Multi-Emotion Detection & XAI

### Emotion Classes

The system classifies each message into one of **6 fine-grained emotions** instead of the old positive/negative:

| Emotion | Example triggers | Risk weight |
|---------|-----------------|-------------|
| `joy` | happy, grateful, elated | 0.00 |
| `neutral` | (polarity fallback) | 0.10 |
| `anxiety` | anxious, overwhelmed, stressed | 0.55 |
| `anger` | angry, furious, resentful | 0.45 |
| `fear` | scared, terrified, dreading | 0.60 |
| `sadness` | sad, depressed, hopeless | 0.65 |
| `crisis` | suicide, self-harm, end my life | 1.00 |

### Crisis Detection

15+ crisis keywords trigger **immediate escalation** regardless of polarity. The `is_crisis` flag is set to `True` and the response directs to 988 immediately:

```
I'm very concerned about what you've shared, and I want you to know that your
life matters deeply. Please reach out to the 988 Suicide & Crisis Lifeline
(call or text 988) right now — they're available 24/7. 💙
```

### XAI — Keyword Attribution

Every non-positive response includes a transparent explanation:

```
_(Analysis: Detected 'anxiety' due to keywords: anxious, overwhelmed)_
```

This helps users understand how the AI is reading their messages.

---

## Risk Scoring & Trend Modeling

### Formula-Based Risk Score

Instead of a simple threshold, the system computes:

```
base_score   = mean(emotion_risk_weight for each recent message)
consec_bonus = min(0.5, consecutive_distress × 0.10)
abuse_boost  = 0.20 if abuse keywords detected, else 0
total_score  = min(1.0, base_score + consec_bonus + abuse_boost)
```

**Levels:**
| Score | Level | Example response |
|-------|-------|-----------------|
| < 0.20 | 🟢 Low | Continue normal support |
| 0.20–0.44 | 🟡 Medium | Show additional resources |
| 0.45–0.69 | 🔴 High | Distress alert triggered |
| ≥ 0.70 | 🚨 Critical | Immediate crisis response |

### Moving Average

The 3-message moving average smooths out single-message noise so the trend chart is more readable.

### Volatility & Stability Index

```python
volatility     = std_dev(sentiment_history)   # 0 = flat, 1 = highly erratic
stability_index = 1.0 - volatility            # 0 = unstable, 1 = perfectly stable
```

Both are shown in `status` and the ⚠️ Risk Dashboard tab.

---

## Emotion Forecasting (Prediction Agent)

### Next-Session Sentiment Prediction

Using **Ordinary Least Squares (OLS) linear regression** on past session sentiment values:

```python
prediction = {
    "predicted_value": -0.12,           # next expected polarity
    "trend_slope":     -0.035,          # rate of change per session
    "confidence":      "medium",        # low (3-4 pts) / medium (5-9) / high (10+)
    "interpretation":  "Neutral to slightly low mood expected — extra self-care may help.",
    "data_points_used": 7
}
```

### Risk Escalation Prediction

```python
risk_escalation = {
    "will_escalate":   True,
    "predicted_risk":  0.72,
    "recommendation":  "Risk appears to be increasing. Consider proactive check-in..."
}
```

Both predictions are shown in:
- The `status` command output
- The 📋 Weekly Report tab
- The 📈 Emotional Trends tab

No external ML dependencies required — pure Python OLS.

---

## Personal History & Context Awareness

### Profile Fields

| Field | Purpose |
|-------|---------|
| `trauma_history` | List of past trauma entries — responses add extra sensitivity |
| `personal_triggers` | Words/topics to acknowledge gently if mentioned in a message |
| `relationship_status` | Used for life-transition empathy (divorce, bereavement, etc.) |
| `family_background` | Background context for culturally-sensitive responses |

### Setting Up in the CLI

During profile creation you will be asked:
```
Relationship / marital status: divorced
Family background (optional): Single parent; estranged from parents.
Any trauma or significant loss? (optional): Lost spouse in 2023.
Sensitive topics (comma-separated, optional): death, hospital
```

You can also add or update this information later:
```
You: profile
> 4. View personal history
> 5. Add trauma / trigger
```

### How It Affects Responses

When a personal trigger is detected in a message:
```
I noticed you touched on something that may feel especially sensitive for you.
It's completely okay to go at your own pace — I'm here with you, no matter what.
```

When the user has trauma history and expresses sadness:
```
I also want you to know — given everything you've been through before, your
resilience is real. You are not alone in this moment. 💙
```

---

## Response Style & Personalization

### Choosing a Style

Set during profile creation or via `profile > Change response style`:

| Style | Description | Best for |
|-------|-------------|---------|
| `short` | 1–2 sentences, direct | Users who prefer brevity |
| `balanced` | 2–4 sentences (default) | Most users |
| `detailed` | 4–6 sentences with questions | Users who want more dialogue |

### Example (Anxiety, all three styles)

**Short:**
> Anxiety is exhausting. Take a slow breath — I'm here with you.

**Balanced:**
> Anxiety is exhausting, and I hear you. Take a slow breath — I'm right here with you. 💙

**Detailed:**
> Anxiety can be completely exhausting — your mind and body are working so hard. I want you to know that what you're feeling is real and understandable, and I'm here to sit with you through it. 💙 Sometimes it helps to just name what you're anxious about — would you like to try?

---

## Gamification (Mood Streak & Badges)

### Mood Streak

The system counts **consecutive sessions where the average sentiment is positive (> 0)**. The streak is shown at session end and in the ⚠️ Risk Dashboard.

```
🔥 Mood Streak: 3 consecutive positive session(s)
```

The streak resets to 0 after a negative or distress session.

### Wellness Badges

Eight badges are awarded automatically at session end:

| Badge | Condition |
|-------|----------|
| 🌱 First Step | Complete your first session |
| 📅 Consistent | Complete 7 sessions |
| 💪 Dedicated | Complete 30 sessions |
| 🔥 3-Day Streak | 3 consecutive positive sessions |
| ⭐ 7-Day Streak | 7 consecutive positive sessions |
| 🌈 Resilient | Recover from a High/Critical risk session |
| 🧠 Self-Aware | Add trauma history or personal triggers |
| 💚 Connected | Add a trusted contact |

Badges are shown in the ⚠️ Risk Dashboard and at session end.

### Weekly Summary Report

Type `weekly` (or `report`) to get a 7-day report:

```
📋 WEEKLY WELLNESS SUMMARY

📅 Period         : Last 7 days
✅ Check-ins       : 5
📈 Average mood    : -0.08 — 😐 Neutral / Mixed
⚠️  Risk incidents  : 1
🔥 Mood streak     : 0 positive session(s)

🎭 Emotion Distribution:
   sadness       3 messages  (60%)
   anxiety       1 messages  (20%)
   neutral       1 messages  (20%)

📡 Next-Session Forecast (medium confidence):
   Neutral to slightly low mood expected — extra self-care may help.

💡 Suggestions:
   - Consider reaching out to a friend or trusted contact this week.
   - Try one small act of self-care today — even a short walk helps.
```

---

## Extended Tracking Features

### 1. One Year Emotional History

**365 days of continuous tracking** (upgraded from 90 days):

**What's Tracked:**
- Daily emotional snapshots
- Session summaries
- Sentiment trends
- Distress patterns
- Milestone progress

**Benefits:**
```
✨ See full year of progress
📈 Identify seasonal patterns
🎯 Track long-term goals
📊 Better trend analysis
🌟 Understand your journey
```

**Historical View:**
```bash
python wellness_buddy.py
> status full

📊 Full Year Overview (365 days):
  Total check-ins: 243
  Average sentiment: +0.08
  
  Best month: June 2025 (+0.45)
  Most challenging: January 2026 (-0.15)
  
  Overall trend: Improving ✨
  Current vs start: +0.40 improvement
```

### 2. Seasonal Pattern Detection

**Automatic detection** of seasonal variations:

**Seasonal Analysis:**
```
🌸 Spring (Mar-May): +0.35 avg sentiment
☀️ Summer (Jun-Aug): +0.42 avg sentiment
🍂 Fall (Sep-Nov): +0.28 avg sentiment
❄️ Winter (Dec-Feb): -0.05 avg sentiment

Insight: You tend to feel better in summer months.
Consider planning extra self-care in winter.
```

### 3. Progress Milestones

**Track progress** from important events:

**Setting Milestones:**
```python
# Mark significant dates
profile.add_milestone("Started therapy", "2025-08-01")
profile.add_milestone("New job", "2025-10-15")
profile.add_milestone("Relationship ended", "2025-12-01")
```

**Viewing Progress:**
```
Progress Since "Started therapy" (205 days ago):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before: -0.20 avg sentiment, 45% distress ratio
After:  +0.30 avg sentiment, 15% distress ratio
Change: +0.50 improvement, -30% less distress ✨

Best streak: 60 consecutive days of positive mood
```

### 4. Data Archiving

**Automatic archiving** of old conversations:

**Configuration:**
```python
CONVERSATION_ARCHIVE_DAYS = 180  # Archive after 6 months
```

**Features:**
- Older conversations archived separately
- Summaries kept in main history
- Archived data still accessible
- Reduces active data size

---

## Security Features

### 1. Password Protection

**Secure profile access** with password/PIN:

**Setup:**
```
Create a password for your profile (min 8 characters): ********
Confirm password: ********

✅ Password set successfully!
Your profile is now protected.
```

**Features:**
- SHA-256 password hashing
- Unique salt per profile
- Passwords never stored in plain text
- Optional (can be disabled)

**Login:**
```
Enter password: ********
✅ Access granted

OR

Enter password: ********
❌ Incorrect password (2 attempts remaining)
```

### 2. Data Encryption

**AES-256 encryption** for all stored data:

**How It Works:**
```
User Data → Serialize to JSON → Encrypt with AES-256 → Save to disk

Encrypted file structure:
{
  "encrypted": true,
  "data": "gAAAAABh3k4p..."  # Base64-encoded encrypted data
}
```

**Key Management:**
```
~/.wellness_buddy/
├── .encryption_key          # Fernet key (600 permissions)
├── username.json            # Encrypted data
└── username_backup_*.json   # Encrypted backups
```

**Important:**
- Encryption key is critical - backup securely!
- Lost key = permanently lost data
- Legacy unencrypted profiles auto-migrate

### 3. Session Timeout

**Auto-logout** after inactivity:

**Configuration:**
```python
SESSION_TIMEOUT_MINUTES = 30  # Default: 30 minutes
```

**Behavior:**
```
[User inactive for 30 minutes]

⚠️ Session Expired
You've been logged out due to inactivity.
Please log in again to continue.

Enter password: ********
```

**Activity Tracking:**
- Updates on every interaction
- Checks on each message
- Graceful logout with data save

### 4. Account Lockout

**Brute force protection:**

**Settings:**
```python
MAX_LOGIN_ATTEMPTS = 3          # Lock after 3 failed attempts
LOCKOUT_DURATION_MINUTES = 15   # Lock for 15 minutes
```

**Lockout Process:**
```
Attempt 1: ❌ Incorrect password (2 attempts remaining)
Attempt 2: ❌ Incorrect password (1 attempt remaining)
Attempt 3: ❌ Incorrect password

🔒 Account Locked
Your account has been locked due to multiple failed login attempts.
Please try again in 15 minutes.
```

**Auto-Unlock:**
- Automatic after lockout duration
- Counter resets on successful login
- Secure against brute force attacks

### 5. Data Integrity

**Verify data hasn't been tampered with:**

**SHA-256 Hashing:**
```python
# Get integrity hash
hash1 = data_store.get_data_integrity_hash("username")
# 'a7b3c4d5e6f7...'

# Later, verify integrity
hash2 = data_store.get_data_integrity_hash("username")

if hash1 == hash2:
    print("✅ Data integrity verified")
else:
    print("⚠️ Data may have been modified")
```

### 6. Automatic Backups

**Timestamped backups** before critical operations:

**Backup Creation:**
```python
# Automatic backup before save
backup_file = data_store.create_backup("username")
# Creates: username_backup_20260222_153045.json
```

**Backup Location:**
```
~/.wellness_buddy/
├── username.json
├── username_backup_20260222_153045.json
├── username_backup_20260221_120030.json
└── ...
```

**Backup Management:**
```bash
# Keep only last 10 backups
cd ~/.wellness_buddy
ls -t *_backup_* | tail -n +11 | xargs rm
```

---

## Specialized Support Features

### 1. Women's Safety Features

**Specialized support** for women experiencing abuse:

**Safety Settings:**
```python
# Enable women's support
profile.enable_women_support()

# Mark family as unsafe (for toxic situations)
profile.add_unsafe_contact("family/parents")
profile.add_unsafe_contact("spouse/partner")
```

**Modified Alert Response:**
```
🛡️ SAFE SUPPORT NETWORK 🛡️

Since family may not be safe, consider these trusted resources:

Women's Organizations:
  • National Coalition Against Domestic Violence: 1-303-839-1852
  • National Organization for Women: 202-628-8669

Building Safe Support:
  • Reach out to trusted friends outside your household
  • Consider confiding in a colleague or mentor you trust
  • Connect with support groups

💚 Your Trusted Contacts:
  • Emma (best friend): 555-1234
  • Dr. Smith (therapist): 555-9999
```

### 2. Trusted Contact Management

**Maintain a safe support network:**

**Adding Contacts:**
```python
# Add trusted friend
profile.add_trusted_contact(
    name="Emma Johnson",
    relationship="best friend",
    contact_info="555-1234"
)

# Add professional support
profile.add_trusted_contact(
    name="Dr. Sarah Smith",
    relationship="therapist",
    contact_info="555-9999"
)
```

**Viewing Contacts:**
```
💚 Your Trusted Contacts:

1. Emma Johnson (best friend)
   Contact: 555-1234
   Added: 2025-08-15

2. Dr. Sarah Smith (therapist)
   Contact: 555-9999
   Added: 2025-09-01

3. Crisis Center (professional support)
   Contact: 1-800-273-8255
   Added: 2025-08-15
```

### 3. Abuse Detection

**Automatic detection** of abuse indicators:

**Detected Keywords (16 indicators):**
- abuse, abused, abusive
- controlling, manipulative
- gaslighting, threatened
- intimidated, belittled
- humiliated, isolated
- trapped, toxic relationship
- emotional abuse, verbal abuse
- domestic violence

**Response:**
```
I've noticed some concerning patterns in what you've shared.
You mentioned experiences that may indicate emotional abuse.

🛡️ You deserve safety and support:
  • Domestic Violence Hotline: 1-800-799-7233
  • Safety Planning: thehotline.org
  
Your trusted contacts:
  • Emma (best friend): 555-1234
```

---

## Guardian Alert System

### Overview

The Guardian Alert System allows designated emergency contacts (therapist, family members, trusted friends) to be automatically notified when sustained emotional distress is detected.

**Configuration (config.py):**
```python
ENABLE_GUARDIAN_ALERTS = True      # Enable the system
GUARDIAN_ALERT_THRESHOLD = 'high'  # When to notify: 'low', 'medium', or 'high'
AUTO_NOTIFY_GUARDIANS = False      # Ask user first (recommended)
```

### 1. Adding Guardian Contacts

**Via CLI:**
```
You: profile
> 2. Add/remove guardian contacts
> 1. Add guardian

Guardian Name: Dr. Smith
Relationship: Therapist
Contact: dr.smith@therapy.com
Notify on severity: high
```

Guardian contacts are stored in the user profile under `guardian_contacts` and are separate from trusted friends.

### 2. Alert Trigger Conditions

Guardians are notified when ALL of the following are true:
- Sustained distress is detected (3+ consecutive distress messages by default)
- The detected severity meets or exceeds `GUARDIAN_ALERT_THRESHOLD`
- The user has at least one guardian contact configured

**Severity Levels:**
```
low    → Mild negative sentiment detected
medium → Moderate distress or multiple distress keywords
high   → Severe distress, sustained patterns, or abuse indicators
```

### 3. Guardian Notification Message

When a guardian alert fires, the system generates:

```
🚨 WELLNESS ALERT FOR [User] 🚨

This is an automated notification from AI Wellness Buddy.

[User] has shown signs of sustained emotional distress and may need support.

Indicators detected:
  • Sustained emotional distress detected
  • 4 consecutive distress messages

What you can do:
  • Reach out to check on them with care and compassion
  • Listen without judgment
  • Offer support and help them access professional resources
  • Take any mention of self-harm seriously - contact emergency services if needed

Professional Resources:
  • Crisis Hotline: 988
  • Emergency Services: 911
  • Crisis Text Line: Text HOME to 741741

This is a support tool, not a replacement for professional care.
If there is immediate danger, contact emergency services immediately.
```

### 4. Privacy-Respecting Design

When `AUTO_NOTIFY_GUARDIANS = False` (default), the system asks the user first:

```
👨‍👩‍👧‍👦 GUARDIAN NOTIFICATION

Would you like to notify your designated guardians/emergency contacts?

Your guardians:
  • Dr. Smith (Therapist)
  • Jane Doe (Sister)
```

When `AUTO_NOTIFY_GUARDIANS = True`, the message confirms:
```
Your designated guardians/emergency contacts have been notified.
```

### 5. Guardian System Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `ENABLE_GUARDIAN_ALERTS` | `True` | Enable/disable the system |
| `GUARDIAN_ALERT_THRESHOLD` | `'high'` | Minimum severity to notify |
| `AUTO_NOTIFY_GUARDIANS` | `False` | Auto-notify vs. ask first |

---

## Government Resources for Women

The system includes an extensive database of government-backed and legal resources specifically for women, displayed automatically when abuse indicators are detected in a female user's session.

### U.S. Government Agencies

```
Office on Women's Health (HHS): 1-800-994-9662
Women's Bureau (Department of Labor): 1-800-827-5335
Violence Against Women Office (DOJ): 202-307-6026
```

### Legal Aid Resources

```
Legal Services Corporation: 202-295-1500
National Women's Law Center: 202-588-5180
American Bar Association Women's Rights: 312-988-5000
```

### Women's Mental Health Services

```
Women's Mental Health - NIMH: 1-866-615-6464
Postpartum Support International: 1-800-944-4773
Anxiety and Depression Association (Women): 240-485-1001
```

### International Resources

```
UN Women Helpline: +1-212-906-6400
International Women's Health Coalition: +1-212-979-8500
Global Fund for Women: +1-415-248-4800
```

### When These Resources Appear

Government resources are included in the distress alert when:
1. The user is identified as female (gender set to 'female')
2. Abuse indicators are detected in the current session

**Example Alert (excerpt):**
```
🏛️ Government & Legal Resources:

U.S. Government Agencies:
  • Office on Women's Health (HHS): 1-800-994-9662
  • Women's Bureau (Department of Labor): 1-800-827-5335
  • Violence Against Women Office (DOJ): 202-307-6026

Legal Aid:
  • Legal Services Corporation: 202-295-1500
  • National Women's Law Center: 202-588-5180
  • American Bar Association Women's Rights: 312-988-5000

Women's Mental Health:
  • Women's Mental Health - NIMH: 1-866-615-6464
  • Postpartum Support International: 1-800-944-4773
  • Anxiety and Depression Association (Women): 240-485-1001
```

---

## User Interface Options

### 1. Command-Line Interface (CLI)

**Traditional terminal interface:**

**Starting:**
```bash
python wellness_buddy.py
```

**Features:**
- Text-based interaction
- Simple and fast
- Works on any system
- No browser required
- Full feature access

**Commands:**
```
help              - Show support resources and trusted contacts
status            - View risk level, stability index, emotion distribution, 7-day history
weekly / report   - Generate 7-day wellness report with AI forecast
profile           - Manage personal history, response style, contacts, security
quit              - End session and save (streak and badges updated)
```

### 2. Web Browser UI (Streamlit) — 4-Tab Analytics Dashboard

**Modern browser-based interface with full analytics:**

**Starting:**
```bash
streamlit run ui_app.py
```

**Tab Layout:**

| Tab | What it shows |
|-----|--------------|
| 💬 **Chat** | Live conversation with XAI annotation per response |
| 📈 **Emotional Trends** | Sentiment line chart, 3-msg moving average, emotion distribution bar chart, 30-day history, OLS forecast, stability/volatility metrics |
| ⚠️ **Risk Dashboard** | Risk level + progress bar (🟢🟡🔴🚨), volatility/stability/consecutive distress metrics, 30-day risk history, escalation forecast, mood streak, badges |
| 📋 **Weekly Report** | 7-day KPIs, emotion distribution, improvement suggestions, OLS forecast |

**Sidebar (always visible):**
- Current user and session number
- Live risk level indicator (updates after every message)
- Quick-action buttons: Help & Resources, Emotional Status, Manage Profile, End Session

**Access:**
```
Local URL: http://localhost:8501
```

### 3. Network UI

**Access from any device on your network:**

**Starting:**
```bash
bash start_ui_network.sh
```

**Features:**
- Access from phone, tablet, other computers
- Same Wi-Fi/LAN required
- Secure with XSRF protection
- Full web UI features

**Access:**
```
Local URL:   http://localhost:8501
Network URL: http://192.168.1.100:8501
```

**Devices:**
- Desktop/laptop browsers
- Mobile browsers (iOS, Android)
- Tablets
- Multiple users simultaneously

---

## Data Management

### 1. Exporting Data

**Export your emotional history:**

**JSON Export:**
```python
# Get all history
history = profile.get_emotional_history()

# Save to file
import json
with open('my_wellness_data.json', 'w') as f:
    json.dump(history, f, indent=2, default=str)
```

**Summary Report:**
```python
# Generate annual report
report = profile.generate_annual_report()

# Save report
with open('annual_report_2026.txt', 'w') as f:
    f.write(report)
```

### 2. Data Deletion

**Complete control over your data:**

**Delete Profile:**
```python
# Via profile menu
> profile
> 4. Delete all my data

Are you sure? This cannot be undone. (yes/no): yes
✅ All data deleted successfully.
```

**Delete Specific Period:**
```python
# Delete data from specific date range
profile.delete_history(
    start_date="2025-01-01",
    end_date="2025-06-30"
)
```

**Manual Cleanup:**
```bash
# Remove all wellness buddy data
rm -rf ~/.wellness_buddy/

# Secure deletion (Linux/Mac)
shred -vfz -n 10 ~/.wellness_buddy/*
rm -rf ~/.wellness_buddy/
```

### 3. Data Backup

**Protect your emotional history:**

**Manual Backup:**
```bash
# Backup entire directory
cp -r ~/.wellness_buddy ~/backup/wellness_buddy_20260222

# Or create tar archive
tar -czf wellness_backup_20260222.tar.gz -C ~ .wellness_buddy
```

**Cloud Backup (encrypted):**
```bash
# Encrypt before uploading
gpg -c wellness_backup_20260222.tar.gz
# Upload wellness_backup_20260222.tar.gz.gpg to cloud
```

**Automatic Backups:**
- System creates backups before saves
- Timestamped: `username_backup_YYYYMMDD_HHMMSS.json`
- Keep last 10-20 backups
- All encrypted if encryption enabled

---

## Advanced Configuration

### 1. Emotional Analysis Settings

```python
# config.py

# Distress detection
DISTRESS_THRESHOLD = -0.3        # Sentiment below this = distress
SUSTAINED_DISTRESS_COUNT = 3     # Consecutive messages for alert

# Pattern tracking
PATTERN_TRACKING_WINDOW = 10     # Messages to analyze
```

**Adjustment Guide:**
- **More Sensitive**: Lower threshold (-0.2), fewer messages (2)
- **Less Sensitive**: Higher threshold (-0.4), more messages (5)
- **Balanced**: Default settings (-0.3, 3 messages)

### 2. Data Retention Settings

```python
# config.py

# Extended tracking
EMOTIONAL_HISTORY_DAYS = 365     # Keep 1 year of history
CONVERSATION_ARCHIVE_DAYS = 180  # Archive after 6 months
MAX_EMOTIONAL_SNAPSHOTS = 365    # Maximum snapshots
```

**Custom Retention:**
```python
# Conservative (smaller storage)
EMOTIONAL_HISTORY_DAYS = 90      # 3 months

# Extended (more history)
EMOTIONAL_HISTORY_DAYS = 730     # 2 years

# Unlimited (use with caution)
EMOTIONAL_HISTORY_DAYS = 999999  # Effectively unlimited
```

### 3. Security Settings

```python
# config.py

# Password protection
ENABLE_PROFILE_PASSWORD = True   # Require password
MIN_PASSWORD_LENGTH = 8          # Minimum password length

# Session management
SESSION_TIMEOUT_MINUTES = 30     # Auto-logout timeout

# Account protection
MAX_LOGIN_ATTEMPTS = 3           # Failed attempts before lockout
LOCKOUT_DURATION_MINUTES = 15    # Lockout duration

# Encryption
ENABLE_DATA_ENCRYPTION = True    # Encrypt data at rest
```

**Security Levels:**

**Maximum Security:**
```python
ENABLE_PROFILE_PASSWORD = True
MIN_PASSWORD_LENGTH = 12
SESSION_TIMEOUT_MINUTES = 15
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 30
ENABLE_DATA_ENCRYPTION = True
```

**Balanced Security (Default):**
```python
ENABLE_PROFILE_PASSWORD = True
MIN_PASSWORD_LENGTH = 8
SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 15
ENABLE_DATA_ENCRYPTION = True
```

**Minimal Security (Private device):**
```python
ENABLE_PROFILE_PASSWORD = False
SESSION_TIMEOUT_MINUTES = 0     # Disabled
ENABLE_DATA_ENCRYPTION = True   # Still recommended
```

### 4. Guardian Alert Settings

```python
# config.py

# Guardian/Emergency Contact Settings
ENABLE_GUARDIAN_ALERTS = True       # Enable guardian notification system
GUARDIAN_ALERT_THRESHOLD = 'high'   # 'low', 'medium', or 'high'
AUTO_NOTIFY_GUARDIANS = False        # Ask user before notifying
```

**Threshold Guide:**
- **`'high'`** (default): Only notify for severe, sustained distress
- **`'medium'`**: Notify for moderate or high distress
- **`'low'`**: Notify even for mild negative patterns

**Auto-Notify Modes:**
```python
AUTO_NOTIFY_GUARDIANS = False   # User is asked first (privacy-first)
AUTO_NOTIFY_GUARDIANS = True    # Guardians notified automatically
```

### 5. Conversation Settings

```python
# config.py

MAX_CONVERSATION_HISTORY = 50    # Messages to keep in session

GREETING_MESSAGES = [
    "Hello! I'm here to support you.",
    "Welcome back! I'm here to listen.",
    "Hi there! This is a safe space."
]
```

---

## Feature Comparison

### Emotion Analysis Comparison

| Aspect | Previous | **Current** |
|--------|----------|-------------|
| Emotion classes | positive / neutral / negative / distress | **joy / sadness / anger / fear / anxiety / crisis** |
| Crisis detection | Keyword threshold | **Dedicated 15-keyword crisis list** |
| XAI attribution | No | **Keyword explanation in every response** |
| Risk scoring | Polarity threshold (-0.3) | **Formula: base + consecutive + abuse** |
| Risk levels | Distress / Not distress | **Low / Medium / High / Critical** |
| Stability index | No | **Volatility + stability (0–1)** |
| Moving average | No | **3-message sliding average** |

### Personalization Comparison

| Feature | Previous | **Current** |
|---------|----------|-------------|
| Personal history | No | **Trauma, triggers, marital status, family background** |
| Response styles | One generic template | **Short / Balanced / Detailed per emotion** |
| Mood streak | No | **Consecutive positive sessions** |
| Wellness badges | No | **8 badge types** |
| Weekly report | No | **`weekly` command with OLS forecast** |

### Tracking Duration Comparison

| Aspect | Previous | **Current** |
|--------|----------|-------------|
| Emotional History | 90 days | **365 days** |
| Pattern Analysis | Short-term | **Long-term** |
| Seasonal Detection | Limited | **Full year** |
| Forecast | No | **OLS next-session prediction** |
| Risk trend | No | **Risk escalation forecast** |

### Security Comparison

| Feature | Previous | **Current** |
|---------|----------|-------------|
| Password Protection | No | **Yes** |
| Data Encryption | No | **AES-256** |
| Session Timeout | No | **Yes** |
| Account Lockout | No | **Yes** |
| Data Integrity | No | **SHA-256** |
| Backups | Manual | **Automatic** |

### Guardian Alert Comparison

| Feature | Previous | **Current** |
|---------|----------|-------------|
| Guardian Contacts | No | **Yes** |
| Emergency Notifications | No | **Yes** |
| Severity Thresholds | No | **Low/Medium/High** |
| Privacy Control | No | **Ask first option** |
| Government Resources | No | **15+ agencies** |
| Auto-Notify Option | No | **Configurable** |

### Interface Comparison

| Interface | Features | Best For |
|-----------|----------|----------|
| **CLI** | Text-based, simple | Quick check-ins, servers |
| **Web UI** | 4-tab analytics dashboard | Daily use, pattern review |
| **Network UI** | Multi-device | Mobile access, family sharing |

---

## Frequently Asked Questions

### General Usage

**Q: How do I get started?**
```bash
# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"

# Start the app
python wellness_buddy.py
```

**Q: How often should I use it?**
A: Daily or every other day is ideal for best pattern tracking. Even brief 5-minute check-ins are valuable.

**Q: Can multiple people use it?**
A: Yes! Each person creates their own profile with separate data.

### Extended Tracking

**Q: Will my existing data be lost with the upgrade?**
A: No! All existing data is preserved. You'll now keep it for 365 days instead of 90.

**Q: Can I export my full year of data?**
A: Yes, use the export feature to get JSON or generate annual reports.

**Q: What happens when I reach 365 days?**
A: Oldest entries are automatically removed, maintaining a rolling 365-day window.

### Security

**Q: Is my data really secure?**
A: Yes:
- AES-256 encryption (military-grade)
- Password hashing with unique salts
- File permissions (owner-only)
- No external data sharing

**Q: What if I forget my password?**
A: You'll need file system access to reset it, or delete and recreate your profile (loses history).

**Q: Can someone access my data without my password?**
A: With file system access, yes (it's stored locally). The encryption protects against casual access, but direct file system access can be used to reset the password. Keep your device secure!

### Data Management

**Q: How much storage does it use?**
A: Approximately 2-3 MB per year of data including encryption and backups.

**Q: Can I backup my data to cloud?**
A: Yes, but encrypt it first:
```bash
gpg -c wellness_backup.tar.gz
```

**Q: How do I completely remove all data?**
A:
```bash
rm -rf ~/.wellness_buddy/
```

### Guardian Alerts

**Q: What are guardian contacts?**
A: Guardian contacts (therapist, family, trusted friends) can be notified when sustained severe distress is detected. Configure using the `profile` command.

**Q: Will guardians be notified automatically?**
A: By default, the system asks you first (`AUTO_NOTIFY_GUARDIANS = False`). You can enable automatic notification in `config.py`.

**Q: What severity level triggers guardian notifications?**
A: Default is 'high' severity only. Change `GUARDIAN_ALERT_THRESHOLD` in `config.py` to 'medium' or 'low' for more sensitive alerts.

---

## Summary

The AI Wellness Buddy provides:

### Core Capabilities
✅ Real-time multi-emotion analysis (joy/sadness/anger/fear/anxiety/crisis)
✅ Crisis detection with 988/911 immediate escalation
✅ XAI keyword attribution in every response
✅ Pattern tracking and intelligent distress alerts
✅ Crisis resource connections
✅ Persistent user profiles

### Intelligent Analysis & Forecasting
✅ Formula-based risk scoring (Low/Medium/High/Critical)
✅ Emotional volatility and stability index
✅ 3-message moving average smoothing
✅ OLS next-session mood prediction
✅ Risk escalation forecasting

### Personalization
✅ Personal history: trauma, triggers, marital status, family background
✅ Response style preference (short/balanced/detailed)
✅ Warm, humanoid, context-aware responses

### Gamification
✅ Mood streak (consecutive positive sessions)
✅ 8 wellness badge types
✅ Weekly summary report with improvement suggestions

### Extended Tracking
✅ 365-day emotional history
✅ Long-term pattern analysis
✅ Seasonal trend detection

### Security
✅ Password protection
✅ AES-256 encryption
✅ Session timeouts
✅ Account lockout
✅ Data integrity checks
✅ Automatic backups

### Specialized Support
✅ Women's safety features
✅ Trusted contact management
✅ Abuse detection
✅ Personalized resources
✅ Government & legal resources (15+)

### Guardian Alert System
✅ Emergency contact notifications
✅ Configurable severity thresholds
✅ Privacy-first design (ask before notify)
✅ Multiple guardian contacts
✅ Formatted alert messages

### Interfaces
✅ Command-line (CLI)
✅ Web browser (Streamlit) — 4-tab analytics dashboard
✅ Network access (multi-device)

---

## Additional Resources

- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Data Retention**: [DATA_RETENTION.md](DATA_RETENTION.md)
- **Network Deployment**: [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)
- **Operation Guide**: [OPERATION_GUIDE.md](OPERATION_GUIDE.md)
- **Detailed Setup**: [DETAILED_SETUP_GUIDE.md](DETAILED_SETUP_GUIDE.md)
- **Quick Start**: [USAGE.md](USAGE.md)
- **UI Guide**: [UI_GUIDE.md](UI_GUIDE.md)

---

**Your emotional wellbeing journey is important. The AI Wellness Buddy is here to support you every step of the way.** 💙🌟
