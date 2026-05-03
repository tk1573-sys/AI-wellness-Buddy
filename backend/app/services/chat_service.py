"""Chat service: maintains conversation context and persists history."""

from __future__ import annotations

import asyncio
import logging
import secrets
import sys
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatHistory
from app.models.emotion import EmotionLog
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.emotion_service import predict
from app.utils import find_project_root

# Add the AI core (project root) to sys.path once.
_root = find_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

logger = logging.getLogger(__name__)

# Per-process pipeline registry (same isolation strategy as the original
# api_service.py, but now keyed by database user_id instead of arbitrary str).
_pipelines: dict[int, object] = {}

_RECENT_EMOTION_LIMIT = 20

# Minimum personalization score for a response to be classified as "personalized".
# A score of 0.4 requires at least a loaded profile (+0.30) plus some emotional
# history (+0.30) or a partial trigger match, ensuring generic fallbacks are
# clearly separated from profile-driven responses.
_PERSONALIZATION_THRESHOLD = 0.4


def _get_pipeline(user_id: int):
    """Lazily initialise a WellnessAgentPipeline for the given user.

    Returns ``None`` (and logs a warning) if the pipeline cannot be
    constructed due to insufficient memory or a missing dependency so
    that callers can use the inline fallback response instead.
    """
    if user_id not in _pipelines:
        try:
            from agent_pipeline import WellnessAgentPipeline  # noqa: PLC0415
            _pipelines[user_id] = WellnessAgentPipeline()
        except (ImportError, MemoryError, OSError, RuntimeError):
            logger.warning(
                "WellnessAgentPipeline init failed for user_id=%d "
                "(possible OOM or missing dependency); using inline fallback.",
                user_id,
                exc_info=True,
            )
            return None
    return _pipelines[user_id]


async def _load_profile_context(db: AsyncSession, user_id: int) -> dict:
    """Load the user profile and return a context dict for the pipeline."""
    from app.models.profile import UserProfile  # noqa: PLC0415

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return {}

    ctx: dict = {}
    if profile.age:
        ctx["age"] = profile.age
    if profile.gender:
        ctx["gender"] = profile.gender
    if profile.occupation:
        ctx["occupation"] = profile.occupation
    if profile.stress_level:
        ctx["stress_level"] = profile.stress_level
    if profile.sleep_pattern:
        ctx["sleep_pattern"] = profile.sleep_pattern
    if profile.triggers:
        ctx["triggers"] = profile.triggers
    if profile.personality_type:
        ctx["personality_type"] = profile.personality_type
    if profile.baseline_emotion:
        ctx["baseline_emotion"] = profile.baseline_emotion
    if profile.language_preference:
        ctx["language_preference"] = profile.language_preference
    return ctx


async def _load_recent_emotions(db: AsyncSession, user_id: int) -> list[str]:
    """Return the last N primary emotions for the user."""
    result = await db.execute(
        select(EmotionLog.primary_emotion)
        .where(EmotionLog.user_id == user_id)
        .order_by(EmotionLog.created_at.desc())
        .limit(_RECENT_EMOTION_LIMIT)
    )
    emotions = [row[0] for row in result.fetchall()]
    return list(reversed(emotions))


def _build_personalized_context(
    user_id: int,
    profile_ctx: dict,
    recent_emotions: list[str],
    matched_triggers: list[str] | None = None,
) -> dict:
    """Merge profile and emotion history into a pipeline context dict."""
    ctx: dict = {"user_name": str(user_id)}
    ctx.update(profile_ctx)

    if recent_emotions:
        ctx["recent_emotions"] = recent_emotions
        # Detect escalation: 3+ consecutive negatives
        NEGATIVE = {"sadness", "anger", "fear", "anxiety", "crisis", "stress"}
        consec = 0
        for e in reversed(recent_emotions):
            if e in NEGATIVE:
                consec += 1
            else:
                break
        ctx["consecutive_negatives"] = consec
        ctx["escalation_risk"] = consec >= 3

    # Inject empathetic trigger context so the pipeline can adjust tone
    if matched_triggers:
        ctx["active_triggers"] = matched_triggers
        ctx["trigger_empathy_hint"] = (
            "The user mentioned personal stressors they have previously identified "
            f"({', '.join(matched_triggers)}). Respond with extra empathy and "
            "acknowledge their specific challenges."
        )

    return ctx


