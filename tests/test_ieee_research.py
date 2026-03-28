"""
IEEE Research submission tests.

Covers the four research-critical feature areas:
1. Personalization Engine (user profile triggers + response integration)
2. Emotion Intelligence (emotion detection, escalation, CDI)
3. Analytics (emotion trends, distribution, JSONL logging)
4. Evaluation Setup (prediction logging, baseline vs personalised comparison)
"""

import json
import os
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Project-root on path
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ===========================================================================
# 1. Personalization Engine
# ===========================================================================

class TestPersonalizationEngine:
    """UserProfile triggers are stored, retrieved, and wired into the pipeline."""

    def test_add_and_get_personal_trigger(self):
        from user_profile import UserProfile
        profile = UserProfile("u1")
        profile.add_personal_trigger("work")
        profile.add_personal_trigger("exam")
        triggers = profile.get_personal_triggers()
        assert "work" in triggers
        assert "exam" in triggers

    def test_add_trigger_normalises_case(self):
        from user_profile import UserProfile
        profile = UserProfile("u2")
        profile.add_personal_trigger("  Anxiety  ")
        assert "anxiety" in profile.get_personal_triggers()

    def test_add_trigger_deduplicates(self):
        from user_profile import UserProfile
        profile = UserProfile("u3")
        profile.add_personal_trigger("stress")
        profile.add_personal_trigger("stress")
        assert profile.get_personal_triggers().count("stress") == 1

    def test_get_personal_context_includes_triggers(self):
        from user_profile import UserProfile
        profile = UserProfile("u4")
        profile.add_personal_trigger("family")
        ctx = profile.get_personal_context()
        assert "personal_triggers" in ctx
        assert "family" in ctx["personal_triggers"]

    def test_get_trigger_context_detects_match(self):
        from user_profile import UserProfile
        profile = UserProfile("u5")
        profile.add_personal_trigger("deadline")
        result = profile.get_trigger_context("I am worried about the deadline tomorrow")
        assert result["triggered"] is True
        assert "deadline" in result["matched_triggers"]

    def test_get_trigger_context_no_match(self):
        from user_profile import UserProfile
        profile = UserProfile("u6")
        profile.add_personal_trigger("exam")
        result = profile.get_trigger_context("I feel fine today")
        assert result["triggered"] is False
        assert result["matched_triggers"] == []

    def test_get_trigger_context_total_triggers(self):
        from user_profile import UserProfile
        profile = UserProfile("u7")
        profile.add_personal_trigger("work")
        profile.add_personal_trigger("family")
        result = profile.get_trigger_context("something unrelated")
        assert result["total_triggers"] == 2

    def test_pipeline_uses_profile_context_for_response(self):
        """When user_profile is passed, the pipeline wires personal context."""
        from agent_pipeline import WellnessAgentPipeline
        from user_profile import UserProfile
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            from emotion_analytics import EmotionAnalyticsLogger
            logger = EmotionAnalyticsLogger(log_dir=tmpdir)
            pipeline = WellnessAgentPipeline(analytics_logger=logger)

            profile = UserProfile("u8")
            profile.add_personal_trigger("exam")
            profile.set_response_style("short")

            result = pipeline.process_turn(
                "I am very anxious about my exam tomorrow",
                user_profile=profile,
            )
        assert "response" in result
        assert "emotion" in result

    def test_pipeline_mode_is_personalized_when_profile_given(self):
        """Mode logged must be 'personalized' when user_profile is provided."""
        from agent_pipeline import WellnessAgentPipeline
        from user_profile import UserProfile
        from emotion_analytics import EmotionAnalyticsLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EmotionAnalyticsLogger(log_dir=tmpdir)
            pipeline = WellnessAgentPipeline(analytics_logger=logger)
            profile = UserProfile("u9")
            pipeline.process_turn("I feel anxious", user_profile=profile)

            entries = logger.load_logs(mode="personalized")
            assert len(entries) == 1
            assert entries[0]["mode"] == "personalized"

    def test_pipeline_mode_is_baseline_without_profile(self):
        """Mode logged must be 'baseline' when no user_profile is passed."""
        from agent_pipeline import WellnessAgentPipeline
        from emotion_analytics import EmotionAnalyticsLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EmotionAnalyticsLogger(log_dir=tmpdir)
            pipeline = WellnessAgentPipeline(analytics_logger=logger)
            pipeline.process_turn("I feel okay")

            entries = logger.load_logs(mode="baseline")
            assert len(entries) == 1
            assert entries[0]["mode"] == "baseline"


