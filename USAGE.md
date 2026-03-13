# Quick Start Guide

## How to Use AI Wellness Buddy

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download required language data
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### 2. Start the Application

```bash
python wellness_buddy.py
```

### 3. First Time Setup

When you first run the app, you'll be asked to:

1. **Create a username** (private, for your eyes only)
2. **Answer optional questions** about your identity
3. **For women**: Option to mark family as unsafe and add trusted contacts

Example session:
```
Choose a username: sarah
How do you identify? (female/male/other/skip): female
Do you feel safe with your family/guardians? (yes/no/skip): no
Would you like to add trusted friends now? (yes/no): yes
Name: Emma
Relationship: best friend
Contact info: 555-1234
```

### 4. Using the Application

Simply type how you're feeling:
```
You: I'm feeling stressed today
Wellness Buddy: I can sense you're going through a difficult time...
```

### 5. Available Commands

While in a session, you can type:

- `help` — View crisis resources and your trusted contacts
- `status` — See risk level, stability index, emotion breakdown, and 7-day history
- `weekly` / `report` — Get a 7-day wellness summary with AI forecast and suggestions
- `profile` — Manage personal history, response style, contacts, or delete data
- `quit` — End the session and save your progress (streak and badges updated)

### 6. Example Session

```
You: I'm feeling overwhelmed
Wellness Buddy: [empathetic response]

You: Everything feels hopeless
Wellness Buddy: [supportive response]

You: I can't take this anymore
Wellness Buddy: [distress alert triggered]

⚠️ EMOTIONAL DISTRESS ALERT ⚠️
I've noticed sustained emotional distress...

📞 General Support Resources:
  • Crisis Hotline: 988
  • Crisis Text Line: Text HOME to 741741
  ...

💚 Your Trusted Contacts:
  • Emma (best friend): 555-1234
  ...
```

### 7. Returning Users

Next time you run the app:
```
Found 1 existing profile(s).
Enter your username to continue: sarah

💙 Welcome back! This is your session #2.
📊 You've checked in 1 time(s) in the last 7 days.
```

### 8. Privacy & Data

- All data stored locally in `~/.wellness_buddy/`
- Your profile: `~/.wellness_buddy/sarah.json`
- Delete anytime via `profile` command → option 4

### 9. Safety Features for Women

If you marked family as unsafe:
- Crisis alerts won't suggest contacting family
- System guides you to:
  - Your trusted contacts (friends you added)
  - Women's support organizations
  - Professional help (therapists, counselors)

### 10. Getting Help

Type `help` anytime to see:
- Crisis hotlines (988, Crisis Text Line, etc.)
- Specialized women's resources (DV hotline, RAINN)
- Your personal trusted contacts list
- Women's organizations (if family is unsafe)

---

**Need immediate help?**
- Emergency: Call 911
- Crisis: Call or text 988
- Domestic Violence: 1-800-799-7233 or text START to 88788
