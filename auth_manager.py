"""
Authentication manager for AI Wellness Buddy.
Provides bcrypt-based password hashing, login verification, and brute-force protection.
"""

import bcrypt
import config


class AuthManager:
    """Manages authentication: hashing, verification, and brute-force lockout."""

    MAX_FAILED_ATTEMPTS = 5  # per-session lockout threshold

    # ------------------------------------------------------------------
    # Password hashing
    # ------------------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a bcrypt hash of *password*.

        Raises ``ValueError`` if the password is shorter than
        ``config.MIN_PASSWORD_LENGTH``.
        """
        if len(password) < config.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters"
            )
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Return ``True`` if *password* matches *password_hash*."""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except (ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Brute-force / session-level lockout helpers
    # ------------------------------------------------------------------

    @staticmethod
    def is_locked_out(failed_attempts: int) -> bool:
        """Return ``True`` when *failed_attempts* reaches the threshold."""
        return failed_attempts >= AuthManager.MAX_FAILED_ATTEMPTS

    @staticmethod
    def validate_password_strength(password: str) -> tuple:
        """Return ``(ok, message)`` describing whether *password* is strong enough."""
        if len(password) < config.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters."
        return True, "Password meets requirements."
