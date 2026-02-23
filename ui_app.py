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
                load_profile(username)

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
        submitted = st.form_submit_button("✅ Create My Profile", use_container_width=True)

        if submitted:
            if not username:
                st.error("Please choose a username.")
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

            st.session_state.buddy.user_profile = profile
            st.session_state.buddy._save_profile()
            st.session_state.profile_loaded = True
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

        concerns = profile_data.get('primary_concerns', [])
        if concerns:
            st.markdown("**Focus areas:**")
            for c in concerns:
                st.caption(f"• {c}")

        st.markdown("---")
        if st.button("📞 Help & Resources", use_container_width=True):
            response = buddy._show_resources()
            st.session_state.messages.append({"role": "assistant", "content": response})
        if st.button("⚙️ Manage Profile", use_container_width=True):
            st.session_state.show_profile_menu = True
        st.markdown("---")
        if st.button("🚪 End Session", use_container_width=True):
            response = buddy._end_session()
            st.session_state.messages.append({"role": "assistant", "content": response})
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

    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input
    if prompt := st.chat_input(f"Share how you're feeling, {display_name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = buddy.process_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


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

    with col2:
        st.subheader("Contacts")
        trusted = buddy.user_profile.get_trusted_contacts()
        if trusted:
            st.markdown("**💚 Trusted Contacts:**")
            for c in trusted:
                st.markdown(f"• **{c['name']}** ({c['relationship']})"
                            + (f" — {c['contact_info']}" if c.get('contact_info') else ""))
        else:
            st.info("No trusted contacts added yet.")

        guardians = buddy.user_profile.get_guardian_contacts()
        if guardians:
            st.markdown("**🔔 Guardian Contacts:**")
            for g in guardians:
                st.markdown(f"• **{g['name']}** ({g['relationship']})"
                            + (f" — {g['contact_info']}" if g.get('contact_info') else ""))

    st.markdown("---")
    st.subheader("⚙️ Manage")
    action = st.selectbox("Action:", ["-- Choose --", "Add Trusted Contact",
                                       "Add Guardian Contact", "Delete All My Data"])
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
    elif action == "Delete All My Data":
        st.warning("⚠️ This cannot be undone!")
        if st.button("Confirm Delete"):
            buddy.data_store.delete_user_data(st.session_state.user_id)
            st.session_state.profile_loaded = False
            st.session_state.buddy = None
            st.rerun()


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
