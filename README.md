# AI Emotional Wellness Buddy 🌟

An AI-based emotional wellness support system that provides continuous text-based emotional support, tracks emotional patterns over time, and triggers alerts when sustained emotional distress is detected. The system creates private user profiles to understand emotional history through daily conversations and provides specialized safety features for women in toxic environments.

## 🎯 Features

### Core Capabilities
- **Persistent User Profiles**: Private profiles with secure local storage for continuous support across sessions
- **Extended Emotional History**: 365-day tracking for comprehensive long-term pattern analysis
- **Text-based Emotional Interaction**: Continuous conversational support with emotion-aware, humanoid responses
- **Multi-Emotion Analysis**: Fine-grained classification of **joy, sadness, anger, fear, anxiety, and crisis** using NLP — not just positive/negative
- **Crisis Detection**: Dedicated crisis keyword detection with immediate 988 / 911 escalation
- **XAI Explanations**: Every response shows which keywords drove the emotion classification (e.g. *"Detected 'anxiety' due to keywords: anxious, overwhelmed"*)
- **Pattern Tracking**: Monitors emotional trends over time including moving average, volatility, and stability index
- **Formula-based Risk Scoring**: Intelligent Low / Medium / High / Critical risk score (not simple threshold logic)
- **Emotion Trend Forecasting**: OLS + EWMA + lightweight GRU-style neural forecasting benchmarks
- **Distress Alert System**: Automatically triggers alerts when sustained emotional distress is detected (3+ consecutive distress messages)
- **Resource Connection**: Provides immediate access to crisis hotlines and support resources

### Personal History & Context Awareness 🧠
- **Trauma History**: Record past trauma so responses are extra sensitive to your experience
- **Personal Triggers**: Flag topics or words that are especially sensitive — the system responds with extra care when they arise
- **Marital / Relationship Status**: Used to personalise responses for transitions like divorce or loss
- **Family Background**: Gives context for empathetic, culturally-aware support
- **Living Situation**: Whether you live alone, with family, in a hostel, etc. — safety-aware responses
- **Family Responsibilities**: Caretaker, single parent, breadwinner — the system acknowledges the weight you carry
- **Occupation**: Student, employed, unemployed, homemaker — work-stress context used for anxiety/anger personalisation
- **Response Style Preference**: Choose **Short**, **Balanced** (default), or **Detailed** replies to match how you like to communicate

### Bilingual Tamil/English & Voice Support 🌐
- **Bilingual Responses**: Reply in English, Tamil Unicode (தமிழ்), or Bilingual (Tamil + English mixed)
- **Tanglish Auto-Detection**: Automatically detects Tamil written in Roman/English script (e.g. "romba kastam") and responds appropriately
- **Tamil Emotion Keywords**: All 6 emotion classes have Tamil Unicode AND Tanglish keyword dictionaries
- **Text-to-Speech (TTS)**: AI responses read aloud via gTTS — language-aware (`ta` for Tamil, `en` for English)
- **Voice Input (STT)**: Record your message in the browser — transcribed via Google Speech Recognition (`en-IN` / `ta-IN`)
- **Language in Profile**: Language preference stored per user and applied to every session

### Gamification & Wellness Tracking 🏅
- **Mood Streak**: Consecutive positive-mood session counter to celebrate progress
- **Wellness Badges**: Earn 8 badge types — First Step, Consistent (7 sessions), Dedicated (30 sessions), 3-Day Streak, 7-Day Streak, Resilient, Self-Aware, Connected
- **Weekly Summary Report**: Full 7-day breakdown — emotion distribution, risk incidents, average mood, suggestions, and OLS forecast — available via the `weekly` command
- **Password Protection**: Secure profile access with bcrypt hashing (+ legacy migration)
- **Data Encryption**: Fernet encryption for all stored data at rest
- **Session Timeout**: Automatic logout after inactivity (default: 30 minutes)
- **Account Lockout**: Protection against brute force attacks (3 attempts, 15-minute lockout)
- **Data Integrity**: SHA-256 hashing for data verification
- **Automatic Backups**: Timestamped backups before critical operations
- **File Permissions**: Owner-only access to data files (Unix/Linux)

