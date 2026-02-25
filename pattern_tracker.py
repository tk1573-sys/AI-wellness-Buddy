"""
Pattern tracking module for monitoring emotional trends over time.
Adds moving average, emotional volatility, stability index, risk scoring,
and emotion distribution tracking.
"""

from datetime import datetime, timedelta
from collections import deque
import config


# Risk score weights for each fine-grained emotion
_EMOTION_RISK_WEIGHTS = {
    'crisis':   1.00,
    'sadness':  0.65,
    'fear':     0.60,
    'anxiety':  0.55,
    'anger':    0.45,
    'neutral':  0.10,
    'joy':      0.00,
    # Coarse-emotion fallbacks
    'distress': 0.80,
    'negative': 0.50,
    'positive': 0.00,
}


class PatternTracker:
    """Tracks emotional patterns over time and detects concerning trends"""

    def __init__(self, window_size=config.PATTERN_TRACKING_WINDOW):
        self.window_size = window_size
        self.emotion_history = deque(maxlen=window_size)
        self.sentiment_history = deque(maxlen=window_size)
        self.distress_count = 0
        self.consecutive_distress = 0

    def add_emotion_data(self, emotion_data):
        """Add new emotion analysis data to tracking history"""
        self.emotion_history.append(emotion_data)
        self.sentiment_history.append(emotion_data['polarity'])

        # Track distress patterns
        primary = emotion_data.get('primary_emotion', emotion_data.get('emotion', 'neutral'))
        is_distress = (
            emotion_data.get('is_crisis', False)
            or primary in ('crisis', 'sadness', 'fear', 'anxiety')
            or (emotion_data['emotion'] in ['distress', 'negative']
                and emotion_data['severity'] in ['medium', 'high'])
        )
        if is_distress:
            self.distress_count += 1
            self.consecutive_distress += 1
        else:
            self.consecutive_distress = 0

    def get_emotional_trend(self):
        """Calculate overall emotional trend"""
        if len(self.sentiment_history) < 2:
            return 'insufficient_data'

        recent_avg = sum(list(self.sentiment_history)[-3:]) / min(3, len(self.sentiment_history))

        if recent_avg > 0.2:
            return 'improving'
        elif recent_avg < -0.2:
            return 'declining'
        else:
            return 'stable'

    def detect_sustained_distress(self):
        """Check if sustained emotional distress is detected"""
        return self.consecutive_distress >= config.SUSTAINED_DISTRESS_COUNT

    # ------------------------------------------------------------------
    # Moving average
    # ------------------------------------------------------------------

    def get_moving_average(self, window=3):
        """
        Compute moving average of recent sentiment values.
        Returns a list of averaged values (length = max(0, n - window + 1)).
        """
        values = list(self.sentiment_history)
        if len(values) < window:
            return values[:]
        return [
            sum(values[i:i + window]) / window
            for i in range(len(values) - window + 1)
        ]

    # ------------------------------------------------------------------
    # Emotional volatility & stability index
    # ------------------------------------------------------------------

    def get_volatility_and_stability(self):
        """
        Compute emotional volatility (std-dev of sentiment) and
        stability index (1 - normalised volatility).

        Returns:
            (volatility: float 0-1, stability_index: float 0-1)
        """
        values = list(self.sentiment_history)
        if len(values) < 2:
            return 0.0, 1.0  # no data → perfectly stable

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5  # range roughly 0 – 1 for [-1, 1] inputs

        volatility = min(1.0, std_dev)
        stability_index = round(1.0 - volatility, 4)
        return round(volatility, 4), stability_index

    # ------------------------------------------------------------------
    # Emotion distribution
    # ------------------------------------------------------------------

    def get_emotion_distribution(self):
        """
        Return proportions (0.0–1.0) for each known emotion class over
        the current window.  Always includes all 7 standard classes so
        callers can rely on a consistent key set.
        Returns a dict {emotion_name: proportion}.
        """
        _ALL_EMOTIONS = ('joy', 'sadness', 'anger', 'fear', 'anxiety', 'neutral', 'crisis')
        counts = {e: 0 for e in _ALL_EMOTIONS}
        total = len(self.emotion_history)
        if total == 0:
            return {e: 0.0 for e in _ALL_EMOTIONS}
        for e in self.emotion_history:
            label = e.get('primary_emotion', e.get('emotion', 'neutral'))
            if label in counts:
                counts[label] += 1
            else:
                counts['neutral'] += 1  # bucket unknown labels as neutral
        return {e: round(counts[e] / total, 4) for e in _ALL_EMOTIONS}

    # ------------------------------------------------------------------
    # Emotional drift score
    # ------------------------------------------------------------------

    def get_emotional_drift_score(self):
        """
        Compute emotional drift: the mean per-step change in sentiment
        over the current window.  Positive = improving, negative = worsening.
        Returns a float in approximately [-1, 1].

        Mathematically equivalent to (values[-1] - values[0]) / (len(values) - 1),
        i.e. the overall rise divided by the number of steps.
        """
        values = list(self.sentiment_history)
        if len(values) < 2:
            return 0.0
        # Mean successive difference == (last - first) / (n - 1)
        drift = (values[-1] - values[0]) / (len(values) - 1)
        return round(drift, 4)

    # ------------------------------------------------------------------
    # Formula-based risk scoring
    # ------------------------------------------------------------------

    def compute_risk_score(self):
        """
        Compute a composite risk score and return a (score, level) tuple.

        Formula:
            base   = mean(emotion_weight  for each message in window)
            consec = min(0.5, consecutive_distress * 0.1)
            abuse  = 0.2  if any abuse indicators detected
            total  = min(1.0, base + consec + abuse)

        Levels:
            < 0.10  → 'info'
            < 0.20  → 'low'
            < 0.45  → 'medium'
            < 0.70  → 'high'
            >= 0.70 → 'critical'
        """
        if not self.emotion_history:
            return 0.0, 'low'

        weighted_sum = 0.0
        has_abuse = False
        for e in self.emotion_history:
            primary = e.get('primary_emotion', e.get('emotion', 'neutral'))
            weight = _EMOTION_RISK_WEIGHTS.get(primary, 0.30)
            # Crisis keyword found → escalate weight to maximum
            if e.get('is_crisis', False):
                weight = 1.0
            weighted_sum += weight
            if e.get('has_abuse_indicators', False):
                has_abuse = True

        base_score = weighted_sum / len(self.emotion_history)
        consecutive_factor = min(0.50, self.consecutive_distress * 0.10)
        abuse_boost = 0.20 if has_abuse else 0.0

        total = min(1.0, base_score + consecutive_factor + abuse_boost)

        if total < 0.10:
            level = 'info'
        elif total < 0.20:
            level = 'low'
        elif total < 0.45:
            level = 'medium'
        elif total < 0.70:
            level = 'high'
        else:
            level = 'critical'

        return round(total, 4), level

    # ------------------------------------------------------------------
    # Existing summary (updated to include new fields)
    # ------------------------------------------------------------------

    def get_pattern_summary(self):
        """Get summary of emotional patterns (backward-compatible + new fields)"""
        if not self.emotion_history:
            return None

        total_messages = len(self.emotion_history)
        distress_messages = sum(
            1 for e in self.emotion_history
            if e['emotion'] in ['distress', 'negative']
        )

        abuse_indicators_count = sum(
            1 for e in self.emotion_history
            if e.get('has_abuse_indicators', False)
        )
        crisis_count = sum(
            1 for e in self.emotion_history
            if e.get('is_crisis', False)
        )

        avg_sentiment = (
            sum(self.sentiment_history) / len(self.sentiment_history)
            if self.sentiment_history else 0
        )

        volatility, stability_index = self.get_volatility_and_stability()
        risk_score, risk_level = self.compute_risk_score()
        moving_avg = self.get_moving_average()
        emotion_distribution = self.get_emotion_distribution()

        return {
            # Backward-compatible keys
            'total_messages': total_messages,
            'distress_messages': distress_messages,
            'distress_ratio': distress_messages / total_messages,
            'abuse_indicators_detected': abuse_indicators_count > 0,
            'abuse_indicators_count': abuse_indicators_count,
            'average_sentiment': avg_sentiment,
            'trend': self.get_emotional_trend(),
            'consecutive_distress': self.consecutive_distress,
            'sustained_distress_detected': self.detect_sustained_distress(),
            # New keys
            'crisis_count': crisis_count,
            'volatility': volatility,
            'stability_index': stability_index,
            'risk_score': risk_score,
            'risk_level': risk_level,
            # Uppercase aliases (used by test_full_coverage and UI display)
            'severity_level': risk_level.upper(),
            'severity_score': risk_score,
            'moving_average': moving_avg,
            'emotion_distribution': emotion_distribution,
            'drift_score': self.get_emotional_drift_score(),
        }

    def reset_consecutive_distress(self):
        """Reset consecutive distress counter after alert"""
        self.consecutive_distress = 0
