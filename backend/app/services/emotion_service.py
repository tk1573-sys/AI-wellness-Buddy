"""Emotion inference service.

Wraps the existing hybrid-model stack (EmotionAnalyzer) and adds:
- Confidence calibration check
- Safety / crisis escalation gate
- Structured logging of every prediction
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.config import get_settings
from app.schemas.emotion import EmotionScore, PredictResponse

# ------------------------------------------------------------------ #
# Allow importing the AI modules that live in the project root.
# The actual import is deferred until first use so that starting the
# app (or importing this module in tests) doesn't require TextBlob /
# torch to be installed up-front.
# ------------------------------------------------------------------ #
_ROOT = Path(__file__).resolve().parents[4]  # repo root
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

settings = get_settings()
logger = logging.getLogger(__name__)

# Module-level singleton — loaded once per worker process.
_analyzer = None  # type: ignore[var-annotated]


def _get_analyzer():
    """Lazily import and initialise EmotionAnalyzer on first use."""
    global _analyzer
    if _analyzer is None:
        logger.info("Loading EmotionAnalyzer (first request in this worker)…")
        from emotion_analyzer import EmotionAnalyzer  # noqa: PLC0415
        _analyzer = EmotionAnalyzer()
    return _analyzer


# --------------------------------------------------------------------------- #
# Public interface
# --------------------------------------------------------------------------- #

def predict(text: str) -> PredictResponse:
    """Run the hybrid emotion pipeline and return a structured response."""
    analyzer = _get_analyzer()

    try:
        result = analyzer.classify_emotion(text)
    except Exception:
        logger.exception("EmotionAnalyzer.classify_emotion failed; falling back")
        result = _fallback_result(text)

    primary = result.get("emotion", "neutral")
    confidence = float(result.get("confidence_score", 0.5))
    uncertainty = float(result.get("uncertainty_score", 0.5))
    is_uncertain = bool(result.get("is_uncertain", False))

    # Build ranked score list from final_probabilities or confidence_distribution
    raw_scores: dict[str, float] = (
        result.get("final_probabilities")
        or result.get("confidence_distribution")
        or {}
    )
    scores = [
        EmotionScore(emotion=e, score=round(s, 4))
        for e, s in sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # Safety gate: flag if crisis emotion is above threshold
    crisis_score = raw_scores.get("crisis", 0.0)
    is_high_risk = crisis_score >= settings.CRISIS_CONFIDENCE_THRESHOLD or primary == "crisis"

    escalation_message = settings.HIGH_RISK_ESCALATION_MESSAGE if is_high_risk else None

    explanation = result.get("explanation") or result.get("explanation_text")

    logger.info(
        "predict text_len=%d emotion=%s confidence=%.3f is_high_risk=%s",
        len(text),
        primary,
        confidence,
        is_high_risk,
    )

    return PredictResponse(
        primary_emotion=primary,
        confidence=round(confidence, 4),
        uncertainty=round(uncertainty, 4),
        is_uncertain=is_uncertain,
        is_high_risk=is_high_risk,
        escalation_message=escalation_message,
        scores=scores,
        explanation=explanation,
    )


def _fallback_result(text: str) -> dict:
    """Minimal keyword-only fallback when the transformer stack is unavailable."""
    text_lower = text.lower()
    if any(w in text_lower for w in ("crisis", "suicid", "harm", "end my life")):
        return {"emotion": "crisis", "confidence_score": 0.9, "uncertainty_score": 0.1,
                "is_uncertain": False, "final_probabilities": {"crisis": 0.9, "neutral": 0.1}}
    if any(w in text_lower for w in ("sad", "depress", "cry", "hopeless")):
        return {"emotion": "sadness", "confidence_score": 0.7, "uncertainty_score": 0.3,
                "is_uncertain": False, "final_probabilities": {"sadness": 0.7, "neutral": 0.3}}
    return {"emotion": "neutral", "confidence_score": 0.5, "uncertainty_score": 0.5,
            "is_uncertain": True, "final_probabilities": {"neutral": 1.0}}
