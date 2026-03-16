"""Tests for session_manager.py – persistent conversation sessions.

Validates create_session, load_session, save_session, round-trip
persistence, and backward-compatible chat_history sync.
"""

import tempfile
import os
import sys

import pytest

# Ensure repo root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from data_store import DataStore
from user_profile import UserProfile
from session_manager import SessionManager


@pytest.fixture()
def tmp_store(tmp_path):
    """Return a DataStore backed by a temporary directory."""
    return DataStore(data_dir=str(tmp_path))


@pytest.fixture()
def mgr(tmp_store):
    """Return a SessionManager wired to a temporary DataStore."""
    return SessionManager(tmp_store)


@pytest.fixture()
def seeded_user(tmp_store):
    """Create a minimal user profile on disk and return user_id."""
    uid = "test_user"
    profile = UserProfile(uid)
    profile.set_password("TestPass1!")
    tmp_store.save_user_data(uid, profile.get_profile())
    return uid


# ------------------------------------------------------------------
# create_session
# ------------------------------------------------------------------

class TestCreateSession:
    def test_returns_dict_with_required_keys(self, mgr, seeded_user):
        session = mgr.create_session(seeded_user)
        for key in ("session_id", "user_id", "created_at",
                     "chat_history", "emotion_history", "risk_history"):
            assert key in session, f"Missing key: {key}"

    def test_session_id_is_uuid(self, mgr, seeded_user):
        import uuid
        session = mgr.create_session(seeded_user)
        uuid.UUID(session["session_id"])  # raises on bad format

    def test_user_id_matches(self, mgr, seeded_user):
        session = mgr.create_session(seeded_user)
        assert session["user_id"] == seeded_user

    def test_histories_start_empty(self, mgr, seeded_user):
        session = mgr.create_session(seeded_user)
        assert session["chat_history"] == []
        assert session["emotion_history"] == []
        assert session["risk_history"] == []

    def test_creates_profile_for_new_user(self, mgr):
        """Even for a user_id with no profile on disk, create_session works."""
        session = mgr.create_session("brand_new")
        assert session["user_id"] == "brand_new"


# ------------------------------------------------------------------
# load_session
# ------------------------------------------------------------------

class TestLoadSession:
    def test_returns_none_for_unknown_user(self, mgr):
        assert mgr.load_session("nonexistent") is None

    def test_returns_none_when_no_session_stored(self, mgr, seeded_user):
        """Profile exists but no session has been created yet."""
        assert mgr.load_session(seeded_user) is None

    def test_round_trip(self, mgr, seeded_user):
        created = mgr.create_session(seeded_user)
        loaded = mgr.load_session(seeded_user)
        assert loaded is not None
        assert loaded["session_id"] == created["session_id"]
        assert loaded["user_id"] == seeded_user

    def test_returns_defensive_copy(self, mgr, seeded_user):
        mgr.create_session(seeded_user)
        s1 = mgr.load_session(seeded_user)
        s1["chat_history"].append({"role": "user", "content": "hi"})
        s2 = mgr.load_session(seeded_user)
        assert s2["chat_history"] == []  # original unchanged


# ------------------------------------------------------------------
# save_session
# ------------------------------------------------------------------

