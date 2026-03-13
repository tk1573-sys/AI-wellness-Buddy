"""Tests for the complete agent pipeline.

Validates:
- Pipeline instantiation
- Full process_turn execution
- Output structure (emotion, pattern, forecasting, alert, response)
"""

from agent_pipeline import (
    WellnessAgentPipeline,
    EmotionAnalysisAgent,
    PatternTrackingAgent,
    ForecastingAgent,
    AlertDecisionAgent,
    ResponseGenerationAgent,
)


# ------------------------------------------------------------------
# Individual agent instantiation
# ------------------------------------------------------------------

def test_emotion_analysis_agent_runs():
    """EmotionAnalysisAgent must classify a message."""
    agent = EmotionAnalysisAgent()
    result = agent.run("I feel anxious about work tomorrow.")
    assert isinstance(result, dict)
    assert 'primary_emotion' in result


def test_pattern_tracking_agent_runs():
    """PatternTrackingAgent must return a pattern summary."""
    agent = PatternTrackingAgent()
    emotion_data = {
        'emotion': 'anxiety',
        'primary_emotion': 'anxiety',
        'polarity': -0.3,
        'severity': 'medium',
    }
    result = agent.run(emotion_data)
    assert isinstance(result, dict)


def test_forecasting_agent_handles_empty():
    """ForecastingAgent must return None for empty history."""
    agent = ForecastingAgent()
    result = agent.run([])
    assert result is None


def test_response_generation_agent_runs():
    """ResponseGenerationAgent must produce a response string."""
    agent = ResponseGenerationAgent()
    emotion_data = {
        'emotion': 'anxiety',
        'primary_emotion': 'anxiety',
        'polarity': -0.3,
        'severity': 'medium',
    }
    result = agent.run("I feel anxious about work tomorrow.", emotion_data)
    assert isinstance(result, str)
    assert len(result) > 0


# ------------------------------------------------------------------
# Full pipeline
# ------------------------------------------------------------------

def test_pipeline_instantiation():
    """WellnessAgentPipeline must instantiate without errors."""
    pipeline = WellnessAgentPipeline()
    assert pipeline is not None
    assert pipeline.emotion_agent is not None
    assert pipeline.pattern_agent is not None
    assert pipeline.forecast_agent is not None
    assert pipeline.alert_agent is not None
    assert pipeline.response_agent is not None


def test_pipeline_process_turn_completes():
    """process_turn must complete without errors."""
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel anxious about work tomorrow.")
    assert isinstance(result, dict)


def test_pipeline_output_has_emotion():
    """Pipeline output must include emotion data."""
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel anxious about work tomorrow.")
    assert 'emotion' in result
    assert isinstance(result['emotion'], dict)
    assert 'primary_emotion' in result['emotion']


def test_pipeline_output_has_patterns():
    """Pipeline output must include pattern summary."""
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel anxious about work tomorrow.")
    assert 'patterns' in result
    assert isinstance(result['patterns'], dict)


def test_pipeline_output_has_forecasting():
    """Pipeline output must include forecasting (may be None on first turn)."""
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel anxious about work tomorrow.")
    assert 'forecasting' in result


def test_pipeline_output_has_alert():
    """Pipeline output must include alert field."""
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel anxious about work tomorrow.")
    assert 'alert' in result


def test_pipeline_output_has_response():
    """Pipeline output must include a text response."""
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel anxious about work tomorrow.")
    assert 'response' in result
    assert isinstance(result['response'], str)
    assert len(result['response']) > 0


def test_pipeline_multiple_turns():
    """Pipeline must handle multiple sequential turns."""
    pipeline = WellnessAgentPipeline()
    for msg in ["I feel sad today", "Work was stressful", "I'm a bit better now"]:
        result = pipeline.process_turn(msg)
        assert 'emotion' in result
        assert 'response' in result
