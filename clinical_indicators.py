"""
Clinical distress indicator layer for the AI Emotional Wellness Buddy.

Computes clinically *inspired* emotional pattern indicators from recent
interaction history.  These indicators are intended for emotional wellness
monitoring and must **never** be presented as a medical diagnosis.

Indicators computed
-------------------
- sustained_sadness      — sadness probability > threshold for 3+ messages
- anxiety_escalation     — anxiety trend increasing across recent messages
- emotional_volatility   — standard deviation of sentiment polarity
- social_withdrawal      — presence of social withdrawal language signals
- negative_self_perception — presence of negative self-talk signals

Ethical disclaimer
------------------
This module provides emotional pattern insights and is **not** a medical
diagnostic tool.  The indicators should be treated as supportive information
only.

Public API
----------
- ``compute_clinical_indicators(emotion_history)``
- ``compute_emotional_risk(emotion_data, clinical_indicators, pattern_summary)``
- ``DISCLAIMER``
"""

from __future__ import annotations

import statistics
from typing import Any

# ── Disclaimer ────────────────────────────────────────────────────────────
DISCLAIMER = (
    "This system provides emotional pattern insights and is not a medical "
    "diagnostic tool."
)

# ── Thresholds (tunable) ─────────────────────────────────────────────────
_SADNESS_THRESHOLD = 0.6
_SADNESS_MIN_MESSAGES = 3
_ANXIETY_TREND_WINDOW = 5

_WITHDRAWAL_KEYWORDS = frozenset([
    "alone", "isolated", "lonely", "nobody", "no one", "withdrawn",
    "avoiding", "don't want to see", "stay away", "shut myself",
    "don't talk", "hiding", "can't face",
])

_NEGATIVE_SELF_KEYWORDS = frozenset([
    "worthless", "useless", "failure", "hate myself", "ugly",
    "stupid", "burden", "can't do anything", "not good enough",
    "loser", "pathetic", "disgusting", "don't deserve",
])


# ── Helper: extract text signals ─────────────────────────────────────────

def _has_keyword_signals(emotion_history: list[dict], keyword_set: frozenset) -> bool:
    """Return True if any recent message contains a keyword from *keyword_set*."""
    for entry in emotion_history:
        # Support both raw text stored in 'text' and distress_keywords list
        text = ""
        if isinstance(entry.get("text"), str):
            text = entry["text"].lower()
        kw_list = entry.get("distress_keywords", [])
        if isinstance(kw_list, list):
            text += " " + " ".join(kw_list)
        for kw in keyword_set:
            if kw in text:
                return True
    return False


# ── Core indicators ──────────────────────────────────────────────────────

def _sustained_sadness(emotion_history: list[dict]) -> bool:
    """True when sadness probability exceeds threshold for 3+ entries."""
    count = 0
    for entry in emotion_history:
        probs = entry.get("emotion_probabilities", {})
        if probs.get("sadness", 0.0) > _SADNESS_THRESHOLD:
            count += 1
    return count >= _SADNESS_MIN_MESSAGES


def _anxiety_escalation(emotion_history: list[dict]) -> bool:
    """True when anxiety probability is trending upward across the window."""
    window = emotion_history[-_ANXIETY_TREND_WINDOW:]
    if len(window) < 2:
        return False
    values = [e.get("emotion_probabilities", {}).get("anxiety", 0.0) for e in window]
    # Simple check: more increases than decreases
    increases = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
    return increases > len(values) // 2


def _emotional_volatility(emotion_history: list[dict]) -> float:
    """Standard deviation of sentiment polarity across window (0.0–1.0)."""
    polarities = [e.get("polarity", 0.0) for e in emotion_history]
    if len(polarities) < 2:
        return 0.0
    return round(min(1.0, statistics.stdev(polarities)), 4)


def _social_withdrawal(emotion_history: list[dict]) -> bool:
    return _has_keyword_signals(emotion_history, _WITHDRAWAL_KEYWORDS)


def _negative_self_perception(emotion_history: list[dict]) -> bool:
    return _has_keyword_signals(emotion_history, _NEGATIVE_SELF_KEYWORDS)


# ── Public API ───────────────────────────────────────────────────────────

def compute_clinical_indicators(emotion_history: list[dict]) -> dict[str, Any]:
    """Compute all clinical distress indicators from *emotion_history*.

    Parameters
    ----------
    emotion_history:
        A list of emotion_data dicts as returned by
        ``EmotionAnalyzer.classify_emotion()``.

    Returns
    -------
    dict with keys ``sustained_sadness`` (bool), ``anxiety_escalation``
    (bool), ``emotional_volatility`` (float), ``social_withdrawal`` (bool),
    ``negative_self_perception`` (bool), and ``disclaimer`` (str).
    """
    if not emotion_history:
        return {
            "sustained_sadness": False,
            "anxiety_escalation": False,
            "emotional_volatility": 0.0,
            "social_withdrawal": False,
            "negative_self_perception": False,
            "disclaimer": DISCLAIMER,
        }

    return {
        "sustained_sadness": _sustained_sadness(emotion_history),
        "anxiety_escalation": _anxiety_escalation(emotion_history),
        "emotional_volatility": _emotional_volatility(emotion_history),
        "social_withdrawal": _social_withdrawal(emotion_history),
        "negative_self_perception": _negative_self_perception(emotion_history),
        "disclaimer": DISCLAIMER,
    }


# ── Emotional risk index ─────────────────────────────────────────────────

def compute_emotional_risk(
    emotion_data: dict,
    clinical_indicators: dict | None = None,
    pattern_summary: dict | None = None,
) -> dict[str, Any]:
    """Compute a weighted emotional risk index.

    Combines:
    - emotion probabilities (sadness, anxiety)
    - emotional volatility from clinical indicators
    - distress keyword density
    - concern level from emotion_data

    Returns
    -------
    dict with ``risk_score`` (float 0–1) and ``risk_level``
    (``'low'`` | ``'medium'`` | ``'high'`` | ``'critical'``).
    """
    probs = emotion_data.get("emotion_probabilities", {})
    sadness_p = probs.get("sadness", 0.0)
    anxiety_p = probs.get("anxiety", 0.0)

    # Volatility from clinical indicators (default 0)
    ci = clinical_indicators or {}
    volatility = ci.get("emotional_volatility", 0.0)

    # Distress keyword density (normalize to 0–1 range, cap at 1.0)
    distress_kw = emotion_data.get("distress_keywords", [])
    kw_factor = min(1.0, len(distress_kw) / 5.0) if distress_kw else 0.0

    # Weighted combination
    risk_score = (
        0.4 * sadness_p
        + 0.3 * anxiety_p
        + 0.2 * volatility
        + 0.1 * kw_factor
    )

    # Boost when clinical red-flags are active
    if ci.get("sustained_sadness"):
        risk_score = min(1.0, risk_score + 0.10)
    if ci.get("anxiety_escalation"):
        risk_score = min(1.0, risk_score + 0.05)

    risk_score = round(min(1.0, max(0.0, risk_score)), 4)

    if risk_score > 0.7:
        level = "critical"
    elif risk_score > 0.5:
        level = "high"
    elif risk_score > 0.3:
        level = "medium"
    else:
        level = "low"

    return {
        "risk_score": risk_score,
        "risk_level": level,
    }
