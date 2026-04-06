"""
Guardian Alert Service
======================

Dispatches emergency notifications to a user's configured guardian via
email (SMTP / SendGrid-ready) and/or WhatsApp (Twilio-ready) when a
high-risk or critical distress event is detected.

Trigger conditions
------------------
* risk_level in {"high", "critical"}
* Self-harm / crisis intent keywords detected in the user's chat
* Repeated distress sessions exceed GUARDIAN_DISTRESS_SESSION_THRESHOLD
* Risk score spike > GUARDIAN_RISK_SPIKE_THRESHOLD

All alerts require explicit user consent (guardian_consent_given=True on
the UserProfile) and a configured guardian email or WhatsApp number.

Every dispatched alert (or failed attempt) is persisted in the
guardian_alerts table via _log_alert().
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.guardian_alert import GuardianAlert
from app.models.profile import UserProfile

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Crisis / self-harm keyword list (extend as needed)
# ---------------------------------------------------------------------------
_CRISIS_KEYWORDS: frozenset[str] = frozenset(
    [
        "kill myself",
        "end my life",
        "want to die",
        "suicide",
        "self harm",
        "self-harm",
        "hurt myself",
        "no reason to live",
        "can't go on",
        "give up on life",
        "worthless",
        "hopeless",
        "nobody cares",
        "disappear forever",
    ]
)


# ---------------------------------------------------------------------------
# Public helpers — trigger conditions
# ---------------------------------------------------------------------------

def is_crisis_keyword_present(text: str) -> bool:
    """Return True if *text* contains at least one crisis-intent keyword."""
    lower = text.lower()
    return any(kw in lower for kw in _CRISIS_KEYWORDS)


def should_trigger_alert(
    *,
    risk_level: str,
    text: str | None = None,
    distress_session_count: int = 0,
    previous_risk_score: float = 0.0,
    current_risk_score: float = 0.0,
) -> bool:
    """Return True when at least one escalation condition is met."""
    if risk_level in ("high", "critical"):
        return True
    if text and is_crisis_keyword_present(text):
        return True
    if distress_session_count >= settings.GUARDIAN_DISTRESS_SESSION_THRESHOLD:
        return True
    spike = current_risk_score - previous_risk_score
    if spike >= settings.GUARDIAN_RISK_SPIKE_THRESHOLD:
        return True
    return False


# ---------------------------------------------------------------------------
# Core dispatch function
# ---------------------------------------------------------------------------

async def dispatch_guardian_alert(
    db: AsyncSession,
    *,
    user_id: int,
    user_alias: str,
    risk_level: str,
    risk_reason: str | None,
    channels: list[str],
) -> list[GuardianAlert]:
    """
    Dispatch alerts on the requested channels and persist a log record for
    each one.  Returns the list of persisted GuardianAlert rows.
    """
    # Load user profile — we need guardian contact info and consent flag
    profile = await _get_profile(db, user_id)

    if profile is None:
        logger.warning("dispatch_guardian_alert: no profile for user_id=%d", user_id)
        return []

    if not profile.guardian_consent_given:
        logger.info(
            "dispatch_guardian_alert: consent not given for user_id=%d — skipping",
            user_id,
        )
        return []

    if not profile.enable_guardian_alerts:
        logger.info(
            "dispatch_guardian_alert: alerts disabled for user_id=%d — skipping",
            user_id,
        )
        return []

    logs: list[GuardianAlert] = []

    for channel in channels:
        status = "failed"
        try:
            if channel == "email" and profile.guardian_email:
                status = _send_email_alert(
                    guardian_name=profile.guardian_name or "Guardian",
                    guardian_email=profile.guardian_email,
                    user_alias=user_alias,
                    risk_level=risk_level,
                    risk_reason=risk_reason,
                )
            elif channel == "whatsapp" and profile.guardian_whatsapp:
                status = _send_whatsapp_alert(
                    guardian_whatsapp=profile.guardian_whatsapp,
                    user_alias=user_alias,
                    risk_level=risk_level,
                    risk_reason=risk_reason,
                )
            else:
                logger.debug(
                    "dispatch_guardian_alert: channel=%s has no contact — skipping",
                    channel,
                )
                continue
        except Exception:  # noqa: BLE001
            logger.exception(
                "dispatch_guardian_alert: error dispatching channel=%s user_id=%d",
                channel,
                user_id,
            )

        log = await _log_alert(
            db,
            user_id=user_id,
            risk_level=risk_level,
            risk_reason=risk_reason,
            channel=channel,
            delivery_status=status,
        )
        logs.append(log)

    return logs


# ---------------------------------------------------------------------------
# Email channel
# ---------------------------------------------------------------------------

def _send_email_alert(
    *,
    guardian_name: str,
    guardian_email: str,
    user_alias: str,
    risk_level: str,
    risk_reason: str | None,
) -> str:
    """Send an alert email via SMTP (SendGrid-compatible).

    Returns "sent" on success, "failed" on error.
    Credentials come from ``settings.SMTP_*`` env variables.
    """
    subject = "AI Wellness Buddy Alert: Immediate Attention Required"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    body_parts = [
        f"Dear {guardian_name},",
        "",
        "The AI Wellness Buddy has detected a high-risk emotional distress signal for "
        f"the user you are registered as a guardian for ({user_alias}).",
        "",
        f"  Risk Level  : {risk_level.upper()}",
        f"  Timestamp   : {timestamp}",
    ]
    if risk_reason:
        body_parts += [f"  Summary     : {risk_reason}"]

    body_parts += [
        "",
        "Please reach out to them as soon as possible and consider contacting "
        "professional mental health services if necessary.",
        "",
        "Crisis resources:",
        "  • 988 Suicide & Crisis Lifeline — call or text 988",
        "  • Crisis Text Line — text HOME to 741741",
        "",
        "— AI Wellness Buddy Safety System",
        "",
        "⚠️  This alert was sent because the user has explicitly consented to "
        "guardian notifications.  If you believe this was sent in error, please "
        "contact the user directly.",
    ]
    body = "\n".join(body_parts)

    if not settings.SMTP_HOST:
        logger.warning("_send_email_alert: SMTP_HOST not configured — alert not sent")
        return "failed"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = guardian_email
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, guardian_email, msg.as_string())

        logger.info("_send_email_alert: sent to %s", guardian_email)
        return "sent"
    except Exception:  # noqa: BLE001
        logger.exception("_send_email_alert: failed to send to %s", guardian_email)
        return "failed"


# ---------------------------------------------------------------------------
# WhatsApp channel (Twilio-ready wrapper)
# ---------------------------------------------------------------------------

def _send_whatsapp_alert(
    *,
    guardian_whatsapp: str,
    user_alias: str,
    risk_level: str,
    risk_reason: str | None,
) -> str:
    """Send a WhatsApp alert via Twilio.

    Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_FROM
    environment variables to be set.

    Returns "sent" on success, "failed" on error.
    """
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("_send_whatsapp_alert: Twilio credentials not configured")
        return "failed"

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = (
        f"🚨 AI Wellness Buddy Alert\n\n"
        f"A high-risk distress signal has been detected for {user_alias}.\n"
        f"Risk Level: {risk_level.upper()}\n"
        f"Time: {timestamp}\n"
    )
    if risk_reason:
        body += f"Reason: {risk_reason}\n"
    body += "\nPlease check in with them immediately.\n988 (crisis line) | Text HOME to 741741"

    try:
        from twilio.rest import Client  # type: ignore[import]

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_FROM}"
        to_number = f"whatsapp:{guardian_whatsapp}"
        client.messages.create(body=body, from_=from_number, to=to_number)
        logger.info("_send_whatsapp_alert: sent to %s", guardian_whatsapp)
        return "sent"
    except ImportError:
        logger.warning("_send_whatsapp_alert: twilio package not installed")
        return "failed"
    except Exception:  # noqa: BLE001
        logger.exception("_send_whatsapp_alert: failed to send to %s", guardian_whatsapp)
        return "failed"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

async def _get_profile(db: AsyncSession, user_id: int) -> UserProfile | None:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _log_alert(
    db: AsyncSession,
    *,
    user_id: int,
    risk_level: str,
    risk_reason: str | None,
    channel: str,
    delivery_status: str,
) -> GuardianAlert:
    alert = GuardianAlert(
        user_id=user_id,
        risk_level=risk_level,
        risk_reason=risk_reason,
        channel=channel,
        delivery_status=delivery_status,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    logger.info(
        "_log_alert: user_id=%d risk=%s channel=%s status=%s",
        user_id,
        risk_level,
        channel,
        delivery_status,
    )
    return alert


async def get_alerts_for_user(
    db: AsyncSession,
    user_id: int,
    limit: int = 50,
) -> list[GuardianAlert]:
    """Return the most recent guardian alerts for a user."""
    result = await db.execute(
        select(GuardianAlert)
        .where(GuardianAlert.user_id == user_id)
        .order_by(GuardianAlert.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
