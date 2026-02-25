"""
Prediction agent for emotional trend forecasting.
Uses Ordinary Least Squares (OLS) linear regression on historical
sentiment values to predict the next session's emotional score.
No external ML dependencies required.

Also provides:
- ``EWMAPredictor``: Exponentially Weighted Moving Average predictor
  (non-linear, recency-weighted baseline for model comparison).
- ``compare_models()``: Leave-one-out MAE/RMSE comparison of OLS vs EWMA.
"""

# Minimum slope magnitude considered a "meaningful" declining trend.
# Smaller slopes are treated as noise / stable.
_PRE_DISTRESS_SLOPE_THRESHOLD = -0.02

# Slope magnitude below which a trend is considered "stable" (not improving/worsening)
_STABLE_SLOPE_THRESHOLD = 0.05


class PredictionAgent:
    """
    Forecasts future emotional state using OLS linear regression.

    Supports two usage modes:
    - **Stateless** (pass ``history`` list to each method directly)
    - **Stateful** (call ``add_data_point()`` to build history, then call
      ``predict_next_state()`` / ``classify_trend()`` / ``get_metrics()``)
    """

    def __init__(self):
        self._history = []          # list of float sentiment values
        self._last_prediction = None  # last predict_next_state() result
        self._mae_sum = 0.0
        self._rmse_sum = 0.0
        self._n_evaluated = 0
        self._pending_actual = None  # sentiment we are waiting to evaluate against

    # ------------------------------------------------------------------
    # Stateful API (backward-compatible with test_full_coverage)
    # ------------------------------------------------------------------

    def add_data_point(self, sentiment, emotion=None):  # noqa: ARG002 (emotion unused but accepted)
        """Append a new sentiment value to the internal history buffer."""
        self._history.append(float(sentiment))
        # If there is a pending prediction, evaluate it against this actual value
        if self._pending_actual is not None:
            error = abs(self._pending_actual - float(sentiment))
            self._mae_sum += error
            self._rmse_sum += error ** 2
            self._n_evaluated += 1
            self._pending_actual = None

    def predict_next_state(self):
        """
        Run OLS forecast on the current internal history.

        Returns a dict with:
          trend (str): 'insufficient_data' | 'improving' | 'stable' | 'worsening'
          confidence (float): 0.0 (no data) or value from predict_next_sentiment
          predicted_sentiment (float | None): clamped to [-1, 1]
          early_warning (bool): True when pre-distress threshold triggered
          warning_message (str | None): message when early_warning is True
        """
        if len(self._history) < 2:
            return {
                'trend': 'insufficient_data',
                'confidence': 0.0,
                'predicted_sentiment': None,
                'early_warning': False,
                'warning_message': None,
            }

        result = self.predict_next_sentiment(self._history)
        if result is None:
            return {
                'trend': 'insufficient_data',
                'confidence': 0.0,
                'predicted_sentiment': None,
                'early_warning': False,
                'warning_message': None,
            }

        predicted = result['predicted_value']
        slope = result['trend_slope']
        conf_map = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        confidence = conf_map.get(result['confidence'], 0.3)

        trend = self.classify_trend()
        warning = self.get_pre_distress_warning(self._history)
        self._pending_actual = predicted  # store so next add_data_point can evaluate it

        return {
            'trend': trend,
            'confidence': confidence,
            'predicted_sentiment': predicted,
            'early_warning': warning is not None,
            'warning_message': warning,
        }

    def classify_trend(self):
        """
        Classify current trend as 'improving', 'worsening', or 'stable'
        based on OLS slope over the internal history.
        """
        result = self.predict_next_sentiment(self._history)
        if result is None:
            return 'insufficient_data'
        slope = result['trend_slope']
        if slope > _STABLE_SLOPE_THRESHOLD:
            return 'improving'
        if slope < -_STABLE_SLOPE_THRESHOLD:
            return 'worsening'
        return 'stable'

    def get_metrics(self):
        """Return accumulated performance metrics for the stateful session."""
        mae = self._mae_sum / self._n_evaluated if self._n_evaluated > 0 else 0.0
        rmse = (self._rmse_sum / self._n_evaluated) ** 0.5 if self._n_evaluated > 0 else 0.0
        return {
            'mae': round(mae, 6),
            'rmse': round(rmse, 6),
            'n_predictions': self._n_evaluated,
            'data_points': len(self._history),
            'trend': self.classify_trend() if len(self._history) >= 2 else 'insufficient_data',
        }

    def get_forecast_series(self, steps=3):
        """
        Predict the next ``steps`` sentiment values using OLS extrapolation.
        Returns a list of floats, each clamped to [-1.0, 1.0].
        """
        if len(self._history) < 2:
            return [0.0] * steps

        history = list(self._history)
        result = self.predict_next_sentiment(history)
        if result is None:
            return [0.0] * steps

        slope = result['trend_slope']
        n = len(history)
        x = list(range(n))
        y = history
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        denom = sum((xi - x_mean) ** 2 for xi in x)
        intercept = y_mean - slope * x_mean if denom != 0 else y_mean

        forecasts = []
        for step in range(1, steps + 1):
            pred = slope * (n - 1 + step) + intercept
            forecasts.append(max(-1.0, min(1.0, pred)))
        return forecasts

    # ------------------------------------------------------------------
    # Stateless prediction methods (original API)
    # ------------------------------------------------------------------

    def predict_next_sentiment(self, history):
        """
        Predict the next sentiment value given a list of past values.

        Args:
            history: list of float sentiment values (polarity, -1 to 1)

        Returns:
            dict with keys:
                predicted_value (float): estimated next sentiment
                trend_slope (float): slope of the regression line
                confidence (str): 'low' | 'medium' | 'high'
                interpretation (str): human-readable description
            or None if fewer than 3 data points.
        """
        if not history or len(history) < 3:
            return None

        n = len(history)
        x = list(range(n))
        y = list(history)

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            predicted = y_mean
            slope = 0.0
        else:
            slope = numerator / denominator
            intercept = y_mean - slope * x_mean
            predicted = slope * n + intercept  # predict index n (next point)

        # Clamp prediction to valid polarity range
        predicted = max(-1.0, min(1.0, predicted))

        # Confidence grows with more data points
        if n >= 10:
            confidence = 'high'
        elif n >= 5:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Human-readable interpretation
        if predicted > 0.3:
            interpretation = "Positive mood expected — keep nurturing what is working."
        elif predicted > 0.0:
            interpretation = 'Mildly positive mood expected — gentle progress ahead.'
        elif predicted > -0.3:
            interpretation = 'Neutral to slightly low mood expected — extra self-care may help.'
        else:
            interpretation = 'Low mood predicted — consider reaching out for support proactively.'

        return {
            'predicted_value': round(predicted, 4),
            'trend_slope': round(slope, 6),
            'confidence': confidence,
            'interpretation': interpretation,
            'data_points_used': n,
        }

    def predict_risk_escalation(self, risk_history):
        """
        Predict whether risk is likely to escalate given a list of past
        risk scores (float 0-1).

        Returns:
            dict with 'will_escalate' (bool), 'predicted_risk' (float),
            'recommendation' (str), or None if insufficient data.
        """
        result = self.predict_next_sentiment(risk_history)
        if result is None:
            return None

        predicted_risk = max(0.0, min(1.0, result['predicted_value']))
        will_escalate = (
            result['trend_slope'] > 0.02 and predicted_risk > 0.45
        )

        if will_escalate:
            recommendation = (
                'Risk appears to be increasing. Consider proactive check-in, '
                'reaching out to a trusted contact, or professional support.'
            )
        else:
            recommendation = (
                'Risk trend is stable or improving. Keep up self-care routines.'
            )

        return {
            'will_escalate': will_escalate,
            'predicted_risk': round(predicted_risk, 4),
            'trend_slope': result['trend_slope'],
            'confidence': result['confidence'],
            'recommendation': recommendation,
        }

    def get_pre_distress_warning(self, sentiment_history):
        """
        Generate a gentle preventive support message when sentiment is
        trending downward into the mild-negative zone (pre-distress early
        warning), before the alert system activates.

        Args:
            sentiment_history: list of float polarity values (-1 to 1)

        Returns:
            str warning message, or None if no early warning is warranted.
        """
        result = self.predict_next_sentiment(sentiment_history)
        if result is None:
            return None

        predicted = result['predicted_value']
        slope = result['trend_slope']

        # Warn only when sentiment is declining and heading into mild-negative
        # territory (-0.50 to -0.10).  Deep distress is handled by AlertSystem;
        # stable/positive trends require no action.
        if slope < _PRE_DISTRESS_SLOPE_THRESHOLD and -0.50 <= predicted < -0.10:
            return (
                "💛 I've noticed your emotional state has been shifting recently. "
                "Before things feel heavier, this might be a good time to try some "
                "gentle self-care — a short walk, reaching out to someone you trust, "
                "or simply taking a few slow breaths. I'm here with you. 💙"
            )
        return None


