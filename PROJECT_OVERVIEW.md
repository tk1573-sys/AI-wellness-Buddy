# AI Wellness Buddy - Project Overview

## What This Project Does

### Executive Summary

The **AI Wellness Buddy** is an intelligent emotional support system that uses natural language processing (NLP) and machine learning to provide continuous mental health monitoring, crisis detection, and support resource connections. The system is specifically designed with enhanced safety features for women in vulnerable situations and includes guardian notification capabilities for emergency support.

---

## Core Functionality

### 1. Emotional Wellbeing Monitoring

**What it does:**
- Analyzes conversations to understand emotional state
- Tracks sentiment over time (positive, neutral, negative)
- Identifies specific emotions (anxious, sad, hopeful, etc.)
- Monitors patterns across days, weeks, and months

**How it works:**
- Uses TextBlob for sentiment analysis (-1 to +1 scale)
- NLTK Brown Corpus for language understanding
- Custom keyword detection for distress and abuse indicators
- Pattern tracking over 365-day rolling window

**Example:**
```
User: "I'm feeling stressed about work"
Analysis:
  - Sentiment: -0.3 (moderate negative)
  - Emotion: anxiety/stress
  - Severity: medium
  - Pattern: First distress message today
```

### 2. Crisis Detection & Alerts

**What it does:**
- Detects sustained emotional distress (3+ consecutive messages)
- Identifies crisis keywords (self-harm, hopelessness, etc.)
- Triggers multi-level alert system
- Provides immediate crisis resources

**How it works:**
- Monitors consecutive distress messages
- Analyzes severity levels (low, medium, high)
- Compares against configurable thresholds
- Triggers appropriate support resources

**Example:**
```
After 3 distress messages:
⚠️ EMOTIONAL DISTRESS ALERT ⚠️
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
┌─────────────────────────────────────────┐
│         User Interfaces                 │
│  (CLI, Web UI, Network UI)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Core Processing Layer              │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ Wellness Buddy (Main Engine)    │  │
│  │  - Session Management           │  │
│  │  - User Interaction             │  │
│  │  - Command Processing           │  │
│  └────────┬────────────────────────┘  │
│           │                            │
│  ┌────────▼────────┐  ┌──────────┐   │
│  │ Emotion Analyzer│  │ Pattern   │   │
│  │  - TextBlob     │  │ Tracker   │   │
│  │  - NLTK        │  │  - Trends │   │
│  │  - Keywords    │  │  - History│   │
│  └────────┬────────┘  └────┬─────┘   │
│           │                 │         │
│  ┌────────▼─────────────────▼──────┐ │
│  │      Alert System               │ │
│  │  - Distress Detection           │ │
│  │  - Guardian Notification        │ │
│  │  - Resource Provision           │ │
│  └────────┬────────────────────────┘ │
└───────────┼──────────────────────────┘
            │
┌───────────▼──────────────────────────┐
│      Data Layer                      │
│                                      │
│  ┌────────────┐  ┌───────────────┐ │
│  │User Profile│  │  Data Store   │ │
│  │ - Security │  │  - Encryption │ │
│  │ - Contacts │  │  - Backups    │ │
│  │ - History  │  │  - Integrity  │ │
│  └────────────┘  └───────────────┘ │
└──────────────────────────────────────┘
```

### Data Flow

```
1. User Input
   ↓
2. Emotion Analysis (TextBlob + NLTK)
   ↓
3. Pattern Tracking (add to history)
   ↓
4. Alert Evaluation
   ↓
5. Response Generation
   ↓
6. Resource Provision (if needed)
   ↓
7. Guardian Notification (if threshold met)
   ↓
8. Data Storage (encrypted)
```

---

## Key Features Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Emotion Analysis** | NLP-based sentiment analysis | Understand emotional state |
| **365-Day Tracking** | Full year of history | Long-term pattern insights |
| **Crisis Detection** | Automatic distress alerts | Timely support provision |
| **Guardian Alerts** | Emergency contact notification | External support layer |
| **Women's Safety** | Abuse detection + resources | Specialized support |
| **Government Resources** | Official agencies | Trusted help channels |
| **Encryption** | AES-256 data encryption | Privacy protection |
| **Multi-Interface** | CLI, Web, Network | Accessibility |
| **Trusted Network** | Non-family contacts | Safe support options |
| **Professional Resources** | Crisis hotlines | 24/7 help access |

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

1. **Women-Specific Safety Features**
   - Abuse detection algorithms
   - Non-family support networks
   - Government resource integration
   - Legal aid connections

2. **Guardian Alert System**
   - Configurable thresholds
   - Privacy-respecting notifications
   - Actionable information for guardians
   - Multi-level severity

3. **Extended Tracking (365 Days)**
   - 4x longer than typical apps
   - Seasonal pattern detection
   - Long-term progress visualization
   - Milestone tracking

4. **Complete Privacy**
   - Local storage only
   - No cloud, no external APIs
   - Full user control
   - Military-grade encryption

5. **Multi-Layer Security**
   - Password protection
   - Session timeouts
   - Account lockout
   - Data integrity checks
   - Automatic backups

6. **Multi-Interface Flexibility**
   - CLI for quick access
   - Web UI for daily use
   - Network UI for mobile devices
   - Same data across all interfaces

---

## Project Metrics

### Code Metrics
- **Total Lines of Code**: ~5,000+
- **Python Modules**: 12 core modules
- **Documentation**: 100KB+ (comprehensive)
- **Test Coverage**: Core functionality tested

### Feature Metrics
- **Support Resources**: 30+ hotlines/organizations
- **Government Agencies**: 15+ women-specific
- **Emotion Keywords**: 40+ tracked
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
2. **Voice Interface** (speech-to-text)
3. **Multilingual Support** (Spanish, French, etc.)
4. **Advanced Analytics** (ML-based predictions)
5. **Wearable Integration** (heart rate, sleep)
6. **Group Support** (anonymous peer support)
7. **Professional Dashboard** (for therapists)
8. **SMS/Email Alerts** (guardian notifications)

### Research Directions
1. **Improved NLP** (transformer models)
2. **Predictive Analytics** (crisis prediction)
3. **Personalization** (adaptive responses)
4. **Integration** (EHR systems)

---

## Conclusion

The AI Wellness Buddy is a comprehensive emotional support system that combines:
- Advanced NLP for emotion understanding
- Long-term pattern tracking (365 days)
- Multi-level crisis detection
- Guardian notification system
- Specialized women's safety features
- Military-grade security
- Complete privacy

It serves as a bridge between individuals and professional mental health care, providing:
- Continuous monitoring
- Timely crisis intervention
- Resource connections
- Safe support networks
- Progress tracking

**Mission**: Make emotional support accessible, private, and effective for everyone, with specialized features for vulnerable populations.

**Vision**: A world where mental health monitoring is as normal as physical health tracking, and help is always within reach.

---

**This project demonstrates how technology can support mental wellbeing while respecting privacy, empowering users, and connecting them to professional help when needed.** 💙
