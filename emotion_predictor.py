"""
Lightweight rule-based emotion predictor. No external dependencies.

Public API
----------
- ``predict_next_emotion(emotion_history)`` — predict the next emotion
- ``detect_trend(emotion_history)``         — classify the recent trend
"""

from __future__ import annotations

from collections import Counter
from typing import List

# Emotions considered stressful / negative (used for trend detection)
_STRESS_EMOTIONS = frozenset(["sadness", "anxiety", "fear", "anger", "stress", "crisis"])
# Emotions considered positive
_POSITIVE_EMOTIONS = frozenset(["joy", "neutral", "calm", "happiness"])


def predict_next_emotion(emotion_history: List[str]) -> str:
    """Return the predicted next emotion based on recent history.

    Rules (applied in order):
    1. If the last two emotions are identical, return that emotion.
    2. Otherwise, return the most frequent emotion in the history.
    3. If the history is empty, return ``"neutral"``.

    Parameters
    ----------
    emotion_history:
        Ordered list of emotion labels (most recent last).
        Typically the last 5 emotions are passed in.
    """
    if not emotion_history:
        return "neutral"

    # Rule 1: repeating last-two trend
    if len(emotion_history) >= 2 and emotion_history[-1] == emotion_history[-2]:
        return emotion_history[-1]

    # Rule 2: most common emotion
    return Counter(emotion_history).most_common(1)[0][0]


def detect_trend(emotion_history: List[str]) -> str:
    """Classify the recent emotional trend using the last 3 emotions.

    Examines the last 3 emotions (or fewer if less history is available)
    and compares the count of stress-category vs positive-category emotions.
    Emotions not in either category are treated as neutral (neither add to
    stress nor positive counts), which defaults the result toward "stable".

    Returns one of:
    - ``"increasing stress"`` — recent window dominated by negative emotions.
    - ``"improving"``         — recent window dominated by positive emotions.
    - ``"stable"``            — no clear shift, tied counts, or unknown emotions.

    Parameters
    ----------
    emotion_history:
        Ordered list of emotion labels (most recent last).
    """
    if not emotion_history:
        return "stable"

    window = emotion_history[-3:] if len(emotion_history) >= 3 else emotion_history
    stress_count = sum(1 for e in window if e in _STRESS_EMOTIONS)
    positive_count = sum(1 for e in window if e in _POSITIVE_EMOTIONS)
    majority = len(window) // 2 + 1

    if stress_count > positive_count and stress_count >= majority:
        return "increasing stress"
    if positive_count > stress_count and positive_count >= majority:
        return "improving"
    return "stable"
