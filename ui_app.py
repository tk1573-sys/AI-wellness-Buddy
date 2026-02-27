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
    """Load existing profile"""
    init_buddy()
    st.session_state.user_id = username
    st.session_state.buddy._load_existing_profile(username)
    st.session_state.profile_loaded = True
    st.success(f"✓ Profile loaded: {username}")
    st.rerun()


# -----------------------------------------------------------------------
# Profile setup screens
# -----------------------------------------------------------------------

def show_profile_setup():
    """Show profile setup interface"""
    st.markdown(
        '<div class="main-header"><h1>🌟 AI Wellness Buddy</h1>'
        '<p>A safe, confidential space for emotional support</p></div>',
        unsafe_allow_html=True
    )
    st.markdown("### Welcome! Let's set up your profile")

    data_store = DataStore()
    existing_users = data_store.list_users()

    if existing_users:
        st.info(f"Found {len(existing_users)} existing profile(s)")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Existing Profile", use_container_width=True):
                st.session_state.show_load = True
                st.session_state.show_create = False
        with col2:
            if st.button("Create New Profile", use_container_width=True):
                st.session_state.show_create = True
                st.session_state.show_load = False

        if st.session_state.get('show_load', False):
            username = st.selectbox("Select your username:", existing_users)
            if st.button("Load Profile"):
                load_profile(username)

        if st.session_state.get('show_create', False):
            create_new_profile()
    else:
        st.info("No existing profiles found. Let's create one!")
        create_new_profile()


