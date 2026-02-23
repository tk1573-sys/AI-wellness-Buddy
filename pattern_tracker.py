"""
Distress Monitoring Agent — Module 2
Sliding window analysis with time-based weighting and severity scoring.
"""

from datetime import datetime, timedelta
from collections import deque
import config


class PatternTracker:
    """
    Tracks emotional patterns over time and detects concerning trends.

    Upgrades over legacy version:
      • Time-weighted sliding window (recent messages count more)
      • Numeric severity score (0-10)
      • Multi-emotion distribution tracking
    """

    def __init__(self, window_size=config.PATTERN_TRACKING_WINDOW):
        self.window_size = window_size
        self.emotion_history = deque(maxlen=window_size)
        self.sentiment_history = deque(maxlen=window_size)
        self.severity_history = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        self.distress_count = 0
        self.consecutive_distress = 0

    # ── Add data ──────────────────────────────────────────────────────────────

    def add_emotion_data(self, emotion_data):
        """Add new emotion analysis data to tracking history."""
        self.emotion_history.append(emotion_data)
        self.sentiment_history.append(emotion_data['polarity'])
        self.severity_history.append(emotion_data.get('severity_score', 5.0))
        self.timestamps.append(emotion_data.get('timestamp', datetime.now()))

        if (emotion_data['emotion'] in ['distress', 'negative']
                and emotion_data['severity'] in ['medium', 'high']):
            self.distress_count += 1
            self.consecutive_distress += 1
        else:
            self.consecutive_distress = 0

    # ── Time-weighted helpers ─────────────────────────────────────────────────

    def _time_weighted_sentiment(self):
        """
        Compute exponentially time-weighted average sentiment.
        More recent messages get higher weight (decay = TIME_DECAY_FACTOR).
        """
        history = list(self.sentiment_history)
        if not history:
            return 0.0
        decay = config.TIME_DECAY_FACTOR
        weights = [decay ** (len(history) - 1 - i) for i in range(len(history))]
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(history, weights))
        return weighted_sum / total_weight

    def _weighted_severity_score(self):
        """
        Sliding window severity score (0-10) with time decay.
        Uses the SEVERITY_SCORE_WINDOW most recent entries.
        """
        window = list(self.severity_history)[-config.SEVERITY_SCORE_WINDOW:]
        if not window:
            return 0.0
        decay = config.TIME_DECAY_FACTOR
        weights = [decay ** (len(window) - 1 - i) for i in range(len(window))]
        total_weight = sum(weights)
        return round(sum(s * w for s, w in zip(window, weights)) / total_weight, 2)

    # ── Trend & distress detection ────────────────────────────────────────────

    def get_emotional_trend(self):
        """Calculate overall emotional trend using time-weighted sentiment."""
        if len(self.sentiment_history) < 2:
            return 'insufficient_data'
        recent_avg = self._time_weighted_sentiment()
        if recent_avg > 0.2:
            return 'improving'
        elif recent_avg < -0.2:
            return 'declining'
        return 'stable'

    def detect_sustained_distress(self):
        """Check if sustained emotional distress is detected."""
        return self.consecutive_distress >= config.SUSTAINED_DISTRESS_COUNT

    def get_severity_level(self):
        """Map numeric severity score to named level."""
        score = self._weighted_severity_score()
        if score >= config.SEVERITY_HIGH_THRESHOLD:
            return 'HIGH'
        elif score >= config.SEVERITY_MEDIUM_THRESHOLD:
            return 'MEDIUM'
        return 'LOW'

    # ── Emotion distribution ──────────────────────────────────────────────────

    def get_emotion_distribution(self):
        """
        Aggregate emotion_scores across the window.
        Returns dict {joy, sadness, anxiety, anger, neutral} with averages.
        """
        categories = ['joy', 'sadness', 'anxiety', 'anger', 'neutral']
        totals = {c: 0.0 for c in categories}
        count = 0
        for entry in self.emotion_history:
            scores = entry.get('emotion_scores')
            if scores:
                for c in categories:
                    totals[c] += scores.get(c, 0.0)
                count += 1
        if count == 0:
            return {c: 0.0 for c in categories}
        return {c: round(totals[c] / count, 4) for c in categories}

    # ── Summary ───────────────────────────────────────────────────────────────

    def get_pattern_summary(self):
        """Get full summary of emotional patterns (backward-compatible + new fields)."""
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
        avg_sentiment = (sum(self.sentiment_history) / len(self.sentiment_history)
                         if self.sentiment_history else 0)

        return {
            # ── legacy fields ─────────────────────────────────────────────
            'total_messages': total_messages,
            'distress_messages': distress_messages,
            'distress_ratio': distress_messages / total_messages,
            'abuse_indicators_detected': abuse_indicators_count > 0,
            'abuse_indicators_count': abuse_indicators_count,
            'average_sentiment': avg_sentiment,
            'trend': self.get_emotional_trend(),
            'consecutive_distress': self.consecutive_distress,
            'sustained_distress_detected': self.detect_sustained_distress(),
            # ── new fields ────────────────────────────────────────────────
            'weighted_sentiment': round(self._time_weighted_sentiment(), 4),
            'severity_score': self._weighted_severity_score(),    # float 0-10
            'severity_level': self.get_severity_level(),           # LOW/MEDIUM/HIGH
            'emotion_distribution': self.get_emotion_distribution(),
        }

    def reset_consecutive_distress(self):
        """Reset consecutive distress counter after alert."""
        self.consecutive_distress = 0
