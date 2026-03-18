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


# -----------------------------------------------------------------------
# Chat-history persistence tests (UserProfile)
# -----------------------------------------------------------------------

def test_user_profile_has_chat_history_field():
    """UserProfile.profile_data must include 'chat_history' by default."""
    from user_profile import UserProfile
    profile = UserProfile("test_user")
    assert 'chat_history' in profile.profile_data
    assert profile.profile_data['chat_history'] == []


def test_load_chat_history_empty_by_default():
    """load_chat_history returns empty list for a fresh profile."""
    from user_profile import UserProfile
    profile = UserProfile("test_user")
    assert profile.load_chat_history() == []


def test_save_and_load_chat_history():
    """save_chat_history + load_chat_history round-trip."""
    from user_profile import UserProfile
    profile = UserProfile("test_user")
    history = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello!"},
    ]
    profile.save_chat_history(history)
    loaded = profile.load_chat_history()
    assert loaded == history


def test_save_chat_history_makes_copy():
    """Saved history must be a copy, not a reference to the original list."""
    from user_profile import UserProfile
    profile = UserProfile("test_user")
    history = [{"role": "user", "content": "hi"}]
    profile.save_chat_history(history)
    # Mutate original — profile should not be affected
    history.append({"role": "assistant", "content": "hello"})
    assert len(profile.load_chat_history()) == 1


def test_load_chat_history_returns_copy():
    """Loaded history must be a copy, not the internal list."""
    from user_profile import UserProfile
    profile = UserProfile("test_user")
    profile.save_chat_history([{"role": "user", "content": "hi"}])
    loaded = profile.load_chat_history()
    loaded.append({"role": "assistant", "content": "hello"})
    assert len(profile.load_chat_history()) == 1


def test_load_chat_history_legacy_profile_without_field():
    """Legacy profiles without chat_history field should return []."""
    from user_profile import UserProfile
    profile = UserProfile("legacy")
    # Simulate a legacy profile missing the key
    del profile.profile_data['chat_history']
    assert profile.load_chat_history() == []


def test_load_profile_restores_chat_history():
    """load_profile() must populate session_state.chat_history from disk."""
    try:
        import streamlit as st
    except ImportError:
        return
    import importlib
    import tempfile
    import os

    # Seed session state
    for key, default in [('chat_history', []), ('messages', []),
                         ('last_user_input', None), ('buddy', None),
                         ('user_id', None), ('current_user', None),
                         ('profile_loaded', False), ('authenticated', False),
                         ('voice_handler', None)]:
        st.session_state[key] = default

    ui_app = importlib.import_module('ui_app')
    from user_profile import UserProfile
    from data_store import DataStore

    saved_history = [
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "I feel happy"},
        {"role": "assistant", "content": "Great to hear!"},
    ]

    # Create a real profile on disk in a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        ds = DataStore(data_dir=tmpdir)
        profile = UserProfile("persist_test")
        profile.set_password("TestPass1!")
        profile.save_chat_history(saved_history)
        ds.save_user_data("persist_test", profile.get_profile())

        # Patch init_buddy to use our temp data store
        from unittest.mock import patch, MagicMock
        from wellness_buddy import WellnessBuddy

        mock_buddy = MagicMock(spec=WellnessBuddy)
        # When _load_existing_profile is called, actually load data
        def _mock_load(username):
            data = ds.load_user_data(username)
            mock_buddy.user_profile = UserProfile(username)
            mock_buddy.user_profile.load_from_data(data)
        mock_buddy._load_existing_profile.side_effect = _mock_load
        mock_buddy.data_store = ds

        st.session_state.buddy = mock_buddy

        # Patch st.rerun to avoid actual rerun
        with patch.object(st, 'rerun'):
            ui_app.load_profile("persist_test")

        assert len(st.session_state.chat_history) == 3
        assert st.session_state.chat_history[1]["content"] == "I feel happy"
        assert st.session_state.authenticated is True
        assert st.session_state.profile_loaded is True


def test_persist_chat_history_saves_to_profile():
    """_persist_chat_history should write session chat_history to profile."""
    try:
        import streamlit as st
    except ImportError:
        return
    import importlib
    from unittest.mock import MagicMock
    from user_profile import UserProfile

    ui_app = importlib.import_module('ui_app')
    profile = UserProfile("saver")
    mock_buddy = MagicMock()
    mock_buddy.user_profile = profile

    st.session_state['buddy'] = mock_buddy
    st.session_state['user_id'] = "saver"
    st.session_state['session_mgr'] = None  # use legacy fallback path
    st.session_state['chat_history'] = [
        {"role": "user", "content": "test message"},
    ]
    st.session_state['messages'] = [
        {"role": "user", "content": "test message"},
    ]

    ui_app._persist_chat_history()

    assert profile.load_chat_history() == [{"role": "user", "content": "test message"}]
    mock_buddy._save_profile.assert_called_once()


