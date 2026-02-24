# AI Emotional Wellness Buddy 🌟

An AI-based emotional wellness support system that provides continuous text-based emotional support, tracks emotional patterns over time, and triggers alerts when sustained emotional distress is detected. The system creates private user profiles to understand emotional history through daily conversations and provides specialized safety features for women in toxic environments.

## 🎯 Features

### Core Capabilities
- **Persistent User Profiles**: Private profiles with secure local storage for continuous support across sessions
- **Extended Emotional History**: **NEW: 365-day tracking** (upgraded from 90 days) for comprehensive long-term pattern analysis
- **Text-based Emotional Interaction**: Continuous conversational support with emotion-aware responses
- **Emotion Analysis**: Advanced sentiment analysis and emotion classification using natural language processing
- **Pattern Tracking**: Monitors emotional trends over time to identify concerning patterns
- **Distress Alert System**: Automatically triggers alerts when sustained emotional distress is detected (3+ consecutive distress messages)
- **Resource Connection**: Provides immediate access to crisis hotlines and support resources

### Enhanced Security Features 🔒 NEW
- **Password Protection**: Secure profile access with password/PIN (SHA-256 hashing)
- **Data Encryption**: AES-256 encryption for all stored data
- **Session Timeout**: Automatic logout after inactivity (default: 30 minutes)
- **Account Lockout**: Protection against brute force attacks (3 attempts, 15-minute lockout)
- **Data Integrity**: SHA-256 hashing for data verification
- **Automatic Backups**: Timestamped backups before critical operations
- **File Permissions**: Owner-only access to data files (Unix/Linux)

### Guardian Alert System 👨‍👩‍👧‍👦 NEW
- **Emergency Contact Notification**: Alerts designated guardians (therapist, family, friends) during severe distress
- **Multi-Level Severity**: Configure alerts for low, medium, or high severity distress
- **Privacy-Respecting**: System asks before notifying guardians (optional auto-notify)
- **Actionable Information**: Guardians receive formatted alerts with specific indicators and professional resources
- **Threshold Configuration**: Control when guardians are notified based on distress patterns
- **Multiple Guardians**: Add multiple emergency contacts with different notification preferences

