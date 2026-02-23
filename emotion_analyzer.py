"""
Emotion Analysis Agent — Module 1
Multi-emotion classification using keyword + sentiment fusion.
Compares rule-based and ML-based approaches (research angle).
"""

from textblob import TextBlob
from datetime import datetime
import re


# ── Keyword dictionaries per emotion category ─────────────────────────────────

_SADNESS_KEYWORDS = [
    'sad', 'depressed', 'depression', 'hopeless', 'worthless', 'alone',
    'lonely', 'grief', 'loss', 'crying', 'tears', 'heartbroken', 'miserable',
    'sorrow', 'despair', 'gloomy', 'down', 'unhappy', 'empty', 'numb',
    'hurt', 'pain', 'suffering', 'tired', 'exhausted', 'joyless', 'bleak',
]

_ANXIETY_KEYWORDS = [
    'anxious', 'anxiety', 'worried', 'worry', 'nervous', 'stressed', 'stress',
    'panic', 'panicking', 'scared', 'afraid', 'fear', 'terrified', 'dread',
    'overwhelmed', 'tense', 'uneasy', 'restless', 'racing thoughts',
    "can't sleep", 'insomnia', 'helpless', 'trapped', 'stuck',
]

_ANGER_KEYWORDS = [
    'angry', 'anger', 'furious', 'frustrated', 'frustration', 'irritated',
    'annoyed', 'rage', 'mad', 'livid', 'resentment', 'bitter', 'hate',
    'hostile', 'infuriated', 'disgusted', 'outraged', 'fed up',
]

_JOY_KEYWORDS = [
    'happy', 'happiness', 'joy', 'joyful', 'excited', 'wonderful', 'amazing',
    'great', 'fantastic', 'grateful', 'thankful', 'blessed', 'cheerful',
    'content', 'pleased', 'delighted', 'glad', 'elated', 'optimistic',
    'positive', 'good', 'love', 'peaceful', 'calm', 'relieved',
]

_DISTRESS_KEYWORDS = [
    'hopeless', 'worthless', 'alone', 'helpless', 'trapped', 'stuck',
    'hurt', 'pain', 'suffering', 'abuse', 'abused', 'victim',
    "can't take it", 'give up', 'end it', 'suicide', 'die',
    'useless', 'burden', 'tired of living',
]

_ABUSE_KEYWORDS = [
    'abuse', 'abused', 'abusive', 'controlling', 'manipulative',
    'gaslighting', 'threatened', 'intimidated', 'belittled',
    'humiliated', 'isolated', 'trapped', 'toxic relationship',
    'emotional abuse', 'verbal abuse', 'domestic violence',
]

# Sentiment polarity ranges for each category (rule-based heuristic)
_POLARITY_MAP = [
    ('joy',     lambda p: p > 0.25),
    ('neutral', lambda p: -0.10 <= p <= 0.25),
    ('sadness', lambda p: -0.50 <= p < -0.10),
    ('anxiety', lambda p: -0.50 <= p < -0.10),   # refined by keywords
    ('anger',   lambda p: -0.50 <= p < -0.10),   # refined by keywords
    ('distress', lambda p: p < -0.50),
]


def _count_keywords(text_lower, keyword_list):
    """Return count of matched keywords."""
    return sum(1 for kw in keyword_list if kw in text_lower)


class EmotionAnalyzer:
    """
    Analyzes emotional content in text messages.

    Provides:
      • Multi-label emotion scores (sadness, anxiety, anger, joy, neutral)
      • Dominant emotion classification
      • Severity level (low / medium / high)
      • Distress & abuse keyword detection
    """

    def __init__(self):
        # kept for backward-compat
        self.distress_keywords = _DISTRESS_KEYWORDS
        self.abuse_keywords = _ABUSE_KEYWORDS

    # ── Low-level helpers ─────────────────────────────────────────────────────

    def analyze_sentiment(self, text):
        """TextBlob-based polarity & subjectivity (rule-based baseline)."""
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'timestamp': datetime.now(),
        }

    def detect_distress_keywords(self, text):
        text_lower = text.lower()
        return [kw for kw in _DISTRESS_KEYWORDS if kw in text_lower]

    def detect_abuse_indicators(self, text):
        text_lower = text.lower()
        return [kw for kw in _ABUSE_KEYWORDS if kw in text_lower]

    # ── Multi-emotion scoring ─────────────────────────────────────────────────

    def get_emotion_scores(self, text):
        """
        Return normalised scores [0-1] for each emotion category.

        Combines keyword frequency with TextBlob polarity.
        This is the *rule-based* approach (research comparison baseline).
        """
        text_lower = text.lower()
        polarity, _ = TextBlob(text).sentiment

        raw = {
            'joy':      _count_keywords(text_lower, _JOY_KEYWORDS),
            'sadness':  _count_keywords(text_lower, _SADNESS_KEYWORDS),
            'anxiety':  _count_keywords(text_lower, _ANXIETY_KEYWORDS),
            'anger':    _count_keywords(text_lower, _ANGER_KEYWORDS),
            'neutral':  0,
        }

        # Boost scores using polarity
        if polarity > 0.2:
            raw['joy'] += polarity * 3
        elif polarity < -0.2:
            raw['sadness'] += abs(polarity) * 2
            raw['anxiety'] += abs(polarity) * 1

        # If no emotion keyword found → neutral
        total = sum(raw.values())
        if total == 0:
            raw['neutral'] = 1.0
            return {k: (1.0 if k == 'neutral' else 0.0) for k in raw}

        # Normalise to 0-1 sum=1
        return {k: round(v / total, 4) for k, v in raw.items()}

    # ── Main classifier ───────────────────────────────────────────────────────

    def classify_emotion(self, text):
        """
        Classify emotional state.  Returns a dict that is a strict superset
        of the legacy output (backward-compatible).

        New fields:
          emotion_scores  – normalised per-category scores
          dominant_emotion – most probable emotion category
          severity_score   – float 0-10 distress severity
        """
        sentiment = self.analyze_sentiment(text)
        distress_kws = self.detect_distress_keywords(text)
        abuse_kws = self.detect_abuse_indicators(text)
        emotion_scores = self.get_emotion_scores(text)

        polarity = sentiment['polarity']

        # ── Determine legacy emotion bucket ──────────────────────────────────
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

        if distress_kws:
            if emotion != 'distress':
                emotion = 'negative'
            severity = 'high' if len(distress_kws) > 2 else 'medium'

        # ── Dominant multi-emotion category ──────────────────────────────────
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)

        # ── Numeric severity score (0-10) ─────────────────────────────────────
        base_score = max(0.0, (-polarity + 1) / 2 * 10)   # 0=very positive, 10=very negative
        kw_bonus = min(len(distress_kws) * 0.5 + len(abuse_kws) * 1.0, 3.0)
        severity_score = round(min(base_score + kw_bonus, 10.0), 2)

        return {
            # ── legacy fields (unchanged) ─────────────────────────────────
            'emotion': emotion,
            'severity': severity,
            'polarity': polarity,
            'subjectivity': sentiment['subjectivity'],
            'distress_keywords': distress_kws,
            'abuse_indicators': abuse_kws,
            'has_abuse_indicators': len(abuse_kws) > 0,
            'timestamp': sentiment['timestamp'],
            # ── new fields ────────────────────────────────────────────────
            'emotion_scores': emotion_scores,       # {joy, sadness, anxiety, anger, neutral}
            'dominant_emotion': dominant_emotion,   # e.g. 'anxiety'
            'severity_score': severity_score,       # float 0-10
        }
