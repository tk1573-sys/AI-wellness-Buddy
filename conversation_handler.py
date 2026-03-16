"""
Conversation handler for managing emotional support interactions.
Supports fine-grained emotion routing (joy/sadness/anger/fear/anxiety/crisis)
and response-style preferences (short/detailed/balanced).
"""

import logging
import random
from collections import deque
from datetime import datetime
import config
from empathetic_responder import EmpatheticResponder
_logger = logging.getLogger(__name__)


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

_EMPATHY_AMPLIFICATION_POOL = [
    "I can sense this is weighing on you deeply right now. "
    "Please be gentle with yourself — what you're feeling matters. 💙",
    "The intensity of what you're going through is real and valid. "
    "You don't have to face this alone — I'm right here with you. 💙",
    "I hear you, and I want you to know that your courage in sharing this "
    "means a great deal. You deserve support and kindness right now. 💙",
]

ANXIETY_RESPONSES = [
    "I can hear the tension in what you're sharing, and that feeling is valid.",
    "What you're feeling right now sounds really overwhelming, and you're not alone.",
    "Anxiety can make everything feel urgent; thank you for talking about it.",
    "It makes sense that your mind feels crowded right now.",
    "That worried feeling can be exhausting, and I appreciate your honesty.",
    "I hear how heavy this anxiety feels for you at this moment.",
    "It sounds like you're carrying a lot internally right now.",
    "Your concern is understandable, and I'm here with you through it.",
    "When anxiety spikes like this, even small things can feel intense.",
    "Thank you for sharing this anxiety with me — we can take it slowly.",
]

STRESS_RESPONSES = [
    "It sounds like you're under a lot of pressure right now.",
    "You're carrying many things at once, and that can feel draining.",
    "This level of stress sounds tough, and your reaction is understandable.",
    "I can hear how mentally and emotionally stretched you feel.",
    "What you're describing sounds like sustained pressure, not a small burden.",
    "That stress response makes sense given everything you're juggling.",
    "It's okay to acknowledge this load — it really does sound heavy.",
    "Your stress is real, and you deserve support while handling it.",
    "You're dealing with a lot, and it's understandable this feels intense.",
    "That constant pressure can wear anyone down; thank you for sharing it.",
]

SADNESS_RESPONSES = [
    "I'm really sorry this feels so heavy right now.",
    "I can hear the sadness in your words, and it matters.",
    "That sounds deeply painful, and I'm here with you.",
    "Your sadness is valid, and you don't have to carry it alone.",
    "It makes sense that this is weighing on your heart.",
    "Thank you for trusting me with this difficult feeling.",
    "I hear how low this moment feels for you.",
    "What you're feeling is real, and you deserve compassion.",
    "I'm with you in this, even if things feel very hard right now.",
    "This sounds emotionally exhausting, and your feelings are important.",
]

FEAR_RESPONSES = [
    "That sounds scary, and it's understandable to feel this way.",
    "I hear the fear in what you're sharing, and you're not alone.",
    "Feeling afraid in this situation makes a lot of sense.",
    "This fear sounds intense, and I'm here to stay with you through it.",
    "You're facing something that feels threatening, and that reaction is valid.",
    "It sounds like your nervous system is on high alert right now.",
    "Thank you for naming this fear — that takes courage.",
    "I can hear how unsettling this feels for you right now.",
    "What you're describing would make many people feel afraid.",
    "You don't have to process this fear by yourself.",
]

NEUTRAL_SUPPORT_RESPONSES = [
    "Thank you for checking in — I'm here to listen.",
    "I hear you, and we can take this conversation at your pace.",
    "I'm here with you; share as much or as little as feels right.",
    "Thanks for opening this conversation — your wellbeing matters.",
    "I'm listening, and we can explore whatever feels most important right now.",
    "I appreciate you reaching out today; that's a meaningful step.",
    "I'm present with you, and we can go one step at a time.",
    "Thank you for sharing — we can work through this together.",
    "I'm right here, and we can keep this gentle and steady.",
    "I hear you clearly, and your feelings are welcome here.",
]

