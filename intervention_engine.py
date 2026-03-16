"""
Rule-based intervention decision engine for the AI Emotional Wellness Buddy.

Maps risk levels and clinical indicators to personalised coping interventions.

Decision logic
--------------
- **Low risk**      → normal empathetic response
- **Moderate risk** → grounding suggestion
- **High risk**     → breathing exercise + supportive message
- **Critical risk** → crisis resources + hotline information

The engine is stateless and safe for concurrent use.

Public API
----------
- ``InterventionEngine``
- ``InterventionEngine.recommend(risk_level, primary_emotion, clinical_indicators)``
"""

from __future__ import annotations

from typing import Any


# ── Crisis resources ─────────────────────────────────────────────────────

_CRISIS_RESOURCES = {
    "hotline": "988 Suicide & Crisis Lifeline — call or text 988 (24/7)",
    "text_line": "Crisis Text Line — text HOME to 741741",
    "emergency": "Emergency services — call 911",
}

# ── Grounding prompts ────────────────────────────────────────────────────

_GROUNDING_PROMPTS = [
    "Let's try a grounding exercise: name 5 things you can see, "
    "4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
    "Take a moment to feel your feet on the ground. "
    "Notice the texture beneath you and take three slow breaths.",
]

# ── Breathing instructions ───────────────────────────────────────────────

_BREATHING_INSTRUCTIONS = (
    "Let's try a calming breathing exercise together: "
    "breathe in slowly for 4 seconds, hold for 4 seconds, "
    "then breathe out gently for 6 seconds. Repeat three times."
)

_SUPPORTIVE_MESSAGE = (
    "You're doing something brave by sharing how you feel. "
    "I'm here with you, and we'll take this one step at a time."
)

# ── Coping tool catalogue ────────────────────────────────────────────────

_COPING_TOOLS = {
    "breathing_exercise": {
        "name": "Breathing Exercise",
        "description": _BREATHING_INSTRUCTIONS,
    },
    "grounding_exercise": {
        "name": "Grounding Exercise",
        "description": _GROUNDING_PROMPTS[0],
    },
    "calming_prompt": {
        "name": "Calming Prompt",
        "description": (
            "Close your eyes for a moment. Picture a place where you feel "
            "completely safe and at peace. Stay there for a few breaths."
        ),
    },
}


class InterventionEngine:
    """Decide which coping interventions to recommend based on risk level.

    Usage::

        engine = InterventionEngine()
        result = engine.recommend("high", "anxiety", clinical_indicators)
    """

    def recommend(
        self,
        risk_level: str,
        primary_emotion: str = "neutral",
        clinical_indicators: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return recommended interventions for the current risk state.

        Parameters
        ----------
        risk_level:
            One of ``'low'``, ``'moderate'`` / ``'medium'``, ``'high'``,
            ``'critical'``.
        primary_emotion:
            The detected primary emotion label.
        clinical_indicators:
            Output from ``compute_clinical_indicators()``, or *None*.

        Returns
        -------
        dict with keys ``level``, ``actions`` (list of str),
        ``coping_tools`` (list of tool dicts), ``resources`` (dict or None),
        and ``supportive_message`` (str or None).
        """
        risk_level = (risk_level or "low").lower()
        # Normalise synonyms
        if risk_level == "medium":
            risk_level = "moderate"

        ci = clinical_indicators or {}

        if risk_level == "critical" or primary_emotion == "crisis":
            return self._critical_intervention(ci)
        if risk_level == "high":
            return self._high_intervention(primary_emotion, ci)
        if risk_level == "moderate":
            return self._moderate_intervention(primary_emotion, ci)
        return self._low_intervention()

    # ── Private builders ─────────────────────────────────────────────

    @staticmethod
    def _low_intervention() -> dict[str, Any]:
        return {
            "level": "low",
            "actions": ["empathetic_response"],
            "coping_tools": [],
            "resources": None,
            "supportive_message": None,
        }

    @staticmethod
    def _moderate_intervention(
        emotion: str,
        ci: dict,
    ) -> dict[str, Any]:
        tools = [_COPING_TOOLS["grounding_exercise"]]
        actions = ["empathetic_response", "grounding_suggestion"]
        if ci.get("anxiety_escalation"):
            tools.append(_COPING_TOOLS["calming_prompt"])
            actions.append("calming_prompt")
        return {
            "level": "moderate",
            "actions": actions,
            "coping_tools": tools,
            "resources": None,
            "supportive_message": None,
        }

    @staticmethod
    def _high_intervention(
        emotion: str,
        ci: dict,
    ) -> dict[str, Any]:
        tools = [
            _COPING_TOOLS["breathing_exercise"],
            _COPING_TOOLS["grounding_exercise"],
        ]
        actions = ["empathetic_response", "breathing_exercise", "supportive_message"]
        if ci.get("social_withdrawal"):
            actions.append("connection_suggestion")
        return {
            "level": "high",
            "actions": actions,
            "coping_tools": tools,
            "resources": None,
            "supportive_message": _SUPPORTIVE_MESSAGE,
        }

    @staticmethod
    def _critical_intervention(ci: dict) -> dict[str, Any]:
        return {
            "level": "critical",
            "actions": ["crisis_response", "safety_resources"],
            "coping_tools": [],
            "resources": dict(_CRISIS_RESOURCES),
            "supportive_message": (
                "Your safety matters most right now. "
                "Please reach out to one of these resources — "
                "trained professionals are available 24/7."
            ),
        }
