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
    with st.form("new_profile"):
        username = st.text_input("Choose a username (private):", key="new_username")
        gender = st.selectbox("How do you identify?", 
                             ["Skip", "Female", "Male", "Other"])
        
        marital_status = st.selectbox(
            "Relationship / marital status:",
            ["Skip", "Single", "Married", "Divorced", "Widowed", "In a relationship", "Other"]
        )
        
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
            key="family_bg",
            height=68,
            help="A brief description helps me respond more sensitively to your situation."
        )
        
        trauma_info = st.text_area(
            "Any trauma or significant loss you'd like me to be aware of? (optional):",
            key="trauma_info",
            height=68,
            help="This stays completely private and helps me support you with extra care."
        )
        
        triggers_info = st.text_input(
            "Topics or words that are especially sensitive for you (comma-separated, optional):",
            key="triggers_info",
            help="I will be especially gentle whenever these come up."
        )
        
        submitted = st.form_submit_button("Create Profile")
        
        if submitted and username:
            # Create profile
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
            
            if family_bg.strip():
                st.session_state.buddy.user_profile.set_family_background(family_bg.strip())
            
            if trauma_info.strip():
                st.session_state.buddy.user_profile.add_trauma_history(trauma_info.strip())
            
            if triggers_info.strip():
                for t in triggers_info.split(','):
                    t = t.strip()
                    if t:
                        st.session_state.buddy.user_profile.add_personal_trigger(t)
            
            # Save profile
            st.session_state.buddy._save_profile()
            st.session_state.profile_loaded = True
            st.success("✓ Profile created successfully!")
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
    st.title("🌟 AI Wellness Buddy")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"**User:** {st.session_state.user_id}")
        
        if st.session_state.buddy.user_profile:
            sessions = st.session_state.buddy.user_profile.get_profile().get('session_count', 0)
            st.markdown(f"**Session:** #{sessions + 1}")
        
        st.markdown("---")
        st.markdown("### Commands")
        
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
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Share how you're feeling..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response from buddy
        response = st.session_state.buddy.process_message(prompt)
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
                              "View Personal History", "Add Trauma / Trigger",
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
                    st.success(f"✓ Added {name} to trusted contacts")
                    st.session_state.show_profile_menu = False
        
        elif action == "View Trusted Contacts":
            if trusted:
                st.markdown("**💚 Your Trusted Contacts:**")
                for contact in trusted:
                    st.write(f"• {contact['name']} ({contact['relationship']})")
                    if contact.get('contact_info'):
                        st.write(f"  Contact: {contact['contact_info']}")
            else:
                st.info("No trusted contacts added yet")
        
        elif action == "View Personal History":
            profile = st.session_state.buddy.user_profile
            demographics = profile.get_profile().get('demographics', {})
            st.markdown("**📋 Your Personal History**")
            st.write(f"**Relationship status:** {demographics.get('relationship_status', 'not set')}")
            st.write(f"**Family background:** {demographics.get('family_background', 'not set')}")
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
                trauma_desc = st.text_area(
                    "Trauma or loss to record (optional):",
                    height=68,
                    help="This stays private and helps me respond with extra care."
                )
                trigger_input = st.text_input(
                    "Sensitive topic/word to add (optional):",
                    help="I will be especially gentle whenever this comes up."
                )
                if st.form_submit_button("Save"):
                    if trauma_desc.strip():
                        st.session_state.buddy.user_profile.add_trauma_history(trauma_desc.strip())
                    if trigger_input.strip():
                        st.session_state.buddy.user_profile.add_personal_trigger(trigger_input.strip())
                    st.session_state.buddy._save_profile()
                    st.success("✓ Personal history updated")
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
def main():
    """Main application"""
    # Custom CSS
    st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show appropriate interface
    if not st.session_state.profile_loaded:
        show_profile_setup()
    else:
        show_chat_interface()

if __name__ == "__main__":
    main()
