"""Tests for chat flow improvements, escalation detection, and response anti-repetition.

Validates:
  - detect_escalation() triggers on 4+ consecutive negative emotions
  - detect_escalation() does NOT trigger for mixed emotions
  - detect_escalation() handles edge cases (empty history, short history)
  - EmpatheticResponder includes validation phrases in responses
  - EmpatheticResponder caps supportive templates at 2 per response
  - EmpatheticResponder avoids repeating responses within 3-message window
  - Intervention engine integration into wellness_buddy metadata
  - CDI gauge import works
"""

import pytest

from clinical_indicators import detect_escalation
from empathetic_responder import (
    EmpatheticResponder,
    EMPATHY_PHRASES,
    VALIDATION_PHRASES,
    SUPPORT_PHRASES,
    HIGH_CONCERN_DEEPENERS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def responder():
    return EmpatheticResponder()


# ---------------------------------------------------------------------------
# 1. Escalation detection
# ---------------------------------------------------------------------------


class TestEscalationDetection:
    """Tests for detect_escalation()."""

    def test_triggers_on_four_negative(self):
        history = [
            {"emotion": "sadness"},
            {"emotion": "anxiety"},
            {"emotion": "fear"},
            {"emotion": "sadness"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is True
        assert result["warning"] is not None
        assert "escalating" in result["warning"].lower()

    def test_no_trigger_mixed_emotions(self):
        history = [
            {"emotion": "sadness"},
            {"emotion": "joy"},
            {"emotion": "fear"},
            {"emotion": "sadness"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is False
        assert result["warning"] is None

    def test_no_trigger_short_history(self):
        history = [
            {"emotion": "sadness"},
            {"emotion": "anxiety"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is False

    def test_no_trigger_empty_history(self):
        result = detect_escalation([])
        assert result["escalation_detected"] is False
        assert result["warning"] is None

    def test_triggers_with_crisis(self):
        history = [
            {"emotion": "crisis"},
            {"emotion": "sadness"},
            {"emotion": "fear"},
            {"emotion": "anxiety"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is True

    def test_custom_window(self):
        history = [
            {"emotion": "sadness"},
            {"emotion": "anxiety"},
        ]
        result = detect_escalation(history, window=2)
        assert result["escalation_detected"] is True

    def test_only_last_window_matters(self):
        history = [
            {"emotion": "joy"},
            {"emotion": "joy"},
            {"emotion": "sadness"},
            {"emotion": "anxiety"},
            {"emotion": "fear"},
            {"emotion": "anger"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is True

    def test_neutral_breaks_escalation(self):
        history = [
            {"emotion": "sadness"},
            {"emotion": "neutral"},
            {"emotion": "fear"},
            {"emotion": "anxiety"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is False

    def test_stress_counts_as_negative(self):
        history = [
            {"emotion": "stress"},
            {"emotion": "stress"},
            {"emotion": "anxiety"},
            {"emotion": "sadness"},
        ]
        result = detect_escalation(history)
        assert result["escalation_detected"] is True


# ---------------------------------------------------------------------------
# 2. Response anti-repetition
# ---------------------------------------------------------------------------

class TestResponseAntiRepetition:
    """Tests for EmpatheticResponder improvements."""

    def test_response_includes_validation(self, responder):
        """Validation layer should be present in responses."""
        # Generate several responses and check that at least one includes
        # a phrase from the validation pool
        all_validations = set()
        for pool in VALIDATION_PHRASES.values():
            all_validations.update(pool)

        found_validation = False
        for _ in range(10):
            resp = responder.generate_response("I feel so sad", "sadness")
            for phrase in all_validations:
                if phrase in resp:
                    found_validation = True
                    break
            if found_validation:
                break
        assert found_validation, "Expected at least one validation phrase in responses"

    def test_no_exact_repeat_within_three(self, responder):
        """Same full response should not appear twice in 3 consecutive calls."""
        responses = []
        for _ in range(3):
            r = responder.generate_response("I'm anxious", "anxiety")
            responses.append(r)
        # At minimum, no consecutive duplicates
        for i in range(1, len(responses)):
            assert responses[i] != responses[i - 1], (
                f"Response {i} repeated: {responses[i]}"
            )

    def test_max_supportive_templates_attribute(self):
        """EmpatheticResponder should have _MAX_SUPPORTIVE_TEMPLATES = 2."""
        assert EmpatheticResponder._MAX_SUPPORTIVE_TEMPLATES == 2

    def test_high_concern_adds_deepener(self, responder):
        """High concern should produce deeper supportive phrases."""
        all_deepeners = set(HIGH_CONCERN_DEEPENERS)
        found = False
        for _ in range(10):
            resp = responder.generate_response(
                "I can't go on", "sadness", concern_level="high"
            )
            for d in all_deepeners:
                if d in resp:
                    found = True
                    break
            if found:
                break
        assert found, "Expected high-concern deepener in high concern responses"

    def test_response_variability(self, responder):
        """Repeated calls with same input should produce varied responses."""
        responses = set()
        for _ in range(8):
            r = responder.generate_response("I'm scared", "fear")
            responses.add(r)
        assert len(responses) >= 2, "Expected at least 2 unique responses in 8 calls"


# ---------------------------------------------------------------------------
# 3. CDI gauge chart import
# ---------------------------------------------------------------------------

class TestCDIGaugeImport:
    """Verify the CDI gauge chart function is importable."""

    def test_create_cdi_gauge_import(self):
        from ui.charts import create_cdi_gauge
        assert callable(create_cdi_gauge)

    def test_create_cdi_gauge_returns_figure(self):
        from ui.charts import create_cdi_gauge
        import plotly.graph_objects as go
        fig = create_cdi_gauge(0.45, "moderate")
        assert isinstance(fig, go.Figure)


# ---------------------------------------------------------------------------
# 4. Wellness buddy escalation metadata
# ---------------------------------------------------------------------------

class TestWellnessBuddyEscalation:
    """Verify escalation detection is integrated into wellness_buddy metadata."""

    @staticmethod
    def _make_buddy():
        from wellness_buddy import WellnessBuddy
        buddy = WellnessBuddy()
        # Minimal stub profile so process_message doesn't bail out
        buddy.user_profile = type('P', (), {
            'get_personal_context': lambda s: {},
            'get_response_style': lambda s: 'balanced',
            'get_profile': lambda s: {},
            'get_trusted_contacts': lambda s: [],
            'get_emotional_history': lambda s, **kw: [],
            'get_mood_streak': lambda s: 0,
            'get_badge_display': lambda s: [],
        })()
        buddy.user_id = 'test_user'
        return buddy

    def test_escalation_in_metadata(self):
        buddy = self._make_buddy()
        buddy.process_message("I feel so sad and lonely")
        meta = buddy.get_last_response_metadata()
        assert 'escalation' in meta
        assert 'escalation_detected' in meta['escalation']

    def test_no_escalation_on_single_message(self):
        buddy = self._make_buddy()
        buddy.process_message("Hello, how are you?")
        meta = buddy.get_last_response_metadata()
        escalation = meta.get('escalation', {})
        assert escalation.get('escalation_detected') is False
