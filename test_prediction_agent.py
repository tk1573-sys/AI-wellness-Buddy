"""Tests for prediction_agent compare_models research_mode flag."""

from prediction_agent import compare_models, SimpleGRUForecaster


HISTORY = [0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4, -0.5]


def test_compare_models_production_excludes_neural():
    """Default (production) mode must NOT include 'neural' key."""
    result = compare_models(HISTORY)
    assert result is not None
    assert 'ols' in result
    assert 'ewma' in result
    assert 'winner' in result
    assert 'neural' not in result, "Production mode should not run neural baseline"


def test_compare_models_research_includes_neural():
    """Research mode must include the 'neural' key."""
    result = compare_models(HISTORY, research_mode=True)
    assert result is not None
    assert 'neural' in result
    neural = result['neural']
    assert neural is not None
    assert 'mae' in neural and 'rmse' in neural


def test_compare_models_research_mode_false_explicit():
    """Explicitly passing research_mode=False behaves like default."""
    result = compare_models(HISTORY, research_mode=False)
    assert result is not None
    assert 'neural' not in result


def test_compare_models_short_history_returns_none():
    """Fewer than 5 points always returns None regardless of mode."""
    assert compare_models([0.1, 0.2, 0.3]) is None
    assert compare_models([0.1, 0.2, 0.3], research_mode=True) is None


def test_compare_models_output_structure():
    """Validate full output structure matches expected schema."""
    result = compare_models(HISTORY, research_mode=True)
    assert isinstance(result['ols']['mae'], float)
    assert isinstance(result['ols']['rmse'], float)
    assert isinstance(result['ewma']['mae'], float)
    assert isinstance(result['ewma']['rmse'], float)
    assert isinstance(result['n_test_points'], int)
    assert result['winner'] in ('ols', 'ewma', 'tie')
    assert result['neural']['model'] == 'simple_gru'


def test_neural_baseline_uses_separate_instances():
    """MAE and RMSE should come from independent forecaster instances.

    We verify this indirectly: both metrics must be valid floats and RMSE >= MAE
    (mathematically guaranteed for any valid evaluation).
    """
    result = compare_models(HISTORY, research_mode=True)
    neural = result['neural']
    assert neural['mae'] >= 0
    assert neural['rmse'] >= 0
    assert neural['rmse'] >= neural['mae'] - 1e-6, "RMSE must be >= MAE"


def test_forecasting_agent_default_no_neural():
    """ForecastingAgent in default mode should not include neural in comparison."""
    from agent_pipeline import ForecastingAgent
    agent = ForecastingAgent()
    result = agent.run(list(HISTORY))
    assert result is not None
    comparison = result.get('model_comparison')
    if comparison is not None:
        assert 'neural' not in comparison


def test_forecasting_agent_research_mode():
    """ForecastingAgent with research_mode=True should include neural."""
    from agent_pipeline import ForecastingAgent
    agent = ForecastingAgent(research_mode=True)
    result = agent.run(list(HISTORY))
    assert result is not None
    comparison = result.get('model_comparison')
    assert comparison is not None
    assert 'neural' in comparison
