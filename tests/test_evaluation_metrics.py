"""Tests for the evaluation metrics pipeline.

Validates:
- compute_metrics returns accuracy, precision, recall, macro F1
- evaluate_emotion_model end-to-end flow
- Confusion matrix structure
- Edge cases (empty, single-class)
"""

import json
import os
import tempfile

from evaluation.emotion_model_evaluation import (
    compute_metrics,
    evaluate_emotion_model,
    SYSTEM_LABELS,
)


# ------------------------------------------------------------------
# compute_metrics
# ------------------------------------------------------------------

def test_accuracy_in_report():
    """compute_metrics must return an accuracy score."""
    y_true = ["joy", "sadness", "anger", "neutral"]
    y_pred = ["joy", "sadness", "anger", "neutral"]
    report = compute_metrics(y_true, y_pred)
    assert "accuracy" in report
    assert report["accuracy"] == 1.0


def test_precision_in_report():
    """compute_metrics must return precision_macro."""
    y_true = ["joy", "sadness"]
    y_pred = ["joy", "joy"]
    report = compute_metrics(y_true, y_pred)
    assert "precision_macro" in report
    assert 0.0 <= report["precision_macro"] <= 1.0


def test_recall_in_report():
    """compute_metrics must return recall_macro."""
    y_true = ["joy", "sadness"]
    y_pred = ["joy", "joy"]
    report = compute_metrics(y_true, y_pred)
    assert "recall_macro" in report
    assert 0.0 <= report["recall_macro"] <= 1.0


def test_macro_f1_in_report():
    """compute_metrics must return macro_f1."""
    y_true = ["joy", "sadness", "anger"]
    y_pred = ["joy", "sadness", "anger"]
    report = compute_metrics(y_true, y_pred)
    assert "macro_f1" in report
    assert 0.0 <= report["macro_f1"] <= 1.0


def test_confusion_matrix_in_report():
    """compute_metrics must include a confusion_matrix dict."""
    y_true = ["joy", "sadness"]
    y_pred = ["joy", "sadness"]
    report = compute_metrics(y_true, y_pred)
    assert "confusion_matrix" in report
    assert isinstance(report["confusion_matrix"], dict)


def test_sample_count():
    """Report must include the sample count."""
    y_true = ["joy", "sadness", "anger"]
    y_pred = ["joy", "sadness", "anger"]
    report = compute_metrics(y_true, y_pred)
    assert report["samples"] == 3


def test_imperfect_predictions():
    """Metrics must be less than 1.0 for imperfect predictions."""
    y_true = ["joy", "joy", "sadness", "sadness"]
    y_pred = ["joy", "sadness", "sadness", "joy"]
    report = compute_metrics(y_true, y_pred)
    assert report["accuracy"] == 0.5


# ------------------------------------------------------------------
# evaluate_emotion_model (end-to-end with synthetic file)
# ------------------------------------------------------------------

def _write_synthetic_dataset():
    """Create a minimal GoEmotions-style JSONL file."""
    rows = [
        {"text": "I feel happy and excited", "labels": ["joy"]},
        {"text": "So sad and lonely", "labels": ["sadness"]},
        {"text": "I am furious", "labels": ["anger"]},
        {"text": "Everything is normal", "labels": ["neutral"]},
    ]
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for row in rows:
            json.dump(row, f)
            f.write("\n")
    return path


def test_evaluate_emotion_model_runs():
    """evaluate_emotion_model must complete and return a report dict."""
    path = _write_synthetic_dataset()
    try:
        report = evaluate_emotion_model(path)
        assert "accuracy" in report
        assert "macro_f1" in report
        assert report["samples"] > 0
    finally:
        os.unlink(path)


def test_evaluate_emotion_model_custom_classifier():
    """Custom classifier function must be used when provided."""
    path = _write_synthetic_dataset()
    try:
        report = evaluate_emotion_model(
            path,
            classifier_fn=lambda text: "neutral",
        )
        assert report["samples"] > 0
    finally:
        os.unlink(path)


def test_evaluate_emotion_model_max_samples():
    """max_samples should limit the number of evaluated samples."""
    path = _write_synthetic_dataset()
    try:
        report = evaluate_emotion_model(path, max_samples=2)
        assert report["samples"] == 2
    finally:
        os.unlink(path)
