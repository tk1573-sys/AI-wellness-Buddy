"""Tests for emotional trend forecasting.

Validates:
- OLS forecasting works
- EWMA forecasting works
- Neural forecasting only runs in research_mode
- MAE and RMSE values are returned
"""

from prediction_agent import PredictionAgent, compare_models


# Synthetic sentiment history used across tests
_HISTORY = [-0.2, -0.3, -0.4, -0.1, 0.1]
# Longer history needed for neural baseline to produce results
_LONG_HISTORY = [-0.2, -0.3, -0.4, -0.1, 0.1, -0.2, -0.3, 0.0, 0.2, 0.1]


# ------------------------------------------------------------------
# OLS forecasting
# ------------------------------------------------------------------

def test_ols_forecasting_works():
    """OLS predictor must return a dict with predicted_value."""
    agent = PredictionAgent()
    result = agent.predict_next_sentiment(_HISTORY)
    assert result is not None
    assert isinstance(result, dict)
    assert 'predicted_value' in result
    assert isinstance(result['predicted_value'], (int, float))


def test_ols_prediction_in_range():
    """OLS predicted_value should be a plausible sentiment value."""
    agent = PredictionAgent()
    result = agent.predict_next_sentiment(_HISTORY)
    assert -2.0 <= result['predicted_value'] <= 2.0


# ------------------------------------------------------------------
# EWMA forecasting
# ------------------------------------------------------------------

def test_ewma_forecasting_works():
    """compare_models must include EWMA metrics."""
    result = compare_models(_HISTORY, research_mode=False)
    assert result is not None
    assert 'ewma' in result


def test_ewma_metrics_returned():
    """EWMA entry must contain MAE and RMSE."""
    result = compare_models(_HISTORY, research_mode=False)
    ewma = result['ewma']
    assert 'mae' in ewma
    assert 'rmse' in ewma
    assert isinstance(ewma['mae'], (int, float))
    assert isinstance(ewma['rmse'], (int, float))


# ------------------------------------------------------------------
# Neural forecasting (research mode only)
# ------------------------------------------------------------------

def test_neural_excluded_from_production_mode():
    """Production mode must NOT include neural model results."""
    result = compare_models(_HISTORY, research_mode=False)
    assert 'neural' not in result


def test_neural_included_in_research_mode():
    """Research mode must include neural model results."""
    result = compare_models(_HISTORY, research_mode=True)
    assert 'neural' in result


def test_neural_metrics_returned():
    """Neural model must return MAE and RMSE (needs longer history)."""
    result = compare_models(_LONG_HISTORY, research_mode=True)
    neural = result['neural']
    assert neural is not None, "Neural requires >=8 data points"
    assert 'mae' in neural
    assert 'rmse' in neural


# ------------------------------------------------------------------
# General metrics
# ------------------------------------------------------------------

def test_mae_and_rmse_returned_for_ols():
    """OLS entry must contain MAE and RMSE."""
    result = compare_models(_HISTORY, research_mode=False)
    ols = result['ols']
    assert 'mae' in ols
    assert 'rmse' in ols
    assert ols['rmse'] >= 0
    assert ols['mae'] >= 0


def test_short_history_returns_none():
    """History with fewer than 5 points should return None."""
    result = compare_models([-0.1, 0.2, 0.3], research_mode=False)
    assert result is None


def test_compare_models_has_winner():
    """compare_models must declare a winner."""
    result = compare_models(_HISTORY, research_mode=False)
    assert 'winner' in result
