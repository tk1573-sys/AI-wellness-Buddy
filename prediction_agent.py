"""
Pattern Prediction Agent — Module 3
Temporal emotional-state modeling using sliding-window linear regression.

Research angle: Temporal distress modeling.
  • Predicts the next sentiment score using a linear trend over the recent window.
  • Classifies trend: improving / stable / worsening.
  • Provides early-warning when predicted sentiment drops below threshold.
  • Tracks MAE and RMSE for model evaluation.

Architecture note:
  A full LSTM requires training data.  This module implements the same
  prediction interface an LSTM would expose, using linear regression as the
  temporal model.  Replace _linear_predict() with an LSTM forward-pass when
  sufficient labelled data becomes available.
"""

import math
from datetime import datetime
from collections import deque
import config

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    _NUMPY_AVAILABLE = False


# ── helpers (pure-python fallback if numpy not present) ──────────────────────

def _linreg_predict(values):
    """
    Return predicted next value using Ordinary Least Squares linear regression.
    Works with plain Python lists or numpy arrays.
    """
    n = len(values)
    if n < 2:
        return values[-1] if values else 0.0
    if _NUMPY_AVAILABLE:
        x = np.arange(n, dtype=float)
        y = np.array(values, dtype=float)
        x_mean, y_mean = x.mean(), y.mean()
        num = float(np.dot(x - x_mean, y - y_mean))
        den = float(np.dot(x - x_mean, x - x_mean))
        slope = num / den if den != 0 else 0.0
        intercept = y_mean - slope * x_mean
        return slope * n + intercept        # predict step n (next)
    else:
        # Pure-python fallback
        x_mean = (n - 1) / 2.0
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0.0
        intercept = y_mean - slope * x_mean
        return slope * n + intercept


