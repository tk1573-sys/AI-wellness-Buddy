# Web UI Guide for AI Wellness Buddy

## Overview

The AI Wellness Buddy includes a **web-based user interface** with a full analytics dashboard that provides an easy-to-use, visual way to interact with the emotional wellness support system.

## Two Ways to Use the System

### 1. **Command Line Interface (CLI)** — Original
```bash
python wellness_buddy.py
```
- Text-based terminal interface
- Suitable for users comfortable with command line
- All features available (including `weekly` report, status, profile)

### 2. **Web UI** — 4-Tab Analytics Dashboard ✨
```bash
streamlit run ui_app.py
```
- Visual, browser-based interface
- Easy point-and-click navigation
- 4 tabs: Chat, Emotional Trends, Risk Dashboard, Weekly Report
- Live risk level and streak in the sidebar

---

## Getting Started with Web UI

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### Step 2: Launch the Web UI

```bash
streamlit run ui_app.py
```

This will:
- Start a local web server
- Automatically open your browser to `http://localhost:8501`
- Display the AI Wellness Buddy interface

### Step 3: Create or Load Profile

**First Time Users:**
1. Enter a username (private, for your eyes only)
2. Fill in optional personalization fields: gender, marital status, **response style**, family background, trauma history, personal triggers
3. For women: Option to mark family as unsafe
4. Click "Create Profile"

**Returning Users:**
1. Click "Load Existing Profile"
2. Select your username from the dropdown
3. Click "Load Profile"

### Step 4: Start Chatting

- Type your feelings in the chat input box
- Press Enter or click Send
- Receive empathetic, emotion-specific responses
- Each response includes an XAI explanation of which keywords were detected

---

## 4-Tab Dashboard

### 💬 Tab 1 — Chat

- Clean, modern chat layout
- Real-time multi-emotion analysis (joy/sadness/anger/fear/anxiety/crisis)
- XAI attribution shown under each response: *"(Analysis: Detected 'anxiety' due to keywords: anxious, overwhelmed)"*
- Message history visible in chat window

### 📈 Tab 2 — Emotional Trends

- **Sentiment over messages** — line chart of session polarity
- **3-message moving average** — smoothed trend line
- **Emotion distribution** — bar chart of fine-grained emotions in current session
- **30-day session history** — long-term mood line chart
- **OLS next-session forecast** — predicted sentiment with interpretation
- **Stability metrics** — volatility and stability index (0–1)

### ⚠️ Tab 3 — Risk Dashboard

- **Current risk level** — displayed as 🟢 Low / 🟡 Medium / 🔴 High / 🚨 Critical
- **Risk score progress bar** — numeric score (0.00–1.00)
- **Key metrics**: risk score, stability, volatility, consecutive distress count
- **30-day risk history** — line chart of risk level over time
- **Risk escalation forecast** — will risk increase next session?
- **Mood streak** — consecutive positive sessions
- **Wellness badges** — earned badges displayed here

### 📋 Tab 4 — Weekly Report

- 7-day summary with check-in count, average mood, risk incidents
- Mood streak count
- Emotion distribution for the week
- OLS next-session forecast with confidence level
- Personalized improvement suggestions

---

## Sidebar (always visible)

```
┌─────────────────────────────┐
│ User: sarah                 │
│ Session: #14                │
│ Risk: 🟡 MEDIUM             │
│ ─────────────────────────── │
│ Quick Actions               │
│ [📞 Help & Resources]       │
│ [📊 Emotional Status]       │
│ [⚙️ Manage Profile]         │
│ ─────────────────────────── │
│ [🚪 End Session]            │
└─────────────────────────────┘
```

- **Risk level** updates automatically after every message
- **Manage Profile** opens profile management options including personal history, response style, and contact management

---

## Advantages of Web UI

✅ **4-Tab Analytics Dashboard** — full trend, risk, and report views  
✅ **Live Risk Indicator** — always visible in the sidebar  
✅ **XAI Transparency** — see why the AI classified each emotion  
✅ **Visual & Intuitive** — no command memorization needed  
✅ **Accessible** — works in any modern browser  
✅ **Responsive** — works on desktop and tablets  
✅ **Same Features** — all CLI functionality available  
✅ **Professional Look** — modern health analytics interface  

---

## Technical Details

### What is Streamlit?
- Python framework for building web UIs
- No HTML/CSS/JavaScript knowledge needed
- Runs locally on your computer
- Completely private - no external servers

### How It Works
1. Streamlit creates a local web server on your machine
2. Your browser connects to `localhost:8501`
3. All data stays on your computer (same as CLI version)
4. Uses the same backend code as CLI version

### Requirements
- Python 3.7+
- Streamlit 1.28.0+
- All original dependencies (nltk, textblob)

---

## Troubleshooting

### Port Already in Use
```bash
streamlit run ui_app.py --server.port 8502
```

### Browser Doesn't Open Automatically
Manually visit: `http://localhost:8501`

### UI Doesn't Start
Check if Streamlit is installed:
```bash
pip install streamlit --upgrade
```

---

## Comparison: CLI vs Web UI

| Feature | CLI | Web UI |
|---------|-----|--------|
| Installation | ✅ Minimal | ✅ +Streamlit |
| Interface | Terminal | Browser |
| Commands | Type commands | Click buttons |
| History | Scrollback | Visual chat |
| Profile Setup | Text prompts | Form fields |
| Resources | Text display | Formatted view |
| Accessibility | Terminal users | All users |

---

## Privacy & Security

Both CLI and Web UI:
- ✅ Run locally on your computer
- ✅ No internet connection required (after dependencies installed)
- ✅ Data stored in `~/.wellness_buddy/`
- ✅ No external servers involved
- ✅ Same privacy guarantees

---

## Recommended For

**Use CLI if:**
- You prefer terminal interfaces
- You want minimal dependencies
- You're comfortable with text commands

**Use Web UI if:**
- You want a visual interface
- You prefer point-and-click
- You want easier navigation
- You're new to the system

---

## Quick Reference

### Starting the UI
```bash
streamlit run ui_app.py
```

### Stopping the UI
- Press `Ctrl+C` in terminal
- Or close the terminal window

### Default URL
```
http://localhost:8501
```

### Data Location
Same as CLI: `~/.wellness_buddy/{username}.json`

---

## Next Steps

1. ✅ Install dependencies with Streamlit
2. ✅ Run `streamlit run ui_app.py`
3. ✅ Create or load your profile
4. ✅ Start sharing your feelings
5. ✅ Use buttons for easy navigation

**Need help?** See `USAGE.md` for detailed instructions on features and commands.
