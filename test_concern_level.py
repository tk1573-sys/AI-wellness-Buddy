"""
Tests for concern level classification, confidence-based empathy amplification,
and UI emotion metadata exposure.

Run with: python -m pytest test_concern_level.py -v
"""

from emotion_analyzer import EmotionAnalyzer
from conversation_handler import ConversationHandler
from wellness_buddy import WellnessBuddy
from user_profile import UserProfile


# ─────────────────────────────────────────────────────────────────────────────
# EmotionAnalyzer — concern_level field
# ─────────────────────────────────────────────────────────────────────────────

class TestConcernLevelClassification:
    """Verify the _compute_concern_level logic and classify_emotion output."""

    def setup_method(self):
        self.analyzer = EmotionAnalyzer()

    def test_crisis_returns_critical(self):
        result = self.analyzer.classify_emotion("I want to kill myself")
        assert result['concern_level'] == 'critical'
        assert result['is_crisis'] is True

    def test_high_sadness_returns_high(self):
        result = self.analyzer.classify_emotion(
            "I feel sad and depressed and hopeless and devastated and heartbroken"
        )
        assert result['concern_level'] in ('high', 'critical')

    def test_positive_message_returns_low(self):
        result = self.analyzer.classify_emotion("I am so happy and joyful today!")
        assert result['concern_level'] == 'low'

    def test_neutral_message_returns_low(self):
        result = self.analyzer.classify_emotion("I'm okay, nothing special happening.")
        assert result['concern_level'] == 'low'

    def test_moderate_anxiety_returns_medium(self):
        result = self.analyzer.classify_emotion(
            "I feel a bit nervous and anxious about the upcoming exam"
        )
        assert result['concern_level'] in ('medium', 'high', 'critical')

    def test_concern_level_always_present(self):
        for text in ["hello", "I'm sad", "I am excited!", "feeling anxious"]:
            result = self.analyzer.classify_emotion(text)
            assert 'concern_level' in result
            assert result['concern_level'] in ('low', 'medium', 'high', 'critical')

    def test_emotion_confidence_always_present(self):
        result = self.analyzer.classify_emotion("I feel very sad")
        assert 'emotion_confidence' in result
        assert isinstance(result['emotion_confidence'], float)
        assert 0.0 <= result['emotion_confidence'] <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Static method test
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeConcernLevelStatic:
    """Direct tests on the static _compute_concern_level method."""

    def test_crisis_always_critical(self):
        level = EmotionAnalyzer._compute_concern_level(
            'crisis', {'crisis': 0.9}, True, ['suicide'], 'high'
        )
        assert level == 'critical'

    def test_high_sadness_prob_with_distress(self):
        level = EmotionAnalyzer._compute_concern_level(
            'sadness', {'sadness': 0.7, 'neutral': 0.3}, False,
            ['sad', 'hopeless'], 'medium'
        )
        assert level == 'high'

    def test_high_sadness_prob_no_distress(self):
        level = EmotionAnalyzer._compute_concern_level(
            'sadness', {'sadness': 0.65, 'neutral': 0.35}, False,
            [], 'medium'
        )
        # sadness > 0.6 but neg_prob < 0.7 → medium
        assert level in ('medium', 'high')

    def test_low_positive(self):
        level = EmotionAnalyzer._compute_concern_level(
            'joy', {'joy': 0.8, 'neutral': 0.2}, False, [], 'low'
        )
        assert level == 'low'

    def test_medium_severity_returns_medium(self):
        level = EmotionAnalyzer._compute_concern_level(
            'neutral', {'neutral': 0.6, 'sadness': 0.2, 'joy': 0.2}, False,
            [], 'medium'
        )
        assert level == 'medium'


# ─────────────────────────────────────────────────────────────────────────────
# ConversationHandler — confidence-based empathy amplification
# ─────────────────────────────────────────────────────────────────────────────

class TestEmpathyAmplification:
    """Verify that high-confidence negative emotions produce amplified responses."""

    def setup_method(self):
        self.handler = ConversationHandler()

    def test_high_confidence_sadness_amplified(self):
        emotion_data = {
            'emotion': 'negative',
            'severity': 'high',
            'polarity': -0.7,
            'primary_emotion': 'sadness',
            'emotion_confidence': 0.75,
            'concern_level': 'high',
            'has_abuse_indicators': False,
            'explanation': '',
            'severity_score': 7.0,
        }
        self.handler.add_message("I feel deeply sad and alone", emotion_data)
        response = self.handler.generate_response(emotion_data)
        assert isinstance(response, str) and len(response) > 20
        # The amplification adds supportive language with 💙
        assert '💙' in response

    def test_low_confidence_no_amplification_marker(self):
        emotion_data = {
            'emotion': 'neutral',
            'severity': 'low',
            'polarity': 0.1,
            'primary_emotion': 'neutral',
            'emotion_confidence': 0.3,
            'concern_level': 'low',
            'has_abuse_indicators': False,
            'explanation': '',
            'severity_score': 2.0,
        }
        self.handler.add_message("I'm okay today", emotion_data)
        response = self.handler.generate_response(emotion_data)
        assert isinstance(response, str) and len(response) > 10
        # Low concern neutral should NOT contain amplification phrases
        assert "intensity of what you're going through" not in response


# ─────────────────────────────────────────────────────────────────────────────
# WellnessBuddy — metadata exposure
# ─────────────────────────────────────────────────────────────────────────────

class TestWellnessBuddyMetadata:
    """Verify concern_level and emotion_confidence appear in response metadata."""

    def setup_method(self):
        self.buddy = WellnessBuddy()
        self.buddy.user_profile = UserProfile('test_meta')
        self.buddy.user_profile.set_name('Tester')
        self.buddy.user_id = 'test_meta'

    def test_metadata_contains_concern_level(self):
        self.buddy.process_message("I feel very sad and hopeless")
        meta = self.buddy.get_last_response_metadata()
        assert 'concern_level' in meta
        assert meta['concern_level'] in ('low', 'medium', 'high', 'critical')

    def test_metadata_contains_emotion_confidence(self):
        self.buddy.process_message("I am happy and grateful!")
        meta = self.buddy.get_last_response_metadata()
        assert 'emotion_confidence' in meta
        assert isinstance(meta['emotion_confidence'], float)

    def test_crisis_metadata_critical(self):
        self.buddy.process_message("I want to end my life")
        meta = self.buddy.get_last_response_metadata()
        assert meta['concern_level'] == 'critical'
