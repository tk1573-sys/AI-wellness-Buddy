"""
Empathetic response generator for warm, natural conversational replies.

Replaces formulaic template-based responses with a multi-layer pipeline:

    Emotional acknowledgment → Validation → Supportive statement → Optional suggestion

Each layer selects from curated phrase pools to produce varied, human-like
empathetic dialogue.
"""

import random
from collections import deque

# ---------------------------------------------------------------------------
# Emotion-specific empathy phrase pools
# ---------------------------------------------------------------------------

EMPATHY_PHRASES = {
    "sadness": [
        "I'm really sorry you're going through this.",
        "That sounds very painful.",
        "It must be hard carrying that feeling.",
        "I can hear how heavy things feel right now.",
        "That kind of sadness can be really exhausting.",
        "It takes courage to share something so difficult.",
        "I'm sorry you're hurting — that really matters.",
    ],
    "anxiety": [
        "That sounds overwhelming.",
        "I can understand why that would make you anxious.",
        "It makes sense that you'd feel stressed about that.",
        "When everything feels urgent, it can be really draining.",
        "That level of worry must be exhausting to carry around.",
        "I hear you — anxiety can make even small things feel huge.",
        "It's completely understandable to feel this way right now.",
    ],
    "anger": [
        "It sounds like you're really frustrated.",
        "That situation would upset many people.",
        "I can see why that made you angry.",
        "Your frustration makes a lot of sense given what happened.",
        "It's okay to feel angry — that's a very human response.",
        "Anyone in your position would feel that way.",
        "I hear the frustration in what you're sharing.",
    ],
    "fear": [
        "That sounds really scary.",
        "I can understand why you'd feel afraid right now.",
        "Feeling frightened in that situation makes complete sense.",
        "It takes real bravery to talk about what scares you.",
        "That kind of fear can feel so isolating.",
        "I hear you — that sounds genuinely frightening.",
        "It's natural to feel scared when things feel uncertain.",
    ],
    "stress": [
        "It sounds like you're under so much pressure right now.",
        "That's a lot to be carrying at once.",
        "No wonder you're feeling stretched thin.",
        "That kind of pressure can wear anyone down.",
        "I can hear how much is on your plate right now.",
        "You've been juggling a lot, and that's genuinely hard.",
        "It makes sense that you're feeling overwhelmed by all of this.",
    ],
    "joy": [
        "That's really wonderful to hear!",
        "I'm so glad things are going well for you.",
        "It sounds like you're in a really good place right now.",
        "That's such great news — you deserve to feel this way.",
        "Hearing that makes me genuinely happy for you.",
    ],
    "neutral": [
        "Thank you for sharing that with me.",
        "I appreciate you opening up.",
        "I'm here and listening.",
        "Thanks for letting me know what's on your mind.",
        "I hear you — take your time.",
    ],
}

# ---------------------------------------------------------------------------
# Validation phrases — affirm the user's emotional experience
# ---------------------------------------------------------------------------

VALIDATION_PHRASES = {
    "sadness": [
        "What you're feeling is completely valid.",
        "It's okay to feel this way — there's nothing wrong with that.",
        "Your feelings make sense, and you don't have to justify them.",
        "Anyone going through this would feel the same way.",
        "You're allowed to feel sad about this.",
    ],
    "anxiety": [
        "Your worry makes sense given what you're dealing with.",
        "It's completely normal to feel anxious about this.",
        "There's nothing wrong with feeling this way.",
        "Many people would feel exactly the same in your shoes.",
        "Your feelings are a natural response to what you're facing.",
    ],
    "anger": [
        "Your anger is completely understandable.",
        "It makes sense that you'd feel this way.",
        "You have every right to feel frustrated about this.",
        "That kind of reaction is totally human.",
        "There's nothing wrong with feeling angry here.",
    ],
    "fear": [
        "It's completely natural to feel afraid right now.",
        "Your fear is a normal response to this situation.",
        "There's no shame in feeling scared about this.",
        "Many people would feel the same way facing this.",
        "Your feelings make complete sense.",
    ],
    "stress": [
        "It's completely understandable that you'd feel this way.",
        "Anyone dealing with this much would feel the pressure.",
        "You're not overreacting — this is genuinely a lot.",
        "Your stress response makes total sense.",
        "It's okay to feel overwhelmed by all of this.",
    ],
    "joy": [
        "You absolutely deserve to feel this way.",
        "That happiness is well earned.",
        "Hold onto that feeling — it matters.",
    ],
    "neutral": [
        "Whatever you're feeling right now is okay.",
        "There's no right or wrong way to feel.",
        "It's perfectly fine to just check in like this.",
    ],
}

