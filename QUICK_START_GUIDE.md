# AI Wellness Buddy - Quick Start Guide

## Get Started in 5 Minutes

This guide helps you quickly set up and start using the AI Wellness Buddy system.

---

## Prerequisites (1 minute)

**You need:**
- Python 3.7+ installed
- Internet connection (for setup only)
- 100MB free disk space

**Check Python:**
```bash
python --version
# Should show 3.7 or higher
```

---

## Installation (2 minutes)

### Option 1: Automatic Setup
```bash
# Clone and setup in one go
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
bash quickstart.sh
```

### Option 2: Manual Setup
```bash
# 1. Clone repository
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download language data
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

---

## First Run (2 minutes)

### Choose Your Interface

**CLI (Command Line) - Simplest**
```bash
python wellness_buddy.py
```

**Web UI - User Friendly**
```bash
streamlit run ui_app.py
# Opens in browser automatically with 4-tab analytics dashboard:
# 💬 Chat | 📈 Emotional Trends | ⚠️ Risk Dashboard | 📋 Weekly Report
```

**Network UI - Access from Phone/Tablet**
```bash
bash start_ui_network.sh
# Shows network URL to use on other devices
```

### Create Your Profile

When you first run, you'll be asked:

```
1. Username: yourname
2. Password: ********** (min 8 characters)
3. Gender (optional): female/male/other/skip
4. Marital / relationship status (optional)
5. Response style: short / balanced (default) / detailed
6. Family background (optional)
7. Trauma or significant loss (optional)
8. Sensitive topics / personal triggers (optional, comma-separated)
9. Safe with family? (optional): yes/no/skip
```

**That's it! You're ready to use the system.**

---

## Basic Usage

### Start a Conversation

Just type how you're feeling:

```
You: I'm feeling stressed today
Wellness Buddy: I can sense you're going through a stressful time...
```

### Use Commands

| Command | What it does |
|---------|--------------|
| `help` | Show crisis resources and your contacts |
| `status` | View risk level, stability, emotion distribution |
| `weekly` / `report` | 7-day wellness summary with AI forecast |
| `profile` | Manage personal history, contacts, and settings |
| `quit` | Save and exit |

### Example Session

```
You: I'm feeling anxious about work
Buddy: It sounds like work is causing you stress...

You: Yes, everything feels overwhelming
Buddy: I hear you. It's okay to feel overwhelmed...

You: help
[Shows crisis resources and contacts]

You: status
[Shows your emotional patterns]

You: quit
Session saved. Take care! 💙
```

---

## Add Guardian/Emergency Contact

### Why Add Guardians?

Guardians get notified if you're in severe distress, providing an extra layer of support.

### How to Add

**Via CLI:**
```
You: profile
Select: 2
Select: 1

Name: Dr. Smith
Relationship: Therapist
Contact: dr.smith@email.com
Notify on: high severity
```

**Via Web UI:**
1. Click "Profile" → "Guardian Contacts"
2. Click "Add Guardian"
3. Fill the form
4. Save

---

## Add Trusted Friends (Non-Family)

For those who can't rely on family:

```
You: profile
Select: 1
Select: 1

Name: Emma
Relationship: best friend
Contact: 555-1234
```

These contacts show up in alerts instead of family.

---

## Understanding Alerts

### When Do Alerts Trigger?

After 3+ consecutive distress messages:

```
⚠️ EMOTIONAL DISTRESS ALERT ⚠️

Support Resources:
📞 Crisis: 988
📱 Text HOME to 741741
🚨 Emergency: 911

👨‍👩‍👧‍👦 Notify guardians? (yes/no)
```

### For Women - Extra Resources

If you're female and abuse indicators detected:

```
🛡️ SPECIALIZED RESOURCES FOR WOMEN

Domestic Violence: 1-800-799-7233
RAINN: 1-800-656-4673
Women's Health: 1-800-994-9662
Legal Aid: 202-295-1500

