"""
Tests for AuthManager — bcrypt hashing, verification, brute-force lockout.
Run with: python -m pytest test_auth_manager.py -v
"""

import pytest
from auth_manager import AuthManager
from user_profile import UserProfile
import config


# ── AuthManager unit tests ──────────────────────────────────────────────

class TestAuthManagerHashing:
    """AuthManager.hash_password / verify_password."""

    def test_hash_and_verify(self):
        pw = "securePass123"
        hashed = AuthManager.hash_password(pw)
        assert AuthManager.verify_password(pw, hashed)

    def test_wrong_password_fails(self):
        hashed = AuthManager.hash_password("correctPassword")
        assert not AuthManager.verify_password("wrongPassword", hashed)

    def test_short_password_raises(self):
        with pytest.raises(ValueError):
            AuthManager.hash_password("short")

    def test_min_length_password(self):
        pw = "a" * config.MIN_PASSWORD_LENGTH
        hashed = AuthManager.hash_password(pw)
        assert AuthManager.verify_password(pw, hashed)

    def test_hash_is_bcrypt_format(self):
        hashed = AuthManager.hash_password("validPassword1")
        assert hashed.startswith("$2")

    def test_verify_bad_hash_returns_false(self):
        assert not AuthManager.verify_password("anything", "not-a-hash")


class TestAuthManagerLockout:
    """Brute-force lockout helpers."""

    def test_not_locked_under_threshold(self):
        assert not AuthManager.is_locked_out(0)
        assert not AuthManager.is_locked_out(4)

    def test_locked_at_threshold(self):
        assert AuthManager.is_locked_out(5)
        assert AuthManager.is_locked_out(10)


class TestAuthManagerPasswordStrength:
    """Password strength validation."""

    def test_valid_password(self):
        ok, msg = AuthManager.validate_password_strength("goodPassword1")
        assert ok is True

    def test_too_short_password(self):
        ok, msg = AuthManager.validate_password_strength("short")
        assert ok is False
        assert "8" in msg or "characters" in msg


# ── UserProfile bcrypt integration ──────────────────────────────────────

class TestUserProfileBcrypt:
    """UserProfile.set_password / verify_password with bcrypt."""

    def test_set_and_verify(self):
        profile = UserProfile("test_bcrypt")
        profile.set_password("mySecurePass")
        assert profile.verify_password("mySecurePass")

    def test_wrong_password(self):
        profile = UserProfile("test_bcrypt")
        profile.set_password("mySecurePass")
        assert not profile.verify_password("wrongPass")

    def test_no_password_allows_access(self):
        profile = UserProfile("test_open")
        profile.profile_data['security_enabled'] = False
        assert profile.verify_password("anything")

    def test_bcrypt_hash_stored(self):
        profile = UserProfile("test_hash")
        profile.set_password("securePass1")
        h = profile.profile_data['password_hash']
        assert h.startswith("$2")

    def test_lockout_after_failed_attempts(self):
        profile = UserProfile("test_lockout")
        profile.set_password("correctPass")
        # Fail enough times to trigger lockout
        for _ in range(config.MAX_LOGIN_ATTEMPTS):
            profile.verify_password("wrong")
        # Now even correct password should fail (lockout)
        assert not profile.verify_password("correctPass")