TAMIL_EMPATHY_VARIATIONS = [
    "நான் உங்களுடன் இருக்கிறேன்.",
    "பரவாயில்லை, மெதுவாக பேசலாம்.",
    "உங்கள் உணர்வுகள் முக்கியம்.",
    "நாம் இதை ஒன்றாக சமாளிக்கலாம்.",
    "நீங்கள் தனியாக இல்லை, நான் கேட்கிறேன்.",
    "மெல்ல மெல்ல பேசலாம், நான் கவனமாக கேட்கிறேன்.",
    "இது கஷ்டமாக இருக்கலாம், ஆனாலும் நீங்கள் பாதுகாப்பாக இருக்கிறீர்கள்.",
    "உங்கள் மனநிலை பற்றி பகிர்ந்ததற்கு நன்றி.",
]

_CONVERSATIONAL_STYLES = ('reflective', 'supportive', 'exploratory', 'coping_guidance')

_TOPIC_KEYWORDS = {
    'work_stress': [
        'work', 'office', 'deadline', 'manager', 'boss', 'meeting', 'project',
        'job', 'shift', 'workload', 'target', 'performance',
    ],
    'career_anxiety': [
        'career', 'promotion', 'interview', 'future', 'exam', 'placement',
        'resume', 'salary', 'profession', 'role change',
    ],
    'relationship_issues': [
        'relationship', 'partner', 'marriage', 'husband', 'wife', 'boyfriend',
        'girlfriend', 'breakup', 'family fight', 'argument',
    ],
    'health_concerns': [
        'health', 'illness', 'pain', 'hospital', 'doctor', 'diagnosis', 'sleep',
        'insomnia', 'medicine', 'panic attack',
    ],
    'general_stress': [
        'stress', 'overwhelmed', 'pressure', 'burnout', 'drained', 'tired',
    ],
}

_TOPIC_SUGGESTIONS = {
    'work_stress': [
        "If work pressure is piling up, would a short reset break and a prioritized top-3 task list help?",
        "A quick workload sort might help: urgent, important, and can-wait.",
    ],
    'career_anxiety': [
        "Career uncertainty can feel intense — one concrete next step today can reduce mental load.",
        "Would it help to focus on one actionable step, like preparing for a single interview/topic?",
    ],
    'relationship_issues': [
        "If this is relationship-related, a calm boundary statement can sometimes reduce emotional strain.",
        "Would you like to frame what you need from that relationship in one clear sentence?",
    ],
    'health_concerns': [
        "Health worries are hard to carry; grounding with slow breathing and gentle self-checks may help.",
        "If symptoms feel persistent or intense, seeking medical guidance can bring clarity and reassurance.",
    ],
    'general_stress': [
        "A tiny reset can help: unclench shoulders, exhale slowly, and choose one small next step.",
        "When stress stacks up, doing one manageable task first can restore a sense of control.",
    ],
}

_WORK_STRESS_COPING = [
    "Would a short priority reset help — list only the top 2 tasks for the next hour?",
    "A brief pause between work blocks can reduce pressure build-up; even 3 minutes can help.",
    "If useful, we can quickly split today's workload into must-do and can-wait.",
]

_ANXIETY_GROUNDING = [
    "If you'd like, try grounding: notice 5 things you see, 4 you feel, 3 you hear.",
    "A gentle breathing cycle can help: inhale slowly, hold briefly, and exhale longer.",
    "Would it help to name one worry and one thing you can control right now?",
]

_LOW_MOOD_SUPPORT = [
    "If it feels okay, writing a few lines about what feels heaviest can bring clarity.",
    "A very small act of care — water, stretch, or fresh air — can sometimes soften this moment.",
    "Would you like to identify one supportive person you could text today?",
]

_RELATIONSHIP_REFLECTION = [
    "If you want, we can explore what you need most from that relationship right now.",
    "Sometimes naming your boundary in one sentence can reduce internal pressure.",
    "Would it help to separate what you can influence from what you can't in this situation?",
]

