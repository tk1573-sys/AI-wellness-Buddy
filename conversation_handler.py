"""
Conversation handler for managing emotional support interactions.
Supports fine-grained emotion routing (joy/sadness/anger/fear/anxiety/crisis)
and response-style preferences (short/detailed/balanced).
"""

import random
from datetime import datetime
import config
from language_handler import LanguageHandler as _LangHandler

_lang_handler = _LangHandler()


# -----------------------------------------------------------------------
# Response templates keyed by (primary_emotion, style)
# Each entry is a list; one is chosen at random.
# -----------------------------------------------------------------------
_RESPONSES = {
    # ---- joy ----
    'joy': {
        'short': [
            "That's wonderful! 😊 Hold onto this feeling.",
            "So glad to hear that! 💛 Keep shining.",
        ],
        'detailed': [
            "I'm really glad to hear that! 😊 Moments like these are precious — hold onto this feeling. "
            "What's been bringing you the most joy today?",
            "That's wonderful to hear! Your happiness genuinely matters to me, and I'm here to celebrate "
            "these moments with you. 💛 These positive feelings are worth cherishing.",
        ],
        'balanced': [
            "I'm really glad to hear that! 😊 Moments like these are precious — hold onto this feeling.",
            "That's wonderful to hear! Your happiness genuinely matters to me. 💛",
            "It's so good to see you in a positive space today. You deserve every bit of joy! 🌟",
        ],
    },

    # ---- neutral ----
    'neutral': {
        'short': [
            "I hear you. I'm here whenever you're ready to share more.",
            "Thank you for checking in. How can I support you today?",
        ],
        'detailed': [
            "Thank you for sharing. I'm fully here with you — there's no rush, take all the time you need. "
            "Even 'just okay' days tell us something about how we're doing.",
            "I hear you. Sometimes 'just okay' is a completely valid place to be. "
            "Would you like to explore what's on your mind, or simply know that I'm here?",
        ],
        'balanced': [
            "Thank you for sharing. I'm fully here with you — there's no rush, take all the time you need.",
            "I hear you. Sometimes 'just okay' is a completely valid place to be. "
            "Would you like to explore what's on your mind?",
            "I appreciate you checking in. I'm listening, and we can go wherever feels right for you.",
        ],
    },

    # ---- sadness ----
    'sadness': {
        'short': [
            "I'm so sorry you're feeling this way. I'm right here with you. 💙",
            "Your sadness is real and valid. I'm here and I care. 💙",
        ],
        'detailed': [
            "I'm so sorry you're carrying this sadness. It takes real courage to acknowledge it, "
            "and I want you to know you're not alone — I'm right here with you. 💙 "
            "Would you like to talk about what's weighing on you?",
            "Sadness can feel so heavy, and what you're feeling is completely valid. "
            "Please know that reaching out was the right thing to do — I'm here for you. 💙",
        ],
        'balanced': [
            "I'm so sorry you're feeling this way. Your sadness is real and it matters — I'm here with you. 💙",
            "That sounds incredibly painful. You don't have to carry this alone; I'm right here. 💙",
            "I can hear how heavy this feels. Your feelings are completely valid, and I care deeply. 💙",
        ],
    },

    # ---- anger ----
    'anger': {
        'short': [
            "It's okay to feel angry. I'm here to listen without judgment.",
            "Your frustration is valid. Take a breath — I'm with you.",
        ],
        'detailed': [
            "It's completely valid to feel angry, and I want to hear what's driving that. "
            "Anger often signals that something important to us has been hurt or threatened. "
            "I'm here to listen without judgment — what's going on?",
            "I hear your frustration, and it makes sense. Anger is a signal worth paying attention to. "
            "Let's explore what's underneath this together, at your pace.",
        ],
        'balanced': [
            "It's completely okay to feel angry. I'm here to listen without judgment. 💙",
            "That frustration sounds real and valid. I'm with you — tell me more when you're ready.",
            "I hear you. Anger is a signal worth listening to; I'm here with you.",
        ],
    },

    # ---- fear ----
    'fear': {
        'short': [
            "You're not facing this fear alone — I'm right here with you. 💙",
            "Fear can feel overwhelming. I'm here and I care.",
        ],
        'detailed': [
            "Fear can feel truly overwhelming, and I want you to know that you are not facing this alone. "
            "What you're experiencing is real, and there is support available. "
            "I'm right here with you — tell me more about what's frightening you. 💙",
            "I hear that fear in what you're sharing. That takes courage to admit. "
            "You don't have to face this by yourself — I'm here with you every step of the way. 💙",
        ],
        'balanced': [
            "You're not facing this fear alone — I'm right here with you. 💙",
            "Fear is incredibly hard to carry. I hear you, and I care about what you're going through.",
            "That sounds really frightening. Please know that you don't have to face this alone. 💙",
        ],
    },

    # ---- anxiety ----
    'anxiety': {
        'short': [
            "Anxiety is exhausting. Take a slow breath — I'm here with you.",
            "You're not alone with this worry. I'm right here. 💙",
        ],
        'detailed': [
            "Anxiety can be completely exhausting — your mind and body are working so hard. "
            "I want you to know that what you're feeling is real and understandable, "
            "and I'm here to sit with you through it. 💙 "
            "Sometimes it helps to just name what you're anxious about — would you like to try?",
            "The overwhelm you're feeling makes complete sense. Anxiety has a way of magnifying "
            "everything at once. Take a gentle breath — I'm here with you, and we can work through "
            "this together one step at a time. 💙",
        ],
        'balanced': [
            "Anxiety is exhausting, and I hear you. Take a slow breath — I'm right here with you. 💙",
            "You're not alone in this worry. What you're feeling is valid, and I care deeply. 💙",
            "I can hear how overwhelmed you feel. Let's take this one moment at a time — I'm with you.",
        ],
    },

    # ---- crisis ----
    'crisis': {
        'short': [
            "I'm very concerned about you right now. Please reach out to a crisis line immediately — "
            "988 (call/text) is available 24/7. I'm here. 💙",
        ],
        'detailed': [
            "What you've shared frightens me deeply, and I want you to know that your life matters "
            "immensely. Please reach out to the 988 Suicide & Crisis Lifeline right now — "
            "call or text 988, available 24/7, completely free and confidential. "
            "If you're in immediate danger, please call 911 or go to your nearest emergency room. "
            "I'm here with you, and you are not alone. 💙",
        ],
        'balanced': [
            "I'm very concerned about what you've shared, and I want you to know that your life matters "
            "deeply. Please reach out to the 988 Suicide & Crisis Lifeline (call or text 988) right now — "
            "they're available 24/7 and here for you. If you're in immediate danger, call 911. "
            "I'm here with you. 💙",
        ],
    },
}


