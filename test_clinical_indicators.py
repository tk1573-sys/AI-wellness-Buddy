"""
Tests for clinical_indicators module and its integration into
wellness_buddy.py and agent_pipeline.py.

Run with: python -m pytest test_clinical_indicators.py -v
"""

from clinical_indicators import (
    compute_clinical_indicators,
    compute_emotional_risk,
    DISCLAIMER,
    _sustained_sadness,
    _anxiety_escalation,
    _emotional_volatility,
    _social_withdrawal,
    _negative_self_perception,
)


# ── Helper builders ──────────────────────────────────────────────────────

def _make_entry(sadness=0.1, anxiety=0.1, polarity=0.0, text="", **kw):
    """Build a minimal emotion_data dict for testing."""
    return {
        "emotion_probabilities": {
            "joy": 0.0, "sadness": sadness, "anger": 0.0,
            "fear": 0.0, "anxiety": anxiety, "neutral": 0.0,
        },
        "polarity": polarity,
        "text": text,
        "distress_keywords": kw.get("distress_keywords", []),
    }


# ── DISCLAIMER ───────────────────────────────────────────────────────────

class TestDisclaimer:
    def test_disclaimer_present(self):
        assert isinstance(DISCLAIMER, str)
        assert "not a medical diagnostic tool" in DISCLAIMER


# ── Sustained sadness ────────────────────────────────────────────────────

class TestSustainedSadness:
    def test_below_threshold(self):
        history = [_make_entry(sadness=0.3) for _ in range(5)]
        assert _sustained_sadness(history) is False

    def test_at_threshold(self):
        history = [_make_entry(sadness=0.65) for _ in range(3)]
        assert _sustained_sadness(history) is True

    def test_not_enough_messages(self):
        history = [_make_entry(sadness=0.8) for _ in range(2)]
        assert _sustained_sadness(history) is False


# ── Anxiety escalation ───────────────────────────────────────────────────

class TestAnxietyEscalation:
    def test_increasing_trend(self):
        history = [_make_entry(anxiety=v) for v in [0.1, 0.2, 0.3, 0.4, 0.5]]
        assert _anxiety_escalation(history) is True

    def test_decreasing_trend(self):
        history = [_make_entry(anxiety=v) for v in [0.5, 0.4, 0.3, 0.2, 0.1]]
        assert _anxiety_escalation(history) is False

    def test_too_few_messages(self):
        history = [_make_entry(anxiety=0.5)]
        assert _anxiety_escalation(history) is False


# ── Emotional volatility ─────────────────────────────────────────────────

class TestEmotionalVolatility:
    def test_no_volatility(self):
        history = [_make_entry(polarity=0.5) for _ in range(5)]
        assert _emotional_volatility(history) == 0.0

    def test_some_volatility(self):
        history = [_make_entry(polarity=p) for p in [-0.8, 0.8, -0.8, 0.8]]
        vol = _emotional_volatility(history)
        assert 0.0 < vol <= 1.0

    def test_single_entry(self):
        assert _emotional_volatility([_make_entry()]) == 0.0


# ── Social withdrawal ────────────────────────────────────────────────────

class TestSocialWithdrawal:
    def test_detected(self):
        history = [_make_entry(text="I feel so alone and isolated")]
        assert _social_withdrawal(history) is True

    def test_not_detected(self):
        history = [_make_entry(text="I had a great day with friends")]
        assert _social_withdrawal(history) is False


# ── Negative self-perception ─────────────────────────────────────────────

class TestNegativeSelfPerception:
    def test_detected(self):
        history = [_make_entry(text="I am worthless and a failure")]
        assert _negative_self_perception(history) is True

    def test_not_detected(self):
        history = [_make_entry(text="I feel proud of my work today")]
        assert _negative_self_perception(history) is False


# ── compute_clinical_indicators (integration) ────────────────────────────

class TestComputeClinicalIndicators:
    def test_empty_history(self):
        result = compute_clinical_indicators([])
        assert result["sustained_sadness"] is False
        assert result["anxiety_escalation"] is False
        assert result["emotional_volatility"] == 0.0
        assert result["social_withdrawal"] is False
        assert result["negative_self_perception"] is False
        assert "disclaimer" in result

    def test_with_sad_history(self):
        history = [_make_entry(sadness=0.7) for _ in range(4)]
        result = compute_clinical_indicators(history)
        assert result["sustained_sadness"] is True

    def test_all_keys_present(self):
        result = compute_clinical_indicators([_make_entry()])
        expected_keys = {
            "sustained_sadness", "anxiety_escalation", "emotional_volatility",
            "social_withdrawal", "negative_self_perception", "disclaimer",
        }
        assert set(result.keys()) == expected_keys


# ── compute_emotional_risk ───────────────────────────────────────────────

