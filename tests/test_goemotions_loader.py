"""Tests for the GoEmotions dataset loader.

Validates:
- Label mapping from GoEmotions labels to system emotion classes
- Text cleaning and normalisation
- JSONL loading (valid, blank lines, empty text)
- CSV loading
- max_samples limit
- Invalid/missing rows handled gracefully
- crisis label present in SYSTEM_LABELS
- load_goemotions_hf raises ImportError when datasets library is unavailable
"""

import csv
import json
import os
import sys
import tempfile
import unittest.mock as mock

from datasets.goemotions_loader import (
    GOEMOTIONS_LABEL_MAP,
    SYSTEM_LABELS,
    load_goemotions,
    load_goemotions_hf,
    map_label,
)


# ------------------------------------------------------------------
# Label mapping
# ------------------------------------------------------------------

def test_known_goemotions_labels_mapped():
    """Well-known GoEmotions labels must map to valid system labels."""
    assert map_label("admiration") == "joy"
    assert map_label("approval") == "joy"
    assert map_label("disappointment") == "sadness"
    assert map_label("anger") == "anger"
    assert map_label("fear") == "fear"
    assert map_label("nervousness") == "anxiety"
    assert map_label("neutral") == "neutral"


def test_unknown_label_defaults_neutral():
    """Unknown labels must default to 'neutral'."""
    assert map_label("xyzzy_unknown") == "neutral"


def test_case_insensitive_mapping():
    """Label mapping must be case-insensitive."""
    assert map_label("ADMIRATION") == "joy"
    assert map_label("Sadness") == "sadness"


def test_all_mapped_labels_are_system_labels():
    """Every mapped value must be a recognised system label."""
    for mapped in GOEMOTIONS_LABEL_MAP.values():
        assert mapped in SYSTEM_LABELS


# ------------------------------------------------------------------
# JSONL loading
# ------------------------------------------------------------------

def _write_jsonl(rows):
    """Write rows to a temp JSONL file and return the path."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for row in rows:
            json.dump(row, f)
            f.write("\n")
    return path


def test_load_jsonl_basic():
    """Basic JSONL file with text + labels must load correctly."""
    path = _write_jsonl([
        {"text": "I feel happy", "labels": ["joy"]},
        {"text": "I am sad", "labels": ["sadness"]},
    ])
    try:
        samples = load_goemotions(path)
        assert len(samples) == 2
        assert samples[0]["label"] == "joy"
        assert samples[1]["label"] == "sadness"
    finally:
        os.unlink(path)


def test_load_jsonl_skips_blank_lines():
    """Blank lines in JSONL must be silently skipped."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w") as f:
        f.write('{"text": "hello", "labels": ["neutral"]}\n')
        f.write("\n")
        f.write("  \n")
        f.write('{"text": "world", "labels": ["joy"]}\n')
    try:
        samples = load_goemotions(path)
        assert len(samples) == 2
    finally:
        os.unlink(path)


def test_load_jsonl_empty_text_skipped():
    """Rows with empty text must be skipped."""
    path = _write_jsonl([
        {"text": "", "labels": ["joy"]},
        {"text": "valid text", "labels": ["sadness"]},
    ])
    try:
        samples = load_goemotions(path)
        assert len(samples) == 1
        assert samples[0]["text"] == "valid text"
    finally:
        os.unlink(path)


def test_load_jsonl_list_labels():
    """When 'labels' is a list, the first item should be used."""
    path = _write_jsonl([
        {"text": "mixed emotions", "labels": ["admiration", "joy"]},
    ])
    try:
        samples = load_goemotions(path)
        assert len(samples) == 1
        assert samples[0]["label"] == "joy"  # admiration → joy
    finally:
        os.unlink(path)


# ------------------------------------------------------------------
# CSV loading
# ------------------------------------------------------------------

