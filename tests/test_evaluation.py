"""Tests for the dataset evaluation framework.

Validates:
- Dataset loader handles blank lines
- Invalid JSON produces clear error
- Evaluation metrics computed (accuracy, precision, recall, macro_f1)
- Summary table formatting
"""

import json
import os
import tempfile

from research_evaluation import (
    evaluate_classifier,
    format_summary_table,
    load_emotion_dataset,
    normalize_emotion_label,
)


# ------------------------------------------------------------------
# Dataset loader robustness
# ------------------------------------------------------------------

def test_dataset_loader_skips_blank_lines():
    """Blank lines in JSONL must be silently skipped."""
    content = (
        '{"text": "I feel happy", "label": "joy"}\n'
        '\n'
        '  \n'
        '{"text": "I am sad", "label": "sadness"}\n'
    )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(content)
        path = f.name
    try:
        samples = load_emotion_dataset(path)
        assert len(samples) == 2
    finally:
        os.unlink(path)


def test_invalid_json_produces_clear_error():
    """Invalid JSON must raise ValueError with the line number."""
    content = (
        '{"text": "ok", "label": "joy"}\n'
        'NOT VALID JSON\n'
    )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(content)
        path = f.name
    try:
        raised = False
        try:
            load_emotion_dataset(path)
        except ValueError as exc:
            raised = True
            assert 'line 2' in str(exc).lower()
        assert raised, "Expected ValueError for bad JSON"
    finally:
        os.unlink(path)


# ------------------------------------------------------------------
# Metric computation
# ------------------------------------------------------------------

def _dummy_classifier(text):
    """Deterministic toy classifier for metric verification."""
    if 'happy' in text.lower() or 'great' in text.lower():
        return 'joy'
    if 'sad' in text.lower() or 'crying' in text.lower():
        return 'sadness'
    if 'angry' in text.lower() or 'furious' in text.lower():
        return 'anger'
    return 'neutral'


_EVAL_SAMPLES = [
    ("I am happy", "joy"),
    ("What a great day", "joy"),
    ("I am sad", "sadness"),
    ("Crying all day", "sadness"),
    ("I am angry", "anger"),
    ("Feeling neutral", "neutral"),
]


def test_accuracy_computed():
    """evaluate_classifier must return an accuracy score."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'accuracy' in report
    assert 0.0 <= report['accuracy'] <= 1.0


def test_precision_computed():
    """evaluate_classifier must return macro precision."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'macro_precision' in report
    assert 0.0 <= report['macro_precision'] <= 1.0


def test_recall_computed():
    """evaluate_classifier must return macro recall."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'macro_recall' in report
    assert 0.0 <= report['macro_recall'] <= 1.0


def test_macro_f1_computed():
    """evaluate_classifier must return macro F1."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'macro_f1' in report
    assert 0.0 <= report['macro_f1'] <= 1.0


def test_micro_f1_computed():
    """evaluate_classifier must return micro F1."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'micro_f1' in report
    assert 0.0 <= report['micro_f1'] <= 1.0


def test_confusion_matrix_computed():
    """evaluate_classifier must return a confusion matrix."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'confusion_matrix' in report
    cm = report['confusion_matrix']
    assert isinstance(cm, dict)


def test_sample_count():
    """Report must record the number of samples evaluated."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert report['samples'] == len(_EVAL_SAMPLES)


# ------------------------------------------------------------------
# Summary table
# ------------------------------------------------------------------

def test_summary_table_formatted():
    """format_summary_table must produce a readable table string."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    table = format_summary_table(report)
    assert isinstance(table, str)
    assert 'Accuracy' in table
    assert 'MACRO' in table


# ------------------------------------------------------------------
# Label normalisation
# ------------------------------------------------------------------

def test_normalize_known_labels():
    """Known labels must map to canonical forms."""
    assert normalize_emotion_label('happiness') == 'joy'
    assert normalize_emotion_label('sad') == 'sadness'
    assert normalize_emotion_label('ANGER') == 'anger'


def test_normalize_unknown_label_defaults_neutral():
    """Unknown labels must fall back to 'neutral'."""
    assert normalize_emotion_label('xyzzy_nonexistent') == 'neutral'
