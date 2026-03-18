"""
Tests for the risk_escalation module.

Run with: python -m pytest tests/test_risk_escalation.py -v
"""

import pytest
from risk_escalation import detect_escalation, escalation_score


# ── detect_escalation ────────────────────────────────────────────────────────


class TestDetectEscalationPathway:
    """Rule 1: neutral → anxiety → sadness → crisis pathway."""

    def test_exact_pathway_triggers(self):
        history = ["neutral", "anxiety", "sadness", "crisis"]
        assert detect_escalation(history) is True

    def test_pathway_embedded_in_longer_history(self):
        history = ["joy", "neutral", "joy", "anxiety", "sadness", "crisis"]
        assert detect_escalation(history) is True

    def test_incomplete_pathway_no_trigger(self):
        history = ["neutral", "anxiety", "sadness"]
        assert detect_escalation(history) is False

    def test_wrong_order_no_trigger(self):
        # Only two negatives before a neutral break — neither rule fires.
        history = ["sadness", "anxiety", "neutral", "crisis"]
        assert detect_escalation(history) is False


class TestDetectEscalationConsecutiveNegatives:
    """Rule 2: 3+ consecutive negative emotions."""

    def test_three_consecutive_negatives(self):
        history = ["neutral", "sadness", "anxiety", "fear"]
        assert detect_escalation(history) is True

    def test_exactly_two_consecutive_no_trigger(self):
        history = ["sadness", "anxiety", "neutral"]
        assert detect_escalation(history) is False

    def test_interrupted_run_no_trigger(self):
        history = ["sadness", "neutral", "anxiety"]
        assert detect_escalation(history) is False

    def test_run_at_end_triggers(self):
        history = ["joy", "neutral", "anger", "sadness", "crisis"]
        assert detect_escalation(history) is True


class TestDetectEscalationEdgeCases:
    """Edge cases and input formats."""

    def test_empty_history(self):
        assert detect_escalation([]) is False

    def test_single_negative(self):
        assert detect_escalation(["sadness"]) is False

    def test_all_positive_no_trigger(self):
        history = ["joy", "neutral", "joy", "neutral"]
        assert detect_escalation(history) is False

    def test_dict_entries_supported(self):
        history = [
            {"emotion": "neutral"},
            {"emotion": "anxiety"},
            {"emotion": "sadness"},
            {"emotion": "crisis"},
        ]
        assert detect_escalation(history) is True

    def test_dict_entries_consecutive_negatives(self):
        history = [
            {"emotion": "sadness"},
            {"emotion": "anxiety"},
            {"emotion": "fear"},
        ]
        assert detect_escalation(history) is True

    def test_mixed_str_and_dict(self):
        history = ["neutral", {"emotion": "anxiety"}, "sadness", "crisis"]
        assert detect_escalation(history) is True

    def test_case_insensitive(self):
        history = ["NEUTRAL", "Anxiety", "SADNESS", "Crisis"]
        assert detect_escalation(history) is True


# ── escalation_score ─────────────────────────────────────────────────────────


class TestEscalationScore:
    """escalation_score must return a float in [0.0, 1.0]."""

    def test_returns_float(self):
        assert isinstance(escalation_score(["neutral"]), float)

    def test_empty_history_returns_zero(self):
        assert escalation_score([]) == 0.0

    def test_all_joy_low_score(self):
        score = escalation_score(["joy", "joy", "joy"])
        assert score == 0.0

    def test_all_crisis_high_score(self):
        score = escalation_score(["crisis", "crisis", "crisis"])
        assert score >= 0.8

    def test_escalating_pathway_gets_bonus(self):
        # Full pathway → detect_escalation returns True → score gets +0.2 bonus
        base_history = ["neutral", "anxiety"]
        escalating = ["neutral", "anxiety", "sadness", "crisis"]
        assert escalation_score(escalating) > escalation_score(base_history)

    def test_score_bounded_zero_to_one(self):
        extremes = [
            [],
            ["joy"] * 10,
            ["crisis"] * 10,
            ["neutral", "anxiety", "sadness", "crisis"],
        ]
        for h in extremes:
            s = escalation_score(h)
            assert 0.0 <= s <= 1.0, f"Score out of range for {h}: {s}"

    def test_higher_severity_higher_score(self):
        mild = ["neutral", "stress"]
        severe = ["neutral", "crisis"]
        assert escalation_score(severe) > escalation_score(mild)

    def test_dict_entries_accepted(self):
        history = [{"emotion": "anxiety"}, {"emotion": "sadness"}]
        score = escalation_score(history)
        assert 0.0 <= score <= 1.0
