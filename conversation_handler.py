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


_SUPPORT_VARIATIONS = [
    "I'm here with you.",
    "Thank you for sharing that.",
    "That sounds really difficult.",
    "You're not alone in this.",
    "Let's take this one step at a time.",
]

# Emotion-specific contextual follow-ups for escalation when the same
# emotion is detected multiple consecutive times.
_ESCALATION_FOLLOWUPS = {
    'anxiety': [
        "\n\nLet's try a grounding exercise: name 5 things you can see around you right now. 🌿",
        "\n\nWhen anxiety builds, slow breathing can help — try 4 seconds in, 7 hold, 8 out. 🌿",
        "\n\nAnxiety often lives in the future. Let's gently bring your focus to this present moment. 🌿",
    ],
    'sadness': [
        "\n\nYour sadness is valid and deserves to be heard. I'm sitting with you in this. 💙",
        "\n\nSometimes sadness needs space, not solutions. I'm here for as long as you need. 💙",
        "\n\nIt takes courage to sit with heavy feelings. You don't have to carry this alone. 💙",
    ],
    'fear': [
        "\n\nFear can feel overwhelming, but you are safe in this moment. Let's focus on what's real right now. 🛡️",
        "\n\nWhat you're feeling is a natural response. Let's work through it together, one thought at a time. 🛡️",
        "\n\nRemember: you have navigated difficult moments before, and you can again. 🛡️",
    ],
    'anger': [
        "\n\nAnger often signals that something important to you has been crossed. Let's explore that. 🔥",
        "\n\nIt's okay to feel angry. Acknowledging it is the first step — what feels most frustrating right now? 🔥",
        "\n\nYour anger is valid. When you're ready, let's talk about what might bring you some relief. 🔥",
    ],
    'stress': [
        "\n\nWhen everything feels like too much, breaking tasks into small steps can help. What's the smallest thing you could tackle first? 🌱",
        "\n\nStress often comes from carrying too much at once. Is there anything you could set down, even temporarily? 🌱",
        "\n\nYou're under a lot of pressure. Let's think about one thing you can do right now to lighten the load. 🌱",
    ],
    'crisis': [
        "\n\nI'm deeply concerned about you right now. Please know that help is available 24/7 — you can call 988 or text HOME to 741741. 💙",
        "\n\nYou matter, and what you're going through matters. If you're in crisis, please reach out to 988. I'm here too. 💙",
    ],
}


