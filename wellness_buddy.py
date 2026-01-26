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


class WellnessBuddy:
    """Main AI Wellness Buddy application"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.pattern_tracker = PatternTracker()
        self.alert_system = AlertSystem()
        self.conversation_handler = ConversationHandler()
        self.user_profile = UserProfile()
        self.session_active = False
        
    def start_session(self):
        """Start a new wellness buddy session"""
        self.session_active = True
        print("\n" + "="*70)
        print("        🌟 AI EMOTIONAL WELLNESS BUDDY 🌟")
        print("="*70)
        print("\nWelcome! This is a safe, confidential space for emotional support.")
        print("I'm here to listen, support you, and connect you with resources when needed.\n")
        
        # Optional profile setup
        self._setup_profile()
        
        print("\n" + self.conversation_handler.get_greeting())
        print("\n(Type 'quit' to end the session, 'help' for resources)\n")
        
    def _setup_profile(self):
        """Optional profile setup for personalized support"""
        print("To provide better personalized support, I have a few optional questions.")
        print("You can skip any question by pressing Enter.\n")
        
        # Gender identification
        gender = input("How do you identify? (female/male/other/skip): ").strip()
        if gender and gender.lower() not in ['skip', '']:
            self.user_profile.set_gender(gender)
            
            # Additional support for women
            if self.user_profile.is_female():
                print("\nI want you to know that specialized support resources for women")
                print("are available if you ever need them, including safety planning")
                print("and support for domestic situations.\n")
    
    def process_message(self, user_message):
        """Process user message and generate response"""
        # Handle special commands
        if user_message.lower() == 'quit':
            return self._end_session()
        
        if user_message.lower() == 'help':
            return self._show_resources()
        
        if user_message.lower() == 'status':
            return self._show_emotional_status()
        
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
            alert_message = self.alert_system.format_alert_message(alert)
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
        
        message += "\n" + "="*70
        return message
    
    def _show_emotional_status(self):
        """Display current emotional pattern status"""
        summary = self.pattern_tracker.get_pattern_summary()
        
        if not summary:
            return "\nNot enough data yet to show emotional patterns."
        
        message = "\n📊 EMOTIONAL PATTERN SUMMARY 📊\n"
        message += "="*70 + "\n"
        message += f"Messages analyzed: {summary['total_messages']}\n"
        message += f"Emotional trend: {summary['trend'].upper()}\n"
        message += f"Average sentiment: {summary['average_sentiment']:.2f} "
        message += f"({'positive' if summary['average_sentiment'] > 0 else 'negative'})\n"
        
        if summary['abuse_indicators_detected']:
            message += "\n⚠️ Note: Indicators of difficult situations detected.\n"
            message += "Support resources are available - type 'help' to see them.\n"
        
        message += "="*70
        return message
    
    def _end_session(self):
        """End the wellness buddy session"""
        self.session_active = False
        
        message = "\n" + "="*70 + "\n"
        message += "Thank you for sharing with me today. Remember:\n\n"
        message += "💙 Your feelings are valid\n"
        message += "💙 You deserve support and care\n"
        message += "💙 Help is always available\n"
        message += "💙 You are not alone\n\n"
        
        # Show summary if there's enough data
        summary = self.pattern_tracker.get_pattern_summary()
        if summary and summary['total_messages'] >= 3:
            message += f"\nToday's session: {summary['total_messages']} messages, "
            message += f"trend: {summary['trend']}\n"
        
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
