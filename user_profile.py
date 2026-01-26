"""
User profile management for personalized support
"""

from datetime import datetime


class UserProfile:
    """Manages user profile and preferences for personalized support"""
    
    def __init__(self):
        self.profile_data = {
            'created_at': datetime.now(),
            'gender': None,
            'support_preferences': {},
            'demographics': {}
        }
    
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
    
    def enable_women_support(self):
        """Enable specialized women's support features"""
        self.profile_data['support_preferences']['women_support_enabled'] = True
    
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