# ===========================================================================
# 2. Emotion Intelligence
# ===========================================================================

class TestEmotionIntelligence:
    """Emotion detection, escalation, and CDI score."""

    def test_emotion_detection_returns_primary_emotion(self):
        from emotion_analyzer import EmotionAnalyzer
        analyzer = EmotionAnalyzer()
        result = analyzer.classify_emotion("I feel happy and joyful today")
        assert "primary_emotion" in result or "emotion" in result

    def test_emotion_probabilities_present(self):
        from emotion_analyzer import EmotionAnalyzer
        analyzer = EmotionAnalyzer()
        result = analyzer.classify_emotion("I am very anxious about everything")
        assert "emotion_probabilities" in result
        total = sum(result["emotion_probabilities"].values())
        assert abs(total - 1.0) < 0.05

    def test_cdi_score_in_valid_range(self):
        from clinical_indicators import compute_cdi, compute_clinical_indicators
        emotion_data = {
            "emotion_probabilities": {"sadness": 0.6, "anxiety": 0.2, "joy": 0.1,
                                       "neutral": 0.1, "anger": 0.0, "fear": 0.0},
            "distress_keywords": ["hopeless", "alone"],
            "concern_level": "high",
        }
        ci = compute_clinical_indicators([emotion_data])
        cdi = compute_cdi(emotion_data, ci)
        assert 0.0 <= cdi["cdi_score"] <= 1.0
        assert cdi["cdi_level"] in ("low", "moderate", "high", "critical")

    def test_cdi_components_present(self):
        from clinical_indicators import compute_cdi
        emotion_data = {
            "emotion_probabilities": {"sadness": 0.5, "anxiety": 0.3, "joy": 0.1,
                                       "neutral": 0.1, "anger": 0.0, "fear": 0.0},
            "distress_keywords": [],
        }
        cdi = compute_cdi(emotion_data)
        assert "cdi_components" in cdi
        for key in ("negative_emotion_probability", "distress_keyword_density",
                    "emotion_volatility", "sustained_sadness"):
            assert key in cdi["cdi_components"]

    def test_escalation_detected_after_consecutive_negatives(self):
        from clinical_indicators import detect_escalation
        history = [
            {"emotion": "sadness"},
            {"emotion": "anxiety"},
            {"emotion": "fear"},
            {"emotion": "anger"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is True
        assert result["warning"] is not None

    def test_no_escalation_with_mixed_emotions(self):
        from clinical_indicators import detect_escalation
        history = [
            {"emotion": "joy"},
            {"emotion": "sadness"},
            {"emotion": "neutral"},
            {"emotion": "joy"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is False

    def test_pipeline_includes_escalation_key(self):
        from agent_pipeline import WellnessAgentPipeline
        from emotion_analytics import EmotionAnalyticsLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EmotionAnalyticsLogger(log_dir=tmpdir)
            pipeline = WellnessAgentPipeline(analytics_logger=logger)
            result = pipeline.process_turn("I feel scared and alone")
            assert "escalation" in result
            assert "escalation_detected" in result["escalation"]

    def test_pipeline_includes_cdi_key(self):
        from agent_pipeline import WellnessAgentPipeline
        from emotion_analytics import EmotionAnalyticsLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EmotionAnalyticsLogger(log_dir=tmpdir)
            pipeline = WellnessAgentPipeline(analytics_logger=logger)
            result = pipeline.process_turn("I have been feeling very sad lately")
            assert "cdi" in result
            assert "cdi_score" in result["cdi"]


# ===========================================================================
# 3. Analytics
# ===========================================================================

class TestEmotionAnalytics:
    """Emotion trends, distribution, and JSONL logging."""

    def _make_logger(self, tmpdir):
        from emotion_analytics import EmotionAnalyticsLogger
        return EmotionAnalyticsLogger(log_dir=tmpdir)

    def test_log_interaction_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="I feel sad",
                emotion_data={"primary_emotion": "sadness", "concern_level": "medium"},
                mode="baseline",
            )
            assert logger.log_path.exists()

    def test_log_interaction_entry_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="I am anxious",
                emotion_data={"primary_emotion": "anxiety", "concern_level": "high"},
                cdi={"cdi_score": 0.45, "cdi_level": "moderate"},
                mode="personalized",
            )
            with open(logger.log_path) as fh:
                entry = json.loads(fh.readline())
            assert entry["emotion"] == "anxiety"
            assert entry["cdi_score"] == 0.45
            assert entry["mode"] == "personalized"

    def test_load_logs_returns_all_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            for emotion in ("joy", "sadness", "anger"):
                logger.log_interaction(
                    user_message=f"I feel {emotion}",
                    emotion_data={"primary_emotion": emotion, "concern_level": "low"},
                )
            entries = logger.load_logs()
            assert len(entries) == 3

    def test_load_logs_filters_by_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="msg1",
                emotion_data={"primary_emotion": "joy"},
                mode="baseline",
            )
            logger.log_interaction(
                user_message="msg2",
                emotion_data={"primary_emotion": "sadness"},
                mode="personalized",
            )
            assert len(logger.load_logs(mode="baseline")) == 1
            assert len(logger.load_logs(mode="personalized")) == 1

    def test_get_emotion_trends_returns_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            for em in ("sadness", "anxiety", "neutral"):
                logger.log_interaction(
                    user_message="msg",
                    emotion_data={"primary_emotion": em},
                )
            trends = logger.get_emotion_trends()
            assert isinstance(trends, list)
            assert len(trends) == 3
            assert all("emotion" in t and "timestamp" in t for t in trends)

    def test_get_emotion_trends_contains_cdi_score(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="I feel hopeless",
                emotion_data={"primary_emotion": "sadness"},
                cdi={"cdi_score": 0.72, "cdi_level": "high"},
            )
            trends = logger.get_emotion_trends()
            assert trends[0]["cdi_score"] == 0.72

    def test_get_emotion_distribution_returns_all_known_emotions(self):
        from emotion_analytics import _KNOWN_EMOTIONS
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="I'm happy",
                emotion_data={"primary_emotion": "joy"},
            )
            dist = logger.get_emotion_distribution()
            for emotion in _KNOWN_EMOTIONS:
                assert emotion in dist

    def test_get_emotion_distribution_sums_to_one(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            for em in ("joy", "sadness", "anger", "neutral"):
                logger.log_interaction(
                    user_message="msg",
                    emotion_data={"primary_emotion": em},
                )
            dist = logger.get_emotion_distribution()
            # Known emotions cover joy/sadness/anger/neutral, others are 0
            total = sum(dist.values())
            assert abs(total - 1.0) < 0.01

    def test_session_distribution_uses_buffer_not_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="hello",
                emotion_data={"primary_emotion": "joy"},
            )
            dist = logger.session_distribution()
            assert dist["joy"] > 0.0

    def test_reset_session_clears_buffer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="hello",
                emotion_data={"primary_emotion": "joy"},
            )
            logger.reset_session()
            assert logger.session_trends() == []

    def test_module_level_get_emotion_trends(self):
        from emotion_analytics import get_emotion_trends
        logs = [
            {"emotion": "sadness", "cdi_score": 0.4, "risk_level": "medium",
             "mode": "baseline", "timestamp": "2026-01-01T00:00:00"},
            {"emotion": "anxiety", "cdi_score": 0.6, "risk_level": "high",
             "mode": "baseline", "timestamp": "2026-01-01T00:01:00"},
        ]
        trends = get_emotion_trends(logs)
        assert len(trends) == 2
        assert trends[0]["emotion"] == "sadness"
        assert trends[1]["cdi_score"] == 0.6

    def test_module_level_get_emotion_distribution(self):
        from emotion_analytics import get_emotion_distribution
        logs = [
            {"emotion": "joy"},
            {"emotion": "joy"},
            {"emotion": "sadness"},
        ]
        dist = get_emotion_distribution(logs)
        assert abs(dist["joy"] - 2 / 3) < 0.01
        assert abs(dist["sadness"] - 1 / 3) < 0.01


