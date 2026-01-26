# AI Emotional Wellness Buddy 🌟

An AI-based emotional wellness support system that provides continuous text-based emotional support, tracks emotional patterns over time, and triggers alerts when sustained emotional distress is detected.

## 🎯 Features

### Core Capabilities
- **Text-based Emotional Interaction**: Continuous conversational support with emotion-aware responses
- **Emotion Analysis**: Advanced sentiment analysis and emotion classification using natural language processing
- **Pattern Tracking**: Monitors emotional trends over time to identify concerning patterns
- **Distress Alert System**: Automatically triggers alerts when sustained emotional distress is detected (3+ consecutive distress messages)
- **Resource Connection**: Provides immediate access to crisis hotlines and support resources

### Specialized Support
- **Women's Support**: Specialized safety and support resources for women experiencing emotional abuse
- **Abuse Detection**: Identifies potential indicators of emotional abuse in toxic family or marital environments
- **Safety Navigation**: Direct connection to domestic violence hotlines and safety planning resources
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

## 💬 How to Use

1. **Start a Session**: Run the application and optionally set up your profile for personalized support
2. **Share Your Feelings**: Type messages describing how you're feeling
3. **Receive Support**: Get empathetic responses and emotional support
4. **Access Resources**: Type 'help' to see support hotlines and resources
5. **Track Patterns**: Type 'status' to view your emotional pattern summary
6. **End Session**: Type 'quit' to safely end your session

### Commands
- `help` - Display support resources and hotlines
- `status` - Show emotional pattern summary
- `quit` - End the session

## 🔒 Privacy & Safety

- All conversations are processed locally in your session
- No data is stored permanently or shared externally
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

## 🧠 How It Works

### Emotion Analysis
The system uses TextBlob for sentiment analysis, combined with keyword detection to:
- Analyze emotional polarity (positive to negative)
- Detect distress-related keywords
- Identify potential abuse indicators
- Classify emotional states (positive, neutral, negative, distress)

### Pattern Tracking
- Maintains a rolling window of recent emotional states
- Tracks consecutive distress messages
- Calculates emotional trends (improving, stable, declining)
- Monitors for sustained distress patterns

### Alert System
- Triggers when 3+ consecutive distress messages are detected
- Provides general crisis resources
- Offers specialized women's support when appropriate
- Includes abuse-specific resources when indicators are detected

## 🏗️ Project Structure

```
AI-wellness-Buddy/
├── wellness_buddy.py       # Main application
├── emotion_analyzer.py     # Emotion analysis and sentiment detection
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