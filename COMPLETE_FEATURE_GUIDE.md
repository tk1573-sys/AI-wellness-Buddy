# Complete Feature Guide

## 🌟 AI Wellness Buddy - Complete Feature Documentation

This comprehensive guide covers ALL features available in the AI Wellness Buddy, from basic to advanced functionality.

## Table of Contents
1. [Overview](#overview)
2. [Core Features](#core-features)
3. [Extended Tracking Features](#extended-tracking-features)
4. [Security Features](#security-features)
5. [Specialized Support Features](#specialized-support-features)
6. [User Interface Options](#user-interface-options)
7. [Data Management](#data-management)
8. [Advanced Configuration](#advanced-configuration)
9. [Feature Comparison](#feature-comparison)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Overview

The AI Wellness Buddy is a comprehensive emotional support system with the following capabilities:

### Quick Feature List

✅ **Core Emotional Support**
- Real-time emotion analysis
- Pattern tracking and trend detection
- Distress alert system
- Crisis resource connections

✅ **Extended Tracking (NEW)**
- 365-day emotional history (up from 90 days)
- Long-term pattern analysis
- Seasonal trend detection
- Progress milestone tracking

✅ **Enhanced Security (NEW)**
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

✅ **Multiple Interfaces**
- Command-line interface (CLI)
- Web browser UI (Streamlit)
- Network-accessible UI
- Mobile-friendly design

---

## Core Features

### 1. Emotion Analysis

**Real-time sentiment analysis** using natural language processing:

**Technologies:**
- TextBlob for sentiment analysis
- NLTK for text processing
- Custom keyword detection

**What It Analyzes:**
```python
{
  "polarity": 0.5,           # -1 (negative) to +1 (positive)
  "subjectivity": 0.6,       # 0 (objective) to 1 (subjective)
  "emotion": "positive",     # Category: positive, neutral, negative, distress
  "severity": "low",         # Severity: low, medium, high
  "distress_keywords": [],   # 24 distress indicators detected
  "abuse_indicators": []     # 16 abuse-related keywords detected
}
```

**Example Interaction:**
```
You: I'm feeling really happy today! Everything is going well.
Wellness Buddy: That's wonderful to hear! I'm glad you're experiencing such positive feelings...

[Emotion Analysis: positive, polarity: +0.85, severity: low]
```

### 2. Pattern Tracking

**Monitors emotional patterns** over time with configurable windows:

**Session-Level Tracking:**
- Last 10 messages (configurable)
- Consecutive distress detection
- Trend analysis (improving, stable, declining)

**Long-Term Tracking:**
- 365 days of emotional history
- Weekly, monthly, quarterly reviews
- Seasonal pattern detection

**Pattern Summary Example:**
```
📊 Current Session Pattern:
  Total messages: 12
  Distress messages: 2
  Distress ratio: 16.7%
  Average sentiment: +0.15
  Trend: Stable
  Consecutive distress: 0

📊 Last 7 Days:
  Check-ins: 5
  Average sentiment: +0.25
  Trend: Improving ✨
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
  "last_session": "2026-02-22T15:30:00",
  "gender": "female",
  "session_count": 287,
  "emotional_history": [...]  # 365 days of snapshots
}
```

**Profile Features:**
- Create and load profiles
- Gender-specific support
- Trusted contact management
- Safety preferences
- Session history

---

## Extended Tracking Features (NEW)

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

## Security Features (NEW)

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
help      - Show support resources
status    - View emotional patterns
profile   - Manage profile and contacts
quit      - End session and save
```

### 2. Web Browser UI (Streamlit)

**Modern browser-based interface:**

**Starting:**
```bash
streamlit run ui_app.py
```

**Features:**
- Visual, point-and-click interface
- Real-time chat display
- Sidebar navigation
- Profile management UI
- Session statistics
- Resource links

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

### 4. Conversation Settings

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

### Tracking Duration Comparison

| Aspect | Previous | **NEW Extended** |
|--------|----------|------------------|
| Emotional History | 90 days | **365 days** |
| Pattern Analysis | Short-term | **Long-term** |
| Seasonal Detection | Limited | **Full year** |
| Milestone Tracking | No | **Yes** |
| Progress Reports | Basic | **Comprehensive** |

### Security Comparison

| Feature | Previous | **NEW Enhanced** |
|---------|----------|------------------|
| Password Protection | No | **Yes** |
| Data Encryption | No | **AES-256** |
| Session Timeout | No | **Yes** |
| Account Lockout | No | **Yes** |
| Data Integrity | No | **SHA-256** |
| Backups | Manual | **Automatic** |

### Interface Comparison

| Interface | Features | Best For |
|-----------|----------|----------|
| **CLI** | Text-based, simple | Quick check-ins, servers |
| **Web UI** | Visual, modern | Daily use, longer sessions |
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

---

## Summary

The AI Wellness Buddy provides:

### Core Capabilities
✅ Real-time emotion analysis
✅ Pattern tracking and alerts
✅ Crisis resource connections
✅ Persistent user profiles

### Extended Features
✅ 365-day tracking (up from 90)
✅ Long-term pattern analysis
✅ Seasonal trend detection
✅ Progress milestones

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

### Interfaces
✅ Command-line (CLI)
✅ Web browser (Streamlit)
✅ Network access (multi-device)

---

## Additional Resources

- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Data Retention**: [DATA_RETENTION.md](DATA_RETENTION.md)
- **Network Deployment**: [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)
- **Quick Start**: [USAGE.md](USAGE.md)
- **UI Guide**: [UI_GUIDE.md](UI_GUIDE.md)

---

**Your emotional wellbeing journey is important. The AI Wellness Buddy is here to support you every step of the way.** 💙🌟