def _match_triggers(message: str, triggers: dict | None) -> list[str]:
    """Return the subset of active trigger keys that appear in *message*.

    Only triggers whose value is truthy are considered active.  The check is
    case-insensitive and matches whole or partial words (e.g. "work" matches
    "overwork").
    """
    if not triggers:
        return []

    msg_lower = message.lower()
    matched: list[str] = []
    for key, active in triggers.items():
        if active and key.lower() in msg_lower:
            matched.append(key)
    return matched


def _compute_personalization_score(
    profile_ctx: dict,
    matched_triggers: list[str],
    recent_emotions: list[str],
) -> float:
    """Compute a [0, 1] personalization score.

    Breakdown:
    - +0.30 if a non-empty profile is loaded
    - +0.40 weighted by trigger match rate (matched / total active triggers)
    - +0.30 if emotional history is available
    """
    score = 0.0

    if profile_ctx:
        score += 0.30

    if profile_ctx.get("triggers"):
        active = [k for k, v in profile_ctx["triggers"].items() if v]
        if active:
            hit_rate = len(matched_triggers) / len(active)
            score += 0.40 * hit_rate

    if recent_emotions:
        score += 0.30

    return round(min(score, 1.0), 4)


async def _maybe_dispatch_crisis_alert(
    db: AsyncSession,
    user_id: int,
    primary_emotion: str,
    message_text: str,
) -> None:
    """Automatically dispatch a guardian alert when a high-risk message is detected.

    The guardian_alert_service handles consent checks, cooldown, and
    channel deduplication internally — so we simply call dispatch and let
    it decide whether to actually send.
    """
    from app.models.user import User  # noqa: PLC0415
    from app.services import guardian_alert_service  # noqa: PLC0415

    risk_level = "critical" if primary_emotion == "crisis" else "high"
    reason = f"Automatic crisis detection — emotion: {primary_emotion}"

    # Resolve a human-readable alias for the alert notification
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user_row = user_result.scalar_one_or_none()
    user_alias = user_row.username if user_row else str(user_id)

    try:
        alerts = await guardian_alert_service.dispatch_guardian_alert(
            db,
            user_id=user_id,
            user_alias=user_alias,
            risk_level=risk_level,
            risk_reason=reason,
            channels=["email", "whatsapp"],
        )
        if alerts:
            logger.warning(
                "auto_crisis_alert user_id=%d emotion=%s alerts_sent=%d",
                user_id, primary_emotion, len(alerts),
            )
        else:
            logger.info(
                "auto_crisis_alert user_id=%d emotion=%s — skipped (consent/cooldown)",
                user_id, primary_emotion,
            )
    except Exception:
        # Never let an alert failure break the chat response.
        logger.exception(
            "auto_crisis_alert failed for user_id=%d — continuing", user_id
        )


