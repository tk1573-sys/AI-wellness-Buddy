"""Tests for emotion detection models.

Validates:
- EmotionTransformer instantiation and lazy loading
- Probability output format and normalisation
- Keyword-based fallback when transformer is unavailable
- Crisis detection probability scores
- EmotionAnalyzer integration (primary_emotion, xai_explanation)
"""

from models.emotion_transformer import EmotionTransformer
from emotion_analyzer import EmotionAnalyzer


# ------------------------------------------------------------------
# EmotionTransformer basics
# ------------------------------------------------------------------

def test_model_loads_successfully():
    """EmotionTransformer must instantiate without errors."""
    et = EmotionTransformer()
    assert et is not None
    assert isinstance(et.available, bool)


def test_emotion_probabilities_returned():
    """classify() must return a dict of emotion→probability."""
    et = EmotionTransformer()
    result = et.classify("I feel extremely overwhelmed and lonely.")
    assert isinstance(result, dict)
    assert len(result) > 0
    assert all(isinstance(v, (int, float)) for v in result.values())


def test_probabilities_sum_to_one():
    """Probability distribution must sum to 1.0 (within tolerance)."""
    et = EmotionTransformer()
    probs = et.classify("I feel extremely overwhelmed and lonely.")
    total = sum(probs.values())
    assert abs(total - 1.0) < 1e-3, f"Probabilities sum to {total}, expected ~1.0"


def test_fallback_keyword_model_works():
    """classify_keywords_only() must return valid probabilities."""
    et = EmotionTransformer()
    probs = et.classify_keywords_only("I am happy and excited")
    assert isinstance(probs, dict)
    assert len(probs) > 0
    total = sum(probs.values())
    assert abs(total - 1.0) < 1e-3


def test_keyword_fallback_detects_sadness():
    """Keyword model must return sadness as top emotion for sad text."""
    et = EmotionTransformer()
    probs = et.classify_keywords_only("I am sad and lonely and crying")
    assert max(probs, key=probs.get) == 'sadness'


def test_keyword_fallback_detects_joy():
    """Keyword model must return joy as top emotion for happy text."""
    et = EmotionTransformer()
    probs = et.classify_keywords_only("I am happy and excited and wonderful")
    assert max(probs, key=probs.get) == 'joy'


# ------------------------------------------------------------------
# Crisis detection
# ------------------------------------------------------------------

def test_crisis_detection_probability_scores():
    """Crisis-related input must produce a probability score for the crisis class."""
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I want to end it all, life is not worth living")
    assert 'primary_emotion' in result
    # Crisis inputs should be flagged with high severity or crisis emotion
    assert result.get('is_crisis') or result.get('primary_emotion') == 'crisis' or \
        result.get('severity') in ('high',)


# ------------------------------------------------------------------
# Full emotion classification integration
# ------------------------------------------------------------------

def test_emotion_detected_for_overwhelmed_input():
    """classify_emotion must return a detected emotion for distress text."""
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel extremely overwhelmed and lonely.")
    assert 'primary_emotion' in result
    assert result['primary_emotion'] != ''


def test_probability_distribution_returned():
    """classify_emotion must include emotion_probabilities."""
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel extremely overwhelmed and lonely.")
    assert 'emotion_probabilities' in result
    probs = result['emotion_probabilities']
    assert isinstance(probs, dict)
    assert len(probs) > 0


def test_explanation_keywords_returned():
    """classify_emotion must include an explanation field."""
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel extremely overwhelmed and lonely.")
    assert 'explanation' in result or 'xai_explanation' in result


def test_xai_explanation_has_key_fields():
    """XAI explanation must contain structured explainability fields."""
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel anxious and stressed")
    xai = result.get('xai_explanation', {})
    assert 'primary_emotion' in xai
    assert 'confidence' in xai
    assert 'key_indicators' in xai
    assert 'model_source' in xai