def test_load_csv():
    """CSV file with text + label columns must load correctly."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "labels"])
        writer.writerow(["I am happy", "joy"])
        writer.writerow(["I am sad", "sadness"])
    try:
        samples = load_goemotions(path, label_key="labels")
        assert len(samples) == 2
    finally:
        os.unlink(path)


# ------------------------------------------------------------------
# max_samples limit
# ------------------------------------------------------------------

def test_max_samples_respected():
    """max_samples must cap the number of returned samples."""
    path = _write_jsonl([
        {"text": f"sample {i}", "labels": ["neutral"]}
        for i in range(20)
    ])
    try:
        samples = load_goemotions(path, max_samples=5)
        assert len(samples) == 5
    finally:
        os.unlink(path)


# ------------------------------------------------------------------
# Text cleaning
# ------------------------------------------------------------------

def test_text_whitespace_normalised():
    """Extra whitespace must be collapsed to single spaces."""
    path = _write_jsonl([
        {"text": "  lots   of   spaces  ", "labels": ["neutral"]},
    ])
    try:
        samples = load_goemotions(path)
        assert samples[0]["text"] == "lots of spaces"
    finally:
        os.unlink(path)


# ------------------------------------------------------------------
# SYSTEM_LABELS completeness
# ------------------------------------------------------------------

def test_crisis_in_system_labels():
    """'crisis' must be present in SYSTEM_LABELS for full schema coverage."""
    assert "crisis" in SYSTEM_LABELS


def test_system_labels_contains_all_required():
    """SYSTEM_LABELS must include all seven emotion classes."""
    required = {"joy", "sadness", "anger", "fear", "anxiety", "neutral", "crisis"}
    assert required.issubset(set(SYSTEM_LABELS))


# ------------------------------------------------------------------
# HuggingFace datasets loader
# ------------------------------------------------------------------

def _make_mock_hf_dataset(label_names: list, rows: list):
    """Build a minimal mock HuggingFace dataset with the go_emotions schema.

    The real go_emotions dataset exposes:
        ds.features["labels"].feature.names  (Sequence(ClassLabel).feature.names)
    """
    mock_class_label = mock.MagicMock()
    mock_class_label.names = label_names

    mock_sequence_feature = mock.MagicMock()
    mock_sequence_feature.feature = mock_class_label

    mock_features = mock.MagicMock()
    mock_features.__getitem__ = mock.Mock(return_value=mock_sequence_feature)

    mock_ds = mock.MagicMock()
    mock_ds.features = mock_features
    mock_ds.__iter__ = mock.Mock(return_value=iter(rows))
    return mock_ds


def _mock_datasets_module(mock_ds):
    """Return a mock 'datasets' module whose load_dataset returns *mock_ds*."""
    mock_load_dataset = mock.MagicMock(return_value=mock_ds)
    mod = mock.MagicMock()
    mod.load_dataset = mock_load_dataset
    return mod


def test_load_goemotions_hf_raises_without_datasets_lib():
    """load_goemotions_hf must raise ImportError when 'datasets' is absent."""
    import pytest
    with pytest.raises(ImportError, match="datasets"):
        with mock.patch.dict(sys.modules, {"datasets": None}):
            load_goemotions_hf()


def test_load_goemotions_hf_uses_first_label_per_row():
    """load_goemotions_hf must pick the first label for multi-label rows."""
    label_names = ["admiration", "joy", "sadness", "neutral"]
    rows = [
        {"text": "I feel great", "labels": [0]},       # admiration → joy
        {"text": "Feeling low today", "labels": [2]},  # sadness → sadness
    ]
    mock_ds = _make_mock_hf_dataset(label_names, rows)
    mock_mod = _mock_datasets_module(mock_ds)

    with mock.patch.dict(sys.modules, {"datasets": mock_mod}):
        samples = load_goemotions_hf(split="test", max_samples=10)

    assert len(samples) == 2
    assert samples[0]["label"] == "joy"      # admiration → joy
    assert samples[1]["label"] == "sadness"  # sadness → sadness


def test_load_goemotions_hf_max_samples_respected():
    """load_goemotions_hf must honour the max_samples limit."""
    mock_ds = _make_mock_hf_dataset(
        label_names=["neutral"],
        rows=[{"text": f"sample {i}", "labels": [0]} for i in range(20)],
    )
    mock_mod = _mock_datasets_module(mock_ds)

    with mock.patch.dict(sys.modules, {"datasets": mock_mod}):
        samples = load_goemotions_hf(split="test", max_samples=5)

    assert len(samples) == 5


def test_load_goemotions_hf_skips_empty_text():
    """load_goemotions_hf must skip rows with empty text."""
    mock_ds = _make_mock_hf_dataset(
        label_names=["neutral"],
        rows=[
            {"text": "", "labels": [0]},
            {"text": "valid text", "labels": [0]},
        ],
    )
    mock_mod = _mock_datasets_module(mock_ds)

    with mock.patch.dict(sys.modules, {"datasets": mock_mod}):
        samples = load_goemotions_hf(split="test")

    assert len(samples) == 1
    assert samples[0]["text"] == "valid text"