### Specialized Support for Women
- **Safe Support Network**: Avoid harmful family contacts in toxic situations; guide toward trusted friends and organizations
- **Trusted Contacts Management**: Add and manage your own safe support network (friends, not family if unsafe)
- **Women's Organizations**: Direct connection to specialized women's support organizations
- **Government Resources**: ⭐ **NEW**: Access to 15+ government agencies (Office on Women's Health, Violence Against Women Office, Legal Services)
- **Legal Aid Connections**: ⭐ **NEW**: National Women's Law Center, Legal Services Corporation, American Bar Association
- **Mental Health Support**: ⭐ **NEW**: Women-specific mental health resources (NIMH Women's Health, Postpartum Support)
- **Abuse Detection**: Identifies potential indicators of emotional abuse in toxic family or marital environments
- **Safety Navigation**: Direct connection to domestic violence hotlines and safety planning resources
- **User Control**: You decide who to trust and what support you need
- **Confidential & Safe**: Private, judgment-free space for emotional expression

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Download required NLTK data (first time only):
```python
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### Running the Application

**Option 1: Command Line Interface (CLI)**
```bash
python wellness_buddy.py
```

**Option 2: Web UI - Local Access** ✨
```bash
streamlit run ui_app.py
```
Opens in your browser at `http://localhost:8501` with a visual, point-and-click interface.

**Option 3: Web UI - Network Access** 🌐 New!
```bash
bash start_ui_network.sh
```
Accessible from any device on your network. The script displays both local and network URLs.

**See `UI_GUIDE.md` for Web UI instructions and `NETWORK_DEPLOYMENT.md` for network/internet deployment options.**

### First Time Setup

On first run, you'll:
1. Create a private username (for your eyes only)
2. Optionally answer personalization questions
3. If you're a woman in an unsafe family situation, you can:
   - Mark family/guardians as unsafe
   - Add trusted friends to your support network
   - Get guidance toward women's organizations instead of family

### Returning Users

The system remembers you! When you return:
- Your profile loads automatically
- Your emotional history is available
- Pattern tracking continues across sessions
- Trusted contacts are preserved

## 💬 How to Use

1. **Create/Load Profile**: Choose a username to create a new profile or load an existing one
2. **Setup Support Network**: Add trusted friends and mark unsafe family if needed (optional)
3. **Share Your Feelings**: Type messages describing how you're feeling
4. **Receive Support**: Get empathetic responses based on your emotional patterns over time
5. **Access Resources**: Type 'help' to see support hotlines and your trusted contacts
6. **Track Patterns**: Type 'status' to view current session and long-term emotional history
7. **Manage Profile**: Type 'profile' to add trusted contacts or update settings
8. **End Session**: Type 'quit' to safely end and save your session

### Commands
- `help` - Display support resources, hotlines, and your trusted contacts
- `status` - Show emotional pattern summary (current session + last 7 days, or full year)
- `profile` - Manage trusted contacts, security settings, and delete data
- `quit` - End the session and save your progress

## 🔒 Privacy & Security

### Enhanced Security Features (NEW)
- **Password Protection**: Set a password to protect your profile from unauthorized access
- **AES-256 Encryption**: All data encrypted at rest with industry-standard encryption
- **Session Timeout**: Automatic logout after 30 minutes of inactivity
- **Account Lockout**: Protection against brute force password attempts
- **Secure Storage**: Encryption keys and data files with restricted permissions (owner-only)

### Data Privacy
- **Local Storage Only**: All data is stored privately on your device in `~/.wellness_buddy/`
- **No External Sharing**: Your conversations and profile are never shared externally
- **Full User Control**: Delete your data anytime via the profile menu
- **Encrypted Files**: Data files use JSON format with optional AES-256 encryption
- **Safe Support**: For women in toxic situations, family contacts are avoided; trusted friends prioritized
- **Automatic Backups**: System creates timestamped backups before critical operations
- This is a support tool, not a replacement for professional mental health care
- Emergency services (911) should be contacted for immediate danger

### Security Best Practices
- Set a strong password (minimum 8 characters, recommended 12+)
- Keep your device secure with device password/lock
- Use only on trusted networks
- Backup your encryption key to a secure location
- Enable all security features for maximum protection

📖 **For detailed security information, see [SECURITY.md](SECURITY.md)**

## 📞 Crisis Resources

### General Support
- **Crisis Hotline**: 988 (Suicide & Crisis Lifeline)
- **Crisis Text Line**: Text HOME to 741741
- **SAMHSA Hotline**: 1-800-662-4357

### Specialized Support for Women
- **Domestic Violence Hotline**: 1-800-799-7233
- **Domestic Violence Text**: Text START to 88788
- **Sexual Assault Hotline**: 1-800-656-4673 (RAINN)
- **Safety Planning**: Visit thehotline.org

### Trusted Support Network (Non-Family for Toxic Situations)
- **National Coalition Against Domestic Violence**: 1-303-839-1852
- **National Organization for Women**: 202-628-8669
- **Women's Resource Center**: Check local listings
- **Professional Support**: Confidential therapists, counselors, social workers
- **Women's Shelters**: For guidance and safety planning

## 🧠 How It Works

### User-Centric Design
The system builds a private profile for each user and continuously understands their emotional history through daily conversations. Instead of just reacting to single messages, it observes emotional patterns over time and responds with empathetic, supportive replies that validate feelings.

### Emotion Analysis
The system uses TextBlob for sentiment analysis, combined with keyword detection to:
- Analyze emotional polarity (positive to negative)
- Detect distress-related keywords (24+ indicators)
- Identify potential abuse indicators (16+ indicators)
- Classify emotional states (positive, neutral, negative, distress)

### Pattern Tracking
- **Session-level**: Rolling window of recent emotional states within current session
- **Multi-day**: Tracks emotional history across sessions (up to 365 days)
- Tracks consecutive distress messages
- Calculates emotional trends (improving, stable, declining)
- Monitors for sustained distress patterns

### Alert System with Safety Features
- Triggers when 3+ consecutive distress messages are detected
- Provides general crisis resources
- For women with unsafe family situations:
  - Avoids suggesting family/guardian contacts
  - Guides toward trusted friends and women's organizations
  - Shows user's own trusted contacts list
  - Emphasizes user control and choice
- Includes abuse-specific resources when indicators are detected

### Data Persistence
- Profiles stored locally in `~/.wellness_buddy/`
- JSON format for easy portability
- Emotional snapshots saved after each session
- Trusted contacts preserved across sessions
- User can delete all data at any time

## 🏗️ Project Structure

```
AI-wellness-Buddy/
├── wellness_buddy.py       # Main application with profile management
├── emotion_analyzer.py     # Emotion analysis and sentiment detection
├── pattern_tracker.py      # Emotional pattern tracking
├── alert_system.py         # Distress alert management with safety features
├── conversation_handler.py # Conversation flow management
├── user_profile.py         # User profile with trusted contacts
├── data_store.py          # Persistent data storage
├── config.py              # Configuration settings
├── ui_app.py              # Streamlit web interface
├── start_ui.sh            # Local UI launcher script
├── start_ui_network.sh    # Network UI launcher script (NEW)
├── .streamlit/
│   └── config.toml        # Streamlit network configuration
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── USAGE.md               # Quick start guide
├── UI_GUIDE.md            # Web UI guide
├── NETWORK_DEPLOYMENT.md  # Network deployment guide
├── SECURITY.md            # Security features guide (NEW)
├── DATA_RETENTION.md      # Data tracking and retention guide (NEW)
├── COMPLETE_FEATURE_GUIDE.md  # Complete feature documentation (NEW)
└── TECHNOLOGIES_AND_DATASETS.md  # Technologies and datasets documentation
```

## 🛠️ Technologies & Datasets

**For a complete overview of all technologies, libraries, frameworks, and datasets used in this project, see [TECHNOLOGIES_AND_DATASETS.md](TECHNOLOGIES_AND_DATASETS.md).**

### Quick Summary
- **NLP Libraries**: NLTK (>=3.8.1), TextBlob (>=0.17.1)
- **Web Framework**: Streamlit (>=1.28.0)
- **Security**: cryptography (>=41.0.0) for AES-256 encryption
- **NLTK Datasets**: Brown Corpus, Punkt Tokenizer Models
- **Storage**: Local JSON files (`~/.wellness_buddy/`) with optional encryption
- **Privacy**: All processing done locally, no external APIs

## 📊 Extended Tracking & Data Retention

**The system now tracks your emotional wellbeing for a full year (365 days) instead of 90 days.**

### What's Tracked
- **365 Days**: Full year of emotional history snapshots
- **Long-term Patterns**: Seasonal variations, monthly trends, annual progress
- **Progress Milestones**: Track improvement from significant life events
- **Comprehensive Analytics**: Better insights with more historical data

### Benefits
- See your full year emotional journey
- Identify seasonal patterns (e.g., winter blues, summer highs)
- Track long-term progress and improvements
- More accurate trend detection
- Better understanding of your mental health patterns

📖 **For detailed information on data retention and tracking, see [DATA_RETENTION.md](DATA_RETENTION.md)**

## 🌐 Network Deployment

**For detailed network deployment instructions, see [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md).**

### Quick Network Access

Access the UI from any device on your network:
```bash
bash start_ui_network.sh
```

The app will be available at:
- **Local**: `http://localhost:8501`
- **Network**: `http://YOUR-IP:8501` (displayed when app starts)

### Deployment Options
- **Local Network**: Access from devices on same Wi-Fi/LAN
- **Streamlit Cloud**: Free cloud deployment for internet access
- **VPS/Cloud Server**: Self-hosted with custom domain
- **Docker**: Containerized deployment

⚠️ **Security Note**: When enabling network access, ensure you're on a trusted network. See [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md) for security best practices.

## 🛠️ Configuration

Key settings can be adjusted in `config.py`:
- `DISTRESS_THRESHOLD`: Sentiment threshold for distress detection (-0.3)
- `SUSTAINED_DISTRESS_COUNT`: Messages needed to trigger alert (3)
- `PATTERN_TRACKING_WINDOW`: Number of messages to analyze (10)

## 🤝 Contributing

This project aims to provide emotional support and connect people with professional resources. Contributions that enhance safety, support, and user experience are welcome.

## ⚠️ Disclaimer

This AI Wellness Buddy is a support tool designed to provide emotional support and connect users with professional resources. It is **not a substitute** for professional mental health care, therapy, or emergency services. 

- For mental health emergencies, call 988 or your local emergency services
- For domestic violence emergencies, call 911 or 1-800-799-7233
- Always consult with qualified mental health professionals for ongoing support

## 📚 Complete Documentation

### Getting Started Documentation
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - ⭐ **NEW**: Get started in 5 minutes
- **[OPERATION_GUIDE.md](OPERATION_GUIDE.md)** - ⭐ **NEW**: Complete operational manual (16KB)
- **[USAGE.md](USAGE.md)** - Quick start guide for basic usage
- **[UI_GUIDE.md](UI_GUIDE.md)** - Web interface guide with screenshots

### Project Understanding
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - ⭐ **NEW**: What this project does (15KB)
- **[COMPLETE_FEATURE_GUIDE.md](COMPLETE_FEATURE_GUIDE.md)** - All features explained (21KB)
- **[README.md](README.md)** - This file, overview and introduction

### Technical Documentation
- **[SECURITY.md](SECURITY.md)** - Complete security features guide (11KB)
- **[DATA_RETENTION.md](DATA_RETENTION.md)** - Extended tracking and data management (13KB)
- **[TECHNOLOGIES_AND_DATASETS.md](TECHNOLOGIES_AND_DATASETS.md)** - Technologies and datasets used

### Deployment Guides
- **[NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)** - Network and cloud deployment guide
- **[NETWORK_QUICK_START.md](NETWORK_QUICK_START.md)** - Quick network access guide
- **[NETWORK_UI_VISUAL_GUIDE.md](NETWORK_UI_VISUAL_GUIDE.md)** - Visual network UI guide

### Academic & Research
- **[MTECH_PROJECT_ASSESSMENT.md](MTECH_PROJECT_ASSESSMENT.md)** - ⭐ **NEW**: MTech suitability analysis (16KB)
  - Suitability rating: 9.3/10 ⭐⭐⭐⭐⭐
  - Grade projection: A+ (90-95%)
  - Publication potential: 2-4 papers
  - Enhancement recommendations

### Quick Reference Table

| Document | Topic | Size | Audience |
|----------|-------|------|----------|
| **QUICK_START_GUIDE.md** | Get started in 5 min | 8KB | New users |
| **OPERATION_GUIDE.md** | Complete operations | 16KB | All users |
| **PROJECT_OVERVIEW.md** | What project does | 15KB | Everyone |
| **COMPLETE_FEATURE_GUIDE.md** | All features | 21KB | Power users |
| **SECURITY.md** | Security features | 11KB | Security-conscious |
| **DATA_RETENTION.md** | 365-day tracking | 13KB | Data management |
| **MTECH_PROJECT_ASSESSMENT.md** | Academic suitability | 16KB | Students/Faculty |

**Total Documentation**: 100KB+ of comprehensive guides

📖 **Start with [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for immediate usage or [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) to understand what the project does.**

## 📄 License

This project is open source and available for use in supporting emotional wellness.

## 🌟 Mission

Our mission is to provide accessible emotional support for everyone, with specialized features to help women and individuals experiencing emotional abuse in toxic environments. Everyone deserves to feel safe, supported, and heard.

---

**Remember**: You are not alone. Help is available 24/7. You deserve support and care. 💙