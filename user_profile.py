"""
User profile management for personalized support
"""

from datetime import datetime


class UserProfile:
    """Manages user profile and preferences for personalized support"""
    
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.profile_data = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_session': datetime.now(),
            'gender': None,
            'support_preferences': {},
            'demographics': {},
            'trusted_contacts': [],  # Safe contacts for emergencies
            'unsafe_contacts': [],   # Family/guardians to avoid in toxic situations
            'emotional_history': [],  # Long-term emotional tracking
            'session_count': 0
        }
    
    def load_from_data(self, data):
        """Load profile from saved data"""
        if data:
            self.profile_data = data
            self.user_id = data.get('user_id')
    
    def set_gender(self, gender):
        """Set user gender for specialized support"""
        if gender.lower() in ['female', 'woman', 'f']:
            self.profile_data['gender'] = 'female'
        elif gender.lower() in ['male', 'man', 'm']:
            self.profile_data['gender'] = 'male'
        else:
            self.profile_data['gender'] = 'other'
    
    def set_relationship_status(self, status):
        """Set relationship status"""
        self.profile_data['demographics']['relationship_status'] = status
    
    def set_living_situation(self, situation):
        """Set living situation for safety considerations"""
        self.profile_data['demographics']['living_situation'] = situation
    
    def enable_women_support(self):
        """Enable specialized women's support features"""
        self.profile_data['support_preferences']['women_support_enabled'] = True
    
    def add_trusted_contact(self, name, relationship, contact_info=None):
        """Add a trusted friend or support person"""
        contact = {
            'name': name,
            'relationship': relationship,
            'contact_info': contact_info,
            'added_at': datetime.now()
        }
        self.profile_data['trusted_contacts'].append(contact)
    
    def add_unsafe_contact(self, relationship):
        """Mark family/guardians as unsafe (for toxic situations)"""
        self.profile_data['unsafe_contacts'].append({
            'relationship': relationship,
            'marked_at': datetime.now()
        })
    
    def get_trusted_contacts(self):
        """Get list of trusted contacts"""
        return self.profile_data.get('trusted_contacts', [])
    
    def has_unsafe_family(self):
        """Check if family/guardians are marked unsafe"""
        return len(self.profile_data.get('unsafe_contacts', [])) > 0
    
    def add_emotional_snapshot(self, emotion_data, session_summary):
        """Add daily emotional snapshot to long-term history"""
        snapshot = {
            'date': datetime.now().date().isoformat(),
            'timestamp': datetime.now(),
            'emotion_data': emotion_data,
            'session_summary': session_summary
        }
        self.profile_data['emotional_history'].append(snapshot)
        
        # Keep last 90 days only
        if len(self.profile_data['emotional_history']) > 90:
            self.profile_data['emotional_history'] = self.profile_data['emotional_history'][-90:]
    
    def get_emotional_history(self, days=None):
        """Get emotional history for specified number of days"""
        history = self.profile_data.get('emotional_history', [])
        if days:
            return history[-days:]
        return history
    
    def increment_session_count(self):
        """Increment session counter"""
        self.profile_data['session_count'] = self.profile_data.get('session_count', 0) + 1
    
    def update_last_session(self):
        """Update last session timestamp"""
        self.profile_data['last_session'] = datetime.now()
    
    def get_profile(self):
        """Get user profile data"""
        return self.profile_data
    
    def is_female(self):
        """Check if user identifies as female"""
        return self.profile_data.get('gender') == 'female'
    
    def needs_women_support(self):
        """Check if women's support features should be enabled"""
        return (self.is_female() or 
                self.profile_data.get('support_preferences', {}).get('women_support_enabled', False))
