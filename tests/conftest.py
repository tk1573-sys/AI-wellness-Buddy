"""Shared fixtures for the tests/ package."""

import sys
import os

# Ensure the project root is on sys.path so that top-level modules
# (emotion_analyzer, agent_pipeline, …) are importable when tests are
# invoked from any working directory.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
