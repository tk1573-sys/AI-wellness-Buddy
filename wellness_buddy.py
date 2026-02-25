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
from prediction_agent import PredictionAgent
from language_handler import LanguageHandler
import config


class WellnessBuddy:
    """Main AI Wellness Buddy application"""
    
    def __init__(self, data_dir=None):
        self.emotion_analyzer = EmotionAnalyzer()
        self.pattern_tracker = PatternTracker()
        self.alert_system = AlertSystem()
        self.conversation_handler = ConversationHandler()
        self.prediction_agent = PredictionAgent()
        self.lang_handler = LanguageHandler()
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
        
        # Use language-aware greeting
        lang_pref = (self.user_profile.get_language_preference()
                     if self.user_profile else 'english')
        bilingual_greeting = self.lang_handler.get_greeting(lang_pref)
        if bilingual_greeting:
            print("\n" + bilingual_greeting)
        else:
            print("\n" + self.conversation_handler.get_greeting())
        print("\n(Commands: 'quit' to end, 'help' for resources, 'status' for analysis, 'report' for weekly summary, 'profile' to manage profile)\n")
        
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
        
        # Relationship / marital status
        print("\nUnderstanding your life situation helps me support you better.")
        marital = input("What is your relationship/marital status? "
                        "(single/married/divorced/widowed/other/skip): ").strip().lower()
        if marital and marital not in ['skip', '']:
            self.user_profile.set_relationship_status(marital)

        # Living situation
        living = input("What is your current living situation? "
                       "(e.g. alone/with family/with partner/in hostel/other/skip): ").strip()
        if living and living.lower() not in ['skip', '']:
            self.user_profile.set_living_situation(living)

        # Family responsibilities
        family_resp = input("\nDo you have family responsibilities? "
                            "(e.g. caretaker/single parent/breadwinner/none/skip): ").strip()
        if family_resp and family_resp.lower() not in ['skip', '']:
            self.user_profile.set_family_responsibilities(family_resp)

        # Occupation
        occupation = input("\nWhat is your occupation or work situation? "
                           "(e.g. student/employed/unemployed/homemaker/skip): ").strip()
        if occupation and occupation.lower() not in ['skip', '']:
            self.user_profile.set_occupation(occupation)

        # Language preference
        print("\nThis app supports English, Tamil (தமிழ்), and bilingual (Tamil+English).")
        lang_choice = input("Preferred language? (english/tamil/bilingual/skip): ").strip().lower()
        if lang_choice in config.SUPPORTED_LANGUAGES:
            self.user_profile.set_language_preference(lang_choice)
            if lang_choice == 'tamil':
                print("  ✓ நான் தமிழில் பதில் சொல்லுவேன்.")
            elif lang_choice == 'bilingual':
                print("  ✓ I'll respond in both Tamil and English.")

        # Family background
        family_bg = input("\nCan you briefly describe your family situation or background? "
                          "(optional — press Enter to skip): ").strip()
        if family_bg:
            self.user_profile.set_family_background(family_bg)

        # Trauma history
        has_trauma = input("\nHave you experienced significant trauma or loss you'd like me "
                           "to be aware of? (yes/no/skip): ").strip().lower()
        if has_trauma == 'yes':
            print("  (This stays private and helps me support you more sensitively.)")
            trauma_desc = input("  Brief description: ").strip()
            if trauma_desc:
                self.user_profile.add_trauma_history(trauma_desc)
                print("  ✓ I'll keep this in mind and respond with extra care.")

        # Personal triggers
        add_triggers = input("\nAre there topics or words that you find especially distressing? "
                             "(yes/no/skip): ").strip().lower()
        if add_triggers == 'yes':
            print("  Add words or phrases one at a time. Press Enter with no input to finish.")
            while True:
                trigger = input("  Sensitive topic/word (or press Enter to finish): ").strip()
                if not trigger:
                    break
                self.user_profile.add_personal_trigger(trigger)
                print(f"  ✓ I'll be especially gentle around '{trigger}'.")

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
        # Ensure profile is loaded
        if not self.user_profile:
            return "⚠️ Profile not initialized. Please restart the session."
        
        # Handle special commands
        if user_message.lower() == 'quit':
            return self._end_session()
        
        if user_message.lower() == 'help':
            return self._show_resources()
        
        if user_message.lower() == 'status':
            return self._show_emotional_status()

        if user_message.lower() in ('weekly', 'report'):
            return self.generate_weekly_summary()
        
        if user_message.lower() == 'profile':
            return self._manage_profile()
        
        # Analyze emotion
        emotion_data = self.emotion_analyzer.classify_emotion(user_message)
        
        # Track patterns
        self.pattern_tracker.add_emotion_data(emotion_data)
        
        # Add to conversation history
        self.conversation_handler.add_message(user_message, emotion_data)
        
        # Generate response (personalized with user context)
        user_context = self.user_profile.get_personal_context()
        user_context['response_style'] = self.user_profile.get_response_style()

        # Attach pre-distress warning if sentiment is trending downward
        sentiment_hist = list(self.pattern_tracker.sentiment_history)
        pre_distress = self.prediction_agent.get_pre_distress_warning(sentiment_hist)
        if pre_distress:
            user_context['pre_distress_warning'] = pre_distress

        response = self.conversation_handler.generate_response(emotion_data, user_context)
        
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
            message += f"  Risk level: {summary['risk_level'].upper()} (score: {summary['risk_score']:.2f})\n"
            message += f"  Stability index: {summary['stability_index']:.2f} "
            message += f"(volatility: {summary['volatility']:.2f})\n"

            # Emotion distribution
            dist = summary.get('emotion_distribution', {})
            if dist:
                message += "\n  Emotion breakdown:\n"
                for emo, count in sorted(dist.items(), key=lambda x: -x[1]):
                    message += f"    {emo}: {count} message(s)\n"

            if summary['abuse_indicators_detected']:
                message += "\n  ⚠️ Note: Indicators of difficult situations detected.\n"
                message += "  Support resources are available - type 'help' to see them.\n"
            if summary.get('crisis_count', 0) > 0:
                message += "\n  🚨 Crisis indicators detected. Please reach out for support.\n"
        else:
            message += "\nNot enough data yet for current session.\n"

        # Long-term history + prediction
        history = self.user_profile.get_emotional_history(days=7)
        if history:
            message += f"\nLast 7 Days:\n"
            message += f"  Check-ins: {len(history)}\n"
            message += f"  Mood streak: {self.user_profile.get_mood_streak()} positive session(s)\n"

            avg_sentiments = []
            for snapshot in history:
                if snapshot.get('session_summary'):
                    avg_sentiments.append(snapshot['session_summary'].get('average_sentiment', 0))

            if avg_sentiments:
                overall_avg = sum(avg_sentiments) / len(avg_sentiments)
                message += f"  Overall sentiment: {overall_avg:.2f} "
                message += f"({'positive' if overall_avg > 0 else 'negative'})\n"

                # Prediction
                forecast = self.prediction_agent.predict_next_sentiment(avg_sentiments)
                if forecast:
                    message += f"\n📡 Next-Session Forecast ({forecast['confidence']} confidence):\n"
                    message += f"  {forecast['interpretation']}\n"

        # Badges
        badges = self.user_profile.get_badge_display()
        if badges:
            message += "\n🏅 Your Wellness Badges:\n"
            for name, desc in badges:
                message += f"  {name} — {desc}\n"

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
        message += f"Trauma records: {len(self.user_profile.get_trauma_history())}\n"
        message += f"Personal triggers: {len(self.user_profile.get_personal_triggers())}\n"
        
        print(message)
        print("\nOptions:")
        print("1. Add trusted contacts")
        print("2. View trusted contacts")
        print("3. Mark family as unsafe (for toxic situations)")
        print("4. Update personal history (trauma / triggers)")
        print("5. View personal history")
        print("6. Delete my data")
        print("7. Return to conversation")
        
        choice = input("\nChoice (1-7): ").strip()
        
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
            # Add trauma records
            trauma_desc = input("\nAny trauma or loss to record (press Enter to skip): ").strip()
            if trauma_desc:
                self.user_profile.add_trauma_history(trauma_desc)
                print("  ✓ Recorded. I'll respond with extra care.")
            # Add triggers
            print("\nAdd sensitive topics/words (press Enter with no input to finish):")
            while True:
                trigger = input("  Sensitive topic/word: ").strip()
                if not trigger:
                    break
                self.user_profile.add_personal_trigger(trigger)
                print(f"  ✓ I'll be especially gentle around '{trigger}'.")
            self._save_profile()
            return "✓ Personal history updated."
        elif choice == '5':
            msg = "\n📋 YOUR PERSONAL HISTORY\n" + "="*70 + "\n"
            demographics = self.user_profile.get_profile().get('demographics', {})
            msg += f"\nRelationship status    : {demographics.get('relationship_status', 'not set')}\n"
            msg += f"Living situation       : {demographics.get('living_situation', 'not set')}\n"
            msg += f"Family responsibilities: {demographics.get('family_responsibilities', 'not set')}\n"
            msg += f"Occupation             : {demographics.get('occupation', 'not set')}\n"
            msg += f"Family background      : {demographics.get('family_background', 'not set')}\n"
            trauma = self.user_profile.get_trauma_history()
            if trauma:
                msg += "\nTrauma records:\n"
                for t in trauma:
                    msg += f"  • {t['description']}\n"
            else:
                msg += "\nNo trauma records on file.\n"
            triggers = self.user_profile.get_personal_triggers()
            if triggers:
                msg += "\nPersonal triggers:\n"
                for tr in triggers:
                    msg += f"  • {tr}\n"
            else:
                msg += "\nNo personal triggers on file.\n"
            return msg
        elif choice == '6':
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

        # Ensure profile exists before trying to save
        if not self.user_profile:
            message = "\n" + "="*70 + "\n"
            message += "Session ended.\n"
            message += "="*70 + "\n"
            return message

        # Save emotional snapshot to long-term history
        pattern_summary = self.pattern_tracker.get_pattern_summary()
        if pattern_summary and pattern_summary.get('total_messages', 0) > 0:
            emotion_data = {
                'messages_count': pattern_summary['total_messages'],
                'distress_messages': pattern_summary['distress_messages'],
                'abuse_indicators': pattern_summary['abuse_indicators_detected'],
                'risk_level': pattern_summary.get('risk_level', 'low'),
                'stability_index': pattern_summary.get('stability_index', 1.0),
            }
            self.user_profile.add_emotional_snapshot(emotion_data, pattern_summary)

        # Update mood streak
        avg_sentiment = 0.0
        if pattern_summary:
            avg_sentiment = pattern_summary.get('average_sentiment', 0.0)
        self.user_profile.update_mood_streak(avg_sentiment)

        # Check if recovering from distress (compare to last completed session)
        prev_history = self.user_profile.get_emotional_history(days=2)
        recovered = False
        if avg_sentiment > 0 and len(prev_history) >= 1:
            last_snap = prev_history[-1].get('emotion_data', {})
            recovered = last_snap.get('risk_level', 'low') in ('high', 'critical')

        # Increment session count then check/award badges
        self.user_profile.increment_session_count()
        newly_awarded = self.user_profile.check_and_award_badges(
            session_avg_sentiment=avg_sentiment,
            recovered_from_distress=recovered
        )

        # Save profile
        self._save_profile()

        message = "\n" + "="*70 + "\n"
        message += "Thank you for sharing with me today. Remember:\n\n"
        message += "💙 Your feelings are valid\n"
        message += "💙 You deserve support and care\n"
        message += "💙 Help is always available\n"
        message += "💙 You are not alone\n"
        message += "💙 You are in control\n\n"

        # Show session summary
        if pattern_summary and pattern_summary['total_messages'] >= 3:
            message += f"\nToday's session: {pattern_summary['total_messages']} messages, "
            message += f"trend: {pattern_summary['trend']}, "
            message += f"risk: {pattern_summary.get('risk_level', 'low').upper()}\n"

        # Streak info
        streak = self.user_profile.get_mood_streak()
        if streak >= 2:
            message += f"\n🔥 Mood streak: {streak} positive session(s) in a row — great work!\n"

        # Badge notifications
        if newly_awarded:
            message += "\n🏅 New badge(s) earned:\n"
            for badge_name in newly_awarded:
                message += f"  {badge_name}\n"

        message += f"\n✓ Your progress has been saved.\n"
        message += "\nTake care of yourself. I'm here whenever you need support.\n"
        message += "="*70 + "\n"

        return message

    def generate_weekly_summary(self):
        """Generate a weekly emotional wellness summary report."""
        history = self.user_profile.get_emotional_history(days=7)

        report = "\n📋 WEEKLY WELLNESS SUMMARY REPORT\n"
        report += "="*70 + "\n"
        report += f"User: {self.user_id}\n\n"

        if not history:
            report += "No data available for the last 7 days.\n"
            report += "Start checking in daily to build your wellness history!\n"
            report += "="*70 + "\n"
            return report

        # --- Aggregate stats ---
        check_ins = len(history)
        sentiments = []
        risk_levels = []
        emotion_counts = {}
        risk_incidents = 0

        for snap in history:
            ss = snap.get('session_summary', {}) or {}
            avg = ss.get('average_sentiment', None)
            if avg is not None:
                sentiments.append(avg)

            risk_lv = snap.get('emotion_data', {}).get('risk_level', None)
            if risk_lv:
                risk_levels.append(risk_lv)
                if risk_lv in ('high', 'critical'):
                    risk_incidents += 1

            dist = ss.get('emotion_distribution', {})
            for emo, cnt in dist.items():
                emotion_counts[emo] = emotion_counts.get(emo, 0) + cnt

        avg_weekly = sum(sentiments) / len(sentiments) if sentiments else None

        # Mood label
        if avg_weekly is None:
            mood_label = 'unknown'
        elif avg_weekly > 0.3:
            mood_label = '😊 Positive'
        elif avg_weekly > 0:
            mood_label = '🙂 Mildly Positive'
        elif avg_weekly > -0.3:
            mood_label = '😐 Neutral / Mixed'
        else:
            mood_label = '😔 Difficult'

        report += f"📅 Period         : Last 7 days\n"
        report += f"✅ Check-ins       : {check_ins}\n"
        if avg_weekly is not None:
            report += f"📈 Average mood    : {avg_weekly:.2f} — {mood_label}\n"
        else:
            report += f"📈 Average mood    : N/A\n"
        report += f"⚠️  Risk incidents  : {risk_incidents}\n"
        report += f"🔥 Mood streak     : {self.user_profile.get_mood_streak()} positive session(s)\n"

        # Emotion distribution
        if emotion_counts:
            report += "\n🎭 Emotion Distribution:\n"
            total_emo = sum(emotion_counts.values())
            for emo, cnt in sorted(emotion_counts.items(), key=lambda x: -x[1]):
                pct = cnt / total_emo * 100
                report += f"   {emo:<12} {cnt:>3} messages  ({pct:.0f}%)\n"

        # Trend prediction
        if len(sentiments) >= 3:
            forecast = self.prediction_agent.predict_next_sentiment(sentiments)
            if forecast:
                report += f"\n📡 Next-Session Forecast ({forecast['confidence']} confidence):\n"
                report += f"   {forecast['interpretation']}\n"
                report += f"   Predicted sentiment: {forecast['predicted_value']:.2f}\n"

        # Improvement suggestions
        report += "\n💡 Suggestions:\n"
        if avg_weekly is not None and avg_weekly < -0.2:
            report += "   • Consider reaching out to a trusted contact or professional.\n"
            report += "   • Try a short mindfulness or breathing exercise daily.\n"
        elif avg_weekly is not None and avg_weekly < 0:
            report += "   • Light physical activity can help lift mood.\n"
            report += "   • Journaling your thoughts may provide clarity.\n"
        else:
            report += "   • Keep up the positive routines that are working for you.\n"
            report += "   • Celebrate small wins — they add up!\n"

        if risk_incidents > 0:
            report += "   • Professional support is always available — type 'help' to see resources.\n"

        # Badges earned
        badges = self.user_profile.get_badge_display()
        if badges:
            report += "\n🏅 Wellness Badges Earned:\n"
            for name, desc in badges:
                report += f"   {name} — {desc}\n"

        report += "\n" + "="*70 + "\n"
        return report

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
