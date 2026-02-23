"""
Response Generation Agent — Module 4
Context-aware, emotion-category-specific response generation.
"""

import random
from datetime import datetime
import config


# ── Response template bank ────────────────────────────────────────────────────
# Keyed by dominant_emotion (multi-emotion categories from Module 1).
# Each entry is a list of templates; {name} and {occupation} are filled at runtime.

_TEMPLATES = {
    'joy': [
        "That's wonderful to hear{name}! 😊 Savour this positive moment — it matters.",
        "Your happiness is contagious{name}! Keep nurturing those good feelings. 🌟",
        "It's great to see you in such good spirits{name}! What's been making you smile?",
        "I love hearing that you're feeling positive{name}. Celebrate these moments! 🎉",
    ],
    'neutral': [
        "Thanks for sharing{name}. I'm here whenever you want to talk more.",
        "I hear you{name}. Would you like to explore what's on your mind a bit deeper?",
        "I'm listening{name} — feel free to share more, there's no rush.",
        "It sounds like you're taking things one step at a time{name}. How can I support you today?",
    ],
    'sadness': [
        "I'm sorry you're feeling this way{name}. 💙 Sadness is a natural emotion, and I'm here with you.",
        "It takes courage to share how you feel{name}. Your pain is valid — you don't have to carry it alone.",
        "I hear the sadness in your words{name}. Let's take this one moment at a time together.",
        "Thank you for opening up{name}. Grief and sadness deserve acknowledgement — I see you. 💙",
    ],
    'anxiety': [
        "I can sense the worry in your words{name}. Let's breathe through this together. 🌿",
        "Anxiety can be overwhelming{name}{occupation_context}. You're not alone — I'm here to help you find calm.",
        "It sounds like you're carrying a lot of stress{name}. Can we talk about what's weighing on you most?",
        "I hear how anxious you're feeling{name}. One small step at a time — you've got this. 💙",
    ],
    'anger': [
        "It sounds like you're really frustrated{name}. Those feelings are valid — I'm listening.",
        "Anger often signals something important{name}. Would you like to talk about what's driving it?",
        "I hear you{name} — it's okay to feel angry. Let's work through this together.",
        "Your feelings of frustration make sense{name}. Tell me more so I can better support you.",
    ],
    # Fallbacks for legacy emotion buckets
    'positive': [
        "I'm so glad to hear you're feeling positive{name}! That's wonderful. 😊",
        "It's great to see you in good spirits{name}! Keep nurturing those positive feelings.",
        "You're doing great{name}! Positive energy like this is worth holding onto. 🌟",
        "That sounds really encouraging{name}! I'm here to celebrate these moments with you.",
    ],
    'negative': [
        "I can sense you're going through a difficult time{name}. I'm here to support you. 💙",
        "That sounds challenging{name}. Remember, it's okay to feel this way.",
        "Thank you for opening up{name}. Your feelings are valid, and I'm here for you.",
        "I hear how hard things feel right now{name}{occupation_context}. You don't have to carry this alone.",
    ],
    'distress': [
        "I hear that you're really struggling right now{name}. You don't have to go through this alone. 💙",
        "What you're feeling sounds incredibly difficult{name}. Your wellbeing matters deeply — I'm here.",
        "I'm concerned about how you're feeling{name}. These emotions are heavy, but support is available.",
        "You reached out, and that takes courage{name}. I'm right here. Let's get through this together. 💙",
    ],
}


class ConversationHandler:
    """Manages conversation flow and context-aware responses."""

    def __init__(self):
        self.conversation_history = []

    def add_message(self, user_message, emotion_data):
        """Add a message to conversation history."""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_message': user_message,
            'emotion_data': emotion_data,
        })
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]

    def _build_name_str(self, user_profile):
        """Return " Name" string or empty string."""
        if not user_profile:
            return '', ''
        display_name = user_profile.get('name') or user_profile.get('user_id', '')
        name_str = f" {display_name}" if display_name else ''
        occ = user_profile.get('occupation', '')
        occ_ctx = f" as a {occ}" if occ else ''
        return name_str, occ_ctx

    def generate_response(self, emotion_data, user_profile=None):
        """
        Generate a context-aware, personalised response.

        Priority:
          1. Use dominant_emotion (multi-emotion category) if available.
          2. Fall back to legacy emotion bucket.
        """
        name_str, occ_ctx = self._build_name_str(user_profile)

        # Pick template bank
        dominant = emotion_data.get('dominant_emotion')
        legacy_emotion = emotion_data.get('emotion', 'neutral')
        key = dominant if (dominant and dominant in _TEMPLATES) else legacy_emotion
        templates = _TEMPLATES.get(key, _TEMPLATES['neutral'])

        # Abuse-indicator override
        if emotion_data.get('has_abuse_indicators'):
            templates = list(templates) + [
                f"I notice you mentioned something that may signal an unsafe situation{name_str}. "
                "You deserve to be safe and respected — specialised support is available."
            ]

        # Context awareness: avoid repeating the last response
        last_resp = getattr(self, '_last_response', None)
        candidates = [t for t in templates if t != last_resp] or templates
        chosen = random.choice(candidates)

        # Fill placeholders
        response = chosen.format(
            name=name_str,
            occupation_context=occ_ctx,
        )
        self._last_response = chosen
        return response

    def get_greeting(self):
        """Get a greeting message."""
        return random.choice(config.GREETING_MESSAGES)
