"""
Visualization Agent — Module 6
Multi-tab Streamlit UI: Chat | Emotional Trends | Weekly Summary |
                        Risk Prediction | Guardian Alerts | Profile
"""

import streamlit as st
from wellness_buddy import WellnessBuddy
from user_profile import UserProfile
from data_store import DataStore
from datetime import datetime, timedelta
import os
import config

# ── Optional heavy deps ───────────────────────────────────────────────────────
try:
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    _CHARTS_AVAILABLE = True
except ImportError:
    _CHARTS_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Wellness Buddy",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ('buddy', None), ('messages', []), ('user_id', None),
    ('profile_loaded', False), ('show_load', False),
    ('show_create', False), ('show_profile_menu', False),
    ('pending_username', None), ('login_error', None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ───────────────────────────────────────────────────────────────────

def init_buddy():
    if st.session_state.buddy is None:
        st.session_state.buddy = WellnessBuddy()
        st.session_state.buddy.data_store = DataStore()

def load_profile(username):
    init_buddy()
    st.session_state.user_id = username
    st.session_state.buddy._load_existing_profile(username)
    st.session_state.profile_loaded = True
    st.success(f"✓ Profile loaded: {username}")
    st.rerun()


def _initiate_login(username):
    """Start the password-check flow for an existing profile."""
    data_store = DataStore()
    raw_data = data_store.load_user_data(username)
    if raw_data and raw_data.get('password_hash') is not None:
        # Profile is password-protected — show the auth form
        st.session_state.pending_username = username
        st.rerun()
    else:
        # No password set — load directly
        load_profile(username)


def _show_login_form():
    """Render the password entry form for a pending profile load."""
    username = st.session_state.pending_username
    st.markdown(f"#### 🔒 Password Required for **{username}**")

    data_store = DataStore()
    raw_data = data_store.load_user_data(username)
    if not raw_data:
        st.error("Profile not found.")
        if st.button("← Back"):
            st.session_state.pending_username = None
            st.rerun()
        return

    profile = UserProfile(username)
    profile.load_from_data(raw_data)

    if profile.is_locked_out():
        st.error(
            f"🔒 Account locked due to too many failed login attempts. "
            f"Please try again in {config.LOCKOUT_DURATION_MINUTES} minutes."
        )
        if st.button("← Back"):
            st.session_state.pending_username = None
            st.rerun()
        return

    # Show any error from the previous attempt
    if st.session_state.login_error:
        st.error(st.session_state.login_error)
        st.session_state.login_error = None

    attempts_used = raw_data.get('failed_login_attempts', 0)
    if attempts_used > 0:
        st.caption(
            f"⚠️ {attempts_used} failed attempt(s). "
            f"{max(0, config.MAX_LOGIN_ATTEMPTS - attempts_used)} remaining before lockout."
        )

    with st.form("login_form"):
        password = st.text_input(
            "Profile Password:", type="password",
            placeholder="Enter your profile password"
        )
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔓 Unlock Profile", use_container_width=True)
        with col2:
            back = st.form_submit_button("← Back", use_container_width=True)

    if back:
        st.session_state.pending_username = None
        st.rerun()

    if submitted:
        if profile.verify_password(password):
            # Persist the reset of failed_login_attempts to disk
            data_store.save_user_data(username, profile.get_profile())
            st.session_state.pending_username = None
            load_profile(username)
        else:
            # Persist the incremented failed attempt count to disk
            data_store.save_user_data(username, profile.get_profile())
            attempts = profile.get_profile().get('failed_login_attempts', 0)
            if profile.is_locked_out():
                st.session_state.login_error = (
                    f"🔒 Account locked for {config.LOCKOUT_DURATION_MINUTES} minutes "
                    "due to too many failed attempts."
                )
            else:
                remaining = max(0, config.MAX_LOGIN_ATTEMPTS - attempts)
                st.session_state.login_error = (
                    f"❌ Incorrect password. {remaining} attempt(s) remaining."
                )
            st.rerun()

# ── Custom CSS ────────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #f0f4f8; }
    /* Headings */
    h1 { color: #2c6e9e; }
    h2, h3 { color: #3a7abf; }
    /* Chat bubbles */
    .stChatMessage { border-radius: 0.75rem; margin-bottom: 0.5rem; }
    /* Buttons */
    .stButton > button { border-radius: 0.5rem; font-weight: 500; }
    /* Metric cards */
    [data-testid="metric-container"] {
        background: #f7faff;
        border: 1px solid #d0e4f7;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROFILE SETUP
# ══════════════════════════════════════════════════════════════════════════════

def show_profile_setup():
    st.title("🌟 AI Wellness Buddy")
    st.markdown("### Welcome! Let's set up your profile")

    # If a password check is in progress, show only the login form
    if st.session_state.pending_username:
        _show_login_form()
        return

    data_store = DataStore()
    existing_users = data_store.list_users()

    if existing_users:
        st.info(f"Found {len(existing_users)} existing profile(s)")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Existing Profile", use_container_width=True):
                st.session_state.show_load = True
        with col2:
            if st.button("Create New Profile", use_container_width=True):
                st.session_state.show_create = True

        if st.session_state.show_load:
            username = st.selectbox("Select your username:", existing_users)
            if st.button("Load Profile"):
                _initiate_login(username)

        if st.session_state.show_create:
            _create_new_profile_form()
    else:
        st.info("No existing profiles found. Let's create one!")
        _create_new_profile_form()


def _create_new_profile_form():
    st.markdown("#### 📋 Tell us about yourself")
    st.caption("Fields marked * are required. Everything else is optional but helps personalise your experience.")

    with st.form("new_profile"):
        st.markdown("**Basic Information**")
        col_a, col_b = st.columns(2)
        with col_a:
            username = st.text_input("Username * (private, never shared):", key="new_username")
            display_name = st.text_input("Preferred name (how we address you):", key="display_name")
        with col_b:
            age_val = st.number_input("Age:", min_value=10, max_value=100, value=18, step=1)
            occupation = st.text_input("Occupation / Student status:", key="occupation",
                                       placeholder="e.g. Software Engineer, College Student")

        st.markdown("---")
        st.markdown("**About You**")
        gender = st.selectbox("How do you identify?",
                              ["Prefer not to say", "Female", "Male", "Non-binary", "Other"])
        primary_concerns = st.multiselect(
            "What brings you here? (select all that apply)",
            ["Stress & Anxiety", "Depression / Low Mood", "Loneliness",
             "Relationship Issues", "Work / Academic Pressure",
             "Family Problems", "Grief / Loss", "Self-esteem",
             "Trauma", "General Wellbeing", "Other"]
        )

        safe_family = "Skip"
        if gender == "Female":
            st.info("💙 Specialized support resources for women are available.")
            safe_family = st.radio("Do you feel safe with your family/guardians?",
                                   ["Skip", "Yes", "No"])
            if safe_family == "No":
                st.warning("🛡️ Your safety is paramount. I will guide you toward trusted support.")

        st.markdown("---")
        st.markdown("**Guardian / Emergency Contact** *(highly recommended)*")
        st.info(
            "🔔 **How alerts work:** When sustained distress is detected, an alert appears "
            "in the **Guardian Alerts** tab with your guardian's details. You stay in full control."
        )
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            guardian_name = st.text_input("Guardian's name:", placeholder="e.g. Mum, Dad, Dr. Smith")
        with col_g2:
            guardian_rel = st.text_input("Relationship:", placeholder="e.g. Parent, Counsellor")
        with col_g3:
            guardian_contact = st.text_input("Phone / Email:", placeholder="e.g. +1-555-0100")

        st.markdown("---")
        st.markdown("**🔒 Profile Password** *(recommended for privacy)*")
        st.info("Set a password so only you can open this profile. Leave blank to skip.")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            new_password = st.text_input(
                f"Password (min {config.MIN_PASSWORD_LENGTH} characters):",
                type="password", key="new_password",
                placeholder="Leave blank for no password"
            )
        with col_p2:
            confirm_password = st.text_input(
                "Confirm password:", type="password", key="confirm_password"
            )

        st.markdown("---")
        submitted = st.form_submit_button("✅ Create My Profile", use_container_width=True)

        if submitted:
            if not username:
                st.error("Please choose a username.")
                return
            # Validate password if provided
            if new_password:
                if new_password != confirm_password:
                    st.error("❌ Passwords do not match. Please try again.")
                    return
                if len(new_password) < config.MIN_PASSWORD_LENGTH:
                    st.error(f"❌ Password must be at least {config.MIN_PASSWORD_LENGTH} characters.")
                    return
            init_buddy()
            st.session_state.user_id = username
            st.session_state.buddy.user_id = username
            profile = UserProfile(username)

            if display_name:
                profile.set_name(display_name)
            if age_val:
                profile.set_age(int(age_val))
            if occupation:
                profile.set_occupation(occupation)
            if primary_concerns:
                profile.set_primary_concerns(primary_concerns)
            if gender != "Prefer not to say":
                profile.set_gender(gender.lower())
            if safe_family == "No":
                profile.add_unsafe_contact('family/guardians')
            if guardian_name and guardian_rel:
                profile.add_guardian_contact(
                    guardian_name, guardian_rel,
                    guardian_contact if guardian_contact else None
                )
            if new_password:
                profile.set_password(new_password)

            st.session_state.buddy.user_profile = profile
            st.session_state.buddy._save_profile()
            st.session_state.profile_loaded = True
            if new_password:
                st.success("✓ Profile created with password protection! Welcome 🎉🔒")
            else:
                st.success("✓ Profile created! Welcome 🎉")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABBED INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def show_main_interface():
    buddy = st.session_state.buddy
    profile_data = buddy.user_profile.get_profile() if buddy.user_profile else {}
    display_name = profile_data.get('name') or st.session_state.user_id or "Friend"

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"## 👤 {display_name}")
        if profile_data.get('occupation'):
            st.caption(profile_data['occupation'])
        if profile_data.get('age'):
            st.caption(f"Age: {profile_data['age']}")
        sessions = profile_data.get('session_count', 0)
        st.markdown(f"**Session #{sessions + 1}**")

        # Module 13 — Gamification metrics in sidebar
        streak = profile_data.get('mood_streak', 0)
        stability = profile_data.get('stability_score', 50.0)
        badges = profile_data.get('badges', [])
        if streak > 0:
            fire = "🔥" * min(streak, 5)
            st.success(f"{fire} **{streak}-session positive streak!**")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Stability", f"{stability:.0f}/100")
        col_s2.metric("Badges", len(badges))
        if badges:
            with st.expander("🏆 My Badges"):
                for b in badges[-5:]:
                    st.caption(f"{b['name']} — {b['desc']}")

        concerns = profile_data.get('primary_concerns', [])
        if concerns:
            st.markdown("**Focus areas:**")
            for c in concerns:
                st.caption(f"• {c}")

        st.markdown("---")
        if st.button("📞 Help & Resources", use_container_width=True):
            response = buddy._show_resources()
            st.session_state.messages.append({"role": "assistant", "content": response, "type": "info"})
        if st.button("⚙️ Manage Profile", use_container_width=True):
            st.session_state.show_profile_menu = True
        st.markdown("---")
        if st.button("🚪 End Session", use_container_width=True):
            response = buddy._end_session()
            st.session_state.messages.append({"role": "assistant", "content": response, "type": "info"})
            st.session_state.profile_loaded = False
            st.session_state.buddy = None
            st.rerun()

    if st.session_state.show_profile_menu:
        _show_profile_menu_sidebar()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "💬 Chat",
        "📈 Emotional Trends",
        "📅 Weekly Summary",
        "🔮 Risk Prediction",
        "🚨 Guardian Alerts",
        "👤 Profile",
    ])

    with tabs[0]:
        _tab_chat(buddy, display_name)
    with tabs[1]:
        _tab_emotional_trends(buddy)
    with tabs[2]:
        _tab_weekly_summary(buddy)
    with tabs[3]:
        _tab_risk_prediction(buddy)
    with tabs[4]:
        _tab_guardian_alerts(buddy)
    with tabs[5]:
        _tab_profile(buddy, profile_data, display_name)


# ── Tab: Chat ─────────────────────────────────────────────────────────────────

def _tab_chat(buddy, display_name):
    st.header(f"🌟 Hi, {display_name}!")

    # Show current session emotion metrics
    summary = buddy.pattern_tracker.get_pattern_summary()
    if summary:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Messages", summary['total_messages'])
        c2.metric("Trend", summary['trend'].replace('_', ' ').title())
        c3.metric("Severity", summary['severity_level'])
        sent_val = summary.get('weighted_sentiment', summary['average_sentiment'])
        c4.metric("Sentiment", f"{sent_val:.2f}")
        st.markdown("---")

    # Chat history with RL feedback buttons (Module 10)
    messages = st.session_state.messages
    for idx, message in enumerate(messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Show 👍/👎 only on regular (non-crisis/alert) assistant messages
            if (message["role"] == "assistant"
                    and message.get("type") == "response"):
                key_base = f"fb_{idx}"
                c_a, c_b, _ = st.columns([1, 1, 8])
                with c_a:
                    if st.button("👍", key=f"{key_base}_up", help="This helped"):
                        _record_feedback(buddy, message.get("template_key"), positive=True)
                with c_b:
                    if st.button("👎", key=f"{key_base}_dn", help="Not helpful"):
                        _record_feedback(buddy, message.get("template_key"), positive=False)

    # Module 8 — XAI: show explanation for the last analyzed emotion
    if messages and buddy.pattern_tracker.emotion_history:
        last_emotion_data = list(buddy.pattern_tracker.emotion_history)[-1]
        explanation = last_emotion_data.get('keyword_explanation', [])
        if explanation:
            with st.expander("🔍 Why did the system classify this emotion? (Explainable AI)"):
                st.caption("These keywords influenced the emotion classification:")
                cols_xai = st.columns(min(len(explanation), 4))
                for i, item in enumerate(explanation[:8]):
                    with cols_xai[i % len(cols_xai)]:
                        contrib_color = "🔴" if item['contribution'] == 'high' else "🟠"
                        st.markdown(
                            f"{contrib_color} **{item['word']}**  \n"
                            f"→ _{item['emotion']}_"
                        )

    # Input
    if prompt := st.chat_input(f"Share how you're feeling, {display_name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "user"})
        response = buddy.process_message(prompt)
        # Determine message type for feedback gating
        if response.startswith("🆘"):
            msg_type = "crisis"
        elif response.startswith("⚠️"):
            msg_type = "alert"
        else:
            msg_type = "response"
        template_key = buddy.conversation_handler.get_last_template_key()
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "type": msg_type,
            "template_key": template_key,
        })
        # Module 11 — show crisis banner prominently at the top
        if msg_type == "crisis":
            st.error("🆘 Crisis resources are shown above. Please reach out immediately.", icon="🆘")
        st.rerun()


def _record_feedback(buddy, template_key, positive: bool):
    """Module 10 — record RL feedback for a specific response template_key."""
    if template_key and buddy.user_profile:
        buddy.user_profile.record_response_feedback(template_key, positive)
        buddy._save_profile()
    if positive:
        st.toast("Thanks for the feedback! 👍", icon="💙")
    else:
        st.toast("Got it — I'll try to respond better. 👎", icon="💬")


# ── Tab: Emotional Trends ─────────────────────────────────────────────────────

def _tab_emotional_trends(buddy):
    st.header("📈 Emotional Trends")

    if not _CHARTS_AVAILABLE:
        st.warning("Install pandas and plotly for charts: `pip install pandas plotly`")
        return

    # Session-level sentiment line chart
    history = list(buddy.pattern_tracker.emotion_history)
    if not history:
        st.info("Start chatting to see emotional trends here.")
        return

    sentiments = [e['polarity'] for e in history]
    emotions = [e.get('dominant_emotion', e.get('emotion', 'neutral')) for e in history]
    indices = list(range(1, len(sentiments) + 1))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Sentiment Over This Session")
        df = pd.DataFrame({'Message #': indices, 'Sentiment': sentiments, 'Emotion': emotions})
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Message #'], y=df['Sentiment'],
            mode='lines+markers',
            marker=dict(color=df['Sentiment'], colorscale='RdYlGn',
                        cmin=-1, cmax=1, size=10),
            line=dict(color='#3a7abf', width=2),
            hovertemplate="Msg %{x}<br>Sentiment: %{y:.2f}<br>Emotion: %{text}",
            text=emotions,
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.update_layout(
            xaxis_title="Message Number",
            yaxis_title="Sentiment Score",
            yaxis=dict(range=[-1.1, 1.1]),
            height=320,
            margin=dict(t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Emotion Distribution")
        dist = buddy.pattern_tracker.get_emotion_distribution()
        labels = [k.title() for k in dist]
        values = list(dist.values())
        if sum(values) > 0:
            fig_pie = px.pie(
                names=labels, values=values,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.35,
            )
            fig_pie.update_layout(height=320, margin=dict(t=30, b=30))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Not enough data yet.")

    # Long-term history heatmap
    lth = buddy.user_profile.get_emotional_history() if buddy.user_profile else []
    if lth:
        st.subheader("Long-Term Emotional History")
        rows = []
        for snap in lth[-30:]:
            ps = snap.get('session_summary') or {}
            rows.append({
                'Date': snap.get('date', ''),
                'Avg Sentiment': ps.get('average_sentiment', 0),
                'Messages': ps.get('total_messages', 0),
            })
        df_lt = pd.DataFrame(rows)
        if not df_lt.empty:
            fig_lt = px.bar(df_lt, x='Date', y='Avg Sentiment',
                            color='Avg Sentiment',
                            color_continuous_scale='RdYlGn',
                            range_color=[-1, 1],
                            title="Average Sentiment per Session (last 30)")
            fig_lt.update_layout(height=300, margin=dict(t=50, b=30))
            st.plotly_chart(fig_lt, use_container_width=True)


# ── Tab: Weekly Summary ───────────────────────────────────────────────────────

def _tab_weekly_summary(buddy):
    st.header("📅 Weekly Summary")

    if not _CHARTS_AVAILABLE:
        st.warning("Install pandas and plotly for charts.")
        return

    lth = buddy.user_profile.get_emotional_history(days=7) if buddy.user_profile else []
    if not lth:
        st.info("Complete a few sessions to see your weekly summary here.")
        _show_current_session_summary(buddy)
        return

    rows = []
    for snap in lth:
        ps = snap.get('session_summary') or {}
        rows.append({
            'Date': snap.get('date', 'Unknown'),
            'Avg Sentiment': round(ps.get('average_sentiment', 0), 3),
            'Messages': ps.get('total_messages', 0),
            'Distress Messages': ps.get('distress_messages', 0),
            'Trend': ps.get('trend', 'N/A'),
        })
    df = pd.DataFrame(rows)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Daily Sentiment (Last 7 Days)")
        fig = px.bar(df, x='Date', y='Avg Sentiment',
                     color='Avg Sentiment', color_continuous_scale='RdYlGn',
                     range_color=[-1, 1], text='Avg Sentiment')
        fig.update_traces(texttemplate='%{text:.2f}')
        fig.update_layout(height=300, margin=dict(t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Session Message Counts")
        fig2 = px.bar(df, x='Date', y=['Messages', 'Distress Messages'],
                      barmode='group',
                      color_discrete_sequence=['#3a7abf', '#e07070'])
        fig2.update_layout(height=300, margin=dict(t=30, b=30))
        st.plotly_chart(fig2, use_container_width=True)

    # Summary stats
    st.subheader("Week at a Glance")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sessions", len(lth))
    c2.metric("Avg Sentiment", f"{df['Avg Sentiment'].mean():.3f}")
    positive_days = (df['Avg Sentiment'] > 0).sum()
    c3.metric("Positive Days", f"{positive_days}/{len(lth)}")

    # Module 6 — Personalised recommendations
    st.markdown("---")
    st.subheader("💡 Personalised Recommendations")
    avg_sent = df['Avg Sentiment'].mean()
    total_distress = df['Distress Messages'].sum()
    trend_vals = list(df['Trend'])
    if avg_sent >= 0.3:
        st.success("✅ You've had a strong positive week! Keep nurturing the habits that support your wellbeing.")
    elif avg_sent >= 0.0:
        st.info("🌤 Your week was mostly stable. Consider light mindfulness or journaling to build on this.")
    elif avg_sent >= -0.3:
        st.warning("⚠️ Your week had some difficult moments. Try to schedule breaks and reach out to trusted people.")
    else:
        st.error("🔴 Your week was challenging. Please consider speaking with a mental health professional.")
    if total_distress > 0:
        st.markdown(f"- You had **{int(total_distress)} distress message(s)** this week — "
                    "be kind to yourself and use the Help & Resources in the sidebar.")
    if 'worsening' in trend_vals:
        st.markdown("- Some sessions showed a **worsening trend** — the Risk Prediction tab may show more insight.")
    if 'improving' in trend_vals:
        st.markdown("- Great news: some sessions showed an **improving trend**. 🌟")

    # Module 12 — Export weekly summary as JSON
    st.markdown("---")
    st.subheader("📥 Export")
    import json as _json
    export_data = {
        'export_type': 'weekly_summary',
        'exported_at': datetime.now().isoformat(),
        'user_id': st.session_state.user_id,
        'sessions': rows,
        'avg_sentiment': float(df['Avg Sentiment'].mean()),
        'positive_days': int(positive_days),
    }
    st.download_button(
        "⬇️ Download Weekly Summary (JSON)",
        data=_json.dumps(export_data, indent=2),
        file_name=f"wellness_summary_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
    )
    if _CHARTS_AVAILABLE:
        st.download_button(
            "⬇️ Download Weekly Summary (CSV)",
            data=df.to_csv(index=False),
            file_name=f"wellness_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    _show_current_session_summary(buddy)


def _show_current_session_summary(buddy):
    """Show a mini summary of the current session."""
    summary = buddy.pattern_tracker.get_pattern_summary()
    if not summary:
        return
    st.subheader("📊 Current Session Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Messages", summary['total_messages'])
    c2.metric("Distress", summary['distress_messages'])
    c3.metric("Trend", summary['trend'].title())
    c4.metric("Severity", summary['severity_level'])


# ── Tab: Risk Prediction ─────────────────────────────────────────────────────

def _tab_risk_prediction(buddy):
    st.header("🔮 Risk Prediction")
    st.caption("Temporal trend model — predicts your next emotional state from recent messages.")

    if not _CHARTS_AVAILABLE:
        st.warning("Install pandas and plotly for charts.")
        return

    agent = buddy.prediction_agent
    history = list(agent._sentiment_buf)

    if len(history) < 3:
        st.info("💬 Send a few more messages (at least 3) to activate the prediction model.")
        return

    # Prediction
    prediction = agent.predict_next_state()
    metrics = agent.get_metrics()
    forecast = agent.get_forecast_series(steps=5)

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trend", prediction['trend'].title())
    c2.metric("Predicted Sentiment", f"{prediction['predicted_sentiment']:.3f}")
    c3.metric("Confidence", f"{prediction['confidence']:.0%}")
    mae_disp = f"{metrics['mae']:.3f}" if metrics['mae'] is not None else "N/A"
    c4.metric("MAE", mae_disp)

    if prediction.get('warning_message'):
        st.warning(prediction['warning_message'])

    # Forecast chart
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Sentiment Trend & Forecast")
        indices_hist = list(range(1, len(history) + 1))
        indices_fore = list(range(len(history) + 1, len(history) + len(forecast) + 1))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=indices_hist, y=history,
            mode='lines+markers', name='Observed',
            line=dict(color='#3a7abf', width=2),
            marker=dict(size=7),
        ))
        if forecast:
            fig.add_trace(go.Scatter(
                x=indices_fore, y=forecast,
                mode='lines+markers', name='Forecast',
                line=dict(color='#e07070', width=2, dash='dash'),
                marker=dict(size=7, symbol='diamond'),
            ))
        fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.4)
        fig.add_hline(y=-0.35, line_dash="dash", line_color="red", opacity=0.6,
                      annotation_text="Early warning threshold",
                      annotation_position="bottom right")
        fig.update_layout(
            xaxis_title="Message Number",
            yaxis_title="Sentiment Score",
            yaxis=dict(range=[-1.1, 1.1]),
            height=350,
            margin=dict(t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Model Metrics")
        st.markdown(f"- **Data points:** {metrics['data_points']}")
        st.markdown(f"- **MAE:** {mae_disp}")
        rmse_disp = f"{metrics['rmse']:.3f}" if metrics['rmse'] is not None else "N/A"
        st.markdown(f"- **RMSE:** {rmse_disp}")
        st.markdown(f"- **Predictions evaluated:** {metrics['n_predictions']}")
        st.markdown(f"- **Current trend:** {metrics['trend'].replace('_', ' ').title()}")

        st.caption("**Research note:** This module uses OLS linear regression "
                   "over a sliding window as a temporal prediction model. "
                   "Replace `_linreg_predict()` in `prediction_agent.py` with "
                   "an LSTM forward-pass when training data is available.")


# ── Tab: Guardian Alerts ──────────────────────────────────────────────────────

def _tab_guardian_alerts(buddy):
    st.header("🚨 Guardian Alerts")
    profile_data = buddy.user_profile.get_profile() if buddy.user_profile else {}
    display_name = profile_data.get('name') or st.session_state.user_id or "User"

    # Guardian contacts
    guardians = buddy.user_profile.get_guardian_contacts() if buddy.user_profile else []
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🔔 Guardian Contacts")
        if guardians:
            for g in guardians:
                st.markdown(f"**{g['name']}** — {g['relationship']}")
                if g.get('contact_info'):
                    st.caption(f"📞 {g['contact_info']}")
        else:
            st.info("No guardian contacts added yet. Add them in your Profile.")

    # Alert log
    with col2:
        st.subheader("📋 Alert Log")
        log = buddy.alert_system.get_alert_log()
        if log:
            if _CHARTS_AVAILABLE:
                import pandas as pd
                df = pd.DataFrame(log)
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
                df = df[['timestamp', 'severity', 'type', 'severity_score',
                          'sustained_distress', 'notify_guardians', 'acknowledged']]
                df.columns = ['Time', 'Severity', 'Type', 'Score',
                              'Sustained', 'Guardians Notified', 'Acknowledged']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                for entry in log[-10:]:
                    ts = entry.get('timestamp', '')
                    sev = entry.get('severity', 'N/A')
                    st.text(f"[{ts}] {sev} — Score: {entry.get('severity_score', 0):.1f}")
        else:
            st.success("✅ No alerts in this session. You're doing great!")

    # Pending alerts with consent mechanism
    st.markdown("---")
    st.subheader("⚡ Pending Alerts")
    pending = [a for a in buddy.alert_system.alerts_triggered if not a.get('acknowledged')]
    if pending:
        for i, alert in enumerate(pending):
            with st.expander(
                f"Alert #{i+1} — Severity: {alert['severity']} "
                f"at {alert['timestamp'].strftime('%H:%M:%S')}"
            ):
                sev = alert.get('severity', 'MEDIUM')
                sev_color = {'INFO': '🟢', 'LOW': '🟡', 'MEDIUM': '🟠',
                             'HIGH': '🔴', 'CRITICAL': '🚨'}.get(sev, '⚠️')
                st.markdown(f"**Severity:** {sev_color} {sev}")
                ps = alert.get('pattern_summary', {})
                st.markdown(f"- Sustained distress: {ps.get('sustained_distress_detected', False)}")
                st.markdown(f"- Severity score: {ps.get('severity_score', 0):.1f}/10")
                st.markdown(f"- Consecutive distress messages: {ps.get('consecutive_distress', 0)}")

                if alert.get('notify_guardians') and guardians:
                    st.markdown("**Guardian contacts:**")
                    for g in alert.get('guardian_contacts', []):
                        st.markdown(f"  • {g['name']} ({g['relationship']})"
                                    + (f" — {g['contact_info']}" if g.get('contact_info') else ""))

                    # Consent mechanism
                    if not alert.get('guardian_consent'):
                        if st.button(f"✅ Consent to notify guardians (Alert #{i+1})",
                                     key=f"consent_{i}"):
                            buddy.alert_system.grant_guardian_consent(alert)
                            st.success("Guardian notification consent granted.")
                            st.rerun()
                    else:
                        st.success("✅ Guardian consent granted.")

                if st.button(f"✔ Acknowledge (Alert #{i+1})", key=f"ack_{i}"):
                    buddy.alert_system.acknowledge_alert(alert)
                    st.rerun()
    else:
        st.info("No pending alerts.")

    # Severity level guide
    with st.expander("ℹ️ Alert Severity Guide"):
        st.markdown("""
| Severity | Meaning | Escalation |
|----------|---------|------------|
| 🟢 INFO | Minor concern detected | Escalates after 60 min |
| 🟡 LOW | Mild sustained negativity | Escalates after 30 min |
| 🟠 MEDIUM | Moderate distress | Escalates after 15 min |
| 🔴 HIGH | Sustained high distress | Escalates after 5 min |
| 🚨 CRITICAL | Severe distress + abuse indicators | Immediate action advised |
        """)


# ── Tab: Profile ──────────────────────────────────────────────────────────────

def _tab_profile(buddy, profile_data, display_name):
    st.header("👤 Profile")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Information")
        st.markdown(f"**Name:** {display_name}")
        st.markdown(f"**Username:** {profile_data.get('user_id', 'N/A')}")
        st.markdown(f"**Age:** {profile_data.get('age', 'Not set')}")
        st.markdown(f"**Occupation:** {profile_data.get('occupation', 'Not set')}")
        st.markdown(f"**Gender:** {profile_data.get('gender', 'Not set')}")
        concerns = profile_data.get('primary_concerns', [])
        if concerns:
            st.markdown(f"**Primary concerns:** {', '.join(concerns)}")
        st.markdown(f"**Sessions completed:** {profile_data.get('session_count', 0)}")
        st.markdown(f"**Response style:** {profile_data.get('response_style', 'balanced')}")

    with col2:
        st.subheader("Wellness Stats (Module 13)")
        streak = profile_data.get('mood_streak', 0)
        best_streak = profile_data.get('best_streak', 0)
        stability = profile_data.get('stability_score', 50.0)
        badges = profile_data.get('badges', [])
        st.metric("Current Streak 🔥", f"{streak} sessions")
        st.metric("Best Streak ⭐", f"{best_streak} sessions")
        st.metric("Stability Score 🎯", f"{stability:.0f}/100")
        if badges:
            st.markdown("**Earned Badges:**")
            for b in badges:
                st.caption(f"{b['name']} — {b['desc']}")
        else:
            st.info("No badges yet — keep chatting to earn them!")

    # Contacts in a separate row below
    st.markdown("---")
    st.subheader("👥 Contacts")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        trusted = buddy.user_profile.get_trusted_contacts()
        if trusted:
            st.markdown("**💚 Trusted Contacts:**")
            for c in trusted:
                st.markdown(f"• **{c['name']}** ({c['relationship']})"
                            + (f" — {c['contact_info']}" if c.get('contact_info') else ""))
        else:
            st.info("No trusted contacts added yet.")
    with col_c2:
        guardians = buddy.user_profile.get_guardian_contacts()
        if guardians:
            st.markdown("**🔔 Guardian Contacts:**")
            for g in guardians:
                st.markdown(f"• **{g['name']}** ({g['relationship']})"
                            + (f" — {g['contact_info']}" if g.get('contact_info') else ""))
        else:
            st.info("No guardian contacts added yet.")

    st.markdown("---")
    st.subheader("⚙️ Manage")

    # Show current password protection status
    has_password = bool(buddy.user_profile.get_profile().get('password_hash'))
    if has_password:
        st.success("🔒 This profile is password-protected.")
    else:
        st.info("🔓 No password set. Add one below to protect your profile.")

    action = st.selectbox("Action:", ["-- Choose --", "Add Trusted Contact",
                                       "Add Guardian Contact",
                                       "Set / Change Password",
                                       "Remove Password",
                                       "Set Response Style",
                                       "Delete All My Data"])
    if action == "Add Trusted Contact":
        with st.form("add_tc"):
            tc_name = st.text_input("Name:")
            tc_rel = st.text_input("Relationship:")
            tc_info = st.text_input("Contact Info (optional):")
            if st.form_submit_button("Add"):
                buddy.user_profile.add_trusted_contact(tc_name, tc_rel, tc_info or None)
                buddy._save_profile()
                st.success(f"✓ Added {tc_name}")
                st.rerun()
    elif action == "Add Guardian Contact":
        with st.form("add_gc"):
            gc_name = st.text_input("Name:")
            gc_rel = st.text_input("Relationship:")
            gc_info = st.text_input("Phone / Email:")
            if st.form_submit_button("Add Guardian"):
                if gc_name and gc_rel:
                    buddy.user_profile.add_guardian_contact(gc_name, gc_rel, gc_info or None)
                    buddy._save_profile()
                    st.success(f"✓ Added {gc_name}")
                    st.rerun()
    elif action == "Set / Change Password":
        with st.form("set_password"):
            st.markdown("**Set or change your profile password**")
            new_pw = st.text_input(
                f"New password (min {config.MIN_PASSWORD_LENGTH} characters):",
                type="password"
            )
            confirm_pw = st.text_input("Confirm new password:", type="password")
            if st.form_submit_button("🔒 Save Password"):
                if not new_pw:
                    st.error("Please enter a password.")
                elif new_pw != confirm_pw:
                    st.error("❌ Passwords do not match.")
                elif len(new_pw) < config.MIN_PASSWORD_LENGTH:
                    st.error(f"❌ Password must be at least {config.MIN_PASSWORD_LENGTH} characters.")
                else:
                    buddy.user_profile.set_password(new_pw)
                    buddy._save_profile()
                    st.success("✅ Password saved. Your profile is now protected.")
                    st.rerun()
    elif action == "Remove Password":
        st.warning("⚠️ This will remove password protection from your profile.")
        with st.form("remove_pw"):
            current_pw = st.text_input("Enter current password to confirm:", type="password")
            if st.form_submit_button("🔓 Remove Password"):
                if buddy.user_profile.verify_password(current_pw):
                    buddy.user_profile.remove_password()
                    buddy._save_profile()
                    st.success("✅ Password removed. Profile is now unprotected.")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password.")
    elif action == "Set Response Style":
        current_style = buddy.user_profile.get_profile().get('response_style', 'balanced')
        st.info(f"Current style: **{current_style}**")
        new_style = st.radio(
            "Choose your preferred response style:",
            ["short", "balanced", "detailed"],
            index=["short", "balanced", "detailed"].index(current_style),
            horizontal=True,
        )
        st.caption({
            "short": "Concise, one-sentence replies.",
            "balanced": "Standard empathetic responses (default).",
            "detailed": "Longer replies with a follow-up prompt.",
        }[new_style])
        if st.button("💾 Save Response Style"):
            buddy.user_profile.set_response_style(new_style)
            buddy._save_profile()
            st.success(f"✅ Response style set to **{new_style}**.")
            st.rerun()
    elif action == "Delete All My Data":
        st.warning("⚠️ This cannot be undone!")
        if st.button("Confirm Delete"):
            buddy.data_store.delete_user_data(st.session_state.user_id)
            st.session_state.profile_loaded = False
            st.session_state.buddy = None
            st.rerun()

    # Module 12 — Export Data
    st.markdown("---")
    st.subheader("📥 Data Export & Privacy")
    with st.expander("⬇️ Export My Data (Module 12 — Privacy & Ethical AI)"):
        import json as _json
        export_profile = {k: v for k, v in profile_data.items()
                          if k not in ('password_hash', 'salt')}  # never export credentials
        st.download_button(
            "⬇️ Download My Profile Data (JSON)",
            data=_json.dumps(export_profile, indent=2, default=str),
            file_name=f"my_wellness_data_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )
        st.caption("⚠️ Password hash and salt are **not** included in the export for your security.")

    with st.expander("🔏 Privacy Policy & Ethical AI"):
        st.markdown("""
### Privacy & Ethical AI

**Your data stays with you**
All profile data is stored only on your device (local filesystem).
No data is sent to external servers or third parties.

**Password protection**
Passwords are hashed with SHA-256 + a unique random salt.
Your plain-text password is never stored.

**Guardian consent**
Guardian notifications require your explicit consent.
You are always in control.

**Data deletion**
You can delete all your data at any time from the Manage section above.

**Ethical AI principles**
- This tool is **not a replacement** for professional mental health care.
- Crisis detection triggers immediate hotline resources, not automated calls.
- Emotion classification is rule-based (explainable) — no black-box models.
- User feedback (👍/👎) is used locally to personalise responses, not shared.
        """)


# ── Profile menu sidebar ──────────────────────────────────────────────────────

def _show_profile_menu_sidebar():
    with st.sidebar:
        st.markdown("### Profile Management")
        buddy = st.session_state.buddy

        action = st.selectbox("Choose action:",
                              ["Cancel", "Add Trusted Contact", "Add Guardian Contact",
                               "Mark Family Unsafe", "View Contacts"])
        if action == "Add Trusted Contact":
            with st.form("stc"):
                name = st.text_input("Name:")
                rel = st.text_input("Relationship:")
                info = st.text_input("Contact Info:")
                if st.form_submit_button("Add"):
                    buddy.user_profile.add_trusted_contact(name, rel, info or None)
                    buddy._save_profile()
                    st.success(f"✓ Added {name}")
                    st.session_state.show_profile_menu = False
        elif action == "Add Guardian Contact":
            with st.form("sgc"):
                g_name = st.text_input("Guardian name:")
                g_rel = st.text_input("Relationship:")
                g_info = st.text_input("Phone/Email:")
                if st.form_submit_button("Add"):
                    if g_name and g_rel:
                        buddy.user_profile.add_guardian_contact(g_name, g_rel, g_info or None)
                        buddy._save_profile()
                        st.success(f"✓ Added {g_name}")
                        st.session_state.show_profile_menu = False
        elif action == "Mark Family Unsafe":
            if st.button("Confirm"):
                buddy.user_profile.add_unsafe_contact('family/guardians')
                buddy._save_profile()
                st.success("✓ Family marked as unsafe")
                st.session_state.show_profile_menu = False
        elif action == "View Contacts":
            for c in buddy.user_profile.get_trusted_contacts():
                st.caption(f"💚 {c['name']} ({c['relationship']})")
            for g in buddy.user_profile.get_guardian_contacts():
                st.caption(f"🔔 {g['name']} ({g['relationship']})")
        if action == "Cancel" or st.button("Close"):
            st.session_state.show_profile_menu = False
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    _inject_css()
    if not st.session_state.profile_loaded:
        show_profile_setup()
    else:
        show_main_interface()


if __name__ == "__main__":
    main()
