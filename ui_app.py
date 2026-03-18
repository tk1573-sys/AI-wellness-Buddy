"""
Web UI for AI Wellness Buddy using Streamlit.
Multi-tab layout: Chat | Emotional Trends | Risk Dashboard | Weekly Report
Supports bilingual Tamil & English with Tanglish and voice input/output.
Premium glassmorphism theme with Plotly visualizations.
Run with: streamlit run ui_app.py
"""

import streamlit as st
from datetime import datetime
from wellness_buddy import WellnessBuddy
from user_profile import UserProfile
from data_store import DataStore
from prediction_agent import PredictionAgent
from voice_handler import VoiceHandler
from auth_manager import AuthManager
from session_manager import SessionManager
from emotion_predictor import predict_next_emotion, detect_trend
import config
import os

# Modular UI components
from ui.theme import get_theme_css
from ui.charts import (
    create_sentiment_chart, create_emotion_donut, create_risk_gauge,
    create_history_chart, create_weekly_chart, create_sparkline,
    create_moving_average_chart, create_risk_history_chart, create_emotion_heatmap,
    create_emotion_journey_line, create_stress_intensity_gauge,
    create_emotion_probability_bar, create_cdi_gauge,
    EMO_COLORS, _HEATMAP_EMOTIONS,
)
from ui.layout import (
    render_hero_section, render_wellness_illustration_large,
    render_chat_header, render_user_avatar, render_risk_badge,
    render_concern_badge,
    render_session_info_card, render_streak_card, render_waveform_section,
    render_session_summary_card, render_emotion_flag,
    render_emotional_avatar, render_wellness_sidebar_card,
    EMO_ICONS, EMO_BUBBLE_CLASS, CONCERN_ICONS,
    RISK_COLOUR, RISK_LEVEL_VALUES, SOUND_LABELS,
)
from ui.animations import (
    ambient_sound_html, ambient_stop_html, TYPING_INDICATOR_HTML,
    canvas_particles_html, breathing_circle_html, guided_breathing_message_html,
    breathing_exercise_html,
)
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="AI Wellness Buddy",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------
# Session state initialisation
# -----------------------------------------------------------------------
for key, default in [
    ('buddy', None),
    ('session_mgr', None),           # SessionManager instance
    ('session_id', None),            # unique id for current session
    ('messages', []),
    ('chat_history', []),            # structured {"role","content"} history
    ('emotion_history', []),         # per-session emotion snapshots
    ('risk_history', []),            # per-session risk scores
    ('last_response', None),         # anti-repeat tracking
    ('last_response_meta', {}),
    ('last_user_input', None),       # dedup: skip reprocessing on rerun
    ('user_id', None),
    ('profile_loaded', False),
    ('show_load', False),
    ('show_create', False),
    ('show_profile_menu', False),
    ('tts_enabled', True),
    ('voice_handler', None),
    ('last_voice_bytes', None),
    ('calm_music_enabled', False),
    ('breathing_active', False),     # user-initiated breathing exercise
    ('authenticated', False),
    ('current_user', None),
    ('failed_attempts', 0),
    ('ui_theme', 'calm'),            # calm | clinical | modern
    ('dark_mode', False),
    ('ambient_sound', 'deep_focus'), # deep_focus | calm_waves | soft_rain
    ('research_logging_enabled', False),
    ('background_theme', 'calm_gradient'),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if (
    not st.session_state.get('_theme_aliases_migrated', False)
    and st.session_state.get('background_theme') in ('soft_aurora', 'ocean_waves')
):
    if st.session_state.get('background_theme') == 'soft_aurora':
        st.session_state.background_theme = 'aurora'
    elif st.session_state.get('background_theme') == 'ocean_waves':
        st.session_state.background_theme = 'ocean'
    st.session_state['_theme_aliases_migrated'] = True


_JOURNEY_TAB_HEATMAP_BASELINE_INTENSITY = 0.05
_JOURNEY_TAB_HEATMAP_MIN_INTENSITY = 0.2
_JOURNEY_TAB_HEATMAP_MAX_INTENSITY = 1.0
_JOURNEY_TAB_HEATMAP_RISK_BOOST = 0.2
_BACKGROUND_SCENES = ["calm_gradient", "night_sky", "aurora", "ocean"]
_UI_THEMES = ["calm", "modern", "clinical"]
_BREATHING_WIDGET_HEIGHT = 280

# Concern level badge colours and emoji icons
_CONCERN_BADGE_COLORS = {
    'low': '#4ade80', 'medium': '#facc15',
    'high': '#f97316', 'critical': '#ef4444',
}
_CONCERN_EMOJI = {
    'low': '🟢', 'medium': '🟡', 'high': '🟠', 'critical': '🔴',
}


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _generate_calming_tone(duration_s: float = 12.0, freq_hz: float = 174.0) -> bytes:
    """Generate a soft calming sine-wave tone as WAV bytes for st.audio().

    Uses a low Solfeggio frequency (174 Hz) with gentle fade-in/out.
    Returns raw WAV data suitable for ``st.audio()``.
    """
    import io
    import wave
    try:
        import numpy as np
    except ImportError:
        return b""
    sample_rate = 22050
    n_samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    # Generate gentle sine wave with volume envelope (fade in/out)
    amplitude = 0.15
    envelope = np.ones(n_samples)
    fade_len = int(sample_rate * 1.5)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    samples = (amplitude * envelope * np.sin(2 * np.pi * freq_hz * t))
    int_samples = np.int16(samples * 32767)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    return buf.getvalue()


def _coarse_to_fine_emotion(label: str) -> str:
    """Map coarse/legacy emotion labels to fine-grained display labels."""
    if label in ('positive',):
        return 'joy'
    if label in ('negative', 'distress'):
        return 'sadness'
    return label


def _count_emotions_from_history(history: list) -> dict[str, int]:
    """Aggregate emotion counts from user emotional history snapshots."""
    counts: dict[str, int] = {}
    for snap in history:
        ed = snap.get('emotion_data', {}) or {}
        emo = ed.get('primary_emotion') or ed.get('emotion', 'neutral')
        emo = _coarse_to_fine_emotion(emo)
        counts[emo] = counts.get(emo, 0) + 1
    return counts


def init_buddy():
    """Initialize wellness buddy instance"""
    if st.session_state.buddy is None:
        st.session_state.buddy = WellnessBuddy()
        st.session_state.buddy.data_store = DataStore()
    if st.session_state.voice_handler is None:
        st.session_state.voice_handler = VoiceHandler()
    if st.session_state.get('session_mgr') is None:
        st.session_state.session_mgr = SessionManager(
            st.session_state.buddy.data_store,
        )


def load_profile(username):
    """Load existing profile after successful authentication."""
    init_buddy()
    st.session_state.user_id = username
    st.session_state.current_user = username
    st.session_state.buddy._load_existing_profile(username)

    # Restore persisted session (chat + emotion + risk history)
    mgr = st.session_state.session_mgr
    session = mgr.load_session(username)
    if session is None:
        session = mgr.create_session(username)
        # Seed from legacy profile chat_history if present
        profile = st.session_state.buddy.user_profile
        if profile:
            legacy = profile.load_chat_history()
            if legacy:
                session["chat_history"] = legacy
                mgr.save_session(username, chat_history=legacy)
    st.session_state.session_id = session["session_id"]
    st.session_state.chat_history = session["chat_history"]
    st.session_state.emotion_history = session["emotion_history"]
    st.session_state.risk_history = session["risk_history"]
    # Populate messages from the persisted chat_history, preserving all fields
    # (including emotion/confidence/concern_level) so badges render correctly.
    # Only initialise once; do not overwrite an already-populated messages list
    # to prevent rerun duplication.
    if not st.session_state["messages"]:
        st.session_state["messages"] = [dict(m) for m in session["chat_history"]]
    st.session_state.profile_loaded = True
    st.session_state.authenticated = True
    st.rerun()


# -----------------------------------------------------------------------
# Profile setup screens — secure login / registration
# -----------------------------------------------------------------------

def show_profile_setup():
    """Show secure login / registration interface (no public user list)."""
    # Show end-of-session summary card if just ended
    summary_html = st.session_state.pop('_session_summary_html', None)
    if summary_html:
        st.markdown(summary_html, unsafe_allow_html=True)

    # Premium hero section with illustration panel
    hero_col, art_col = st.columns([3, 2])
    with hero_col:
        st.markdown(render_hero_section(), unsafe_allow_html=True)
    with art_col:
        st.markdown(render_wellness_illustration_large(), unsafe_allow_html=True)

    # Check brute-force lockout
    if AuthManager.is_locked_out(st.session_state.failed_attempts):
        st.error(
            "🔒 Too many failed login attempts. Please restart the application to try again."
        )
        return

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", width="stretch"):
            st.session_state.show_load = True
            st.session_state.show_create = False
    with col2:
        if st.button("Create Account", width="stretch"):
            st.session_state.show_create = True
            st.session_state.show_load = False

    if st.session_state.get('show_load', False):
        _render_login_form()

    if st.session_state.get('show_create', False):
        create_new_profile()


def _render_login_form():
    """Render username + password login form."""
    with st.form("login_form"):
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        submitted = st.form_submit_button("Sign In")

    if submitted:
        if not username or not password:
            st.warning("Please enter both username and password.")
            return

        data_store = DataStore()
        if not data_store.user_exists(username):
            st.error("Invalid username or password.")
            st.session_state.failed_attempts += 1
            return

        # Load profile data and verify password
        data = data_store.load_user_data(username)
        temp_profile = UserProfile(username)
        temp_profile.load_from_data(data)

        if temp_profile.verify_password(password):
            st.session_state.failed_attempts = 0
            # Persist profile — legacy SHA-256 hashes are auto-migrated to bcrypt
            # inside verify_password, so we always save after successful login.
            data_store.save_user_data(username, temp_profile.get_profile())
            load_profile(username)
        else:
            st.session_state.failed_attempts += 1
            remaining = AuthManager.MAX_FAILED_ATTEMPTS - st.session_state.failed_attempts
            if remaining > 0:
                st.error(f"Invalid username or password. {remaining} attempt(s) remaining.")
            else:
                st.error("🔒 Too many failed attempts. Login locked for this session.")



def create_new_profile():
    """Create new profile interface with password registration."""
    with st.form("new_profile"):
        username = st.text_input("Choose a username (private):", key="new_username")
        password = st.text_input(
            "Choose a password (min 8 characters):", type="password", key="new_password"
        )
        confirm_password = st.text_input(
            "Confirm password:", type="password", key="confirm_password"
        )
        gender = st.selectbox("How do you identify?",
                              ["Skip", "Female", "Male", "Other"])

        marital_status = st.selectbox(
            "Relationship / marital status:",
            ["Skip", "Single", "Married", "Divorced", "Widowed", "In a relationship", "Other"]
        )

        living_situation = st.selectbox(
            "Current living situation:",
            ["Skip", "Alone", "With family", "With partner", "With roommates",
             "In hostel / PG", "Other"],
            help="Helps me respond with awareness of your home environment."
        )

        family_responsibilities = st.selectbox(
            "Family responsibilities:",
            ["Skip", "None", "Caretaker (elderly / sick family member)",
             "Single parent", "Breadwinner / main earner",
             "Supporting siblings", "Multiple responsibilities", "Other"],
            help="Understanding your responsibilities helps me acknowledge the load you carry."
        )

        occupation = st.selectbox(
            "Occupation / work situation:",
            ["Skip", "Student", "Employed (full-time)", "Employed (part-time)",
             "Self-employed", "Unemployed / job-seeking", "Homemaker",
             "On leave / career break", "Retired", "Other"],
            help="Work stress is a significant factor in emotional wellbeing."
        )

        response_style = st.selectbox(
            "Preferred response style:",
            ["Balanced", "Short", "Detailed"],
            help="Short: brief supportive replies. Detailed: fuller exploration. Balanced: in between."
        )

        language_preference = st.selectbox(
            "Preferred language / மொழி:",
            ["English", "Tamil (தமிழ்)", "Bilingual (Tamil + English)"],
            help=(
                "English: responses in English only. "
                "Tamil: responses in Tamil script. "
                "Bilingual: Tamil + English mixed (best for Tanglish speakers)."
            ),
        )
        _LANG_MAP = {
            "English": "english",
            "Tamil (தமிழ்)": "tamil",
            "Bilingual (Tamil + English)": "bilingual",
        }

        show_safety = False
        if gender == "Female":
            st.info("💙 Specialized support resources for women are available.")
            safe_family = st.radio("Do you feel safe with your family/guardians?",
                                   ["Skip", "Yes", "No"])
            if safe_family == "No":
                show_safety = True
                st.warning("🛡️ I understand. Your safety is paramount. "
                           "I will guide you toward trusted friends and women's organizations.")

        family_bg = st.text_area(
            "Family background / situation (optional):",
            key="family_bg", height=68,
            help="A brief description helps me respond more sensitively."
        )

        trauma_info = st.text_area(
            "Any trauma or significant loss you'd like me to be aware of? (optional):",
            key="trauma_info", height=68,
            help="This stays completely private and helps me support you with extra care."
        )

        triggers_info = st.text_input(
            "Topics or words that are especially sensitive for you (comma-separated, optional):",
            key="triggers_info",
            help="I will be especially gentle whenever these come up."
        )

        submitted = st.form_submit_button("Create Profile")

        if submitted and username:
            # Validate password
            if not password or not confirm_password:
                st.error("Please enter and confirm a password.")
                return
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            ok, msg = AuthManager.validate_password_strength(password)
            if not ok:
                st.error(msg)
                return

            # Check if username already exists
            data_store = DataStore()
            if data_store.user_exists(username):
                st.error("Username already taken. Please choose a different one.")
                return

            init_buddy()
            st.session_state.user_id = username
            st.session_state.current_user = username
            st.session_state.buddy.user_id = username
            st.session_state.buddy.user_profile = UserProfile(username)

            # Set bcrypt password
            st.session_state.buddy.user_profile.set_password(password)

            if gender != "Skip":
                st.session_state.buddy.user_profile.set_gender(gender.lower())
            if show_safety:
                st.session_state.buddy.user_profile.add_unsafe_contact('family/guardians')
            if marital_status != "Skip":
                st.session_state.buddy.user_profile.set_relationship_status(marital_status.lower())
            if living_situation != "Skip":
                st.session_state.buddy.user_profile.set_living_situation(living_situation)
            if family_responsibilities != "Skip":
                st.session_state.buddy.user_profile.set_family_responsibilities(
                    family_responsibilities)
            if occupation != "Skip":
                st.session_state.buddy.user_profile.set_occupation(occupation)
            if response_style != "Balanced":
                st.session_state.buddy.user_profile.set_response_style(response_style.lower())
            lang_val = _LANG_MAP.get(language_preference, 'english')
            st.session_state.buddy.user_profile.set_language_preference(lang_val)
            if family_bg.strip():
                st.session_state.buddy.user_profile.set_family_background(family_bg.strip())
            if trauma_info.strip():
                st.session_state.buddy.user_profile.add_trauma_history(trauma_info.strip())
            if triggers_info.strip():
                for t in triggers_info.split(','):
                    t = t.strip()
                    if t:
                        st.session_state.buddy.user_profile.add_personal_trigger(t)

            st.session_state.buddy._save_profile()
            st.session_state.profile_loaded = True
            st.session_state.authenticated = True
            st.success("✓ Profile created successfully!")
            st.rerun()


# -----------------------------------------------------------------------
# Helpers: voice input & TTS output
# -----------------------------------------------------------------------

def _get_lang_pref() -> str:
    """Return current user's language preference or default."""
    try:
        return st.session_state.buddy.user_profile.get_language_preference()
    except Exception:
        return 'english'


def _play_tts(text: str):
    """Render a gTTS audio player for *text* if TTS is enabled."""
    if not st.session_state.get('tts_enabled', False):
        return
    vh: VoiceHandler = st.session_state.voice_handler
    if vh is None or not vh.tts_available:
        return
    lang_pref = _get_lang_pref()
    audio_bytes = vh.text_to_speech(text, lang_pref)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=False)


