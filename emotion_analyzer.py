"""
Emotion analysis module using sentiment analysis and keyword detection.
Supports multi-emotion classification (joy, sadness, anger, fear, anxiety, neutral, crisis)
with XAI-style keyword attribution.
"""

from textblob import TextBlob
from datetime import datetime
import re
from language_handler import (
    TANGLISH_EMOTION_KEYWORDS,
    TAMIL_UNICODE_EMOTION_KEYWORDS,
    LanguageHandler,
)


class EmotionAnalyzer:
    """Analyzes emotional content in text messages"""

    def __init__(self):
        # --- Legacy coarse keywords (backward-compat) ---
        self.distress_keywords = [
            'sad', 'depressed', 'hopeless', 'worthless', 'alone', 'lonely',
            'anxious', 'scared', 'afraid', 'helpless', 'trapped', 'stuck',
            'hurt', 'pain', 'suffering', 'abuse', 'abused', 'victim',
            "can't take it", 'give up', 'end it', 'suicide', 'die',
            'useless', 'burden', 'tired of living',
            # Tanglish distress
            'kedachu', 'kedaitu', 'kastam', 'kashtam', 'vali', 'valikudu',
        ]

        self.abuse_keywords = [
            'abuse', 'abused', 'abusive', 'controlling', 'manipulative',
            'gaslighting', 'threatened', 'intimidated', 'belittled',
            'humiliated', 'isolated', 'trapped', 'toxic relationship',
            'emotional abuse', 'verbal abuse', 'domestic violence',
        ]

        # --- Crisis / self-harm keywords (immediate escalation) ---
        self.crisis_keywords = [
            'suicide', 'suicidal', 'kill myself', 'end my life', 'want to die',
            'self-harm', 'self harm', 'cut myself', 'hurt myself',
            'no reason to live', 'better off dead', 'tired of living',
            'end it all', 'take my own life', 'overdose', 'not worth living',
            # Tanglish crisis keywords
            'saaga poiren', 'saaganum', 'saagavendum',
            'vazhka venam', 'uyir thola poiren', 'suicide pannuven',
            # Tamil Unicode crisis keywords
            'சாகப்போகிறேன்', 'வாழ்க்கை வேண்டாம்', 'தற்கொலை',
        ]

        # --- Fine-grained multi-emotion keyword dictionaries ---
        self.emotion_keywords = {
            'joy': [
                'happy', 'joyful', 'excited', 'wonderful', 'amazing', 'love',
                'great', 'fantastic', 'thrilled', 'delighted', 'cheerful',
                'grateful', 'blessed', 'elated', 'euphoric', 'content',
                'pleased', 'glad', 'overjoyed', 'celebrate', 'proud',
                # Tanglish joy
                *TANGLISH_EMOTION_KEYWORDS.get('joy', []),
                # Tamil Unicode joy
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('joy', []),
            ],
            'sadness': [
                'sad', 'depressed', 'sorrowful', 'miserable', 'grief', 'cry',
                'crying', 'tears', 'heartbroken', 'devastated', 'melancholy',
                'gloomy', 'despair', 'hopeless', 'lonely', 'alone',
                'mourning', 'loss', 'empty', 'numb', 'broken',
                # Tanglish sadness
                *TANGLISH_EMOTION_KEYWORDS.get('sadness', []),
                # Tamil Unicode sadness
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('sadness', []),
            ],
            'anger': [
                'angry', 'furious', 'annoyed', 'frustrated', 'rage', 'mad',
                'hate', 'resentful', 'irritated', 'outraged', 'livid',
                'bitter', 'hostile', 'agitated', 'enraged', 'infuriated',
                # Tanglish anger
                *TANGLISH_EMOTION_KEYWORDS.get('anger', []),
                # Tamil Unicode anger
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('anger', []),
            ],
            'fear': [
                'scared', 'afraid', 'terrified', 'dread', 'frightened',
                'phobia', 'horror', 'panic', 'timid', 'petrified',
                'shaking', 'trembling', 'fearful', 'dreading',
                # Tanglish fear
                *TANGLISH_EMOTION_KEYWORDS.get('fear', []),
                # Tamil Unicode fear
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('fear', []),
            ],
            'anxiety': [
                'anxious', 'stressed', 'overwhelmed', 'tense', 'uneasy',
                'worried', 'worry', 'apprehensive', 'restless', 'nervous',
                'on edge', 'can\'t sleep', 'racing thoughts', 'tight chest',
                'pit in my stomach', 'catastrophe', 'what if', 'uncertain',
                # Tanglish anxiety
                *TANGLISH_EMOTION_KEYWORDS.get('anxiety', []),
                # Tamil Unicode anxiety
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('anxiety', []),
            ],
        }

        # Weights for computing emotion scores (higher = more severe)
        self.emotion_severity_weights = {
            'crisis':   1.00,
            'sadness':  0.65,
            'fear':     0.60,
            'anxiety':  0.55,
            'anger':    0.45,
            'joy':      0.00,
            'neutral':  0.10,
        }

        # Language handler for script detection
        self._lang_handler = LanguageHandler()

    # ------------------------------------------------------------------
    # Sentiment analysis (TextBlob)
    # ------------------------------------------------------------------

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text using TextBlob.
        Returns polarity (-1 to 1) and subjectivity (0 to 1).
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'timestamp': datetime.now()
        }

    # ------------------------------------------------------------------
    # Legacy keyword detectors (kept for backward compatibility)
    # ------------------------------------------------------------------

    def detect_distress_keywords(self, text):
        """Detect distress-related keywords in text"""
        text_lower = text.lower()
        return [kw for kw in self.distress_keywords if kw in text_lower]

    def detect_abuse_indicators(self, text):
        """Detect potential abuse-related keywords"""
        text_lower = text.lower()
        return [kw for kw in self.abuse_keywords if kw in text_lower]

    def detect_crisis_indicators(self, text):
        """Detect crisis / self-harm keywords requiring immediate escalation"""
        text_lower = text.lower()
        return [kw for kw in self.crisis_keywords if kw in text_lower]

    # ------------------------------------------------------------------
    # Multi-emotion detection
    # ------------------------------------------------------------------

    def detect_emotion_scores(self, text):
        """
        Score each fine-grained emotion by keyword matches.
        Returns a dict mapping emotion name → match count.
        """
        text_lower = text.lower()
        scores = {emo: 0 for emo in self.emotion_keywords}
        for emo, keywords in self.emotion_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[emo] += 1
        return scores

    def detect_primary_emotion(self, text, polarity):
        """
        Determine the primary fine-grained emotion label.
        Falls back to polarity-based classification when no keywords match.
        """
        text_lower = text.lower()

        # Crisis always wins
        if any(kw in text_lower for kw in self.crisis_keywords):
            return 'crisis'

        scores = self.detect_emotion_scores(text)
        max_score = max(scores.values())
        if max_score > 0:
            # Pick the highest-scoring emotion; break ties by severity weight
            candidates = [e for e, s in scores.items() if s == max_score]
            return max(candidates,
                       key=lambda e: self.emotion_severity_weights.get(e, 0))

        # Fallback: polarity-based
        if polarity > 0.2:
            return 'joy'
        elif polarity > -0.1:
            return 'neutral'
        elif polarity > -0.4:
            return 'sadness'
        else:
            return 'sadness'

    # ------------------------------------------------------------------
    # XAI attribution
    # ------------------------------------------------------------------

    def explain_emotion(self, text, primary_emotion):
        """
        Return a human-readable explanation of which keywords drove the
        emotion classification (lightweight XAI / keyword attribution).
        """
        text_lower = text.lower()
        matched = []
        if primary_emotion == 'crisis':
            matched = [kw for kw in self.crisis_keywords if kw in text_lower]
        else:
            keywords = self.emotion_keywords.get(primary_emotion, [])
            matched = [kw for kw in keywords if kw in text_lower]

        if matched:
            return f"Detected '{primary_emotion}' due to keywords: {', '.join(matched[:5])}"
        return f"Detected '{primary_emotion}' based on overall sentiment."

    # ------------------------------------------------------------------
    # Main classification entry point
    # ------------------------------------------------------------------

    def classify_emotion(self, text):
        """
        Classify emotional state based on sentiment and keywords.
        Handles English, Tamil Unicode, and Tanglish input.
        Returns a dict with both coarse (backward-compat) and fine-grained
        emotion data, plus XAI explanation and crisis flag.
        """
        sentiment = self.analyze_sentiment(text)
        distress_keywords = self.detect_distress_keywords(text)
        abuse_keywords = self.detect_abuse_indicators(text)
        crisis_keywords_found = self.detect_crisis_indicators(text)

        polarity = sentiment['polarity']

        # --- Script detection for Tamil / Tanglish ---
        detected_script = self._lang_handler.detect_script(text)

        # Override primary emotion with Tamil/Tanglish if detected
        tanglish_emotion = None
        if detected_script == 'tanglish':
            tanglish_emotion = self._lang_handler.detect_tanglish_emotion(text)
        elif detected_script == 'tamil':
            tanglish_emotion = self._lang_handler.detect_tamil_unicode_emotion(text)

        # --- Coarse emotion (backward-compatible) ---
        if crisis_keywords_found:
            emotion = 'distress'
            severity = 'high'
        elif polarity > 0.3:
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

        # Adjust based on legacy distress keywords
        if distress_keywords:
            if emotion not in ('distress',):
                emotion = 'negative'
            severity = 'high' if len(distress_keywords) > 2 else 'medium'

        # --- Fine-grained emotion ---
        primary_emotion = self.detect_primary_emotion(text, polarity)

        # Tamil/Tanglish override: if a specific emotion was found, use it
        if tanglish_emotion:
            primary_emotion = tanglish_emotion

        emotion_scores = self.detect_emotion_scores(text)
        explanation = self.explain_emotion(text, primary_emotion)

        has_abuse_indicators = len(abuse_keywords) > 0
        is_crisis = len(crisis_keywords_found) > 0

        return {
            # Coarse fields (backward-compatible)
            'emotion': emotion,
            'severity': severity,
            'polarity': polarity,
            'subjectivity': sentiment['subjectivity'],
            'distress_keywords': distress_keywords,
            'abuse_indicators': abuse_keywords,
            'has_abuse_indicators': has_abuse_indicators,
            'timestamp': sentiment['timestamp'],
            # Fine-grained fields (new)
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'explanation': explanation,
            'is_crisis': is_crisis,
            'crisis_keywords': crisis_keywords_found,
            # Language / script metadata
            'detected_script': detected_script,
        }