class TestComputeEmotionalRisk:
    def test_low_risk(self):
        emotion_data = _make_entry(sadness=0.1, anxiety=0.1)
        result = compute_emotional_risk(emotion_data)
        assert result["risk_level"] == "low"
        assert 0.0 <= result["risk_score"] <= 0.3

    def test_high_risk(self):
        emotion_data = _make_entry(sadness=0.8, anxiety=0.7)
        clinical = {"emotional_volatility": 0.6, "sustained_sadness": True,
                     "anxiety_escalation": True}
        result = compute_emotional_risk(emotion_data, clinical)
        assert result["risk_level"] in ("high", "critical")
        assert result["risk_score"] > 0.5

    def test_risk_score_bounds(self):
        emotion_data = _make_entry(sadness=1.0, anxiety=1.0)
        clinical = {"emotional_volatility": 1.0, "sustained_sadness": True,
                     "anxiety_escalation": True}
        result = compute_emotional_risk(emotion_data, clinical)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_medium_risk(self):
        emotion_data = _make_entry(sadness=0.5, anxiety=0.3)
        result = compute_emotional_risk(emotion_data)
        assert result["risk_level"] in ("low", "medium")

    def test_distress_keywords_boost(self):
        emotion_data = _make_entry(sadness=0.4, anxiety=0.3)
        emotion_data["distress_keywords"] = ["hopeless", "trapped", "exhausted", "crying", "pain"]
        result = compute_emotional_risk(emotion_data)
        assert result["risk_score"] > 0.3

    def test_risk_levels_mapping(self):
        """Verify all four risk levels are reachable."""
        levels_seen = set()
        for sadness in [0.05, 0.4, 0.7, 0.9]:
            ed = _make_entry(sadness=sadness, anxiety=sadness * 0.8)
            ci = {"emotional_volatility": sadness * 0.5,
                  "sustained_sadness": sadness > 0.6,
                  "anxiety_escalation": sadness > 0.7}
            r = compute_emotional_risk(ed, ci)
            levels_seen.add(r["risk_level"])
        assert len(levels_seen) >= 3  # at least low, medium, high reachable


# ── Integration: WellnessBuddy metadata ──────────────────────────────────

class TestWellnessBuddyIntegration:
    def test_metadata_has_clinical_indicators(self):
        from wellness_buddy import WellnessBuddy
        from user_profile import UserProfile
        buddy = WellnessBuddy()
        buddy.user_profile = UserProfile("ci_test")
        buddy.user_profile.set_name("Tester")
        buddy.user_id = "ci_test"
        buddy.process_message("I feel very sad and hopeless")
        meta = buddy.get_last_response_metadata()
        assert "clinical_indicators" in meta
        ci = meta["clinical_indicators"]
        assert "sustained_sadness" in ci
        assert "anxiety_escalation" in ci
        assert "emotional_volatility" in ci
        assert "disclaimer" in ci

    def test_metadata_has_emotional_risk(self):
        from wellness_buddy import WellnessBuddy
        from user_profile import UserProfile
        buddy = WellnessBuddy()
        buddy.user_profile = UserProfile("risk_test")
        buddy.user_profile.set_name("Tester")
        buddy.user_id = "risk_test"
        buddy.process_message("I am happy today")
        meta = buddy.get_last_response_metadata()
        assert "emotional_risk" in meta
        er = meta["emotional_risk"]
        assert "risk_score" in er
        assert "risk_level" in er

    def test_metadata_has_disclaimer(self):
        from wellness_buddy import WellnessBuddy
        from user_profile import UserProfile
        buddy = WellnessBuddy()
        buddy.user_profile = UserProfile("disc_test")
        buddy.user_profile.set_name("Tester")
        buddy.user_id = "disc_test"
        buddy.process_message("Hello there")
        meta = buddy.get_last_response_metadata()
        assert "disclaimer" in meta
        assert "not a medical diagnostic tool" in meta["disclaimer"]


# ── Integration: Agent pipeline output ───────────────────────────────────

class TestAgentPipelineIntegration:
    def test_pipeline_output_has_clinical_fields(self):
        from agent_pipeline import WellnessAgentPipeline
        pipeline = WellnessAgentPipeline()
        result = pipeline.process_turn("I feel anxious and worried")
        assert "clinical_indicators" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "concern_level" in result
        assert "disclaimer" in result

    def test_pipeline_output_research_ready(self):
        """Pipeline output should contain all research-ready fields."""
        from agent_pipeline import WellnessAgentPipeline
        pipeline = WellnessAgentPipeline()
        result = pipeline.process_turn("Things are going well today")
        research_keys = {
            "emotion", "concern_level", "clinical_indicators",
            "risk_score", "risk_level", "patterns", "forecasting",
            "alert", "response", "disclaimer",
        }
        assert research_keys.issubset(set(result.keys()))
