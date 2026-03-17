"""Tests for evaluation/report_generator.py.

Validates:
- generate_classification_report output structure and values
- Support counts derived from confusion matrix
- generate_model_comparison_summary ordering and fields
- generate_paper_tables Markdown output format
- generate_report file outputs (JSON + CSV)
- generate_report accepts pre-computed ablation results
- generate_report accepts pre-loaded sample lists
- Edge cases: no models, missing keys, empty confusion matrix
"""

import csv
import json
import os
import tempfile

import pytest

from evaluation.report_generator import (
    generate_classification_report,
    generate_model_comparison_summary,
    generate_paper_tables,
    generate_report,
)


# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

_LABELS = ["joy", "sadness"]


def _model_metrics(accuracy=0.8, macro_f1=0.8, prefix=""):
    """Return a single-model metrics dict with realistic structure."""
    return {
        "accuracy":        accuracy,
        "precision_macro": macro_f1,
        "recall_macro":    macro_f1,
        "macro_f1":        macro_f1,
        "samples":         10,
        "per_class": {
            "joy": {
                "precision": 0.9,
                "recall":    0.8,
                "f1":        round(2 * 0.9 * 0.8 / (0.9 + 0.8), 4),
            },
            "sadness": {
                "precision": 0.7,
                "recall":    0.8,
                "f1":        round(2 * 0.7 * 0.8 / (0.7 + 0.8), 4),
            },
        },
        "confusion_matrix": {
            "joy":     {"joy": 4, "sadness": 1},
            "sadness": {"joy": 1, "sadness": 4},
        },
    }


def _ablation_results():
    """Return a minimal ablation results dict with three models."""
    return {
        "meta": {
            "timestamp": "2026-01-01T00:00:00Z",
            "dataset":   "test",
            "samples":   10,
            "labels":    _LABELS,
        },
        "keyword":     _model_metrics(accuracy=0.5,  macro_f1=0.5),
        "transformer": _model_metrics(accuracy=0.65, macro_f1=0.65),
        "hybrid":      _model_metrics(accuracy=0.8,  macro_f1=0.8),
    }


# ---------------------------------------------------------------------------
# generate_classification_report
# ---------------------------------------------------------------------------

class TestGenerateClassificationReport:

    def test_required_top_level_keys(self):
        report = generate_classification_report(_model_metrics(), _LABELS)
        assert "per_class" in report
        assert "macro" in report
        assert "accuracy" in report
        assert "samples" in report

    def test_per_class_has_all_labels(self):
        report = generate_classification_report(_model_metrics(), _LABELS)
        for lbl in _LABELS:
            assert lbl in report["per_class"]

    def test_per_class_metrics_keys(self):
        report = generate_classification_report(_model_metrics(), _LABELS)
        for lbl in _LABELS:
            m = report["per_class"][lbl]
            assert "precision" in m
            assert "recall" in m
            assert "f1" in m
            assert "support" in m

    def test_support_from_confusion_matrix(self):
        """Support for 'joy' = sum of row in confusion_matrix['joy']."""
        m = _model_metrics()
        report = generate_classification_report(m, _LABELS)
        # confusion_matrix['joy'] = {'joy': 4, 'sadness': 1} → support = 5
        assert report["per_class"]["joy"]["support"] == 5

    def test_support_zero_for_missing_label(self):
        """Labels not in the confusion matrix should have support 0."""
        report = generate_classification_report(_model_metrics(), ["joy", "crisis"])
        assert report["per_class"]["crisis"]["support"] == 0

    def test_macro_keys(self):
        macro = generate_classification_report(_model_metrics(), _LABELS)["macro"]
        assert "precision" in macro
        assert "recall" in macro
        assert "f1" in macro

    def test_accuracy_is_float(self):
        report = generate_classification_report(_model_metrics(), _LABELS)
        assert isinstance(report["accuracy"], float)

    def test_samples_is_int(self):
        report = generate_classification_report(_model_metrics(), _LABELS)
        assert isinstance(report["samples"], int)
        assert report["samples"] == 10

    def test_values_rounded_to_4dp(self):
        report = generate_classification_report(_model_metrics(), _LABELS)
        for lbl in _LABELS:
            for col in ("precision", "recall", "f1"):
                val = report["per_class"][lbl][col]
                assert val == round(val, 4)

    def test_defaults_labels_from_per_class_keys(self):
        """When labels=None, fall back to per_class keys."""
        report = generate_classification_report(_model_metrics())
        assert "joy" in report["per_class"]
        assert "sadness" in report["per_class"]

    def test_missing_confusion_matrix_gives_zero_support(self):
        m = {
            "accuracy": 0.5, "precision_macro": 0.5, "recall_macro": 0.5,
            "macro_f1": 0.5, "samples": 4,
            "per_class": {"joy": {"precision": 0.5, "recall": 0.5, "f1": 0.5}},
        }
        report = generate_classification_report(m, ["joy"])
        assert report["per_class"]["joy"]["support"] == 0


