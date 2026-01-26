"""
Configuration settings for AI Wellness Buddy
"""

# Emotional distress thresholds
DISTRESS_THRESHOLD = -0.3  # Negative sentiment threshold
SUSTAINED_DISTRESS_COUNT = 3  # Number of consecutive distress messages to trigger alert
PATTERN_TRACKING_WINDOW = 10  # Number of recent messages to analyze for patterns

# Support resources
GENERAL_SUPPORT_RESOURCES = {
    "crisis_hotline": "988 (Suicide & Crisis Lifeline)",
    "text_line": "Text HOME to 741741 (Crisis Text Line)",
    "mental_health": "SAMHSA National Helpline: 1-800-662-4357"
}

WOMEN_SUPPORT_RESOURCES = {
    "domestic_violence": "1-800-799-7233 (National Domestic Violence Hotline)",
    "domestic_violence_text": "Text START to 88788",
    "women_safety": "1-800-656-4673 (RAINN National Sexual Assault Hotline)",
    "women_legal": "National Women's Law Center: 202-588-5180",
    "safety_planning": "Visit thehotline.org for safety planning resources"
}

# Conversation settings
MAX_CONVERSATION_HISTORY = 50
GREETING_MESSAGES = [
    "Hello! I'm here to support you. How are you feeling today?",
    "Welcome back! I'm here to listen. What's on your mind?",
    "Hi there! This is a safe space. How can I support you today?"
]

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