# ---------------------------------------------------------------------------
# Supportive statements — convey warmth and presence
# ---------------------------------------------------------------------------

SUPPORT_PHRASES = {
    "low": [
        "I'm right here with you.",
        "You don't have to figure this out alone.",
        "Take all the time you need.",
        "We can work through this together.",
    ],
    "medium": [
        "You're not alone in this — I'm here.",
        "I'm really glad you're talking about this.",
        "You're showing real strength by sharing.",
        "Please know that reaching out matters.",
    ],
    "high": [
        "I'm really glad you shared that with me.",
        "You don't have to handle this alone.",
        "Your wellbeing is what matters most right now.",
        "Please be gentle with yourself — you deserve care.",
        "I want you to know that someone hears you.",
    ],
    "critical": [
        "I'm really glad you shared that with me.",
        "You don't have to carry this by yourself.",
        "What you're feeling is serious, and you deserve support.",
        "Please know that help is available and you matter deeply.",
        "You are not alone, even when it feels that way.",
        "I hear you, and I'm staying right here with you.",
    ],
}

# ---------------------------------------------------------------------------
# Gentle suggestion pools — phrased as invitations, not commands
# ---------------------------------------------------------------------------

GENTLE_SUGGESTIONS = {
    "sadness": [
        "Sometimes it helps to take things one small step at a time.",
        "One thing that might help is giving yourself permission to rest.",
        "If you feel up to it, even a short walk can shift things slightly.",
        "When you're ready, we could talk about what would feel most supportive.",
        "It might help to do one small kind thing for yourself today.",
    ],
    "anxiety": [
        "Sometimes a few slow, deep breaths can help ground you in the moment.",
        "One small thing that might help is focusing on just one thing at a time.",
        "If it feels right, try naming five things you can see around you.",
        "When anxiety spikes, even a brief pause can make a difference.",
        "It might help to write down what's worrying you — sometimes seeing it helps.",
    ],
    "anger": [
        "Sometimes stepping away from the situation briefly can help clear your head.",
        "If it feels right, try putting those feelings into words — even in writing.",
        "One thing that might help is giving yourself space to cool down first.",
        "When frustration builds up, a short physical activity can release some of it.",
        "It might help to think about what would feel fair to you in this situation.",
    ],
    "fear": [
        "Sometimes talking through what specifically scares you can make it feel smaller.",
        "If you'd like, we can break this down into smaller, more manageable pieces.",
        "One thing that might help is reminding yourself of times you've gotten through tough things.",
        "When fear feels big, focusing on what you can control right now can help.",
        "It might help to think about one small step you could take.",
    ],
    "stress": [
        "Sometimes it helps to pick just one thing to focus on and let the rest wait.",
        "If you can, even a short break might help you reset.",
        "One thing that might help is writing down everything on your plate — it can feel lighter.",
        "When it all feels like too much, starting with the smallest task can build momentum.",
        "It might help to figure out which thing needs attention first and start there.",
    ],
    "neutral": [
        "If anything comes to mind that you'd like to talk about, I'm here.",
        "Sometimes just checking in with yourself is a good first step.",
        "If you'd like, we can explore what's been on your mind lately.",
    ],
}

# ---------------------------------------------------------------------------
# High-concern deepening phrases
# ---------------------------------------------------------------------------

HIGH_CONCERN_DEEPENERS = [
    "I really want you to know — what you're feeling matters, and so do you.",
    "Please don't hesitate to reach out to someone you trust if things feel too heavy.",
    "You deserve real support right now, not just kind words.",
    "If this has been going on for a while, talking to a professional could help a lot.",
    "I'm here for you, and I hope you know that asking for help is a sign of strength.",
]

# ---------------------------------------------------------------------------
# Context-aware phrases — reference conversation history
# ---------------------------------------------------------------------------

HISTORY_AWARE_PHRASES = [
    "It sounds like this has been weighing on you for a while now.",
    "From what you've shared, it seems like things have been building up.",
    "I can see this isn't something that just started — you've been dealing with this.",
    "Given everything you've told me, I can understand why this feels so heavy.",
]

# ---------------------------------------------------------------------------
# Humanisation post-processing helpers
# ---------------------------------------------------------------------------

_ROBOTIC_PHRASES = [
    "I have detected",
    "I can see that the emotional state is",
    "Based on my analysis",
    "My assessment indicates",
    "I am programmed to",
]