# ---------------------------------------------------------------------------
# generate_model_comparison_summary
# ---------------------------------------------------------------------------

class TestGenerateModelComparisonSummary:

    def test_returns_list(self):
        assert isinstance(generate_model_comparison_summary(_ablation_results()), list)

    def test_one_row_per_model(self):
        rows = generate_model_comparison_summary(_ablation_results())
        model_names = [r["model"] for r in rows]
        assert set(model_names) == {"keyword", "transformer", "hybrid"}

    def test_sorted_by_descending_macro_f1(self):
        rows = generate_model_comparison_summary(_ablation_results())
        f1_values = [r["macro_f1"] for r in rows]
        assert f1_values == sorted(f1_values, reverse=True)

    def test_row_has_required_fields(self):
        rows = generate_model_comparison_summary(_ablation_results())
        for row in rows:
            for col in ("model", "accuracy", "precision_macro", "recall_macro",
                        "macro_f1", "samples"):
                assert col in row

    def test_meta_key_excluded(self):
        rows = generate_model_comparison_summary(_ablation_results())
        names = [r["model"] for r in rows]
        assert "meta" not in names

    def test_statistical_tests_key_excluded(self):
        abl = _ablation_results()
        abl["statistical_tests"] = {"p_value_hybrid_vs_transformer": 0.01}
        rows = generate_model_comparison_summary(abl)
        names = [r["model"] for r in rows]
        assert "statistical_tests" not in names

    def test_values_are_rounded(self):
        rows = generate_model_comparison_summary(_ablation_results())
        for row in rows:
            for col in ("accuracy", "precision_macro", "recall_macro", "macro_f1"):
                val = row[col]
                assert val == round(val, 4)

    def test_hybrid_is_first_when_best(self):
        rows = generate_model_comparison_summary(_ablation_results())
        assert rows[0]["model"] == "hybrid"

    def test_empty_ablation_returns_empty_list(self):
        rows = generate_model_comparison_summary({"meta": {}})
        assert rows == []


# ---------------------------------------------------------------------------
# generate_paper_tables
# ---------------------------------------------------------------------------

