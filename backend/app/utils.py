"""
Shared utility: resolve the AI project root directory.

The root is discovered by walking upwards from any file in the backend
looking for the `emotion_analyzer.py` marker (a well-known file that only
exists in the project root).  This is more robust than a fixed number of
``..`` traversals because it does not depend on where the backend folder is
placed within the repo.
"""

from __future__ import annotations

from pathlib import Path


def find_project_root() -> Path:
    """Return the absolute path of the repository root.

    Walks upward from this file until it finds a directory that contains
    ``emotion_analyzer.py`` (the canonical AI-core module).  Raises
    ``RuntimeError`` if the marker is not found within 10 levels.
    """
    candidate = Path(__file__).resolve().parent
    for _ in range(10):
        if (candidate / "emotion_analyzer.py").exists():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    raise RuntimeError(
        "Could not locate the project root (looked for emotion_analyzer.py). "
        "Ensure the backend is run from within the AI-wellness-Buddy repository."
    )
