"""Tests for improved research_evaluation.py utilities."""

import json
import os
import tempfile

from research_evaluation import (
    evaluate_classifier,
    evaluate_emotion_model,
    format_summary_table,
    load_emotion_dataset,
    normalize_emotion_label,
)


# ---------------------------------------------------------------------------
# JSONL loader robustness
# ---------------------------------------------------------------------------

def test_load_jsonl_skips_blank_lines():
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
        assert samples[0] == ('I feel happy', 'joy')
        assert samples[1] == ('I am sad', 'sadness')
    finally:
        os.unlink(path)


def test_load_jsonl_reports_line_number_on_bad_json():
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
            assert 'line 2' in str(exc).lower(), f"Expected line number in error: {exc}"
        assert raised, "Expected ValueError for bad JSON"
    finally:
        os.unlink(path)


def test_load_jsonl_blank_lines_between_valid_records():
    """Multiple blank lines between records should not cause issues."""
    content = (
        '\n\n'
        '{"text": "one", "label": "joy"}\n'
        '\n\n\n'
        '{"text": "two", "label": "anger"}\n'
        '\n'
    )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(content)
        path = f.name
    try:
        samples = load_emotion_dataset(path)
        assert len(samples) == 2
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Dataset-specific field mapping
# ---------------------------------------------------------------------------

def test_goemotions_field_mapping():
    """GoEmotions-style data uses 'labels' list field."""
    content = '{"text": "This is great!", "labels": ["joy"]}\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False,
                                     prefix='goemotions_') as f:
        f.write(content)
        path = f.name
    try:
        samples = load_emotion_dataset(path)
        assert len(samples) == 1
        assert samples[0][1] == 'joy'
    finally:
        os.unlink(path)


def test_emotionlines_field_mapping():
    """EmotionLines-style data uses 'utterance' / 'emotion' fields."""
    data = [{"utterance": "I'm scared", "emotion": "fear"}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False,
                                     prefix='emotionlines_') as f:
        json.dump(data, f)
        path = f.name
    try:
        samples = load_emotion_dataset(path, dataset_type='emotionlines')
        assert len(samples) == 1
        assert samples[0] == ("I'm scared", 'fear')
    finally:
        os.unlink(path)


def test_dailydialog_field_mapping():
    """DailyDialog-style data uses 'text' / 'emotion' fields."""
    content = '{"text": "hello there", "emotion": "neutral"}\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False,
                                     prefix='dailydialog_') as f:
        f.write(content)
        path = f.name
    try:
        samples = load_emotion_dataset(path)
        assert len(samples) == 1
        assert samples[0][1] == 'neutral'
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Extended evaluation metrics
# ---------------------------------------------------------------------------

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


def test_evaluate_classifier_micro_metrics():
    """micro precision/recall/F1 must be present and sensible."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'micro_precision' in report
    assert 'micro_recall' in report
    assert 'micro_f1' in report
    assert report['micro_precision'] >= 0.0
    assert report['micro_f1'] >= 0.0


def test_evaluate_classifier_confusion_matrix():
    """Confusion matrix must be returned as a nested dict."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'confusion_matrix' in report
    cm = report['confusion_matrix']
    assert isinstance(cm, dict)
    # All standard labels must be present as rows
    for label in ['joy', 'sadness', 'anger', 'neutral']:
        assert label in cm


def test_evaluate_classifier_roc_auc():
    """ROC-AUC must be present with macro and per-class values."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    assert 'roc_auc' in report
    roc = report['roc_auc']
    assert roc is not None
    assert 'macro' in roc
    assert 'per_class' in roc
    assert 0.0 <= roc['macro'] <= 1.0


def test_evaluate_classifier_backward_compat():
    """Existing keys (samples, accuracy, macro_*, per_class) must still exist."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    for key in ['samples', 'accuracy', 'macro_precision', 'macro_recall',
                'macro_f1', 'per_class']:
        assert key in report


# ---------------------------------------------------------------------------
# evaluate_emotion_model helper
# ---------------------------------------------------------------------------

def test_evaluate_emotion_model_helper():
    """evaluate_emotion_model() loads a dataset file and returns a report."""
    content = (
        '{"text": "I am so happy today", "label": "joy"}\n'
        '{"text": "I feel very sad", "label": "sadness"}\n'
        '{"text": "I am angry", "label": "anger"}\n'
    )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(content)
        path = f.name
    try:
        report = evaluate_emotion_model(path, classifier_fn=_dummy_classifier)
        assert report['samples'] == 3
        assert 'macro_f1' in report
        assert 'micro_f1' in report
        assert 'confusion_matrix' in report
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Summary table formatter
# ---------------------------------------------------------------------------

def test_format_summary_table():
    """format_summary_table() must produce a string with key rows."""
    report = evaluate_classifier(_EVAL_SAMPLES, _dummy_classifier)
    table = format_summary_table(report)
    assert isinstance(table, str)
    assert 'MACRO' in table
    assert 'MICRO' in table
    assert 'Accuracy' in table
    assert 'Samples' in table