_FILLER_SOFTENERS = [
    (" You should ", " Sometimes it helps to "),
    (" You need to ", " One thing that might help is to "),
    (" You must ", " It might be worth trying to "),
    (" You have to ", " If you feel up to it, you could "),
]


class EmpatheticResponder:
    """Multi-layer empathetic response generator.

    Produces warm, varied, human-sounding replies by composing four
    independent layers:

    1. **Emotional acknowledgment** — show the user you *hear* them.
    2. **Validation** — affirm that their feelings make sense.
    3. **Supportive statement** — convey warmth and presence,
       with intensity scaled by *concern_level*.
    4. **Optional suggestion** — a gentle, non-directive nudge.
    """

    def __init__(self):
        self._recent_phrases: deque = deque(maxlen=30)
        # Track last 3 full responses to prevent repetition across messages
        self._recent_responses: deque = deque(maxlen=3)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_response(
        self,
        user_text: str,
        emotion: str,
        concern_level: str = "low",
        emotion_confidence: float = 0.0,
        history: list | None = None,
    ) -> str:
        """Build a multi-layer empathetic response.

        Parameters
        ----------
        user_text : str
            The latest user message.
        emotion : str
            Detected primary emotion (sadness, anxiety, anger, fear,
            stress, joy, neutral …).
        concern_level : str
            One of ``low``, ``medium``, ``high``, ``critical``.
        emotion_confidence : float
            Model confidence in the detected emotion (0–1).
        history : list | None
            Recent conversation history (list of dicts with ``role`` and
            ``content`` keys).

        Returns
        -------
        str
            A warm, multi-sentence empathetic response.
        """
        emotion = self._normalise_emotion(emotion)
        concern_level = concern_level if concern_level in SUPPORT_PHRASES else "low"

        # Layer 1 — Emotional acknowledgment (always included)
        empathy = self._pick(EMPATHY_PHRASES.get(emotion, EMPATHY_PHRASES["neutral"]))

        # Layer 2 — Supportive statement (always included, scaled by concern)
        support = self._pick(SUPPORT_PHRASES[concern_level])

        parts: list[str] = [empathy, support]

        # For high/critical concern, add a deepener to show extra care
        if concern_level in ("high", "critical"):
            parts.append(self._pick(HIGH_CONCERN_DEEPENERS))

        # Context memory (reference history when available)
        elif history and len(history) >= 4 and emotion not in ("joy", "neutral"):
            parts.append(self._pick(HISTORY_AWARE_PHRASES))

        response = " ".join(parts)

        # Humanisation pass
        response = self._humanise(response)

        # --- Avoid repeating the same response in the last 3 messages ---
        max_regen = 4
        while response in self._recent_responses and max_regen > 0:
            parts_retry: list[str] = [
                self._pick(EMPATHY_PHRASES.get(emotion, EMPATHY_PHRASES["neutral"])),
                self._pick(SUPPORT_PHRASES[concern_level]),
            ]
            response = self._humanise(" ".join(parts_retry))
            max_regen -= 1

        self._recent_responses.append(response)

        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_emotion(emotion: str) -> str:
        """Map raw emotion labels to pool keys."""
        emotion = (emotion or "neutral").lower().strip()
        alias = {
            "happy": "joy",
            "happiness": "joy",
            "worried": "anxiety",
            "nervous": "anxiety",
            "anxious": "anxiety",
            "frustrated": "anger",
            "irritated": "anger",
            "scared": "fear",
            "terrified": "fear",
            "depressed": "sadness",
            "lonely": "sadness",
            "sad": "sadness",
            "stressed": "stress",
            "overwhelmed": "stress",
        }
        return alias.get(emotion, emotion) if emotion not in EMPATHY_PHRASES else emotion

    def _pick(self, pool: list[str]) -> str:
        """Choose a phrase from *pool*, avoiding recent repeats."""
        candidates = [p for p in pool if p not in self._recent_phrases]
        if not candidates:
            # All used recently — reset and pick randomly
            candidates = pool
        choice = random.choice(candidates)
        self._recent_phrases.append(choice)
        return choice

    @staticmethod
    def _humanise(text: str) -> str:
        """Post-process to remove robotic phrasing and soften directives."""
        for robotic in _ROBOTIC_PHRASES:
            if robotic in text:
                text = text.replace(robotic, "It seems like")

        for old, new in _FILLER_SOFTENERS:
            text = text.replace(old, new)

        return text