# ---------------------------------------------------------------------------
# EWMAPredictor — Exponentially Weighted Moving Average
# ---------------------------------------------------------------------------

class EWMAPredictor:
    """
    Exponentially Weighted Moving Average (EWMA) predictor for emotional
    sentiment sequences.

    Unlike OLS which fits a straight line to all historical points equally,
    EWMA assigns exponentially higher weight to recent observations (controlled
    by *alpha*).  This makes it more responsive to recent trend changes and
    serves as a stronger non-linear baseline in the model-comparison study.

    Parameters
    ----------
    alpha : float
        Smoothing factor ∈ (0, 1].  Higher alpha → more weight on recent
        values (faster adaptation); lower alpha → smoother (historical).
        Default 0.3 is recommended for emotional sentiment which typically
        changes gradually.

    Theoretical justification
    -------------------------
    Brown's simple exponential smoothing is equivalent to an infinite-order
    MA model with geometrically decreasing weights.  It is optimal under a
    local-level state-space model (Harvey, 1990) and is widely used for
    short-term time-series forecasting in healthcare analytics.
    """

    def __init__(self, alpha=0.3):
        if not 0 < alpha <= 1:
            raise ValueError(f"alpha must be in (0, 1], got {alpha}")
        self.alpha = alpha

    def predict_next(self, history):
        """
        One-step-ahead EWMA prediction.

        Parameters
        ----------
        history : list[float]

        Returns
        -------
        float | None
            Predicted next sentiment value, clamped to [-1, 1], or ``None``
            if fewer than 2 data points.
        """
        if not history or len(history) < 2:
            return None
        ewma = history[0]
        for v in history[1:]:
            ewma = self.alpha * v + (1 - self.alpha) * ewma
        return round(max(-1.0, min(1.0, ewma)), 4)

    def _leave_one_out_errors(self, history):
        """Yield (predicted, actual) pairs via leave-one-out on history[2:]."""
        for i in range(2, len(history)):
            pred = self.predict_next(history[:i])
            if pred is not None:
                yield pred, history[i]

    def compute_mae(self, history):
        """Leave-one-out Mean Absolute Error."""
        errors = [abs(p - a) for p, a in self._leave_one_out_errors(history)]
        return round(sum(errors) / len(errors), 4) if errors else None

    def compute_rmse(self, history):
        """Leave-one-out Root Mean Squared Error."""
        errors = [(p - a) ** 2 for p, a in self._leave_one_out_errors(history)]
        return round((sum(errors) / len(errors)) ** 0.5, 4) if errors else None