def _handle_voice_input():
    """Render compact inline voice recorder and return transcribed text or None.

    Uses session-state deduplication (``last_voice_bytes``) to ensure each
    recording is processed exactly once, preventing the auto-trigger loop
    caused by Streamlit reruns.
    """
    try:
        from audio_recorder_streamlit import audio_recorder
    except ImportError:
        st.caption("🎤 voice unavailable")
        return None

    vh: VoiceHandler = st.session_state.voice_handler
    if vh is None or not vh.stt_available:
        st.caption("🎤 mic unavailable")
        return None

    # Minimum bytes for a viable audio sample (~1 second at 16-bit 8kHz mono)
    MIN_AUDIO_BYTES = 1000

    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#9B8CFF",
        icon_size="2x",
        pause_threshold=2.0,
        key="voice_recorder",
    )

    # Deduplicate: only process if this is a *new* recording
    if (
        audio_bytes
        and len(audio_bytes) > MIN_AUDIO_BYTES
        and audio_bytes != st.session_state.get('last_voice_bytes')
    ):
        st.session_state.last_voice_bytes = audio_bytes
        lang_pref = _get_lang_pref()
        with st.spinner("Transcribing…"):
            transcript = vh.transcribe_audio(audio_bytes, lang_pref)
        if transcript:
            st.success(f"Transcribed: *{transcript}*")
            return transcript
        else:
            st.warning("Could not transcribe audio. Please try again or type your message.")
    return None


