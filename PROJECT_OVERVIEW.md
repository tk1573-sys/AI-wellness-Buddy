# AI Wellness Buddy - Project Overview

## What This Project Does

### Executive Summary

The **AI Wellness Buddy** is an intelligent emotional support system that uses natural language processing (NLP) and machine learning to provide continuous mental health monitoring, crisis detection, and support resource connections. The system is specifically designed with enhanced safety features for women in vulnerable situations and includes guardian notification capabilities for emergency support.

---

## Core Functionality

### 1. Emotional Wellbeing Monitoring

**What it does:**
- Analyzes conversations to understand emotional state
- Classifies one of **6 fine-grained emotions**: joy, sadness, anger, fear, anxiety, crisis
- Detects crisis keywords for immediate 988/911 escalation
- Provides XAI attribution — explains *why* an emotion was classified
- Monitors patterns across days, weeks, and months

**How it works:**
- Uses TextBlob for sentiment analysis (-1 to +1 scale)
- NLTK Brown Corpus for language understanding
- Per-emotion keyword dictionaries (joy: 21 keywords, sadness: 21, anger: 16, fear: 14, anxiety: 18, crisis: 15+)
- 24+ distress keywords, 16+ abuse keywords
- Pattern tracking over 365-day rolling window

**Example:**
```
User: "I'm feeling really anxious and overwhelmed"
Analysis:
  - Sentiment: -0.35 (moderate negative)
  - Primary emotion: anxiety
  - XAI: "Detected 'anxiety' due to keywords: anxious, overwhelmed"
  - Risk level: Medium (score: 0.38)
  - Stability index: 0.82
```

### 2. Crisis Detection & Alerts

**What it does:**
- Detects 15+ crisis keywords (self-harm, suicidal ideation) with immediate escalation
- Detects sustained emotional distress (3+ consecutive messages)
- Computes formula-based risk score: Low / Medium / High / Critical
- Provides immediate crisis resources
- Forecasts risk escalation with OLS regression

**How it works:**
- Crisis keywords bypass all other logic and trigger immediate 988/911 response
- Risk score formula: `base(emotion weights) + consecutive_factor + abuse_boost`
- OLS prediction on historical sentiment values for next-session forecast
- Configurable thresholds for guardian notifications

**Example:**
```
After 4 consecutive distress messages (High risk):
⚠️ EMOTIONAL DISTRESS ALERT ⚠️
Risk level: HIGH (score: 0.66)
Resources provided:
  • Crisis Hotline: 988
  • Text Line: 741741
  • Emergency: 911
  • Guardian notification offered
```

### 3. Guardian/Emergency Contact System

**What it does:**
- Notifies designated guardians during severe distress
- Configurable notification thresholds
- Privacy-respecting (asks before notifying)
- Formatted notifications with actionable information

**How it works:**
```python
1. User configures guardian contacts
2. System monitors distress severity
3. When threshold reached:
   - Ask user permission (if AUTO_NOTIFY = False)
   - Send formatted notification to guardians
   - Log notification for user review
4. Guardian receives:
   - Alert type and severity
   - What to do
   - Professional resources
```

**Guardian receives:**
```
🚨 WELLNESS ALERT FOR [User] 🚨

Sustained emotional distress detected.
Indicators: 5 consecutive distress messages

What you can do:
  • Reach out with care
  • Listen without judgment
  • Connect to professional help

Resources: 988, 911, 741741
```

### 4. Specialized Women's Support

**What it does:**
- Detects abuse indicators in conversations
- Provides expanded resources for women
- Includes government agencies and legal aid
- Supports non-family support networks

**Abuse Detection:**
Monitors 16 keywords:
- Emotional: gaslighting, manipulative, controlling
- Physical: abuse, threatened, intimidated
- Isolation: trapped, isolated, toxic relationship

**Resources Provided:**
- **Domestic Violence**: 1-800-799-7233
- **Government Agencies**: Women's Health, Violence Against Women Office
- **Legal Aid**: National Women's Law Center, Legal Services
- **Mental Health**: Women-specific crisis lines

**Safe Support Network:**
For women who can't rely on family:
- Mark family as unsafe
- Add trusted friends only
- Connects to women's organizations
- Professional shelter and counseling resources

### 5. Long-Term Pattern Tracking

**What it does:**
- Stores 365 days of emotional history (extended from 90)
- Analyzes trends over weeks, months, seasons
- Identifies improvement or decline
- Tracks progress from milestones

**Patterns Detected:**
- **Weekly**: Best/worst days, consistency
- **Monthly**: Month-over-month comparison
- **Seasonal**: Winter blues, summer highs
- **Annual**: Full year journey