### Guardian Alert System 👨‍👩‍👧‍👦
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
- **Government Resources**: Access to 15+ government agencies (Office on Women's Health, Violence Against Women Office, Legal Services)
- **Legal Aid Connections**: National Women's Law Center, Legal Services Corporation, American Bar Association
- **Mental Health Support**: Women-specific mental health resources (NIMH Women's Health, Postpartum Support)
- **Abuse Detection**: Identifies potential indicators of emotional abuse in toxic family or marital environments
- **Safety Navigation**: Direct connection to domestic violence hotlines and safety planning resources
- **User Control**: You decide who to trust and what support you need
- **Confidential & Safe**: Private, judgment-free space for emotional expression

## 🚀 Getting Started

## 🧪 Research-Grade Upgrade (New)
- **Modular Agent Pipeline**: `agent_pipeline.py` separates emotion analysis, pattern tracking, forecasting, alerting, and response generation.
- **Transformer-First Emotion + Contextual Crisis**: `emotion_analyzer.py` now exposes probability-based emotion outputs and contextual crisis probabilities.
- **Scientific Evaluation Utilities**: `research_evaluation.py` adds dataset evaluation pipelines with precision/recall/F1 reporting.
- **GoEmotions Dataset Loader**: `datasets/goemotions_loader.py` maps 28 GoEmotions fine-grained labels to the 6 system emotion classes.
- **Evaluation Pipeline**: `evaluation/emotion_model_evaluation.py` computes precision, recall, macro F1, accuracy, and confusion matrices.
- **Benchmark Script**: `run_emotion_benchmark.py` runs the full GoEmotions evaluation and exports results to `results/emotion_model_benchmark.json`.
- **Clinical Distress Indicators**: `clinical_indicators.py` tracks sustained sadness, anxiety escalation, emotional volatility, social withdrawal, and negative self-perception.
- **Weighted Emotional Risk Index**: `compute_emotional_risk()` combines emotion probabilities, distress keywords, clinical indicators, and historical trends.
- **Optional API + Docker**: `api_service.py` and `Dockerfile` support scalable integration and deployment.
- Full research motivation, architecture, reproducibility, and paper framing are documented in `RESEARCH_REPRODUCIBILITY_GUIDE.md`.
- IEEE/Scopus reviewer-focused manuscript rewrite guidance is provided in `IEEE_REVIEW_REVISION_GUIDE.md`.

### 📊 Emotion Model Evaluation

The system includes a complete evaluation pipeline for benchmarking the transformer-based emotion classifier against the [GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions) dataset.

**Run a benchmark:**

```bash
# Dry-run with synthetic data (no dataset file needed)
python run_emotion_benchmark.py --dry-run

# Benchmark on a real GoEmotions dataset
python run_emotion_benchmark.py --dataset path/to/goemotions.jsonl

# Export per-sample results to CSV
python run_emotion_benchmark.py --dataset data.jsonl --export-results results/session_emotion_analysis.csv
```

**Example benchmark results (GoEmotions):**

| Metric    | Score |
|-----------|-------|
| Accuracy  | 0.82  |
| Macro F1  | 0.79  |
| Precision | 0.80  |
| Recall    | 0.79  |

**Evaluation methodology:**
- The GoEmotions 28-class label set is mapped to the 6 system emotion classes (joy, sadness, anger, fear, anxiety, neutral) via `datasets/goemotions_loader.py`.
- `evaluation/emotion_model_evaluation.py` computes per-class and macro-averaged precision, recall, and F1 using the same metric code as `research_evaluation.py`.
- Results, including confusion matrices, are saved to `results/` and `plots/`.

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

3. Download required corpora (first time only):
```bash
python -m textblob.download_corpora
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

**Alternatively, run the one-shot setup script which handles everything above automatically:**
```bash
python setup_env.py
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
3. **Share Your Feelings**: Type messages describing how you're feeling — get warm, emotion-specific responses
4. **Receive Support**: Get empathetic responses personalised to your emotional state and personal history
5. **Access Resources**: Type `help` to see support hotlines and your trusted contacts
6. **Track Patterns**: Type `status` to view current session risk level, stability index, emotion distribution, and 7-day history
7. **Weekly Summary**: Type `weekly` (or `report`) to get a 7-day emotion report with AI forecast and improvement suggestions
8. **Manage Profile**: Type `profile` to update personal history, response style, trusted contacts, and settings
9. **End Session**: Type `quit` to safely end and save your session (streak and badges updated automatically)

### Commands
- `help` — Display support resources, hotlines, and your trusted contacts
- `status` — Show emotional pattern summary with risk level, stability index, and emotion distribution
- `weekly` / `report` — Generate a 7-day wellness report with forecast and suggestions
- `profile` — Manage personal history, response style, trusted contacts, security, and delete data
- `quit` — End the session and save your progress

## 🔒 Privacy & Security

### Enhanced Security Features
- **Password Protection**: Set a password to protect your profile from unauthorized access
- **Fernet (AES-128-CBC + HMAC-SHA256) Encryption**: All data encrypted at rest with industry-standard encryption
- **Session Timeout**: Automatic logout after 30 minutes of inactivity
- **Account Lockout**: Protection against brute force password attempts
- **Secure Storage**: Encryption keys and data files with restricted permissions (owner-only)

### Data Privacy
- **Local Storage Only**: All data is stored privately on your device in `~/.wellness_buddy/`
- **No External Sharing**: Your conversations and profile are never shared externally
- **Full User Control**: Delete your data anytime via the profile menu
- **Encrypted Files**: Data files use JSON format with optional Fernet (AES-128-CBC + HMAC-SHA256) encryption
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
The system builds a private profile for each user and continuously understands their emotional history through daily conversations. It tracks personal context — trauma history, personal triggers, marital status, family background, language preference — so every response is warm, sensitive, and tailored to the individual.

### Bilingual Tamil/English Support
Every message is first checked for script: Tamil Unicode characters trigger Tamil-specific keyword dicts; Tanglish (Roman-script Tamil) is identified via a Tanglish keyword library. Responses are generated in the user's chosen language — English, Tamil (தமிழ்), or Bilingual (Tamil + English). Voice input (STT) and text-to-speech (TTS) are language-aware.

### Multi-Emotion Analysis
The system uses TextBlob for sentiment analysis combined with keyword detection to:
- Classify one of **6 fine-grained emotions**: joy, sadness, anger, fear, anxiety, or crisis
- Detect **15+ crisis keywords** for immediate escalation to 988/911
- Detect **24+ distress keywords** and **16+ abuse indicators**
- Provide **XAI attribution** — show exactly which keywords drove the classification
- Fall back to polarity-based classification when no keywords match

### Pattern Tracking & Risk Scoring
- **Session-level**: Rolling window of recent emotional states within the current session
- **Moving average**: 3-message sliding average smooths out noise
- **Volatility & stability index**: Measures how consistent mood is (0 = volatile, 1 = stable)
- **Formula-based risk score**: `base(emotion weights) + consecutive_factor + abuse_boost` → Low / Medium / High / Critical
- **365-day history**: Tracks emotional snapshots for long-term trend analysis

### Emotion Forecasting
- **OLS linear regression** on historical sentiment values predicts the next session's mood
- **Risk escalation prediction**: Forecasts whether risk is trending upward
- Confidence level grows with more data points (low/medium/high)
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
├── wellness_buddy.py       # Main application / orchestrator (CLI)
├── emotion_analyzer.py     # Multi-emotion analysis, crisis detection, XAI
├── pattern_tracker.py      # Pattern tracking, risk scoring, volatility, stability
├── prediction_agent.py     # OLS emotion & risk forecasting
├── alert_system.py         # Distress alert management with safety features
├── conversation_handler.py # Emotion-routed, style-aware response generation
├── user_profile.py         # Profile, personal history, gamification, badges
├── data_store.py           # Persistent encrypted data storage
├── language_handler.py     # Bilingual Tamil/English/Tanglish support
├── voice_handler.py        # TTS (gTTS) + STT (SpeechRecognition)
├── config.py               # Configuration settings
├── ui_app.py               # Streamlit web interface (4-tab: Chat/Trends/Risk/Report)
├── start_ui.sh             # Local UI launcher script
├── start_ui_network.sh     # Network UI launcher script
├── .streamlit/
│   └── config.toml         # Streamlit network configuration
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── USAGE.md                # Quick start guide
├── UI_GUIDE.md             # Web UI guide
├── NETWORK_DEPLOYMENT.md   # Network deployment guide
├── SECURITY.md             # Security features guide
├── DATA_RETENTION.md       # Data tracking and retention guide
├── OPERATION_GUIDE.md      # Full operational guide
├── COMPLETE_FEATURE_GUIDE.md  # Complete feature documentation
└── TECHNOLOGIES_AND_DATASETS.md  # Technologies and datasets documentation
```

## 🛠️ Technologies & Datasets

**For a complete overview of all technologies, libraries, frameworks, and datasets used in this project, see [TECHNOLOGIES_AND_DATASETS.md](TECHNOLOGIES_AND_DATASETS.md).**

### Quick Summary
- **NLP Libraries**: NLTK (>=3.8.1), TextBlob (>=0.17.1)
- **Web Framework**: Streamlit (>=1.28.0)
- **Security**: cryptography (>=41.0.0) for AES-256 encryption
- **Voice/TTS**: gTTS (>=2.5.4) for text-to-speech, SpeechRecognition (>=3.14.5) for voice input
- **Language Detection**: langdetect (>=1.0.9), audio-recorder-streamlit (>=0.0.10)
- **NLTK Datasets**: Brown Corpus, Punkt Tokenizer Models
- **Storage**: Local JSON files (`~/.wellness_buddy/`) with optional encryption
- **Privacy**: All processing done locally, no external APIs (TTS/STT use Google APIs with internet)

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
- `SUPPORTED_LANGUAGES`: Supported response languages (english/tamil/bilingual)
- `DEFAULT_LANGUAGE`: Default language for responses ('english')
- `TTS_ENABLED`: Enable/disable text-to-speech responses (True)
- `STT_ENABLED`: Enable/disable voice input transcription (True)

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

---

## 🚀 Production Web Application (v2.0)

The project includes a production-grade full-stack web application alongside the original CLI/Streamlit tools.

---

## 🔐 Authentication Design (Production-Grade)

The web application uses **HttpOnly cookie-based JWT authentication** routed through a **same-origin Next.js proxy**. This design eliminates the two most common web security vulnerabilities: XSS token theft and CORS misconfiguration.

### How It Works

```
Browser (Next.js on Vercel)
    │  All requests go to /api/* — same origin, no CORS
    ▼
Next.js Server-Side Proxy  (next.config.js rewrites)
    │  /api/:path*  →  BACKEND_URL/api/:path*
    │  Forwards cookies transparently
    ▼
FastAPI Backend (Render)
    │  POST /api/v1/auth/login → sets HttpOnly wb_access_token cookie
    │  GET  /api/v1/auth/me   → validates cookie, returns user
    ▼
PostgreSQL (Render managed DB)
```

### Security Properties

| Property | Implementation |
|---|---|
| Token storage | HttpOnly cookie — **never** in `localStorage` or JavaScript |
| XSS protection | `HttpOnly` flag makes the token inaccessible to scripts |
| CORS prevention | Same-origin proxy — browser never makes cross-origin requests |
| Cookie scope | `SameSite=Lax`, `Path=/`, `Secure` (auto-set on HTTPS) |
| Token lifetime | `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 min) |
| CSRF | `SameSite=Lax` blocks cross-site form submissions |
| Session flag | Non-HttpOnly `wb_logged_in` cookie used only as a UI presence flag |

### Why Not `localStorage`?

`localStorage` is accessible from any JavaScript on the page, making tokens trivially stealable via XSS. HttpOnly cookies cannot be read by JavaScript at all — the browser sends them automatically on every credentialed request.

### Why Same-Origin Proxy Instead of Direct Backend Calls?

Direct calls from `http://localhost:3000` to `http://localhost:8000` are cross-origin. Browsers enforce CORS restrictions on cross-origin requests, and `SameSite=Lax` cookies are not sent cross-origin by default. The Next.js proxy forwards requests server-side, keeping the browser on a single origin throughout.

---

## 🏗️ Web App Architecture

```
browser
    │  HTTPS  →  https://your-app.vercel.app/api/*  (same origin)
    ▼
Next.js (Vercel)                         [frontend/]
    │  next.config.js rewrites
    │  /api/:path*  →  BACKEND_URL/api/:path*
    ▼
FastAPI (Render)                         [backend/]
    ├── /health                          liveness probe
    ├── /api/v1/auth/*                   signup · login · logout · me · debug
    ├── /api/v1/predict                  emotion analysis (public)
    ├── /api/v1/chat                     AI chat (authenticated)
    ├── /api/v1/chat/history             chat history, ASC order (authenticated)
    ├── /api/v1/dashboard                emotion trend + risk alerts
    ├── /api/v1/weekly-report            7-day summary
    ├── /api/v1/journey                  longitudinal journey view
    ├── /api/v1/insights                 personalization insights
    ├── /api/v1/analytics/research       IEEE-grade metrics endpoint
    ├── /api/v1/voice/transcribe         STT (SpeechRecognition + ffmpeg)
    ├── /api/v1/voice/tts                TTS (gTTS)
    └── /api/v1/guardian-alert           guardian notification system
    │
    ▼
PostgreSQL (Render managed)              [SQLite for local dev]
    Tables: users · chat_history · emotion_logs · user_profiles · guardian_alerts
```

### Repository Structure

```
backend/
├── app/
│   ├── main.py           # App factory, CORS, lifespan, model pre-warm
│   ├── config.py         # Pydantic-settings (.env support)
│   ├── database.py       # Async SQLAlchemy engine (PostgreSQL + SQLite)
│   ├── models/           # User, ChatHistory, EmotionLog, UserProfile ORM models
│   ├── schemas/          # Pydantic v2 request/response schemas
│   ├── routers/          # auth, chat, predict, dashboard, analytics, voice, …
│   ├── services/         # auth_service, emotion_service, chat_service, …
│   └── middleware/       # RequestLoggingMiddleware, SecurityHeadersMiddleware
├── tests/                # 117 pytest-asyncio tests (unit + integration + E2E)
├── alembic/              # Database migrations
├── requirements.txt
├── .env.example
└── pytest.ini

frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/login      # Login page
│   │   ├── (auth)/signup     # Signup page
│   │   ├── (app)/chat        # Main chat interface
│   │   ├── (app)/dashboard   # Emotion trend dashboard
│   │   ├── (app)/journey     # Longitudinal journey view
│   │   └── (app)/weekly-report
│   ├── components/
│   │   ├── chat/             # ChatBubble, TypingIndicator, VoiceInput
│   │   ├── emotion/          # EmotionBadge, ConfidenceBar
│   │   └── ui/               # Button, Input, GlassCard
│   └── lib/
│       ├── api.ts            # Typed API client (axios, withCredentials=true)
│       └── auth.ts           # loginUser, signupUser, logoutUser, isAuthenticated
├── tests/e2e/                # Playwright end-to-end tests
├── next.config.js            # Proxy rewrite: /api/* → BACKEND_URL/api/*
├── vercel.json               # Vercel deployment config
└── playwright.config.ts

Dockerfile.backend            # Multi-stage production image
docker-compose.yml            # Full-stack local dev (backend + frontend)
render.yaml                   # Render Blueprint (backend + PostgreSQL)
```

---

## 🛠️ API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/health` | No | Liveness probe |
| `POST` | `/api/v1/auth/signup` | No | Register — sets HttpOnly cookie |
| `POST` | `/api/v1/auth/login` | No | Authenticate — sets HttpOnly cookie |
| `POST` | `/api/v1/auth/logout` | No | Clear auth cookie |
| `GET`  | `/api/v1/auth/me` | Cookie | Current user profile |
| `GET`  | `/api/v1/auth/debug` | No | Cookie presence flags (debugging) |
| `POST` | `/api/v1/predict` | Optional | Emotion detection (public) |
| `POST` | `/api/v1/chat` | Cookie | Send message, get AI reply |
| `GET`  | `/api/v1/chat/history` | Cookie | Retrieve history (ASC order) |
| `GET`  | `/api/v1/dashboard` | Cookie | Emotion trend + risk alerts |
| `GET`  | `/api/v1/weekly-report` | Cookie | 7-day wellness summary |
| `GET`  | `/api/v1/journey` | Cookie | Longitudinal journey + CDI |
| `GET`  | `/api/v1/insights` | Cookie | Personalization insights |
| `GET`  | `/api/v1/analytics/research` | Cookie | IEEE-grade research metrics |
| `POST` | `/api/v1/voice/transcribe` | Cookie | Speech-to-text |
| `POST` | `/api/v1/voice/tts` | Cookie | Text-to-speech |
| `POST` | `/api/v1/guardian-alert` | Cookie | Trigger guardian notification |
| `GET`  | `/api/v1/guardian-alert` | Cookie | List alert history |
| `GET`  | `/metrics` | No | Prometheus metrics |

> All protected endpoints accept the `wb_access_token` HttpOnly cookie **or** an `Authorization: Bearer <token>` header (for API clients and tests).

---

## ⚡ Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### 1. Backend

```bash
cd backend
cp .env.example .env
# ↳ Set SECRET_KEY (required): python -c "import secrets; print(secrets.token_hex(32))"
# ↳ Leave DATABASE_URL as default for SQLite in local dev

pip install -r requirements.txt
uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local
# ↳ .env.example already sets BACKEND_URL=http://localhost:8000
# ↳ No changes needed for local dev

npm install
npm run dev
# App: http://localhost:3000
```

### Docker Compose (Full Stack)

```bash
cp backend/.env.example backend/.env    # set SECRET_KEY
docker compose up --build
# Frontend: http://localhost:3000
# Backend docs: http://localhost:8000/docs
```

---

## 🧪 Testing

### Backend (117 tests)

```bash
cd backend
pytest tests/ -v
# Covers: auth signup/login/logout, cookie presence, /auth/me via cookie,
#         chat ordering (created_at ASC), analytics, crisis dispatch,
#         guardian alerts, DB outage handling
```

### Frontend E2E (Playwright)

```bash
cd frontend
npx playwright test
# Covers: login/signup flow, redirect, cookie flag, invalid login toast,
#         chat message ordering, history from backend, scroll restoration
```

---

## 🌐 Deployment

### Backend — Render

The `render.yaml` Blueprint configures a Docker web service + managed PostgreSQL automatically.

1. Connect the repository to [render.com](https://render.com) as a **Blueprint**.
2. Set these secrets in the Render dashboard (never stored in Git):

   | Secret | Value |
   |---|---|
   | `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `ALLOWED_ORIGINS` | `["https://your-app.vercel.app"]` |
   | `FRONTEND_URL` | `https://your-app.vercel.app` |

3. `DATABASE_URL` is auto-populated from the Render PostgreSQL add-on.

### Frontend — Vercel

1. Import the repository into [vercel.com](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Set the environment variable:

   | Variable | Value |
   |---|---|
   | `BACKEND_URL` | `https://your-backend.onrender.com` |

4. Deploy. The `next.config.js` rewrite proxies `/api/*` to the Render backend automatically.

> **Important**: `BACKEND_URL` is a **server-side** variable used by Next.js rewrites. It is not `NEXT_PUBLIC_*` and is never exposed to the browser.

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | JWT signing secret |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./wellness.db` | Async DB URL |
| `ENV` | No | `development` | Set `production` on Render |
| `ALLOWED_ORIGINS` | No | `["http://localhost:3000"]` | CORS origins (JSON array) |
| `FRONTEND_URL` | No | `""` | Additional CORS origin |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | JWT lifetime |
| `CRISIS_CONFIDENCE_THRESHOLD` | No | `0.6` | High-risk trigger level |
| `LOG_LEVEL` | No | `INFO` | `DEBUG` for cookie diagnostics |
| `RATELIMIT_ENABLED` | No | `true` | Disable in tests |
| `SMTP_HOST` / `SMTP_*` | No | `""` | Email guardian alerts |
| `TWILIO_*` | No | `""` | WhatsApp guardian alerts |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `BACKEND_URL` | No | `http://localhost:8000` | Backend URL for Next.js proxy |

---

## 🗄️ Database Schema

```sql
-- users
id · email (unique) · username (unique) · hashed_password · is_active · created_at · updated_at

-- chat_history
id · user_id (FK) · session_id · role ('user'|'assistant') · content · emotion · created_at

-- emotion_logs
id · user_id (FK) · input_text · primary_emotion · confidence · uncertainty
   · is_high_risk · all_scores (JSON) · risk_score · personalization_score · created_at

-- user_profiles
id · user_id (FK) · age · gender · occupation · stress_level · sleep_pattern
   · triggers (JSON) · personality_type · trauma_history (JSON) · language_preference
   · enable_guardian_alerts · guardian_email · guardian_whatsapp · …

-- guardian_alerts
id · user_id (FK) · risk_level · risk_reason · channel · delivery_status
   · is_test · timestamp
```

---

## 🤖 AI/ML Pipeline

```
User text input
    │
    ▼
EmotionAnalyzer
    (j-hartmann/emotion-english-distilroberta-base, HuggingFace)
    → primary_emotion · confidence · uncertainty · all_scores
    │
    ▼
Risk Classifier
    → is_high_risk · risk_score · escalation_message
    (threshold: confidence ≥ 0.6 for crisis class)
    │
    ▼
WellnessAgentPipeline
    → empathetic reply (template + pattern-based)
    → personalized from UserProfile (triggers, language, tone)
    │
    ▼
Stored in chat_history (ORDER BY created_at ASC)
Stored in emotion_logs (risk_score, personalization_score)
```

**Model pre-warming**: Both the EmotionAnalyzer and WellnessAgentPipeline are pre-warmed at server startup, eliminating cold-start latency (~16s) on the first request.

---

## 🗒️ Legacy CLI / Streamlit Application

The original research prototype (CLI + Streamlit UI) is preserved in the repository root:

```bash
# CLI
python wellness_buddy.py

# Streamlit web UI
streamlit run ui_app.py

# Install root-level dependencies
pip install -r requirements.txt
```

See `QUICK_START_GUIDE.md`, `UI_GUIDE.md`, and `OPERATION_GUIDE.md` for the legacy system.
