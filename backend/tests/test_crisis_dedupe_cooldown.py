"""Crisis alert dedupe + cooldown repeated-flow validation.

Proves that duplicate / repeated crisis messages do NOT trigger multiple
guardian alerts inside the cooldown window, and that a new alert IS allowed
once the cooldown has expired.

Scenarios
---------
1. Same user, same session — 2nd crisis message within 30 s → only ONE alert.
2. Same user, different chat turns — N crisis messages within cooldown → ONE dispatch.
3. After cooldown expires — next crisis message generates a NEW alert.
4. Duplicate channels in the request list → deduplicated; no repeated rows.

All tests work against the in-memory SQLite DB used by the shared test
session and mock the SMTP/Twilio layers so no real messages are sent.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from app.models.guardian_alert import GuardianAlert
from app.models.profile import UserProfile
from app.models.user import User
from app.services.guardian_alert_service import dispatch_guardian_alert

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

# Incrementing seed so every test gets an isolated user_id / email namespace.
_UID_SEED = 5000


def _next_uid() -> int:
    """Return a fresh unique integer for each call (process-local)."""
    global _UID_SEED
    _UID_SEED += 1
    return _UID_SEED


async def _create_user_with_guardian_profile(
    db,
    *,
    uid_seed: int | None = None,
    guardian_email: str = "guardian@example.com",
    guardian_whatsapp: str | None = None,
) -> tuple[User, UserProfile]:
    """Insert a User + enabled guardian UserProfile and flush to DB."""
    uid = uid_seed if uid_seed is not None else _next_uid()
    user = User(
        email=f"user{uid}@test.com",
        username=f"user{uid}",
        hashed_password="hashed",
        is_active=True,
    )
    db.add(user)
    await db.flush()  # populate user.id

    profile = UserProfile(
        user_id=user.id,
        enable_guardian_alerts=True,
        guardian_consent_given=True,
        guardian_name="Test Guardian",
        guardian_email=guardian_email,
        guardian_whatsapp=guardian_whatsapp,
    )
    db.add(profile)
    await db.flush()
    return user, profile


async def _count_real_alerts(db, user_id: int) -> int:
    """Return the number of non-test alert rows in the DB for *user_id*."""
    result = await db.execute(
        select(GuardianAlert).where(
            GuardianAlert.user_id == user_id,
            GuardianAlert.is_test.is_(False),
        )
    )
    return len(result.scalars().all())


async def _get_real_alerts(db, user_id: int) -> list[GuardianAlert]:
    result = await db.execute(
        select(GuardianAlert).where(
            GuardianAlert.user_id == user_id,
            GuardianAlert.is_test.is_(False),
        ).order_by(GuardianAlert.timestamp.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Scenario 1 — SAME USER, SAME SESSION
#   Two crisis messages sent within 30 seconds.
#   Expected: exactly ONE guardian alert dispatched & persisted.
# ---------------------------------------------------------------------------

async def test_same_session_two_crisis_messages_only_one_alert(db_session):
    """
    COOLDOWN PROOF — same session:
    Sending two crisis messages within the cooldown window must produce
    exactly one guardian alert log row and one effective dispatch.
    """
    user, _profile = await _create_user_with_guardian_profile(db_session)

    dispatch_kwargs = dict(
        user_id=user.id,
        user_alias=user.username,
        risk_level="critical",
        risk_reason="I want to harm myself",
        channels=["email"],
        is_test=False,
    )

    with patch(
        "app.services.guardian_alert_service._send_email_alert",
        return_value="sent",
    ) as mock_email:
        # ── Message 1 ───────────────────────────────────────────────────────
        result1 = await dispatch_guardian_alert(db_session, **dispatch_kwargs)

        # ── Message 2 (within cooldown, ~0 s later) ─────────────────────────
        dispatch_kwargs["risk_reason"] = "I still feel the same"
        result2 = await dispatch_guardian_alert(db_session, **dispatch_kwargs)

    # ── Assertions ────────────────────────────────────────────────────────
    # Exactly one real email was sent
    assert mock_email.call_count == 1, (
        f"Expected 1 email dispatch; got {mock_email.call_count}"
    )

    # First call returned one alert log; second returned empty (cooldown)
    assert len(result1) == 1, f"First dispatch should create 1 log; got {len(result1)}"
    assert len(result2) == 0, f"Second dispatch should be blocked by cooldown; got {len(result2)}"

    # DB must contain exactly ONE real alert row
    alert_rows = await _get_real_alerts(db_session, user.id)
    assert len(alert_rows) == 1, (
        f"DB must contain 1 guardian_alert row; found {len(alert_rows)}"
    )
    assert alert_rows[0].delivery_status == "sent"
    assert alert_rows[0].is_test is False


# ---------------------------------------------------------------------------
# Scenario 2 — SAME USER, MULTIPLE CHAT TURNS within cooldown
#   N messages — all crisis-level — dispatched in quick succession.
#   Expected: only the FIRST triggers a dispatch; the rest are silently skipped.
# ---------------------------------------------------------------------------

async def test_multiple_crisis_turns_within_cooldown_dispatch_once(db_session):
    """
    COOLDOWN PROOF — multiple turns:
    Firing N crisis dispatches for the same user within the cooldown window
    must result in exactly 1 DB row and 1 real send attempt.
    """
    user, _profile = await _create_user_with_guardian_profile(db_session)

    crisis_messages = [
        "I want to kill myself",
        "I can't go on",
        "There's no reason to live",
        "Please help me — I'm going to end it",
        "I'm done",
    ]

    with patch(
        "app.services.guardian_alert_service._send_email_alert",
        return_value="sent",
    ) as mock_email:
        results = []
        for msg in crisis_messages:
            res = await dispatch_guardian_alert(
                db_session,
                user_id=user.id,
                user_alias=user.username,
                risk_level="critical",
                risk_reason=msg,
                channels=["email"],
                is_test=False,
            )
            results.append(res)

    # Only the very first call should have triggered an email
    assert mock_email.call_count == 1, (
        f"Expected 1 email send; got {mock_email.call_count} across {len(crisis_messages)} turns"
    )

    # First call returns a log; every subsequent call returns []
    assert len(results[0]) == 1, "First dispatch must create 1 alert log"
    for i, r in enumerate(results[1:], start=2):
        assert r == [], (
            f"Turn {i} inside cooldown must return [] (was blocked); got {r}"
        )

    # DB row count
    alert_rows = await _get_real_alerts(db_session, user.id)
    assert len(alert_rows) == 1, (
        f"Expected 1 DB row; found {len(alert_rows)}"
    )


# ---------------------------------------------------------------------------
# Scenario 3 — AFTER COOLDOWN EXPIRES
#   The first alert is planted with an old timestamp (> 30 min ago) so the
#   cooldown window has lapsed.  The second dispatch must create a new alert.
# ---------------------------------------------------------------------------

async def test_new_alert_allowed_after_cooldown_expires(db_session):
    """
    COOLDOWN PROOF — expiry:
    Once the cooldown window has elapsed, a subsequent crisis message must
    produce a fresh guardian alert.
    """
    user, _profile = await _create_user_with_guardian_profile(db_session)

    # Plant an existing "sent" alert with a timestamp 35 min in the past so
    # it falls outside the 30-minute cooldown window.
    old_ts = datetime.now(timezone.utc) - timedelta(minutes=35)
    old_alert = GuardianAlert(
        user_id=user.id,
        risk_level="critical",
        risk_reason="Earlier crisis — now outside cooldown",
        channel="email",
        delivery_status="sent",
        is_test=False,
        timestamp=old_ts,
    )
    db_session.add(old_alert)
    await db_session.commit()

    with patch(
        "app.services.guardian_alert_service._send_email_alert",
        return_value="sent",
    ) as mock_email:
        result = await dispatch_guardian_alert(
            db_session,
            user_id=user.id,
            user_alias=user.username,
            risk_level="critical",
            risk_reason="I still feel like ending it all",
            channels=["email"],
            is_test=False,
        )

    # ── Assertions ────────────────────────────────────────────────────────
    # A new real alert must have been sent
    assert mock_email.call_count == 1, (
        "After cooldown expiry a fresh email must be sent"
    )
    assert len(result) == 1, "New dispatch should create 1 log"
    assert result[0].delivery_status == "sent"

    # DB must now have 2 real rows: the old planted one + the fresh one
    alert_rows = await _get_real_alerts(db_session, user.id)
    assert len(alert_rows) == 2, (
        f"Expected 2 DB rows (old + new); found {len(alert_rows)}"
    )

    # The new alert (higher ID) must have a later or equal timestamp than the old one.
    # Normalise to naive UTC for comparison since SQLite server_default produces
    # naive datetimes while our manually-set old_ts is timezone-aware.
    def _to_naive(dt: datetime) -> datetime:
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    ts0 = _to_naive(alert_rows[0].timestamp)
    ts1 = _to_naive(alert_rows[1].timestamp)
    assert ts1 >= ts0, (
        "New alert timestamp must be >= the expired alert's timestamp"
    )


# ---------------------------------------------------------------------------
# Scenario 3b — SECOND CALL WITHIN COOLDOWN AFTER FIRST WAS SENT
#   Explicit cooldown timestamp check: verifies _is_on_cooldown sees the
#   recently-committed row.
# ---------------------------------------------------------------------------

async def test_cooldown_timestamp_blocks_second_call(db_session):
    """
    COOLDOWN TIMESTAMP PROOF:
    After the first dispatch commits a 'sent' row, _is_on_cooldown must find
    that row and block the immediately-following call.
    """
    from app.services.guardian_alert_service import _is_on_cooldown

    user, _profile = await _create_user_with_guardian_profile(db_session)

    with patch(
        "app.services.guardian_alert_service._send_email_alert",
        return_value="sent",
    ):
        await dispatch_guardian_alert(
            db_session,
            user_id=user.id,
            user_alias=user.username,
            risk_level="critical",
            risk_reason="First crisis",
            channels=["email"],
            is_test=False,
        )

    # _is_on_cooldown must now return True
    on_cooldown = await _is_on_cooldown(db_session, user.id)
    assert on_cooldown is True, (
        "_is_on_cooldown must return True immediately after a 'sent' alert is committed"
    )


async def test_cooldown_not_active_before_any_alert(db_session):
    """
    COOLDOWN TIMESTAMP PROOF — baseline:
    A brand-new user with no alert history must NOT be on cooldown.
    """
    from app.services.guardian_alert_service import _is_on_cooldown

    user, _profile = await _create_user_with_guardian_profile(db_session)

    on_cooldown = await _is_on_cooldown(db_session, user.id)
    assert on_cooldown is False, (
        "_is_on_cooldown must return False when no alert has been sent yet"
    )


async def test_cooldown_not_active_after_window_passes(db_session):
    """
    COOLDOWN TIMESTAMP PROOF — expiry:
    An old 'sent' alert (> GUARDIAN_ALERT_COOLDOWN_MINUTES ago) must NOT
    keep the user on cooldown.
    """
    from app.services.guardian_alert_service import _is_on_cooldown

    user, _profile = await _create_user_with_guardian_profile(db_session)

    # Plant a 'sent' alert outside the cooldown window
    old_ts = datetime.now(timezone.utc) - timedelta(minutes=31)
    old_alert = GuardianAlert(
        user_id=user.id,
        risk_level="critical",
        risk_reason="Past crisis",
        channel="email",
        delivery_status="sent",
        is_test=False,
        timestamp=old_ts,
    )
    db_session.add(old_alert)
    await db_session.commit()

    on_cooldown = await _is_on_cooldown(db_session, user.id)
    assert on_cooldown is False, (
        "_is_on_cooldown must return False once the 30-min window has elapsed"
    )


async def test_test_alerts_do_not_trigger_cooldown(db_session):
    """
    TEST ALERT ISOLATION:
    is_test=True alerts must NEVER activate the cooldown for real alerts.
    """
    from app.services.guardian_alert_service import _is_on_cooldown

    user, _profile = await _create_user_with_guardian_profile(db_session)

    # Plant a fresh is_test=True + delivery_status="test" alert
    test_alert = GuardianAlert(
        user_id=user.id,
        risk_level="high",
        risk_reason="UI test trigger",
        channel="email",
        delivery_status="test",
        is_test=True,
        timestamp=datetime.now(timezone.utc),
    )
    db_session.add(test_alert)
    await db_session.commit()

    # Real alert cooldown must NOT be active — test alerts are excluded
    on_cooldown = await _is_on_cooldown(db_session, user.id)
    assert on_cooldown is False, (
        "A is_test=True alert must never activate the real-alert cooldown"
    )


# ---------------------------------------------------------------------------
# Scenario 4 — DUPLICATE CHANNEL PREVENTION
#   Requesting the same channel multiple times must not produce duplicate rows.
# ---------------------------------------------------------------------------

async def test_duplicate_channels_are_deduplicated(db_session):
    """
    DEDUPE PROOF — channels:
    Passing ["email", "email", "whatsapp", "whatsapp"] must result in exactly
    one row per unique channel (max 2 rows, not 4).
    """
    user, _profile = await _create_user_with_guardian_profile(
        db_session,
        guardian_email="g@example.com",
        guardian_whatsapp="+15550001234",
    )

    with (
        patch(
            "app.services.guardian_alert_service._send_email_alert",
            return_value="sent",
        ) as mock_email,
        patch(
            "app.services.guardian_alert_service._send_whatsapp_alert",
            return_value="sent",
        ) as mock_whatsapp,
    ):
        result = await dispatch_guardian_alert(
            db_session,
            user_id=user.id,
            user_alias=user.username,
            risk_level="critical",
            risk_reason="Duplicate channel test",
            channels=["email", "email", "whatsapp", "whatsapp"],
            is_test=False,
        )

    # Each unique channel should be sent exactly once
    assert mock_email.call_count == 1, (
        f"email must be dispatched exactly once; got {mock_email.call_count}"
    )
    assert mock_whatsapp.call_count == 1, (
        f"whatsapp must be dispatched exactly once; got {mock_whatsapp.call_count}"
    )

    # Exactly 2 DB rows — one per unique channel
    alert_rows = await _get_real_alerts(db_session, user.id)
    assert len(alert_rows) == 2, (
        f"Expected 2 DB rows (email + whatsapp); found {len(alert_rows)}"
    )

    channels_in_db = {row.channel for row in alert_rows}
    assert channels_in_db == {"email", "whatsapp"}, (
        f"DB rows must cover email + whatsapp; got {channels_in_db}"
    )

    # No channel appears more than once
    channel_list = [row.channel for row in alert_rows]
    assert len(channel_list) == len(set(channel_list)), (
        f"Duplicate channel entries found in DB: {channel_list}"
    )


async def test_single_channel_not_duplicated(db_session):
    """
    DEDUPE PROOF — single channel:
    Passing ["email", "email", "email"] must write exactly ONE email row.
    """
    user, _profile = await _create_user_with_guardian_profile(db_session)

    with patch(
        "app.services.guardian_alert_service._send_email_alert",
        return_value="sent",
    ) as mock_email:
        result = await dispatch_guardian_alert(
            db_session,
            user_id=user.id,
            user_alias=user.username,
            risk_level="critical",
            risk_reason="Single-channel dedupe test",
            channels=["email", "email", "email"],
            is_test=False,
        )

    assert mock_email.call_count == 1
    alert_rows = await _get_real_alerts(db_session, user.id)
    assert len(alert_rows) == 1
    assert alert_rows[0].channel == "email"


# ---------------------------------------------------------------------------
# Scenario 5 — CONSENT GATE: no profile / no consent → no dispatch
#   Safety double-gate must block dispatch if consent is not set.
# ---------------------------------------------------------------------------

async def test_no_profile_returns_empty(db_session):
    """No UserProfile → dispatch must return [] silently."""
    user = User(
        email=f"nopr{_next_uid()}@test.com",
        username=f"nopr{_next_uid()}",
        hashed_password="hashed",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    result = await dispatch_guardian_alert(
        db_session,
        user_id=user.id,
        user_alias=user.username,
        risk_level="critical",
        risk_reason="No profile",
        channels=["email"],
    )
    assert result == []


async def test_alerts_disabled_returns_empty(db_session):
    """enable_guardian_alerts=False → dispatch must return [] silently."""
    user = User(
        email=f"nodis{_next_uid()}@test.com",
        username=f"nodis{_next_uid()}",
        hashed_password="hashed",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    profile = UserProfile(
        user_id=user.id,
        enable_guardian_alerts=False,    # disabled
        guardian_consent_given=True,
        guardian_email="g@example.com",
    )
    db_session.add(profile)
    await db_session.flush()

    result = await dispatch_guardian_alert(
        db_session,
        user_id=user.id,
        user_alias=user.username,
        risk_level="critical",
        risk_reason="Alerts disabled",
        channels=["email"],
    )
    assert result == []


async def test_no_consent_returns_empty(db_session):
    """guardian_consent_given=False → dispatch must return [] silently."""
    user = User(
        email=f"noconsent{_next_uid()}@test.com",
        username=f"noconsent{_next_uid()}",
        hashed_password="hashed",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    profile = UserProfile(
        user_id=user.id,
        enable_guardian_alerts=True,
        guardian_consent_given=False,    # no consent
        guardian_email="g@example.com",
    )
    db_session.add(profile)
    await db_session.flush()

    result = await dispatch_guardian_alert(
        db_session,
        user_id=user.id,
        user_alias=user.username,
        risk_level="critical",
        risk_reason="No consent",
        channels=["email"],
    )
    assert result == []


# ---------------------------------------------------------------------------
# Scenario 6 — TEST ALERT BYPASS
#   is_test=True alerts must bypass the cooldown entirely so the UI test
#   button always works even when a real cooldown is active.
# ---------------------------------------------------------------------------

async def test_test_alerts_bypass_cooldown(db_session):
    """
    TEST ALERT BYPASS PROOF:
    Even when a real 'sent' alert is within the cooldown window, is_test=True
    dispatches must still go through (logged as 'test').
    """
    user, _profile = await _create_user_with_guardian_profile(db_session)

    # Plant a fresh real 'sent' alert so the cooldown is active
    sent_alert = GuardianAlert(
        user_id=user.id,
        risk_level="critical",
        risk_reason="Real alert",
        channel="email",
        delivery_status="sent",
        is_test=False,
        timestamp=datetime.now(timezone.utc),
    )
    db_session.add(sent_alert)
    await db_session.commit()

    # Test dispatch must succeed despite the cooldown
    result = await dispatch_guardian_alert(
        db_session,
        user_id=user.id,
        user_alias=user.username,
        risk_level="high",
        risk_reason="UI test button",
        channels=["email"],
        is_test=True,  # test flag bypasses cooldown
    )

    assert len(result) == 1, (
        "is_test=True dispatch must succeed even when real cooldown is active"
    )
    assert result[0].delivery_status == "test"
    assert result[0].is_test is True


# ---------------------------------------------------------------------------
# Scenario 7 — LOG MESSAGES (caplog)
#   Verify cooldown-skip is recorded in the application log at INFO level.
# ---------------------------------------------------------------------------

async def test_cooldown_skip_is_logged(db_session, caplog):
    """
    LOG PROOF:
    When a dispatch is blocked by cooldown, the service must log an INFO
    message containing 'cooldown' so ops can trace the suppression.
    """
    user, _profile = await _create_user_with_guardian_profile(db_session)

    with patch(
        "app.services.guardian_alert_service._send_email_alert",
        return_value="sent",
    ):
        # First dispatch — succeeds
        await dispatch_guardian_alert(
            db_session,
            user_id=user.id,
            user_alias=user.username,
            risk_level="critical",
            risk_reason="Crisis 1",
            channels=["email"],
            is_test=False,
        )

        # Second dispatch — should be blocked and logged
        with caplog.at_level(logging.INFO, logger="app.services.guardian_alert_service"):
            await dispatch_guardian_alert(
                db_session,
                user_id=user.id,
                user_alias=user.username,
                risk_level="critical",
                risk_reason="Crisis 2 — blocked",
                channels=["email"],
                is_test=False,
            )

    cooldown_logs = [
        r for r in caplog.records
        if "cooldown" in r.message.lower()
    ]
    assert len(cooldown_logs) >= 1, (
        f"Expected at least 1 log record mentioning 'cooldown'; "
        f"got: {[r.message for r in caplog.records]}"
    )
