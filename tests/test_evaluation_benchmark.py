"""Tests for the IEEE evaluation and benchmarking script (evaluation.py).

Validates:
- _log_prediction produces required fields
- _compute_metrics returns emotion_accuracy, risk_detection_rate,
  personalization_score_avg, macro_precision, macro_recall, macro_f1
- run_evaluation runs end-to-end and writes results.json
- Comparison table contains expected column headers
- Prediction logs contain all required fields
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Import evaluation.py directly by file path to avoid the naming conflict
# with the existing evaluation/ package directory.
# ---------------------------------------------------------------------------
_EVAL_PATH = os.path.join(os.path.dirname(__file__), "..", "evaluation.py")
_spec = importlib.util.spec_from_file_location("evaluation_script", _EVAL_PATH)
_eval_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_eval_mod)

_compute_metrics = _eval_mod._compute_metrics
_log_prediction = _eval_mod._log_prediction
_print_comparison_table = _eval_mod._print_comparison_table
_TEST_DATASET = _eval_mod._TEST_DATASET
run_evaluation = _eval_mod.run_evaluation

# ---------------------------------------------------------------------------
# Guard: skip end-to-end tests that require EmotionAnalyzer (needs textblob)
# ---------------------------------------------------------------------------
try:
    import textblob  # noqa: F401
    _HAS_TEXTBLOB = True
except ImportError:
    _HAS_TEXTBLOB = False

_needs_emotion_analyzer = pytest.mark.skipif(
    not _HAS_TEXTBLOB,
    reason="textblob not installed — EmotionAnalyzer unavailable",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_log(
    text="I feel happy",
    predicted="joy",
    actual="joy",
    risk_flag=False,
    response_type="low",
    confidence=0.8,
    boost=0.0,
) -> dict:
    return {
        "input_text": text,
        "predicted_emotion": predicted,
        "actual_emotion": actual,
        "risk_flag": risk_flag,
        "response_type": response_type,
        "emotion_confidence": confidence,
        "personalization_boost": boost,
    }


# ---------------------------------------------------------------------------
# _log_prediction
# ---------------------------------------------------------------------------

def test_log_prediction_required_fields():
    """_log_prediction must include all six required fields."""
    fake_result = {
        "primary_emotion": "anxiety",
        "is_crisis": False,
        "concern_level": "medium",
        "emotion_confidence": 0.7,
        "personalization_boost": 0.0,
    }
    log = _log_prediction("I feel anxious", fake_result, "anxiety")
    for field in ("input_text", "predicted_emotion", "actual_emotion",
                  "risk_flag", "response_type", "emotion_confidence"):
        assert field in log, f"Missing field: {field}"


def test_log_prediction_crisis_sets_risk_flag():
    """Crisis primary_emotion must set risk_flag=True."""
    fake_result = {
        "primary_emotion": "crisis",
        "is_crisis": True,
        "concern_level": "critical",
        "emotion_confidence": 0.9,
        "personalization_boost": 0.0,
    }
    log = _log_prediction("I want to end it all", fake_result, "crisis")
    assert log["risk_flag"] is True


def test_log_prediction_non_crisis_no_risk_flag():
    """Non-crisis emotion at low concern must not set risk_flag."""
    fake_result = {
        "primary_emotion": "neutral",
        "is_crisis": False,
        "concern_level": "low",
        "emotion_confidence": 0.6,
        "personalization_boost": 0.0,
    }
    log = _log_prediction("Just a normal day", fake_result, "neutral")
    assert log["risk_flag"] is False


def test_log_prediction_response_type_crisis():
    """Crisis concern level must yield response_type='crisis'."""
    fake_result = {
        "primary_emotion": "crisis",
        "is_crisis": True,
        "concern_level": "critical",
        "emotion_confidence": 0.95,
        "personalization_boost": 0.0,
    }
    log = _log_prediction("I want to hurt myself", fake_result, "crisis")
    assert log["response_type"] == "crisis"


def test_log_prediction_response_type_low():
    """Joy at low concern must yield response_type='low'."""
    fake_result = {
        "primary_emotion": "joy",
        "is_crisis": False,
        "concern_level": "low",
        "emotion_confidence": 0.85,
        "personalization_boost": 0.0,
    }
    log = _log_prediction("I am so happy!", fake_result, "joy")
    assert log["response_type"] == "low"


# ---------------------------------------------------------------------------
# _compute_metrics
# ---------------------------------------------------------------------------

def test_emotion_accuracy_perfect():
    """Perfect predictions must yield emotion_accuracy=1.0."""
    logs = [
        _make_log(predicted="joy", actual="joy"),
        _make_log(predicted="sadness", actual="sadness"),
        _make_log(predicted="anger", actual="anger"),
    ]
    metrics = _compute_metrics(logs, "test")
    assert metrics["emotion_accuracy"] == 1.0


def test_emotion_accuracy_half():
    """Half-correct predictions must yield emotion_accuracy=0.5."""
    logs = [
        _make_log(predicted="joy", actual="joy"),
        _make_log(predicted="joy", actual="sadness"),
    ]
    metrics = _compute_metrics(logs, "test")
    assert metrics["emotion_accuracy"] == 0.5


def test_risk_detection_rate_full():
    """When all crisis samples are flagged, risk_detection_rate=1.0."""
    logs = [
        _make_log(predicted="crisis", actual="crisis", risk_flag=True, response_type="crisis"),
        _make_log(predicted="crisis", actual="crisis", risk_flag=True, response_type="crisis"),
    ]
    metrics = _compute_metrics(logs, "test")
    assert metrics["risk_detection_rate"] == 1.0


def test_risk_detection_rate_zero():
    """When no crisis samples are flagged, risk_detection_rate=0.0."""
    logs = [
        _make_log(predicted="joy", actual="crisis", risk_flag=False),
        _make_log(predicted="neutral", actual="crisis", risk_flag=False),
    ]
    metrics = _compute_metrics(logs, "test")
    assert metrics["risk_detection_rate"] == 0.0


def test_personalization_score_avg_with_boosts():
    """personalization_score_avg must be the mean of non-zero boosts."""
    logs = [
        _make_log(boost=0.15),
        _make_log(boost=0.15),
        _make_log(boost=0.0),  # not boosted
    ]
    metrics = _compute_metrics(logs, "test")
    assert metrics["personalization_score_avg"] == pytest.approx(0.15, abs=1e-4)


def test_personalization_score_zero_when_no_triggers():
    """personalization_score_avg must be 0.0 when no triggers matched."""
    logs = [_make_log(boost=0.0), _make_log(boost=0.0)]
    metrics = _compute_metrics(logs, "test")
    assert metrics["personalization_score_avg"] == 0.0


def test_metrics_keys_present():
    """_compute_metrics must return all required top-level keys."""
    logs = [_make_log(predicted="joy", actual="joy")]
    metrics = _compute_metrics(logs, "test")
    for key in (
        "emotion_accuracy",
        "risk_detection_rate",
        "personalization_score_avg",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "per_class_metrics",
        "risk_confusion",
    ):
        assert key in metrics, f"Missing key: {key}"


def test_macro_f1_in_range():
    """macro_f1 must be in [0.0, 1.0]."""
    logs = [
        _make_log(predicted="joy", actual="joy"),
        _make_log(predicted="sadness", actual="sadness"),
        _make_log(predicted="joy", actual="sadness"),
    ]
    metrics = _compute_metrics(logs, "test")
    assert 0.0 <= metrics["macro_f1"] <= 1.0


# ---------------------------------------------------------------------------
# _print_comparison_table
# ---------------------------------------------------------------------------

def test_comparison_table_contains_headers():
    """Comparison table must mention both model column names."""
    baseline = {
        "emotion_accuracy": 0.72,
        "macro_precision": 0.70,
        "macro_recall": 0.68,
        "macro_f1": 0.69,
        "risk_detection_rate": 0.60,
        "personalization_score_avg": 0.0,
    }
    proposed = {
        "emotion_accuracy": 0.85,
        "macro_precision": 0.84,
        "macro_recall": 0.83,
        "macro_f1": 0.835,
        "risk_detection_rate": 0.78,
        "personalization_score_avg": 0.15,
    }
    table = _print_comparison_table(baseline, proposed)
    assert "Baseline" in table
    assert "Proposed" in table


def test_comparison_table_contains_metric_names():
    """Comparison table must include all key metric row labels."""
    baseline = {
        "emotion_accuracy": 0.72,
        "macro_precision": 0.70,
        "macro_recall": 0.68,
        "macro_f1": 0.69,
        "risk_detection_rate": 0.60,
        "personalization_score_avg": 0.0,
    }
    proposed = dict(baseline)
    table = _print_comparison_table(baseline, proposed)
    for label in ("accuracy", "precision", "recall", "F1", "risk_detection_rate"):
        assert label in table, f"'{label}' not found in comparison table"


# ---------------------------------------------------------------------------
# run_evaluation — end-to-end
# ---------------------------------------------------------------------------

def _tiny_dataset():
    """Minimal dataset for fast end-to-end tests."""
    return [
        ("I feel so happy", "joy", False),
        ("I am really sad", "sadness", False),
        ("I want to end it all", "crisis", False),
        ("Stressed about my deadline", "anxiety", True),
    ]


@_needs_emotion_analyzer
def test_run_evaluation_returns_dict():
    """run_evaluation must return a dict with baseline/proposed keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_evaluation(dataset=_tiny_dataset(), output_dir=tmpdir)
    assert isinstance(results, dict)
    assert "baseline" in results
    assert "proposed" in results


