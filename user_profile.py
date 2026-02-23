"""
User profile management for personalized support
"""

from datetime import datetime
import hashlib
import secrets
import config


class UserProfile:
    """Manages user profile and preferences for personalized support"""
    
    def __init__(self, user_id=None):
        self.user_id = user_id
        current_time = datetime.now()  # Calculate once for consistency
        self.profile_data = {
            'user_id': user_id,
            'name': None,            # Display / preferred name
            'age': None,             # Age (integer)
            'occupation': None,      # Job / student status
            'primary_concerns': [],  # Reasons for using the app
            'created_at': current_time,
            'last_session': current_time,
            'gender': None,
            'support_preferences': {},
            'demographics': {},
            'trusted_contacts': [],    # Safe contacts for emergencies
            'guardian_contacts': [],   # Guardian / emergency contacts for alerts
            'unsafe_contacts': [],     # Family/guardians to avoid in toxic situations
            'emotional_history': [],   # Long-term emotional tracking (now 1 year)
            'session_count': 0,
            # Security fields
            'password_hash': None,  # Hashed password for profile protection
            'salt': None,  # Salt for password hashing
            'failed_login_attempts': 0,
            'lockout_until': None,
            'last_activity': current_time,  # Set at creation time
            'security_enabled': config.ENABLE_PROFILE_PASSWORD
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
    
    def set_name(self, name):
        """Set the user's preferred display name"""
        self.profile_data['name'] = name

    def set_age(self, age):
        """Set the user's age"""
        self.profile_data['age'] = age

    def set_occupation(self, occupation):
        """Set the user's occupation or student status"""
        self.profile_data['occupation'] = occupation

    def set_primary_concerns(self, concerns):
        """Set the user's primary concerns or reasons for using the app"""
        self.profile_data['primary_concerns'] = concerns

    def get_display_name(self):
        """Get the best available name to address the user"""
        return self.profile_data.get('name') or self.profile_data.get('user_id') or 'Friend'

    def add_guardian_contact(self, name, relationship, contact_info=None):
        """Add a guardian or emergency contact for distress alerts"""
        contact = {
            'name': name,
            'relationship': relationship,
            'contact_info': contact_info,
            'added_at': datetime.now()
        }
        if 'guardian_contacts' not in self.profile_data:
            self.profile_data['guardian_contacts'] = []
        self.profile_data['guardian_contacts'].append(contact)

    def get_guardian_contacts(self):
        """Get list of guardian / emergency contacts"""
        return self.profile_data.get('guardian_contacts', [])

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
        
        # Keep last year of data (365 days) for extended tracking
        max_snapshots = config.EMOTIONAL_HISTORY_DAYS
        if len(self.profile_data['emotional_history']) > max_snapshots:
            self.profile_data['emotional_history'] = self.profile_data['emotional_history'][-max_snapshots:]
    
    def get_emotional_history(self, days=None):
        """Get emotional history for specified number of days"""
        history = self.profile_data.get('emotional_history', [])
        if days:
            return history[-days:]
        return history
    
    def set_password(self, password):
        """Set password for profile protection"""
        if len(password) < config.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters")
        
        # Generate a random salt
        self.profile_data['salt'] = secrets.token_hex(32)
        
        # Hash the password with the salt using SHA-256
        password_with_salt = password + self.profile_data['salt']
        self.profile_data['password_hash'] = hashlib.sha256(password_with_salt.encode()).hexdigest()
        self.profile_data['security_enabled'] = True
    
    def verify_password(self, password):
        """Verify password for profile access"""
        if not self.profile_data.get('security_enabled'):
            return True  # No password set, allow access
        
        # Check if account is locked out
        if self.is_locked_out():
            return False
        
        if not self.profile_data.get('password_hash') or not self.profile_data.get('salt'):
            return True  # Legacy profile without password
        
        # Hash the provided password with the stored salt
        password_with_salt = password + self.profile_data['salt']
        password_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
        
        # Verify the hash
        if password_hash == self.profile_data['password_hash']:
            # Successful login - reset failed attempts
            self.profile_data['failed_login_attempts'] = 0
            self.profile_data['lockout_until'] = None
            self.update_last_activity()
            return True
        else:
            # Failed login
            self.profile_data['failed_login_attempts'] = self.profile_data.get('failed_login_attempts', 0) + 1
            if self.profile_data['failed_login_attempts'] >= config.MAX_LOGIN_ATTEMPTS:
                # Lock out the account
                from datetime import timedelta
                self.profile_data['lockout_until'] = datetime.now() + timedelta(minutes=config.LOCKOUT_DURATION_MINUTES)
            return False
    
    def is_locked_out(self):
        """Check if account is currently locked out"""
        lockout_until = self.profile_data.get('lockout_until')
        if lockout_until:
            if isinstance(lockout_until, str):
                lockout_until = datetime.fromisoformat(lockout_until)
            if datetime.now() < lockout_until:
                return True
            else:
                # Lockout period expired
                self.profile_data['lockout_until'] = None
                self.profile_data['failed_login_attempts'] = 0
        return False
    
    def update_last_activity(self):
        """Update last activity timestamp for session management"""
        self.profile_data['last_activity'] = datetime.now()
    
    def is_session_expired(self):
        """Check if session has expired due to inactivity"""
        if not config.SESSION_TIMEOUT_MINUTES:
            return False
        
        last_activity = self.profile_data.get('last_activity')
        if not last_activity:
            return False
        
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        
        from datetime import timedelta
        timeout = timedelta(minutes=config.SESSION_TIMEOUT_MINUTES)
        return datetime.now() - last_activity > timeout
    
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