# ---------------------------------------------------------------------------
# Model comparison utility
# ---------------------------------------------------------------------------

def compare_models(history):
    """
    Compare OLS and EWMA predictors on a shared sentiment *history* using
    leave-one-out cross-validation.

    Returns
    -------
    dict with keys:
        ``ols``  — {'mae': float, 'rmse': float}
        ``ewma`` — {'mae': float, 'rmse': float}
        ``n_test_points`` — int (number of points used for evaluation)
        ``winner`` — 'ols' | 'ewma' | 'tie' (based on lower MAE)
    or ``None`` if fewer than 5 data points.

    Research use
    ------------
    This function powers Table 5.2 in the thesis (OLS vs EWMA comparison)
    and Section 3 of CONFERENCE_PAPER_1.  The comparison validates that
    OLS is a strong, interpretable baseline, while EWMA captures recent-trend
    adaptation that OLS cannot represent with a single global slope.
    """
    if not history or len(history) < 5:
        return None

    ols_agent  = PredictionAgent()
    ewma_agent = EWMAPredictor(alpha=0.3)

    ols_errors, ewma_errors = [], []
    for i in range(2, len(history)):
        window = history[:i]
        ols_r  = ols_agent.predict_next_sentiment(window)
        ewma_r = ewma_agent.predict_next(window)
        if ols_r is not None and ewma_r is not None:
            actual = history[i]
            ols_errors.append(abs(ols_r['predicted_value'] - actual))
            ewma_errors.append(abs(ewma_r - actual))

    if not ols_errors:
        return None

    ols_mae  = round(sum(ols_errors) / len(ols_errors), 4)
    ewma_mae = round(sum(ewma_errors) / len(ewma_errors), 4)
    ols_rmse  = round((sum(e ** 2 for e in ols_errors) / len(ols_errors)) ** 0.5, 4)
    ewma_rmse = round((sum(e ** 2 for e in ewma_errors) / len(ewma_errors)) ** 0.5, 4)

    if ols_mae < ewma_mae - 1e-4:
        winner = 'ols'
    elif ewma_mae < ols_mae - 1e-4:
        winner = 'ewma'
    else:
        winner = 'tie'

    return {
        'ols':  {'mae': ols_mae,  'rmse': ols_rmse},
        'ewma': {'mae': ewma_mae, 'rmse': ewma_rmse},
        'n_test_points': len(ols_errors),
        'winner': winner,
    }