**Example Output:**
```
📊 Last 30 Days Analysis:
  Check-ins: 22
  Average sentiment: +0.15
  Trend: Improving ✨
  
  Best week: Week of Feb 15 (+0.45)
  Most challenging: Week of Feb 1 (-0.10)
```

### 6. Multi-Interface Access

**What it offers:**

**CLI (Command Line):**
- Fast, lightweight
- Works anywhere
- Terminal-based interaction
- Perfect for quick check-ins

**Web UI (Browser):**
- Visual interface
- Point-and-click navigation
- Charts and graphs
- User-friendly for daily use

**Network UI:**
- Access from any device
- Phone, tablet, laptop support
- Same Wi-Fi connection
- Mobile-friendly design

### 7. Security & Privacy

**What it provides:**

**Data Security:**
- AES-256 encryption at rest
- SHA-256 password hashing
- Unique salt per user
- Owner-only file permissions (600)

**Session Security:**
- 30-minute timeout
- Account lockout (3 failed attempts)
- Secure password requirements (8+ chars)

**Privacy:**
- All data stored locally
- No external API calls
- No cloud storage
- User controls all data
- Can delete anytime

---

## Technical Architecture

### Components

```
┌─────────────────────────────────────────────────┐
│                 User Interfaces                  │
│  CLI  |  Web UI (4-tab)  |  Network UI          │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Core Processing Layer                 │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ WellnessBuddy (Orchestrator)               │ │
│  │  - Session management, commands, weekly    │ │
│  └──┬─────────────────────────────────────────┘ │
│     │                                            │
│  ┌──▼──────────────┐  ┌──────────────────────┐ │
│  │ EmotionAnalyzer │  │  PatternTracker       │ │
│  │  - 6 emotions   │  │  - Moving average     │ │
│  │  - Crisis det.  │  │  - Volatility/Stab.   │ │
│  │  - XAI attrib.  │  │  - Risk scoring       │ │
│  └──┬──────────────┘  └────────┬─────────────┘ │
│     │                           │                │
│  ┌──▼───────────────────────────▼─────────────┐ │
│  │  ConversationHandler                        │ │
│  │  - 6-emotion × 3-style response templates  │ │
│  │  - Trauma / trigger / marital awareness     │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌──────────────────┐  ┌───────────────────────┐ │
│  │  PredictionAgent │  │  AlertSystem           │ │
│  │  - OLS forecast  │  │  - Distress detection  │ │
│  │  - Risk escalat. │  │  - Guardian notify     │ │
│  └──────────────────┘  └───────────────────────┘ │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│                  Data Layer                      │
│  ┌────────────────────┐  ┌──────────────────┐   │
│  │  UserProfile        │  │  DataStore       │   │
│  │  - Personal history │  │  - Encryption    │   │
│  │  - Gamification     │  │  - Backups       │   │
│  │  - Response style   │  │  - Integrity     │   │
│  └────────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Data Flow

```
1. User Input
   ↓
2. Multi-Emotion Analysis (TextBlob + NLTK + keyword dicts)
   → primary_emotion + XAI explanation + is_crisis flag
   ↓
3. Pattern Tracking
   → risk score (Low/Medium/High/Critical)
   → volatility + stability index
   → moving average + emotion distribution
   ↓
4. Alert Evaluation
   → sustained distress → distress alert
   → crisis keywords → immediate 988/911 response
   ↓
5. Response Generation (ConversationHandler)
   → emotion × style template
   → personalised for trauma/triggers/marital status
   → XAI annotation appended
   ↓
6. Resource Provision (if needed)
   ↓
7. Guardian Notification (if threshold met)
   ↓
8. Prediction (OLS) surfaced in status / weekly / UI tabs
   ↓