[Plus government agencies and legal resources]
```

---

## Quick Troubleshooting

### Problem: Can't Install
```bash
# Solution: Upgrade pip
pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: NLTK Error
```bash
# Solution: Download data again
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### Problem: Forgot Password
```bash
# Solution: Reset via file
nano ~/.wellness_buddy/yourname.json
# Set: "password_hash": null, "security_enabled": false
```

### Problem: Web UI Won't Open
```bash
# Solution: Try different port
streamlit run ui_app.py --server.port 8080
```

---

## Essential Phone Numbers

**Keep these handy:**

### General Crisis
- **988** - Suicide & Crisis Lifeline
- **911** - Emergency Services
- **741741** - Text HOME for Crisis Text Line

### Women's Support
- **1-800-799-7233** - Domestic Violence Hotline
- **1-800-656-4673** - RAINN Sexual Assault
- **88788** - Text START for DV support

### Mental Health
- **1-800-662-4357** - SAMHSA Mental Health
- **1-866-615-6464** - Women's Mental Health

---

## Daily Usage Tips

### ✅ Do's
- ✅ Use daily or every other day
- ✅ Be honest about feelings
- ✅ Use `help` when feeling distressed
- ✅ Check `status` weekly
- ✅ Keep guardian contacts updated
- ✅ Backup data monthly

### ❌ Don'ts
- ❌ Don't skip sessions for weeks
- ❌ Don't share password
- ❌ Don't ignore alerts
- ❌ Don't use on public WiFi (for web UI)
- ❌ Don't add unsafe people as contacts
- ❌ Don't rely solely on app for crisis

---

## Privacy & Security Quick Tips

### 🔒 Security Checklist
- [ ] Set strong password (12+ characters)
- [ ] Use on private device
- [ ] Enable encryption (default: ON)
- [ ] Lock computer when away
- [ ] Use private network for web UI
- [ ] Review permissions monthly

### 📂 Data Locations
```
Your data: ~/.wellness_buddy/yourname.json
Backups: ~/.wellness_buddy/yourname_backup_*.json
Key: ~/.wellness_buddy/.encryption_key
```

### 🗑️ Delete All Data
```bash
# Complete removal
rm -rf ~/.wellness_buddy/
```

---

## Next Steps

### After Quick Start

1. **Read Full Guide**: See OPERATION_GUIDE.md
2. **Review Features**: See COMPLETE_FEATURE_GUIDE.md
3. **Check Security**: See SECURITY.md
4. **Understand Data**: See DATA_RETENTION.md

### For Women in Unsafe Situations

1. Mark family as unsafe
2. Add only trusted friends
3. Review safety resources
4. Create safety plan
5. Use on private device only

### For Setting Up Network Access

1. Run: `bash start_ui_network.sh`
2. Note the network URL
3. Access from phone/tablet browser
4. Add to home screen for app-like experience

---

## Common Workflows

### Daily Check-in (2 minutes)
```bash
1. python wellness_buddy.py
2. Login with username/password
3. Type how you're feeling
4. Use 'quit' when done
```

### Weekly Review (5 minutes)
```bash
1. Start session
2. Type: status
3. Review patterns
4. Adjust as needed
5. Export data if desired
```

### Add Emergency Contact (3 minutes)
```bash
1. Start session
2. Type: profile
3. Select guardian contacts
4. Add details
5. Set notification preferences
```

---

## Getting Help

### Documentation
- **This Guide**: Quick start
- **OPERATION_GUIDE.md**: Complete operations
- **COMPLETE_FEATURE_GUIDE.md**: All features
- **SECURITY.md**: Security details

### Support
- **GitHub Issues**: Bug reports
- **Documentation**: In repository
- **Professional Help**: See resources above

### Crisis Resources
- **Immediate Danger**: Call 911
- **Crisis Line**: Call/text 988
- **Domestic Violence**: 1-800-799-7233

---

## Summary Checklist

Before you start using regularly:

- [ ] Installation complete
- [ ] Profile created with password
- [ ] Guardian contacts added (optional)
- [ ] Trusted contacts added (if needed)
- [ ] Understand basic commands (help, status, profile, quit)
- [ ] Emergency numbers saved
- [ ] Know where data is stored
- [ ] Reviewed privacy settings

**You're all set! Start your wellness journey.** 💙

---

## Quick Command Reference

```bash
# Start CLI
python wellness_buddy.py

# Start Web UI
streamlit run ui_app.py

# Start Network UI
bash start_ui_network.sh

# In-session commands
help      # Resources
status    # Patterns
profile   # Settings
quit      # Exit
```

---

**Remember**: This is a support tool, not a replacement for professional mental health care. For emergencies, call 911. For crisis support, call 988.

**You're not alone. Help is available 24/7.** 💙