class PredictionAgent:
    """
    Predicts the user's next emotional state and issues early warnings.

    Public interface (mirrors an LSTM prediction module):
      add_data_point(sentiment, emotion_label, timestamp)
      predict_next_state()  → {predicted_sentiment, trend, confidence, warning}
      get_metrics()         → {mae, rmse, trend_accuracy, n_predictions}
    """

    TREND_LABELS = ('improving', 'stable', 'worsening')

    def __init__(
        self,
        window_size: int = config.PREDICTION_WINDOW,
        warning_threshold: float = config.EARLY_WARNING_THRESHOLD,
        min_confidence: float = config.PREDICTION_CONFIDENCE_MIN,
    ):
        self.window_size = window_size
        self.warning_threshold = warning_threshold
        self.min_confidence = min_confidence

        self._sentiment_buf: deque = deque(maxlen=window_size + 1)
        self._emotion_buf: deque = deque(maxlen=window_size + 1)
        self._timestamps: deque = deque(maxlen=window_size + 1)
        self._predictions: list = []   # list of (predicted, actual) tuples

        # Running metric accumulators
        self._mae_sum: float = 0.0
        self._mse_sum: float = 0.0
        self._n_preds: int = 0
        self._trend_correct: int = 0

    # ── Data ingestion ────────────────────────────────────────────────────────

    def add_data_point(self, sentiment: float, emotion_label: str = 'neutral',
                       timestamp: datetime = None):
        """Add one observation.  Evaluates the previous prediction if present."""
        ts = timestamp or datetime.now()

        # If we already have a prediction pending, evaluate it
        if self._predictions and self._predictions[-1][1] is None:
            pred_val = self._predictions[-1][0]
            # Store (predicted, actual)
            self._predictions[-1] = (pred_val, sentiment)
            err = abs(pred_val - sentiment)
            self._mae_sum += err
            self._mse_sum += err ** 2
            self._n_preds += 1

        self._sentiment_buf.append(sentiment)
        self._emotion_buf.append(emotion_label)
        self._timestamps.append(ts)

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict_next_state(self):
        """
        Predict the next emotional state.

        Returns a dict:
          predicted_sentiment  float   – predicted polarity score
          trend                str     – 'improving' | 'stable' | 'worsening'
          confidence           float   – 0-1 confidence estimate
          early_warning        bool    – True if predicted sentiment < threshold
          warning_message      str     – human-readable warning or None
        """
        buf = list(self._sentiment_buf)
        n = len(buf)

        if n < 2:
            return {
                'predicted_sentiment': buf[-1] if buf else 0.0,
                'trend': 'insufficient_data',
                'confidence': 0.0,
                'early_warning': False,
                'warning_message': None,
            }

        predicted = _linreg_predict(buf)
        predicted = max(-1.0, min(1.0, predicted))   # clamp to [-1, 1]

        # Trend based on slope (compare mean of first half vs second half)
        mid = max(1, n // 2)
        first_half_mean = sum(buf[:mid]) / mid
        second_half_mean = sum(buf[mid:]) / (n - mid)
        delta = second_half_mean - first_half_mean

        if delta > 0.1:
            trend = 'improving'
        elif delta < -0.1:
            trend = 'worsening'
        else:
            trend = 'stable'

        # Confidence: inversely proportional to variance
        if _NUMPY_AVAILABLE:
            import numpy as np
            variance = float(np.var(buf))
        else:
            mean_val = sum(buf) / n
            variance = sum((v - mean_val) ** 2 for v in buf) / n
        confidence = max(0.0, min(1.0, 1.0 - variance))

        early_warning = (predicted < self.warning_threshold
                         and confidence >= self.min_confidence)

        warning_message = None
        if early_warning:
            warning_message = (
                "📊 Early warning: your emotional state is predicted to worsen. "
                "Consider reaching out to a trusted person or professional support."
            )
        elif trend == 'worsening' and confidence >= self.min_confidence:
            warning_message = (
                "📈 Your recent messages show a declining trend. "
                "I'm here if you'd like to talk more."
            )

        # Log prediction for metric evaluation
        self._predictions.append((predicted, None))   # actual filled next call

        return {
            'predicted_sentiment': round(predicted, 4),
            'trend': trend,
            'confidence': round(confidence, 4),
            'early_warning': early_warning,
            'warning_message': warning_message,
        }

    def classify_trend(self):
        """Simple trend label without a full prediction."""
        buf = list(self._sentiment_buf)
        n = len(buf)
        if n < 2:
            return 'insufficient_data'
        mid = max(1, n // 2)
        delta = (sum(buf[mid:]) / (n - mid)) - (sum(buf[:mid]) / mid)
        if delta > 0.1:
            return 'improving'
        elif delta < -0.1:
            return 'worsening'
        return 'stable'

    # ── Metrics (for research evaluation) ────────────────────────────────────

    def get_metrics(self):
        """
        Return evaluation metrics for the prediction model.

        Returns:
          mae          – Mean Absolute Error (lower is better)
          rmse         – Root Mean Squared Error (lower is better)
          n_predictions – number of evaluated predictions
          trend        – current trend classification
          data_points  – observations collected so far
        """
        mae = (self._mae_sum / self._n_preds) if self._n_preds > 0 else None
        rmse = (math.sqrt(self._mse_sum / self._n_preds)
                if self._n_preds > 0 else None)
        return {
            'mae': round(mae, 4) if mae is not None else None,
            'rmse': round(rmse, 4) if rmse is not None else None,
            'n_predictions': self._n_preds,
            'trend': self.classify_trend(),
            'data_points': len(self._sentiment_buf),
        }

    def get_forecast_series(self, steps=5):
        """
        Generate a short forecast series (next `steps` sentiment values).
        Useful for plotting a forecast line in the UI.
        """
        buf = list(self._sentiment_buf)
        if len(buf) < 2:
            return []
        forecasts = []
        current_buf = buf.copy()
        for _ in range(steps):
            next_val = _linreg_predict(current_buf[-self.window_size:])
            next_val = max(-1.0, min(1.0, next_val))
            forecasts.append(round(next_val, 4))
            current_buf.append(next_val)
        return forecasts