# ===========================================================================
# 4. Evaluation Setup
# ===========================================================================

class TestEvaluationSetup:
    """Research evaluation logging: predictions, outputs, and A/B comparison."""

    def _make_logger(self, tmpdir):
        from emotion_analytics import EmotionAnalyticsLogger
        return EmotionAnalyticsLogger(log_dir=tmpdir)

    def test_log_entry_includes_prediction_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            entry = logger.log_interaction(
                user_message="I feel overwhelmed",
                emotion_data={
                    "primary_emotion": "anxiety",
                    "confidence_score": 0.82,
                    "concern_level": "high",
                    "is_crisis": False,
                },
                cdi={"cdi_score": 0.55, "cdi_level": "high"},
                escalation={"escalation_detected": False, "warning": None},
                response="I hear you. Let's breathe through this together.",
                mode="baseline",
            )
            assert entry["emotion"] == "anxiety"
            assert entry["confidence"] == 0.82
            assert entry["cdi_score"] == 0.55
            assert entry["escalation_detected"] is False
            assert "I hear you" in entry["response_snippet"]

    def test_compare_modes_returns_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            # Baseline: higher distress
            for _ in range(3):
                logger.log_interaction(
                    user_message="I feel sad",
                    emotion_data={"primary_emotion": "sadness"},
                    cdi={"cdi_score": 0.65, "cdi_level": "high"},
                    mode="baseline",
                )
            # Personalized: lower distress (intervention helps)
            for _ in range(3):
                logger.log_interaction(
                    user_message="I feel better with support",
                    emotion_data={"primary_emotion": "neutral"},
                    cdi={"cdi_score": 0.30, "cdi_level": "moderate"},
                    mode="personalized",
                )
            comparison = logger.compare_modes()
            assert "baseline" in comparison
            assert "personalized" in comparison
            assert "cdi_improvement" in comparison
            assert comparison["baseline"]["n"] == 3
            assert comparison["personalized"]["n"] == 3

    def test_compare_modes_cdi_improvement_direction(self):
        """Personalized avg CDI lower than baseline yields negative improvement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="sad",
                emotion_data={"primary_emotion": "sadness"},
                cdi={"cdi_score": 0.8},
                mode="baseline",
            )
            logger.log_interaction(
                user_message="better",
                emotion_data={"primary_emotion": "neutral"},
                cdi={"cdi_score": 0.2},
                mode="personalized",
            )
            comparison = logger.compare_modes()
            # personalized CDI (0.2) < baseline CDI (0.8) → improvement < 0
            assert comparison["cdi_improvement"] < 0.0

    def test_compare_modes_escalation_rates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="crisis",
                emotion_data={"primary_emotion": "crisis"},
                escalation={"escalation_detected": True},
                mode="baseline",
            )
            logger.log_interaction(
                user_message="okay",
                emotion_data={"primary_emotion": "neutral"},
                escalation={"escalation_detected": False},
                mode="personalized",
            )
            comparison = logger.compare_modes()
            assert comparison["escalation_rate_baseline"] == 1.0
            assert comparison["escalation_rate_personalized"] == 0.0

    def test_log_persists_across_logger_instances(self):
        """Two separate logger instances sharing the same file accumulate entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from emotion_analytics import EmotionAnalyticsLogger
            l1 = EmotionAnalyticsLogger(log_dir=tmpdir)
            l1.log_interaction(
                user_message="first",
                emotion_data={"primary_emotion": "joy"},
                mode="baseline",
            )
            l2 = EmotionAnalyticsLogger(log_dir=tmpdir)
            l2.log_interaction(
                user_message="second",
                emotion_data={"primary_emotion": "sadness"},
                mode="baseline",
            )
            entries = l2.load_logs()
            assert len(entries) == 2

    def test_extra_fields_stored(self):
        """Extra research metadata (e.g. fusion_alpha) can be attached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = self._make_logger(tmpdir)
            logger.log_interaction(
                user_message="test",
                emotion_data={"primary_emotion": "neutral"},
                mode="baseline",
                extra={"fusion_alpha": 0.65, "experiment_id": "exp_001"},
            )
            entries = logger.load_logs()
            assert entries[0]["fusion_alpha"] == 0.65
            assert entries[0]["experiment_id"] == "exp_001"

    def test_pipeline_logs_every_turn(self):
        """Each pipeline.process_turn() call produces exactly one log entry."""
        from agent_pipeline import WellnessAgentPipeline
        from emotion_analytics import EmotionAnalyticsLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EmotionAnalyticsLogger(log_dir=tmpdir)
            pipeline = WellnessAgentPipeline(analytics_logger=logger)
            pipeline.process_turn("Turn one")
            pipeline.process_turn("Turn two")
            pipeline.process_turn("Turn three")
            entries = logger.load_logs()
            assert len(entries) == 3
