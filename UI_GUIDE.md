# Web UI Guide for AI Wellness Buddy

## Overview

The AI Wellness Buddy now includes a **web-based user interface** that provides an easy-to-use, visual way to interact with the emotional wellness support system.

## Two Ways to Use the System

### 1. **Command Line Interface (CLI)** - Original
```bash
python wellness_buddy.py
```
- Text-based terminal interface
- Suitable for users comfortable with command line
- All features available

### 2. **Web UI** - New ✨
```bash
streamlit run ui_app.py
```
- Visual, browser-based interface
- Easy point-and-click navigation
- Same features with better accessibility

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
2. Optionally answer personalization questions
3. For women: Option to mark family as unsafe
4. Click "Create Profile"

**Returning Users:**
1. Click "Load Existing Profile"
2. Select your username from dropdown
3. Click "Load Profile"

### Step 4: Start Chatting

- Type your feelings in the chat input box
- Press Enter or click Send
- Receive empathetic responses from the AI
- Your conversation is analyzed in real-time

---

## Web UI Features

### 💬 **Chat Interface**
- Clean, modern chat layout
- Real-time emotional analysis
- Message history visible in chat window

### 📞 **Help & Resources Button**
- View crisis hotlines instantly
- See your trusted contacts
- Access women's support resources (if applicable)

### 📊 **Emotional Status Button**
- Current session summary
- 7-day emotional trends
- Pattern analysis

### ⚙️ **Manage Profile Button**
- Add trusted contacts
- View existing contacts
- Mark family as unsafe
- Delete all data

### 🚪 **End Session Button**
- Save your progress
- View session summary
- Close safely

---

## Web UI Screenshots

### Main Chat Interface
```
┌─────────────────────────────────────────┐
│  🌟 AI Wellness Buddy                   │
├─────────────────────────────────────────┤
│ Sidebar:                    │ Chat:     │
│ - User: sarah              │           │
│ - Session: #3              │ You:      │
│                            │ I'm...    │
│ Commands:                  │           │
│ [📞 Help & Resources]      │ Buddy:    │
│ [📊 Emotional Status]      │ I hear... │
│ [⚙️ Manage Profile]        │           │
│ [🚪 End Session]           │ Input:    │
│                            │ [Type...] │
└────────────────────────────────────────┘
```

---

## Advantages of Web UI

✅ **Visual & Intuitive** - No command memorization needed  
✅ **Accessible** - Works in any modern browser  
✅ **Clean Layout** - Easy to read conversation history  
✅ **Button Navigation** - Simple point-and-click for commands  
✅ **Responsive** - Works on desktop and tablets  
✅ **Same Features** - All CLI functionality available  
✅ **Professional Look** - Modern interface design  

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
