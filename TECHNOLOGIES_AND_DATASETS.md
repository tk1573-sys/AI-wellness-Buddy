# Technologies and Datasets Used in AI Wellness Buddy

This document provides a comprehensive overview of all technologies, libraries, frameworks, and datasets used in the AI Wellness Buddy project.

## 🛠️ Core Technologies

### Programming Language
- **Python 3.7+**: Core programming language for the entire application

### Python Libraries & Frameworks

#### Natural Language Processing (NLP)
1. **NLTK (Natural Language Toolkit) >= 3.8.1**
   - Purpose: Natural language processing foundation
   - Used for: Text tokenization and language processing
   - Required NLTK Datasets:
     - `brown`: Brown Corpus - a general corpus of English text for training
     - `punkt`: Punkt Tokenizer Models - for sentence tokenization

2. **TextBlob >= 0.17.1**
   - Purpose: Sentiment analysis and text processing
   - Used for: 
     - Sentiment polarity analysis (-1 to 1 scale)
     - Subjectivity analysis (0 to 1 scale)
     - Emotion classification based on text content
   - Built on top of NLTK and Pattern libraries

#### Utility Libraries
3. **python-dateutil >= 2.8.2**
   - Purpose: Date/time parsing and manipulation
   - Used for: Handling timestamps, date arithmetic, and ISO format conversion

#### Web UI Framework
4. **Streamlit >= 1.28.0**
   - Purpose: Web-based user interface
   - Used for: Creating an interactive browser-based UI for the application
   - Features: Real-time chat interface, sidebar navigation, profile management

### Python Standard Libraries
The following standard library modules are used throughout the application:
- **json**: Data serialization and storage
- **os**: Operating system interface for file operations
- **sys**: System-specific parameters and functions
- **pathlib**: Object-oriented filesystem paths
- **datetime**: Date and time manipulation
- **collections** (deque): Efficient queue data structure for pattern tracking
- **random**: Random selection for greeting messages
- **re**: Regular expression operations
- **tempfile**: Temporary file and directory creation
- **shutil**: High-level file operations

## 📊 Datasets

### NLTK Downloaded Datasets

1. **Brown Corpus**
   - Type: Text corpus
   - Size: ~1 million words
   - Purpose: General-purpose English language corpus
   - Used by: TextBlob for sentiment analysis training
   - Download: `nltk.download('brown')`

2. **Punkt Tokenizer Models**
   - Type: Pre-trained tokenization models
   - Purpose: Sentence boundary detection and tokenization
   - Used by: NLTK for text processing
   - Download: `nltk.download('punkt')`

### Built-in Knowledge Bases

The application includes several built-in keyword databases for emotion detection:

1. **Distress Keywords Dataset** (24 keywords)
   - Location: `emotion_analyzer.py`
   - Purpose: Detect emotional distress in user messages
   - Keywords include:
     - Emotional states: 'sad', 'depressed', 'hopeless', 'worthless', 'alone', 'lonely'
     - Anxiety/fear: 'anxious', 'scared', 'afraid', 'helpless', 'trapped', 'stuck'
     - Physical/emotional pain: 'hurt', 'pain', 'suffering'
     - Abuse-related: 'abuse', 'abused', 'victim'
     - Crisis indicators: 'can\'t take it', 'give up', 'end it', 'suicide', 'die', 'tired of living'

2. **Abuse Indicator Keywords Dataset** (16 keywords/phrases)
   - Location: `emotion_analyzer.py`
   - Purpose: Detect potential abuse situations
   - Keywords include:
     - Direct abuse terms: 'abuse', 'abused', 'abusive', 'domestic violence'
     - Manipulation tactics: 'controlling', 'manipulative', 'gaslighting'
     - Emotional harm: 'threatened', 'intimidated', 'belittled', 'humiliated'
     - Isolation: 'isolated', 'trapped'
     - Relationship types: 'toxic relationship', 'emotional abuse', 'verbal abuse'

3. **Support Resources Database**
   - Location: `config.py`
   - Includes:
     - General mental health hotlines (988, 741741, 1-800-662-4357)
     - Domestic violence resources (1-800-799-7233, 88788, 1-800-656-4673)
     - Women's organizations (1-303-839-1852, 202-628-8669)
     - Professional support guidance

4. **Greeting Messages Database**
   - Location: `config.py`
   - Purpose: Variety of welcoming messages for user interaction

### User-Generated Data

