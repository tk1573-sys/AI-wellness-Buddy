"""
Web UI for AI Wellness Buddy using Streamlit.
Multi-tab layout: Chat | Emotional Trends | Risk Dashboard | Weekly Report
Supports bilingual Tamil & English with Tanglish and voice input/output.
Premium glassmorphism theme with Plotly visualizations.
Run with: streamlit run ui_app.py
"""

import streamlit as st
from wellness_buddy import WellnessBuddy
from user_profile import UserProfile
from data_store import DataStore
from prediction_agent import PredictionAgent
from voice_handler import VoiceHandler
from auth_manager import AuthManager
import plotly.graph_objects as go
import config
import os

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
    ('messages', []),
    ('user_id', None),
    ('profile_loaded', False),
    ('show_load', False),
    ('show_create', False),
    ('show_profile_menu', False),
    ('tts_enabled', True),
    ('voice_handler', None),
    ('last_voice_bytes', None),
    ('calm_music_enabled', False),
    ('authenticated', False),
    ('current_user', None),
    ('failed_attempts', 0),
    ('ui_theme', 'calm'),          # calm | clinical | modern
    ('dark_mode', False),
    ('ambient_sound', 'deep_focus'),  # deep_focus | calm_waves | soft_rain
]:
    if key not in st.session_state:
        st.session_state[key] = default


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def init_buddy():
    """Initialize wellness buddy instance"""
    if st.session_state.buddy is None:
        st.session_state.buddy = WellnessBuddy()
        st.session_state.buddy.data_store = DataStore()
    if st.session_state.voice_handler is None:
        st.session_state.voice_handler = VoiceHandler()


def load_profile(username):
    """Load existing profile after successful authentication."""
    init_buddy()
    st.session_state.user_id = username
    st.session_state.current_user = username
    st.session_state.buddy._load_existing_profile(username)
    st.session_state.profile_loaded = True
    st.session_state.authenticated = True
    st.rerun()


# -----------------------------------------------------------------------
# Profile setup screens — secure login / registration
# -----------------------------------------------------------------------