@_needs_emotion_analyzer
def test_run_evaluation_writes_results_json():
    """run_evaluation must write results.json to the output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_evaluation(dataset=_tiny_dataset(), output_dir=tmpdir)
        json_path = os.path.join(tmpdir, "results.json")
        assert os.path.exists(json_path), "results.json not written"
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    assert "baseline" in data
    assert "proposed" in data


@_needs_emotion_analyzer
def test_results_json_has_meta():
    """results.json must include a meta section with timestamp and labels."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_evaluation(dataset=_tiny_dataset(), output_dir=tmpdir)
        with open(os.path.join(tmpdir, "results.json"), encoding="utf-8") as f:
            data = json.load(f)
    assert "meta" in data
    assert "timestamp" in data["meta"]
    assert "labels" in data["meta"]


@_needs_emotion_analyzer
def test_results_json_predictions_logged():
    """Prediction logs in results.json must include all required fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_evaluation(dataset=_tiny_dataset(), output_dir=tmpdir)
        with open(os.path.join(tmpdir, "results.json"), encoding="utf-8") as f:
            data = json.load(f)

    for model_key in ("baseline", "proposed"):
        preds = data[model_key]["predictions"]
        assert len(preds) == len(_tiny_dataset())
        for entry in preds:
            for field in ("input_text", "predicted_emotion", "actual_emotion",
                          "risk_flag", "response_type"):
                assert field in entry, f"[{model_key}] Missing field: {field}"


@_needs_emotion_analyzer
def test_results_json_metrics_keys():
    """Metrics section in results.json must include all headline metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_evaluation(dataset=_tiny_dataset(), output_dir=tmpdir)
        with open(os.path.join(tmpdir, "results.json"), encoding="utf-8") as f:
            data = json.load(f)

    for model_key in ("baseline", "proposed"):
        metrics = data[model_key]["metrics"]
        for key in (
            "emotion_accuracy",
            "risk_detection_rate",
            "personalization_score_avg",
            "macro_precision",
            "macro_recall",
            "macro_f1",
        ):
            assert key in metrics, f"[{model_key}] Missing metric: {key}"