The application creates and maintains local user datasets:

1. **User Profile Data**
   - Storage Location: `~/.wellness_buddy/[username].json`
   - Format: JSON
   - Contains:
     - User identification and preferences
     - Gender information
     - Safety settings (unsafe contacts)
     - Trusted contacts list
     - Session history and statistics

2. **Emotional History Data**
   - Storage: Part of user profile JSON
   - Contains:
     - Emotion analysis results per message
     - Sentiment polarity scores
     - Distress keyword matches
     - Abuse indicator detections
     - Timestamps for all entries
     - Pattern tracking over time (up to 90 days)

## 🏗️ Application Architecture

### Core Modules

1. **wellness_buddy.py**: Main application controller
2. **emotion_analyzer.py**: NLP-based emotion analysis using TextBlob
3. **pattern_tracker.py**: Time-series emotional pattern tracking
4. **alert_system.py**: Distress detection and alert management
5. **conversation_handler.py**: Conversation flow and response generation
6. **user_profile.py**: User profile management with safety features
7. **data_store.py**: JSON-based persistent storage system
8. **config.py**: Configuration and resource databases
9. **ui_app.py**: Streamlit-based web interface

### Data Storage Technology

- **Format**: JSON (JavaScript Object Notation)
- **Storage**: Local filesystem (`~/.wellness_buddy/`)
- **Serialization**: Python's built-in `json` module
- **Benefits**: 
  - Human-readable
  - No external database server required
  - Privacy-focused (all data stays local)
  - Easily portable and backup-friendly
  - Can be encrypted if needed

## 🔧 Configuration & Thresholds

Key algorithmic parameters defined in `config.py`:

- **DISTRESS_THRESHOLD**: -0.3 (sentiment polarity threshold)
- **SUSTAINED_DISTRESS_COUNT**: 3 (consecutive distress messages to trigger alert)
- **PATTERN_TRACKING_WINDOW**: 10 (number of recent messages analyzed)
- **MAX_CONVERSATION_HISTORY**: 50 (maximum messages stored per session)

## 📱 User Interfaces

1. **Command Line Interface (CLI)**
   - Technology: Python standard I/O
   - Entry point: `wellness_buddy.py`

2. **Web Browser Interface**
   - Technology: Streamlit framework
   - Entry point: `ui_app.py`
   - Features: Point-and-click, chat interface, visual profile management

## 🔒 Privacy & Security

### Data Privacy Technologies
- **Local-only storage**: No cloud services or external APIs
- **File system permissions**: User home directory storage
- **JSON format**: Supports future encryption implementation
- **User control**: Built-in data deletion functionality

### No External AI/ML Services
- The application does NOT use:
  - External AI APIs (OpenAI, Claude, etc.)
  - Cloud-based ML services
  - External databases
  - Third-party analytics
  
All processing is done locally using open-source libraries.

## 📦 Installation & Setup

### Package Management
- **Package Manager**: pip (Python package installer)
- **Dependencies File**: `requirements.txt`

### Quick Setup Scripts
- **quickstart.sh**: Bash script for automated setup
- **start_ui.sh**: Bash script for launching web UI

## 🧪 Testing

- **Test Framework**: Python's built-in `unittest` module
- **Test File**: `test_wellness_buddy.py`
- **Test Coverage**: All core modules (emotion analyzer, pattern tracker, alert system, etc.)

## 📝 Documentation

- **README.md**: Main project documentation
- **USAGE.md**: Quick start guide
- **UI_GUIDE.md**: Web interface guide
- **UI_DEMO.txt**: UI demonstration notes
- **TECHNOLOGIES_AND_DATASETS.md**: This file

## 🌐 External Resources

While the application doesn't connect to external services during operation, it provides references to:
- Crisis hotlines and helplines
- Mental health resources
- Domestic violence support organizations
- Professional support contacts

These are informational only and embedded in the configuration file.

## Summary

The AI Wellness Buddy uses a **lightweight, privacy-focused technology stack** based on:
- Python's NLP libraries (NLTK, TextBlob) for emotion analysis
- Local JSON storage for data persistence
- Streamlit for modern web UI
- No external APIs or cloud services
- Open-source, transparent algorithms
- User-controlled data with complete privacy

All datasets are either:
1. Standard NLP corpora (Brown, Punkt) downloaded via NLTK
2. Curated keyword lists for emotion/abuse detection
3. User-generated data stored locally in JSON format
