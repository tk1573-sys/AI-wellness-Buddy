"""Tests for the empathetic response generator (empathetic_responder.py).

Validates:
  - Responses contain empathy phrases from curated pools.
  - Responses vary across runs (conversational variability).
  - Responses adapt to emotion type.
  - Responses become stronger when concern_level is high/critical.
  - Gentle suggestions never use commanding language.
  - Context memory adds history-aware phrases for longer conversations.
  - Humanisation layer removes robotic phrasing.
  - Integration with conversation_handler.generate_response().
"""

import re
import pytest

from empathetic_responder import (
    EMPATHY_PHRASES,
    VALIDATION_PHRASES,
    SUPPORT_PHRASES,
    GENTLE_SUGGESTIONS,
    HIGH_CONCERN_DEEPENERS,
    HISTORY_AWARE_PHRASES,
    EmpatheticResponder,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def responder():
    return EmpatheticResponder()


# ---------------------------------------------------------------------------
# 1. Responses contain empathy phrases from curated pools
# ---------------------------------------------------------------------------

class TestEmpathyPhrases:
    """Verify that responses include phrases from the empathy pools."""

    @pytest.mark.parametrize("emotion", ["sadness", "anxiety", "anger", "fear", "stress"])
    def test_contains_empathy_phrase(self, responder, emotion):
        resp = responder.generate_response("I feel bad", emotion, "low", 0.5)
        pool = EMPATHY_PHRASES[emotion]
        assert any(phrase in resp for phrase in pool), (
            f"Response for {emotion!r} should include an empathy phrase from the pool"
        )

    def test_contains_validation_phrase(self, responder):
        resp = responder.generate_response("I'm so sad", "sadness", "low", 0.6)
        pool = VALIDATION_PHRASES["sadness"]
        assert any(phrase in resp for phrase in pool)

    def test_contains_support_phrase(self, responder):
        resp = responder.generate_response("I'm anxious", "anxiety", "medium", 0.7)
        pool = SUPPORT_PHRASES["medium"]
        assert any(phrase in resp for phrase in pool)


# ---------------------------------------------------------------------------
# 2. Conversational variability — responses differ across runs
# ---------------------------------------------------------------------------

class TestVariability:
    """Responses should vary when called multiple times with the same input."""

    def test_responses_vary(self, responder):
        seen = set()
        for _ in range(10):
            resp = responder.generate_response("I'm feeling down", "sadness", "low", 0.5)
            seen.add(resp)
        assert len(seen) > 1, "Responses should vary across multiple calls"

    def test_no_immediate_repeat(self, responder):
        r1 = responder.generate_response("worried", "anxiety", "low", 0.5)
        r2 = responder.generate_response("worried", "anxiety", "low", 0.5)
        # With anti-repeat deque, consecutive identical responses are unlikely
        # but not impossible once pools are exhausted. Check for at least
        # one difference in ten attempts.
        any_different = False
        for _ in range(10):
            ra = responder.generate_response("worried", "anxiety", "low", 0.5)
            rb = responder.generate_response("worried", "anxiety", "low", 0.5)
            if ra != rb:
                any_different = True
                break
        assert any_different, "Consecutive responses should differ at least sometimes"


# ---------------------------------------------------------------------------
# 3. Responses adapt to emotion type
# ---------------------------------------------------------------------------

class TestEmotionAdaptation:
    """Different emotions should yield qualitatively different responses."""

    def test_sadness_vs_anger(self, responder):
        sad = responder.generate_response("I'm so sad", "sadness", "low", 0.5)
        angry = responder.generate_response("I'm so angry", "anger", "low", 0.5)
        assert sad != angry, "Sadness and anger responses should differ"

    def test_anxiety_includes_anxiety_content(self, responder):
        resp = responder.generate_response("I'm really anxious", "anxiety", "low", 0.6)
        pool = EMPATHY_PHRASES["anxiety"] + VALIDATION_PHRASES["anxiety"]
        assert any(phrase in resp for phrase in pool)

    def test_fear_includes_fear_content(self, responder):
        resp = responder.generate_response("I'm scared", "fear", "low", 0.5)
        pool = EMPATHY_PHRASES["fear"] + VALIDATION_PHRASES["fear"]
        assert any(phrase in resp for phrase in pool)

    def test_joy_includes_joy_content(self, responder):
        resp = responder.generate_response("I'm so happy!", "joy", "low", 0.8)
        pool = EMPATHY_PHRASES["joy"]
        assert any(phrase in resp for phrase in pool)

    def test_neutral_is_supportive(self, responder):
        resp = responder.generate_response("Not much", "neutral", "low", 0.3)
        pool = EMPATHY_PHRASES["neutral"]
        assert any(phrase in resp for phrase in pool)

    def test_emotion_alias_mapping(self, responder):
        """Aliases like 'depressed' should map to 'sadness' pool."""
        resp = responder.generate_response("I'm depressed", "depressed", "low", 0.5)
        pool = EMPATHY_PHRASES["sadness"]
        assert any(phrase in resp for phrase in pool)


# ---------------------------------------------------------------------------
# 4. Concern level escalation
# ---------------------------------------------------------------------------

class TestConcernLevel:
    """High/critical concern should produce stronger responses."""

    def test_high_concern_includes_deepener(self, responder):
        resp = responder.generate_response("I can't do this", "sadness", "high", 0.9)
        has_deepener = any(phrase in resp for phrase in HIGH_CONCERN_DEEPENERS)
        has_high_support = any(phrase in resp for phrase in SUPPORT_PHRASES["high"])
        assert has_deepener or has_high_support, (
            "High concern should include a deepener or high-support phrase"
        )

    def test_critical_concern_includes_deepener(self, responder):
        resp = responder.generate_response("I want to give up", "sadness", "critical", 0.95)
        has_deepener = any(phrase in resp for phrase in HIGH_CONCERN_DEEPENERS)
        has_critical_support = any(phrase in resp for phrase in SUPPORT_PHRASES["critical"])
        assert has_deepener or has_critical_support

    def test_high_concern_longer_than_low(self, responder):
        low = responder.generate_response("I'm a bit down", "sadness", "low", 0.4)
        high = responder.generate_response("I'm really struggling", "sadness", "high", 0.9)
        assert len(high) >= len(low), (
            "High-concern responses should be at least as long as low-concern ones"
        )


# ---------------------------------------------------------------------------
# 5. Gentle suggestions — no commanding language
# ---------------------------------------------------------------------------

class TestGentleSuggestions:
    """Suggestions should be invitations, not commands."""

    _COMMANDING = [" You should ", " You need to ", " You must ", " You have to "]

    def test_no_commanding_language(self, responder):
        for emotion in ("sadness", "anxiety", "anger", "fear", "stress"):
            for _ in range(5):
                resp = responder.generate_response("help me", emotion, "medium", 0.6)
                for cmd in self._COMMANDING:
                    assert cmd not in resp, (
                        f"Response contains commanding phrase {cmd!r}"
                    )

    def test_suggestion_uses_soft_language(self, responder):
        resp = responder.generate_response("I'm stressed", "stress", "medium", 0.6)
        suggestion_pool = GENTLE_SUGGESTIONS["stress"]
        assert any(s in resp for s in suggestion_pool), (
            "Response should include a gentle suggestion"
        )

    def test_joy_skips_suggestion(self, responder):
        resp = responder.generate_response("I'm so happy!", "joy", "low", 0.8)
        suggestion_pool = GENTLE_SUGGESTIONS.get("joy", [])
        # Joy shouldn't include suggestions (no "joy" suggestions pool used)
        # Just verify no commanding language
        for cmd in self._COMMANDING:
            assert cmd not in resp


# ---------------------------------------------------------------------------
# 6. Context memory — history-aware phrases
# ---------------------------------------------------------------------------

class TestContextMemory:
    """Long conversations should trigger history-aware references."""

    def test_long_history_includes_reference(self, responder):
        history = [
            {"role": "user", "content": "I'm worried about exams"},
            {"role": "assistant", "content": "That's understandable"},
            {"role": "user", "content": "The pressure keeps building"},
            {"role": "assistant", "content": "I hear you"},
            {"role": "user", "content": "I can't sleep now"},
        ]
        resp = responder.generate_response(
            "It's getting worse", "anxiety", "medium", 0.7, history=history
        )
        has_ref = any(phrase in resp for phrase in HISTORY_AWARE_PHRASES)
        assert has_ref, "Long history should trigger a history-aware phrase"

    def test_short_history_no_reference(self, responder):
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]
        resp = responder.generate_response(
            "I'm fine", "neutral", "low", 0.3, history=history
        )
        has_ref = any(phrase in resp for phrase in HISTORY_AWARE_PHRASES)
        assert not has_ref, "Short history should NOT trigger a history-aware phrase"

    def test_joy_no_history_reference(self, responder):
        history = [{"role": "user", "content": "msg"}] * 6
        resp = responder.generate_response(
            "I'm great!", "joy", "low", 0.8, history=history
        )
        has_ref = any(phrase in resp for phrase in HISTORY_AWARE_PHRASES)
        assert not has_ref, "Joy responses shouldn't include history-aware phrases"