# -----------------------------------------------------------------------
# Main chat interface (tab 1)
# -----------------------------------------------------------------------

def render_chat_tab():
    """Render the chat tab with text input, voice input, and TTS output."""
    lang_pref = _get_lang_pref()

    # Language badge
    _LANG_LABELS = {
        'english': '🇬🇧 English',
        'tamil': '🇮🇳 Tamil (தமிழ்)',
        'bilingual': '🇮🇳🇬🇧 Bilingual',
    }
    st.caption(f"Language: {_LANG_LABELS.get(lang_pref, lang_pref)}")

    # Determine current dominant emotion for reactive bubble color
    buddy = st.session_state.buddy
    _dom_emotion = 'neutral'
    _summary = buddy.pattern_tracker.get_pattern_summary() if buddy else None
    if _summary:
        _dist = _summary.get('emotion_distribution', {})
        if _dist:
            _dom_emotion = max(_dist, key=_dist.get)
    # Inject emotion-reactive CSS class
    st.markdown(render_emotion_flag(_dom_emotion), unsafe_allow_html=True)

    # Add a welcome message when there's no chat history yet
    if not st.session_state["messages"]:
        user_name = st.session_state.user_id or "friend"
        greeting = (
            f"Hello **{user_name}** 👋  \n"
            "I'm your Wellness Buddy — a safe, confidential space for emotional support.  \n"
            "Share how you're feeling, and I'll do my best to listen and help."
        )
        st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.session_state["messages"].append({"role": "assistant", "content": greeting})

    # --- Dedicated container: render from session_state["messages"] only.
    #     Using a single list prevents UI duplication during Streamlit reruns.
    chat_container = st.container()

    with chat_container:
        for idx, message in enumerate(st.session_state["messages"]):
            with st.chat_message(message["role"]):
                # Show emotion badge with confidence and concern level beside user messages
                _msg_emo = message.get("emotion", "")
                if _msg_emo and message["role"] == "user":
                    _icon = EMO_ICONS.get(_msg_emo, "")
                    _msg_conf = message.get("confidence", 0.0)
                    _msg_concern = message.get("concern_level", "")
                    _badge_color = _CONCERN_BADGE_COLORS.get(_msg_concern, '#9B8CFF')
                    _badge_parts = [f"{_icon} {_msg_emo.capitalize()}"]
                    if _msg_conf:
                        _badge_parts.append(f"{_msg_conf:.0%}")
                    if _msg_concern:
                        _badge_parts.append(_msg_concern.capitalize())
                    _badge_text = " · ".join(_badge_parts)
                    st.markdown(
                        f"{message['content']}  \n"
                        f'<span style="display:inline-block;background:{_badge_color}22;'
                        f'color:{_badge_color};border:1px solid {_badge_color}44;'
                        f'border-radius:12px;padding:2px 10px;font-size:0.8rem;'
                        f'margin-top:4px;">{_badge_text}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(message["content"])
                # Replay TTS button for assistant messages
                if message["role"] == "assistant" and st.session_state.get('tts_enabled', False):
                    vh: VoiceHandler = st.session_state.voice_handler
                    if vh and vh.tts_available:
                        if st.button("🔊", key=f"tts_{idx}",
                                     help="Listen to this response"):
                            _play_tts(message["content"])

    # ---- Emotion Result Panel: show analytics for the latest response ----
    _meta = st.session_state.get('last_response_meta') or {}
    _probs = _meta.get('emotion_probabilities', {})
    _expl = _meta.get('explanation', '')
    _det_emotion = _meta.get('emotion', '')
    _xai = _meta.get('xai_explanation', {})
    _concern = _meta.get('concern_level', '')
    _emo_conf = _meta.get('emotion_confidence', 0.0)
    if _probs and _det_emotion:
        _conf = _xai.get('confidence', _probs.get(_det_emotion, 0))
        # Inline concern + confidence badges above the expander
        _concern_html = render_concern_badge(_concern) if _concern else ''
        _conf_pct = f"{_emo_conf:.0%}" if 'emotion_confidence' in _meta else f"{_conf:.0%}"
        st.markdown(
            f"{_concern_html}"
            f"&nbsp; `🎯 Confidence {_conf_pct}`"
            f"&nbsp; `{EMO_ICONS.get(_det_emotion, '')} {_det_emotion.capitalize()}`",
            unsafe_allow_html=True,
        )
        _concern_display = f"  |  Concern: **{_concern.capitalize()}**" if _concern else ""
        with st.expander(
            f"🔬 Emotion Analysis — **{_det_emotion.capitalize()}**"
            f"  (confidence {_conf:.1%}){_concern_display}",
            expanded=False,
        ):
            chart_col, info_col = st.columns([3, 2])
            with chart_col:
                st.plotly_chart(
                    create_emotion_probability_bar(_probs),
                    width="stretch",
                )
            with info_col:
                st.markdown(f"**Detected emotion:** {_det_emotion.capitalize()}")
                st.markdown(f"**Confidence:** {_conf:.1%}")
                if _concern:
                    st.markdown(
                        f"**Concern level:** {render_concern_badge(_concern)}",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Concern level:** {_CONCERN_EMOJI.get(_concern, '⬜')} {_concern.capitalize()}")
                # XAI key indicators
                indicators = _xai.get('key_indicators', [])
                if indicators:
                    st.markdown("**Key indicators:**")
                    for kw in indicators:
                        st.markdown(f"- {kw}")
                elif _expl:
                    st.markdown(f"**Explanation:** {_expl}")
                # Sentiment contribution
                _sent = _xai.get('sentiment_contribution', {})
                if _sent:
                    st.markdown(
                        f"**Sentiment:** {_sent.get('influence', 'neutral')} "
                        f"(polarity {_sent.get('polarity', 0):.2f})"
                    )
                # Model source
                _src = _xai.get('model_source', '')
                if _src:
                    st.caption(f"Model: {_src}")
                # Distress keywords (backward compat)
                kw = _meta.get('distress_keywords', [])
                if kw:
                    st.markdown(f"**Distress keywords:** {', '.join(kw)}")

    # ---- Crisis resources: show immediately when crisis detected ----
    if _det_emotion == 'crisis':
        st.error(
            "🆘 **Crisis Resources — Please reach out now**\n\n"
            "- **988 Suicide & Crisis Lifeline**: Call or text **988** (24/7)\n"
            "- **Crisis Text Line**: Text **HOME** to **741741**\n"
            "- **Emergency**: Call **911**\n\n"
            "You are not alone. Help is available right now. 💙"
        )

    # ---- Escalation warning ----
    _escalation = _meta.get('escalation', {})
    if _escalation.get('escalation_detected'):
        st.warning(_escalation.get('warning', ''))

    # ---- Emotion prediction insight ----
    _emo_labels = [
        e['emotion'] for e in st.session_state.get('emotion_history', [])
        if isinstance(e, dict) and e.get('emotion')
    ]
    if _emo_labels:
        _next_emotion = predict_next_emotion(_emo_labels)
        _trend = detect_trend(_emo_labels)
        st.info(
            f"🔮 **Predicted next emotion:** {_next_emotion.capitalize()} "
            f" | 📈 **Trend:** {_trend.capitalize()}"
        )

    # ---- Intervention recommendations ----
    _interventions = _meta.get('interventions', {})
    _intervention_level = _interventions.get('level', '')
    if _intervention_level in ('moderate', 'high', 'critical'):
        _inter_msg = _interventions.get('supportive_message', '')
        if _inter_msg:
            st.info(f"💡 {_inter_msg}")

    # ---- Breathing exercise: triggered by anxiety emotion or high risk ----
    _risk_level = _meta.get('risk_level', 'low')
    _should_offer = (
        (_det_emotion == 'anxiety' or _risk_level == 'high')
        and _det_emotion != 'crisis'
        and not st.session_state.get('breathing_active', False)
    )
    if _should_offer:
        st.info(
            "😌 Anxiety or elevated risk detected. Would you like to try a calming breathing exercise?"
        )
        if st.button("🫁 Start Breathing Exercise", key="start_breathing"):
            st.session_state.breathing_active = True
            st.rerun()

    if st.session_state.get('breathing_active', False):
        components.html(breathing_exercise_html(), height=_BREATHING_WIDGET_HEIGHT)
        _vol = st.session_state.get('_calm_volume', 0.03)
        _sound = st.session_state.get('ambient_sound', 'deep_focus')
        st.markdown(ambient_sound_html(_sound, _vol), unsafe_allow_html=True)
        # Calming audio (st.audio for browsers that block Web Audio autoplay)
        _tone = _generate_calming_tone()
        if _tone:
            st.audio(_tone, format="audio/wav")
        if st.button("✖ Stop Breathing Exercise", key="stop_breathing"):
            st.session_state.breathing_active = False
            st.markdown(ambient_stop_html(), unsafe_allow_html=True)
            st.rerun()

    # Inline voice mic near chat input
    feedback_col, mic_col = st.columns([11, 1])
    with mic_col:
        voice_transcript = _handle_voice_input()
    if voice_transcript and voice_transcript != st.session_state.last_user_input:
        with feedback_col:
            st.caption(f"🎤 *{voice_transcript}*")
        _add_chat_message("user", voice_transcript)
        # Typing indicator (cleared after response)
        typing_placeholder = st.empty()
        with typing_placeholder.chat_message("assistant"):
            st.markdown(TYPING_INDICATOR_HTML, unsafe_allow_html=True)
        response = st.session_state.buddy.respond(
            voice_transcript,
            context=st.session_state.chat_history,
            options={
                'calm_mode_active': st.session_state.get('calm_music_enabled', False),
                'research_logging': st.session_state.get('research_logging_enabled', False),
            },
        )
        typing_placeholder.empty()
        _add_chat_message("assistant", response)
        st.session_state.last_response = response
        st.session_state.last_response_meta = st.session_state.buddy.get_last_response_metadata()
        # Tag the user message with the detected emotion for badge display
        _tag_last_user_emotion(st.session_state.last_response_meta)
        _track_session_metadata(st.session_state.last_response_meta)
        # Do NOT auto-enable calm mode; breathing button shown separately
        st.session_state.last_user_input = voice_transcript
        _play_tts(response)
        st.rerun()

    # Text chat input
    placeholder = {
        'tamil':     'உங்கள் உணர்வுகளை பகிர்ந்துகொள்ளுங்கள்…',
        'bilingual': 'Share / சொல்லுங்க…',
    }.get(lang_pref, 'Share how you\'re feeling…')

    if prompt := st.chat_input(placeholder):
        if prompt != st.session_state.last_user_input:
            _add_chat_message("user", prompt)
            response = st.session_state.buddy.respond(
                prompt,
                context=st.session_state.chat_history,
                options={
                    'calm_mode_active': st.session_state.get('calm_music_enabled', False),
                    'research_logging': st.session_state.get('research_logging_enabled', False),
                },
            )
            _add_chat_message("assistant", response)
            st.session_state.last_response = response
            st.session_state.last_response_meta = st.session_state.buddy.get_last_response_metadata()
            # Tag the user message with the detected emotion for badge display
            _tag_last_user_emotion(st.session_state.last_response_meta)
            _track_session_metadata(st.session_state.last_response_meta)
            # Do NOT auto-enable calm mode; only mark that breathing was suggested
            # so the UI can present the opt-in button
            st.session_state.last_user_input = prompt
            if st.session_state.get('tts_enabled', False):
                _play_tts(response)
            st.rerun()


def _add_chat_message(role, content, emotion=None):
    """Append a message to both chat_history and the messages list.

    When *emotion* is provided it is stored alongside the message so the
    Chat tab can display an emotion badge next to the user's text.

    The updated chat history is also persisted to the user profile so it
    survives page reloads and re-logins.
    """
    entry = {"role": role, "content": content}
    if emotion:
        entry["emotion"] = emotion
    st.session_state.chat_history.append(entry)
    # messages is the primary rendering list; store full entry (including any
    # emotion fields) so badges render correctly when iterating messages.
    st.session_state["messages"].append(dict(entry))
    # Persist to user profile storage
    _persist_chat_history()


def _tag_last_user_emotion(meta: dict):
    """Retroactively annotate the most recent *user* message with the
    emotion detected by the pipeline so a badge can be rendered."""
    emo = meta.get('emotion', '')
    if not emo:
        return
    confidence = meta.get('emotion_confidence', 0.0)
    concern = meta.get('concern_level', '')
    # Annotate both lists so that badges show whether rendering from
    # chat_history (backend context) or messages (primary render list).
    for store in (st.session_state.chat_history, st.session_state["messages"]):
        for msg in reversed(store):
            if msg["role"] == "user":
                msg["emotion"] = emo
                msg["confidence"] = confidence
                msg["concern_level"] = concern
                break


def _track_session_metadata(meta: dict):
    """Append emotion and risk snapshots from *meta* to session history.

    Called after each assistant response so that longitudinal analysis has
    a record of every interaction in the current session.
    """
    now = datetime.now().isoformat()
    emo = meta.get('emotion')
    if emo:
        st.session_state.emotion_history.append({
            'timestamp': now,
            'emotion': emo,
            'confidence': meta.get('emotion_confidence', 0.0),
            'concern_level': meta.get('concern_level', 'low'),
        })
    risk_score = meta.get('risk_score')
    risk_level = meta.get('risk_level')
    if risk_score is not None or risk_level is not None:
        st.session_state.risk_history.append({
            'timestamp': now,
            'risk_score': float(risk_score) if risk_score is not None else 0.0,
            'risk_level': risk_level or 'low',
        })


def _persist_chat_history():
    """Save current session state to the user profile on disk.

    Persists chat_history, emotion_history, and risk_history via
    :class:`SessionManager`.  Errors are silently suppressed so that a
    disk-write failure does not interrupt the ongoing conversation.
    """
    buddy = st.session_state.get('buddy')
    mgr = st.session_state.get('session_mgr')
    user_id = st.session_state.get('user_id')
    if buddy and buddy.user_profile and user_id:
        try:
            if mgr:
                mgr.save_session(
                    user_id,
                    chat_history=st.session_state.chat_history,
                    emotion_history=st.session_state.get('emotion_history', []),
                    risk_history=st.session_state.get('risk_history', []),
                )
            else:
                # Fallback: legacy path (no session manager yet)
                buddy.user_profile.save_chat_history(st.session_state.chat_history)
                buddy._save_profile()
        except Exception:
            pass  # best-effort; chat continues in session_state


# -----------------------------------------------------------------------
# Emotional trends tab (tab 2)
# -----------------------------------------------------------------------

def render_trends_tab():
    """Render the Emotional Trends tab with Plotly charts"""
    st.subheader("📈 Emotional Trends")
    st.caption("REAL-TIME SENTIMENT TRACKING AND HISTORICAL MOOD ANALYSIS")

    buddy = st.session_state.buddy
    summary = buddy.pattern_tracker.get_pattern_summary()
    history = buddy.user_profile.get_emotional_history(days=30)

    # ---- Current session sentiment line (Plotly interactive) ----
    sentiments = list(buddy.pattern_tracker.sentiment_history)
    if sentiments:
        st.markdown("#### Current Session — Sentiment Over Messages")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(create_sentiment_chart(sentiments), width="stretch")
        with col2:
            if summary:
                ma = summary.get('moving_average', [])
                if len(ma) >= 2:
                    st.plotly_chart(create_moving_average_chart(ma), width="stretch")
                    st.caption("3-message moving average of sentiment")
    else:
        st.info("Start chatting to see your sentiment trend.")

    # ---- Emotion distribution (Plotly donut chart) ----
    if summary:
        dist = summary.get('emotion_distribution', {})
        if dist:
            st.markdown("#### Current Session — Emotion Distribution")
            emotions = sorted(dist.keys(), key=lambda e: -dist[e])
            counts = [dist[e] for e in emotions]
            colors = [EMO_COLORS.get(e, '#9B8CFF') for e in emotions]

            col_a, col_b = st.columns([1, 2])
            with col_a:
                for emo, cnt in zip(emotions, counts):
                    st.metric(label=emo.capitalize(), value=cnt)
            with col_b:
                st.plotly_chart(
                    create_emotion_donut(emotions, counts, colors),
                    width="stretch",
                )

    # ---- Emotion heatmap (intensity over conversation time) ----
    if summary and sentiments:
        dist = summary.get('emotion_distribution', {})
        if dist and len(sentiments) >= 2:
            st.markdown("#### Emotion Intensity Heatmap")
            # Build a simple heatmap from available data
            total = sum(dist.values()) or 1
            base_intensities = {e: dist.get(e, 0) / total for e in _HEATMAP_EMOTIONS}
            # Create per-message approximation using sentiment + distribution
            emotion_timeline = []
            for s_val in sentiments:
                seg = {}
                for emo in _HEATMAP_EMOTIONS:
                    base = base_intensities.get(emo, 0)
                    # Modulate by sentiment: positive sentiment boosts joy, negative boosts sadness
                    if emo in ('joy',):
                        seg[emo] = min(1.0, base + max(0, s_val) * 0.3)
                    elif emo in ('sadness', 'fear', 'crisis'):
                        seg[emo] = min(1.0, base + max(0, -s_val) * 0.3)
                    else:
                        seg[emo] = base
                emotion_timeline.append(seg)
            st.plotly_chart(
                create_emotion_heatmap(emotion_timeline),
                width="stretch",
            )

    # ---- Historical 30-day sentiment (Plotly interactive timeline) ----
    if history:
        st.markdown("#### Last 30 Days — Average Mood per Session")
        hist_data = []
        for snap in history:
            ss = snap.get('session_summary', {}) or {}
            avg = ss.get('average_sentiment', None)
            if avg is not None:
                hist_data.append(avg)

        if hist_data:
            predictor = PredictionAgent()
            forecast = predictor.predict_next_sentiment(hist_data)
            st.plotly_chart(
                create_history_chart(hist_data, forecast),
                width="stretch",
            )

            if forecast:
                st.info(
                    f"📡 **Next-session forecast** ({forecast['confidence']} confidence): "
                    f"{forecast['interpretation']} "
                    f"(predicted score: **{forecast['predicted_value']:.2f}**)"
                )
    else:
        st.info("Complete more sessions to see your 30-day mood history.")

    # ---- Volatility gauge ----
    if summary and summary.get('total_messages', 0) >= 2:
        st.markdown("#### Emotional Stability")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Volatility", f"{summary['volatility']:.2f}",
                      help="How much your mood fluctuates (0 = steady, 1 = very volatile)")
        col_s2.metric("Stability Index", f"{summary['stability_index']:.2f}",
                      help="1 = perfectly stable, 0 = highly volatile")
        col_s3.metric("Trend", summary['trend'].upper())

    # ---- Weekly emotional distribution pie chart ----
    history = buddy.user_profile.get_emotional_history(days=7)
    if history:
        weekly_counts = _count_emotions_from_history(history)
        if weekly_counts:
            st.markdown("#### Weekly Emotion Distribution")
            emo_labels = sorted(weekly_counts.keys(), key=lambda e: -weekly_counts[e])
            emo_vals = [weekly_counts[e] for e in emo_labels]
            emo_cols = [EMO_COLORS.get(e, '#9B8CFF') for e in emo_labels]
            st.plotly_chart(
                create_emotion_donut(emo_labels, emo_vals, emo_cols),
                width="stretch",
            )


def render_emotional_journey_tab():
    """Render the Emotional Journey insights panel.

    If no timeline exists yet, a contextual prompt is shown. Otherwise this
    tab displays a journey trend line, stress intensity gauge, heatmap
    timeline, and compact session metrics.
    """
    st.subheader("🌊 Emotional Journey")
    st.caption("EMOTION TRAJECTORY, HEATMAP TIMELINE, STRESS INTENSITY, AND SESSION SNAPSHOT")

    timeline = st.session_state.buddy.get_emotion_timeline()
    if not timeline:
        st.info("Start chatting to unlock your emotional journey insights.")
        return

    line_col, gauge_col = st.columns([2, 1])
    with line_col:
        st.plotly_chart(create_emotion_journey_line(timeline), width="stretch")
    with gauge_col:
        latest_risk = float(timeline[-1].get('risk_score', 0.0))
        st.plotly_chart(create_stress_intensity_gauge(latest_risk), width="stretch")

    heatmap_payload = []
    for point in timeline:
        emo = point.get('emotion', 'neutral')
        row = {key: _JOURNEY_TAB_HEATMAP_BASELINE_INTENSITY for key in _HEATMAP_EMOTIONS}
        if emo in row:
            row[emo] = min(
                _JOURNEY_TAB_HEATMAP_MAX_INTENSITY,
                max(
                    _JOURNEY_TAB_HEATMAP_MIN_INTENSITY,
                    float(point.get('risk_score', 0.0)) + _JOURNEY_TAB_HEATMAP_RISK_BOOST,
                ),
            )
        heatmap_payload.append(row)
    st.plotly_chart(create_emotion_heatmap(heatmap_payload), width="stretch")

    emotion_counts = {}
    for point in timeline:
        emo = point.get('emotion', 'neutral')
        emotion_counts[emo] = emotion_counts.get(emo, 0) + 1
    dominant = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
    avg_risk = sum(float(p.get('risk_score', 0.0)) for p in timeline) / len(timeline)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Conversation Turns", len(timeline))
    col_b.metric("Dominant Emotion", dominant.capitalize())
    col_c.metric("Avg Session Risk", f"{avg_risk:.2f}")


# -----------------------------------------------------------------------
# Risk Dashboard tab (tab 3)
# -----------------------------------------------------------------------


def render_risk_tab():
    """Render the Risk Dashboard tab with Plotly gauge"""
    st.subheader("⚠️ Risk Dashboard")
    st.caption("COMPOSITE RISK SCORING, CRISIS DETECTION, AND ESCALATION FORECAST")

    buddy = st.session_state.buddy
    summary = buddy.pattern_tracker.get_pattern_summary()

    if not summary or summary['total_messages'] == 0:
        st.info("Start a conversation to see your risk dashboard.")
        return

    risk_level = summary.get('risk_level', 'low')
    risk_score = summary.get('risk_score', 0.0)
    icon = RISK_COLOUR.get(risk_level, '⬜')

    st.markdown(f"### Current Risk Level: {icon} {risk_level.upper()}")

    # Plotly semi-circular animated risk dial
    st.plotly_chart(create_risk_gauge(risk_score, risk_level), width="stretch")

    # Clinical Distress Index (CDI) gauge
    _last_meta = st.session_state.get('last_response_meta') or {}
    _cdi = _last_meta.get('cdi', {})
    _cdi_score = _cdi.get('cdi_score', 0.0)
    _cdi_level = _cdi.get('cdi_level', 'low')
    if _cdi_score > 0:
        st.plotly_chart(create_cdi_gauge(_cdi_score, _cdi_level), width="stretch")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Risk Score", f"{risk_score:.2f}")
    col2.metric("Stability", f"{summary['stability_index']:.2f}")
    col3.metric("Volatility", f"{summary['volatility']:.2f}")
    col4.metric("Consecutive Distress", summary['consecutive_distress'])

    # Crisis alert
    if summary.get('crisis_count', 0) > 0:
        st.error(
            "🚨 **Crisis indicators have been detected.** "
            "Please reach out to the 988 Suicide & Crisis Lifeline (call or text **988**) "
            "or go to your nearest emergency room. You are not alone. 💙"
        )

    # Alert history
    alert_log = buddy.alert_system.get_alert_log()
    if alert_log:
        st.markdown("#### 🔔 Alert History")
        for alert in reversed(alert_log[-10:]):
            _sev = alert.get('severity', 'INFO')
            _ts = alert.get('timestamp', '')
            _ack = "✅" if alert.get('acknowledged') else "⏳"
            if isinstance(_ts, str):
                _ts_display = _ts[:19]
            else:
                _ts_display = _ts.strftime('%Y-%m-%d %H:%M') if hasattr(_ts, 'strftime') else str(_ts)
            st.markdown(f"- {_ack} **{_sev}** — {_ts_display}")

    # Risk history (last 30 days) — Plotly
    history = buddy.user_profile.get_emotional_history(days=30)
    risk_hist = []
    for snap in history:
        ed = snap.get('emotion_data', {}) or {}
        rl = ed.get('risk_level', None)
        if rl:
            risk_hist.append(RISK_LEVEL_VALUES.get(rl, 0.10))

    if risk_hist:
        st.markdown("#### 30-Day Risk Level History")
        st.plotly_chart(create_risk_history_chart(risk_hist), width="stretch")

        # Risk escalation forecast
        predictor = PredictionAgent()
        esc = predictor.predict_risk_escalation(risk_hist)
        if esc:
            if esc['will_escalate']:
                st.warning(f"📡 **Risk escalation forecast:** {esc['recommendation']}")
            else:
                st.success(f"📡 **Risk forecast:** {esc['recommendation']}")

    # Mood streak & badges
    streak = buddy.user_profile.get_mood_streak()
    badges = buddy.user_profile.get_badge_display()

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### 🔥 Mood Streak")
        st.metric("Consecutive Positive Sessions", streak)
        if streak >= 7:
            st.success("Amazing — 7+ positive sessions in a row! ⭐")
        elif streak >= 3:
            st.info("Great work — 3+ positive sessions in a row! 🔥")
        elif streak >= 1:
            st.info("You're building momentum! Keep it up.")

    with col_g2:
        st.markdown("#### 🏅 Wellness Badges")
        if badges:
            for name, desc in badges:
                st.success(f"**{name}** — {desc}")
        else:
            st.info("Complete sessions to earn wellness badges!")


# -----------------------------------------------------------------------
# Weekly Report tab (tab 4)
# -----------------------------------------------------------------------

def render_weekly_report_tab():
    """Render the Weekly Report tab with Plotly charts"""
    st.subheader("📋 Weekly Wellness Report")
    st.caption("7-DAY AGGREGATED WELLNESS SUMMARY WITH PREDICTIONS AND SUGGESTIONS")

    buddy = st.session_state.buddy
    report_text = buddy.generate_weekly_summary()

    st.markdown(report_text)

    # Quick KPIs from history
    history = buddy.user_profile.get_emotional_history(days=7)
    if history:
        sentiments = []
        risk_incidents = 0
        for snap in history:
            ss = snap.get('session_summary', {}) or {}
            avg = ss.get('average_sentiment', None)
            if avg is not None:
                sentiments.append(avg)
            ed = snap.get('emotion_data', {}) or {}
            if ed.get('risk_level') in ('high', 'critical'):
                risk_incidents += 1

        if sentiments:
            st.markdown("#### 7-Day Mood Chart")
            st.plotly_chart(create_weekly_chart(sentiments), width="stretch")

            # Forecasted mood trend
            if len(sentiments) >= 3:
                predictor = PredictionAgent()
                forecast = predictor.predict_next_sentiment(sentiments)
                if forecast:
                    st.markdown("#### Forecasted Mood Trend")
                    st.plotly_chart(
                        create_history_chart(sentiments, forecast),
                        width="stretch",
                    )
                    st.info(
                        f"📡 **Forecast** ({forecast['confidence']} confidence): "
                        f"{forecast['interpretation']} "
                        f"(predicted score: **{forecast['predicted_value']:.2f}**)"
                    )

        # Weekly emotion distribution
        weekly_emo_counts = _count_emotions_from_history(history)
        if weekly_emo_counts:
            st.markdown("#### Emotion Distribution Summary")
            emo_labels = sorted(weekly_emo_counts.keys(),
                                key=lambda e: -weekly_emo_counts[e])
            emo_vals = [weekly_emo_counts[e] for e in emo_labels]
            emo_cols = [EMO_COLORS.get(e, '#9B8CFF') for e in emo_labels]
            st.plotly_chart(
                create_emotion_donut(emo_labels, emo_vals, emo_cols),
                width="stretch",
            )

        col1, col2, col3 = st.columns(3)
        col1.metric("Sessions This Week", len(history))
        col2.metric("Risk Incidents", risk_incidents)
        col3.metric("Mood Streak", buddy.user_profile.get_mood_streak())


# -----------------------------------------------------------------------
# Profile management sidebar
# -----------------------------------------------------------------------

def show_profile_menu():
    """Show profile management menu"""
    with st.sidebar:
        st.markdown("### Profile Management")

        trusted = st.session_state.buddy.user_profile.get_trusted_contacts()
        st.write(f"Trusted contacts: {len(trusted)}")

        action = st.selectbox("Choose action:",
                              ["Cancel", "Add Trusted Contact", "View Trusted Contacts",
                               "View Personal History", "Add Trauma / Trigger",
                               "Change Response Style", "Change Language",
                               "Mark Family Unsafe", "Delete All Data"])

        if action == "Add Trusted Contact":
            with st.form("add_contact"):
                name = st.text_input("Name:")
                relationship = st.text_input("Relationship:")
                contact_info = st.text_input("Contact Info (optional):")
                if st.form_submit_button("Add"):
                    st.session_state.buddy.user_profile.add_trusted_contact(
                        name, relationship, contact_info if contact_info else None
                    )
                    st.session_state.buddy._save_profile()
                    st.success(f"✓ Added {name}")
                    st.session_state.show_profile_menu = False

        elif action == "View Trusted Contacts":
            if trusted:
                st.markdown("**💚 Your Trusted Contacts:**")
                for contact in trusted:
                    st.write(f"• {contact['name']} ({contact['relationship']})")
                    if contact.get('contact_info'):
                        st.write(f"  {contact['contact_info']}")
            else:
                st.info("No trusted contacts added yet")

        elif action == "View Personal History":
            profile = st.session_state.buddy.user_profile
            demographics = profile.get_profile().get('demographics', {})
            st.markdown("**📋 Your Personal History**")
            st.write(f"**Relationship:** {demographics.get('relationship_status', 'not set')}")
            st.write(f"**Living situation:** {demographics.get('living_situation', 'not set')}")
            st.write(f"**Family responsibilities:** {demographics.get('family_responsibilities', 'not set')}")
            st.write(f"**Occupation:** {demographics.get('occupation', 'not set')}")
            st.write(f"**Family background:** {demographics.get('family_background', 'not set')}")
            st.write(f"**Response style:** {profile.get_response_style()}")
            trauma = profile.get_trauma_history()
            if trauma:
                st.markdown("**Trauma records:**")
                for t in trauma:
                    st.write(f"• {t['description']}")
            else:
                st.info("No trauma records on file.")
            triggers = profile.get_personal_triggers()
            if triggers:
                st.markdown("**Personal triggers:**")
                st.write(", ".join(triggers))
            else:
                st.info("No personal triggers on file.")

        elif action == "Add Trauma / Trigger":
            with st.form("add_personal_history"):
                trauma_desc = st.text_area("Trauma or loss to record (optional):", height=68)
                trigger_input = st.text_input("Sensitive topic/word to add (optional):")
                if st.form_submit_button("Save"):
                    if trauma_desc.strip():
                        st.session_state.buddy.user_profile.add_trauma_history(trauma_desc.strip())
                    if trigger_input.strip():
                        st.session_state.buddy.user_profile.add_personal_trigger(trigger_input.strip())
                    st.session_state.buddy._save_profile()
                    st.success("✓ Personal history updated")
                    st.session_state.show_profile_menu = False

        elif action == "Change Response Style":
            current = st.session_state.buddy.user_profile.get_response_style()
            new_style = st.selectbox("Response style:", ["balanced", "short", "detailed"],
                                     index=["balanced", "short", "detailed"].index(current))
            if st.button("Save Style"):
                st.session_state.buddy.user_profile.set_response_style(new_style)
                st.session_state.buddy._save_profile()
                st.success(f"✓ Response style set to '{new_style}'")
                st.session_state.show_profile_menu = False

        elif action == "Change Language":
            current_lang = st.session_state.buddy.user_profile.get_language_preference()
            _LANG_OPTIONS = ["english", "tamil", "bilingual"]
            _LANG_DISPLAY = ["English", "Tamil (தமிழ்)", "Bilingual (Tamil + English)"]
            idx = _LANG_OPTIONS.index(current_lang) if current_lang in _LANG_OPTIONS else 0
            new_lang_display = st.selectbox("Language / மொழி:", _LANG_DISPLAY, index=idx)
            new_lang = _LANG_OPTIONS[_LANG_DISPLAY.index(new_lang_display)]
            if st.button("Save Language"):
                st.session_state.buddy.user_profile.set_language_preference(new_lang)
                st.session_state.buddy._save_profile()
                st.success(f"✓ Language set to '{new_lang_display}'")
                st.session_state.show_profile_menu = False

        elif action == "Mark Family Unsafe":
            if st.button("Confirm"):
                st.session_state.buddy.user_profile.add_unsafe_contact('family/guardians')
                st.session_state.buddy._save_profile()
                st.success("✓ Family marked as unsafe")
                st.session_state.show_profile_menu = False

        elif action == "Delete All Data":
            st.warning("⚠️ This cannot be undone!")
            if st.button("Confirm Delete"):
                st.session_state.buddy.data_store.delete_user_data(st.session_state.user_id)
                st.success("Data deleted")
                st.session_state.profile_loaded = False
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.session_state.buddy = None
                st.rerun()

        if action == "Cancel" or st.button("Close"):
            st.session_state.show_profile_menu = False
            st.rerun()


# -----------------------------------------------------------------------
# Main chat interface with tabs
# -----------------------------------------------------------------------

def show_chat_interface():
    """Show main multi-tab chat interface"""
    # Sidebar — premium info panel
    with st.sidebar:
        # User avatar circle + name
        user_id = st.session_state.user_id
        st.markdown(
            render_wellness_sidebar_card("Profile", render_user_avatar(user_id), icon="🧘"),
            unsafe_allow_html=True,
        )

        # Risk badge — color-coded
        summary = st.session_state.buddy.pattern_tracker.get_pattern_summary()
        risk_level = 'low'
        if summary:
            risk_level = summary.get('risk_level', 'low')
        st.markdown(
            render_wellness_sidebar_card("Daily Emotional Status", render_risk_badge(risk_level), icon="💠"),
            unsafe_allow_html=True,
        )

        # Session info + streak card
        if st.session_state.buddy.user_profile:
            sessions = st.session_state.buddy.user_profile.get_profile().get('session_count', 0)
            streak = st.session_state.buddy.user_profile.get_mood_streak()
            lang_pref = st.session_state.buddy.user_profile.get_language_preference()
            msg_count = len(st.session_state.get('chat_history', []))

            st.markdown(render_session_info_card(sessions + 1, lang_pref, msg_count), unsafe_allow_html=True)
            st.markdown(render_streak_card(streak), unsafe_allow_html=True)

        # Mini sentiment sparkline in sidebar
        sentiments = list(st.session_state.buddy.pattern_tracker.sentiment_history)
        if len(sentiments) >= 2:
            st.plotly_chart(create_sparkline(sentiments), width="stretch")
            st.caption("Session sentiment")

        st.markdown("---")

        # TTS toggle
        vh: VoiceHandler = st.session_state.voice_handler
        if vh and vh.tts_available:
            st.session_state.tts_enabled = st.toggle(
                "🔊 Voice Responses (TTS)",
                value=st.session_state.get('tts_enabled', False),
                help="Auto-play AI responses as audio using Google TTS (requires internet).",
            )
        else:
            st.caption("🔇 TTS unavailable (install gTTS)")

        # ---- Theme & Display ----
        st.markdown(
            '<p style="font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:0.25rem;">'
            '🎨 UI Customization</p>',
            unsafe_allow_html=True,
        )
        current_bg = st.session_state.get('background_theme', 'calm_gradient')
        current_theme = st.session_state.get('ui_theme', 'calm')
        selected_bg = st.selectbox(
            "Background Scene",
            _BACKGROUND_SCENES,
            index=_BACKGROUND_SCENES.index(
                current_bg
                if current_bg in _BACKGROUND_SCENES
                else "calm_gradient"
            ),
            help="Choose a dynamic background scene.",
        )
        selected_theme = st.selectbox(
            "UI Style",
            _UI_THEMES,
            index=_UI_THEMES.index(
                current_theme
                if current_theme in _UI_THEMES
                else "calm"
            ),
            help="Choose the global UI style tone.",
        )
        selected_dark = st.toggle(
            "Dark Mode",
            value=st.session_state.get('dark_mode', False),
            help="Switch to a calm dark theme.",
        )
        selected_calm = st.toggle(
            "Calm Mode",
            value=st.session_state.get('calm_music_enabled', False),
            help="Enable calm mode atmosphere and breathing visuals.",
        )
        theme_changed = (
            selected_bg != st.session_state.get('background_theme')
            or selected_theme != st.session_state.get('ui_theme')
            or selected_dark != st.session_state.get('dark_mode')
            or selected_calm != st.session_state.get('calm_music_enabled')
        )
        st.session_state.background_theme = selected_bg
        st.session_state.ui_theme = selected_theme
        st.session_state.dark_mode = selected_dark
        st.session_state.calm_music_enabled = selected_calm
        if theme_changed:
            st.rerun()

        # ---- Ambient Sound ----
        st.markdown(
            '<p style="font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:0.25rem;">'
            '🎵 Ambient Sound</p>',
            unsafe_allow_html=True,
        )
        if st.session_state.calm_music_enabled:
            _SOUND_OPTIONS = ["Deep Focus", "Calm Waves", "Soft Rain", "White Noise"]
            _SOUND_KEYS = ["deep_focus", "calm_waves", "soft_rain", "white_noise"]
            _cur_key = st.session_state.get('ambient_sound', 'deep_focus')
            _cur_idx = _SOUND_KEYS.index(_cur_key) if _cur_key in _SOUND_KEYS else 0
            sound_choice = st.selectbox(
                "Soundscape",
                _SOUND_OPTIONS,
                index=_cur_idx,
                key="ambient_selector",
            )
            _SOUND_MAP = dict(zip(_SOUND_OPTIONS, _SOUND_KEYS))
            st.session_state.ambient_sound = _SOUND_MAP.get(sound_choice, 'deep_focus')
            vol = st.slider(
                "🔈 Volume",
                min_value=0, max_value=100, value=30,
                key="calm_volume",
                help="Adjust ambient volume (0 = mute).",
            )
            st.session_state['_calm_volume'] = vol / 1000.0  # 0.0 – 0.1 range

        st.session_state.research_logging_enabled = st.toggle(
            "🧪 Research Logging",
            value=st.session_state.get('research_logging_enabled', False),
            help="When enabled, structured emotion/topic/trend metadata is logged for export.",
        )

        st.markdown("---")
        st.markdown(
            '<p style="font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:0.5rem;">'
            '⚡ Quick Actions</p>',
            unsafe_allow_html=True,
        )

        if st.button("📞 Help & Resources", width="stretch"):
            response = st.session_state.buddy._show_resources()
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.button("📊 Emotional Status", width="stretch"):
            response = st.session_state.buddy._show_emotional_status()
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.button("⚙️ Manage Profile", width="stretch"):
            st.session_state.show_profile_menu = True

        st.markdown("---")

        if st.button("🚪 End Session", width="stretch"):
            # Gather session stats for summary card
            buddy = st.session_state.buddy
            _sum = buddy.pattern_tracker.get_pattern_summary()
            _dom_emo = 'neutral'
            _rl = 'low'
            if _sum:
                _dist = _sum.get('emotion_distribution', {})
                if _dist:
                    _dom_emo = max(_dist, key=_dist.get)
                _rl = _sum.get('risk_level', 'low')
            _streak = buddy.user_profile.get_mood_streak()
            _msg_count = len(st.session_state.get('chat_history', []))
            st.session_state['_session_summary_html'] = render_session_summary_card(
                dominant_emotion=_dom_emo,
                message_count=_msg_count,
                risk_level=_rl,
                streak=_streak,
            )
            response = buddy._end_session()
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.profile_loaded = False
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.buddy = None
            st.rerun()

    # Profile menu overlay
    if st.session_state.get('show_profile_menu', False):
        show_profile_menu()

    # ---- Animated header bar with risk accent + emotional state ----
    summary = st.session_state.buddy.pattern_tracker.get_pattern_summary()
    _risk_level_hdr = summary.get('risk_level', 'low') if summary else 'low'
    # Determine dominant emotion for header and avatar
    _dom_emo_str = 'neutral'
    _emo_icon = '😊'
    _avatar_state = None
    _trend = None
    if summary:
        dist = summary.get('emotion_distribution', {})
        if dist:
            _dom_emo_str = max(dist, key=dist.get)
            _emo_icon = EMO_ICONS.get(_dom_emo_str, '😊')
    _meta = st.session_state.get('last_response_meta') or {}
    _last_chat = st.session_state.get('chat_history', [])
    _last_chat_entry = _last_chat[-1] if _last_chat else {}
    _meta_ts = _meta.get('timestamp')
    _is_recent_meta = False
    if _meta_ts:
        try:
            _meta_age = (datetime.now() - datetime.fromisoformat(_meta_ts)).total_seconds()
            _is_recent_meta = 0 <= _meta_age <= 900
        except ValueError:
            _is_recent_meta = False
    meta_is_fresh = (
        _last_chat
        and _last_chat_entry.get('role') == 'assistant'
        and _is_recent_meta
    )
    if _meta.get('emotion') and meta_is_fresh:
        _dom_emo_str = _meta.get('emotion', _dom_emo_str)
    _avatar_state = _meta.get('avatar_state')
    _trend = _meta.get('trend')
    streak = st.session_state.buddy.user_profile.get_mood_streak()

    # Header + dynamic emotional avatar side-by-side
    hdr_col, avatar_col = st.columns([5, 1])
    with hdr_col:
        st.markdown(
            render_chat_header(
                accent_color=_risk_level_hdr,
                emo_icon=_emo_icon,
                streak=streak,
            ),
            unsafe_allow_html=True,
        )
    with avatar_col:
        st.markdown(
            render_emotional_avatar(_dom_emo_str, avatar_state=_avatar_state, trend=_trend),
            unsafe_allow_html=True,
        )

    # Main content — tabs
    tab_chat, tab_trends, tab_journey, tab_risk, tab_report = st.tabs([
        "💬 Chat",
        "📈 Emotional Trends",
        "🌊 Emotional Journey",
        "⚠️ Risk Dashboard",
        "📋 Weekly Report",
    ])

    with tab_chat:
        render_chat_tab()

    with tab_trends:
        render_trends_tab()

    with tab_journey:
        render_emotional_journey_tab()

    with tab_risk:
        render_risk_tab()

    with tab_report:
        render_weekly_report_tab()


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    """Main application"""
    # ---- Determine risk-level accent colour for atmosphere ----
    _risk_level = 'low'
    if st.session_state.get('buddy') and st.session_state.get('profile_loaded'):
        _sum = st.session_state.buddy.pattern_tracker.get_pattern_summary()
        if _sum:
            _risk_level = _sum.get('risk_level', 'low')

    # ---- Inject theme CSS from modular theme engine ----
    st.markdown(
        get_theme_css(
            dark_mode=st.session_state.dark_mode,
            ui_theme=st.session_state.ui_theme,
            risk_level=_risk_level,
            background_theme=st.session_state.background_theme,
            calm_mode=st.session_state.calm_music_enabled,
        ),
        unsafe_allow_html=True,
    )

    # ---- Floating canvas particles ----
    st.markdown(
        canvas_particles_html(
            theme=st.session_state.background_theme,
            calm_mode=st.session_state.calm_music_enabled,
        ),
        unsafe_allow_html=True,
    )

    # ---- Background ambient sound with 4 soundscapes ----
    if st.session_state.calm_music_enabled:
        _vol = st.session_state.get('_calm_volume', 0.03)
        _sound = st.session_state.get('ambient_sound', 'deep_focus')

        # Calm mode pulsing background + waveform visualization
        st.markdown('<div class="calm-mode-overlay"></div>', unsafe_allow_html=True)
        st.markdown(render_waveform_section(_sound), unsafe_allow_html=True)
        st.markdown(ambient_sound_html(_sound, _vol), unsafe_allow_html=True)

        # Breathing circle only shown via CSS (calm mode sidebar toggle)
        st.markdown(breathing_circle_html(), unsafe_allow_html=True)
        st.markdown(guided_breathing_message_html(), unsafe_allow_html=True)
    else:
        # Stop ambient if it was playing (only when breathing exercise is also off)
        if not st.session_state.get('breathing_active', False):
            st.markdown(ambient_stop_html(), unsafe_allow_html=True)

    if not st.session_state.profile_loaded or not st.session_state.authenticated:
        show_profile_setup()
    else:
        show_chat_interface()


if __name__ == "__main__":
    main()