def show_profile_setup():
    """Show secure login / registration interface (no public user list)."""
    st.markdown(
        '<div class="main-header"><h1>🌟 AI Wellness Buddy</h1>'
        '<p>A safe, confidential space for emotional support</p></div>',
        unsafe_allow_html=True
    )

    # Check brute-force lockout
    if AuthManager.is_locked_out(st.session_state.failed_attempts):
        st.error(
            "🔒 Too many failed login attempts. Please restart the application to try again."
        )
        return

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True):
            st.session_state.show_load = True
            st.session_state.show_create = False
    with col2:
        if st.button("Create Account", use_container_width=True):
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

    # Add a welcome message when there's no chat history yet
    if not st.session_state.messages:
        user_name = st.session_state.user_id or "friend"
        greeting = (
            f"Hello **{user_name}** 👋  \n"
            "I'm your Wellness Buddy — a safe, confidential space for emotional support.  \n"
            "Share how you're feeling, and I'll do my best to listen and help."
        )
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Display chat history with fade-in animation
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Replay TTS button for assistant messages
            if message["role"] == "assistant" and st.session_state.get('tts_enabled', False):
                vh: VoiceHandler = st.session_state.voice_handler
                if vh and vh.tts_available:
                    if st.button("🔊", key=f"tts_{idx}",
                                 help="Listen to this response"):
                        _play_tts(message["content"])

    # Inline voice mic near chat input
    feedback_col, mic_col = st.columns([11, 1])
    with mic_col:
        voice_transcript = _handle_voice_input()
    if voice_transcript:
        with feedback_col:
            st.caption(f"🎤 *{voice_transcript}*")
        st.session_state.messages.append({"role": "user", "content": voice_transcript})
        # Typing indicator (cleared after response)
        typing_placeholder = st.empty()
        with typing_placeholder.chat_message("assistant"):
            st.markdown(
                '<div class="typing-indicator">'
                '<span></span><span></span><span></span>'
                '</div>',
                unsafe_allow_html=True,
            )
        response = st.session_state.buddy.process_message(voice_transcript)
        typing_placeholder.empty()
        st.session_state.messages.append({"role": "assistant", "content": response})
        _play_tts(response)
        st.rerun()

    # Text chat input
    placeholder = {
        'tamil':     'உங்கள் உணர்வுகளை பகிர்ந்துகொள்ளுங்கள்…',
        'bilingual': 'Share / சொல்லுங்க…',
    }.get(lang_pref, 'Share how you\'re feeling…')

    if prompt := st.chat_input(placeholder):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = st.session_state.buddy.process_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        if st.session_state.get('tts_enabled', False):
            _play_tts(response)
        st.rerun()


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
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=sentiments,
                mode='lines+markers',
                name='Sentiment',
                line=dict(color='#5B8CFF', width=3, shape='spline'),
                marker=dict(size=7, color='#9B8CFF', line=dict(color='#fff', width=1)),
                fill='tozeroy',
                fillcolor='rgba(91,140,255,0.12)',
                hovertemplate='Message %{x}<br>Sentiment: %{y:.2f}<extra></extra>',
            ))
            fig.update_layout(
                template='plotly_white',
                xaxis_title='Message #',
                yaxis_title='Sentiment',
                height=320,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
                hoverlabel=dict(bgcolor='#fff', font_size=12, font_family='Inter'),
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if summary:
                ma = summary.get('moving_average', [])
                if len(ma) >= 2:
                    fig_ma = go.Figure()
                    fig_ma.add_trace(go.Scatter(
                        y=ma,
                        mode='lines',
                        name='3-msg MA',
                        line=dict(color='#FF8A65', width=2, dash='dot'),
                    ))
                    fig_ma.update_layout(
                        template='plotly_white',
                        height=220,
                        margin=dict(l=30, r=10, t=10, b=30),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig_ma, use_container_width=True)
                    st.caption("3-message moving average of sentiment")
    else:
        st.info("Start chatting to see your sentiment trend.")

    # ---- Emotion distribution (Plotly donut chart) ----
    if summary:
        dist = summary.get('emotion_distribution', {})
        if dist:
            st.markdown("#### Current Session — Emotion Distribution")
            _EMO_COLORS = {
                'joy': '#4DD0E1', 'positive': '#4DD0E1',
                'neutral': '#9B8CFF',
                'sadness': '#5B8CFF', 'negative': '#5B8CFF',
                'anger': '#FF8A65',
                'fear': '#FFB74D', 'anxiety': '#FFB74D',
                'crisis': '#EF5350', 'distress': '#EF5350',
            }
            emotions = sorted(dist.keys(), key=lambda e: -dist[e])
            counts = [dist[e] for e in emotions]
            colors = [_EMO_COLORS.get(e, '#9B8CFF') for e in emotions]

            col_a, col_b = st.columns([1, 2])
            with col_a:
                for emo, cnt in zip(emotions, counts):
                    st.metric(label=emo.capitalize(), value=cnt)
            with col_b:
                fig_donut = go.Figure(go.Pie(
                    labels=[e.capitalize() for e in emotions],
                    values=counts,
                    hole=0.55,
                    marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
                    textinfo='label+percent',
                    textposition='outside',
                    textfont=dict(size=12),
                    hoverinfo='label+value+percent',
                    pull=[0.03] * len(emotions),
                ))
                fig_donut.update_layout(
                    template='plotly_white',
                    height=320,
                    margin=dict(l=20, r=20, t=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    annotations=[dict(
                        text='Emotions',
                        x=0.5, y=0.5,
                        font=dict(size=14, color='#64748B'),
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig_donut, use_container_width=True)

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
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(
                y=hist_data,
                mode='lines+markers',
                name='Mood',
                line=dict(color='#9B8CFF', width=3, shape='spline'),
                marker=dict(size=6, color='#5B8CFF', line=dict(color='#fff', width=1)),
                fill='tozeroy',
                fillcolor='rgba(155,140,255,0.10)',
                hovertemplate='Session %{x}<br>Avg Mood: %{y:.2f}<extra></extra>',
            ))

            # Prediction & forecast overlay
            predictor = PredictionAgent()
            forecast = predictor.predict_next_sentiment(hist_data)
            if forecast:
                # Add forecast point as dashed extension
                pred_val = forecast['predicted_value']
                fig_hist.add_trace(go.Scatter(
                    x=[len(hist_data) - 1, len(hist_data)],
                    y=[hist_data[-1], pred_val],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#FF8A65', width=2, dash='dash'),
                    marker=dict(size=8, color='#FF8A65', symbol='diamond',
                                line=dict(color='#fff', width=1)),
                    hovertemplate='Forecast<br>Predicted: %{y:.2f}<extra></extra>',
                ))

            fig_hist.update_layout(
                template='plotly_white',
                xaxis_title='Session',
                yaxis_title='Avg Mood',
                height=320,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
                hoverlabel=dict(bgcolor='#fff', font_size=12, font_family='Inter'),
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

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


# -----------------------------------------------------------------------
# Risk Dashboard tab (tab 3)
# -----------------------------------------------------------------------

_RISK_COLOUR = {
    'low':      '🟢',
    'medium':   '🟡',
    'high':     '🔴',
    'critical': '🚨',
}

# Numeric representation of risk levels for charting
_RISK_LEVEL_VALUES = {'low': 0.10, 'medium': 0.35, 'high': 0.65, 'critical': 0.90}


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
    icon = _RISK_COLOUR.get(risk_level, '⬜')

    st.markdown(f"### Current Risk Level: {icon} {risk_level.upper()}")

    # Plotly semi-circular animated risk dial
    _GAUGE_COLORS = {
        'low': '#5B8CFF',
        'medium': '#FFB74D',
        'high': '#EF5350',
        'critical': '#D32F2F',
    }
    bar_color = _GAUGE_COLORS.get(risk_level, '#5B8CFF')
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        title={'text': '<b>Risk Score</b>', 'font': {'size': 18, 'color': '#64748B', 'family': 'Inter'}},
        number={'suffix': ' / 1.00', 'font': {'size': 32, 'color': '#334155', 'family': 'Inter'}},
        delta={'reference': 0.25, 'increasing': {'color': '#EF5350'}, 'decreasing': {'color': '#5B8CFF'}},
        gauge={
            'axis': {
                'range': [0, 1],
                'tickwidth': 1,
                'tickcolor': '#94a3b8',
                'tickvals': [0, 0.25, 0.5, 0.75, 1.0],
                'ticktext': ['Safe', 'Low', 'Med', 'High', 'Crit'],
                'tickfont': {'size': 10, 'color': '#94a3b8'},
            },
            'bar': {'color': bar_color, 'thickness': 0.82},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 0.25], 'color': 'rgba(91,140,255,0.10)'},
                {'range': [0.25, 0.50], 'color': 'rgba(255,183,77,0.10)'},
                {'range': [0.50, 0.75], 'color': 'rgba(239,83,80,0.10)'},
                {'range': [0.75, 1.0], 'color': 'rgba(211,47,47,0.12)'},
            ],
            'threshold': {
                'line': {'color': '#D32F2F', 'width': 3},
                'thickness': 0.85,
                'value': risk_score,
            },
        },
    ))
    fig_gauge.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'},
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

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

    # Risk history (last 30 days) — Plotly
    history = buddy.user_profile.get_emotional_history(days=30)
    risk_hist = []
    for snap in history:
        ed = snap.get('emotion_data', {}) or {}
        rl = ed.get('risk_level', None)
        if rl:
            risk_hist.append(_RISK_LEVEL_VALUES.get(rl, 0.10))

    if risk_hist:
        st.markdown("#### 30-Day Risk Level History")
        fig_rh = go.Figure()
        fig_rh.add_trace(go.Scatter(
            y=risk_hist,
            mode='lines+markers',
            name='Risk',
            line=dict(color='#EF5350', width=2, shape='spline'),
            marker=dict(size=6, color='#FF8A65', line=dict(color='#fff', width=1)),
            fill='tozeroy',
            fillcolor='rgba(239,83,80,0.10)',
            hovertemplate='Session %{x}<br>Risk: %{y:.2f}<extra></extra>',
        ))
        fig_rh.update_layout(
            template='plotly_white',
            xaxis_title='Session',
            yaxis_title='Risk (0=low, 1=critical)',
            yaxis=dict(range=[0, 1]),
            height=300,
            margin=dict(l=40, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter'),
            hoverlabel=dict(bgcolor='#fff', font_size=12, font_family='Inter'),
        )
        st.plotly_chart(fig_rh, use_container_width=True)

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
            fig_wk = go.Figure()
            fig_wk.add_trace(go.Scatter(
                y=sentiments,
                mode='lines+markers',
                name='Daily Mood',
                line=dict(color='#4DD0E1', width=3, shape='spline'),
                marker=dict(size=7, color='#5B8CFF', line=dict(color='#fff', width=1)),
                fill='tozeroy',
                fillcolor='rgba(77,208,225,0.12)',
                hovertemplate='Day %{x}<br>Mood: %{y:.2f}<extra></extra>',
            ))
            fig_wk.update_layout(
                template='plotly_white',
                xaxis_title='Day',
                yaxis_title='Avg Mood',
                height=300,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
                hoverlabel=dict(bgcolor='#fff', font_size=12, font_family='Inter'),
            )
            st.plotly_chart(fig_wk, use_container_width=True)

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
        initials = (user_id[0].upper() if user_id else "?")
        st.markdown(
            f'<div style="text-align:center;margin-bottom:0.75rem;">'
            f'<div style="width:72px;height:72px;border-radius:50%;'
            f'background:linear-gradient(135deg,#5B8CFF,#9B8CFF);'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:1.8rem;color:#fff;font-weight:700;letter-spacing:0.5px;'
            f'box-shadow:0 6px 20px rgba(91,140,255,0.35);'
            f'border:3px solid rgba(255,255,255,0.6);">{initials}</div>'
            f'<p style="margin:0.5rem 0 0;font-weight:600;font-size:1.1rem;'
            f'color:#334155;">{user_id}</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Risk badge — color-coded
        summary = st.session_state.buddy.pattern_tracker.get_pattern_summary()
        risk_level = 'low'
        if summary:
            risk_level = summary.get('risk_level', 'low')
        _BADGE_STYLE = {
            'low':      ('🟢', '#5B8CFF', 'rgba(91,140,255,0.10)', 'rgba(91,140,255,0.25)'),
            'medium':   ('🟡', '#FFB74D', 'rgba(255,183,77,0.10)', 'rgba(255,183,77,0.25)'),
            'high':     ('🔴', '#EF5350', 'rgba(239,83,80,0.10)', 'rgba(239,83,80,0.25)'),
            'critical': ('🚨', '#D32F2F', 'rgba(211,47,47,0.12)', 'rgba(211,47,47,0.30)'),
        }
        r_icon, r_color, r_bg, r_shadow = _BADGE_STYLE.get(risk_level, _BADGE_STYLE['low'])
        st.markdown(
            f'<div style="text-align:center;padding:0.6rem 0.75rem;border-radius:0.75rem;'
            f'background:{r_bg};border:1px solid {r_color};margin-bottom:0.75rem;'
            f'box-shadow:0 2px 12px {r_shadow};backdrop-filter:blur(6px);'
            f'transition:all 0.3s ease;">'
            f'<span style="font-size:1.15rem;font-weight:600;">{r_icon} Risk: '
            f'<strong style="color:{r_color};">{risk_level.upper()}</strong></span></div>',
            unsafe_allow_html=True,
        )

        # Session info + streak card
        if st.session_state.buddy.user_profile:
            sessions = st.session_state.buddy.user_profile.get_profile().get('session_count', 0)
            streak = st.session_state.buddy.user_profile.get_mood_streak()
            lang_pref = st.session_state.buddy.user_profile.get_language_preference()
            _LANG_ICONS = {'english': '🇬🇧', 'tamil': '🇮🇳', 'bilingual': '🇮🇳🇬🇧'}

            # Session & language info in compact card
            st.markdown(
                f'<div style="padding:0.5rem 0.75rem;border-radius:0.6rem;'
                f'background:rgba(255,255,255,0.55);backdrop-filter:blur(8px);'
                f'border:1px solid rgba(255,255,255,0.3);margin-bottom:0.5rem;'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.03);">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<span style="font-size:0.88rem;color:#475569;">📅 Session #{sessions + 1}</span>'
                f'<span style="font-size:0.88rem;color:#475569;">'
                f'{_LANG_ICONS.get(lang_pref, "🌐")} {lang_pref.capitalize()}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            # Streak card
            streak_emoji = "🔥" if streak >= 3 else "⭐" if streak >= 1 else "💤"
            streak_label = "on fire!" if streak >= 7 else "growing!" if streak >= 3 else "building" if streak >= 1 else "start today"
            st.markdown(
                f'<div style="text-align:center;padding:0.65rem 0.75rem;border-radius:0.75rem;'
                f'background:linear-gradient(135deg,rgba(77,208,225,0.10),rgba(155,140,255,0.10));'
                f'border:1px solid rgba(155,140,255,0.15);'
                f'box-shadow:0 2px 10px rgba(77,208,225,0.08);margin:0.5rem 0 0.75rem;">'
                f'<span style="font-size:1.6rem;">{streak_emoji}</span><br>'
                f'<strong style="font-size:1.2rem;color:#334155;">{streak}</strong>'
                f'<span style="font-size:0.85rem;color:#64748B;margin-left:0.25rem;">'
                f'positive streak</span><br>'
                f'<span style="font-size:0.75rem;color:#9B8CFF;font-style:italic;">'
                f'{streak_label}</span></div>',
                unsafe_allow_html=True,
            )

        # Mini sentiment sparkline in sidebar
        sentiments = list(st.session_state.buddy.pattern_tracker.sentiment_history)
        if len(sentiments) >= 2:
            fig_spark = go.Figure(go.Scatter(
                y=sentiments, mode='lines',
                line=dict(color='#5B8CFF', width=2),
                fill='tozeroy',
                fillcolor='rgba(91,140,255,0.10)',
            ))
            fig_spark.update_layout(
                height=80, margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                showlegend=False,
            )
            st.plotly_chart(fig_spark, use_container_width=True)
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
            '🎨 Theme & Display</p>',
            unsafe_allow_html=True,
        )
        st.session_state.dark_mode = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state.get('dark_mode', False),
            help="Switch to a calm dark theme.",
        )
        theme_choice = st.selectbox(
            "Wellness Theme",
            ["Calm Therapy", "Clinical", "Modern Startup"],
            index=["Calm Therapy", "Clinical", "Modern Startup"].index(
                {"calm": "Calm Therapy", "clinical": "Clinical", "modern": "Modern Startup"}.get(
                    st.session_state.get('ui_theme', 'calm'), "Calm Therapy"
                )
            ),
            key="theme_selector",
            help="Visual theme: Calm (soft gradients), Clinical (professional), Modern (vibrant).",
        )
        _THEME_MAP = {"Calm Therapy": "calm", "Clinical": "clinical", "Modern Startup": "modern"}
        st.session_state.ui_theme = _THEME_MAP.get(theme_choice, 'calm')

        # ---- Ambient Sound ----
        st.markdown(
            '<p style="font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:0.25rem;">'
            '🎵 Ambient Sound</p>',
            unsafe_allow_html=True,
        )
        st.session_state.calm_music_enabled = st.toggle(
            "Enable Ambient",
            value=st.session_state.get('calm_music_enabled', False),
            help="Play calming ambient background. Starts after interaction (browser safe).",
        )
        if st.session_state.calm_music_enabled:
            sound_choice = st.selectbox(
                "Soundscape",
                ["Deep Focus", "Calm Waves", "Soft Rain"],
                index=["deep_focus", "calm_waves", "soft_rain"].index(
                    st.session_state.get('ambient_sound', 'deep_focus')
                ),
                key="ambient_selector",
            )
            _SOUND_MAP = {"Deep Focus": "deep_focus", "Calm Waves": "calm_waves", "Soft Rain": "soft_rain"}
            st.session_state.ambient_sound = _SOUND_MAP.get(sound_choice, 'deep_focus')
            vol = st.slider(
                "🔈 Volume",
                min_value=0, max_value=100, value=30,
                key="calm_volume",
                help="Adjust ambient volume (0 = mute).",
            )
            st.session_state['_calm_volume'] = vol / 1000.0  # 0.0 – 0.1 range

        st.markdown("---")
        st.markdown(
            '<p style="font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:0.5rem;">'
            '⚡ Quick Actions</p>',
            unsafe_allow_html=True,
        )

        if st.button("📞 Help & Resources", use_container_width=True):
            response = st.session_state.buddy._show_resources()
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.button("📊 Emotional Status", use_container_width=True):
            response = st.session_state.buddy._show_emotional_status()
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.button("⚙️ Manage Profile", use_container_width=True):
            st.session_state.show_profile_menu = True

        st.markdown("---")

        if st.button("🚪 End Session", use_container_width=True):
            response = st.session_state.buddy._end_session()
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.profile_loaded = False
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.buddy = None
            st.rerun()

    # Profile menu overlay
    if st.session_state.get('show_profile_menu', False):
        show_profile_menu()

    # Main content — tabs
    tab_chat, tab_trends, tab_risk, tab_report = st.tabs([
        "💬 Chat",
        "📈 Emotional Trends",
        "⚠️ Risk Dashboard",
        "📋 Weekly Report",
    ])

    with tab_chat:
        render_chat_tab()

    with tab_trends:
        render_trends_tab()

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

    _RISK_GLOW = {
        'low':      'rgba(91,140,255,0.18)',
        'medium':   'rgba(255,183,77,0.22)',
        'high':     'rgba(239,83,80,0.18)',
        'critical': 'rgba(211,47,47,0.28)',
    }
    _RISK_BORDER = {
        'low':      'transparent',
        'medium':   'rgba(255,183,77,0.4)',
        'high':     'rgba(239,83,80,0.45)',
        'critical': '#D32F2F',
    }
    glow_color = _RISK_GLOW.get(_risk_level, _RISK_GLOW['low'])
    border_color = _RISK_BORDER.get(_risk_level, 'transparent')

    # Pulsing animation for critical risk
    critical_bar_css = ""
    if _risk_level == 'critical':
        critical_bar_css = """
        .main::before {
            content: '🚨 CRITICAL — Please reach out for support';
            display: block;
            text-align: center;
            padding: 0.5rem;
            background: linear-gradient(90deg, #D32F2F, #EF5350, #D32F2F);
            color: #fff;
            font-weight: 700;
            font-size: 0.9rem;
            animation: pulse-bar 1.5s ease-in-out infinite;
            border-radius: 0 0 0.5rem 0.5rem;
        }
        @keyframes pulse-bar {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        """

    # ---- Dark mode & theme variables ----
    _dark = st.session_state.get('dark_mode', False)
    _theme = st.session_state.get('ui_theme', 'calm')

    if _dark:
        bg_gradient = 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 25%, #1a1a2e 50%, #0f172a 75%, #1e1b4b 100%)'
        card_bg = 'rgba(30,27,75,0.60)'
        card_border = 'rgba(91,140,255,0.15)'
        text_primary = '#e2e8f0'
        text_secondary = '#94a3b8'
        text_heading = '#f1f5f9'
        sidebar_bg = 'linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(30,27,75,0.95) 100%)'
        form_bg = 'rgba(30,27,75,0.65)'
        input_bg = 'rgba(30,27,75,0.80)'
        particle_color = 'rgba(91,140,255,0.06)'
    else:
        # Light mode theme variants
        _THEME_BG = {
            'calm':     'linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 25%, #fff5f0 50%, #f0fffe 75%, #f0f4ff 100%)',
            'clinical': 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #f8fafc 100%)',
            'modern':   'linear-gradient(135deg, #ede9fe 0%, #e0f2fe 25%, #fce7f3 50%, #e0f2fe 75%, #ede9fe 100%)',
        }
        bg_gradient = _THEME_BG.get(_theme, _THEME_BG['calm'])
        card_bg = 'rgba(255,255,255,0.65)'
        card_border = 'rgba(255,255,255,0.35)'
        text_primary = '#475569'
        text_secondary = '#64748B'
        text_heading = '#1e293b'
        sidebar_bg = 'linear-gradient(180deg, rgba(91,140,255,0.05) 0%, rgba(155,140,255,0.05) 50%, rgba(77,208,225,0.03) 100%)'
        form_bg = 'rgba(255,255,255,0.60)'
        input_bg = 'rgba(255,255,255,0.75)'
        particle_color = 'rgba(91,140,255,0.04)'

    st.markdown(f"""
    <style>
    /* ---- Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ---- Animated gradient background ---- */
    @keyframes gradientBG {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .stApp {{
        background: {bg_gradient};
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    /* ---- Floating particles (pure CSS) ---- */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: 0;
        background-image:
            radial-gradient(2px 2px at 20% 30%, {particle_color}, transparent),
            radial-gradient(2px 2px at 40% 70%, {particle_color}, transparent),
            radial-gradient(2px 2px at 60% 40%, {particle_color}, transparent),
            radial-gradient(2px 2px at 80% 60%, {particle_color}, transparent),
            radial-gradient(3px 3px at 10% 80%, {particle_color}, transparent),
            radial-gradient(3px 3px at 70% 20%, {particle_color}, transparent),
            radial-gradient(2px 2px at 50% 50%, {particle_color}, transparent),
            radial-gradient(2px 2px at 90% 90%, {particle_color}, transparent);
        background-size: 200% 200%;
        animation: particleDrift 30s linear infinite;
    }}
    @keyframes particleDrift {{
        0%   {{ background-position: 0% 0%; }}
        50%  {{ background-position: 100% 100%; }}
        100% {{ background-position: 0% 0%; }}
    }}

    /* ---- Premium typography hierarchy ---- */
    h1, h2, h3 {{ color: {text_heading}; letter-spacing: -0.02em; font-weight: 700; }}
    h4 {{ color: {'#cbd5e1' if _dark else '#334155'}; font-weight: 600; letter-spacing: -0.01em; }}
    p, li, span {{ color: {text_primary}; }}
    .stCaption, caption {{ color: {text_secondary}; letter-spacing: 0.02em; text-transform: uppercase; font-size: 0.72rem; }}

    /* ---- Glassmorphism chat cards — depth layered ---- */
    .stChatMessage {{
        padding: 1.1rem 1.3rem;
        border-radius: 1rem;
        background: {card_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {card_border};
        box-shadow: 0 4px 24px {glow_color}, inset 0 1px 0 rgba(255,255,255,0.08);
        margin-bottom: 0.8rem;
        animation: fadeSlideIn 0.45s cubic-bezier(0.22,1,0.36,1);
        transition: box-shadow 0.3s ease, transform 0.3s ease;
        position: relative;
        z-index: 1;
    }}
    .stChatMessage:hover {{
        transform: translateY(-1px);
        box-shadow: 0 8px 32px {glow_color};
    }}
    @keyframes fadeSlideIn {{
        from {{ opacity: 0; transform: translateY(16px) scale(0.98); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}

    /* ---- User vs assistant message distinction ---- */
    .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        border-left: 3px solid #5B8CFF;
    }}
    .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        border-left: 3px solid #9B8CFF;
    }}

    /* ---- Typing indicator animation ---- */
    .typing-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 6px 0;
    }}
    .typing-indicator span {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #9B8CFF;
        animation: typingBounce 1.2s ease-in-out infinite;
        box-shadow: 0 0 6px rgba(155,140,255,0.4);
    }}
    .typing-indicator span:nth-child(2) {{ animation-delay: 0.15s; }}
    .typing-indicator span:nth-child(3) {{ animation-delay: 0.3s; }}
    @keyframes typingBounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
        30% {{ transform: translateY(-8px); opacity: 1; }}
    }}

    /* ---- AI responding glow ---- */
    @keyframes assistantGlow {{
        0%, 100% {{ box-shadow: 0 0 12px rgba(155,140,255,0.15); }}
        50% {{ box-shadow: 0 0 24px rgba(155,140,255,0.30); }}
    }}
    .typing-indicator {{
        animation: assistantGlow 2s ease-in-out infinite;
        border-radius: 1rem;
        padding: 8px 12px;
    }}

    /* ---- Premium chat input bar ---- */
    [data-testid="stChatInput"] {{
        background: {input_bg} !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 1.25rem !important;
        border: 1px solid rgba(91,140,255,0.18) !important;
        box-shadow: 0 4px 28px rgba(91,140,255,0.10);
        transition: box-shadow 0.3s ease, border-color 0.3s ease;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: #5B8CFF !important;
        box-shadow: 0 4px 32px rgba(91,140,255,0.20);
    }}
    [data-testid="stChatInput"] textarea {{
        font-size: 0.98rem;
        color: {text_primary};
    }}
    /* Send button ripple glow */
    [data-testid="stChatInput"] button {{
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-radius: 50%;
    }}
    [data-testid="stChatInput"] button:hover {{
        transform: scale(1.12);
        box-shadow: 0 0 16px rgba(91,140,255,0.4);
    }}
    [data-testid="stChatInput"] button:active {{
        transform: scale(0.95);
        box-shadow: 0 0 24px rgba(91,140,255,0.5);
    }}

    /* ---- Sidebar polish ---- */
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem;
        background: {sidebar_bg};
    }}
    section[data-testid="stSidebar"] .stMarkdown p {{
        font-size: 0.9rem;
        color: {text_primary};
    }}

    /* ---- Tab labels with slide transition ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.25rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.6rem 1rem;
        transition: color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
        letter-spacing: 0.01em;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: #5B8CFF;
        background: rgba(91,140,255,0.06);
        box-shadow: 0 -2px 10px rgba(91,140,255,0.10);
        transform: translateY(-1px);
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        box-shadow: 0 -2px 14px rgba(91,140,255,0.14);
    }}
    /* Tab content slide */
    .stTabs [data-baseweb="tab-panel"] {{
        animation: tabSlideIn 0.35s ease-out;
    }}
    @keyframes tabSlideIn {{
        from {{ opacity: 0; transform: translateX(12px); }}
        to   {{ opacity: 1; transform: translateX(0); }}
    }}

    /* ---- Metric cards — glassmorphism with hover tilt ---- */
    [data-testid="stMetric"] {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 0.75rem;
        padding: 0.8rem;
        border: 1px solid {card_border};
        box-shadow: 0 2px 16px rgba(0,0,0,0.04);
        transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s ease;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px) perspective(600px) rotateX(1deg);
        box-shadow: 0 8px 28px rgba(91,140,255,0.14);
    }}

    /* ---- Button hover glow ---- */
    .stButton > button {{
        border-radius: 0.5rem;
        transition: all 0.3s cubic-bezier(0.22,1,0.36,1);
        border: 1px solid rgba(91,140,255,0.2);
        font-weight: 500;
        letter-spacing: 0.01em;
    }}
    .stButton > button:hover {{
        box-shadow: 0 0 20px rgba(91,140,255,0.28);
        border-color: #5B8CFF;
        transform: translateY(-2px);
    }}
    .stButton > button:active {{
        transform: translateY(0);
        box-shadow: 0 0 8px rgba(91,140,255,0.15);
    }}

    /* ---- Toggle styling ---- */
    [data-testid="stToggle"] label {{
        font-weight: 500;
    }}

    /* ---- Expander styling ---- */
    .streamlit-expanderHeader {{
        font-weight: 600;
    }}

    /* ---- Header area ---- */
    .main-header {{
        text-align: center;
        padding: 2rem 0 1.25rem 0;
    }}
    .main-header h1 {{
        font-size: 2.6rem;
        margin-bottom: 0;
        background: linear-gradient(135deg, #5B8CFF, #9B8CFF, #FF8A65);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        letter-spacing: -0.03em;
    }}
    .main-header p {{
        color: {text_secondary};
        font-size: 0.95rem;
        margin-top: 0.25rem;
        letter-spacing: 0.02em;
    }}

    /* ---- Risk-level atmospheric border ---- */
    .main .block-container {{
        border-top: 3px solid {border_color};
        transition: border-color 0.5s ease;
    }}

    /* ---- Critical pulsing warning bar ---- */
    {critical_bar_css}

    /* ---- Smooth card hover elevation ---- */
    .stExpander {{
        transition: box-shadow 0.3s ease, transform 0.3s ease;
        border-radius: 0.75rem;
    }}
    .stExpander:hover {{
        box-shadow: 0 4px 20px rgba(91,140,255,0.10);
        transform: translateY(-2px);
    }}

    /* ---- Profile setup form glassmorphism ---- */
    [data-testid="stForm"] {{
        background: {form_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 1rem;
        border: 1px solid {card_border};
        padding: 1.5rem;
        box-shadow: 0 4px 28px rgba(91,140,255,0.10);
    }}

    /* ---- Slider styling ---- */
    [data-testid="stSlider"] {{
        padding-top: 0;
    }}

    /* ---- Plotly chart containers with shimmer loading ---- */
    [data-testid="stPlotlyChart"] {{
        border-radius: 0.75rem;
        overflow: hidden;
        animation: shimmerIn 0.6s ease-out;
    }}
    @keyframes shimmerIn {{
        from {{ opacity: 0.3; }}
        to   {{ opacity: 1; }}
    }}

    /* ---- Selectbox & form inputs ---- */
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {{
        font-weight: 500;
        font-size: 0.88rem;
        letter-spacing: 0.01em;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ---- Background ambient sound with 3 soundscapes ----
    if st.session_state.get('calm_music_enabled', False):
        _vol = st.session_state.get('_calm_volume', 0.03)
        _sound = st.session_state.get('ambient_sound', 'deep_focus')
        # Soundscape configs: { primary_freq, primary_type, harmonic_freq, harmonic_type, harmonic_ratio }
        _SOUNDSCAPES = {
            'deep_focus':  {'f1': 174, 't1': 'sine', 'f2': 285, 't2': 'sine', 'hr': 0.3},
            'calm_waves':  {'f1': 136, 't1': 'sine', 'f2': 204, 't2': 'triangle', 'hr': 0.25},
            'soft_rain':   {'f1': 220, 't1': 'triangle', 'f2': 330, 't2': 'sine', 'hr': 0.2},
        }
        sc = _SOUNDSCAPES.get(_sound, _SOUNDSCAPES['deep_focus'])
        st.markdown(
            f"""
            <div id="ambient-music-container" style="display:none;">
                <p style="font-size:0.75rem;color:#9B8CFF;">🎵 Ambient active</p>
            </div>
            <script>
            (function() {{
                var vol = {_vol};
                var f1 = {sc['f1']}, t1 = '{sc['t1']}';
                var f2 = {sc['f2']}, t2 = '{sc['t2']}';
                var hr = {sc['hr']};
                var soundKey = '{_sound}';

                // If same soundscape already running, just update volume
                if (window._ambientInitialized && window._ambientSoundKey === soundKey) {{
                    if (window._ambientGain) {{
                        window._ambientGain.gain.setTargetAtTime(vol, window._ambientCtx.currentTime, 0.1);
                    }}
                    if (window._ambientGain2) {{
                        window._ambientGain2.gain.setTargetAtTime(vol * hr, window._ambientCtx.currentTime, 0.1);
                    }}
                    return;
                }}

                // Stop existing if switching soundscape
                if (window._ambientOsc) {{ try {{ window._ambientOsc.stop(); }} catch(e) {{}} }}
                if (window._ambientOsc2) {{ try {{ window._ambientOsc2.stop(); }} catch(e) {{}} }}
                window._ambientInitialized = false;

                window._ambientInitialized = true;
                window._ambientSoundKey = soundKey;
                try {{
                    var ctx = window._ambientCtx || new (window.AudioContext || window.webkitAudioContext)();
                    window._ambientCtx = ctx;
                    var osc1 = ctx.createOscillator();
                    osc1.type = t1;
                    osc1.frequency.value = f1;
                    var osc2 = ctx.createOscillator();
                    osc2.type = t2;
                    osc2.frequency.value = f2;
                    var gain1 = ctx.createGain();
                    var gain2 = ctx.createGain();
                    gain1.gain.value = vol;
                    gain2.gain.value = vol * hr;
                    osc1.connect(gain1);
                    osc2.connect(gain2);
                    gain1.connect(ctx.destination);
                    gain2.connect(ctx.destination);
                    osc1.start();
                    osc2.start();
                    window._ambientOsc = osc1;
                    window._ambientOsc2 = osc2;
                    window._ambientGain = gain1;
                    window._ambientGain2 = gain2;
                }} catch(e) {{}}
            }})();
            </script>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Stop ambient if it was playing
        st.markdown(
            """
            <script>
            (function() {
                if (window._ambientOsc) {
                    try { window._ambientOsc.stop(); } catch(e) {}
                    window._ambientOsc = null;
                }
                if (window._ambientOsc2) {
                    try { window._ambientOsc2.stop(); } catch(e) {}
                    window._ambientOsc2 = null;
                }
                window._ambientInitialized = false;
                window._ambientSoundKey = null;
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

    if not st.session_state.profile_loaded or not st.session_state.authenticated:
        show_profile_setup()
    else:
        show_chat_interface()


if __name__ == "__main__":
    main()
