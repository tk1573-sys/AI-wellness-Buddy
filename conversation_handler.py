"""
Conversation handler for managing emotional support interactions
"""

import random
from datetime import datetime
import config


class ConversationHandler:
    """Manages conversation flow and responses"""
    
    def __init__(self):
        self.conversation_history = []
        
    def add_message(self, user_message, emotion_data):
        """Add a message to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_message': user_message,
            'emotion_data': emotion_data
        })
        
        # Limit history size
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]
    
    def generate_response(self, emotion_data, user_profile=None):
        """Generate appropriate response based on emotional state"""
        emotion = emotion_data['emotion']
        severity = emotion_data['severity']

        # Build a personal address from profile data
        name_str = ""
        occupation_context = ""
        if user_profile:
            display_name = user_profile.get('name') or user_profile.get('user_id', '')
            if display_name:
                name_str = f" {display_name}"
            occupation = user_profile.get('occupation', '')
            if occupation:
                occupation_context = f" as a {occupation}"

        if emotion == 'positive':
            responses = [
                f"I'm so glad to hear you're feeling positive{name_str}! That's wonderful. 😊",
                f"It's great to see you in good spirits{name_str}! Keep nurturing those positive feelings.",
                f"That sounds really encouraging{name_str}! I'm here to celebrate these moments with you.",
                f"You're doing great{name_str}! Positive energy like this is worth holding onto. 🌟"
            ]
        elif emotion == 'neutral':
            responses = [
                f"Thank you for sharing{name_str}. I'm here to listen whenever you're ready.",
                f"I hear you{name_str}. Would you like to talk more about what's on your mind?",
                f"I'm listening{name_str}. Feel free to share more if you'd like — there's no rush.",
                f"It sounds like you're taking things one step at a time{name_str}. How can I support you today?"
            ]
        elif emotion == 'negative' and severity == 'medium':
            responses = [
                f"I can sense you're going through a difficult time{name_str}. I'm here to support you. 💙",
                f"That sounds challenging{name_str}. Remember, it's okay to feel this way, and I'm here to listen.",
                f"Thank you for opening up{name_str}. Your feelings are valid, and I'm here for you.",
                f"I hear how hard things feel right now{name_str}{occupation_context}. You don't have to carry this alone. 💙"
            ]
        else:  # distress or high severity
            responses = [
                f"I hear that you're really struggling right now{name_str}. Please know that you don't have to go through this alone. 💙",
                f"What you're feeling sounds incredibly difficult{name_str}. Your wellbeing matters deeply — I'm here with you.",
                f"I'm concerned about how you're feeling{name_str}. These emotions are heavy, but support is available. You matter so much.",
                f"You reached out, and that takes courage{name_str}. I'm right here. Let's get through this together. 💙"
            ]
        
        # Add specific support for abuse indicators
        if emotion_data.get('has_abuse_indicators'):
            responses.append(
                f"\nI notice you mentioned something that might indicate a difficult situation{name_str}. "
                "If you're in an unsafe environment, please know that specialized support is available. "
                "You deserve to be safe and respected."
            )
        
        return random.choice(responses) if responses else f"I'm here to listen and support you{name_str}."
    
    def get_greeting(self):
        """Get a greeting message"""
        return random.choice(config.GREETING_MESSAGES)
