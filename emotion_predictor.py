"""
Lightweight rule-based emotion predictor. No external dependencies.

Public API
----------
- ``predict_next_emotion(emotion_history)`` — predict the next emotion
- ``detect_trend(emotion_history)``         — classify the recent trend
- ``hybrid_predict(transformer_scores, keyword_scores)`` — fuse transformer
  and keyword probability distributions into a single normalised prediction
  using the explicit equation:

      P_final = α · P_transformer + (1 − α) · P_keyword

  where α is computed dynamically from the transformer's normalised Shannon
  entropy so that a less-certain transformer cedes more weight to the
  keyword model.

Helper functions (module-private)
----------------------------------
- ``_compute_entropy(scores)``       — normalised Shannon entropy H ∈ [0, 1]
- ``_compute_alpha_dynamic(scores)`` — entropy-adjusted fusion weight α
- ``_normalize_scores(scores)``      — re-scale scores to sum to 1.0
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List, Union

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

# Dynamic alpha range.
# α = _ALPHA_MAX when transformer entropy is 0 (fully confident).
# α = _ALPHA_MIN when transformer entropy is 1 (maximally uncertain).
# Linear interpolation: α = _ALPHA_MAX·(1−H_t) + _ALPHA_MIN·H_t
_ALPHA_MAX: float = _TRANSFORMER_WEIGHT   # upper bound of dynamic α = 0.7
_ALPHA_MIN: float = 0.3                   # lower bound of dynamic α

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

def _compute_entropy(scores: Dict[str, float]) -> float:
    """Return the normalised Shannon entropy H ∈ [0, 1] of *scores*.

    Entropy is normalised by log(n) so that a uniform distribution over *n*
    classes gives H = 1.0 and a degenerate (one-hot) distribution gives
    H = 0.0.  An empty or zero-total *scores* dict returns 1.0 (maximum
    uncertainty).

    Parameters
    ----------
    scores:
        Non-negative real-valued distribution (need not sum to 1.0).

    Returns
    -------
    float
        Normalised entropy in [0, 1].
    """
    total = sum(scores.values())
    if total <= 0 or not scores:
        return 1.0
    n = len(scores)
    # Single-class distribution has zero entropy by definition (no uncertainty).
    if n == 1:
        return 0.0
    max_entropy = math.log(n)
    raw_entropy = -sum(
        (v / total) * math.log(v / total) for v in scores.values() if v > 0
    )
    return round(min(1.0, max(0.0, raw_entropy / max_entropy)), 4)


def _compute_alpha_dynamic(transformer_scores: Dict[str, float]) -> float:
    r"""Compute an entropy-adjusted fusion weight α for the transformer.

    The weight is linearly interpolated between *_ALPHA_MAX* (when the
    transformer is fully confident, H_t = 0) and *_ALPHA_MIN* (when the
    transformer is maximally uncertain, H_t = 1):

    .. math::

        \alpha = \alpha_{\max} \cdot (1 - H_t) + \alpha_{\min} \cdot H_t

    This ensures the transformer's contribution decreases gracefully as its
    output distribution becomes less informative, allowing the keyword model
    to compensate when the neural component is uncertain.

    Parameters
    ----------
    transformer_scores:
        Raw transformer probability distribution (keys are emotion labels).

    Returns
    -------
    float
        Dynamic weight α ∈ [_ALPHA_MIN, _ALPHA_MAX].
    """
    H_t = _compute_entropy(transformer_scores)
    return round(_ALPHA_MAX * (1.0 - H_t) + _ALPHA_MIN * H_t, 4)


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
    *,
    mode: str = "hybrid",
    return_intermediates: bool = False,
) -> Union[Dict[str, float], Dict[str, object]]:
    """Fuse transformer and keyword probability distributions.

    Fusion equation (hybrid mode)
    ------------------------------
    .. math::

        P_{\\text{final}}[e] = \\alpha \\cdot P_t[e] + (1 - \\alpha) \\cdot P_k[e]

    where α is computed dynamically from the normalised Shannon entropy of
    the transformer output (see :func:`_compute_alpha_dynamic`), and both
    inputs are normalised (calibrated) to proper probability distributions
    before fusion.

    Algorithm
    ---------
    0. **Calibration** – normalise both *transformer_scores* (P_t) and
       *keyword_scores* (P_k) so that each sums to 1.0 before fusion.
    1. **Keyword override** – if the highest-confidence keyword emotion exceeds
       :data:`_KEYWORD_OVERRIDE_THRESHOLD` (0.8), the keyword distribution is
       used directly because the explicit signal is considered highly reliable.
    2. **Dynamic alpha** – compute α from the transformer's normalised entropy
       so that a more uncertain transformer cedes weight to the keyword model.
    3. **Weighted blend** – apply the fusion equation::

           P_final[e] = α · P_t[e] + (1 − α) · P_k[e]

    4. **Minority-class boost** – emotions that are systematically
       under-represented in common training corpora (``fear``, ``anxiety``,
       ``crisis``) receive a small multiplicative boost
       (see :data:`_MINORITY_CLASS_BOOST`) to improve recall.
    5. **Normalisation** – the resulting scores are re-normalised to sum to 1.0.

    Ablation study support
    ----------------------
    Set *mode* to one of:

    - ``"hybrid"`` (default) – full dynamic-alpha fusion as above.
    - ``"transformer_only"`` – use P_t directly (α = 1.0), bypassing keywords.
    - ``"keyword_only"`` – use P_k directly (α = 0.0), bypassing the
      transformer.

    Parameters
    ----------
    transformer_scores:
        Probability distribution returned by the transformer model.
        Keys are emotion labels; values are non-negative floats.
    keyword_scores:
        Probability distribution from the keyword/heuristic classifier.
        Keys are emotion labels; values are non-negative floats.
    mode:
        Fusion mode for ablation study support.  One of ``"hybrid"``,
        ``"transformer_only"``, or ``"keyword_only"``.  Defaults to
        ``"hybrid"``.
    return_intermediates:
        When ``True``, return a dict containing the intermediate probability
        distributions ``pk``, ``pt``, the dynamic weight ``alpha``, and the
        ``final_probabilities`` instead of just the fused distribution.

    Returns
    -------
    dict[str, float] or dict[str, object]
        When *return_intermediates* is ``False`` (default): fused, normalised
        probability distribution over all emotion labels.
        When *return_intermediates* is ``True``: a dict with keys ``pk``,
        ``pt``, ``alpha``, and ``final_probabilities``.
    """
    if not transformer_scores and not keyword_scores:
        if return_intermediates:
            return {"pk": {}, "pt": {}, "alpha": None, "final_probabilities": {}}
        return {}

    # ------------------------------------------------------------------
    # Step 0: Calibration — normalise both inputs before fusion
    # ------------------------------------------------------------------
    pt: Dict[str, float] = _normalize_scores(transformer_scores) if transformer_scores else {}
    pk: Dict[str, float] = _normalize_scores(keyword_scores) if keyword_scores else {}

    # ------------------------------------------------------------------
    # Ablation modes
    # ------------------------------------------------------------------
    if mode == "transformer_only":
        final = pt if pt else pk
        if return_intermediates:
            return {"pk": pk, "pt": pt, "alpha": 1.0, "final_probabilities": final}
        return final

    if mode == "keyword_only":
        final = pk if pk else pt
        if return_intermediates:
            return {"pk": pk, "pt": pt, "alpha": 0.0, "final_probabilities": final}
        return final

    # ------------------------------------------------------------------
    # Step 1: keyword override when confidence is very high
    # ------------------------------------------------------------------
    if pk:
        top_keyword_emotion = max(pk, key=lambda k: pk[k])
        if pk[top_keyword_emotion] > _KEYWORD_OVERRIDE_THRESHOLD:
            merged: Dict[str, float] = {k: 0.0 for k in pt}
            merged.update(pk)
            final = _normalize_scores(merged)
            if return_intermediates:
                return {"pk": pk, "pt": pt, "alpha": 0.0, "final_probabilities": final}
            return final

    # ------------------------------------------------------------------
    # Step 2: dynamic alpha based on transformer entropy
    # ------------------------------------------------------------------
    # When pt is empty (transformer unavailable), rely fully on pk (alpha = 0.0).
    alpha = _compute_alpha_dynamic(pt) if pt else 0.0

    # ------------------------------------------------------------------
    # Step 3: weighted blend — P_final = α·P_t + (1−α)·P_k
    # ------------------------------------------------------------------
    all_labels = set(pt) | set(pk)
    merged = {}
    for label in all_labels:
        t_val = pt.get(label, 0.0)
        k_val = pk.get(label, 0.0)
        merged[label] = alpha * t_val + (1.0 - alpha) * k_val

    # ------------------------------------------------------------------
    # Step 4: minority-class boost (improves recall for rare emotions)
    # ------------------------------------------------------------------
    for label, boost in _MINORITY_CLASS_BOOST.items():
        if label in merged:
            merged[label] *= boost

    # ------------------------------------------------------------------
    # Step 5: normalise
    # ------------------------------------------------------------------
    final = _normalize_scores(merged)

    if return_intermediates:
        return {"pk": pk, "pt": pt, "alpha": alpha, "final_probabilities": final}
    return final
