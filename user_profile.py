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
            'created_at': current_time,
            'last_session': current_time,
            'gender': None,
            'support_preferences': {},
            'demographics': {},
            'trusted_contacts': [],  # Safe contacts for emergencies
            'unsafe_contacts': [],   # Family/guardians to avoid in toxic situations
            'emotional_history': [],  # Long-term emotional tracking (now 1 year)
            'trauma_history': [],    # Personal trauma records for sensitive support
            'personal_triggers': [], # Topics/keywords that are especially sensitive
            'response_style': 'balanced',  # 'short', 'detailed', or 'balanced'
            'language_preference': config.DEFAULT_LANGUAGE,  # 'english', 'tamil', 'bilingual'
            'mood_streak': 0,        # Consecutive positive-mood sessions
            'wellness_badges': [],   # Earned wellness badges
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
    
    def set_family_background(self, info):
        """Store family background / situation for context-aware support"""
        self.profile_data['demographics']['family_background'] = info

    def set_family_responsibilities(self, responsibilities):
        """Store the user's family responsibilities (e.g. caretaker, single parent, breadwinner)"""
        self.profile_data['demographics']['family_responsibilities'] = responsibilities

    def get_family_responsibilities(self):
        """Return the user's family responsibilities string"""
        return self.profile_data.get('demographics', {}).get('family_responsibilities')

    def set_occupation(self, occupation):
        """Store the user's occupation / work situation for stress-context-aware support"""
        self.profile_data['demographics']['occupation'] = occupation

    def get_occupation(self):
        """Return the user's occupation string"""
        return self.profile_data.get('demographics', {}).get('occupation')

    def get_living_situation(self):
        """Return the user's living situation string"""
        return self.profile_data.get('demographics', {}).get('living_situation')

    
    def add_trauma_history(self, description, approximate_date=None):
        """Record a past trauma so responses can be more sensitive"""
        entry = {
            'description': description,
            'recorded_at': datetime.now()
        }
        if approximate_date:
            entry['approximate_date'] = approximate_date
        self.profile_data.setdefault('trauma_history', []).append(entry)
    
    def add_personal_trigger(self, trigger):
        """Add a topic or keyword that is especially sensitive for this user"""
        triggers = self.profile_data.setdefault('personal_triggers', [])
        normalized = trigger.strip().lower()
        if normalized and normalized not in triggers:
            triggers.append(normalized)
    
    def get_personal_triggers(self):
        """Return the list of personal trigger words/phrases"""
        return self.profile_data.get('personal_triggers', [])
    
    def get_trauma_history(self):
        """Return the list of recorded trauma entries"""
        return self.profile_data.get('trauma_history', [])
    
    def get_personal_context(self):
        """Return a context dict used to personalize conversation responses"""
        demographics = self.profile_data.get('demographics', {})
        return {
            'gender': self.profile_data.get('gender'),
            'marital_status': demographics.get('relationship_status'),
            'family_background': demographics.get('family_background'),
            'family_responsibilities': demographics.get('family_responsibilities'),
            'occupation': demographics.get('occupation'),
            'living_situation': demographics.get('living_situation'),
            'has_trauma_history': len(self.profile_data.get('trauma_history', [])) > 0,
            'trauma_count': len(self.profile_data.get('trauma_history', [])),
            'personal_triggers': self.profile_data.get('personal_triggers', []),
            'has_unsafe_family': self.has_unsafe_family(),
            'language_preference': self.profile_data.get(
                'language_preference', config.DEFAULT_LANGUAGE
            ),
        }
    
    def set_response_style(self, style):
        """Set preferred response style: 'short', 'detailed', or 'balanced'"""
        if style in ('short', 'detailed', 'balanced'):
            self.profile_data['response_style'] = style

    def get_response_style(self):
        """Get preferred response style (default: 'balanced')"""
        return self.profile_data.get('response_style', 'balanced')

    def set_language_preference(self, language):
        """Set preferred language: 'english', 'tamil', or 'bilingual'."""
        if language in config.SUPPORTED_LANGUAGES:
            self.profile_data['language_preference'] = language

    def get_language_preference(self):
        """Get preferred language (default: 'english')."""
        return self.profile_data.get('language_preference', config.DEFAULT_LANGUAGE)

    # ------------------------------------------------------------------
    # Gamification — mood streak & wellness badges
    # ------------------------------------------------------------------

    # Badge definitions: (id, name, description, condition_key)
    _BADGE_DEFINITIONS = [
        ('first_step',   '🌱 First Step',       'Completed your first session',            'first_session'),
        ('consistent',   '🔄 Consistent',        'Completed 7 or more sessions',            'sessions_7'),
        ('dedicated',    '💪 Dedicated',         'Completed 30 or more sessions',           'sessions_30'),
        ('streak_3',     '🔥 3-Day Streak',       'Three consecutive positive-mood sessions', 'streak_3'),
        ('streak_7',     '⭐ 7-Day Streak',       'Seven consecutive positive-mood sessions', 'streak_7'),
        ('resilient',    '🛡️ Resilient',         'Recovered from distress to positive mood', 'recovered'),
        ('self_aware',   '🧠 Self-Aware',        'Added personal triggers or trauma history', 'self_aware'),
        ('connected',    '💚 Connected',         'Added a trusted contact',                  'has_contact'),
    ]

    def update_mood_streak(self, session_avg_sentiment):
        """
        Update the mood streak based on the session average sentiment.
        Increments streak on positive sessions (avg > 0), resets otherwise.
        Returns the new streak value.
        """
        if session_avg_sentiment > 0:
            self.profile_data['mood_streak'] = self.profile_data.get('mood_streak', 0) + 1
        else:
            self.profile_data['mood_streak'] = 0
        return self.profile_data['mood_streak']

    def get_mood_streak(self):
        """Return current mood streak (consecutive positive sessions)"""
        return self.profile_data.get('mood_streak', 0)

    def award_badge(self, badge_id):
        """Award a badge if not already earned. Returns True if newly awarded."""
        badges = self.profile_data.setdefault('wellness_badges', [])
        if badge_id not in badges:
            badges.append(badge_id)
            return True
        return False

    def get_badges(self):
        """Return list of earned badge IDs"""
        return self.profile_data.get('wellness_badges', [])

    def get_badge_display(self):
        """Return list of (name, description) for earned badges"""
        earned = set(self.get_badges())
        return [
            (name, desc)
            for bid, name, desc, _ in self._BADGE_DEFINITIONS
            if bid in earned
        ]

    def check_and_award_badges(self, session_avg_sentiment=None, recovered_from_distress=False):
        """
        Evaluate all badge conditions and award any newly earned badges.
        Returns a list of newly awarded badge names.
        """
        newly_awarded = []
        session_count = self.profile_data.get('session_count', 0)
        streak = self.profile_data.get('mood_streak', 0)

        conditions = {
            'first_session': session_count >= 1,   # awarded after the first completed session
            'sessions_7':    session_count >= 7,
            'sessions_30':   session_count >= 30,
            'streak_3':      streak >= 3,
            'streak_7':      streak >= 7,
            'recovered':     recovered_from_distress,
            'self_aware':    (len(self.get_trauma_history()) > 0 or
                              len(self.get_personal_triggers()) > 0),
            'has_contact':   len(self.get_trusted_contacts()) > 0,
        }

        for bid, name, desc, cond_key in self._BADGE_DEFINITIONS:
            if conditions.get(cond_key, False):
                if self.award_badge(bid):
                    newly_awarded.append(name)

        return newly_awarded

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
