"""
Persistent conversation session manager.

Provides ``create_session``, ``load_session``, and ``save_session`` so that
conversation state (chat_history, emotion_history, risk_history) survives
login, page-refresh, and application restarts.

Session data is stored inside the user's profile via :class:`UserProfile`
and persisted through :class:`DataStore`.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from data_store import DataStore
from user_profile import UserProfile


class SessionManager:
    """Coordinate session lifecycle for a single user.

    Parameters
    ----------
    data_store : DataStore
        Shared data-store instance used for reading/writing user JSON.
    """

    def __init__(self, data_store: DataStore):
        self.data_store = data_store

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_session(self, user_id: str) -> Dict:
        """Create a new conversation session for *user_id*.

        A fresh ``session_id`` is generated and the session record is
        persisted immediately so it survives an early restart.

        Returns the session dict.
        """
        session = {
            "session_id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "chat_history": [],
            "emotion_history": [],
            "risk_history": [],
            "coping_tools_used": [],
        }
        self._persist(user_id, session)
        return session

    def load_session(self, user_id: str) -> Optional[Dict]:
        """Load the most-recent session for *user_id*.

        Returns ``None`` when no stored session exists (e.g. first-time
        user).  The caller should fall back to ``create_session`` in that
        case.
        """
        profile = self._load_profile(user_id)
        if profile is None:
            return None
        session = profile.profile_data.get("session")
        if session is None:
            return None
        # Defensive copy so callers cannot mutate the stored version.
        return {
            "session_id": session.get("session_id", ""),
            "user_id": session.get("user_id", user_id),
            "created_at": session.get("created_at", ""),
            "chat_history": list(session.get("chat_history", [])),
            "emotion_history": list(session.get("emotion_history", [])),
            "risk_history": list(session.get("risk_history", [])),
            "coping_tools_used": list(session.get("coping_tools_used", [])),
        }

    def save_session(
        self,
        user_id: str,
        *,
        session_id: Optional[str] = None,
        chat_history: Optional[List] = None,
        emotion_history: Optional[List] = None,
        risk_history: Optional[List] = None,
        coping_tools_used: Optional[List] = None,
    ) -> Dict:
        """Persist the current session state for *user_id*.

        Only supplied fields are updated; ``None`` fields are left
        unchanged.  Returns the updated session dict.
        """
        profile = self._load_profile(user_id)
        if profile is None:
            # First save for a brand-new user – bootstrap a session.
            session = self.create_session(user_id)
        else:
            session = profile.profile_data.get("session")
            if session is None:
                session = self.create_session(user_id)

        if session_id is not None:
            session["session_id"] = session_id
        if chat_history is not None:
            session["chat_history"] = list(chat_history)
        if emotion_history is not None:
            session["emotion_history"] = list(emotion_history)
        if risk_history is not None:
            session["risk_history"] = list(risk_history)
        if coping_tools_used is not None:
            session["coping_tools_used"] = list(coping_tools_used)

        self._persist(user_id, session)
        return dict(session)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load a :class:`UserProfile` from the data-store."""
        data = self.data_store.load_user_data(user_id)
        if data is None:
            return None
        profile = UserProfile(user_id)
        profile.load_from_data(data)
        return profile

    def _persist(self, user_id: str, session: Dict) -> None:
        """Write *session* into the user's profile and flush to disk."""
        profile = self._load_profile(user_id)
        if profile is None:
            profile = UserProfile(user_id)
        profile.profile_data["session"] = session
        # Keep the top-level chat_history in sync for backward compat.
        profile.save_chat_history(session.get("chat_history", []))
        self.data_store.save_user_data(user_id, profile.get_profile())
