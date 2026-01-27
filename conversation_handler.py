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
    
    def generate_response(self, emotion_data):
        """Generate appropriate response based on emotional state"""
        emotion = emotion_data['emotion']
        severity = emotion_data['severity']
        
        if emotion == 'positive':
            responses = [
                "I'm so glad to hear you're feeling positive! That's wonderful. 😊",
                "It's great to see you in good spirits! Keep nurturing those positive feelings.",
                "That sounds really encouraging! I'm here to celebrate these moments with you."
            ]
        elif emotion == 'neutral':
            responses = [
                "Thank you for sharing. I'm here to listen. How else are you feeling?",
                "I hear you. Would you like to talk more about what's on your mind?",
                "I'm listening. Feel free to share more if you'd like."
            ]
        elif emotion == 'negative' and severity == 'medium':
            responses = [
                "I can sense you're going through a difficult time. I'm here to support you. 💙",
                "That sounds challenging. Remember, it's okay to feel this way, and I'm here to listen.",
                "Thank you for opening up. Your feelings are valid, and I'm here for you."
            ]
        else:  # distress or high severity
            responses = [
                "I hear that you're really struggling right now. Please know that you don't have to go through this alone. 💙",
                "What you're feeling sounds incredibly difficult. Your wellbeing matters deeply. I'm here with you.",
                "I'm concerned about how you're feeling. These emotions are heavy, but support is available. You matter."
            ]
        
        # Add specific support for abuse indicators
        if emotion_data.get('has_abuse_indicators'):
            responses.append(
                "\nI notice you mentioned something that might indicate a difficult situation. "
                "If you're in an unsafe environment, please know that specialized support is available. "
                "You deserve to be safe and respected."
            )
        
        return random.choice(responses) if responses else "I'm here to listen and support you."
    
    def get_greeting(self):
        """Get a greeting message"""
        return random.choice(config.GREETING_MESSAGES)