async def handle_chat(
    db: AsyncSession,
    user_id: int,
    req: ChatRequest,
) -> ChatResponse:
    """Process one chat turn, persist to DB, and return structured reply."""

    t_start = time.perf_counter()

    session_id = req.session_id or secrets.token_hex(16)
    pipeline = _get_pipeline(user_id)

    # Load user context (profile + emotion history)
    profile_ctx = await _load_profile_context(db, user_id)
    recent_emotions = await _load_recent_emotions(db, user_id)

    # ── Personalization layer ─────────────────────────────────────────────
    matched_triggers = _match_triggers(req.message, profile_ctx.get("triggers"))
    personalization_score = _compute_personalization_score(
        profile_ctx, matched_triggers, recent_emotions
    )
    response_type = "personalized" if personalization_score >= _PERSONALIZATION_THRESHOLD else "generic"

    logger.info(
        "personalization user_id=%d triggers_matched=%s score=%.4f type=%s",
        user_id, matched_triggers, personalization_score, response_type,
    )

    context = _build_personalized_context(
        user_id, profile_ctx, recent_emotions, matched_triggers
    )
    # Allow the per-request language preference to override the profile setting
    if req.language_preference:
        context["language_preference"] = req.language_preference

    # Run full agent pipeline (emotion → pattern → response)
    t_nlp_start = time.perf_counter()
    _pipeline_fallback = {
        "response": "I'm here for you. Could you tell me more about how you're feeling?",
        "emotion": {"primary_emotion": "neutral", "confidence_score": 0.5},
        "patterns": {},
    }
    if pipeline is None:
        logger.warning("Pipeline unavailable for user_id=%d; using fallback response.", user_id)
        result = _pipeline_fallback
    else:
        try:
            result = await asyncio.to_thread(pipeline.process_turn, req.message, context=context)
        except Exception:
            logger.exception("Pipeline error for user_id=%d", user_id)
            result = _pipeline_fallback
    t_nlp_end = time.perf_counter()
    logger.info("timing nlp=%.3fs user_id=%d", t_nlp_end - t_nlp_start, user_id)

    emotion_data: dict = result.get("emotion") or {}
    primary = emotion_data.get("primary_emotion", "neutral")
    confidence = float(emotion_data.get("confidence_score", 0.5))
    reply_text: str = result.get("response", "")
    patterns: dict = result.get("patterns") or {}

    # Safety gate
    crisis_score = (emotion_data.get("final_probabilities") or {}).get("crisis", 0.0)
    from app.config import get_settings
    settings = get_settings()
    is_high_risk = (
        primary == "crisis"
        or float(crisis_score) >= settings.CRISIS_CONFIDENCE_THRESHOLD
    )
    escalation_message = settings.HIGH_RISK_ESCALATION_MESSAGE if is_high_risk else None

    # Build score list for the response
    raw_scores: dict = (
        emotion_data.get("final_probabilities")
        or emotion_data.get("confidence_distribution")
        or {}
    )
    scores = [
        {"emotion": e, "score": round(s, 4)}
        for e, s in sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # ── Persist user message, assistant reply, and emotion log in one flush ──
    t_db_start = time.perf_counter()
    db.add(ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role="user",
        content=req.message,
        emotion=primary,
    ))
    db.add(ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role="assistant",
        content=reply_text,
    ))
    db.add(EmotionLog(
        user_id=user_id,
        input_text=req.message,
        primary_emotion=primary,
        confidence=round(confidence, 4),
        uncertainty=round(float(emotion_data.get("uncertainty_score", 0.5)), 4),
        is_high_risk=is_high_risk,
        all_scores=raw_scores,
    ))
    # Flush all three inserts in a single round-trip instead of separate flushes.
    await db.flush()
    t_db_end = time.perf_counter()
    logger.info("timing db=%.3fs user_id=%d", t_db_end - t_db_start, user_id)

    t_total = time.perf_counter() - t_start
    logger.info(
        "chat user_id=%d session=%s emotion=%s is_high_risk=%s response_type=%s total=%.3fs",
        user_id, session_id, primary, is_high_risk, response_type, t_total,
    )

    # ── Auto crisis alert dispatch ────────────────────────────────────────
    if is_high_risk:
        await _maybe_dispatch_crisis_alert(db, user_id, primary, req.message)

    return ChatResponse(
        session_id=session_id,
        reply=reply_text,
        primary_emotion=primary,
        confidence=round(confidence, 4),
        is_high_risk=is_high_risk,
        escalation_message=escalation_message,
        scores=scores,
        personalization_score=personalization_score,
        used_triggers=matched_triggers,
        response_type=response_type,
    )
