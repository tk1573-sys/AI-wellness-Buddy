"""
Tests for the research-grade architecture upgrades.

Covers:
- Emotion fusion weights (0.75/0.25)
- Clinical Distress Index (CDI)
- Intervention Engine
- Temporal emotion tracking (rolling average, emotion volatility)
- Session memory coping_tools_used field
- Explainability fused_score field
- CDI gauge chart
- Data store session log
- Agent pipeline CDI + intervention integration
"""

import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

import pytest
from emotion_analyzer import EmotionAnalyzer
from pattern_tracker import PatternTracker
from clinical_indicators import compute_cdi, compute_clinical_indicators
from intervention_engine import InterventionEngine
from explainability import generate_explanation
from session_manager import SessionManager
from data_store import DataStore


# ---------------------------------------------------------------------------
# 1. Emotion Fusion Weights
# ---------------------------------------------------------------------------

class TestEmotionFusionWeights:
    def test_transformer_weight_is_075(self):
        assert EmotionAnalyzer._TRANSFORMER_WEIGHT == 0.75

    def test_heuristic_weight_is_025(self):
        assert EmotionAnalyzer._HEURISTIC_WEIGHT == 0.25

    def test_weights_sum_to_one(self):
        assert abs(EmotionAnalyzer._TRANSFORMER_WEIGHT + EmotionAnalyzer._HEURISTIC_WEIGHT - 1.0) < 1e-9

    def test_classify_returns_emotion_probabilities(self):
        ea = EmotionAnalyzer()
        result = ea.classify_emotion("I feel happy today")
        assert 'emotion_probabilities' in result
        assert 'emotion_confidence' in result
        # Probabilities should sum approximately to 1
        total = sum(result['emotion_probabilities'].values())
        assert abs(total - 1.0) < 0.02

    def test_crisis_overrides_other_emotions(self):
        ea = EmotionAnalyzer()
        result = ea.classify_emotion("I want to kill myself")
        assert result['is_crisis'] is True
        assert result['primary_emotion'] == 'crisis'
        assert result['concern_level'] == 'critical'


# ---------------------------------------------------------------------------
# 2. Temporal Emotion Tracking
# ---------------------------------------------------------------------------

class TestTemporalTracking:
    def _make_entry(self, emotion, prob=0.7, polarity=-0.3):
        return {
            'emotion': 'negative' if emotion != 'joy' else 'positive',
            'primary_emotion': emotion,
            'emotion_probabilities': {
                'joy': 0.0, 'sadness': 0.0, 'anger': 0.0,
                'fear': 0.0, 'anxiety': 0.0, 'neutral': 0.0, 'crisis': 0.0,
                emotion: prob,
            },
            'polarity': polarity,
            'severity': 'medium',
            'is_crisis': False,
            'has_abuse_indicators': False,
        }

    def test_rolling_emotion_average_empty(self):
        pt = PatternTracker()
        avg = pt.get_rolling_emotion_average()
        assert avg['joy'] == 0.0
        assert avg['sadness'] == 0.0

    def test_rolling_emotion_average_single_entry(self):
        pt = PatternTracker()
        pt.add_emotion_data(self._make_entry('sadness', 0.8))
        avg = pt.get_rolling_emotion_average()
        assert avg['sadness'] == 0.8

    def test_rolling_emotion_average_multiple(self):
        pt = PatternTracker()
        pt.add_emotion_data(self._make_entry('sadness', 0.6))
        pt.add_emotion_data(self._make_entry('sadness', 0.8))
        avg = pt.get_rolling_emotion_average()
        assert abs(avg['sadness'] - 0.7) < 0.01

    def test_emotion_volatility_empty(self):
        pt = PatternTracker()
        assert pt.get_emotion_volatility() == 0.0

    def test_emotion_volatility_single(self):
        pt = PatternTracker()
        pt.add_emotion_data(self._make_entry('sadness', 0.8))
        assert pt.get_emotion_volatility() == 0.0

    def test_emotion_volatility_varied(self):
        pt = PatternTracker()
        pt.add_emotion_data(self._make_entry('sadness', 0.9))
        pt.add_emotion_data(self._make_entry('joy', 0.3, polarity=0.5))
        pt.add_emotion_data(self._make_entry('sadness', 0.8))
        vol = pt.get_emotion_volatility()
        assert vol > 0.0  # There should be some volatility

    def test_pattern_summary_includes_temporal_fields(self):
        pt = PatternTracker()
        pt.add_emotion_data(self._make_entry('sadness', 0.7))
        summary = pt.get_pattern_summary()
        assert 'rolling_emotion_average' in summary
        assert 'emotion_volatility' in summary
        assert isinstance(summary['rolling_emotion_average'], dict)
        assert isinstance(summary['emotion_volatility'], float)


# ---------------------------------------------------------------------------
# 3. Clinical Distress Index (CDI)
# ---------------------------------------------------------------------------