# -----------------------------------------------------------------------
# Streamlit deprecation checks
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------
# Breathing exercise trigger logic tests
# -----------------------------------------------------------------------

def _breathing_should_offer(det_emotion: str, risk_level: str, breathing_active: bool) -> bool:
    """Mirror of the _should_offer computation in ui_app.py render_chat_tab()."""
    return (
        (det_emotion == 'anxiety' or risk_level == 'high')
        and det_emotion != 'crisis'
        and not breathing_active
    )


def test_breathing_active_initialised_false():
    """breathing_active session state key must default to False."""
    try:
        import streamlit as st
    except ImportError:
        return
    importlib.import_module('ui_app')
    assert st.session_state.get('breathing_active') is False


def test_breathing_should_offer_for_anxiety_emotion():
    """_should_offer must be True when emotion is anxiety (even at low risk)."""
    assert _breathing_should_offer('anxiety', 'low', False) is True


def test_breathing_should_offer_for_high_risk():
    """_should_offer must be True when risk_level is high (any non-crisis emotion)."""
    assert _breathing_should_offer('sadness', 'high', False) is True


def test_breathing_should_not_offer_for_neutral_low_risk():
    """_should_offer must be False for neutral emotion and low risk."""
    assert _breathing_should_offer('neutral', 'low', False) is False


def test_breathing_should_not_offer_when_already_active():
    """_should_offer must be False when breathing exercise is already running."""
    assert _breathing_should_offer('anxiety', 'high', True) is False


def test_breathing_should_not_offer_for_crisis():
    """_should_offer must be False even when anxiety/high-risk during crisis."""
    assert _breathing_should_offer('crisis', 'high', False) is False


# -----------------------------------------------------------------------
# Streamlit deprecation checks
# -----------------------------------------------------------------------

def test_no_deprecated_use_container_width():
    """ui_app.py and ui/ must not use the deprecated use_container_width arg.

    Streamlit >= 1.54 replaces the old parameter with width='stretch'/'content'.
    """
    import pathlib
    # Only check the production UI source files, not test or doc files
    _DEPRECATED = 'use_container_width'
    repo = pathlib.Path(__file__).resolve().parent
    targets = [repo / 'ui_app.py'] + list((repo / 'ui').rglob('*.py'))
    violations = []
    for py_file in targets:
        if not py_file.exists():
            continue
        text = py_file.read_text(encoding='utf-8', errors='ignore')
        for lineno, line in enumerate(text.splitlines(), 1):
            if _DEPRECATED in line:
                violations.append(f"{py_file.name}:{lineno}: {line.strip()}")
    assert violations == [], (
        "Deprecated parameter found:\n" + "\n".join(violations)
    )


# -----------------------------------------------------------------------
# Emotion prediction insight tests
# -----------------------------------------------------------------------

def test_emotion_predictor_imported_in_ui_app():
    """ui_app.py must import predict_next_emotion and detect_trend."""
    import pathlib
    text = (pathlib.Path(__file__).resolve().parent / 'ui_app.py').read_text(encoding='utf-8')
    assert 'from emotion_predictor import predict_next_emotion, detect_trend' in text


def test_predict_next_emotion_basic():
    """predict_next_emotion returns the repeating last emotion."""
    from emotion_predictor import predict_next_emotion
    assert predict_next_emotion(['sadness', 'sadness']) == 'sadness'


def test_predict_next_emotion_most_common():
    """predict_next_emotion returns the most frequent emotion in history."""
    from emotion_predictor import predict_next_emotion
    assert predict_next_emotion(['joy', 'sadness', 'sadness', 'anxiety']) == 'sadness'


def test_predict_next_emotion_empty_returns_neutral():
    """predict_next_emotion returns 'neutral' for empty history."""
    from emotion_predictor import predict_next_emotion
    assert predict_next_emotion([]) == 'neutral'


def test_detect_trend_increasing_stress():
    """detect_trend returns 'increasing stress' for a negative window."""
    from emotion_predictor import detect_trend
    assert detect_trend(['anxiety', 'sadness', 'anger']) == 'increasing stress'


def test_detect_trend_improving():
    """detect_trend returns 'improving' for a positive window."""
    from emotion_predictor import detect_trend
    assert detect_trend(['joy', 'neutral', 'joy']) == 'improving'


def test_detect_trend_stable():
    """detect_trend returns 'stable' for a mixed window."""
    from emotion_predictor import detect_trend
    assert detect_trend(['sadness', 'joy']) == 'stable'


def test_detect_trend_empty_returns_stable():
    """detect_trend returns 'stable' for empty history."""
    from emotion_predictor import detect_trend
    assert detect_trend([]) == 'stable'
