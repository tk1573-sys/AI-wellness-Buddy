"""
Pattern tracking module for monitoring emotional trends over time
"""

from datetime import datetime, timedelta
from collections import deque
import config


class PatternTracker:
    """Tracks emotional patterns over time and detects concerning trends"""
    
    def __init__(self, window_size=config.PATTERN_TRACKING_WINDOW):
        self.window_size = window_size
        self.emotion_history = deque(maxlen=window_size)
        self.sentiment_history = deque(maxlen=window_size)
        self.distress_count = 0
        self.consecutive_distress = 0
        
    def add_emotion_data(self, emotion_data):
        """Add new emotion analysis data to tracking history"""
        self.emotion_history.append(emotion_data)
        self.sentiment_history.append(emotion_data['polarity'])
        
        # Track distress patterns
        if emotion_data['emotion'] in ['distress', 'negative'] and emotion_data['severity'] in ['medium', 'high']:
            self.distress_count += 1
            self.consecutive_distress += 1
        else:
            self.consecutive_distress = 0
    
    def get_emotional_trend(self):
        """Calculate overall emotional trend"""
        if len(self.sentiment_history) < 2:
            return 'insufficient_data'
        
        recent_avg = sum(list(self.sentiment_history)[-3:]) / min(3, len(self.sentiment_history))
        
        if recent_avg > 0.2:
            return 'improving'
        elif recent_avg < -0.2:
            return 'declining'
        else:
            return 'stable'
    
    def detect_sustained_distress(self):
        """Check if sustained emotional distress is detected"""
        return self.consecutive_distress >= config.SUSTAINED_DISTRESS_COUNT
    
    def get_pattern_summary(self):
        """Get summary of emotional patterns"""
        if not self.emotion_history:
            return None
        
        total_messages = len(self.emotion_history)
        distress_messages = sum(1 for e in self.emotion_history 
                               if e['emotion'] in ['distress', 'negative'])
        
        abuse_indicators_count = sum(1 for e in self.emotion_history 
                                    if e.get('has_abuse_indicators', False))
        
        avg_sentiment = sum(self.sentiment_history) / len(self.sentiment_history) if self.sentiment_history else 0
        
        return {
            'total_messages': total_messages,
            'distress_messages': distress_messages,
            'distress_ratio': distress_messages / total_messages,
            'abuse_indicators_detected': abuse_indicators_count > 0,
            'abuse_indicators_count': abuse_indicators_count,
            'average_sentiment': avg_sentiment,
            'trend': self.get_emotional_trend(),
            'consecutive_distress': self.consecutive_distress,
            'sustained_distress_detected': self.detect_sustained_distress()
        }
    
    def reset_consecutive_distress(self):
        """Reset consecutive distress counter after alert"""
        self.consecutive_distress = 0