class TestCDI:
    def test_cdi_low_for_positive(self):
        emotion_data = {
            'emotion_probabilities': {'joy': 0.9, 'sadness': 0.02, 'anxiety': 0.02,
                                       'fear': 0.02, 'anger': 0.02, 'neutral': 0.02},
            'distress_keywords': [],
        }
        result = compute_cdi(emotion_data)
        assert result['cdi_level'] == 'low'
        assert result['cdi_score'] < 0.3

    def test_cdi_high_for_distressed(self):
        emotion_data = {
            'emotion_probabilities': {'sadness': 0.6, 'anxiety': 0.3, 'fear': 0.05,
                                       'anger': 0.02, 'joy': 0.01, 'neutral': 0.02},
            'distress_keywords': ['hopeless', 'alone', 'worthless', 'depressed'],
        }
        ci = {
            'emotional_volatility': 0.6,
            'sustained_sadness': True,
        }
        result = compute_cdi(emotion_data, ci)
        assert result['cdi_level'] in ('high', 'critical')
        assert result['cdi_score'] > 0.5

    def test_cdi_returns_components(self):
        emotion_data = {
            'emotion_probabilities': {'sadness': 0.5, 'anxiety': 0.2},
            'distress_keywords': ['sad'],
        }
        result = compute_cdi(emotion_data)
        assert 'cdi_components' in result
        comp = result['cdi_components']
        assert 'negative_emotion_probability' in comp
        assert 'distress_keyword_density' in comp
        assert 'emotion_volatility' in comp
        assert 'sustained_sadness' in comp

    def test_cdi_includes_disclaimer(self):
        result = compute_cdi({'emotion_probabilities': {}, 'distress_keywords': []})
        assert 'disclaimer' in result

    def test_cdi_moderate_level(self):
        emotion_data = {
            'emotion_probabilities': {'sadness': 0.4, 'anxiety': 0.3, 'fear': 0.1,
                                       'anger': 0.05, 'joy': 0.05, 'neutral': 0.1},
            'distress_keywords': ['sad'],
        }
        ci = {'emotional_volatility': 0.2, 'sustained_sadness': False}
        result = compute_cdi(emotion_data, ci)
        assert result['cdi_level'] in ('low', 'moderate')

    def test_cdi_score_capped_at_one(self):
        emotion_data = {
            'emotion_probabilities': {'sadness': 0.9, 'anxiety': 0.9, 'fear': 0.9, 'anger': 0.9},
            'distress_keywords': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
        ci = {'emotional_volatility': 1.0, 'sustained_sadness': True}
        result = compute_cdi(emotion_data, ci)
        assert result['cdi_score'] <= 1.0


# ---------------------------------------------------------------------------
# 4. Intervention Engine
# ---------------------------------------------------------------------------

class TestInterventionEngine:
    def setup_method(self):
        self.engine = InterventionEngine()

    def test_low_risk_returns_empathetic_response(self):
        result = self.engine.recommend('low', 'neutral')
        assert result['level'] == 'low'
        assert 'empathetic_response' in result['actions']
        assert result['resources'] is None
        assert result['coping_tools'] == []

    def test_moderate_risk_returns_grounding(self):
        result = self.engine.recommend('moderate', 'anxiety')
        assert result['level'] == 'moderate'
        assert 'grounding_suggestion' in result['actions']
        assert len(result['coping_tools']) >= 1

    def test_medium_normalised_to_moderate(self):
        result = self.engine.recommend('medium', 'sadness')
        assert result['level'] == 'moderate'

    def test_high_risk_returns_breathing(self):
        result = self.engine.recommend('high', 'anxiety')
        assert result['level'] == 'high'
        assert 'breathing_exercise' in result['actions']
        assert 'supportive_message' in result['actions']
        assert result['supportive_message'] is not None

    def test_critical_risk_returns_crisis_resources(self):
        result = self.engine.recommend('critical', 'crisis')
        assert result['level'] == 'critical'
        assert 'crisis_response' in result['actions']
        assert result['resources'] is not None
        assert '988' in result['resources']['hotline']

    def test_crisis_emotion_triggers_critical(self):
        result = self.engine.recommend('low', 'crisis')
        assert result['level'] == 'critical'

    def test_anxiety_escalation_adds_calming_prompt(self):
        ci = {'anxiety_escalation': True}
        result = self.engine.recommend('moderate', 'anxiety', ci)
        assert 'calming_prompt' in result['actions']

    def test_social_withdrawal_adds_connection(self):
        ci = {'social_withdrawal': True}
        result = self.engine.recommend('high', 'sadness', ci)
        assert 'connection_suggestion' in result['actions']

    def test_none_risk_defaults_to_low(self):
        result = self.engine.recommend(None, 'neutral')
        assert result['level'] == 'low'


# ---------------------------------------------------------------------------
# 5. Explainability fused_score
# ---------------------------------------------------------------------------

class TestExplainabilityFusedScore:
    def test_fused_score_present(self):
        result = generate_explanation(
            "I feel sad",
            {'primary_emotion': 'sadness', 'emotion_probabilities': {'sadness': 0.8},
             'polarity': -0.5, 'subjectivity': 0.7},
            transformer_available=True,
        )
        assert 'fused_score' in result

    def test_fused_score_transformer_weights(self):
        result = generate_explanation(
            "I feel sad",
            {'primary_emotion': 'sadness', 'emotion_probabilities': {'sadness': 0.8},
             'polarity': -0.5, 'subjectivity': 0.7},
            transformer_available=True,
        )
        assert result['fused_score']['transformer_weight'] == 0.75
        assert result['fused_score']['keyword_weight'] == 0.25

    def test_fused_score_keyword_only(self):
        result = generate_explanation(
            "I feel sad",
            {'primary_emotion': 'sadness', 'emotion_probabilities': {'sadness': 0.8},
             'polarity': -0.5, 'subjectivity': 0.7},
            transformer_available=False,
        )
        assert result['fused_score']['transformer_weight'] == 0.0
        assert result['fused_score']['keyword_weight'] == 1.0


# ---------------------------------------------------------------------------
# 6. Session Memory – coping_tools_used
# ---------------------------------------------------------------------------

class TestSessionCopingTools:
    def test_create_session_includes_coping_tools(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ds = DataStore(data_dir=tmpdir)
            mgr = SessionManager(ds)
            session = mgr.create_session("test_user")
            assert 'coping_tools_used' in session
            assert session['coping_tools_used'] == []

    def test_save_and_load_coping_tools(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ds = DataStore(data_dir=tmpdir)
            mgr = SessionManager(ds)
            mgr.create_session("test_user")
            mgr.save_session("test_user", coping_tools_used=["breathing_exercise"])
            loaded = mgr.load_session("test_user")
            assert loaded['coping_tools_used'] == ["breathing_exercise"]


# ---------------------------------------------------------------------------
# 7. CDI Gauge Chart
# ---------------------------------------------------------------------------

class TestCDIGauge:
    def test_cdi_gauge_returns_figure(self):
        from ui.charts import create_cdi_gauge
        fig = create_cdi_gauge(0.45, 'moderate')
        assert fig is not None
        # Should be a plotly Figure
        assert hasattr(fig, 'update_layout')

    def test_cdi_gauge_all_levels(self):
        from ui.charts import create_cdi_gauge
        for level in ('low', 'moderate', 'high', 'critical'):
            fig = create_cdi_gauge(0.5, level)
            assert fig is not None


# ---------------------------------------------------------------------------
# 8. Data Store Session Log
# ---------------------------------------------------------------------------

class TestDataStoreSessionLog:
    def test_save_session_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ds = DataStore(data_dir=tmpdir)
            entry = {
                'timestamp': '2026-01-01T00:00:00',
                'message': 'I feel sad',
                'emotion': 'sadness',
                'confidence': 0.85,
                'risk_level': 'medium',
            }
            ds.save_session_log('test_user', entry)
            log_file = os.path.join(tmpdir, 'test_user_session_data.json')
            assert os.path.exists(log_file)
            with open(log_file) as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]['emotion'] == 'sadness'

    def test_save_session_log_appends(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ds = DataStore(data_dir=tmpdir)
            for i in range(3):
                ds.save_session_log('test_user', {'message': f'msg {i}'})
            log_file = os.path.join(tmpdir, 'test_user_session_data.json')
            with open(log_file) as f:
                data = json.load(f)
            assert len(data) == 3


# ---------------------------------------------------------------------------
# 9. Agent Pipeline CDI + Intervention Integration
# ---------------------------------------------------------------------------

class TestAgentPipelineCDI:
    def test_pipeline_returns_cdi(self):
        from agent_pipeline import WellnessAgentPipeline
        pipeline = WellnessAgentPipeline()
        result = pipeline.process_turn("I feel very sad and lonely")
        assert 'cdi' in result
        assert 'cdi_score' in result['cdi']
        assert 'cdi_level' in result['cdi']

    def test_pipeline_returns_interventions(self):
        from agent_pipeline import WellnessAgentPipeline
        pipeline = WellnessAgentPipeline()
        result = pipeline.process_turn("I feel okay today")
        assert 'interventions' in result
        assert 'level' in result['interventions']
        assert 'actions' in result['interventions']


# ---------------------------------------------------------------------------
# 10. Wellness Buddy CDI + Intervention Integration
# ---------------------------------------------------------------------------

class TestWellnessBuddyCDI:
    def test_metadata_includes_cdi(self):
        from wellness_buddy import WellnessBuddy
        from user_profile import UserProfile
        with tempfile.TemporaryDirectory() as tmpdir:
            buddy = WellnessBuddy(data_dir=tmpdir)
            buddy.session_active = True
            buddy.user_profile = UserProfile("test_user")
            # Process a message directly
            buddy.process_message("I feel so sad and hopeless")
            meta = buddy.get_last_response_metadata()
            assert 'cdi' in meta
            assert 'interventions' in meta