class ConversationHandler:
    """Manages conversation flow and responses"""

    def __init__(self):
        self.conversation_history = []
        self._last_pool_choice = None  # last base template chosen (for dedup)
        self._last_response = None     # full last assistant response (for anti-repeat)
        self._support_idx = 0          # rotating index into _SUPPORT_VARIATIONS

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

    # ------------------------------------------------------------------
    # Conversation context helpers
    # ------------------------------------------------------------------

    def get_chat_history(self):
        """Return structured chat history as a list of role/content dicts."""
        result = []
        for entry in self.conversation_history:
            result.append({"role": "user", "content": entry['user_message']})
        return result

    def _consecutive_emotion_count(self, emotion):
        """Count how many of the most recent messages share the same primary emotion."""
        count = 0
        for entry in reversed(self.conversation_history):
            e = entry.get('emotion_data', {}).get('primary_emotion')
            if e == emotion:
                count += 1
            else:
                break
        return count

    def _choose_unique(self, pool):
        """Pick a random item from pool, avoiding consecutive repetition of the same base template."""
        if len(pool) <= 1:
            return pool[0] if pool else ''
        candidates = [t for t in pool if t != self._last_pool_choice]
        if not candidates:
            candidates = pool
        chosen = random.choice(candidates)
        self._last_pool_choice = chosen
        return chosen

    def _ensure_no_repeat(self, response, emotion):
        """If *response* is identical to the last assistant response,
        append a rotating supportive follow-up to ensure variation."""
        if response and response == self._last_response:
            variation = _SUPPORT_VARIATIONS[self._support_idx % len(_SUPPORT_VARIATIONS)]
            self._support_idx += 1
            response = response + " " + variation
        self._last_response = response
        return response

    def generate_response(self, emotion_data, user_context=None):
        """Generate a warm, humanoid, personalized response based on
        emotional state and optional user profile context.
        Supports English, Tamil, and bilingual (Tamil+English) responses.

        *user_context* may contain a ``context`` key holding the structured
        chat history (list of ``{"role": ..., "content": ...}`` dicts) so
        the generator can take previous conversation into account."""
        primary_emotion = emotion_data.get('primary_emotion', None)
        coarse_emotion = emotion_data['emotion']
        severity = emotion_data['severity']
        sentiment_score = emotion_data.get('sentiment_score', emotion_data.get('polarity', 0.0))

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
        family_resp = user_context.get('family_responsibilities') if user_context else None
        occupation = user_context.get('occupation') if user_context else None
        living_situation = user_context.get('living_situation') if user_context else None
        user_name = user_context.get('user_name') if user_context else None

        # ---- Try bilingual / Tamil pool first (if preference set) ----
        lang_pool = []
        if lang_pref in ('tamil', 'bilingual') and primary_emotion:
            lang_pool = _lang_handler.get_response_pool(primary_emotion, lang_pref)

        if lang_pool:
            response = self._choose_unique(lang_pool)
        elif primary_emotion and primary_emotion in _RESPONSES:
            # ---- Route by fine-grained primary emotion (English) ----
            pool = _RESPONSES[primary_emotion].get(style, _RESPONSES[primary_emotion]['balanced'])
            response = self._choose_unique(pool)
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
            response = self._choose_unique(pool)

        # ---- Personalised name greeting (warm touch) ----
        if user_name and lang_pref != 'tamil' and primary_emotion not in ('crisis',) and response:
            # Prepend a short personal address for warmer tone
            if primary_emotion in ('sadness', 'fear', 'anxiety', 'anger', 'joy'):
                response = f"{user_name}, " + response[0].lower() + response[1:]

        # ---- Intensity adjustment based on sentiment score ----
        if lang_pref != 'tamil' and primary_emotion in ('sadness', 'fear', 'anxiety'):
            if sentiment_score < -0.6:
                response += (
                    "\n\nI can feel the weight of what you're carrying right now. "
                    "Please know that reaching out like this shows real courage. 💙"
                )

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
            # Family responsibilities context
            if family_resp and primary_emotion in ('sadness', 'anxiety', 'anger', 'fear'):
                response += (
                    f"\n\nI also hear the weight of your responsibilities — carrying so much for "
                    f"others while managing your own feelings takes real strength. "
                    f"Please remember that taking care of yourself is just as important. 💙"
                )
            # Occupation / work stress context
            if occupation and primary_emotion in ('anxiety', 'anger', 'sadness'):
                response += (
                    f"\n\nWork and daily responsibilities can add a great deal of pressure. "
                    f"It's okay to acknowledge that stress — you don't have to push through it alone. 💙"
                )
            # Living situation context (e.g. alone, unsafe home)
            if living_situation and primary_emotion in ('fear', 'anxiety', 'sadness', 'crisis'):
                response += (
                    f"\n\nYour living situation is something I'm keeping in mind. "
                    f"If you ever feel unsafe or need support, please don't hesitate to reach out "
                    f"to a trusted person or type 'help' to see resources. 💙"
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

        # ---- Emotional escalation for repeated emotions ----
        if primary_emotion and lang_pref != 'tamil':
            consec = self._consecutive_emotion_count(primary_emotion)
            if consec >= 2 and primary_emotion in _ESCALATION_FOLLOWUPS:
                pool = _ESCALATION_FOLLOWUPS[primary_emotion]
                response += pool[(consec - 2) % len(pool)]

        # ---- Anti-repeat safeguard ----
        response = self._ensure_no_repeat(response, primary_emotion)

        return response

    def get_greeting(self):
        """Get a greeting message"""
        return random.choice(config.GREETING_MESSAGES)
