"""
Web UI for AI Wellness Buddy using Streamlit.
Multi-tab layout: Chat | Emotional Trends | Risk Dashboard | Weekly Report
Supports bilingual Tamil & English with Tanglish and voice input/output.
Run with: streamlit run ui_app.py
"""

import streamlit as st
from wellness_buddy import WellnessBuddy
from user_profile import UserProfile
from data_store import DataStore
from prediction_agent import PredictionAgent
from voice_handler import VoiceHandler
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
    """Show microphone recorder and return transcribed text or None.

    Uses session-state deduplication (``last_voice_bytes``) to ensure each
    recording is processed exactly once, preventing the auto-trigger loop
    caused by Streamlit reruns.
    """
    try:
        from audio_recorder_streamlit import audio_recorder
    except ImportError:
        st.caption("🎤 Install `audio-recorder-streamlit` for voice input.")
        return None

    vh: VoiceHandler = st.session_state.voice_handler
    if vh is None or not vh.stt_available:
        st.caption("🎤 Speech recognition unavailable (SpeechRecognition not installed).")
        return None

    # Minimum bytes for a viable audio sample (~1 second at 16-bit 8kHz mono)
    MIN_AUDIO_BYTES = 1000

    st.markdown("**🎤 Voice input** — click the mic, speak, click again to stop:")
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#5B7FE8",
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
        user_name = st.session_state.user_id or "there"
        greeting = (
            f"Hello **{user_name}** 👋  \n"
            "I'm your Wellness Buddy — a safe, confidential space for emotional support.  \n"
            "Share how you're feeling, and I'll do my best to listen and help."
        )
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Display chat history
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

    # Voice input section (collapsible)
    with st.expander("🎤 Voice Input (click to expand)", expanded=False):
        voice_transcript = _handle_voice_input()
        if voice_transcript:
            # Auto-send transcribed text as a message
            st.session_state.messages.append({"role": "user", "content": voice_transcript})
            response = st.session_state.buddy.process_message(voice_transcript)
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Auto-play TTS for voice-initiated responses
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
    """Render the Emotional Trends tab with charts"""
    st.subheader("📈 Emotional Trends")
    st.caption("Real-time sentiment tracking and historical mood analysis")

    buddy = st.session_state.buddy
    summary = buddy.pattern_tracker.get_pattern_summary()
    history = buddy.user_profile.get_emotional_history(days=30)

    # ---- Current session sentiment line ----
    sentiments = list(buddy.pattern_tracker.sentiment_history)
    if sentiments:
        st.markdown("#### Current Session — Sentiment Over Messages")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.line_chart({"Sentiment": sentiments})
        with col2:
            if summary:
                ma = summary.get('moving_average', [])
                if len(ma) >= 2:
                    st.line_chart({"3-msg Moving Avg": ma})
                    st.caption("3-message moving average of sentiment")
    else:
        st.info("Start chatting to see your sentiment trend.")

    # ---- Emotion distribution (current session) ----
    if summary:
        dist = summary.get('emotion_distribution', {})
        if dist:
            st.markdown("#### Current Session — Emotion Distribution")
            col_a, col_b = st.columns([1, 2])
            with col_a:
                for emo, cnt in sorted(dist.items(), key=lambda x: -x[1]):
                    st.metric(label=emo.capitalize(), value=cnt)
            with col_b:
                st.bar_chart(dist)

    # ---- Historical 30-day sentiment ----
    if history:
        st.markdown("#### Last 30 Days — Average Mood per Session")
        hist_data = []
        for snap in history:
            ss = snap.get('session_summary', {}) or {}
            avg = ss.get('average_sentiment', None)
            if avg is not None:
                hist_data.append(avg)

        if hist_data:
            st.line_chart({"Avg Mood": hist_data})

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
    """Render the Risk Dashboard tab"""
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
    st.progress(min(1.0, risk_score), text=f"Risk score: {risk_score:.2f} / 1.00")

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

    # Risk history (last 30 days)
    history = buddy.user_profile.get_emotional_history(days=30)
    risk_hist = []
    for snap in history:
        ed = snap.get('emotion_data', {}) or {}
        rl = ed.get('risk_level', None)
        if rl:
            risk_hist.append(_RISK_LEVEL_VALUES.get(rl, 0.10))

    if risk_hist:
        st.markdown("#### 30-Day Risk Level History")
        st.line_chart({"Risk (0=low, 1=critical)": risk_hist})

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
    """Render the Weekly Report tab"""
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
            st.line_chart({"Daily Avg Mood": sentiments})

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
    # Sidebar
    with st.sidebar:
        st.markdown("#### 🌟 AI Wellness Buddy")
        st.markdown("---")
        st.markdown(f"**👤 User:** {st.session_state.user_id}")

        if st.session_state.buddy.user_profile:
            sessions = st.session_state.buddy.user_profile.get_profile().get('session_count', 0)
            streak = st.session_state.buddy.user_profile.get_mood_streak()
            lang_pref = st.session_state.buddy.user_profile.get_language_preference()
            st.markdown(f"**📅 Session:** #{sessions + 1}")
            if streak > 0:
                st.markdown(f"**🔥 Streak:** {streak} positive")
            _LANG_ICONS = {'english': '🇬🇧', 'tamil': '🇮🇳', 'bilingual': '🇮🇳🇬🇧'}
            st.markdown(f"**🌐 Language:** {_LANG_ICONS.get(lang_pref, '🌐')} {lang_pref.capitalize()}")

        summary = st.session_state.buddy.pattern_tracker.get_pattern_summary()
        if summary:
            risk_icon = _RISK_COLOUR.get(summary.get('risk_level', 'low'), '⬜')
            st.markdown(f"**⚠️ Risk:** {risk_icon} {summary.get('risk_level', 'low').upper()}")

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
    st.markdown("""
    <style>
    /* ---- Professional chat bubble styling ---- */
    .stChatMessage {
        padding: 1rem 1.25rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 0.5rem;
    }
    /* ---- Sidebar polish ---- */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    /* ---- Tab labels ---- */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
    }
    /* ---- Metric cards ---- */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border-radius: 0.5rem;
        padding: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    /* ---- Expander styling ---- */
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    /* ---- Header area ---- */
    .main-header {
        text-align: center;
        padding: 0.5rem 0 0.25rem 0;
        color: #5B7FE8;
    }
    .main-header h1 { font-size: 2rem; margin-bottom: 0; }
    .main-header p { color: #64748B; font-size: 0.95rem; margin-top: 0.25rem; }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.profile_loaded:
        show_profile_setup()
    else:
        show_chat_interface()


if __name__ == "__main__":
    main()
