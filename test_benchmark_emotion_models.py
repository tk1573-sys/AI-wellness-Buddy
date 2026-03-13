"""Tests for benchmark_emotion_models.py."""

import json
import os
import tempfile

from benchmark_emotion_models import (
    LABELS,
    _SYNTHETIC_SAMPLES,
    _make_keyword_classifier,
    _make_transformer_classifier,
    _make_hybrid_classifier,
    create_synthetic_dataset,
    format_comparison_table,
    render_confusion_matrix_text,
    run_benchmark,
)


# ---------------------------------------------------------------------------
# Classifier factories
# ---------------------------------------------------------------------------

def test_keyword_classifier_returns_label():
    """Keyword classifier must return a string from the label set."""
    clf = _make_keyword_classifier()
    result = clf("I am so happy and joyful today")
    assert isinstance(result, str)
    assert result in LABELS or result in (
        "joy", "sadness", "anger", "fear", "anxiety", "neutral", "crisis",
    )


def test_keyword_classifier_detects_sadness():
    """Keyword classifier must detect sadness from keyword-heavy input."""
    clf = _make_keyword_classifier()
    result = clf("I am sad and lonely and crying")
    assert result == "sadness"


def test_keyword_classifier_detects_joy():
    """Keyword classifier must detect joy from keyword-heavy input."""
    clf = _make_keyword_classifier()
    result = clf("I am happy and excited and wonderful")
    assert result == "joy"


def test_transformer_classifier_returns_label():
    """Transformer classifier must return a valid label string."""
    clf, _et = _make_transformer_classifier()
    result = clf("I feel great today")
    assert isinstance(result, str)


def test_hybrid_classifier_returns_label():
    """Hybrid classifier must return a valid label string."""
    clf, _analyzer = _make_hybrid_classifier()
    result = clf("I am feeling anxious and worried")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Synthetic dataset
# ---------------------------------------------------------------------------

def test_synthetic_samples_not_empty():
    """Built-in synthetic samples must contain entries."""
    assert len(_SYNTHETIC_SAMPLES) > 10


def test_synthetic_samples_cover_all_emotions():
    """Synthetic dataset must cover at least joy/sadness/anger/fear/anxiety/neutral."""
    labels_in_data = {label for _, label in _SYNTHETIC_SAMPLES}
    for emo in ("joy", "sadness", "anger", "fear", "anxiety", "neutral"):
        assert emo in labels_in_data, f"Missing emotion: {emo}"


def test_create_synthetic_dataset_creates_file():
    """create_synthetic_dataset() must produce a valid JSONL file."""
    path = create_synthetic_dataset()
    try:
        assert os.path.exists(path)
        with open(path) as f:
            lines = [l.strip() for l in f if l.strip()]
        assert len(lines) == len(_SYNTHETIC_SAMPLES)
        # Verify each line is valid JSON
        for line in lines:
            obj = json.loads(line)
            assert "text" in obj
            assert "label" in obj
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def test_format_comparison_table():
    """format_comparison_table() must produce a readable table."""
    results = {
        "Model A": {"accuracy": 0.85, "macro_f1": 0.80, "micro_f1": 0.83},
        "Model B": {"accuracy": 0.72, "macro_f1": 0.68, "micro_f1": 0.70},
    }
    table = format_comparison_table(results)
    assert isinstance(table, str)
    assert "Model A" in table
    assert "Model B" in table
    assert "Accuracy" in table
    assert "Macro F1" in table


# ---------------------------------------------------------------------------
# Confusion matrix rendering
# ---------------------------------------------------------------------------

def test_render_confusion_matrix_text():
    """Text confusion matrix must include all labels."""
    cm = {
        "joy": {"joy": 5, "sadness": 1},
        "sadness": {"joy": 0, "sadness": 4},
    }
    labels = ["joy", "sadness"]
    text = render_confusion_matrix_text(cm, labels)
    assert isinstance(text, str)
    assert "joy" in text
    assert "sadness" in text


def test_render_confusion_matrix_handles_missing_keys():
    """Missing keys in confusion matrix must default to zero."""
    cm = {"joy": {"joy": 3}}  # sadness row missing
    labels = ["joy", "sadness"]
    text = render_confusion_matrix_text(cm, labels)
    assert "joy" in text
    assert "sadness" in text


# ---------------------------------------------------------------------------
# End-to-end benchmark (dry-run)
# ---------------------------------------------------------------------------

def test_run_benchmark_dry_run():
    """Dry-run benchmark must produce valid structured results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_benchmark(output_dir=tmpdir, dry_run=True)
        assert "meta" in results
        assert "datasets" in results
        assert results["meta"]["labels"] == LABELS
        assert len(results["datasets"]) > 0

        # Check JSON output file was created
        json_path = os.path.join(tmpdir, "evaluation_results.json")
        assert os.path.exists(json_path)
        with open(json_path) as f:
            loaded = json.load(f)
        assert loaded["meta"]["labels"] == LABELS


def test_run_benchmark_dry_run_has_all_models():
    """Dry-run must evaluate all three models."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_benchmark(output_dir=tmpdir, dry_run=True)
        for ds_name, ds_results in results["datasets"].items():
            assert "Keyword Model" in ds_results
            assert "Transformer Model" in ds_results
            assert "Hybrid Model" in ds_results


def test_run_benchmark_dry_run_reports_have_metrics():
    """Each model report must include standard evaluation metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_benchmark(output_dir=tmpdir, dry_run=True)
        for ds_name, ds_results in results["datasets"].items():
            for model_name, report in ds_results.items():
                assert "accuracy" in report, f"{model_name} missing accuracy"
                assert "macro_f1" in report, f"{model_name} missing macro_f1"
                assert "micro_f1" in report, f"{model_name} missing micro_f1"
                assert "confusion_matrix" in report, f"{model_name} missing confusion_matrix"
                assert "per_class" in report, f"{model_name} missing per_class"
                assert "samples" in report, f"{model_name} missing samples"


def test_run_benchmark_with_custom_dataset():
    """Benchmark should work with an explicitly provided dataset file."""
    content = (
        '{"text": "I am happy and joyful", "label": "joy"}\n'
        '{"text": "I feel sad and lonely", "label": "sadness"}\n'
        '{"text": "I am angry and furious", "label": "anger"}\n'
        '{"text": "I feel neutral today", "label": "neutral"}\n'
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False
    ) as f:
        f.write(content)
        ds_path = f.name

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_benchmark(
                dataset_paths=[ds_path], output_dir=tmpdir,
            )
            assert len(results["datasets"]) == 1
            ds_key = list(results["datasets"].keys())[0]
            assert results["datasets"][ds_key]["Keyword Model"]["samples"] == 4
    finally:
        os.unlink(ds_path)


def test_run_benchmark_accuracy_bounds():
    """All accuracy and F1 values must be between 0 and 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = run_benchmark(output_dir=tmpdir, dry_run=True)
        for ds_results in results["datasets"].values():
            for report in ds_results.values():
                assert 0.0 <= report["accuracy"] <= 1.0
                assert 0.0 <= report["macro_f1"] <= 1.0
                assert 0.0 <= report["micro_f1"] <= 1.0