# ---------------------------------------------------------------------------
# 7. Humanisation layer
# ---------------------------------------------------------------------------

class TestHumanisation:
    """Robotic phrasing should be replaced by natural language."""

    def test_no_robotic_phrasing(self, responder):
        for _ in range(10):
            resp = responder.generate_response("I'm sad", "sadness", "medium", 0.6)
            assert "I have detected" not in resp
            assert "emotional state is" not in resp
            assert "Based on my analysis" not in resp


# ---------------------------------------------------------------------------
# 8. Integration with ConversationHandler
# ---------------------------------------------------------------------------

class TestIntegration:
    """EmpatheticResponder is used by ConversationHandler.generate_response."""

    def test_handler_uses_empathetic_responder(self):
        from conversation_handler import ConversationHandler
        handler = ConversationHandler()
        assert hasattr(handler, '_empathetic_responder')
        assert isinstance(handler._empathetic_responder, EmpatheticResponder)

    def test_handler_sadness_response_contains_empathy(self):
        from conversation_handler import ConversationHandler
        handler = ConversationHandler()
        emotion_data = {
            'emotion': 'negative',
            'primary_emotion': 'sadness',
            'severity': 'moderate',
            'polarity': -0.5,
            'sentiment_score': -0.5,
            'concern_level': 'medium',
            'emotion_confidence': 0.7,
        }
        handler.add_message("I feel so alone", emotion_data)
        resp = handler.generate_response(emotion_data, {
            'response_style': 'balanced',
            'language_preference': 'english',
        })
        sadness_pool = EMPATHY_PHRASES["sadness"] + VALIDATION_PHRASES["sadness"]
        assert any(phrase in resp for phrase in sadness_pool), (
            "Handler response should contain empathetic sadness phrasing"
        )

    def test_handler_high_concern_depth(self):
        from conversation_handler import ConversationHandler
        handler = ConversationHandler()
        emotion_data = {
            'emotion': 'negative',
            'primary_emotion': 'anxiety',
            'severity': 'high',
            'polarity': -0.8,
            'sentiment_score': -0.8,
            'concern_level': 'high',
            'emotion_confidence': 0.9,
        }
        handler.add_message("I can't breathe, everything is falling apart", emotion_data)
        resp = handler.generate_response(emotion_data, {
            'response_style': 'balanced',
            'language_preference': 'english',
        })
        combined = SUPPORT_PHRASES["high"] + HIGH_CONCERN_DEEPENERS
        assert any(phrase in resp for phrase in combined), (
            "High-concern handler response should include deeper support"
        )

    def test_crisis_still_uses_templates(self):
        """Crisis responses should still use the explicit crisis templates."""
        from conversation_handler import ConversationHandler
        handler = ConversationHandler()
        emotion_data = {
            'emotion': 'negative',
            'primary_emotion': 'crisis',
            'severity': 'extreme',
            'polarity': -0.9,
            'sentiment_score': -0.9,
        }
        resp = handler.generate_response(emotion_data, {
            'response_style': 'balanced',
            'language_preference': 'english',
        })
        assert "988" in resp, "Crisis response must reference 988 lifeline"

    def test_joy_still_uses_templates(self):
        """Joy responses should still use the existing joy templates."""
        from conversation_handler import ConversationHandler
        handler = ConversationHandler()
        emotion_data = {
            'emotion': 'positive',
            'primary_emotion': 'joy',
            'severity': 'mild',
            'polarity': 0.8,
            'sentiment_score': 0.8,
        }
        resp = handler.generate_response(emotion_data, {
            'response_style': 'balanced',
            'language_preference': 'english',
        })
        # Joy responses should contain positive emojis or "glad"/"wonderful"
        assert any(w in resp.lower() for w in ("glad", "wonderful", "😊", "💛", "🌟"))


