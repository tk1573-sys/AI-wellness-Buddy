"""
Lightweight rule-based emotion predictor. No external dependencies.

Public API
----------
- ``predict_next_emotion(emotion_history)`` — predict the next emotion
- ``detect_trend(emotion_history)``         — classify the recent trend
- ``hybrid_predict(transformer_scores, keyword_scores)`` — fuse transformer
  and keyword probability distributions into a single normalised prediction
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List

# Emotions considered stressful / negative (used for trend detection)
_STRESS_EMOTIONS = frozenset(["sadness", "anxiety", "fear", "anger", "stress", "crisis"])
# Emotions considered positive
_POSITIVE_EMOTIONS = frozenset(["joy", "neutral", "calm", "happiness"])

# ---------------------------------------------------------------------------
# Hybrid fusion constants
# ---------------------------------------------------------------------------

# Blend weights for transformer vs keyword scores (must sum to 1.0)
_TRANSFORMER_WEIGHT: float = 0.7
_KEYWORD_WEIGHT: float = 0.3

# When the top keyword emotion exceeds this confidence the keyword result
# overrides the transformer prediction entirely.
_KEYWORD_OVERRIDE_THRESHOLD: float = 0.8

# Multiplicative boost applied to minority emotion classes after blending.
# These emotions are under-represented in most training corpora, so a small
# boost improves their recall without dramatically shifting precision.
_MINORITY_CLASS_BOOST: Dict[str, float] = {
    "fear":    1.20,
    "anxiety": 1.15,
    "crisis":  1.30,
}

# Number of decimal places used when rounding normalised scores.
_SCORE_PRECISION: int = 4


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


# ---------------------------------------------------------------------------
# Hybrid fusion
# ---------------------------------------------------------------------------

def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Return *scores* re-scaled so all values sum to 1.0.

    If the total is zero a uniform distribution over all keys is returned.
    If *scores* is empty an empty dict is returned.
    """
    if not scores:
        return {}
    total = sum(scores.values())
    if total <= 0:
        n = len(scores)
        return {k: round(1.0 / n, _SCORE_PRECISION) for k in scores}
    return {k: round(v / total, _SCORE_PRECISION) for k, v in scores.items()}


def hybrid_predict(
    transformer_scores: Dict[str, float],
    keyword_scores: Dict[str, float],
) -> Dict[str, float]:
    """Fuse transformer and keyword probability distributions.

    Algorithm
    ---------
    1. **Keyword override** – if the highest-confidence keyword emotion exceeds
       :data:`_KEYWORD_OVERRIDE_THRESHOLD` (0.8), the keyword distribution is
       used directly (after normalisation) because the explicit signal is
       considered highly reliable.
    2. **Weighted blend** – otherwise the two distributions are combined::

           final_score[e] = 0.7 * transformer[e] + 0.3 * keyword[e]

    3. **Minority-class boost** – emotions that are systematically
       under-represented in common training corpora (``fear``, ``anxiety``,
       ``crisis``) receive a small multiplicative boost
       (see :data:`_MINORITY_CLASS_BOOST`) to improve recall for these classes.
    4. **Normalisation** – the resulting scores are re-normalised to sum to 1.0.

    Parameters
    ----------
    transformer_scores:
        Probability distribution returned by the transformer model.
        Keys are emotion labels; values are non-negative floats.
    keyword_scores:
        Probability distribution from the keyword/heuristic classifier.
        Keys are emotion labels; values are non-negative floats.

    Returns
    -------
    dict[str, float]
        Fused, normalised probability distribution over all emotion labels
        present in either input distribution.
    """
    if not transformer_scores and not keyword_scores:
        return {}

    # ------------------------------------------------------------------
    # Step 1: keyword override when confidence is very high
    # ------------------------------------------------------------------
    if keyword_scores:
        top_keyword_emotion = max(keyword_scores, key=lambda k: keyword_scores[k])
        if keyword_scores[top_keyword_emotion] > _KEYWORD_OVERRIDE_THRESHOLD:
            # Merge all labels (keep transformer keys at 0 if absent)
            merged: Dict[str, float] = {k: 0.0 for k in transformer_scores}
            merged.update(keyword_scores)
            return _normalize_scores(merged)

    # ------------------------------------------------------------------
    # Step 2: weighted blend
    # ------------------------------------------------------------------
    all_labels = set(transformer_scores) | set(keyword_scores)
    merged = {}
    for label in all_labels:
        t_val = transformer_scores.get(label, 0.0)
        k_val = keyword_scores.get(label, 0.0)
        merged[label] = _TRANSFORMER_WEIGHT * t_val + _KEYWORD_WEIGHT * k_val

    # ------------------------------------------------------------------
    # Step 3: minority-class boost (improves recall for rare emotions)
    # ------------------------------------------------------------------
    for label, boost in _MINORITY_CLASS_BOOST.items():
        if label in merged:
            merged[label] *= boost

    # ------------------------------------------------------------------
    # Step 4: normalise
    # ------------------------------------------------------------------
    return _normalize_scores(merged)
