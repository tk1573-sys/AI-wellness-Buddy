"""
Configuration settings for AI Wellness Buddy
"""

# Emotional distress thresholds
DISTRESS_THRESHOLD = -0.3  # Negative sentiment threshold
SUSTAINED_DISTRESS_COUNT = 3  # Number of consecutive distress messages to trigger alert
PATTERN_TRACKING_WINDOW = 10  # Number of recent messages to analyze for patterns

# Data retention settings (EXTENDED TRACKING)
EMOTIONAL_HISTORY_DAYS = 365  # Keep emotional history for 1 year (was 90 days)
CONVERSATION_ARCHIVE_DAYS = 180  # Archive conversations after 6 months
MAX_EMOTIONAL_SNAPSHOTS = 365  # Maximum number of emotional snapshots to keep

# Security settings
ENABLE_PROFILE_PASSWORD = True  # Require password for profile access
SESSION_TIMEOUT_MINUTES = 30  # Auto-logout after inactivity
ENABLE_DATA_ENCRYPTION = True  # Encrypt sensitive data at rest
MIN_PASSWORD_LENGTH = 8  # Minimum password length
MAX_LOGIN_ATTEMPTS = 3  # Maximum failed login attempts before lockout
LOCKOUT_DURATION_MINUTES = 15  # Duration of account lockout

# Guardian/Emergency Contact Settings
ENABLE_GUARDIAN_ALERTS = True  # Enable guardian notification system
GUARDIAN_ALERT_THRESHOLD = 'high'  # 'low', 'medium', 'high' - when to notify guardians
AUTO_NOTIFY_GUARDIANS = False  # Automatically notify or ask user first

# Support resources
GENERAL_SUPPORT_RESOURCES = {
    "crisis_hotline": "988 (Suicide & Crisis Lifeline)",
    "text_line": "Text HOME to 741741 (Crisis Text Line)",
    "mental_health": "SAMHSA National Helpline: 1-800-662-4357",
    "emergency": "911 (Emergency Services)"
}

WOMEN_SUPPORT_RESOURCES = {
    "domestic_violence": "1-800-799-7233 (National Domestic Violence Hotline)",
    "domestic_violence_text": "Text START to 88788",
    "women_safety": "1-800-656-4673 (RAINN National Sexual Assault Hotline)",
    "women_legal": "National Women's Law Center: 202-588-5180",
    "safety_planning": "Visit thehotline.org for safety planning resources"
}

# Government and Legal Resources for Women
GOVERNMENT_WOMEN_RESOURCES = {
    "us_govt": [
        "Office on Women's Health (HHS): 1-800-994-9662",
        "Women's Bureau (Department of Labor): 1-800-827-5335",
        "Violence Against Women Office (DOJ): 202-307-6026"
    ],
    "legal_aid": [
        "Legal Services Corporation: 202-295-1500",
        "National Women's Law Center: 202-588-5180",
        "American Bar Association Women's Rights: 312-988-5000"
    ],
    "mental_health": [
        "Women's Mental Health - NIMH: 1-866-615-6464",
        "Postpartum Support International: 1-800-944-4773",
        "Anxiety and Depression Association (Women): 240-485-1001"
    ],
    "international": [
        "UN Women Helpline: +1-212-906-6400",
        "International Women's Health Coalition: +1-212-979-8500",
        "Global Fund for Women: +1-415-248-4800"
    ]
}

# Trusted support resources (non-family for toxic situations)
TRUSTED_SUPPORT_RESOURCES = {
    "women_organizations": [
        "National Coalition Against Domestic Violence: 1-303-839-1852",
        "National Organization for Women: 202-628-8669",
        "Women's Resource Center (check local listings)"
    ],
    "friend_support_tips": [
        "Reach out to trusted friends outside your household",
        "Consider confiding in a colleague or mentor you trust",
        "Connect with support groups where you can meet safe people"
    ],
    "professional_support": [
        "Contact a therapist or counselor (confidential)",
        "Reach out to women's shelters for guidance",
        "Speak with a social worker who specializes in family situations"
    ]
}

# Conversation settings
MAX_CONVERSATION_HISTORY = 50
GREETING_MESSAGES = [
    "Hello! I'm here to support you. How are you feeling today?",
    "Welcome back! I'm here to listen. What's on your mind?",
    "Hi there! This is a safe space. How can I support you today?"
]

# Language settings
SUPPORTED_LANGUAGES = ('english', 'tamil', 'bilingual')
DEFAULT_LANGUAGE = 'english'   # 'english', 'tamil', or 'bilingual' (Tamil+English)

# Voice / TTS settings
TTS_ENABLED = True             # Enable text-to-speech responses (requires internet)
STT_ENABLED = True             # Enable speech-to-text input (requires internet)
TTS_DEFAULT_LANG = 'en'       # BCP-47 language code used by gTTS

# Alert messages
DISTRESS_ALERT_MESSAGE = """
⚠️ EMOTIONAL DISTRESS ALERT ⚠️

I've noticed you've been experiencing sustained emotional distress. 
Your wellbeing is important, and you don't have to face this alone.

Please consider reaching out to professional support:
"""

WOMEN_SAFETY_MESSAGE = """
🛡️ SPECIALIZED SUPPORT FOR WOMEN 🛡️

If you're experiencing emotional abuse in your family or relationship,
please know that you deserve safety and support:
"""
