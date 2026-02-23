"""
Web UI for AI Wellness Buddy using Streamlit
Run with: streamlit run ui_app.py
"""

import streamlit as st
from wellness_buddy import WellnessBuddy
from user_profile import UserProfile
from data_store import DataStore
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="AI Wellness Buddy",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'buddy' not in st.session_state:
    st.session_state.buddy = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'profile_loaded' not in st.session_state:
    st.session_state.profile_loaded = False

def init_buddy():
    """Initialize wellness buddy instance"""
    if st.session_state.buddy is None:
        st.session_state.buddy = WellnessBuddy()
        st.session_state.buddy.data_store = DataStore()

def show_profile_setup():
    """Show profile setup interface"""
    st.title("🌟 AI Wellness Buddy")
    st.markdown("### Welcome! Let's set up your profile")

    # Check for existing profiles
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
    st.markdown("#### 📋 Tell us about yourself")
    st.caption("Fields marked * are required. Everything else is optional but helps us personalise your experience.")

    with st.form("new_profile"):
        # ── Basic identity ──────────────────────────────────────────
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

        # ── Personal details ────────────────────────────────────────
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
                st.warning("🛡️ I understand. Your safety is paramount. "
                           "I will guide you toward trusted friends and women's organisations.")

        st.markdown("---")

        # ── Guardian / Emergency Contact ─────────────────────────────
        st.markdown("**Guardian / Emergency Contact** *(highly recommended)*")
        st.info(
            "🔔 **How the alert system works:** If your Wellness Buddy detects signs of "
            "sustained emotional distress across multiple messages, it will display a "
            "notification here so you know it's time to reach out. If you add a guardian "
            "contact below, that person's details will appear in the alert so you or a "
            "trusted helper can quickly reach them. No message is automatically sent — "
            "you stay in full control at all times."
        )
        guardian_name = st.text_input("Guardian's name:", key="guardian_name",
                                      placeholder="e.g. Mum, Dad, Dr. Smith")
        guardian_relationship = st.text_input("Relationship:", key="guardian_rel",
                                              placeholder="e.g. Parent, Counsellor, Friend")
        guardian_contact = st.text_input("Phone / Email:", key="guardian_contact",
                                         placeholder="e.g. +1-555-0100 or guardian@email.com")

        st.markdown("---")
        submitted = st.form_submit_button("✅ Create My Profile", use_container_width=True)

        if submitted:
            if not username:
                st.error("Please choose a username.")
                return

            # Build profile
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

            if guardian_name and guardian_relationship:
                profile.add_guardian_contact(
                    guardian_name, guardian_relationship,
                    guardian_contact if guardian_contact else None
                )

            st.session_state.buddy.user_profile = profile
            st.session_state.buddy._save_profile()
            st.session_state.profile_loaded = True
            st.success("✓ Profile created successfully! Welcome 🎉")
            st.rerun()

def load_profile(username):
    """Load existing profile"""
    init_buddy()
    st.session_state.user_id = username
    st.session_state.buddy._load_existing_profile(username)
    st.session_state.profile_loaded = True
    st.success(f"✓ Profile loaded: {username}")
    st.rerun()

def show_chat_interface():
    """Show main chat interface"""
    buddy = st.session_state.buddy
    profile_data = buddy.user_profile.get_profile() if buddy.user_profile else {}
    display_name = profile_data.get('name') or st.session_state.user_id or "Friend"

    st.title(f"🌟 Hi, {display_name}!")

    # Sidebar
    with st.sidebar:
        st.markdown(f"**👤 {display_name}**")
        if profile_data.get('occupation'):
            st.caption(profile_data['occupation'])
        if profile_data.get('age'):
            st.caption(f"Age: {profile_data['age']}")

        sessions = profile_data.get('session_count', 0)
        st.markdown(f"**Session:** #{sessions + 1}")

        concerns = profile_data.get('primary_concerns', [])
        if concerns:
            st.markdown("**Focus areas:**")
            for c in concerns:
                st.caption(f"• {c}")

        st.markdown("---")
        st.markdown("### Quick Actions")

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

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(f"Share how you're feeling, {display_name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = buddy.process_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Show profile menu if requested
    if st.session_state.get('show_profile_menu', False):
        show_profile_menu()

def show_profile_menu():
    """Show profile management menu"""
    with st.sidebar:
        st.markdown("### Profile Management")

        trusted = st.session_state.buddy.user_profile.get_trusted_contacts()
        st.write(f"Trusted contacts: {len(trusted)}")

        action = st.selectbox("Choose action:",
                              ["Cancel", "Add Trusted Contact", "View Trusted Contacts",
                               "Add Guardian Contact", "Mark Family Unsafe", "Delete All Data"])

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
                    st.success(f"✓ Added {name} to trusted contacts")
                    st.session_state.show_profile_menu = False

        elif action == "Add Guardian Contact":
            with st.form("add_guardian"):
                g_name = st.text_input("Guardian's name:")
                g_rel = st.text_input("Relationship:")
                g_contact = st.text_input("Phone / Email:")
                if st.form_submit_button("Add Guardian"):
                    if g_name and g_rel:
                        st.session_state.buddy.user_profile.add_guardian_contact(
                            g_name, g_rel, g_contact if g_contact else None
                        )
                        st.session_state.buddy._save_profile()
                        st.success(f"✓ Added {g_name} as guardian contact")
                        st.session_state.show_profile_menu = False
                    else:
                        st.error("Name and relationship are required.")

        elif action == "View Trusted Contacts":
            if trusted:
                st.markdown("**💚 Your Trusted Contacts:**")
                for contact in trusted:
                    st.write(f"• {contact['name']} ({contact['relationship']})")
                    if contact.get('contact_info'):
                        st.write(f"  Contact: {contact['contact_info']}")
            else:
                st.info("No trusted contacts added yet")

            guardians = st.session_state.buddy.user_profile.get_guardian_contacts()
            if guardians:
                st.markdown("**🔔 Your Guardian Contacts:**")
                for contact in guardians:
                    st.write(f"• {contact['name']} ({contact['relationship']})")
                    if contact.get('contact_info'):
                        st.write(f"  Contact: {contact['contact_info']}")

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

def main():
    """Main application"""
    # Custom CSS for a friendlier look
    st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] {
        background-color: #f0f4f8;
    }
    h1 { color: #2c6e9e; }
    h3 { color: #3a7abf; }
    .stAlert { border-radius: 0.5rem; }
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.profile_loaded:
        show_profile_setup()
    else:
        show_chat_interface()

if __name__ == "__main__":
    main()
