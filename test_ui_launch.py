"""Smoke test: verify that the Streamlit UI module imports without errors.

This does **not** start a Streamlit server.  It simply imports the core
modules that ``streamlit run ui_app.py`` would load to check that all
internal dependencies resolve correctly.
"""

import importlib
import sys


def test_ui_app_imports():
    """ui_app.py must be importable without raising."""
    # Streamlit may not be installed in CI — we only check the import chain
    # that would fail due to *our* code, not missing third-party packages.
    try:
        import streamlit  # noqa: F401
    except ImportError:
        # If streamlit is not installed we can't meaningfully test the import
        return
    # Import the UI module; it should not raise
    ui_app = importlib.import_module('ui_app')
    assert ui_app is not None


def test_ui_charts_module_imports():
    """ui/charts.py must be importable."""
    try:
        import plotly  # noqa: F401
    except ImportError:
        return
    charts = importlib.import_module('ui.charts')
    assert charts is not None


def test_core_modules_import():
    """Core backend modules must import without errors."""
    for mod_name in [
        'wellness_buddy',
        'emotion_analyzer',
        'agent_pipeline',
        'prediction_agent',
        'research_evaluation',
    ]:
        mod = importlib.import_module(mod_name)
        assert mod is not None, f"Failed to import {mod_name}"
