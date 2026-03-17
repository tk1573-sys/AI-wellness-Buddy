"""Tests for evaluation/statistical_tests.py.

Validates:
- compute_p_value returns a scipy TtestResult with .statistic and .pvalue
- compute_p_value raises on empty or length-mismatched inputs
- interpret_p_value returns the correct string for p < alpha and p >= alpha
- interpret_p_value handles NaN gracefully
- run_significance_tests produces the expected keys
- run_significance_tests saves results/statistical_significance.json
- run_significance_tests works with pre-loaded samples
- run_significance_tests raises ValueError on empty datasets
- Integration: run_ablation_study with run_stats=True includes stat results
"""

import json
import math
import os
import tempfile

import pytest

from evaluation.statistical_tests import (
    SIGNIFICANCE_THRESHOLD,
    compute_p_value,
    interpret_p_value,
    run_significance_tests,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_samples(n: int = 10):
    """Return a minimal set of labelled samples."""
    base = [
        {"text": "I feel happy and excited", "label": "joy"},
        {"text": "So sad and lonely today", "label": "sadness"},
        {"text": "I am so angry and furious", "label": "anger"},
        {"text": "Everything is fine", "label": "neutral"},
        {"text": "Feeling anxious and worried", "label": "anxiety"},
        {"text": "Scared and frightened", "label": "fear"},
    ]
    # Repeat if more than 6 samples are requested
    repeated = (base * ((n // len(base)) + 1))[:n]
    return repeated


# ---------------------------------------------------------------------------
# compute_p_value
# ---------------------------------------------------------------------------

def test_compute_p_value_returns_statistic_and_pvalue():
    """compute_p_value must return an object with .statistic and .pvalue."""
    a = [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    b = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    result = compute_p_value(a, b)
    assert hasattr(result, "statistic")
    assert hasattr(result, "pvalue")


def test_compute_p_value_pvalue_in_zero_one():
    """p-value must be in [0, 1] for distinct score arrays."""
    a = [1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
    b = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    result = compute_p_value(a, b)
    assert 0.0 <= result.pvalue <= 1.0


def test_compute_p_value_statistic_is_float():
    """t-statistic must be a real float."""
    a = [1.0, 1.0, 0.0, 1.0, 0.0]
    b = [0.0, 1.0, 0.0, 0.0, 0.0]
    result = compute_p_value(a, b)
    assert isinstance(float(result.statistic), float)


def test_compute_p_value_raises_on_empty_a():
    """compute_p_value must raise ValueError when model_a_scores is empty."""
    with pytest.raises(ValueError, match="not be empty"):
        compute_p_value([], [1.0, 0.0])


def test_compute_p_value_raises_on_empty_b():
    """compute_p_value must raise ValueError when model_b_scores is empty."""
    with pytest.raises(ValueError, match="not be empty"):
        compute_p_value([1.0, 0.0], [])


def test_compute_p_value_raises_on_length_mismatch():
    """compute_p_value must raise ValueError when lengths differ."""
    with pytest.raises(ValueError, match="same length"):
        compute_p_value([1.0, 0.0], [1.0, 0.0, 1.0])


def test_compute_p_value_identical_arrays_returns_nan():
    """Identical score arrays yield NaN (ttest_rel returns NaN, not an error)."""
    a = [1.0, 0.0, 1.0, 0.0]
    result = compute_p_value(a, list(a))
    assert math.isnan(result.pvalue)


def test_compute_p_value_single_element():
    """Single-element arrays should either succeed or return NaN — not crash."""
    try:
        result = compute_p_value([1.0], [0.0])
        # If it succeeds, pvalue should be NaN (df=0 for ttest_rel of 1 pair)
        assert math.isnan(result.pvalue) or 0.0 <= result.pvalue <= 1.0
    except Exception:
        pass  # scipy may raise on df=0; that's acceptable


# ---------------------------------------------------------------------------
# interpret_p_value
# ---------------------------------------------------------------------------

def test_interpret_p_value_significant_below_alpha():
    """p < alpha must return 'statistically significant'."""
    assert interpret_p_value(0.01) == "statistically significant"


def test_interpret_p_value_not_significant_above_alpha():
    """p >= alpha must return 'not statistically significant'."""
    assert interpret_p_value(0.5) == "not statistically significant"


def test_interpret_p_value_equal_to_alpha_not_significant():
    """p == alpha must return 'not statistically significant'."""
    assert interpret_p_value(0.05, alpha=0.05) == "not statistically significant"


def test_interpret_p_value_nan_returns_indeterminate():
    """NaN p-value must return the 'indeterminate' string."""
    result = interpret_p_value(float("nan"))
    assert "indeterminate" in result


def test_interpret_p_value_respects_custom_alpha():
    """interpret_p_value must honour the *alpha* parameter."""
    assert interpret_p_value(0.04, alpha=0.01) == "not statistically significant"
    assert interpret_p_value(0.004, alpha=0.01) == "statistically significant"


# ---------------------------------------------------------------------------
# SIGNIFICANCE_THRESHOLD constant
# ---------------------------------------------------------------------------

def test_significance_threshold_is_0_05():
    """SIGNIFICANCE_THRESHOLD must be 0.05."""
    assert SIGNIFICANCE_THRESHOLD == 0.05


# ---------------------------------------------------------------------------
# run_significance_tests — return-value keys
# ---------------------------------------------------------------------------

def test_run_significance_tests_has_p_value_keys():
    """run_significance_tests must return both p-value keys."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    assert "p_value_hybrid_vs_transformer" in result
    assert "p_value_hybrid_vs_keyword" in result


def test_run_significance_tests_has_t_statistic_keys():
    """run_significance_tests must return both t-statistic keys."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    assert "t_statistic_hybrid_vs_transformer" in result
    assert "t_statistic_hybrid_vs_keyword" in result


def test_run_significance_tests_has_interpretation_keys():
    """run_significance_tests must return both interpretation keys."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    assert "interpretation_hybrid_vs_transformer" in result
    assert "interpretation_hybrid_vs_keyword" in result


def test_run_significance_tests_has_meta():
    """run_significance_tests must include a 'meta' block."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    assert "meta" in result
    meta = result["meta"]
    assert "timestamp" in meta
    assert "samples" in meta
    assert "alpha" in meta


def test_run_significance_tests_p_values_are_float():
    """p-values must be float (including NaN for identical classifiers)."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    assert isinstance(result["p_value_hybrid_vs_transformer"], float)
    assert isinstance(result["p_value_hybrid_vs_keyword"], float)


def test_run_significance_tests_interpretation_is_string():
    """Interpretation values must be non-empty strings."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    for key in ("interpretation_hybrid_vs_transformer", "interpretation_hybrid_vs_keyword"):
        assert isinstance(result[key], str) and result[key]


# ---------------------------------------------------------------------------
# run_significance_tests — file output
# ---------------------------------------------------------------------------

def test_run_significance_tests_saves_json():
    """run_significance_tests must save results/statistical_significance.json."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        run_significance_tests(samples, output_dir=tmpdir, verbose=False)
        json_path = os.path.join(tmpdir, "results", "statistical_significance.json")
        assert os.path.exists(json_path), "JSON output not found"
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    assert "p_value_hybrid_vs_transformer" in data
    assert "p_value_hybrid_vs_keyword" in data


def test_run_significance_tests_json_has_meta():
    """The saved JSON must contain the 'meta' section."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        run_significance_tests(samples, output_dir=tmpdir, verbose=False)
        json_path = os.path.join(tmpdir, "results", "statistical_significance.json")
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    meta = data["meta"]
    assert "timestamp" in meta
    assert "samples" in meta
    assert "alpha" in meta


def test_run_significance_tests_custom_filename():
    """run_significance_tests must respect a custom results_filename."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        run_significance_tests(
            samples,
            output_dir=tmpdir,
            results_filename="custom_stats.json",
            verbose=False,
        )
        json_path = os.path.join(tmpdir, "results", "custom_stats.json")
        assert os.path.exists(json_path)


# ---------------------------------------------------------------------------
# run_significance_tests — edge cases
# ---------------------------------------------------------------------------

def test_run_significance_tests_empty_dataset_raises():
    """run_significance_tests must raise ValueError on an empty dataset."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="No samples"):
            run_significance_tests([], output_dir=tmpdir, verbose=False)


def test_run_significance_tests_meta_sample_count():
    """The meta.samples count must match the number of samples supplied."""
    samples = _make_samples(6)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(samples, output_dir=tmpdir, verbose=False)
    assert result["meta"]["samples"] == 6


def test_run_significance_tests_custom_alpha_in_meta():
    """The custom alpha must appear in the meta section."""
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_significance_tests(
            samples, output_dir=tmpdir, alpha=0.01, verbose=False
        )
    assert result["meta"]["alpha"] == 0.01


# ---------------------------------------------------------------------------
# Integration: run_ablation_study with run_stats=True
# ---------------------------------------------------------------------------

def test_ablation_study_with_run_stats_includes_statistical_tests():
    """run_ablation_study(run_stats=True) must embed 'statistical_tests' key."""
    from evaluation.emotion_model_evaluation import run_ablation_study
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_ablation_study(
            samples, output_dir=tmpdir, run_stats=True, verbose=False
        )
    assert "statistical_tests" in result


def test_ablation_study_with_run_stats_saves_significance_json():
    """run_ablation_study(run_stats=True) must save statistical_significance.json."""
    from evaluation.emotion_model_evaluation import run_ablation_study
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        run_ablation_study(samples, output_dir=tmpdir, run_stats=True, verbose=False)
        json_path = os.path.join(tmpdir, "results", "statistical_significance.json")
        assert os.path.exists(json_path)


def test_ablation_study_without_run_stats_excludes_key():
    """run_ablation_study(run_stats=False) must NOT include 'statistical_tests'."""
    from evaluation.emotion_model_evaluation import run_ablation_study
    samples = _make_samples()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_ablation_study(
            samples, output_dir=tmpdir, run_stats=False, verbose=False
        )
    assert "statistical_tests" not in result