9. Data Storage (encrypted) + streak/badge update at session end
```

---

## Key Features Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Multi-Emotion Analysis** | 6 fine-grained emotions + crisis | Nuanced understanding |
| **XAI Attribution** | Keyword-driven explanation | Transparent AI |
| **Risk Scoring** | Formula-based Low/Medium/High/Critical | Intelligent, not threshold-based |
| **Stability Index** | Volatility + stability (0–1) | Mood consistency insight |
| **OLS Forecasting** | Next-session mood & risk prediction | Proactive support |
| **Personal History** | Trauma, triggers, marital status | Truly personalised responses |
| **Response Styles** | Short / Balanced / Detailed | User preference |
| **Gamification** | Streak + 8 badges | Engagement & motivation |
| **Weekly Report** | 7-day summary + suggestions | Self-awareness |
| **365-Day Tracking** | Full year of history | Long-term pattern insights |
| **Crisis Detection** | 15+ crisis keywords → 988/911 | Timely intervention |
| **Guardian Alerts** | Emergency contact notification | External support layer |
| **Women's Safety** | Abuse detection + resources | Specialised support |
| **Government Resources** | 15+ official agencies | Trusted help channels |
| **Encryption** | AES-256 data encryption | Privacy protection |
| **4-Tab Web UI** | Chat/Trends/Risk/Report | Health analytics dashboard |

---

## Use Cases

### 1. Daily Mental Health Monitoring

**Scenario:** Individual wants to track mental health

**Usage:**
- Daily 5-minute check-ins
- Express feelings in conversation
- Review weekly patterns
- Identify triggers and improvements

**Outcome:**
- Better self-awareness
- Early detection of decline
- Documented progress
- Professional help when needed

### 2. Crisis Support & Resource Connection

**Scenario:** User experiencing severe distress

**Usage:**
- Express crisis feelings
- System detects severity
- Immediate resources provided
- Guardian notified if configured

**Outcome:**
- Immediate crisis resources
- Connection to help (988, 911)
- Support from guardians
- Documentation for professional care

### 3. Women's Safety & Support

**Scenario:** Woman in abusive relationship

**Usage:**
- Private device, secure location
- Express concerns safely
- System detects abuse indicators
- Receives specialized resources

**Outcome:**
- Access to DV hotlines
- Government agency connections
- Legal aid information
- Safety planning resources
- Non-family support network

### 4. Therapeutic Progress Tracking

**Scenario:** Person in therapy wants to track progress

**Usage:**
- Daily emotional journaling
- Track mood patterns
- Review improvement over time
- Share data with therapist

**Outcome:**
- Objective progress data
- Identify effective strategies
- Therapist has better insights
- Motivated by visible progress

### 5. Guardian/Caregiver Monitoring

**Scenario:** Elderly parent with depression, adult child as guardian

**Usage:**
- Parent uses daily for check-ins
- Guardian gets alerts for severe distress
- Professional resources provided
- Family stays informed

**Outcome:**
- Early intervention possible
- Guardian peace of mind
- Professional help accessed quickly
- Documented emotional health

---

## Technology Stack

### Core Technologies

**Programming Language:**
- Python 3.7+

**NLP & Machine Learning:**
- NLTK 3.8.1+ (Natural Language Toolkit)
  - Brown Corpus (1M+ words)
  - Punkt tokenizer
- TextBlob 0.17.1+ (Sentiment analysis)
  - Polarity: -1 to +1
  - Subjectivity: 0 to 1

**Web Framework:**
- Streamlit 1.28.0+ (Web UI)
  - Real-time updates
  - Interactive components
  - Network accessibility

**Security:**
- cryptography 41.0.0+ (AES-256 encryption)
  - Fernet symmetric encryption
  - Secure key generation

**Utilities:**
- python-dateutil 2.8.2+ (Date handling)
- hashlib (SHA-256 hashing)
- secrets (Secure random generation)

### Data Storage

**Format:** JSON (human-readable, portable)
**Encryption:** AES-256 in CBC mode
**Location:** Local filesystem (`~/.wellness_buddy/`)
**Backup:** Automatic timestamped backups

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.7+
- **RAM**: 2GB
- **Storage**: 100MB application + ~2MB per user per year
- **Network**: Internet for initial setup only

### Recommended Setup
- **OS**: Latest Windows 11, macOS 13+, Ubuntu 22.04+
- **Python**: 3.9+
- **RAM**: 4GB
- **Storage**: 500MB free
- **Network**: Wi-Fi for network UI access

---

## Innovation & Unique Features

### What Makes This Project Special

1. **Multi-Emotion AI with XAI**
   - 6 fine-grained emotions (not just positive/negative)
   - Crisis keyword detection with immediate escalation
   - XAI attribution — shows which words drove classification
   - Formula-based risk scoring (not simple threshold)

2. **Emotion Forecasting**
   - OLS linear regression on historical sentiment
   - Next-session mood prediction with confidence level
   - Risk escalation forecast
   - No external ML dependencies

3. **Personal History & Deep Personalization**
   - Trauma history stored for extra-sensitive responses
   - Personal triggers for gentle acknowledgement
   - Marital/relationship context for life-transition empathy
   - Response style preference (short/balanced/detailed)

4. **Gamified Mental Wellness Tracking**
   - Mood streak (consecutive positive sessions)
   - 8 wellness badge types
   - Weekly summary report with OLS forecast

5. **Women-Specific Safety Features**
   - Abuse detection algorithms
   - Non-family support networks
   - Government resource integration
   - Legal aid connections

6. **Guardian Alert System**
   - Configurable thresholds
   - Privacy-respecting notifications
   - Actionable information for guardians
   - Multi-level severity

7. **Extended Tracking (365 Days)**
   - 4x longer than typical apps
   - Seasonal pattern detection
   - Long-term progress visualization

8. **Complete Privacy**
   - Local storage only
   - No cloud, no external APIs
   - Full user control
   - Military-grade encryption

9. **Multi-Layer Security**
   - Password protection
   - Session timeouts
   - Account lockout
   - Data integrity checks
   - Automatic backups

10. **Multi-Interface Flexibility**
    - CLI for quick access
    - Web UI (4-tab analytics dashboard) for daily use
    - Network UI for mobile devices
    - Same data across all interfaces

---

## Project Metrics

### Code Metrics
- **Total Lines of Code**: 6,000+
- **Python Modules**: 8 core modules (emotion_analyzer, pattern_tracker, prediction_agent, conversation_handler, alert_system, user_profile, data_store, wellness_buddy)
- **Documentation**: 100KB+ (comprehensive)
- **Test Coverage**: 14 automated tests

### Feature Metrics
- **Emotion Classes**: 6 fine-grained (joy/sadness/anger/fear/anxiety/crisis)
- **Emotion Keywords**: 90+ (per-emotion dictionaries + crisis + distress + abuse)
- **Response Templates**: 6 emotions × 3 styles = 18 template sets
- **Wellness Badges**: 8 badge types
- **Support Resources**: 30+ hotlines/organizations
- **Government Agencies**: 15+ women-specific
- **Retention Period**: 365 days
- **Security Layers**: 7 distinct features

### Usage Metrics (Designed For)
- **Daily Sessions**: 5-15 minutes
- **Storage Per Year**: ~2MB per user
- **Response Time**: < 1 second
- **Uptime**: 24/7 local availability

---

## Impact & Benefits

### For Individual Users
- ✅ Better emotional self-awareness
- ✅ Early crisis detection
- ✅ Immediate resource access
- ✅ Long-term progress tracking
- ✅ Safe, private space for expression

### For Women in Crisis
- ✅ Specialized support resources
- ✅ Government agency connections
- ✅ Legal aid access
- ✅ Non-family support networks
- ✅ Safety planning resources

### For Guardians/Families
- ✅ Early warning system
- ✅ Professional resource guidance
- ✅ Actionable information
- ✅ Peace of mind
- ✅ Timely intervention capability

### For Mental Health Professionals
- ✅ Objective progress data
- ✅ Pattern visualization
- ✅ Client self-monitoring tool
- ✅ Crisis early detection
- ✅ Treatment effectiveness tracking

---

## Future Enhancements (Roadmap)

### Planned Features
1. **Mobile Apps** (iOS/Android native)
2. **Voice Interface** (speech-to-text + tone analysis)
3. **Multilingual Support** (Spanish, French, etc.)
4. **Transformer-Based Emotion Model** (fine-tuned BERT/RoBERTa)
5. **Wearable Integration** (heart rate, sleep data)
6. **Group Support** (anonymous peer support)
7. **Professional Dashboard** (for therapists)
8. **SMS/Email Alerts** (guardian notifications)

### Already Implemented (From Roadmap)
✅ **Multi-Emotion Classification** — 6 fine-grained emotions  
✅ **Predictive Analytics** — OLS next-session and risk escalation forecast  
✅ **Personalization** — personal history, response styles, gamification  
✅ **XAI / Explainability** — keyword attribution in every response  
✅ **Advanced Visualization** — 4-tab analytics dashboard  

### Research Directions
1. **Transformer Models** (BERT/RoBERTa for emotion classification)
2. **Reinforcement Learning** (adaptive response optimization)
3. **Multimodal Input** (voice + text)
4. **EHR Integration** (clinical use cases)

---

## Conclusion

The AI Wellness Buddy is a comprehensive emotional support system that combines:
- **Multi-emotion AI** with 6 fine-grained emotion classes and XAI attribution
- **Formula-based risk scoring** (Low/Medium/High/Critical)
- **OLS forecasting** for next-session mood and risk escalation prediction
- **Personal history awareness** — trauma, triggers, marital status, family background
- **Gamification** — mood streak, 8 wellness badges, weekly summary reports
- Long-term pattern tracking (365 days)
- Multi-level crisis detection and guardian notification system
- Specialized women's safety features and government resources
- Military-grade security and complete privacy

It serves as a bridge between individuals and professional mental health care, providing:
- Continuous, intelligent monitoring
- Timely crisis intervention
- Warm, humanoid, personalized responses
- Resource connections and safe support networks
- Progress tracking and wellness gamification

**Mission**: Make emotional support accessible, private, and effective for everyone, with specialized features for vulnerable populations.

**Vision**: A world where mental health monitoring is as normal as physical health tracking, and help is always within reach.

---

**This project demonstrates how technology can support mental wellbeing while respecting privacy, empowering users, and connecting them to professional help when needed.** 💙