class TestGeneratePaperTables:

    def test_returns_dict_with_expected_keys(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert "model_comparison" in tables
        assert "per_class_hybrid" in tables

    def test_model_comparison_is_string(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert isinstance(tables["model_comparison"], str)

    def test_model_comparison_contains_pipe(self):
        """Markdown tables use pipe characters."""
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert "|" in tables["model_comparison"]

    def test_model_comparison_contains_all_model_names(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        for name in ("keyword", "transformer", "hybrid"):
            assert name in tables["model_comparison"]

    def test_model_comparison_header_row(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        header_line = tables["model_comparison"].splitlines()[0]
        for col in ("Model", "Precision", "Recall", "F1", "Accuracy"):
            assert col in header_line

    def test_per_class_hybrid_is_string(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert isinstance(tables["per_class_hybrid"], str)

    def test_per_class_hybrid_contains_pipe(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert "|" in tables["per_class_hybrid"]

    def test_per_class_hybrid_contains_class_names(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        for lbl in _LABELS:
            assert lbl in tables["per_class_hybrid"]

    def test_per_class_hybrid_contains_support_column(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert "Support" in tables["per_class_hybrid"]

    def test_per_class_hybrid_contains_macro_avg(self):
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        assert "macro avg" in tables["per_class_hybrid"]

    def test_separator_row_present(self):
        """The header separator row must use dashes."""
        tables = generate_paper_tables(_ablation_results(), _LABELS)
        lines = tables["model_comparison"].splitlines()
        separator_line = lines[1]  # second line is the separator
        assert "---" in separator_line

    def test_no_model_fallback_uses_first_available(self):
        """When 'hybrid' key is absent, falls back to first available model."""
        abl = {
            "meta":    _ablation_results()["meta"],
            "keyword": _model_metrics(),
        }
        tables = generate_paper_tables(abl, _LABELS)
        assert "|" in tables["per_class_hybrid"]


# ---------------------------------------------------------------------------
# generate_report — return structure
# ---------------------------------------------------------------------------

class TestGenerateReportStructure:

    def test_top_level_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_report(_ablation_results(), output_dir=tmpdir,
                                     verbose=False, labels=_LABELS)
        for key in ("meta", "classification_reports", "model_comparison", "paper_tables"):
            assert key in result

    def test_meta_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_report(_ablation_results(), output_dir=tmpdir,
                                     verbose=False, labels=_LABELS)
        for k in ("timestamp", "dataset", "samples", "labels"):
            assert k in result["meta"]

    def test_classification_reports_has_all_models(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_report(_ablation_results(), output_dir=tmpdir,
                                     verbose=False, labels=_LABELS)
        for name in ("keyword", "transformer", "hybrid"):
            assert name in result["classification_reports"]

    def test_model_comparison_is_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_report(_ablation_results(), output_dir=tmpdir,
                                     verbose=False, labels=_LABELS)
        assert isinstance(result["model_comparison"], list)

    def test_paper_tables_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_report(_ablation_results(), output_dir=tmpdir,
                                     verbose=False, labels=_LABELS)
        assert "model_comparison" in result["paper_tables"]
        assert "per_class_hybrid" in result["paper_tables"]


# ---------------------------------------------------------------------------
# generate_report — file output
# ---------------------------------------------------------------------------

class TestGenerateReportFiles:

    def test_json_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(_ablation_results(), output_dir=tmpdir,
                            verbose=False, labels=_LABELS)
            assert os.path.exists(os.path.join(tmpdir, "results", "final_report.json"))

    def test_csv_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(_ablation_results(), output_dir=tmpdir,
                            verbose=False, labels=_LABELS)
            assert os.path.exists(os.path.join(tmpdir, "results", "final_report.csv"))

    def test_json_is_valid_and_has_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(_ablation_results(), output_dir=tmpdir,
                            verbose=False, labels=_LABELS)
            json_path = os.path.join(tmpdir, "results", "final_report.json")
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        assert "meta" in data
        assert "model_comparison" in data
        assert "classification_reports" in data

    def test_csv_has_header_and_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(_ablation_results(), output_dir=tmpdir,
                            verbose=False, labels=_LABELS)
            csv_path = os.path.join(tmpdir, "results", "final_report.csv")
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
        assert len(reader) == 3  # one row per model
        assert "macro_f1" in reader[0]
        assert "accuracy" in reader[0]

    def test_custom_json_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(_ablation_results(), output_dir=tmpdir,
                            json_filename="custom_report.json",
                            verbose=False, labels=_LABELS)
            assert os.path.exists(
                os.path.join(tmpdir, "results", "custom_report.json")
            )

    def test_custom_csv_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(_ablation_results(), output_dir=tmpdir,
                            csv_filename="custom_report.csv",
                            verbose=False, labels=_LABELS)
            assert os.path.exists(
                os.path.join(tmpdir, "results", "custom_report.csv")
            )

    def test_results_dir_created_automatically(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "nested", "output")
            generate_report(_ablation_results(), output_dir=nested,
                            verbose=False, labels=_LABELS)
            assert os.path.exists(os.path.join(nested, "results", "final_report.json"))


# ---------------------------------------------------------------------------
# generate_report — pre-loaded sample list integration
# ---------------------------------------------------------------------------

class TestGenerateReportFromSamples:

    def _make_samples(self, n=8):
        base = [
            {"text": "I feel happy", "label": "joy"},
            {"text": "I am very sad", "label": "sadness"},
            {"text": "Great day!", "label": "joy"},
            {"text": "Feeling down", "label": "sadness"},
        ]
        return (base * ((n // len(base)) + 1))[:n]

    def test_accepts_pre_loaded_samples(self):
        samples = self._make_samples()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_report(samples, output_dir=tmpdir, verbose=False)
        assert "classification_reports" in result

    def test_saves_json_from_samples(self):
        samples = self._make_samples()
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(samples, output_dir=tmpdir, verbose=False)
            assert os.path.exists(
                os.path.join(tmpdir, "results", "final_report.json")
            )

    def test_saves_csv_from_samples(self):
        samples = self._make_samples()
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_report(samples, output_dir=tmpdir, verbose=False)
            assert os.path.exists(
                os.path.join(tmpdir, "results", "final_report.csv")
            )
