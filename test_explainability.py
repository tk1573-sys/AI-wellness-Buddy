"""
Tests for the explainability module (Explainable AI / XAI).

Validates keyword extraction, sentiment contribution analysis,
model-source labelling, and the structured explanation builder.
"""

import pytest

from explainability import (
    extract_key_indicators,
    generate_explanation,
    get_model_source,
    get_sentiment_contribution,
)


# -----------------------------------------------------------------------
# extract_key_indicators
# -----------------------------------------------------------------------

class TestExtractKeyIndicators:
    """Tests for keyword-indicator extraction."""

    KEYWORDS = {
        'joy': ['happy', 'excited', 'love'],
        'sadness': ['sad', 'lonely', 'overwhelmed', 'tired', 'cry'],
        'anger': ['angry', 'furious'],
        'crisis': [],
    }
    CRISIS_KEYWORDS = ['suicide', 'kill myself', 'end it all']

    def test_basic_match(self):
        result = extract_key_indicators(
            "I feel lonely and tired today",
            "sadness",
            emotion_keywords=self.KEYWORDS,
        )
        assert 'lonely' in result
        assert 'tired' in result

    def test_no_match_returns_empty(self):
        result = extract_key_indicators(
            "The weather is nice",
            "joy",
            emotion_keywords=self.KEYWORDS,
        )
        assert result == []

    def test_max_indicators_cap(self):
        # All sadness keywords in one sentence
        text = "I feel sad lonely overwhelmed tired cry"
        result = extract_key_indicators(
            text, "sadness",
            emotion_keywords=self.KEYWORDS,
            max_indicators=3,
        )
        assert len(result) <= 3

    def test_crisis_keywords(self):
        result = extract_key_indicators(
            "I want to end it all",
            "crisis",
            emotion_keywords=self.KEYWORDS,
            crisis_keywords=self.CRISIS_KEYWORDS,
        )
        assert 'end it all' in result

    def test_none_keywords(self):
        result = extract_key_indicators("hello", "neutral")
        assert result == []

    def test_case_insensitive(self):
        result = extract_key_indicators(
            "I am LONELY",
            "sadness",
            emotion_keywords=self.KEYWORDS,
        )
        assert 'lonely' in result


# -----------------------------------------------------------------------
# get_sentiment_contribution
# -----------------------------------------------------------------------

class TestGetSentimentContribution:
    """Tests for sentiment contribution summary."""

    def test_positive_polarity(self):
        result = get_sentiment_contribution(0.6, 0.8)
        assert result['influence'] == 'positive'
        assert result['polarity'] == 0.6
        assert result['subjectivity'] == 0.8

    def test_negative_polarity(self):
        result = get_sentiment_contribution(-0.5, 0.3)
        assert result['influence'] == 'negative'

    def test_neutral_zone(self):
        result = get_sentiment_contribution(0.05, 0.5)
        assert result['influence'] == 'neutral'

    def test_boundary_positive(self):
        # Exactly at boundary → neutral (not > 0.15)
        result = get_sentiment_contribution(0.15, 0.0)
        assert result['influence'] == 'neutral'

    def test_rounding(self):
        result = get_sentiment_contribution(0.123456789, 0.987654321)
        assert result['polarity'] == 0.1235
        assert result['subjectivity'] == 0.9877


# -----------------------------------------------------------------------
# get_model_source
# -----------------------------------------------------------------------

class TestGetModelSource:
    """Tests for model-source label."""

    def test_transformer_available(self):
        assert get_model_source(True) == "transformer + keyword hybrid"

    def test_keyword_only(self):
        assert get_model_source(False) == "keyword heuristic"


# -----------------------------------------------------------------------
# generate_explanation
# -----------------------------------------------------------------------

class TestGenerateExplanation:
    """Tests for the structured explanation builder."""

    KEYWORDS = {
        'sadness': ['overwhelmed', 'lonely', 'tired'],
        'joy': ['happy', 'excited'],
    }

    def test_full_explanation_structure(self):
        emotion_data = {
            'primary_emotion': 'sadness',
            'emotion_probabilities': {'sadness': 0.71, 'joy': 0.1, 'neutral': 0.19},
            'polarity': -0.45,
            'subjectivity': 0.72,
        }
        result = generate_explanation(
            "I feel overwhelmed and lonely",
            emotion_data,
            emotion_keywords=self.KEYWORDS,
        )
        assert result['primary_emotion'] == 'sadness'
        assert result['confidence'] == 0.71
        assert 'overwhelmed' in result['key_indicators']
        assert 'lonely' in result['key_indicators']
        assert result['sentiment_contribution']['influence'] == 'negative'
        assert result['model_source'] == 'keyword heuristic'

    def test_transformer_source(self):
        emotion_data = {
            'primary_emotion': 'joy',
            'emotion_probabilities': {'joy': 0.9},
            'polarity': 0.5,
            'subjectivity': 0.6,
        }
        result = generate_explanation(
            "I am so happy",
            emotion_data,
            emotion_keywords=self.KEYWORDS,
            transformer_available=True,
        )
        assert result['model_source'] == 'transformer + keyword hybrid'

    def test_missing_emotion_data_fields(self):
        """Graceful fallback when emotion_data is sparse."""
        result = generate_explanation("hello", {})
        assert result['primary_emotion'] == 'neutral'
        assert result['confidence'] == 0.0
        assert result['key_indicators'] == []
        assert result['model_source'] == 'keyword heuristic'

    def test_confidence_rounding(self):
        emotion_data = {
            'primary_emotion': 'joy',
            'emotion_probabilities': {'joy': 0.123456789},
            'polarity': 0.0,
            'subjectivity': 0.0,
        }
        result = generate_explanation("happy", emotion_data,
                                      emotion_keywords=self.KEYWORDS)
        assert result['confidence'] == 0.1235
