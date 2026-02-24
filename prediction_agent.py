"""
Prediction agent for emotional trend forecasting.
Uses Ordinary Least Squares (OLS) linear regression on historical
sentiment values to predict the next session's emotional score.
No external ML dependencies required.
"""


class PredictionAgent:
    """Forecasts future emotional state using OLS linear regression."""

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
