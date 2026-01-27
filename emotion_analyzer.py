"""
Emotion analysis module using sentiment analysis and keyword detection
"""

from textblob import TextBlob
from datetime import datetime
import re


class EmotionAnalyzer:
    """Analyzes emotional content in text messages"""
    
    def __init__(self):
        self.distress_keywords = [
            'sad', 'depressed', 'hopeless', 'worthless', 'alone', 'lonely',
            'anxious', 'scared', 'afraid', 'helpless', 'trapped', 'stuck',
            'hurt', 'pain', 'suffering', 'abuse', 'abused', 'victim',
            'can\'t take it', 'give up', 'end it', 'suicide', 'die',
            'worthless', 'useless', 'burden', 'tired of living'
        ]
        
        self.abuse_keywords = [
            'abuse', 'abused', 'abusive', 'controlling', 'manipulative',
            'gaslighting', 'threatened', 'intimidated', 'belittled',
            'humiliated', 'isolated', 'trapped', 'toxic relationship',
            'emotional abuse', 'verbal abuse', 'domestic violence'
        ]
        
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text using TextBlob
        Returns polarity (-1 to 1) and subjectivity (0 to 1)
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'timestamp': datetime.now()
        }
    
    def detect_distress_keywords(self, text):
        """Detect distress-related keywords in text"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.distress_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def detect_abuse_indicators(self, text):
        """Detect potential abuse-related keywords"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.abuse_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def classify_emotion(self, text):
        """
        Classify emotional state based on sentiment and keywords
        Returns emotion category and severity
        """
        sentiment = self.analyze_sentiment(text)
        distress_keywords = self.detect_distress_keywords(text)
        abuse_keywords = self.detect_abuse_indicators(text)
        
        polarity = sentiment['polarity']
        
        # Determine emotion category
        if polarity > 0.3:
            emotion = 'positive'
            severity = 'low'
        elif polarity > -0.1:
            emotion = 'neutral'
            severity = 'low'
        elif polarity > -0.5:
            emotion = 'negative'
            severity = 'medium'
        else:
            emotion = 'distress'
            severity = 'high'
        
        # Adjust based on keywords
        if distress_keywords:
            if emotion != 'distress':
                emotion = 'negative'
            severity = 'high' if len(distress_keywords) > 2 else 'medium'
        
        has_abuse_indicators = len(abuse_keywords) > 0
        
        return {
            'emotion': emotion,
            'severity': severity,
            'polarity': polarity,
            'subjectivity': sentiment['subjectivity'],
            'distress_keywords': distress_keywords,
            'abuse_indicators': abuse_keywords,
            'has_abuse_indicators': has_abuse_indicators,
            'timestamp': sentiment['timestamp']
        }
