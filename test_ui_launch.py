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


# -----------------------------------------------------------------------
# Session-state deduplication tests
# -----------------------------------------------------------------------

def _setup_streamlit_session():
    """Prepare a minimal Streamlit session_state for unit-level checks."""
    try:
        import streamlit as st
    except ImportError:
        return None, None
    # Seed the keys that _add_chat_message relies on
    for key, default in [('chat_history', []), ('messages', []),
                         ('last_user_input', None)]:
        st.session_state[key] = default
    ui_app = importlib.import_module('ui_app')
    return st, ui_app


def test_last_user_input_initialised():
    """Session state must include last_user_input after importing ui_app."""
    try:
        import streamlit as st
    except ImportError:
        return
    importlib.import_module('ui_app')
    assert 'last_user_input' in st.session_state


def test_add_chat_message_appends_once():
    """_add_chat_message should add exactly one entry to chat_history."""
    st, ui_app = _setup_streamlit_session()
    if st is None:
        return
    ui_app._add_chat_message("user", "hello")
    assert len(st.session_state.chat_history) == 1
    assert st.session_state.chat_history[0] == {
        "role": "user", "content": "hello",
    }


def test_add_chat_message_with_emotion():
    """_add_chat_message stores emotion when provided."""
    st, ui_app = _setup_streamlit_session()
    if st is None:
        return
    ui_app._add_chat_message("user", "I feel sad", emotion="sadness")
    assert st.session_state.chat_history[0]["emotion"] == "sadness"


def test_add_chat_message_syncs_legacy_messages():
    """_add_chat_message must keep the legacy 'messages' list in sync."""
    st, ui_app = _setup_streamlit_session()
    if st is None:
        return
    ui_app._add_chat_message("assistant", "How are you?")
    assert len(st.session_state.messages) == 1
    assert st.session_state.messages[0] == {
        "role": "assistant", "content": "How are you?",
    }


def test_duplicate_input_guard_prevents_reprocessing():
    """When last_user_input matches the new input, no message should be added.

    This simulates the guard logic used in render_chat_tab(): a message is
    only processed when ``prompt != st.session_state.last_user_input``.
    """
    st, ui_app = _setup_streamlit_session()
    if st is None:
        return
    # Simulate first submission
    prompt = "I'm feeling anxious"
    if prompt != st.session_state.last_user_input:
        ui_app._add_chat_message("user", prompt)
        st.session_state.last_user_input = prompt
    assert len(st.session_state.chat_history) == 1

    # Simulate rerun with same prompt — guard should prevent append
    if prompt != st.session_state.last_user_input:
        ui_app._add_chat_message("user", prompt)
        st.session_state.last_user_input = prompt
    assert len(st.session_state.chat_history) == 1  # still 1, not 2


def test_different_input_allowed_after_guard():
    """A new, different prompt should be processed normally."""
    st, ui_app = _setup_streamlit_session()
    if st is None:
        return
    first = "hello"
    second = "how are you"
    # First message
    if first != st.session_state.last_user_input:
        ui_app._add_chat_message("user", first)
        st.session_state.last_user_input = first
    # Second (different) message
    if second != st.session_state.last_user_input:
        ui_app._add_chat_message("user", second)
        st.session_state.last_user_input = second
    assert len(st.session_state.chat_history) == 2