_TOPIC_CONTEXT_WINDOW = 6
_MAX_REGEN_ATTEMPTS = 6
# Keep lightweight memory limited to recent 10 turns for concise contextual references.
_MEMORY_WINDOW = 10
# Only occasionally reference memory to avoid overusing callback statements.
_MEMORY_REFERENCE_PROBABILITY = 0.35
# In early stage, skip suggestion half the time to avoid overly directive responses.
_EARLY_STAGE_SUGGESTION_SKIP_PROBABILITY = 0.5
_IMPROVING_TREND_MESSAGE_PROBABILITY = 0.5
_WORSENING_TREND_MESSAGE = "It sounds like things may be getting heavier over the last few messages."
_IMPROVING_TREND_MESSAGE = (
    "I also notice some signs of steadier breathing room compared with earlier messages."
)
_CALM_MODE_SUGGESTION = (
    "If you'd like, we can take a brief breathing pause together to help settle your system."
)
_TREND_LAST_STEP_THRESHOLD = 1
_TREND_DELTA_THRESHOLD = 2
_TREND_IMPROVEMENT_DELTA = -1
_EMOTION_SEVERITY_RANK = {
    'joy': 0, 'neutral': 1, 'stress': 2, 'anxiety': 3,
    'fear': 3, 'sadness': 4, 'anger': 4, 'crisis': 5, 'distress': 5,
}

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
        self._style_idx = 0
        self._recent_responses = deque(maxlen=5)
        self._recent_pool_choices = deque(maxlen=5)
        self._topic_history = deque(maxlen=_MEMORY_WINDOW)
        self._emotion_history = deque(maxlen=_MEMORY_WINDOW)
        self._recent_user_messages = deque(maxlen=_MEMORY_WINDOW)
        self._emotion_timeline = deque(maxlen=config.MAX_CONVERSATION_HISTORY)
        self._last_response_metadata = {}
        self._research_logging_enabled = False
        self._session_log = []
        self._empathetic_responder = EmpatheticResponder()

    def add_message(self, user_message, emotion_data):
        """Add a message to conversation history"""
        primary_emotion = emotion_data.get('primary_emotion') or emotion_data.get('emotion', 'neutral')
        detected_topic = self._detect_topic(user_message)
        risk_score = float(emotion_data.get('severity_score', 0.0)) / 10.0
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_message': user_message,
            'emotion_data': emotion_data
        })
        self._recent_user_messages.append(user_message)
        self._emotion_history.append(primary_emotion)
        if detected_topic:
            self._topic_history.append(detected_topic)
        self._emotion_timeline.append({
            'timestamp': datetime.now().isoformat(),
            'emotion': primary_emotion,
            'risk_score': round(risk_score, 3),
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

    def get_emotion_timeline(self):
        """Return timeline entries for UI analytics charts."""
        return list(self._emotion_timeline)

    def get_last_response_metadata(self):
        """Return metadata from the most recently generated response."""
        return dict(self._last_response_metadata)

    def enable_research_logging(self, enabled=True):
        """Enable/disable structured research logging for the session."""
        self._research_logging_enabled = bool(enabled)

    def export_session_log(self):
        """Export structured response metadata collected in research mode."""
        return list(self._session_log)

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

    def _detect_emotion_trend(self, history=None):
        """Detect short-horizon emotion trend from recent states."""
        seq = list(history or self._emotion_history)
        if len(seq) < 3:
            return 'stable'
        vals = [_EMOTION_SEVERITY_RANK.get(e, 1) for e in seq[-4:]]
        delta = vals[-1] - vals[0]
        if vals[-1] >= max(vals[:-1]) + _TREND_LAST_STEP_THRESHOLD or delta >= _TREND_DELTA_THRESHOLD:
            return 'worsening'
        if vals[-1] <= min(vals[:-1]) - _TREND_LAST_STEP_THRESHOLD or delta <= _TREND_IMPROVEMENT_DELTA:
            return 'improving'
        return 'stable'

    def _choose_unique(self, pool):
        """Pick a random item from pool, avoiding recently used templates."""
        if len(pool) <= 1:
            return pool[0] if pool else ''
        recent_used = set(self._recent_pool_choices)
        candidates = [t for t in pool if t not in recent_used]
        if not candidates:
            candidates = [t for t in pool if t != self._last_pool_choice]
        if not candidates:
            candidates = pool
        chosen = random.choice(candidates)
        self._last_pool_choice = chosen
        self._recent_pool_choices.append(chosen)
        return chosen

    def _detect_topic(self, text):
        """Lightweight topic detection using keyword matching."""
        if not text:
            return None
        text_lower = text.lower()
        for topic, keywords in _TOPIC_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        return None

    @staticmethod
    def _escalation_stage(consecutive_count):
        """Map consecutive emotion count to escalation depth."""
        if consecutive_count >= 4:
            return 3
        if consecutive_count >= 3:
            return 2
        if consecutive_count >= 2:
            return 1
        return 0

    def _select_conversational_style(self):
        """Rotate conversational style with slight randomness for variety."""
        if random.random() < 0.4:
            return random.choice(_CONVERSATIONAL_STYLES)
        style_name = _CONVERSATIONAL_STYLES[self._style_idx % len(_CONVERSATIONAL_STYLES)]
        self._style_idx += 1
        return style_name

    def _build_memory_reference(self, topic, emotion):
        """Occasionally reference earlier repeated topic/emotion context."""
        if random.random() > _MEMORY_REFERENCE_PROBABILITY:
            return ""
        topic_count = self._topic_history.count(topic) if topic else 0
        emotion_count = self._emotion_history.count(emotion) if emotion else 0
        if topic and topic_count >= 2:
            readable_topic = topic.replace('_', ' ')
            return (
                f"You mentioned earlier that {readable_topic} has been recurring. "
                f"That kind of ongoing pressure can slowly drain energy."
            )
        if emotion and emotion_count >= 3:
            readable_emotion = emotion.replace('_', ' ')
            return (
                f"I've noticed this {readable_emotion} feeling has shown up repeatedly in the recent messages, "
                "which suggests it's been weighing on you for a while."
            )
        return ""

    def _get_adaptive_suggestion(self, topic, emotion, stage, calm_mode_active=False):
        """Return optional context-aware coping suggestion."""
        if stage < 1 and not calm_mode_active and random.random() < _EARLY_STAGE_SUGGESTION_SKIP_PROBABILITY:
            return ""
        if topic == 'work_stress':
            return self._choose_unique(_WORK_STRESS_COPING)
        if topic == 'relationship_issues':
            return self._choose_unique(_RELATIONSHIP_REFLECTION)
        if emotion in ('anxiety', 'stress') or calm_mode_active:
            return self._choose_unique(_ANXIETY_GROUNDING)
        if emotion in ('sadness', 'fear'):
            return self._choose_unique(_LOW_MOOD_SUPPORT)
        if topic in _TOPIC_SUGGESTIONS:
            return self._choose_unique(_TOPIC_SUGGESTIONS[topic])
        return ""

    @staticmethod
    def _avatar_state_for(emotion, trend):
        """Map emotion/trend to UI avatar animation state."""
        mapping = {
            'anxiety': 'glow',
            'sadness': 'slow_pulse',
            'stress': 'bounce',
            'neutral': 'soft_glow',
            'joy': 'soft_glow',
            'fear': 'pulse',
            'anger': 'pulse',
            'crisis': 'pulse',
        }
        if trend == 'worsening' and emotion in ('anxiety', 'stress', 'sadness', 'fear'):
            return 'pulse'
        return mapping.get(emotion, 'soft_glow')

    def _build_response_segments(self, emotion, topic, lang_pref, stage, conversation_style='supportive',
                                 calm_mode_active=False):
        """Compose response from modular empathy/reflection/suggestion/closing segments."""
        emotion_key = emotion if emotion in {'anxiety', 'stress', 'sadness', 'fear'} else 'neutral'
        empathy_map = {
            'anxiety': ANXIETY_RESPONSES,
            'stress': STRESS_RESPONSES,
            'sadness': SADNESS_RESPONSES,
            'fear': FEAR_RESPONSES,
            'neutral': NEUTRAL_SUPPORT_RESPONSES,
        }
        if lang_pref == 'tamil':
            tamil_empathy = self._choose_unique(TAMIL_EMPATHY_VARIATIONS)
            empathy = tamil_empathy
        else:
            empathy = self._choose_unique(empathy_map[emotion_key])
            if lang_pref == 'bilingual':
                tamil_empathy = self._choose_unique(TAMIL_EMPATHY_VARIATIONS)
                empathy = f"{tamil_empathy} {empathy}"

        reflection_pool = {
            0: [
                "I'm listening and staying with you in this moment.",
                "We can take this one gentle step at a time.",
            ],
            1: [
                "I can see this has been continuing and weighing on you.",
                "It sounds like this isn't just a passing moment — it's been persisting.",
            ],
            2: [
                "Since this feeling keeps returning, let's focus on one grounding step right now.",
                "Because this has stayed with you, a small coping action could help ease the intensity.",
            ],
            3: [
                "You've been carrying this for a while, so steady support and a practical plan may help.",
                "Given how persistent this is, we can combine emotional support with a simple action plan.",
            ],
        }
        style_extras = {0: [], 1: [], 2: [], 3: []}
        if conversation_style == 'exploratory':
            style_extras[0].append("What part of this feels the hardest right now?")
            style_extras[1].append("What has felt most draining about this lately?")
        elif conversation_style == 'coping_guidance':
            style_extras[2].append("Let's try one practical coping step and keep it manageable.")
            style_extras[3].append("We'll combine emotional support with a clear, gentle action plan.")
        elif conversation_style == 'reflective':
            style_extras[0].append("It sounds like you're carrying quite a lot right now.")
        else:  # supportive
            style_extras[0].append("I'm really glad you're sharing this here.")
        reflection_candidates = reflection_pool[stage] + style_extras[stage]
        reflection = self._choose_unique(reflection_candidates)

        suggestion = self._get_adaptive_suggestion(topic, emotion_key, stage, calm_mode_active=calm_mode_active)

        if stage >= 3:
            guidance_pool = [
                "If this keeps feeling intense, reaching out to a trusted person or professional support can be a strong next step.",
                "You deserve sustained support here — we can keep planning practical steps together.",
            ]
            suggestion = f"{suggestion} {self._choose_unique(guidance_pool)}".strip()

        closing_pool = [
            "I'm here with you.",
            "You're not alone in this.",
            "We'll move through this together.",
            "Your feelings matter, and I'm with you.",
        ]
        if lang_pref in ('tamil', 'bilingual'):
            closing_pool.extend([
                "நீங்கள் தனியாக இல்லை.",
                "நான் தொடர்ந்து உங்களுடன் இருக்கிறேன்.",
            ])
        closing = self._choose_unique(closing_pool)

        segments = [empathy, reflection]
        if suggestion:
            segments.append(suggestion)
        segments.append(closing)
        return " ".join(segment.strip() for segment in segments if segment and segment.strip())

    def _ensure_no_repeat(self, response, emotion, regenerate_fn=None):
        """Avoid duplicates across the most recent assistant replies."""
        _ = emotion  # kept for backward-compatible call signature
        attempts = 0
        while (
            response and response in self._recent_responses and regenerate_fn
            and attempts < _MAX_REGEN_ATTEMPTS
        ):
            response = regenerate_fn()
            attempts += 1
        if response and response in self._recent_responses:
            variation = _SUPPORT_VARIATIONS[self._support_idx % len(_SUPPORT_VARIATIONS)]
            self._support_idx += 1
            response = response + " " + variation
        self._last_response = response
        if response:
            self._recent_responses.append(response)
        return response

    def generate_response(self, emotion_data, user_context=None, return_metadata=False):
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

        debug_enabled = bool(user_context and user_context.get('debug_response_generation'))
        calm_mode_active = bool(user_context and user_context.get('calm_mode_active'))
        research_logging = bool(user_context and user_context.get('research_logging'))
        if research_logging:
            self.enable_research_logging(True)
        detected_topic = None
        template_label = "legacy"
        conversation_style = self._select_conversational_style()
        suggestion_type = None

        # Build conversational context text (current + recent) for topic detection
        context_msgs = []
        if user_context and isinstance(user_context.get('context'), list):
            context_msgs = [
                m.get('content', '')
                for m in user_context['context'][-_TOPIC_CONTEXT_WINDOW:]
                if m.get('role') == 'user'
            ]
        history_msgs = [
            e.get('user_message', '')
            for e in self.conversation_history[-_TOPIC_CONTEXT_WINDOW:]
        ]
        context_blob = " ".join([m for m in (context_msgs + history_msgs) if m])
        detected_topic = self._detect_topic(context_blob)
        emotion_trend = self._detect_emotion_trend()

        normalized_emotion = primary_emotion
        # In work/pressure contexts, anger often reflects stress overload; route to stress pool.
        if normalized_emotion == 'anger' and detected_topic in ('work_stress', 'general_stress'):
            normalized_emotion = 'stress'
        if normalized_emotion not in ('anxiety', 'stress', 'sadness', 'fear'):
            if coarse_emotion == 'negative':
                normalized_emotion = 'sadness'
            elif coarse_emotion == 'neutral':
                normalized_emotion = 'neutral'

        # Capture last user message for empathetic responder
        _last_user_msg = ''
        if self.conversation_history:
            _last_user_msg = self.conversation_history[-1].get('user_message', '')

        # Crisis response remains explicit and immediate
        if primary_emotion == 'crisis':
            crisis_pool = _RESPONSES['crisis'].get(style, _RESPONSES['crisis']['balanced'])
            response = self._choose_unique(crisis_pool)
            template_label = f"crisis/{style}"
        # Positive emotion uses existing joy templates
        elif coarse_emotion == 'positive' and primary_emotion not in ('anxiety', 'stress', 'sadness', 'fear'):
            joy_pool = _RESPONSES['joy'].get(style, _RESPONSES['joy']['balanced'])
            response = self._choose_unique(joy_pool)
            template_label = f"joy/{style}"
        else:
            consec = self._consecutive_emotion_count(primary_emotion) if primary_emotion else 1
            stage = self._escalation_stage(consec)
            # Use empathetic responder for warm, human-like replies
            concern_level = emotion_data.get('concern_level', 'low')
            emotion_confidence = emotion_data.get('emotion_confidence', 0.0)
            chat_context = user_context.get('context') if user_context else None
            empathetic_base = self._empathetic_responder.generate_response(
                user_text=_last_user_msg,
                emotion=normalized_emotion or 'neutral',
                concern_level=concern_level,
                emotion_confidence=emotion_confidence,
                history=chat_context,
            )
            # Append topic-specific adaptive suggestion when a topic is detected
            topic_suggestion = self._get_adaptive_suggestion(
                detected_topic, normalized_emotion or 'neutral', stage,
                calm_mode_active=calm_mode_active,
            )
            if topic_suggestion and lang_pref != 'tamil':
                empathetic_base = f"{empathetic_base} {topic_suggestion}"
            # For Tamil, fall back to modular segments (Tamil phrase pools)
            if lang_pref == 'tamil':
                response = self._build_response_segments(
                    normalized_emotion or 'neutral',
                    detected_topic,
                    lang_pref,
                    stage,
                    conversation_style=conversation_style,
                    calm_mode_active=calm_mode_active,
                )
            else:
                response = empathetic_base
            template_label = f"empathetic/{normalized_emotion or 'neutral'}/stage-{stage}"
            if detected_topic:
                template_label += f"/{detected_topic}"
            if detected_topic == 'work_stress':
                suggestion_type = 'work_stress_coping'
            elif detected_topic == 'relationship_issues':
                suggestion_type = 'relationship_reflection'
            elif normalized_emotion in ('anxiety', 'stress'):
                suggestion_type = 'anxiety_grounding'
            elif normalized_emotion in ('sadness', 'fear'):
                suggestion_type = 'low_mood_support'
            else:
                suggestion_type = 'general_support'

        memory_reference = self._build_memory_reference(detected_topic, normalized_emotion)
        if memory_reference and lang_pref != 'tamil':
            response += f"\n\n{memory_reference}"
            template_label += "/memory-ref"

        if emotion_trend == 'worsening' and lang_pref != 'tamil':
            response += f"\n\n{_WORSENING_TREND_MESSAGE}"
        elif (
            emotion_trend == 'improving'
            and lang_pref != 'tamil'
            and random.random() < _IMPROVING_TREND_MESSAGE_PROBABILITY
        ):
            response += f"\n\n{_IMPROVING_TREND_MESSAGE}"

        # ---- Personalised name greeting (warm touch) ----
        if user_name and lang_pref != 'tamil' and primary_emotion not in ('crisis',) and response:
            # Prepend a short personal address for warmer tone
            if primary_emotion in ('sadness', 'fear', 'anxiety', 'anger', 'joy'):
                response = f"{user_name}, " + response[0].lower() + response[1:]

        # ---- Confidence-based empathy amplification ----
        # When the dominant negative emotion probability is very high (>0.6),
        # add stronger supportive language to acknowledge intensity.
        emotion_confidence = float(emotion_data.get('emotion_confidence', 0.0))
        concern_level = emotion_data.get('concern_level', 'low')
        if lang_pref != 'tamil' and primary_emotion in ('sadness', 'fear', 'anxiety'):
            if emotion_confidence > 0.6 or concern_level in ('high', 'critical'):
                response += "\n\n" + self._choose_unique(_EMPATHY_AMPLIFICATION_POOL)

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

        # Keep escalation follow-ups for additional continuity on repeated negative emotions
        if primary_emotion and lang_pref != 'tamil':
            consec = self._consecutive_emotion_count(primary_emotion)
            if consec >= 2 and primary_emotion in _ESCALATION_FOLLOWUPS:
                pool = _ESCALATION_FOLLOWUPS[primary_emotion]
                response += pool[(consec - 2) % len(pool)]

        calm_mode_suggested = False
        breathing_suggested = False
        repeated_anxiety_or_stress = (
            primary_emotion in ('anxiety', 'stress')
            and self._consecutive_emotion_count(primary_emotion) >= 2
        )
        if repeated_anxiety_or_stress and not calm_mode_active:
            response += f"\n\n{_CALM_MODE_SUGGESTION}"
            calm_mode_suggested = True
            breathing_suggested = True
            if not suggestion_type:
                suggestion_type = 'anxiety_grounding'

        # Offer grounding for high concern non-anxiety emotions that missed
        # the breathing path above (completes the coping-tool step).
        # Tamil is excluded because grounding phrases have no Tamil
        # translations yet; Tamil responses use modular segment pools.
        if (
            not breathing_suggested
            and concern_level in ('high', 'critical')
            and primary_emotion in ('sadness', 'fear')
            and lang_pref != 'tamil'
        ):
            response += "\n\n" + self._choose_unique(_ANXIETY_GROUNDING)
            if not suggestion_type:
                suggestion_type = 'grounding_exercise'

        # For crisis: skip breathing UI suggestion entirely
        if primary_emotion == 'crisis':
            breathing_suggested = False
            calm_mode_suggested = False

        if debug_enabled:
            _logger.info(
                "Response debug | emotion=%s topic=%s template=%s",
                primary_emotion,
                detected_topic or 'none',
                template_label,
            )

        # ---- Anti-repeat safeguard (recent window of 5) ----
        regen_stage = self._escalation_stage(
            self._consecutive_emotion_count(primary_emotion) if primary_emotion else 1
        )

        def _regen():
            if lang_pref != 'tamil':
                return self._empathetic_responder.generate_response(
                    user_text=_last_user_msg,
                    emotion=normalized_emotion or 'neutral',
                    concern_level=emotion_data.get('concern_level', 'low'),
                    emotion_confidence=emotion_data.get('emotion_confidence', 0.0),
                    history=user_context.get('context') if user_context else None,
                )
            refreshed = self._build_response_segments(
                normalized_emotion or 'neutral',
                detected_topic,
                lang_pref,
                regen_stage,
                conversation_style=conversation_style,
                calm_mode_active=calm_mode_active,
            )
            return refreshed

        response = self._ensure_no_repeat(
            response,
            primary_emotion,
            regenerate_fn=_regen if primary_emotion != 'crisis' else None,
        )

        avatar_state = self._avatar_state_for(normalized_emotion or 'neutral', emotion_trend)
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'emotion': normalized_emotion or 'neutral',
            'topic': detected_topic,
            'trend': emotion_trend,
            'avatar_state': avatar_state,
            'calm_mode_suggested': calm_mode_suggested,
            'breathing_suggested': breathing_suggested,
            'calm_mode_active': calm_mode_active,
            'conversational_style': conversation_style,
            'response_template': template_label,
            'suggestion_type': suggestion_type,
            'response': response,
        }
        self._last_response_metadata = metadata

        if self._research_logging_enabled:
            self._session_log.append({
                'timestamp': datetime.now().isoformat(),
                'emotion': metadata['emotion'],
                'topic': metadata['topic'],
                'trend': metadata['trend'],
                'response_template': metadata['response_template'],
                'suggestion_type': metadata['suggestion_type'],
            })

        if return_metadata:
            return metadata
        return response

    def get_greeting(self):
        """Get a greeting message"""
        return random.choice(config.GREETING_MESSAGES)
