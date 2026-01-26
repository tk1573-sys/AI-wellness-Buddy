# AI Emotional Wellness Buddy 🌟

An AI-based emotional wellness support system that provides continuous text-based emotional support, tracks emotional patterns over time, and triggers alerts when sustained emotional distress is detected. The system creates private user profiles to understand emotional history through daily conversations and provides specialized safety features for women in toxic environments.

## 🎯 Features

### Core Capabilities
- **Persistent User Profiles**: Private profiles with secure local storage for continuous support across sessions
- **Multi-Day Emotional History**: Tracks emotional patterns over days/weeks, not just single sessions
- **Text-based Emotional Interaction**: Continuous conversational support with emotion-aware responses
- **Emotion Analysis**: Advanced sentiment analysis and emotion classification using natural language processing
- **Pattern Tracking**: Monitors emotional trends over time to identify concerning patterns
- **Distress Alert System**: Automatically triggers alerts when sustained emotional distress is detected (3+ consecutive distress messages)
- **Resource Connection**: Provides immediate access to crisis hotlines and support resources

### Specialized Support for Women
- **Safe Support Network**: Avoid harmful family contacts in toxic situations; guide toward trusted friends and organizations
- **Trusted Contacts Management**: Add and manage your own safe support network (friends, not family if unsafe)
- **Women's Organizations**: Direct connection to specialized women's support organizations
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

Start the AI Wellness Buddy:
```bash
python wellness_buddy.py
```

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
- `status` - Show emotional pattern summary (current session + last 7 days)
- `profile` - Manage trusted contacts and safety settings
- `quit` - End the session and save your progress

## 🔒 Privacy & Safety

- **Local Storage Only**: All data is stored privately on your device in `~/.wellness_buddy/`
- **No External Sharing**: Your conversations and profile are never shared externally
- **Full User Control**: Delete your data anytime via the profile menu
- **Encryption Ready**: Data files use JSON format (can be encrypted if needed)
- **Safe Support**: For women in toxic situations, family contacts are avoided; trusted friends prioritized
- This is a support tool, not a replacement for professional mental health care
- Emergency services (911) should be contacted for immediate danger

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
- **Multi-day**: Tracks emotional history across sessions (up to 90 days)
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
├── data_store.py          # Persistent data storage (NEW)
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```
├── pattern_tracker.py      # Emotional pattern tracking
├── alert_system.py         # Distress alert management
├── conversation_handler.py # Conversation flow management
├── user_profile.py         # User profile for personalized support
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

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

## 📄 License

This project is open source and available for use in supporting emotional wellness.

## 🌟 Mission

Our mission is to provide accessible emotional support for everyone, with specialized features to help women and individuals experiencing emotional abuse in toxic environments. Everyone deserves to feel safe, supported, and heard.

---

**Remember**: You are not alone. Help is available 24/7. You deserve support and care. 💙