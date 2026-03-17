"""Tests for the ablation study pipeline.

Validates:
- get_classifier returns callable for all three modes
- get_classifier raises ValueError for unknown modes
- run_ablation_study produces metrics for all three models
- run_ablation_study saves JSON and CSV to the specified output directory
- run_ablation_study uses the same dataset for all models
- pre-loaded samples are accepted in place of a file path
- Comparison table formatting
"""

import csv
import json
import os
import tempfile

import pytest

from evaluation.emotion_model_evaluation import (
    ABLATION_MODELS,
    _format_comparison_table,
    get_classifier,
    run_ablation_study,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_synthetic_jsonl(path: str) -> None:
    """Write a minimal GoEmotions-style JSONL file."""
    rows = [
        {"text": "I feel happy and excited", "labels": ["joy"]},
        {"text": "So sad and lonely today", "labels": ["sadness"]},
        {"text": "I am so angry and furious", "labels": ["anger"]},
        {"text": "Everything is perfectly fine", "labels": ["neutral"]},
        {"text": "Feeling anxious and worried", "labels": ["anxiety"]},
        {"text": "Scared and frightened by everything", "labels": ["fear"]},
    ]
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# get_classifier
# ---------------------------------------------------------------------------

def test_get_classifier_keyword_returns_callable():
    """get_classifier('keyword') must return a callable."""
    clf = get_classifier("keyword")
    assert callable(clf)


def test_get_classifier_transformer_returns_callable():
    """get_classifier('transformer') must return a callable."""
    clf = get_classifier("transformer")
    assert callable(clf)


def test_get_classifier_hybrid_returns_callable():
    """get_classifier('hybrid') must return a callable."""
    clf = get_classifier("hybrid")
    assert callable(clf)


def test_get_classifier_unknown_raises_value_error():
    """get_classifier with an unrecognised mode must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown classifier mode"):
        get_classifier("magic_model")


def test_get_classifier_case_insensitive():
    """get_classifier must accept upper-case mode names."""
    clf = get_classifier("KEYWORD")
    assert callable(clf)


def test_get_classifier_keyword_returns_system_label():
    """Keyword classifier output must be a system emotion label."""
    from evaluation.emotion_model_evaluation import SYSTEM_LABELS
    clf = get_classifier("keyword")
    result = clf("I feel so happy today")
    assert result in SYSTEM_LABELS


def test_get_classifier_transformer_returns_system_label():
    """Transformer classifier output must be a system emotion label."""
    from evaluation.emotion_model_evaluation import SYSTEM_LABELS
    clf = get_classifier("transformer")
    result = clf("I feel so happy today")
    assert result in SYSTEM_LABELS


def test_get_classifier_hybrid_returns_system_label():
    """Hybrid classifier output must be a system emotion label."""
    from evaluation.emotion_model_evaluation import SYSTEM_LABELS
    clf = get_classifier("hybrid")
    result = clf("I feel so happy today")
    assert result in SYSTEM_LABELS


# ---------------------------------------------------------------------------
# ABLATION_MODELS constant
# ---------------------------------------------------------------------------

def test_ablation_models_contains_three_modes():
    """ABLATION_MODELS must list exactly the three ablation modes."""
    assert set(ABLATION_MODELS) == {"keyword", "transformer", "hybrid"}


# ---------------------------------------------------------------------------
# run_ablation_study — from file path
# ---------------------------------------------------------------------------

def test_run_ablation_study_returns_all_models():
    """run_ablation_study must include results for every ablation model."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_ablation_study(path, output_dir=tmpdir, verbose=False)
        for mode in ABLATION_MODELS:
            assert mode in result, f"Missing model '{mode}' in ablation results"
    finally:
        os.unlink(path)


def test_run_ablation_study_accuracy_in_range():
    """Each model's accuracy must be between 0 and 1."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_ablation_study(path, output_dir=tmpdir, verbose=False)
        for mode in ABLATION_MODELS:
            assert 0.0 <= result[mode]["accuracy"] <= 1.0
    finally:
        os.unlink(path)


def test_run_ablation_study_macro_f1_in_range():
    """Each model's macro_f1 must be between 0 and 1."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_ablation_study(path, output_dir=tmpdir, verbose=False)
        for mode in ABLATION_MODELS:
            assert 0.0 <= result[mode]["macro_f1"] <= 1.0
    finally:
        os.unlink(path)


def test_run_ablation_study_sample_count_consistent():
    """All three models must see the same number of samples."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_ablation_study(path, output_dir=tmpdir, verbose=False)
        sample_counts = {result[mode]["samples"] for mode in ABLATION_MODELS}
        assert len(sample_counts) == 1, "All models must use the same sample count"
    finally:
        os.unlink(path)


def test_run_ablation_study_saves_json():
    """run_ablation_study must write ablation_results.json."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_ablation_study(path, output_dir=tmpdir, verbose=False)
            json_path = os.path.join(tmpdir, "results", "ablation_results.json")
            assert os.path.exists(json_path), "JSON output file not found"
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            assert "meta" in data
            for mode in ABLATION_MODELS:
                assert mode in data
    finally:
        os.unlink(path)


def test_run_ablation_study_saves_csv():
    """run_ablation_study must write ablation_comparison.csv."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_ablation_study(path, output_dir=tmpdir, verbose=False)
            csv_path = os.path.join(tmpdir, "results", "ablation_comparison.csv")
            assert os.path.exists(csv_path), "CSV output file not found"
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            assert len(rows) == len(ABLATION_MODELS)
            model_names_in_csv = {r["model"] for r in rows}
            assert model_names_in_csv == set(ABLATION_MODELS)
    finally:
        os.unlink(path)


def test_run_ablation_study_json_has_meta():
    """The JSON output must contain a 'meta' section with dataset info."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    _write_synthetic_jsonl(path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_ablation_study(path, output_dir=tmpdir, verbose=False)
            json_path = os.path.join(tmpdir, "results", "ablation_results.json")
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        meta = data["meta"]
        assert "timestamp" in meta
        assert "samples" in meta
        assert "labels" in meta
        assert "models" in meta
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# run_ablation_study — from pre-loaded samples
# ---------------------------------------------------------------------------

def test_run_ablation_study_accepts_preloaded_samples():
    """run_ablation_study must accept a list of dicts instead of a file path."""
    samples = [
        {"text": "I feel happy and excited", "label": "joy"},
        {"text": "So sad today", "label": "sadness"},
        {"text": "Really angry right now", "label": "anger"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_ablation_study(samples, output_dir=tmpdir, verbose=False)
    for mode in ABLATION_MODELS:
        assert mode in result


def test_run_ablation_study_empty_dataset_raises():
    """run_ablation_study must raise ValueError when the dataset is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="No samples"):
            run_ablation_study([], output_dir=tmpdir, verbose=False)


# ---------------------------------------------------------------------------
# CSV content
# ---------------------------------------------------------------------------

def test_csv_contains_accuracy_column():
    """The CSV export must include an 'accuracy' column for each model."""
    samples = [
        {"text": "I feel happy and excited", "label": "joy"},
        {"text": "So sad today", "label": "sadness"},
        {"text": "Really angry right now", "label": "anger"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        run_ablation_study(samples, output_dir=tmpdir, verbose=False)
        csv_path = os.path.join(tmpdir, "results", "ablation_comparison.csv")
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    for row in rows:
        assert "accuracy" in row
        assert float(row["accuracy"]) >= 0.0


def test_csv_contains_macro_f1_column():
    """The CSV export must include a 'macro_f1' column."""
    samples = [
        {"text": "I feel happy", "label": "joy"},
        {"text": "I am so sad", "label": "sadness"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        run_ablation_study(samples, output_dir=tmpdir, verbose=False)
        csv_path = os.path.join(tmpdir, "results", "ablation_comparison.csv")
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    for row in rows:
        assert "macro_f1" in row


# ---------------------------------------------------------------------------
# Comparison table formatting
# ---------------------------------------------------------------------------

def test_format_comparison_table_contains_headers():
    """_format_comparison_table must include column headers."""
    fake_results = {
        "keyword": {"accuracy": 0.8, "precision_macro": 0.75, "recall_macro": 0.72, "macro_f1": 0.73},
        "transformer": {"accuracy": 0.85, "precision_macro": 0.82, "recall_macro": 0.80, "macro_f1": 0.81},
        "hybrid": {"accuracy": 0.88, "precision_macro": 0.85, "recall_macro": 0.84, "macro_f1": 0.84},
    }
    table = _format_comparison_table(fake_results)
    assert "Accuracy" in table
    assert "Macro F1" in table


def test_format_comparison_table_contains_model_names():
    """_format_comparison_table must include each model name as a row."""
    fake_results = {
        "keyword": {"accuracy": 0.5, "precision_macro": 0.5, "recall_macro": 0.5, "macro_f1": 0.5},
        "transformer": {"accuracy": 0.6, "precision_macro": 0.6, "recall_macro": 0.6, "macro_f1": 0.6},
        "hybrid": {"accuracy": 0.7, "precision_macro": 0.7, "recall_macro": 0.7, "macro_f1": 0.7},
    }
    table = _format_comparison_table(fake_results)
    for model in fake_results:
        assert model in table
