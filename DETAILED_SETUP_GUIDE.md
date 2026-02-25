# AI Wellness Buddy - Complete Step-by-Step Setup Guide

## Comprehensive Installation and Configuration Manual

**Last Updated**: February 2026  
**Version**: 5.0  
**For**: Windows, macOS, and Linux

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Pre-Installation Checklist](#pre-installation-checklist)
4. [Installation Methods](#installation-methods)
5. [Step-by-Step Setup](#step-by-step-setup)
6. [Configuration](#configuration)
7. [First Run](#first-run)
8. [Advanced Features Setup](#advanced-features-setup)
9. [Testing Your Installation](#testing-your-installation)
10. [Troubleshooting](#troubleshooting)
11. [Uninstallation](#uninstallation)

---

## 1. Introduction

This guide provides complete, step-by-step instructions for installing and configuring the AI Wellness Buddy system. Whether you're a:
- **Student** setting up for an MTech project
- **Researcher** evaluating the system
- **Individual** seeking mental health support
- **Developer** contributing to the project

This guide will help you get started.

### What You'll Accomplish

By the end of this guide, you will have:
- ✅ Installed Python and all dependencies
- ✅ Downloaded the AI Wellness Buddy code
- ✅ Configured the system for your needs
- ✅ Created your first user profile
- ✅ Tested all major features
- ✅ Set up guardian/emergency contacts (optional)
- ✅ Configured language preference and voice I/O (optional)
- ✅ Configured security settings

### Time Required

- **Quick Setup** (basic installation): 10-15 minutes
- **Full Setup** (all features configured): 30-45 minutes
- **Testing & Verification**: 15-20 minutes

**Total**: 1-1.5 hours for complete setup and testing

---

## 2. System Requirements

### Minimum Requirements

**Operating System:**
- Windows 10 or later
- macOS 10.14 (Mojave) or later
- Linux (Ubuntu 18.04+, Debian 10+, Fedora 30+, or equivalent)

**Hardware:**
- CPU: Dual-core processor (2.0 GHz or faster)
- RAM: 2 GB minimum
- Storage: 500 MB free space (100 MB for application + 400 MB for dependencies)
- Display: 1024x768 minimum resolution
- Network: Internet connection required for initial setup only

**Software:**
- Python 3.7 or higher (3.9+ recommended)
- pip (Python package installer)
- Git (for downloading code)

### Recommended Configuration

**Operating System:**
- Windows 11
- macOS 13 (Ventura) or later
- Ubuntu 22.04 LTS or later

**Hardware:**
- CPU: Quad-core processor (2.5 GHz or faster)
- RAM: 4 GB or more
- Storage: 1 GB free space
- Display: 1920x1080 or higher
- Network: Wi-Fi for network UI features

**Software:**
- Python 3.11 (latest stable)
- pip 23.0+
- Git 2.40+

### Verification

Before proceeding, verify you have a compatible system:

**Windows:**
```cmd
winver
```
Look for Windows 10 version 1903 or later.

**macOS:**
```bash
sw_vers
```
Look for ProductVersion 10.14 or later.

**Linux:**
```bash
lsb_release -a
```
Look for Ubuntu 18.04+ or equivalent.

---

## 3. Pre-Installation Checklist

Before starting installation, complete this checklist:

### ☐ Python Installation Check

**Windows:**
1. Open Command Prompt (Press `Win + R`, type `cmd`, press Enter)
2. Type: `python --version`
3. Expected output: `Python 3.7.0` or higher

**macOS/Linux:**
1. Open Terminal
2. Type: `python3 --version`
3. Expected output: `Python 3.7.0` or higher

**If Python is NOT installed:**
- Windows: Download from https://www.python.org/downloads/ (check "Add Python to PATH" during installation)
- macOS: `brew install python3` (requires Homebrew)
- Linux: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### ☐ pip Installation Check

**Check pip:**
```bash
# Windows
python -m pip --version

# macOS/Linux
python3 -m pip --version
```

**Expected output:** `pip 20.0.0` or higher

**If pip is NOT installed:**
```bash
# Windows
python -m ensurepip --upgrade

# macOS/Linux
python3 -m ensurepip --upgrade
```

### ☐ Git Installation Check

**Check Git:**
```bash
git --version
```

**Expected output:** `git version 2.0.0` or higher

**If Git is NOT installed:**
- Windows: Download from https://git-scm.com/download/win
- macOS: `brew install git` or download from https://git-scm.com/download/mac
- Linux: `sudo apt install git` (Ubuntu/Debian)

### ☐ Internet Connection

Verify you have internet access:
```bash
ping google.com -c 4
```

You should see responses with times (e.g., "64 bytes from...").

### ☐ Administrator/Sudo Access

You may need administrator privileges for:
- Installing Python packages globally
- Setting file permissions
- Configuring network settings

### ☐ Disk Space

Check available disk space:

**Windows:**
```cmd
dir C:\
```
Look for "bytes free" at the bottom.

**macOS/Linux:**
```bash
df -h /
```
Look for "Available" column.

**Requirement:** At least 500 MB free.

---

## 4. Installation Methods

Choose one of three installation methods:

### Method 1: Quick Setup (Recommended for Beginners)

**Advantages:**
- Fastest method (5-10 minutes)
- Automated installation
- Includes all dependencies

**Disadvantages:**
- Less control over installation
- May install globally (affects system)

### Method 2: Manual Setup (Recommended for Developers)

**Advantages:**
- Full control over each step
- Understand what's being installed
- Better for troubleshooting

**Disadvantages:**
- Takes longer (15-20 minutes)
- More commands to run

### Method 3: Virtual Environment Setup (Recommended for Multiple Projects)

**Advantages:**
- Isolated installation (doesn't affect other projects)
- Easy to uninstall (just delete folder)
- Best practice for Python development

**Disadvantages:**
- Slightly more complex
- Need to activate environment each time

---

## 5. Step-by-Step Setup

Choose your operating system and follow the corresponding steps.

### 5.1 Windows Installation

#### Option A: Quick Setup (Windows)

**Step 1: Download the Code**

1. Open Command Prompt (`Win + R`, type `cmd`, Enter)
2. Navigate to where you want to install:
   ```cmd
   cd C:\Users\YourUsername\Documents
   ```
3. Clone the repository:
   ```cmd
   git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
   ```
4. Enter the directory:
   ```cmd
   cd AI-wellness-Buddy
   ```

**Step 2: Run Quick Setup Script**

1. Run the automated setup:
   ```cmd
   python quickstart.py
   ```
2. The script will:
   - Check Python version
   - Install all dependencies
   - Download NLTK data
   - Create configuration files
   - Test the installation

**Step 3: Verify Installation**

You should see output like:
```
✓ Python version check passed
✓ Installing dependencies...
✓ Downloading NLTK data...
✓ Creating configuration...
✓ Installation complete!

To start using AI Wellness Buddy:
  python wellness_buddy.py
```

**Jump to Section 6 (Configuration)**

#### Option B: Manual Setup (Windows)

**Step 1: Download the Code**

Same as Option A, Steps 1-4.

**Step 2: Install Dependencies**

1. Install required packages:
   ```cmd
   python -m pip install -r requirements.txt
   ```
   
   This installs:
   - nltk (Natural Language Toolkit)
   - textblob (Sentiment Analysis)
   - streamlit (Web UI)
   - cryptography (Encryption)
   - python-dateutil (Date handling)
   - gTTS (Text-to-Speech, requires internet)
   - SpeechRecognition (Voice input, requires internet)
   - langdetect (Language detection)
   - audio-recorder-streamlit (Browser microphone widget)

2. Wait for installation (2-5 minutes depending on internet speed)

3. Verify installation:
   ```cmd
   python -m pip list
   ```
   
   You should see all packages listed.

**Step 3: Download NLTK Data**

1. Run Python interactively:
   ```cmd
   python
   ```

2. Download required NLTK data:
   ```python
   import nltk
   nltk.download('brown')
   nltk.download('punkt')
   exit()
   ```

3. You should see:
   ```
   [nltk_data] Downloading package brown to ...
   [nltk_data] Downloading package punkt to ...
   ```

**Step 4: Verify Installation**

1. Run the test script:
   ```cmd
   python test_wellness_buddy.py
   ```

2. Expected output:
   ```
   Testing Emotion Analyzer...
   ✓ Sentiment analysis working
   ✓ Keyword detection working
   
   Testing Data Store...
   ✓ Encryption working
   ✓ Storage working
   
   All tests passed!
   ```

**Jump to Section 6 (Configuration)**

#### Option C: Virtual Environment Setup (Windows)

**Step 1: Create Virtual Environment**

1. Navigate to parent directory:
   ```cmd
   cd C:\Users\YourUsername\Documents
   ```

2. Create virtual environment:
   ```cmd
   python -m venv wellness-env
   ```

3. Activate virtual environment:
   ```cmd
   wellness-env\Scripts\activate
   ```

4. You should see `(wellness-env)` prefix in your prompt:
   ```
   (wellness-env) C:\Users\YourUsername\Documents>
   ```

**Step 2: Clone and Install**

1. Clone repository:
   ```cmd
   git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
   cd AI-wellness-Buddy
   ```

2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

**Step 3: Download NLTK Data**

Same as Option B, Step 3.

**Step 4: Verify**

Same as Option B, Step 4.

**Important:** Always activate virtual environment before using:
```cmd
C:\Users\YourUsername\Documents\wellness-env\Scripts\activate
```

---

### 5.2 macOS Installation

#### Option A: Quick Setup (macOS)

**Step 1: Open Terminal**

1. Press `Cmd + Space`, type "Terminal", press Enter
2. Or navigate: Applications > Utilities > Terminal

**Step 2: Install Homebrew (if not installed)**

Check if Homebrew is installed:
```bash
brew --version
```

If not found, install:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 3: Install Python 3 (if needed)**

```bash
brew install python3
```

Verify:
```bash
python3 --version
```

**Step 4: Download the Code**

1. Navigate to Documents:
   ```bash
   cd ~/Documents
   ```

2. Clone repository:
   ```bash
   git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
   cd AI-wellness-Buddy
   ```

**Step 5: Run Quick Setup**

```bash
bash quickstart.sh
```

The script will install everything automatically.

**Step 6: Verify**

You should see:
```
✓ Installation complete!
To start: python3 wellness_buddy.py
```

#### Option B: Manual Setup (macOS)

**Step 1: Download the Code**

```bash
cd ~/Documents
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
```

**Step 2: Install Dependencies**

```bash
python3 -m pip install -r requirements.txt
```

**Step 3: Download NLTK Data**

```bash
python3 -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

**Step 4: Verify**

```bash
python3 test_wellness_buddy.py
```

#### Option C: Virtual Environment (macOS)

**Step 1: Create Virtual Environment**

```bash
cd ~/Documents
python3 -m venv wellness-env
source wellness-env/bin/activate
```

**Step 2: Clone and Install**

```bash
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
pip install -r requirements.txt
```

**Step 3: Download NLTK Data**

```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

**Step 4: Verify**

```bash
python test_wellness_buddy.py
```

**Important:** Always activate before using:
```bash
source ~/Documents/wellness-env/bin/activate
```

---

### 5.3 Linux Installation (Ubuntu/Debian)

#### Option A: Quick Setup (Linux)

**Step 1: Update System**

```bash
sudo apt update
sudo apt upgrade -y
```

**Step 2: Install Prerequisites**

```bash
sudo apt install -y python3 python3-pip git
```

**Step 3: Download Code**

```bash
cd ~/Documents
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
```

**Step 4: Run Quick Setup**

```bash
bash quickstart.sh
```

**Step 5: Verify**

Should see: "✓ Installation complete!"

#### Option B: Manual Setup (Linux)

**Step 1: Install Python and pip**

```bash
sudo apt update
sudo apt install -y python3 python3-pip git
```

Verify:
```bash
python3 --version
pip3 --version
```

**Step 2: Download Code**

```bash
cd ~/Documents
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
```

**Step 3: Install Dependencies**

```bash
pip3 install -r requirements.txt
```

**Step 4: Download NLTK Data**

```bash
python3 -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

**Step 5: Verify**

```bash
python3 test_wellness_buddy.py
```

#### Option C: Virtual Environment (Linux)

**Step 1: Install venv**

```bash
sudo apt install python3-venv
```

**Step 2: Create Environment**

```bash
cd ~/Documents
python3 -m venv wellness-env
source wellness-env/bin/activate
```

**Step 3: Clone and Install**

```bash
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
pip install -r requirements.txt
```

**Step 4: Download NLTK Data**

```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

**Step 5: Verify**

```bash
python test_wellness_buddy.py
```

---

## 6. Configuration

After installation, configure the system for your needs.

### 6.1 Basic Configuration

**Step 1: Review config.py**

Open `config.py` in a text editor:

**Windows:**
```cmd
notepad config.py
```

**macOS:**
```bash
open -e config.py
```

**Linux:**
```bash
nano config.py
```

**Step 2: Key Settings to Review**

```python
# Emotional distress thresholds
DISTRESS_THRESHOLD = -0.3  # How negative before "distressed"
SUSTAINED_DISTRESS_COUNT = 3  # Consecutive distress messages for alert

# Data retention
EMOTIONAL_HISTORY_DAYS = 365  # Keep 1 year of history

# Security settings
ENABLE_PROFILE_PASSWORD = True  # Require password?
SESSION_TIMEOUT_MINUTES = 30  # Auto-logout time
ENABLE_DATA_ENCRYPTION = True  # Encrypt data?

# Guardian alerts
ENABLE_GUARDIAN_ALERTS = True  # Allow guardian notifications?
GUARDIAN_ALERT_THRESHOLD = 'high'  # When to alert: low/medium/high
AUTO_NOTIFY_GUARDIANS = False  # Ask first (recommended)
```

**Step 3: Customize for Your Needs**

**For Higher Privacy:**
```python
ENABLE_PROFILE_PASSWORD = True
ENABLE_DATA_ENCRYPTION = True
SESSION_TIMEOUT_MINUTES = 15  # Shorter timeout
```

**For Easier Access:**
```python
ENABLE_PROFILE_PASSWORD = False  # If private device
SESSION_TIMEOUT_MINUTES = 60  # Longer timeout
```

**For More Sensitive Detection:**
```python
DISTRESS_THRESHOLD = -0.2  # Detect distress earlier
SUSTAINED_DISTRESS_COUNT = 2  # Alert after 2 messages
```

**Step 4: Save Changes**

- Press `Ctrl + S` (Windows/Linux) or `Cmd + S` (macOS)
- Close the editor

### 6.2 Advanced Configuration

**Email Notifications (Optional)**

If you want to send email notifications to guardians:

1. Open `config.py`
2. Add email configuration:

```python
# Email settings (optional)
ENABLE_EMAIL_NOTIFICATIONS = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"  # Use App Password, not regular password
SYSTEM_EMAIL = "wellness-buddy@yourdomain.com"
```

**For Gmail:**
1. Go to https://myaccount.google.com/apppasswords
2. Create an App Password
3. Use that password in config

**Network UI Configuration**

For accessing from other devices:

```python
# Network UI settings
NETWORK_UI_HOST = "0.0.0.0"  # Accept connections from any device
NETWORK_UI_PORT = 8501  # Default Streamlit port
```

---

## 7. First Run

### 7.1 Starting the Application

**Option 1: Command Line Interface (CLI)**

**Windows:**
```cmd
python wellness_buddy.py
```

**macOS/Linux:**
```bash
python3 wellness_buddy.py
```

**Option 2: Web User Interface**

**Windows:**
```cmd
python -m streamlit run ui_app.py
```

**macOS/Linux:**
```bash
python3 -m streamlit run ui_app.py
```

Or use the launcher:
```bash
bash start_ui.sh
```

**Option 3: Network UI (Access from other devices)**

**Windows:**
```cmd
start_ui_network.bat
```

**macOS/Linux:**
```bash
bash start_ui_network.sh
```

### 7.2 First-Time Setup Wizard

When you first run the system, you'll see:

```
╔══════════════════════════════════════════════════════════════╗
║           Welcome to AI Wellness Buddy!                      ║
║        Your Private Mental Wellbeing Companion              ║
╚══════════════════════════════════════════════════════════════╝

This appears to be your first time using the system.
Let's set up your profile.

Press Enter to continue...
```

**Step 1: Create Username**

```
Choose a username (private, just for you):
> sarah

Great! Your data will be stored privately at:
~/.wellness_buddy/sarah.json
```

**Tips:**
- Use a name you'll remember
- No spaces or special characters
- This is just for your own reference

**Step 2: Set Password (Optional but Recommended)**

```
Would you like to set a password to protect your profile? (yes/no)
> yes

Create a password (minimum 8 characters):
> **********

Confirm password:
> **********

✓ Password set successfully!
```

**Tips:**
- Use a strong password (12+ characters recommended)
- Mix letters, numbers, symbols
- Don't forget it! (no recovery mechanism for privacy)

**Step 3: Demographic Information (Optional)**

```
The following questions help personalize support.
You can skip any question by pressing Enter.

How do you identify? (female/male/other/skip):
> female

Age range? (18-25/26-35/36-50/51+/skip):
> 26-35

✓ Profile preferences saved.
```

**Step 4: Personal History (Optional)**

```
These questions help tailor responses to your life experience.
You can skip any question by pressing Enter.

Relationship / marital status (single/married/divorced/other/skip):
> divorced

Living situation (alone/with family/with partner/in hostel/other/skip):
> Alone

Family responsibilities (caretaker/single parent/breadwinner/none/skip):
> Single parent

Occupation (student/employed/unemployed/homemaker/skip):
> Employed (full-time)

Family background (optional):
> Estranged from parents.

Any trauma or significant loss? (optional):
> Lost spouse in 2023.

Sensitive topics / triggers (comma-separated, optional):
> death, hospital

✓ Personal history saved.
```

**Step 5: Language Preference**

```
Choose your preferred response language:
  1. English (default)
  2. Tamil (தமிழ்) — responses in Tamil script
  3. Bilingual (Tamil + English) — mixed responses

Your choice (1-3): 1

✓ Language set to English.
```

**Step 6: Safety Settings**

```
For your safety, we can provide specialized resources.

Do you feel safe with your family/guardians? (yes/no/skip):
> no

✓ Noted. We'll prioritize non-family resources and trusted friends.
```

**Important:** This affects which resources are shown.

**Step 7: Encryption Setup**

```
Setting up AES-256 encryption for your data...
Generating encryption key...
✓ Encryption configured!

Your encryption key is stored at:
~/.wellness_buddy/.encryption_key

Keep your device secure. If you lose this key, data cannot be recovered.
```

**Step 8: Complete**

```
╔══════════════════════════════════════════════════════════════╗
║              Setup Complete!                                 ║
╚══════════════════════════════════════════════════════════════╝

You're all set! Your profile is ready.

What would you like to do?
  1. Start a conversation
  2. View settings
  3. Read documentation
  4. Exit

Your choice (1-4):
```

### 7.3 Your First Conversation

Choose option 1 to start:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session #1 for sarah
Started: 2024-01-15 14:30:22
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💙 Hello! I'm here to support you. How are you feeling today?

Type your message (or 'help' for options, 'quit' to end):
> I'm feeling a bit anxious about my upcoming exams

I understand. Test anxiety is very common. It sounds like you're 
feeling stressed about your exams. Would you like to talk about 
what's making you most anxious?

> Yes, I'm worried I won't remember everything I studied

That's a valid concern. Many students feel this way. The fact that
you're studying shows you care about doing well. Have you tried
any relaxation techniques before studying?

> No, I haven't. Do you have suggestions?

Absolutely! Here are some techniques that can help:
• Deep breathing: 4 seconds in, hold 4, out 4
• Take regular breaks (25 min study, 5 min break)
• Get enough sleep - crucial for memory
• Try practice tests to build confidence

Would you like to try a breathing exercise right now?

> 

Commands available:
  help    - View crisis resources, hotlines, and your trusted contacts
  status  - View risk level, stability index, emotion distribution
  weekly  - Generate 7-day wellness report with forecast
  profile - Manage personal history, language, response style, contacts
  quit    - Save and exit session
```

---

## 8. Advanced Features Setup

### 8.1 Adding Guardian/Emergency Contacts

**Via CLI:**

```
> profile

Profile Options:
1. View profile information
2. Manage guardian contacts
3. Manage trusted friends
4. View personal history
5. Add trauma / trigger
6. Change response style
7. Change language preference
8. Change password
9. Delete all my data

Your choice (1-9): 2

Guardian Contact Management:
1. Add guardian contact
2. View guardians
3. Remove guardian
4. Back

Your choice: 1

Adding Guardian Contact
━━━━━━━━━━━━━━━━━━━━━

Name: Dr. Sarah Johnson
Relationship (therapist/family/friend): therapist
Email: dr.johnson@therapy.com
Phone (optional): 555-123-4567
Notify on severity (low/medium/high): high

✓ Guardian added successfully!

Guardian Summary:
• Dr. Sarah Johnson (therapist)
• Will be notified on: HIGH severity alerts
• Contact: dr.johnson@therapy.com, 555-123-4567
```

**Via Web UI:**

1. Click "Profile" in sidebar
2. Select "Guardian Contacts"
3. Click "➕ Add Guardian"
4. Fill in the form:
   - Name: Dr. Sarah Johnson
   - Relationship: Therapist
   - Email: dr.johnson@therapy.com
   - Phone: 555-123-4567
   - Notify on: High severity
5. Click "Save"

### 8.2 Adding Trusted Friends (Non-Family)

For those who can't rely on family:

```
> profile
Your choice: 3

Trusted Friend Management:
1. Add trusted friend
2. View trusted contacts
3. Remove contact
4. Back

Your choice: 1

Adding Trusted Friend
━━━━━━━━━━━━━━━━━━━━

Name: Emma Rodriguez
Relationship: best friend
Contact info: 555-987-6543
Notes (optional): Known since college, very supportive

✓ Trusted friend added!
```

### 8.3 Configuring Alert Thresholds

Customize when alerts trigger:

```python
# In config.py

# Option 1: Conservative (fewer alerts)
GUARDIAN_ALERT_THRESHOLD = 'high'  # Only severe crises
SUSTAINED_DISTRESS_COUNT = 5  # Need 5 distress messages

# Option 2: Moderate (balanced)
GUARDIAN_ALERT_THRESHOLD = 'medium'  # Moderate and severe
SUSTAINED_DISTRESS_COUNT = 3  # Need 3 distress messages

# Option 3: Sensitive (more alerts)
GUARDIAN_ALERT_THRESHOLD = 'low'  # Any detected distress
SUSTAINED_DISTRESS_COUNT = 2  # Need 2 distress messages
```

### 8.4 Network Access Setup

To access from phone/tablet:

**Step 1: Start Network UI**

```bash
bash start_ui_network.sh
```

**Step 2: Note the Network URL**

You'll see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501

Your network IP addresses:
  • Wi-Fi: 192.168.1.100
  • Ethernet: 192.168.1.105

Share the Network URL with other devices on your network.
```

**Step 3: Access from Other Device**

On your phone/tablet:
1. Open web browser
2. Enter: `http://192.168.1.100:8501`
3. Bookmark for easy access

**Step 4: Security Note**

```
⚠️ SECURITY NOTICE ⚠️
This interface is accessible to anyone on your local network.
Only use on trusted networks (home Wi-Fi, not public Wi-Fi).
Your data remains on your computer.
```

### 8.5 Language & Voice Setup

#### Setting Language Preference

**Via CLI (during profile creation):**
```
Choose your preferred response language:
  1. English (default)
  2. Tamil (தமிழ்)
  3. Bilingual (Tamil + English)
Your choice (1-3): 2
✓ Language set to Tamil.
```

**Via CLI (after creation):**
```
You: profile
> 7. Change language preference
> Select: Bilingual
✓ Language updated to bilingual.
```

**Via Web UI:** Select from the **"Preferred language / மொழி"** dropdown in the profile creation form or from the sidebar language menu.

#### Setting Up Text-to-Speech (TTS)

TTS requires `gTTS` and an internet connection.

1. Verify gTTS is installed:
   ```bash
   python -c "from gtts import gTTS; print('gTTS OK')"
   ```
2. In the Web UI, toggle **"🔊 Voice Responses"** in the sidebar.
3. AI responses will now be read aloud in the selected language.

**Tamil TTS example:**
```python
from gtts import gTTS
tts = gTTS(text="வணக்கம்!", lang='ta')
tts.save("hello_tamil.mp3")
```

#### Setting Up Voice Input (STT)

Voice input requires `SpeechRecognition` and an internet connection.

1. Verify SpeechRecognition is installed:
   ```bash
   python -c "import speech_recognition as sr; print('SR OK')"
   ```
2. In the Web UI (💬 Chat tab), expand **"🎤 Voice Input"**.
3. Click **"Start Recording"**, speak your message, then click **"Stop"**.
4. The transcript auto-fills the chat input — review and send.

**Linux microphone setup (if needed):**
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS microphone permission:**
- System Preferences → Security & Privacy → Microphone → allow your browser.

**Windows:** Microphone should work out of the box; check Settings → Privacy → Microphone if it doesn't.

#### Disabling Voice for Offline Use

Edit `config.py`:
```python
TTS_ENABLED = False   # Responses text-only
STT_ENABLED = False   # No microphone input
```

The app always works without TTS/STT — they gracefully degrade.

---

## 9. Testing Your Installation

### 9.1 Automated Tests

Run the test suite:

```bash
python -m pytest test_wellness_buddy.py -v
```

**Expected output:**

```
Running AI Wellness Buddy Test Suite
═══════════════════════════════════════════════════════════════

Testing Emotion Analyzer...
✓ Sentiment analysis: polarity calculated correctly
✓ Multi-emotion classification (7 classes): working
✓ Confidence scoring (normalized 0-1): accurate
✓ XAI keyword attribution: working
✓ Crisis keyword detection: accurate
✓ Tamil/Tanglish emotion detection: working
✓ Abuse keyword detection: working

Testing Pattern Tracker...
✓ Emotional snapshot addition: working
✓ Consecutive distress tracking: accurate
✓ Trend calculation: correct
✓ Moving average: working
✓ Volatility & stability index: accurate
✓ 5-level risk scoring (INFO→CRITICAL): correct
✓ Emotional drift score: working
✓ 365-day retention: verified

Testing Alert System...
✓ Distress alert triggering: working
✓ Alert message formatting: correct
✓ Severity detection: accurate
✓ Guardian alert formatting: correct

Testing Prediction Agent...
✓ OLS forecast: working
✓ EWMA predictor: working
✓ Model comparison (OLS vs EWMA): working
✓ Pre-distress early warning: working

Testing Data Store...
✓ User data save: successful
✓ User data load: successful
✓ Encryption: working (AES-256)
✓ Decryption: working
✓ Backup creation: successful

Testing User Profile...
✓ Profile creation: working
✓ Personal history fields (7): all saved/loaded correctly
✓ Trauma history & triggers: working
✓ Gamification (streak, 8 badges): working
✓ Password hashing: secure (SHA-256)
✓ Password verification: accurate
✓ Session timeout: functioning
✓ Account lockout: working

Testing Bilingual & Voice...
✓ Language detection (Tamil/Tanglish/English): working
✓ Tanglish emotion detection: accurate
✓ Bilingual response selection: working
✓ Voice handler TTS (gTTS): available
✓ Voice handler STT (SpeechRecognition): available

Testing Evaluation Framework...
✓ Scenario generation (5 scenarios): working
✓ MAE/RMSE metrics: accurate
✓ Pearson correlation: working
✓ Detection metrics: working

═══════════════════════════════════════════════════════════════
Test Summary: 26/26 tests passed ✓
═══════════════════════════════════════════════════════════════

🎉 All tests passed! Your installation is working correctly.
```

**If any tests fail:**
See Section 10 (Troubleshooting)

### 9.2 Manual Feature Testing

**Test 1: Basic Conversation**

```bash
python wellness_buddy.py
```

Try:
1. Enter a positive message: "I'm feeling great today!"
2. Check sentiment is detected as positive
3. Enter a negative message: "I'm feeling really sad"
4. Check sentiment is detected as negative

**Test 2: Alert System**

Enter 3 consecutive distress messages:
1. "I'm feeling hopeless"
2. "Everything feels overwhelming"
3. "I don't know if I can go on"

You should see an alert:
```
⚠️ EMOTIONAL DISTRESS ALERT ⚠️

I've noticed sustained emotional distress.
Your wellbeing is important.

📞 General Support Resources:
  • Crisis: 988
  ...
```

**Test 3: Guardian Notification**

If you set up a guardian:
1. Trigger an alert (as above)
2. When asked "Would you like to notify guardians?"
3. Choose "Yes"
4. Verify notification is sent

**Test 4: Encryption**

1. Create a test profile
2. Add some emotional data
3. Check the data file:
   ```bash
   cat ~/.wellness_buddy/testuser.json
   ```
4. Data should look encrypted (gibberish), not readable

**Test 5: Web UI**

```bash
streamlit run ui_app.py
```

1. Browser should open automatically
2. Try all features in the web interface
3. Verify charts display correctly

**Test 6: Network Access**

```bash
bash start_ui_network.sh
```

1. Note network URL
2. Access from phone/tablet
3. Verify functionality

**Test 7: Bilingual Emotion Detection**

```bash
python wellness_buddy.py
```

Try Tamil/Tanglish input:
1. Type `romba kastam ah iruku` — should detect `sadness`
2. Type `tension ah iruku` — should detect `anxiety`
3. Set language to `bilingual` via `profile > 7`, then type a message and verify the response includes Tamil text

**Test 8: TTS & Voice Input**

```bash
streamlit run ui_app.py
```

1. Toggle **"🔊 Voice Responses"** in the sidebar — it should switch on without error
2. Send a chat message and check that a 🔊 button appears next to the response
3. Click 🔊 to play the response audio
4. In the 💬 Chat tab, expand **"🎤 Voice Input"** — record a short message and verify transcript appears

---

## 10. Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Python not found"

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**

**Windows:**
1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. Restart Command Prompt

**macOS/Linux:**
Try `python3` instead of `python`:
```bash
python3 wellness_buddy.py
```

#### Issue 2: "Module not found"

**Error:**
```
ModuleNotFoundError: No module named 'nltk'
```

**Solution:**
```bash
pip install -r requirements.txt
```

If still failing:
```bash
pip install nltk textblob streamlit cryptography python-dateutil
```

#### Issue 3: NLTK Data Missing

**Error:**
```
LookupError: Resource brown not found.
```

**Solution:**
```python
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

Or manually:
```python
python
>>> import nltk
>>> nltk.download('all')  # Downloads everything (takes longer)
>>> exit()
```

#### Issue 4: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: '.wellness_buddy'
```

**Solution:**

**Windows:**
Run Command Prompt as Administrator

**macOS/Linux:**
```bash
sudo chown -R $USER ~/.wellness_buddy
chmod 700 ~/.wellness_buddy
```

#### Issue 5: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
Change the port:
```bash
streamlit run ui_app.py --server.port 8502
```

Or kill the process using the port:

**Windows:**
```cmd
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -ti:8501 | xargs kill -9
```

#### Issue 6: Forgot Password

**Error:**
Cannot log in to profile.

**Solution:**
Reset password (data preserved):

1. Open your profile file:
   ```bash
   nano ~/.wellness_buddy/youruser.json
   ```

2. Find and change:
   ```json
   "password_hash": null,
   "salt": null,
   "security_enabled": false
   ```

3. Save and exit
4. Next login, set a new password

**Warning:** Do NOT edit other fields or data may be corrupted.

#### Issue 7: Web UI Won't Open

**Error:**
Streamlit starts but browser doesn't open.

**Solution:**
Manually open:
1. Look for output: `Local URL: http://localhost:8501`
2. Copy that URL
3. Open browser manually
4. Paste URL

Or disable auto-open:
```bash
streamlit run ui_app.py --server.headless=true
```

#### Issue 8: Encryption Key Lost

**Error:**
```
cryptography.fernet.InvalidToken: 
```

**Solution:**
If encryption key is lost, data cannot be recovered (by design for privacy).

Options:
1. Restore from backup:
   ```bash
   cp ~/.wellness_buddy/user_backup_*.json ~/.wellness_buddy/user.json
   ```

2. Start fresh (data loss):
   ```bash
   rm ~/.wellness_buddy/user.json
   rm ~/.wellness_buddy/.encryption_key
   ```

**Prevention:**
Backup your encryption key:
```bash
cp ~/.wellness_buddy/.encryption_key ~/safe-backup-location/
```

#### Issue 9: Tests Failing

**Error:**
Some tests fail.

**Solution:**

1. Check Python version:
   ```bash
   python --version
   ```
   Should be 3.7+

2. Reinstall dependencies:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. Clear cache:
   ```bash
   rm -rf __pycache__
   ```

4. Run tests with verbose output:
   ```bash
   python test_wellness_buddy.py -v
   ```

#### Issue 10: Slow Performance

**Symptoms:**
System is sluggish, responses take long.

**Solutions:**

1. **Check RAM usage:**
   Close other applications

2. **Reduce history:**
   In `config.py`:
   ```python
   EMOTIONAL_HISTORY_DAYS = 180  # Instead of 365
   ```

3. **Disable encryption (not recommended):**
   ```python
   ENABLE_DATA_ENCRYPTION = False
   ```

4. **Use CLI instead of Web UI:**
   CLI uses less resources

#### Issue 11: TTS Not Working / No Audio

**Error:**
No audio plays when TTS is enabled.

**Solution:**

1. Verify gTTS is installed:
   ```bash
   python -c "from gtts import gTTS; print('OK')"
   ```
   If not:
   ```bash
   pip install gTTS>=2.5.4
   ```

2. Check internet connection (gTTS requires network access to Google TTS).

3. Disable TTS for offline use in `config.py`:
   ```python
   TTS_ENABLED = False
   ```

#### Issue 12: Voice Input Not Recording

**Error:**
Microphone button does nothing or transcription is empty.

**Solution:**

1. Verify SpeechRecognition is installed:
   ```bash
   python -c "import speech_recognition; print('OK')"
   ```
   If not:
   ```bash
   pip install SpeechRecognition>=3.14.5 audio-recorder-streamlit>=0.0.10
   ```

2. **Linux:** Install PortAudio:
   ```bash
   sudo apt install portaudio19-dev python3-pyaudio
   pip install pyaudio
   ```

3. **macOS:** Allow microphone in System Preferences → Privacy → Microphone.

4. **Browser:** Ensure the browser has microphone permission (look for the mic icon in the URL bar).

5. Disable STT for offline use:
   ```python
   STT_ENABLED = False
   ```

---

## 11. Uninstallation

### Complete Removal

**Step 1: Delete Application Files**

**Windows:**
```cmd
cd C:\Users\YourUsername\Documents
rmdir /s AI-wellness-Buddy
```

**macOS/Linux:**
```bash
cd ~/Documents
rm -rf AI-wellness-Buddy
```

**Step 2: Delete User Data**

**Windows:**
```cmd
rmdir /s %USERPROFILE%\.wellness_buddy
```

**macOS/Linux:**
```bash
rm -rf ~/.wellness_buddy
```

**Step 3: Uninstall Python Packages (Optional)**

If not using for other projects:
```bash
pip uninstall nltk textblob streamlit cryptography python-dateutil
```

**Step 4: Delete Virtual Environment (If Used)**

**Windows:**
```cmd
rmdir /s wellness-env
```

**macOS/Linux:**
```bash
rm -rf wellness-env
```

### Partial Removal (Keep Data)

To reinstall but keep your data:

**Step 1: Backup Data**
```bash
cp -r ~/.wellness_buddy ~/wellness_buddy_backup
```

**Step 2: Delete Application**
Same as Complete Removal Step 1

**Step 3: Reinstall**
Follow installation steps again

**Step 4: Restore Data**
```bash
cp -r ~/wellness_buddy_backup ~/.wellness_buddy
```

---

## Appendix A: Command Reference

### Essential Commands

**Start CLI:**
```bash
python wellness_buddy.py
```

**Start Web UI:**
```bash
streamlit run ui_app.py
```

**Start Network UI:**
```bash
bash start_ui_network.sh
```

**Run Tests:**
```bash
python test_wellness_buddy.py
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Download NLTK Data:**
```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### In-Session Commands

**While using the system:**

- `help` — Show crisis resources, hotlines, and your trusted contacts
- `status` — View risk level, stability index, emotion distribution, 7-day history
- `weekly` / `report` — Generate 7-day wellness report with OLS forecast and suggestions
- `profile` — Manage personal history, response style, language, contacts, security
- `quit` — Save and exit (streak and badges updated)

**Profile menu options:**
```
1. View profile information
2. Manage guardian contacts
3. Manage trusted friends
4. View personal history
5. Add trauma / trigger
6. Change response style
7. Change language preference
8. Change password
9. Delete all my data
```

---

## Appendix B: File Locations

**Application Files:**
```
~/Documents/AI-wellness-Buddy/  (or installation directory)
├── wellness_buddy.py           # Main CLI application / orchestrator
├── ui_app.py                   # Web UI application (4-tab Streamlit)
├── config.py                   # Configuration
├── emotion_analyzer.py         # Multi-emotion NLP + crisis + XAI
├── pattern_tracker.py          # Pattern analysis, risk scoring, volatility
├── prediction_agent.py         # OLS emotion & risk forecasting
├── conversation_handler.py     # Emotion-routed, style-aware responses
├── alert_system.py             # Distress alert management
├── data_store.py               # Storage module (AES-256 encrypted)
├── user_profile.py             # Profile, personal history, gamification
├── language_handler.py         # Tamil/Tanglish/bilingual support
├── voice_handler.py            # TTS (gTTS) + STT (SpeechRecognition)
├── evaluation_framework.py     # Scenario-based evaluation, MAE/RMSE/correlation/t-test
└── requirements.txt            # Python dependencies
```

**User Data:**
```
~/.wellness_buddy/
├── username.json               # Your encrypted data
├── username_backup_*.json      # Automatic backups
├── .encryption_key             # Encryption key (guard carefully!)
└── wellness_buddy.log          # System logs (if enabled)
```

---

## Appendix C: Getting Help

### Documentation

- **Quick Start:** QUICK_START_GUIDE.md
- **Full Operations:** OPERATION_GUIDE.md
- **All Features:** COMPLETE_FEATURE_GUIDE.md
- **Security:** SECURITY.md
- **Data Retention:** DATA_RETENTION.md

### Support

- **GitHub Issues:** https://github.com/tk1573-sys/AI-wellness-Buddy/issues
- **Documentation:** All markdown files in repository
- **Email:** [Support email if available]

### Crisis Resources

**If you're in crisis:**
- **Call:** 988 (Suicide & Crisis Lifeline)
- **Text:** HOME to 741741 (Crisis Text Line)
- **Emergency:** 911

**This is a support tool, not emergency services.**

---

## Conclusion

You should now have AI Wellness Buddy fully installed and configured. Key achievements:

✅ System installed and verified  
✅ Profile created with personal history and language preference  
✅ Guardian contacts configured (optional)  
✅ Language & voice (TTS/STT) set up (optional)  
✅ Network access set up (optional)  
✅ All 26 tests passing  
✅ First conversation completed  

### Next Steps

1. **Use regularly:** Daily or every other day for best results
2. **Review patterns:** Check `status` weekly; type `weekly` for full 7-day report
3. **Update guardians:** Keep contacts current
4. **Backup data:** Monthly export recommended
5. **Explore features:** Try all interfaces (CLI, Web, Network) and voice I/O

### Remember

- All data stays on your device
- You control your data completely
- This supplements, not replaces, professional care
- You're not alone - help is available 24/7

**Enjoy using AI Wellness Buddy! 💙**

---

*End of Step-by-Step Setup Guide*