def create_new_profile():
    """Create new profile interface"""
    with st.form("new_profile"):
        username = st.text_input("Choose a username (private):", key="new_username")
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
            init_buddy()
            st.session_state.user_id = username
            st.session_state.buddy.user_id = username
            st.session_state.buddy.user_profile = UserProfile(username)

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
        response = st.session_state.buddy.process_message(voice_transcript)
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
    st.caption("Real-time sentiment tracking and historical mood analysis")

    buddy = st.session_state.buddy
    summary = buddy.pattern_tracker.get_pattern_summary()
    history = buddy.user_profile.get_emotional_history(days=30)

    # ---- Current session sentiment line (Plotly gradient) ----
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
                marker=dict(size=7, color='#9B8CFF'),
                fill='tozeroy',
                fillcolor='rgba(91,140,255,0.12)',
            ))
            fig.update_layout(
                template='plotly_white',
                xaxis_title='Message #',
                yaxis_title='Sentiment',
                height=320,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
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

    # ---- Emotion distribution (Plotly colored bar chart) ----
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
                fig_bar = go.Figure(go.Bar(
                    x=[e.capitalize() for e in emotions],
                    y=counts,
                    marker_color=colors,
                    marker_line=dict(width=0),
                ))
                fig_bar.update_layout(
                    template='plotly_white',
                    height=300,
                    margin=dict(l=30, r=10, t=10, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_title='Count',
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    # ---- Historical 30-day sentiment (Plotly) ----
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
                line=dict(color='#9B8CFF', width=3, shape='spline'),
                marker=dict(size=6, color='#5B8CFF'),
                fill='tozeroy',
                fillcolor='rgba(155,140,255,0.10)',
            ))
            fig_hist.update_layout(
                template='plotly_white',
                xaxis_title='Session',
                yaxis_title='Avg Mood',
                height=300,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            # Prediction
            predictor = PredictionAgent()
            forecast = predictor.predict_next_sentiment(hist_data)
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
    st.caption("Composite risk scoring, crisis detection, and escalation forecast")

    buddy = st.session_state.buddy
    summary = buddy.pattern_tracker.get_pattern_summary()

    if not summary or summary['total_messages'] == 0:
        st.info("Start a conversation to see your risk dashboard.")
        return

    risk_level = summary.get('risk_level', 'low')
    risk_score = summary.get('risk_score', 0.0)
    icon = _RISK_COLOUR.get(risk_level, '⬜')

    st.markdown(f"### Current Risk Level: {icon} {risk_level.upper()}")

    # Plotly gauge-style risk indicator
    _GAUGE_COLORS = {
        'low': '#5B8CFF',
        'medium': '#FFB74D',
        'high': '#EF5350',
        'critical': '#D32F2F',
    }
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        number={'suffix': ' / 1.00', 'font': {'size': 28}},
        gauge={
            'axis': {'range': [0, 1], 'tickwidth': 1},
            'bar': {'color': _GAUGE_COLORS.get(risk_level, '#5B8CFF')},
            'bgcolor': 'rgba(0,0,0,0)',
            'steps': [
                {'range': [0, 0.25], 'color': 'rgba(91,140,255,0.15)'},
                {'range': [0.25, 0.50], 'color': 'rgba(255,183,77,0.15)'},
                {'range': [0.50, 0.75], 'color': 'rgba(239,83,80,0.15)'},
                {'range': [0.75, 1.0], 'color': 'rgba(211,47,47,0.20)'},
            ],
            'threshold': {
                'line': {'color': '#D32F2F', 'width': 3},
                'thickness': 0.8,
                'value': risk_score,
            },
        },
    ))
    fig_gauge.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
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
            line=dict(color='#EF5350', width=2, shape='spline'),
            marker=dict(size=6, color='#FF8A65'),
            fill='tozeroy',
            fillcolor='rgba(239,83,80,0.10)',
        ))
        fig_rh.update_layout(
            template='plotly_white',
            xaxis_title='Session',
            yaxis_title='Risk (0=low, 1=critical)',
            yaxis=dict(range=[0, 1]),
            height=280,
            margin=dict(l=40, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
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
    st.caption("7-day aggregated wellness summary with predictions and suggestions")

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
                line=dict(color='#4DD0E1', width=3, shape='spline'),
                marker=dict(size=7, color='#5B8CFF'),
                fill='tozeroy',
                fillcolor='rgba(77,208,225,0.12)',
            ))
            fig_wk.update_layout(
                template='plotly_white',
                xaxis_title='Day',
                yaxis_title='Avg Mood',
                height=280,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
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
            f'<div style="text-align:center;margin-bottom:0.5rem;">'
            f'<div style="width:64px;height:64px;border-radius:50%;'
            f'background:linear-gradient(135deg,#5B8CFF,#9B8CFF);'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:1.6rem;color:#fff;font-weight:700;'
            f'box-shadow:0 4px 15px rgba(91,140,255,0.3);">{initials}</div>'
            f'<p style="margin:0.4rem 0 0;font-weight:600;font-size:1.05rem;">'
            f'{user_id}</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Risk badge — color-coded
        summary = st.session_state.buddy.pattern_tracker.get_pattern_summary()
        risk_level = 'low'
        if summary:
            risk_level = summary.get('risk_level', 'low')
        _BADGE_STYLE = {
            'low':      ('🟢', '#5B8CFF', 'rgba(91,140,255,0.12)'),
            'medium':   ('🟡', '#FFB74D', 'rgba(255,183,77,0.15)'),
            'high':     ('🔴', '#EF5350', 'rgba(239,83,80,0.15)'),
            'critical': ('🚨', '#D32F2F', 'rgba(211,47,47,0.20)'),
        }
        r_icon, r_color, r_bg = _BADGE_STYLE.get(risk_level, _BADGE_STYLE['low'])
        st.markdown(
            f'<div style="text-align:center;padding:0.5rem;border-radius:0.5rem;'
            f'background:{r_bg};border:1px solid {r_color};margin-bottom:0.75rem;">'
            f'<span style="font-size:1.1rem;">{r_icon} Risk: '
            f'<strong style="color:{r_color};">{risk_level.upper()}</strong></span></div>',
            unsafe_allow_html=True,
        )

        # Session info + streak card
        if st.session_state.buddy.user_profile:
            sessions = st.session_state.buddy.user_profile.get_profile().get('session_count', 0)
            streak = st.session_state.buddy.user_profile.get_mood_streak()
            lang_pref = st.session_state.buddy.user_profile.get_language_preference()
            _LANG_ICONS = {'english': '🇬🇧', 'tamil': '🇮🇳', 'bilingual': '🇮🇳🇬🇧'}
            st.markdown(f"📅 **Session:** #{sessions + 1}")
            st.markdown(f"🌐 **Language:** {_LANG_ICONS.get(lang_pref, '🌐')} {lang_pref.capitalize()}")
            # Streak card
            streak_emoji = "🔥" if streak >= 3 else "⭐" if streak >= 1 else "💤"
            st.markdown(
                f'<div style="text-align:center;padding:0.5rem;border-radius:0.5rem;'
                f'background:linear-gradient(135deg,rgba(77,208,225,0.12),rgba(155,140,255,0.12));'
                f'margin:0.5rem 0;">'
                f'<span style="font-size:1.4rem;">{streak_emoji}</span><br>'
                f'<strong>{streak}</strong> positive streak</div>',
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

        # Background ambient music toggle
        st.session_state.calm_music_enabled = st.toggle(
            "🎵 Calm Background Mode",
            value=st.session_state.get('calm_music_enabled', False),
            help="Play a calming ambient loop. Audio starts after interaction (browser policy safe).",
        )

        st.markdown("---")
        st.markdown("### Quick Actions")

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

    st.markdown(f"""
    <style>
    /* ---- Animated gradient background ---- */
    @keyframes gradientBG {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .stApp {{
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 25%, #fff5f0 50%, #f0fffe 75%, #f0f4ff 100%);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
    }}

    /* ---- Glassmorphism chat cards ---- */
    .stChatMessage {{
        padding: 1rem 1.25rem;
        border-radius: 1rem;
        background: rgba(255,255,255,0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.35);
        box-shadow: 0 4px 20px {glow_color};
        margin-bottom: 0.75rem;
        animation: fadeInUp 0.4s ease-out;
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ---- Premium chat input bar ---- */
    [data-testid="stChatInput"] {{
        background: rgba(255,255,255,0.70) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 1.25rem !important;
        border: 1px solid rgba(91,140,255,0.18) !important;
        box-shadow: 0 4px 24px rgba(91,140,255,0.08);
        transition: box-shadow 0.3s ease, border-color 0.3s ease;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: #5B8CFF !important;
        box-shadow: 0 4px 28px rgba(91,140,255,0.16);
    }}
    [data-testid="stChatInput"] textarea {{
        font-size: 0.98rem;
    }}

    /* ---- Sidebar polish ---- */
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem;
        background: linear-gradient(180deg, rgba(91,140,255,0.06), rgba(155,140,255,0.06));
    }}

    /* ---- Tab labels with transition ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.25rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 0.5rem 0.5rem 0 0;
        transition: color 0.3s ease, background 0.3s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: #5B8CFF;
        background: rgba(91,140,255,0.06);
    }}

    /* ---- Metric cards — glassmorphism ---- */
    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.70);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 0.75rem;
        padding: 0.75rem;
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(91,140,255,0.12);
    }}

    /* ---- Button hover glow ---- */
    .stButton > button {{
        border-radius: 0.5rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(91,140,255,0.2);
    }}
    .stButton > button:hover {{
        box-shadow: 0 0 16px rgba(91,140,255,0.25);
        border-color: #5B8CFF;
        transform: translateY(-1px);
    }}

    /* ---- Expander styling ---- */
    .streamlit-expanderHeader {{
        font-weight: 600;
    }}

    /* ---- Header area ---- */
    .main-header {{
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        color: #5B8CFF;
    }}
    .main-header h1 {{
        font-size: 2.2rem;
        margin-bottom: 0;
        background: linear-gradient(135deg, #5B8CFF, #9B8CFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .main-header p {{ color: #64748B; font-size: 0.95rem; margin-top: 0.25rem; }}

    /* ---- Risk-level atmospheric border ---- */
    .main .block-container {{
        border-top: 3px solid {border_color};
        transition: border-color 0.5s ease;
    }}

    /* ---- Critical pulsing warning bar ---- */
    {critical_bar_css}

    /* ---- Smooth card hover elevation ---- */
    .stExpander, [data-testid="stVerticalBlock"] > div {{
        transition: box-shadow 0.3s ease;
    }}

    /* ---- Profile setup form glassmorphism ---- */
    [data-testid="stForm"] {{
        background: rgba(255,255,255,0.60);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 1rem;
        border: 1px solid rgba(255,255,255,0.30);
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(91,140,255,0.08);
    }}
    </style>
    """, unsafe_allow_html=True)

    # ---- Background ambient music ----
    if st.session_state.get('calm_music_enabled', False):
        # Royalty-free ambient audio data URI (tiny silent init + JS-driven)
        st.markdown(
            """
            <div id="ambient-music-container" style="display:none;">
                <p style="font-size:0.75rem;color:#9B8CFF;">🎵 Calm mode active</p>
            </div>
            <script>
            (function() {
                if (window._ambientInitialized) return;
                window._ambientInitialized = true;
                try {
                    var ctx = new (window.AudioContext || window.webkitAudioContext)();
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.value = 174;  // 174 Hz Solfeggio frequency for relaxation
                    gain.gain.value = 0.03;  // Low volume — subtle background ambience
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    window._ambientOsc = osc;
                    window._ambientGain = gain;
                    window._ambientCtx = ctx;
                } catch(e) {}
            })();
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
                    window._ambientInitialized = false;
                }
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

    if not st.session_state.profile_loaded:
        show_profile_setup()
    else:
        show_chat_interface()


if __name__ == "__main__":
    main()
