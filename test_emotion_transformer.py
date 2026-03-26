"""Tests for the models.emotion_transformer module."""

from models.emotion_transformer import EmotionTransformer


# ------------------------------------------------------------------
# Instantiation and availability
# ------------------------------------------------------------------

def test_emotion_transformer_instantiates():
    """EmotionTransformer must instantiate without raising."""
    et = EmotionTransformer()
    assert isinstance(et, EmotionTransformer)


def test_available_is_bool():
    """available property must always be a boolean."""
    et = EmotionTransformer()
    assert isinstance(et.available, bool)


# ------------------------------------------------------------------
# Lazy loading
# ------------------------------------------------------------------

def test_lazy_loading_deferred():
    """Model loading should NOT happen at construction time."""
    et = EmotionTransformer()
    assert et._load_attempted is False, "Model must not be loaded at __init__"
    assert et._pipeline is None


def test_lazy_loading_triggered_on_classify():
    """First classify() call should trigger model loading."""
    et = EmotionTransformer()
    _ = et.classify("hello")
    assert et._load_attempted is True


def test_lazy_loading_triggered_on_available():
    """Accessing .available should trigger model loading."""
    et = EmotionTransformer()
    _ = et.available
    assert et._load_attempted is True


# ------------------------------------------------------------------
# Output format: normalised probability distribution
# ------------------------------------------------------------------

def test_classify_returns_dict():
    """classify() must return a dict."""
    et = EmotionTransformer()
    result = et.classify("I feel happy today")
    assert isinstance(result, dict)


def test_classify_keys_are_emotions():
    """classify() output must contain all canonical emotion labels."""
    et = EmotionTransformer()
    result = et.classify("I feel happy today")
    for emotion in EmotionTransformer.EMOTIONS:
        assert emotion in result, f"Missing emotion label: {emotion}"


def test_classify_probabilities_sum_to_one():
    """classify() output values must sum to 1.0 (within tolerance)."""
    et = EmotionTransformer()
    for text in [
        "I feel happy today",
        "I am very sad and lonely",
        "This is just a normal day",
        "I am angry and furious",
        "I am scared and terrified",
        "I feel stressed and overwhelmed",
        "asdfghjkl",  # no keywords
    ]:
        result = et.classify(text)
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-3, (
            f"Probabilities sum to {total} for text: {text!r}"
        )


def test_classify_values_are_non_negative():
    """All probability values must be >= 0."""
    et = EmotionTransformer()
    result = et.classify("I am very worried and anxious")
    for label, prob in result.items():
        assert prob >= 0.0, f"Negative probability for {label}: {prob}"


# ------------------------------------------------------------------
# Keyword fallback (no transformer available in test env)
# ------------------------------------------------------------------

def test_keyword_fallback_joy():
    et = EmotionTransformer()
    result = et.classify("I am so happy and excited and joyful")
    assert result["joy"] > 0


def test_keyword_fallback_sadness():
    et = EmotionTransformer()
    result = et.classify("I feel sad and heartbroken and devastated")
    assert result["sadness"] > 0


def test_keyword_fallback_anger():
    et = EmotionTransformer()
    result = et.classify("I am furious and angry and enraged")
    assert result["anger"] > 0


def test_keyword_fallback_fear():
    et = EmotionTransformer()
    result = et.classify("I am terrified and scared and frightened")
    assert result["fear"] > 0


def test_keyword_fallback_anxiety():
    et = EmotionTransformer()
    result = et.classify("I feel anxious stressed and overwhelmed")
    assert result["anxiety"] > 0


def test_keyword_fallback_neutral():
    et = EmotionTransformer()
    result = et.classify("Everything is okay and fine and normal")
    assert result["neutral"] > 0


def test_no_keywords_returns_uniform():
    """When no keywords match, the keyword-only path returns a uniform distribution."""
    et = EmotionTransformer()
    result = et._classify_keywords("xyzzy foobarbaz")
    values = list(result.values())
    # All values should be equal (uniform) in the keyword-only fallback
    assert all(abs(v - values[0]) < 1e-3 for v in values)


# ------------------------------------------------------------------
# Single-message inference cache
# ------------------------------------------------------------------

def test_cache_returns_same_result():
    """Repeated classify() with the same text should return identical results."""
    et = EmotionTransformer()
    r1 = et.classify("I feel happy today")
    r2 = et.classify("I feel happy today")
    assert r1 == r2


def test_cache_returns_copy():
    """Cache must return a copy so mutations don't affect stored value."""
    et = EmotionTransformer()
    r1 = et.classify("I feel happy today")
    r1["joy"] = 999.0  # mutate returned dict
    r2 = et.classify("I feel happy today")
    assert r2["joy"] != 999.0


def test_cache_invalidated_on_new_text():
    """Different text should produce a fresh classification."""
    et = EmotionTransformer()
    r1 = et.classify("I am extremely happy")
    r2 = et.classify("I am extremely sad")
    # At minimum, the dominant emotions should differ
    assert r1 != r2


def test_invalidate_cache():
    """invalidate_cache() should clear the cache."""
    et = EmotionTransformer()
    _ = et.classify("I feel happy today")
    assert et._cache_key is not None
    et.invalidate_cache()
    assert et._cache_key is None
    assert et._cache_value is None


# ------------------------------------------------------------------
# Integration with EmotionAnalyzer
# ------------------------------------------------------------------

def test_emotion_analyzer_uses_transformer():
    """EmotionAnalyzer should have an EmotionTransformer instance."""
    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()
    assert hasattr(analyzer, '_emotion_transformer')
    assert isinstance(analyzer._emotion_transformer, EmotionTransformer)


def test_emotion_analyzer_probabilities_sum_to_one():
    """emotion_probabilities in classify_emotion() must sum to ~1.0."""
    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()
    for text in [
        "I feel very anxious and scared today",
        "I am so happy and excited",
        "Everything is normal and okay",
        "I am furious about what happened",
    ]:
        result = analyzer.classify_emotion(text)
        probs = result['emotion_probabilities']
        total = sum(probs.values())
        assert abs(total - 1.0) < 1e-2, (
            f"Probabilities sum to {total} for text: {text!r}"
        )


def test_emotion_analyzer_backward_compat_fields():
    """classify_emotion() must still return all backward-compatible fields."""
    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel a bit nervous")
    required_keys = [
        'emotion', 'severity', 'polarity', 'subjectivity',
        'primary_emotion', 'emotion_scores', 'emotion_probabilities',
        'is_crisis', 'crisis_probability', 'explanation',
        'dominant_emotion', 'crisis_detected', 'severity_score',
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"


def test_classify_emotion_ml_no_double_inference():
    """classify_emotion_ml() must not trigger extra transformer inference."""
    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()
    # First call — triggers classify_emotion() which calls transformer.classify()
    result = analyzer.classify_emotion_ml("I am sad and crying")
    assert 'ml_available' in result
    assert 'ml_scores' in result
    # The cache key should match the text (only one pass happened)
    assert analyzer._emotion_transformer._cache_key == "I am sad and crying"
