# AI Wellness Buddy - Operation Guide

## Complete Guide to Operating the AI Wellness Buddy System

### Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Daily Operation](#daily-operation)
6. [Guardian/Emergency Contact Setup](#guardian-emergency-contact-setup)
7. [Women's Safety Features](#womens-safety-features)
8. [Alert System](#alert-system)
9. [Data Management](#data-management)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## Introduction

The AI Wellness Buddy is an intelligent emotional support system designed to:
- Monitor emotional wellbeing through conversation
- Detect patterns of distress
- Provide crisis resources and support
- Notify guardians/emergency contacts when needed
- Offer specialized support for women in difficult situations

This guide will help you operate the system effectively.

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: Version 3.7 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for application, additional space for data
- **Internet**: Required for initial setup (downloading dependencies)

### Recommended Setup
- Stable internet connection for web UI
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Private, secure device for confidential conversations

---

## Installation

### Step 1: Download the Project
```bash
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download Required Language Data
```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### Step 4: Verify Installation
```bash
python wellness_buddy.py
```

If you see the welcome screen, installation is successful!

---

## Getting Started

### First Time Setup

#### 1. Choose Your Interface

**Option A: Command Line Interface (CLI)**
```bash
python wellness_buddy.py
```
- Best for: Quick check-ins, simple operation
- Advantages: Fast, lightweight, works anywhere
- Disadvantages: Text-only, no visual elements

**Option B: Web Browser UI**
```bash
streamlit run ui_app.py
```
Or use the launcher:
```bash
bash start_ui.sh
```
- Best for: Regular use, visual preferences
- Advantages: User-friendly, visual interface, easy navigation
- Disadvantages: Requires browser, slightly more resources

**Option C: Network UI (Access from multiple devices)**
```bash
bash start_ui_network.sh
```
- Best for: Access from phone/tablet, multiple users
- Advantages: Access from any device on network
- Disadvantages: Security considerations on shared networks

#### 2. Create Your Profile

First-time users will be prompted to:

1. **Choose a username** (private, for your use only)
   ```
   Choose a username: sarah
   ```

2. **Set optional demographic information**
   ```
   How do you identify? (female/male/other/skip): female
   ```

3. **Configure safety settings** (especially for women)
   ```
   Do you feel safe with your family/guardians? (yes/no/skip): no
   ```

4. **Set up password protection** (NEW - Enhanced Security)
   ```
   Create a password for your profile (min 8 characters): ********
   Confirm password: ********
   ```

#### 3. Add Guardian/Emergency Contacts

If you want guardians to be notified during severe distress:

```
Would you like to add guardian/emergency contacts? (yes/no): yes

Guardian Contact 1:
  Name: Dr. Smith
  Relationship: Therapist
  Contact: dr.smith@therapy.com
  Notify on: high severity only

Guardian Contact 2:
  Name: Jane Doe
  Relationship: Sister
  Contact: jane.doe@email.com
  Notify on: medium or higher
```

#### 4. Add Trusted Friends (Non-Family)

For those in unsafe family situations:

```
Would you like to add trusted friends? (yes/no): yes

Name: Emma
Relationship: best friend
Contact info: 555-1234
```

---

## Daily Operation

### Starting a Session

1. **Launch the application**
   ```bash
   python wellness_buddy.py
   # or
   streamlit run ui_app.py
   ```

2. **Log in with your username**
   ```
   Enter your username: sarah
   Enter password: ********
   ```

3. **See your wellness summary**
   ```
   💙 Welcome back! This is your session #42.
   📊 You've checked in 15 time(s) in the last 7 days.
   ```

### Using the System

#### Basic Conversation
Simply type how you're feeling:

```
You: I'm feeling stressed about work today
Wellness Buddy: I can sense you're going through a stressful time...

You: Everything feels overwhelming
Wellness Buddy: It sounds like you're carrying a heavy burden...
```

#### Available Commands

While in a session, you can use these commands:

- **`help`** - View crisis resources and your contacts
  ```
  You: help
  
  📞 Crisis Resources:
    • Crisis Hotline: 988
    • Text Line: Text HOME to 741741
    • Emergency: 911
  
  💚 Your Trusted Contacts:
    • Emma (best friend): 555-1234
  ```

- **`status`** - View your emotional patterns
  ```
  You: status
  
  📊 Current Session:
    Messages: 12
    Average sentiment: +0.15
    Trend: Stable
  
  📊 Last 7 Days:
    Check-ins: 5
    Average sentiment: +0.25
    Trend: Improving ✨
  ```

- **`profile`** - Manage contacts and settings
  ```
  You: profile
  
  Profile Options:
  1. Add/remove trusted contacts
  2. Add/remove guardian contacts
  3. Update safety settings
  4. Change password
  5. Delete all data
  ```

- **`quit`** - End session and save
  ```
  You: quit
  
  Session saved successfully.
  Take care! 💙
  ```

### Understanding the Response System

The system analyzes your messages for:

1. **Emotional Content**
   - Sentiment (positive, neutral, negative)
   - Intensity (low, medium, high)
   - Specific emotions (sad, anxious, hopeful, etc.)

2. **Distress Indicators**
   - Keywords related to emotional distress
   - Patterns of sustained negative emotion
   - Mentions of self-harm or crisis

3. **Abuse Indicators** (for women's safety)
   - Keywords related to emotional/physical abuse
   - Controlling behavior patterns
   - Safety concerns

---

## Guardian/Emergency Contact Setup

### When to Use Guardian Alerts

Guardian alerts are designed for:
- Severe emotional distress
- Sustained patterns of crisis
- When you might need external support
- Safety concerns

### Setting Up Guardians

#### Via CLI:
```
You: profile
Select: 2. Manage guardian contacts
Select: 1. Add guardian contact

Name: Dr. Sarah Johnson
Relationship: Therapist
Contact: sarah.johnson@therapy.com
Phone: 555-123-4567
Notify threshold: high
Auto-notify: no (ask me first)
```

#### Via Web UI:
1. Click "Profile" in sidebar
2. Select "Guardian Contacts"
3. Click "Add Guardian"
4. Fill in the form
5. Save

### Guardian Notification Settings

**Notification Thresholds:**
- **Low**: Any detected distress (not recommended)
- **Medium**: Moderate sustained distress (3+ messages)
- **High**: Severe sustained distress (5+ messages, crisis keywords)

**Auto-Notification:**
- **Enabled**: Guardians notified automatically
- **Disabled**: System asks before notifying (recommended)

### What Guardians Receive

When an alert is triggered, guardians receive:

```
🚨 WELLNESS ALERT FOR Sarah 🚨

This is an automated notification from AI Wellness Buddy.

Sarah has shown signs of sustained emotional distress 
and may need support.

Indicators detected:
  • Sustained emotional distress detected
  • 5 consecutive distress messages

What you can do:
  • Reach out with care and compassion
  • Listen without judgment
  • Help access professional resources

Professional Resources:
  • Crisis Hotline: 988
  • Emergency: 911
```

---

## Women's Safety Features

### Specialized Support for Women

The system includes enhanced features for women, especially those in unsafe situations:

#### 1. Abuse Detection
Automatically detects keywords and patterns related to:
- Emotional abuse
- Controlling behavior
- Gaslighting
- Physical threats
- Isolation

#### 2. Expanded Resources

When abuse indicators are detected, you receive:

**Domestic Violence Resources:**
- National Domestic Violence Hotline: 1-800-799-7233
- Text START to 88788
- RAINN Sexual Assault Hotline: 1-800-656-4673

**Government Agencies:**
- Office on Women's Health: 1-800-994-9662
- Violence Against Women Office: 202-307-6026
- Women's Bureau (Dept of Labor): 1-800-827-5335

**Legal Aid:**
- Legal Services Corporation: 202-295-1500
- National Women's Law Center: 202-588-5180
- American Bar Association: 312-988-5000

**Mental Health (Women-Specific):**
- Women's Mental Health - NIMH: 1-866-615-6464
- Postpartum Support International: 1-800-944-4773
- Anxiety and Depression (Women): 240-485-1001

#### 3. Safe Support Network

For women who cannot rely on family:

**Mark Family as Unsafe:**
```
Do you feel safe with your family/guardians? (yes/no): no
```

This ensures:
- Alerts don't suggest contacting family
- Focus on trusted friends instead
- Connection to women's organizations
- Professional support emphasis

**Build Trusted Network:**
```
Add trusted friends outside family:
  • Best friend
  • Colleague
  • Mentor
  • Support group member
```

#### 4. Safety Planning

The system provides guidance on:
- Creating a safety plan
- Documenting incidents
- Finding safe shelter
- Legal protections
- Financial independence

---

## Alert System

### How Alerts Work

The system monitors for:

1. **Consecutive Distress Messages** (default: 3+)
   - Multiple messages showing distress
   - Sustained negative emotion
   - Worsening emotional state

2. **Severity Levels**
   - **Low**: Single distress indicator
   - **Medium**: 3+ consecutive distress messages
   - **High**: 5+ messages + crisis keywords

3. **Abuse Indicators** (for women)
   - Specific keywords detected
   - Pattern of controlling behavior
   - Safety concerns mentioned

### When Alerts Trigger

You'll see:

```
⚠️ EMOTIONAL DISTRESS ALERT ⚠️

I've noticed sustained emotional distress.
Your wellbeing is important.

📞 General Support Resources:
  • Crisis Hotline: 988
  • Text HOME to 741741
  • Emergency: 911

🛡️ Specialized Resources for Women:
  [Women's resources...]

👨‍👩‍👧‍👦 GUARDIAN NOTIFICATION
Would you like to notify your guardians?
  • Dr. Sarah Johnson (Therapist)
  • Jane Doe (Sister)
```

### Responding to Alerts

**Options:**
1. **Access Resources**: Call/text the provided numbers
2. **Notify Guardians**: Yes/No to notify emergency contacts
3. **Continue Session**: Keep talking if helpful
4. **End Session**: Take a break, resources saved

### Alert History

View past alerts:
```
You: status full

Alert History (Last 30 Days):
  • Feb 20: Distress alert - Guardians notified
  • Feb 15: Distress alert - Resources accessed
  • Feb 10: Abuse indicators - Women's resources provided
```

---

## Data Management

### Data Storage

All data is stored locally:
```
~/.wellness_buddy/
├── sarah.json              # Your profile
├── sarah_backup_*.json     # Automatic backups
└── .encryption_key         # Encryption key
```

### Data Security

**Encryption:**
- All data encrypted with AES-256
- Password protected
- Encryption key stored separately

**Permissions:**
- Files readable only by you (600 permissions)
- Encryption key protected

**Backups:**
- Automatic backups before major changes
- Timestamped: `sarah_backup_20260222_153000.json`
- Keep last 10 backups

### Exporting Data

**Export your history:**
```python
# Via Python
from data_store import DataStore
from user_profile import UserProfile

ds = DataStore()
data = ds.load_user_data('sarah')

import json
with open('my_wellness_data.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)
```

**Via Profile Menu:**
```
You: profile
Select: 5. Export data
Filename: my_backup_2026.json
✓ Data exported successfully
```

### Deleting Data

**Complete deletion:**
```
You: profile
Select: 4. Delete all my data

Are you sure? This cannot be undone. (yes/no): yes
✓ All data deleted successfully
```

**Manual deletion:**
```bash
# Remove all data
rm -rf ~/.wellness_buddy/

# Or secure deletion
shred -vfz -n 10 ~/.wellness_buddy/*
rm -rf ~/.wellness_buddy/
```

---

## Troubleshooting

### Common Issues

#### 1. Cannot Start Application

**Problem**: `ModuleNotFoundError`
**Solution**:
```bash
pip install -r requirements.txt
```

**Problem**: NLTK data missing
**Solution**:
```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

#### 2. Forgot Password

**Solution** (requires file access):
```bash
# Edit your profile file
nano ~/.wellness_buddy/sarah.json

# Remove password fields:
"password_hash": null,
"salt": null,
"security_enabled": false
```

#### 3. Session Timeout

**Problem**: Logged out after inactivity
**Solution**: 
- Re-enter password
- Or adjust timeout in config.py:
  ```python
  SESSION_TIMEOUT_MINUTES = 60  # Increase to 60 min
  ```

#### 4. Guardian Alerts Not Working

**Check**:
1. Guardian contacts configured?
2. Alert threshold set correctly?
3. Severity level reached?

**Debug**:
```python
# In config.py
GUARDIAN_ALERT_THRESHOLD = 'medium'  # Lower threshold
```

#### 5. Data Decryption Error

**Problem**: Wrong encryption key
**Solution**: Restore from backup
```bash
cp ~/.wellness_buddy/sarah_backup_20260220_120000.json ~/.wellness_buddy/sarah.json
```

### Getting Help

**Resources:**
1. Check documentation in repository
2. Review error messages carefully
3. Check log files (if enabled)
4. Restore from backup if needed

**Support:**
- GitHub Issues: Report bugs
- Documentation: COMPLETE_FEATURE_GUIDE.md
- Security: SECURITY.md
- Data: DATA_RETENTION.md

---

## Best Practices

### For Regular Users

1. **Daily Check-ins**: Use consistently for best pattern tracking
2. **Honest Communication**: System works best with honest sharing
3. **Access Resources**: Don't hesitate to use provided resources
4. **Backup Data**: Export data monthly
5. **Update Contacts**: Keep guardian contacts current
6. **Review Patterns**: Check status weekly

### For Women in Unsafe Situations

1. **Use Private Device**: Don't use shared/monitored devices
2. **Secure Location**: Use in private, safe location
3. **Delete History**: Clear browser history after web UI use
4. **Trusted Contacts Only**: Don't add unsafe family members
5. **Safety Plan**: Have plan before leaving unsafe situation
6. **Professional Help**: Connect with women's organizations

### For Guardians

1. **Respond Promptly**: Check notifications quickly
2. **Non-Judgmental**: Approach with care and empathy
3. **Professional Referral**: Guide to professional help
4. **Emergency Response**: Call 911 if immediate danger
5. **Follow Up**: Check in regularly
6. **Respect Privacy**: Don't demand access to data

### Security Best Practices

1. **Strong Password**: Use 12+ characters
2. **Regular Updates**: Keep software updated
3. **Trusted Networks**: Use on secure Wi-Fi only
4. **Backup Key**: Save encryption key securely
5. **Lock Device**: Always lock computer when away
6. **Secure Deletion**: Use secure delete when removing data

---

## Quick Reference Card

### Essential Commands
```
help     - Crisis resources and contacts
status   - View emotional patterns
profile  - Manage settings and contacts
quit     - End session and save
```

### Emergency Numbers
```
Crisis: 988
Emergency: 911
Text: HOME to 741741
DV Hotline (Women): 1-800-799-7233
```

### File Locations
```
Data: ~/.wellness_buddy/
Config: ./config.py
Logs: ~/.wellness_buddy/wellness_buddy.log
```

### Common Tasks
```
Add Guardian: profile → 2 → 1
Export Data: profile → 5
Change Password: profile → 4
View History: status full
```

---

## Conclusion

The AI Wellness Buddy is designed to support your emotional wellbeing through:
- Continuous monitoring and pattern recognition
- Timely crisis resource provision
- Guardian notification when needed
- Specialized support for women
- Secure, private data storage

Use this guide as a reference for daily operation. Remember: this is a support tool, not a replacement for professional mental health care. Always seek professional help for serious mental health concerns.

**Stay safe, stay well, and remember - you're not alone.** 💙