@_needs_emotion_analyzer
def test_run_evaluation_sample_count_matches():
    """Prediction count must equal dataset size for both models."""
    dataset = _tiny_dataset()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_evaluation(dataset=dataset, output_dir=tmpdir)
    assert results["baseline"]["metrics"]["samples"] == len(dataset)
    assert results["proposed"]["metrics"]["samples"] == len(dataset)


@_needs_emotion_analyzer
def test_proposed_personalization_score_higher():
    """Proposed model must yield a higher personalization_score than baseline."""
    dataset = [
        ("Stressed about my deadline", "anxiety", True),
        ("Worried about the exam tomorrow", "anxiety", True),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_evaluation(dataset=dataset, output_dir=tmpdir)
    baseline_ps = results["baseline"]["metrics"]["personalization_score_avg"]
    proposed_ps = results["proposed"]["metrics"]["personalization_score_avg"]
    assert proposed_ps > baseline_ps


def test_built_in_dataset_loaded():
    """_TEST_DATASET must be a non-empty list of 3-tuples."""
    assert len(_TEST_DATASET) > 0
    for item in _TEST_DATASET:
        assert len(item) == 3
        text, label, trigger = item
        assert isinstance(text, str)
        assert isinstance(label, str)
        assert isinstance(trigger, bool)