# ---------------------------------------------------------------------------
# 9. Module public API smoke test
# ---------------------------------------------------------------------------

class TestPublicAPI:
    def test_empathetic_responder_has_generate_response(self):
        r = EmpatheticResponder()
        assert callable(getattr(r, 'generate_response', None))

    def test_pools_have_entries(self):
        for emotion, pool in EMPATHY_PHRASES.items():
            assert len(pool) >= 3, f"EMPATHY_PHRASES[{emotion!r}] needs >= 3 entries"
        for emotion, pool in VALIDATION_PHRASES.items():
            assert len(pool) >= 3, f"VALIDATION_PHRASES[{emotion!r}] needs >= 3 entries"
        for level, pool in SUPPORT_PHRASES.items():
            assert len(pool) >= 3, f"SUPPORT_PHRASES[{level!r}] needs >= 3 entries"

    def test_normalise_emotion_aliases(self, responder):
        assert responder._normalise_emotion("depressed") == "sadness"
        assert responder._normalise_emotion("worried") == "anxiety"
        assert responder._normalise_emotion("frustrated") == "anger"
        assert responder._normalise_emotion("scared") == "fear"
        assert responder._normalise_emotion("stressed") == "stress"
        assert responder._normalise_emotion("happy") == "joy"
        assert responder._normalise_emotion("neutral") == "neutral"
