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
    
    def generate_response(self, emotion_data, user_context=None):
        """Generate a warm, humanoid, personalized response based on
        emotional state and optional user profile context."""
        emotion = emotion_data['emotion']
        severity = emotion_data['severity']

        # Detect whether the latest message touches a known personal trigger
        triggered = False
        if user_context and self.conversation_history:
            last_msg = self.conversation_history[-1]['user_message'].lower()
            for trigger in user_context.get('personal_triggers', []):
                if trigger in last_msg:
                    triggered = True
                    break

        has_trauma = user_context and user_context.get('has_trauma_history', False)
        marital_status = user_context.get('marital_status') if user_context else None
        family_bg = user_context.get('family_background') if user_context else None

        if emotion == 'positive':
            responses = [
                "I'm really glad to hear that! 😊 Moments like these are precious — hold onto this feeling.",
                "That's wonderful to hear! Your happiness genuinely matters to me, and I'm here to celebrate "
                "these moments with you. 💛",
                "It's so good to see you in a positive space today. You deserve every bit of joy that comes "
                "your way! 🌟",
            ]

        elif emotion == 'neutral':
            responses = [
                "Thank you for sharing. I'm fully here with you — there's no rush, take all the time you need.",
                "I hear you. Sometimes 'just okay' is a completely valid place to be. "
                "Would you like to explore what's on your mind?",
                "I appreciate you checking in. I'm listening, and we can go wherever feels right for you.",
            ]

        elif emotion == 'negative' and severity == 'medium':
            responses = [
                "I can hear that things feel heavy right now. Your feelings are completely valid, "
                "and you don't have to carry this alone. 💙",
                "That sounds genuinely difficult. It takes real courage to acknowledge how you're feeling, "
                "and I'm right here with you.",
                "Thank you for trusting me with this. Whatever you're going through, you matter deeply, "
                "and support is here for you. 💙",
            ]
            if has_trauma:
                responses.append(
                    "I hear you, and given what you've already been through, it makes complete sense that "
                    "this feels heavy. You've shown real strength before, and I'm right here with you now. 💙"
                )
            if marital_status in ('divorced', 'widowed', 'separated'):
                responses.append(
                    "I know life transitions like the one you've been through can make hard days feel even "
                    "harder. Your feelings are understandable, and I'm here to listen without judgment. 💙"
                )

        else:  # distress or high severity
            responses = [
                "I hear you, and I want you to know you are not alone in this moment. "
                "Your pain is real and it matters deeply. 💙",
                "This sounds incredibly difficult, and I'm so glad you reached out. "
                "You deserve care and support right now — I'm here with you, every step of the way.",
                "I'm genuinely concerned about how you're feeling, and I care about you deeply. "
                "You don't have to face this alone; help and support are always here for you. 💙",
            ]
            if has_trauma:
                responses.append(
                    "I can hear how much pain you're in right now, and I want you to know that your past "
                    "experiences don't define your worth. You have survived hard things before, and you are "
                    "not alone in this moment. 💙"
                )
            if family_bg:
                responses.append(
                    "Given everything that has shaped your life, what you're feeling makes complete sense. "
                    "Please know that you are seen, heard, and supported — you do not have to face this alone. 💙"
                )

        response = random.choice(responses)

        # Gently acknowledge if a personal trigger was mentioned
        if triggered:
            response += (
                "\n\nI noticed you touched on something that may feel especially sensitive for you. "
                "It's completely okay to go at your own pace — I'm here with you, no matter what."
            )

        # Add specific support for abuse indicators
        if emotion_data.get('has_abuse_indicators'):
            response += (
                "\n\nI want you to know that what you are experiencing is not your fault. "
                "You deserve to feel safe and respected. Specialised support is available whenever you are ready — "
                "please type 'help' to see resources, or just keep talking to me. 💙"
            )

        return response
    
    def get_greeting(self):
        """Get a greeting message"""
        return random.choice(config.GREETING_MESSAGES)