class ConversationHandler:
    """Manages conversation flow and responses"""

    def __init__(self):
        self.conversation_history = []

    def add_message(self, user_message, emotion_data):
        """Add a message to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_message': user_message,
            'emotion_data': emotion_data
        })

        # Limit history size
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]

    def generate_response(self, emotion_data, user_context=None):
        """Generate a warm, humanoid, personalized response based on
        emotional state and optional user profile context.
        Supports English, Tamil, and bilingual (Tamil+English) responses."""
        primary_emotion = emotion_data.get('primary_emotion', None)
        coarse_emotion = emotion_data['emotion']
        severity = emotion_data['severity']

        # Determine response style
        style = 'balanced'
        if user_context:
            style = user_context.get('response_style', 'balanced')

        # Language preference
        lang_pref = 'english'
        if user_context:
            lang_pref = user_context.get('language_preference', 'english')

        # Detect whether the latest message touches a known personal trigger
        triggered = False
        if user_context and self.conversation_history:
            last_msg = self.conversation_history[-1]['user_message'].lower()
            for trigger in user_context.get('personal_triggers', []):
                if trigger in last_msg:
                    triggered = True
                    break

        has_trauma = user_context and user_context.get('has_trauma_history', False)
        marital_status = user_context.get('marital_status') if user_context else None
        family_bg = user_context.get('family_background') if user_context else None

        # ---- Try bilingual / Tamil pool first (if preference set) ----
        lang_pool = []
        if lang_pref in ('tamil', 'bilingual') and primary_emotion:
            lang_pool = _lang_handler.get_response_pool(primary_emotion, lang_pref)

        if lang_pool:
            response = random.choice(lang_pool)
        elif primary_emotion and primary_emotion in _RESPONSES:
            # ---- Route by fine-grained primary emotion (English) ----
            pool = _RESPONSES[primary_emotion].get(style, _RESPONSES[primary_emotion]['balanced'])
            response = random.choice(pool)
        else:
            # ---- Fallback to coarse-emotion logic (backward-compatible) ----
            if coarse_emotion == 'positive':
                pool = _RESPONSES['joy'].get(style, _RESPONSES['joy']['balanced'])
            elif coarse_emotion == 'neutral':
                pool = _RESPONSES['neutral'].get(style, _RESPONSES['neutral']['balanced'])
            elif coarse_emotion == 'negative' and severity == 'medium':
                pool = _RESPONSES['sadness'].get(style, _RESPONSES['sadness']['balanced'])
                if has_trauma:
                    pool = pool + [
                        "I hear you, and given what you've already been through, it makes complete sense "
                        "that this feels heavy. You've shown real strength before, and I'm right here. 💙"
                    ]
                if marital_status in ('divorced', 'widowed', 'separated'):
                    pool = pool + [
                        "Life transitions like the one you've been through can make hard days feel even "
                        "harder. Your feelings are understandable, and I'm here to listen. 💙"
                    ]
            else:  # distress or high severity
                pool = _RESPONSES['sadness'].get(style, _RESPONSES['sadness']['balanced']) + [
                    "I hear you, and I want you to know you are not alone in this moment. "
                    "Your pain is real and it matters deeply. 💙",
                    "I'm genuinely concerned about how you're feeling. "
                    "You don't have to face this alone; help is always here for you. 💙",
                ]
                if has_trauma:
                    pool.append(
                        "I can hear how much pain you're in, and I want you to know that your past "
                        "experiences don't define your worth. You have survived hard things before. 💙"
                    )
                if family_bg:
                    pool.append(
                        "Given everything that has shaped your life, what you're feeling makes sense. "
                        "Please know that you are seen, heard, and supported. 💙"
                    )
            response = random.choice(pool)

        # Personalise for trauma context on heavier emotions (English / bilingual)
        if lang_pref != 'tamil':
            if primary_emotion in ('sadness', 'fear', 'anxiety', 'crisis') and has_trauma:
                response += (
                    "\n\nI also want you to know — given everything you've been through before, "
                    "your resilience is real. You are not alone in this moment. 💙"
                )
            if primary_emotion in ('sadness', 'anger') and marital_status in (
                    'divorced', 'widowed', 'separated'):
                response += (
                    "\n\nLife transitions like the one you've been through can make these feelings "
                    "especially heavy. Your emotions are completely understandable, and I'm here. 💙"
                )

        # Gently acknowledge if a personal trigger was mentioned
        if triggered:
            if lang_pref == 'tamil':
                response += (
                    "\n\nஒரு முக்கியமான விஷயம் பேசுகிறீர்கள். உங்கள் வேகத்தில் போகலாம் — "
                    "நான் இங்கே இருக்கிறேன். 💙"
                )
            elif lang_pref == 'bilingual':
                response += (
                    "\n\nநீங்கள் ஒரு முக்கியமான விஷயம் பற்றி பேசுகிறீர்கள். "
                    "It's okay to take your time — I'm here with you, no matter what. 💙"
                )
            else:
                response += (
                    "\n\nI noticed you touched on something that may feel especially sensitive for you. "
                    "It's completely okay to go at your own pace — I'm here with you, no matter what."
                )

        # Add specific support for abuse indicators
        if emotion_data.get('has_abuse_indicators'):
            if lang_pref == 'tamil':
                response += (
                    "\n\nநீங்கள் அனுபவிப்பது உங்கள் தவறு அல்ல. "
                    "நீங்கள் பாதுகாப்பாக இருக்க வேண்டும். 'help' என்று தட்டச்சு செய்யுங்கள். 💙"
                )
            elif lang_pref == 'bilingual':
                response += (
                    "\n\nஇது உங்கள் தவறு இல்லை — What you are experiencing is not your fault. "
                    "You deserve to feel safe. Type 'help' to see resources. 💙"
                )
            else:
                response += (
                    "\n\nI want you to know that what you are experiencing is not your fault. "
                    "You deserve to feel safe and respected. Specialized support is available whenever "
                    "you are ready — please type 'help' to see resources, or just keep talking to me. 💙"
                )

        # XAI: surface the explanation for transparency (English / bilingual only)
        explanation = emotion_data.get('explanation', '')
        if explanation and primary_emotion not in (None, 'neutral', 'joy') and lang_pref != 'tamil':
            response += f"\n\n_(Analysis: {explanation})_"

        # Pre-distress early warning from PredictionAgent
        if user_context:
            pre_distress = user_context.get('pre_distress_warning')
            if pre_distress and primary_emotion not in ('crisis', 'joy'):
                response += f"\n\n{pre_distress}"

        return response

    def get_greeting(self):
        """Get a greeting message"""
        return random.choice(config.GREETING_MESSAGES)