class TestSaveSession:
    def test_persists_chat_history(self, mgr, seeded_user):
        mgr.create_session(seeded_user)
        history = [{"role": "user", "content": "hello"}]
        mgr.save_session(seeded_user, chat_history=history)
        loaded = mgr.load_session(seeded_user)
        assert loaded["chat_history"] == history

    def test_persists_emotion_history(self, mgr, seeded_user):
        mgr.create_session(seeded_user)
        emotions = [{"ts": "2026-01-01", "emotion": "joy"}]
        mgr.save_session(seeded_user, emotion_history=emotions)
        loaded = mgr.load_session(seeded_user)
        assert loaded["emotion_history"] == emotions

    def test_persists_risk_history(self, mgr, seeded_user):
        mgr.create_session(seeded_user)
        risks = [{"ts": "2026-01-01", "risk_score": 0.3, "risk_level": "low"}]
        mgr.save_session(seeded_user, risk_history=risks)
        loaded = mgr.load_session(seeded_user)
        assert loaded["risk_history"] == risks

    def test_partial_update_preserves_other_fields(self, mgr, seeded_user):
        mgr.create_session(seeded_user)
        mgr.save_session(seeded_user, chat_history=[{"role": "user", "content": "a"}])
        mgr.save_session(seeded_user, emotion_history=[{"emotion": "joy"}])
        loaded = mgr.load_session(seeded_user)
        assert len(loaded["chat_history"]) == 1
        assert len(loaded["emotion_history"]) == 1

    def test_save_creates_session_if_none(self, mgr, seeded_user):
        """Calling save_session before create_session still works."""
        mgr.save_session(seeded_user, chat_history=[{"role": "user", "content": "hi"}])
        loaded = mgr.load_session(seeded_user)
        assert loaded is not None
        assert loaded["chat_history"] == [{"role": "user", "content": "hi"}]

    def test_updates_session_id(self, mgr, seeded_user):
        mgr.create_session(seeded_user)
        mgr.save_session(seeded_user, session_id="custom-id-123")
        loaded = mgr.load_session(seeded_user)
        assert loaded["session_id"] == "custom-id-123"


# ------------------------------------------------------------------
# Backward compatibility – chat_history sync
# ------------------------------------------------------------------

class TestBackwardCompat:
    def test_chat_history_syncs_to_profile(self, mgr, seeded_user, tmp_store):
        """save_session should also update UserProfile.chat_history."""
        mgr.create_session(seeded_user)
        history = [{"role": "user", "content": "sync test"}]
        mgr.save_session(seeded_user, chat_history=history)
        # Load the raw profile, not the session
        data = tmp_store.load_user_data(seeded_user)
        profile = UserProfile(seeded_user)
        profile.load_from_data(data)
        assert profile.load_chat_history() == history


# ------------------------------------------------------------------
# Integration: survives login/refresh/restart
# ------------------------------------------------------------------

class TestSurvivalScenarios:
    def test_survives_login_cycle(self, tmp_store):
        """Session data survives a full logout+login cycle."""
        mgr1 = SessionManager(tmp_store)
        uid = "survival_user"
        # Bootstrap user on disk
        profile = UserProfile(uid)
        profile.set_password("TestPass1!")
        tmp_store.save_user_data(uid, profile.get_profile())
        # First "login"
        s = mgr1.create_session(uid)
        sid = s["session_id"]
        mgr1.save_session(uid, chat_history=[{"role": "user", "content": "hi"}],
                          emotion_history=[{"emotion": "joy"}],
                          risk_history=[{"risk_score": 0.1}])
        # Simulate restart – new SessionManager instance
        mgr2 = SessionManager(tmp_store)
        loaded = mgr2.load_session(uid)
        assert loaded["session_id"] == sid
        assert len(loaded["chat_history"]) == 1
        assert len(loaded["emotion_history"]) == 1
        assert len(loaded["risk_history"]) == 1

    def test_survives_fresh_data_store(self, tmp_path):
        """Session data survives when DataStore is re-created from disk."""
        ds1 = DataStore(data_dir=str(tmp_path))
        mgr1 = SessionManager(ds1)
        uid = "disk_user"
        profile = UserProfile(uid)
        profile.set_password("TestPass1!")
        ds1.save_user_data(uid, profile.get_profile())
        mgr1.create_session(uid)
        mgr1.save_session(uid, chat_history=[{"role": "user", "content": "persist"}])
        # Brand-new DataStore pointing at same directory
        ds2 = DataStore(data_dir=str(tmp_path))
        mgr2 = SessionManager(ds2)
        loaded = mgr2.load_session(uid)
        assert loaded is not None
        assert loaded["chat_history"] == [{"role": "user", "content": "persist"}]
