"""
AI-based Emotional Wellness Buddy
Main application that integrates all components for emotional support
"""

import sys
from emotion_analyzer import EmotionAnalyzer
from pattern_tracker import PatternTracker
from alert_system import AlertSystem
from conversation_handler import ConversationHandler
from user_profile import UserProfile
from data_store import DataStore


class WellnessBuddy:
    """Main AI Wellness Buddy application"""
    
    def __init__(self, data_dir=None):
        self.emotion_analyzer = EmotionAnalyzer()
        self.pattern_tracker = PatternTracker()
        self.alert_system = AlertSystem()
        self.conversation_handler = ConversationHandler()
        self.user_profile = None
        self.data_store = DataStore(data_dir)
        self.session_active = False
        self.user_id = None
        
    def start_session(self):
        """Start a new wellness buddy session"""
        self.session_active = True
        print("\n" + "="*70)
        print("        🌟 AI EMOTIONAL WELLNESS BUDDY 🌟")
        print("="*70)
        print("\nWelcome! This is a safe, confidential space for emotional support.")
        print("I'm here to listen, support you, and connect you with resources when needed.\n")
        
        # Load or create user profile
        self._load_or_create_profile()
        
        print("\n" + self.conversation_handler.get_greeting())
        print("\n(Commands: 'quit' to end, 'help' for resources, 'profile' to manage profile)\n")
        
    def _load_or_create_profile(self):
        """Load existing profile or create new one"""
        print("=" * 70)
        print("USER PROFILE")
        print("=" * 70)
        
        # Check for existing users
        existing_users = self.data_store.list_users()
        
        if existing_users:
            print(f"\nFound {len(existing_users)} existing profile(s).")
            choice = input("Enter your username to continue, or 'new' for new profile: ").strip()
            
            if choice.lower() == 'new':
                self._create_new_profile()
            elif choice in existing_users:
                self._load_existing_profile(choice)
            else:
                print(f"\nProfile '{choice}' not found. Creating new profile.")
                self.user_id = choice
                self._create_new_profile()
        else:
            print("\nNo existing profiles found. Let's create one!")
            self._create_new_profile()
        
        # Show returning user info
        if self.user_profile.get_profile().get('session_count', 0) > 0:
            sessions = self.user_profile.get_profile()['session_count']
            print(f"\n💙 Welcome back! This is your session #{sessions + 1}.")
            
            # Show emotional history summary
            history = self.user_profile.get_emotional_history(days=7)
            if history:
                print(f"📊 You've checked in {len(history)} time(s) in the last 7 days.")
    
    def _create_new_profile(self):
        """Create a new user profile"""
        if not self.user_id:
            self.user_id = input("\nChoose a username (private, for your eyes only): ").strip()
        
        self.user_profile = UserProfile(self.user_id)
        
        print("\nTo provide better personalized support, I have a few optional questions.")
        print("You can skip any question by pressing Enter.\n")
        
        # Gender identification
        gender = input("How do you identify? (female/male/other/skip): ").strip()
        if gender and gender.lower() not in ['skip', '']:
            self.user_profile.set_gender(gender)
            
            # Additional support for women
            if self.user_profile.is_female():
                print("\n💙 Specialized support resources for women are available.")
                
                # Ask about safety in family/home
                safety = input("\nDo you feel safe with your family/guardians? (yes/no/skip): ").strip().lower()
                if safety == 'no':
                    print("\n🛡️ I understand. Your safety is paramount.")
                    print("I will guide you toward trusted friends and women's organizations,")
                    print("not family members, when suggesting support resources.")
                    
                    # Mark family as unsafe
                    self.user_profile.add_unsafe_contact('family/guardians')
                    
                    # Offer to add trusted contacts
                    add_trusted = input("\nWould you like to add trusted friends now? (yes/no): ").strip().lower()
                    if add_trusted == 'yes':
                        self._add_trusted_contacts()
        
        # Save the new profile
        self._save_profile()
        print("\n✓ Profile created and saved securely.\n")
    
    def _load_existing_profile(self, user_id):
        """Load an existing user profile"""
        self.user_id = user_id
        data = self.data_store.load_user_data(user_id)
        
        if data:
            self.user_profile = UserProfile(user_id)
            self.user_profile.load_from_data(data)
            print(f"\n✓ Profile loaded for: {user_id}")
        else:
            print(f"\n⚠️ Could not load profile. Creating new one.")
            self._create_new_profile()
    
    def _add_trusted_contacts(self):
        """Add trusted contacts to user profile"""
        print("\n💚 Add people you trust (friends, not family if unsafe):\n")
        
        while True:
            name = input("Name (or press Enter to finish): ").strip()
            if not name:
                break
            
            relationship = input(f"Relationship with {name} (e.g., friend, colleague): ").strip()
            contact_info = input(f"Contact info (optional, for your reference): ").strip()
            
            self.user_profile.add_trusted_contact(
                name, 
                relationship, 
                contact_info if contact_info else None
            )
            print(f"✓ Added {name} to your trusted contacts.\n")
    
    def _save_profile(self):
        """Save user profile to persistent storage"""
        if self.user_profile and self.user_id:
            self.user_profile.update_last_session()
            self.data_store.save_user_data(self.user_id, self.user_profile.get_profile())
    
    def process_message(self, user_message):
        """Process user message and generate response"""
        # Handle special commands
        if user_message.lower() == 'quit':
            return self._end_session()
        
        if user_message.lower() == 'help':
            return self._show_resources()
        
        if user_message.lower() == 'status':
            return self._show_emotional_status()
        
        if user_message.lower() == 'profile':
            return self._manage_profile()
        
        # Analyze emotion
        emotion_data = self.emotion_analyzer.classify_emotion(user_message)
        
        # Track patterns
        self.pattern_tracker.add_emotion_data(emotion_data)
        
        # Add to conversation history
        self.conversation_handler.add_message(user_message, emotion_data)
        
        # Generate response
        response = self.conversation_handler.generate_response(emotion_data)
        
        # Check for distress alerts
        pattern_summary = self.pattern_tracker.get_pattern_summary()
        if self.alert_system.should_trigger_alert(pattern_summary):
            alert = self.alert_system.trigger_distress_alert(
                pattern_summary, 
                self.user_profile.get_profile()
            )
            
            # Pass trusted contacts to alert formatter
            trusted_contacts = self.user_profile.get_trusted_contacts()
            alert_message = self.alert_system.format_alert_message(alert, trusted_contacts)
            response += "\n\n" + alert_message
            
            # Reset counter after alert
            self.pattern_tracker.reset_consecutive_distress()
        
        return response
    
    def _show_resources(self):
        """Display support resources"""
        import config
        
        message = "\n📞 SUPPORT RESOURCES 📞\n"
        message += "="*70 + "\n\n"
        message += "General Support:\n"
        for key, value in config.GENERAL_SUPPORT_RESOURCES.items():
            message += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        if self.user_profile.is_female():
            message += "\n🛡️ Specialized Resources for Women:\n"
            for key, value in config.WOMEN_SUPPORT_RESOURCES.items():
                message += f"  • {key.replace('_', ' ').title()}: {value}\n"
            
            # Show trusted support if family is unsafe
            if self.user_profile.has_unsafe_family():
                message += "\n\n🤝 Trusted Support Network (Non-Family):\n"
                for org in config.TRUSTED_SUPPORT_RESOURCES['women_organizations']:
                    message += f"  • {org}\n"
        
        # Show user's trusted contacts
        trusted = self.user_profile.get_trusted_contacts()
        if trusted:
            message += "\n\n💚 Your Trusted Contacts:\n"
            for contact in trusted:
                message += f"  • {contact['name']} ({contact['relationship']})\n"
                if contact.get('contact_info'):
                    message += f"    Contact: {contact['contact_info']}\n"
        
        message += "\n" + "="*70
        return message
    
    def _show_emotional_status(self):
        """Display current emotional pattern status"""
        summary = self.pattern_tracker.get_pattern_summary()
        
        message = "\n📊 EMOTIONAL PATTERN SUMMARY 📊\n"
        message += "="*70 + "\n"
        
        # Current session
        if summary:
            message += "\nCurrent Session:\n"
            message += f"  Messages analyzed: {summary['total_messages']}\n"
            message += f"  Emotional trend: {summary['trend'].upper()}\n"
            message += f"  Average sentiment: {summary['average_sentiment']:.2f} "
            message += f"({'positive' if summary['average_sentiment'] > 0 else 'negative'})\n"
            
            if summary['abuse_indicators_detected']:
                message += "\n  ⚠️ Note: Indicators of difficult situations detected.\n"
                message += "  Support resources are available - type 'help' to see them.\n"
        else:
            message += "\nNot enough data yet for current session.\n"
        
        # Long-term history
        history = self.user_profile.get_emotional_history(days=7)
        if history:
            message += f"\nLast 7 Days:\n"
            message += f"  Check-ins: {len(history)}\n"
            
            # Calculate average sentiment over time
            avg_sentiments = []
            for snapshot in history:
                if snapshot.get('session_summary'):
                    avg_sentiments.append(snapshot['session_summary'].get('average_sentiment', 0))
            
            if avg_sentiments:
                overall_avg = sum(avg_sentiments) / len(avg_sentiments)
                message += f"  Overall sentiment: {overall_avg:.2f} "
                message += f"({'positive' if overall_avg > 0 else 'negative'})\n"
        
        message += "="*70
        return message
    
    def _manage_profile(self):
        """Manage user profile settings"""
        message = "\n⚙️ PROFILE MANAGEMENT ⚙️\n"
        message += "="*70 + "\n"
        message += f"\nUsername: {self.user_id}\n"
        message += f"Total sessions: {self.user_profile.get_profile().get('session_count', 0) + 1}\n"
        
        trusted = self.user_profile.get_trusted_contacts()
        message += f"Trusted contacts: {len(trusted)}\n"
        
        print(message)
        print("\nOptions:")
        print("1. Add trusted contacts")
        print("2. View trusted contacts")
        print("3. Mark family as unsafe (for toxic situations)")
        print("4. Delete my data")
        print("5. Return to conversation")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == '1':
            self._add_trusted_contacts()
            self._save_profile()
            return "✓ Trusted contacts updated."
        elif choice == '2':
            if trusted:
                msg = "\n💚 Your Trusted Contacts:\n"
                for contact in trusted:
                    msg += f"  • {contact['name']} ({contact['relationship']})\n"
                    if contact.get('contact_info'):
                        msg += f"    Contact: {contact['contact_info']}\n"
                return msg
            else:
                return "No trusted contacts added yet."
        elif choice == '3':
            self.user_profile.add_unsafe_contact('family/guardians')
            self._save_profile()
            return "✓ Noted. I will avoid suggesting family contacts in crisis situations."
        elif choice == '4':
            confirm = input("\n⚠️ Delete all your data? This cannot be undone. (yes/no): ").strip().lower()
            if confirm == 'yes':
                self.data_store.delete_user_data(self.user_id)
                return "Your data has been deleted. Session will end."
            else:
                return "Data deletion cancelled."
        else:
            return "Returning to conversation..."
    
    def _end_session(self):
        """End the wellness buddy session"""
        self.session_active = False
        
        # Save emotional snapshot to long-term history
        pattern_summary = self.pattern_tracker.get_pattern_summary()
        if pattern_summary and pattern_summary.get('total_messages', 0) > 0:
            emotion_data = {
                'messages_count': pattern_summary['total_messages'],
                'distress_messages': pattern_summary['distress_messages'],
                'abuse_indicators': pattern_summary['abuse_indicators_detected']
            }
            self.user_profile.add_emotional_snapshot(emotion_data, pattern_summary)
        
        # Increment session count
        self.user_profile.increment_session_count()
        
        # Save profile
        self._save_profile()
        
        message = "\n" + "="*70 + "\n"
        message += "Thank you for sharing with me today. Remember:\n\n"
        message += "💙 Your feelings are valid\n"
        message += "💙 You deserve support and care\n"
        message += "💙 Help is always available\n"
        message += "💙 You are not alone\n"
        message += "💙 You are in control\n\n"
        
        # Show summary if there's enough data
        if pattern_summary and pattern_summary['total_messages'] >= 3:
            message += f"\nToday's session: {pattern_summary['total_messages']} messages, "
            message += f"trend: {pattern_summary['trend']}\n"
        
        message += f"\n✓ Your progress has been saved.\n"
        message += "\nTake care of yourself. I'm here whenever you need support.\n"
        message += "="*70 + "\n"
        
        return message
    
    def run(self):
        """Run the interactive wellness buddy session"""
        self.start_session()
        
        while self.session_active:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                response = self.process_message(user_input)
                print(f"\nWellness Buddy: {response}")
                
            except KeyboardInterrupt:
                print("\n")
                response = self._end_session()
                print(response)
                break
            except Exception as e:
                print(f"\n⚠️ An error occurred: {e}")
                print("Please try again or type 'quit' to end the session.\n")


def main():
    """Main entry point"""
    try:
        buddy = WellnessBuddy()
        buddy.run()
    except Exception as e:
        print(f"\n❌ Error starting Wellness Buddy: {e}")
        print("Please make sure all dependencies are installed:")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
