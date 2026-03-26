"""Emotion inference service.

Wraps the existing hybrid-model stack (EmotionAnalyzer) and adds:
- Confidence calibration check
- Safety / crisis escalation gate
- Retry logic with exponential back-off for model loading
- Structured logging of every prediction
"""

from __future__ import annotations

import logging
import sys
import time

from app.config import get_settings
from app.schemas.emotion import EmotionScore, PredictResponse
from app.utils import find_project_root

# ------------------------------------------------------------------ #
# Add the AI core (project root) to sys.path once at import time.
# The actual heavy imports (TextBlob, torch) are deferred until first
# use so that loading this module in tests does not require the full
# ML stack to be installed.
# ------------------------------------------------------------------ #
_root = find_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

settings = get_settings()
logger = logging.getLogger(__name__)

# Module-level singleton — loaded once per worker process.
_analyzer = None  # type: ignore[var-annotated]

_MAX_RETRIES = 3
_RETRY_DELAY_S = 2.0  # seconds between retries (doubles each attempt)


def _get_analyzer():
    """Lazily import and initialise EmotionAnalyzer on first use.

    Retries up to ``_MAX_RETRIES`` times with exponential back-off so that
    transient I/O errors during model loading do not crash the worker.
    """
    global _analyzer
    if _analyzer is not None:
        return _analyzer

    delay = _RETRY_DELAY_S
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            logger.info("Loading EmotionAnalyzer (attempt %d/%d)…", attempt, _MAX_RETRIES)
            from emotion_analyzer import EmotionAnalyzer  # noqa: PLC0415
            _analyzer = EmotionAnalyzer()
            logger.info("EmotionAnalyzer loaded successfully.")
            return _analyzer
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            logger.warning(
                "EmotionAnalyzer load attempt %d/%d failed: %s",
                attempt, _MAX_RETRIES, exc,
            )
            if attempt < _MAX_RETRIES:
                time.sleep(delay)
                delay *= 2

    logger.error("EmotionAnalyzer failed to load after %d attempts; using fallback.", _MAX_RETRIES)
    raise RuntimeError("EmotionAnalyzer unavailable") from last_exc


def predict(text: str) -> PredictResponse:
    """Run the hybrid emotion pipeline and return a structured response.

    Falls back gracefully if the analyzer is unavailable or times out.
    A simple keyword-based fallback is used in those cases.
    """
    try:
        analyzer = _get_analyzer()
    except RuntimeError:
        logger.warning("Analyzer unavailable — using keyword fallback for prediction.")
        return _build_response(_fallback_result(text))

    # Per-call timeout: if classification takes longer than 30 s something
    # is badly wrong; return the fallback rather than stalling the request.
    import signal

    def _timeout_handler(signum, frame):
        raise TimeoutError("EmotionAnalyzer.classify_emotion timed out")

    # SIGALRM is Unix-only; skip timeout on Windows.
    _use_alarm = hasattr(signal, "SIGALRM")
    if _use_alarm:
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(30)
    try:
        result = analyzer.classify_emotion(text)
    except TimeoutError:
        logger.warning("classify_emotion timed out; using fallback")
        result = _fallback_result(text)
    except Exception:
        logger.exception("EmotionAnalyzer.classify_emotion failed; falling back")
        result = _fallback_result(text)
    finally:
        if _use_alarm:
            signal.alarm(0)  # cancel any pending alarm

    return _build_response(result)


def _build_response(result: dict) -> PredictResponse:
    """Convert a raw classify_emotion dict into a PredictResponse."""
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
        len(result.get("_text", "")),
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
        return {
            "emotion": "crisis",
            "confidence_score": 0.9,
            "uncertainty_score": 0.1,
            "is_uncertain": False,
            "final_probabilities": {"crisis": 0.9, "neutral": 0.1},
        }
    if any(w in text_lower for w in ("sad", "depress", "cry", "hopeless")):
        return {
            "emotion": "sadness",
            "confidence_score": 0.7,
            "uncertainty_score": 0.3,
            "is_uncertain": False,
            "final_probabilities": {"sadness": 0.7, "neutral": 0.3},
        }
    return {
        "emotion": "neutral",
        "confidence_score": 0.5,
        "uncertainty_score": 0.5,
        "is_uncertain": True,
        "final_probabilities": {"neutral": 1.0},
    }
