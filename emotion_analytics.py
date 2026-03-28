"""
Emotion Analytics and Research Evaluation Logger.

Provides structured JSONL-based logging of emotion predictions and chat
responses for offline IEEE research evaluation.  Each logged entry captures
enough information to:

- Reconstruct emotion trends over a session or across sessions.
- Compare *baseline* (no personalisation) vs *personalized* pipelines.
- Compute distribution statistics for the Results section.

Public API
----------
- ``EmotionAnalyticsLogger``        — main logging + analytics class.
- ``get_emotion_trends(logs)``       — module-level helper over raw log list.
- ``get_emotion_distribution(logs)`` — module-level helper over raw log list.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Canonical emotion labels recognised by this system.
_KNOWN_EMOTIONS = ("joy", "sadness", "anger", "fear", "anxiety", "neutral", "crisis", "stress")

# Default directory for log files (relative to project root).
_DEFAULT_LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")


# ---------------------------------------------------------------------------
# Module-level helpers (stateless, operate on raw log lists)
# ---------------------------------------------------------------------------

def get_emotion_trends(logs: list[dict]) -> list[dict]:
    """Return a temporal trend series from a list of logged entries.

    Each item in the returned list is a lightweight dict containing the
    timestamp, detected emotion, CDI score, and risk level so that the
    caller can plot or tabulate temporal change.

    Parameters
    ----------
    logs:
        Raw log entries as returned by
        :meth:`EmotionAnalyticsLogger.load_logs`.

    Returns
    -------
    list[dict] with keys ``timestamp``, ``emotion``, ``cdi_score``,
    ``risk_level``, and ``mode``.
    """
    trends = []
    for entry in logs:
        trends.append({
            "timestamp": entry.get("timestamp", ""),
            "emotion": entry.get("emotion", "neutral"),
            "cdi_score": entry.get("cdi_score", 0.0),
            "risk_level": entry.get("risk_level", "low"),
            "mode": entry.get("mode", "baseline"),
        })
    return trends


def get_emotion_distribution(logs: list[dict]) -> dict[str, float]:
    """Return the normalised frequency distribution of emotions in *logs*.

    Parameters
    ----------
    logs:
        Raw log entries as returned by
        :meth:`EmotionAnalyticsLogger.load_logs`.

    Returns
    -------
    dict mapping emotion label → proportion (0.0–1.0), with all
    :data:`_KNOWN_EMOTIONS` present (zero-filled if not observed).
    """
    counter: Counter = Counter()
    for entry in logs:
        emotion = entry.get("emotion", "neutral")
        counter[emotion] += 1

    total = sum(counter.values()) or 1
    dist: dict[str, float] = {e: 0.0 for e in _KNOWN_EMOTIONS}
    for emotion, count in counter.items():
        dist[emotion] = round(count / total, 4)
    return dist


# ---------------------------------------------------------------------------
# Main logger class
# ---------------------------------------------------------------------------

class EmotionAnalyticsLogger:
    """Append-only JSONL logger for emotion analytics and research evaluation.

    Parameters
    ----------
    log_dir:
        Directory where JSONL log files are stored.  Defaults to the
        ``logs/`` directory at the project root.
    log_filename:
        Base name of the JSONL log file (default ``emotion_analytics.jsonl``).
    """

    def __init__(
        self,
        log_dir: str | None = None,
        log_filename: str = "emotion_analytics.jsonl",
    ) -> None:
        self.log_dir = Path(log_dir or _DEFAULT_LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / log_filename
        # In-memory buffer avoids repeated disk reads for the current session.
        self._buffer: list[dict] = []

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_interaction(
        self,
        *,
        user_message: str,
        emotion_data: dict,
        cdi: dict | None = None,
        escalation: dict | None = None,
        response: str = "",
        mode: str = "baseline",
        user_id: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        """Append one interaction record to the JSONL log file.

        Parameters
        ----------
        user_message:
            Raw user input for this turn.
        emotion_data:
            Full dict returned by ``EmotionAnalyzer.classify_emotion()``.
        cdi:
            CDI result dict (``cdi_score``, ``cdi_level``).  May be *None*.
        escalation:
            Escalation result dict (``escalation_detected``, ``warning``).
        response:
            The generated response string.
        mode:
            ``'baseline'`` or ``'personalized'``.  Used for A/B comparison.
        user_id:
            Optional user identifier for multi-user studies.
        extra:
            Any additional key-value pairs to persist (e.g. fusion_alpha).

        Returns
        -------
        The logged entry dict.
        """
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "mode": mode,
            "user_message": user_message,
            "emotion": emotion_data.get("primary_emotion") or emotion_data.get("emotion", "neutral"),
            "confidence": emotion_data.get("confidence_score", 0.0),
            "risk_level": emotion_data.get("concern_level", "low"),
            "is_crisis": emotion_data.get("is_crisis", False),
            "cdi_score": (cdi or {}).get("cdi_score", 0.0),
            "cdi_level": (cdi or {}).get("cdi_level", "low"),
            "escalation_detected": (escalation or {}).get("escalation_detected", False),
            "response_snippet": response[:120] if response else "",
        }
        if extra:
            entry.update(extra)

        self._buffer.append(entry)
        try:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError:
            pass  # Non-fatal — in-memory buffer still updated.
        return entry

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_logs(
        self,
        mode: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        """Load all persisted log entries, optionally filtered.

        Parameters
        ----------
        mode:
            When provided, only entries whose ``mode`` field matches are
            returned.  Use ``'baseline'`` or ``'personalized'``.
        user_id:
            When provided, only entries for this user are returned.

        Returns
        -------
        list[dict] of matching log entries.
        """
        entries: list[dict] = []
        if not self.log_path.exists():
            return entries
        with self.log_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if mode is not None and obj.get("mode") != mode:
                    continue
                if user_id is not None and obj.get("user_id") != user_id:
                    continue
                entries.append(obj)
        return entries

    # ------------------------------------------------------------------
    # Analytics helpers (operate on persisted logs)
    # ------------------------------------------------------------------

    def get_emotion_trends(
        self,
        mode: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        """Return temporal emotion trend from persisted logs.

        Delegates to the module-level :func:`get_emotion_trends` helper after
        loading and filtering the log entries.
        """
        return get_emotion_trends(self.load_logs(mode=mode, user_id=user_id))

    def get_emotion_distribution(
        self,
        mode: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, float]:
        """Return normalised emotion frequency distribution from persisted logs.

        Delegates to the module-level :func:`get_emotion_distribution` helper.
        """
        return get_emotion_distribution(self.load_logs(mode=mode, user_id=user_id))

    # ------------------------------------------------------------------
    # Evaluation comparison
    # ------------------------------------------------------------------

    def compare_modes(self) -> dict[str, Any]:
        """Compare baseline vs personalised mode metrics.

        Returns a summary dict suitable for inclusion in a Results table:

        .. code-block:: python

            {
                'baseline': {'n': int, 'avg_cdi': float, 'emotion_distribution': dict},
                'personalized': {'n': int, 'avg_cdi': float, 'emotion_distribution': dict},
                'cdi_improvement': float,          # personalized − baseline (negative = better)
                'escalation_rate_baseline': float,
                'escalation_rate_personalized': float,
            }
        """
        baseline_logs = self.load_logs(mode="baseline")
        personalized_logs = self.load_logs(mode="personalized")

        def _summarise(logs: list[dict]) -> dict[str, Any]:
            n = len(logs)
            if n == 0:
                return {
                    "n": 0,
                    "avg_cdi": 0.0,
                    "emotion_distribution": get_emotion_distribution([]),
                    "escalation_rate": 0.0,
                }
            avg_cdi = round(sum(e.get("cdi_score", 0.0) for e in logs) / n, 4)
            escalations = sum(1 for e in logs if e.get("escalation_detected"))
            return {
                "n": n,
                "avg_cdi": avg_cdi,
                "emotion_distribution": get_emotion_distribution(logs),
                "escalation_rate": round(escalations / n, 4),
            }

        b = _summarise(baseline_logs)
        p = _summarise(personalized_logs)
        cdi_improvement = round(p["avg_cdi"] - b["avg_cdi"], 4)

        return {
            "baseline": b,
            "personalized": p,
            "cdi_improvement": cdi_improvement,
            "escalation_rate_baseline": b["escalation_rate"],
            "escalation_rate_personalized": p["escalation_rate"],
        }

    # ------------------------------------------------------------------
    # In-session helpers (operate on the in-memory buffer)
    # ------------------------------------------------------------------

    def session_trends(self) -> list[dict]:
        """Return trends for the current session (in-memory buffer only)."""
        return get_emotion_trends(self._buffer)

    def session_distribution(self) -> dict[str, float]:
        """Return emotion distribution for the current session (in-memory buffer only)."""
        return get_emotion_distribution(self._buffer)

    def reset_session(self) -> None:
        """Clear the in-memory session buffer (does not touch the log file)."""
        self._buffer.clear()
