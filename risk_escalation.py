"""
Risk escalation detection for the AI Emotional Wellness Buddy.

Provides simple rule-based logic to detect emotional escalation risk from a
sequence of emotion labels and to assign a numeric severity score.

Public API
----------
- ``detect_escalation(emotion_history)`` → bool
- ``escalation_score(emotion_history)`` → float  (0.0 – 1.0)
"""

from __future__ import annotations

# Canonical emotion labels used across the codebase.
_NEGATIVE_EMOTIONS: frozenset[str] = frozenset(
    ["sadness", "anxiety", "fear", "anger", "stress", "crisis"]
)

# Minimum consecutive negative emotions required to trigger escalation.
_MIN_CONSECUTIVE_NEGATIVE = 3

# Default severity assigned to any emotion label not in _SEVERITY.
# Chosen to be mildly negative, acknowledging that an unknown label may still
# carry some emotional weight.
_DEFAULT_SEVERITY = 0.3

# Scoring formula weights (must sum to 1.0).
_MEAN_WEIGHT = 0.4
_RECENCY_WEIGHT = 0.6

# Within the recency component the *last* entry is weighted more heavily.
_RECENCY_LAST_WEIGHT = 0.5
_RECENCY_REST_WEIGHT = 0.5  # distributed evenly across all other entries

# Flat bonus added to the base score when detect_escalation returns True.
_ESCALATION_BONUS = 0.2

# Severity weights for individual emotion labels (higher → more severe).
_SEVERITY: dict[str, float] = {
    "joy": 0.0,
    "neutral": 0.0,
    "stress": 0.4,
    "anxiety": 0.5,
    "anger": 0.5,
    "fear": 0.6,
    "sadness": 0.7,
    "crisis": 1.0,
}

# The classic escalation pathway that should always trigger detection.
_ESCALATION_PATHWAY = ("neutral", "anxiety", "sadness", "crisis")


def _normalise(history: list) -> list[str]:
    """Return a list of lower-cased emotion label strings.

    Each element of *history* may be either a plain ``str`` (an emotion label)
    or a ``dict`` that contains an ``'emotion'`` key.  If the ``'emotion'``
    key is absent or falsy the entry is treated as ``'neutral'`` so that
    missing data does not raise an exception; callers should ensure their data
    is well-formed if they need strict validation.
    """
    result: list[str] = []
    for entry in history:
        if isinstance(entry, dict):
            label = (entry.get("emotion") or "neutral").lower().strip()
        else:
            label = str(entry).lower().strip()
        result.append(label)
    return result


def detect_escalation(emotion_history: list) -> bool:
    """Detect whether an emotion history shows signs of escalation.

    Two rules trigger a ``True`` result:

    1. **Pathway match** – the sequence contains the sub-sequence
       ``neutral → anxiety → sadness → crisis`` (in order, not necessarily
       consecutive).
    2. **Consecutive negatives** – there are 3 or more negative emotions in a
       row anywhere in the history.

    Parameters
    ----------
    emotion_history:
        A list of emotion labels.  Each item may be a plain ``str`` (e.g.
        ``"anxiety"``) or a ``dict`` with an ``'emotion'`` key (e.g.
        ``{"emotion": "anxiety", "confidence": 0.9}``).

    Returns
    -------
    bool
        ``True`` if the history is escalating, ``False`` otherwise.
    """
    labels = _normalise(emotion_history)
    if not labels:
        return False

    # Rule 1: pathway sub-sequence match.
    pathway = list(_ESCALATION_PATHWAY)
    idx = 0
    for label in labels:
        if idx < len(pathway) and label == pathway[idx]:
            idx += 1
        if idx == len(pathway):
            return True

    # Rule 2: 3+ consecutive negative emotions.
    consecutive = 0
    for label in labels:
        if label in _NEGATIVE_EMOTIONS:
            consecutive += 1
            if consecutive >= _MIN_CONSECUTIVE_NEGATIVE:
                return True
        else:
            consecutive = 0

    return False


def escalation_score(emotion_history: list) -> float:
    """Compute a numeric escalation severity score between 0.0 and 1.0.

    The score combines three signals:

    * **Mean severity** of all emotions in the history.
    * **Recency bias** – the most recent emotion is weighted more heavily.
    * **Escalation flag** – a fixed bonus when :func:`detect_escalation`
      returns ``True``.

    Parameters
    ----------
    emotion_history:
        Same format as :func:`detect_escalation`.

    Returns
    -------
    float
        A value in ``[0.0, 1.0]`` where 0.0 means no concern and 1.0 means
        maximum escalation risk.
    """
    labels = _normalise(emotion_history)
    if not labels:
        return 0.0

    severities = [_SEVERITY.get(label, _DEFAULT_SEVERITY) for label in labels]

    # Mean severity across all entries.
    mean_sev = sum(severities) / len(severities)

    # Recency bias: weight the last entry at 50 %, rest split evenly.
    if len(labels) == 1:
        recency_sev = severities[-1]
    else:
        rest_weight = _RECENCY_REST_WEIGHT / (len(severities) - 1)
        recency_sev = severities[-1] * _RECENCY_LAST_WEIGHT + sum(
            s * rest_weight for s in severities[:-1]
        )

    # Blend mean and recency signals.
    base_score = _MEAN_WEIGHT * mean_sev + _RECENCY_WEIGHT * recency_sev

    # Escalation bonus.
    if detect_escalation(emotion_history):
        base_score = min(1.0, base_score + _ESCALATION_BONUS)

    return round(min(1.0, max(0.0, base_score)), 4)
