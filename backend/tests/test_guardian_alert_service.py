"""Tests for guardian alert service safety fixes.

Covers:
  1. Keyword false-positive reduction (removed broad words)
  2. Negation detection in is_crisis_keyword_present()
  3. Trigger condition — high risk requires score gate
  4. Trigger condition — critical bypasses score gate
  5. should_trigger_alert() spike / session count paths
"""

from __future__ import annotations

import pytest

from app.services.guardian_alert_service import (
    is_crisis_keyword_present,
    should_trigger_alert,
)


# ---------------------------------------------------------------------------
# is_crisis_keyword_present — keyword coverage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "I want to kill myself",
    "I'm going to end my life tonight",
    "I want to die",
    "I am thinking about suicide",
    "I hurt myself last night",
    "there is no reason to live anymore",
    "I give up on life",
    "I want to disappear forever",
    "I can't go on like this",
])
def test_crisis_keyword_detected(text: str):
    assert is_crisis_keyword_present(text) is True


# ---------------------------------------------------------------------------
# is_crisis_keyword_present — removed high-FP words must NOT trigger
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "This code is completely worthless.",
    "The situation feels hopeless but I'll try again.",
    "Nobody cares about my opinion at work.",
    "I feel kind of hopeless about the project timeline.",
])
def test_removed_high_fp_words_do_not_trigger(text: str):
    assert is_crisis_keyword_present(text) is False


# ---------------------------------------------------------------------------
# is_crisis_keyword_present — negation detection
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "I don't want to die",
    "I didn't want to hurt myself",
    "I won't kill myself",
    "I never want to end my life",
    "No, I don't want to die",
    "I'm not thinking about suicide",
    "I am not going to hurt myself",
])
def test_negated_crisis_phrases_not_detected(text: str):
    assert is_crisis_keyword_present(text) is False


# ---------------------------------------------------------------------------
# should_trigger_alert — critical always triggers
# ---------------------------------------------------------------------------

def test_critical_always_triggers_regardless_of_score():
    assert should_trigger_alert(risk_level="critical", current_risk_score=0.0) is True
    assert should_trigger_alert(risk_level="critical", current_risk_score=0.3) is True


# ---------------------------------------------------------------------------
# should_trigger_alert — high requires minimum score gate
# ---------------------------------------------------------------------------

def test_high_below_min_score_does_not_trigger():
    """risk_level='high' alone with a low score should NOT trigger."""
    assert should_trigger_alert(risk_level="high", current_risk_score=0.3) is False


def test_high_above_min_score_triggers():
    assert should_trigger_alert(risk_level="high", current_risk_score=0.7) is True


def test_high_exactly_at_min_score_triggers():
    # 0.65 is the default GUARDIAN_HIGH_RISK_MIN_SCORE
    assert should_trigger_alert(risk_level="high", current_risk_score=0.65) is True


# ---------------------------------------------------------------------------
# should_trigger_alert — other conditions (low risk_level)
# ---------------------------------------------------------------------------

def test_crisis_keyword_in_text_triggers_regardless_of_level():
    assert should_trigger_alert(
        risk_level="low",
        text="I want to kill myself",
        current_risk_score=0.1,
    ) is True


def test_distress_session_threshold_triggers():
    assert should_trigger_alert(
        risk_level="low",
        distress_session_count=3,
    ) is True


def test_distress_session_below_threshold_does_not_trigger():
    assert should_trigger_alert(
        risk_level="low",
        distress_session_count=2,
    ) is False


def test_risk_spike_triggers():
    assert should_trigger_alert(
        risk_level="low",
        previous_risk_score=0.2,
        current_risk_score=0.7,  # spike = 0.5 >= 0.4
    ) is True


def test_risk_spike_below_threshold_does_not_trigger():
    assert should_trigger_alert(
        risk_level="low",
        previous_risk_score=0.5,
        current_risk_score=0.7,  # spike = 0.2 < 0.4
    ) is False


# ---------------------------------------------------------------------------
# Negation edge cases — word boundaries
# ---------------------------------------------------------------------------

def test_negation_must_be_close_enough():
    """A negation word far from the keyword (>40 chars away) should not suppress it."""
    # Build a string where "not" appears more than 40 chars before "want to die"
    far_text = "not " + "x" * 50 + "I want to die"
    # The negation is > 40 chars away from the keyword position, so it should fire
    assert is_crisis_keyword_present(far_text) is True
