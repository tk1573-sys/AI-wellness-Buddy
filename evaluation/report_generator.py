"""
Research-paper-ready report generation for emotion classifier evaluations.

Consumes the metric dicts produced by
:func:`~evaluation.emotion_model_evaluation.run_ablation_study` (or any
``{model: metrics}`` mapping that follows the same schema) and generates:

* Per-class classification reports (with support counts)
* Multi-model comparison summaries
* IEEE-style Markdown tables suitable for direct copy-paste
* Confusion-matrix visualisations (when matplotlib is available)
* ``results/final_report.json`` and ``results/final_report.csv``

Public API
----------
- ``generate_classification_report(model_results, labels)``
- ``generate_model_comparison_summary(ablation_results)``
- ``generate_paper_tables(ablation_results, labels)``
- ``generate_report(dataset_or_results, ...)``
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Ensure the project root is importable
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

__all__ = [
    "generate_classification_report",
    "generate_model_comparison_summary",
    "generate_paper_tables",
    "generate_report",
]

# Metric columns included in per-class tables
_PER_CLASS_COLS = ("precision", "recall", "f1", "support")
# Metric columns included in the model-comparison summary
_SUMMARY_COLS = ("accuracy", "precision_macro", "recall_macro", "macro_f1", "samples")


# ---------------------------------------------------------------------------
# Support-count helper
# ---------------------------------------------------------------------------

def _extract_support(model_metrics: dict, labels: list[str]) -> dict[str, int]:
    """Derive per-class support counts from the confusion matrix.

    Support for class *l* equals the total number of true instances:
    ``sum(confusion_matrix[l].values())``.

    Parameters
    ----------
    model_metrics : dict
        A single-model metrics dict as stored by
        :func:`~evaluation.emotion_model_evaluation.run_ablation_study`.
    labels : list[str]
        Ordered label list.

    Returns
    -------
    dict[str, int]
        ``{label: count}`` mapping.  Missing/zero entries default to ``0``.
    """
    confusion = model_metrics.get("confusion_matrix", {})
    support: dict[str, int] = {}
    for label in labels:
        row = confusion.get(label, {})
        support[label] = int(sum(row.values())) if row else 0
    return support


# ---------------------------------------------------------------------------
# Per-class classification report
# ---------------------------------------------------------------------------

def generate_classification_report(
    model_results: dict,
    labels: list[str] | None = None,
) -> dict:
    """Build a per-class classification report for a single model.

    Parameters
    ----------
    model_results : dict
        Metrics dict for one model (as returned by
        :func:`~evaluation.emotion_model_evaluation.run_ablation_study`).
        Must contain ``per_class``, ``macro_f1``, ``precision_macro``,
        ``recall_macro``, and optionally ``confusion_matrix``.
    labels : list[str] or None
        Label ordering.  Defaults to the keys of ``per_class``.

    Returns
    -------
    dict
        ``{
            "per_class": {label: {precision, recall, f1, support}},
            "macro":     {precision, recall, f1},
            "accuracy":  float,
            "samples":   int,
        }``
    """
    per_class_raw = model_results.get("per_class", {})
    labels = labels or list(per_class_raw.keys())
    support = _extract_support(model_results, labels)

    per_class_out: dict[str, dict] = {}
    for label in labels:
        metrics = per_class_raw.get(label, {})
        per_class_out[label] = {
            "precision": round(float(metrics.get("precision", 0.0)), 4),
            "recall":    round(float(metrics.get("recall",    0.0)), 4),
            "f1":        round(float(metrics.get("f1",        0.0)), 4),
            "support":   support.get(label, 0),
        }

    macro = {
        "precision": round(float(model_results.get("precision_macro", 0.0)), 4),
        "recall":    round(float(model_results.get("recall_macro",    0.0)), 4),
        "f1":        round(float(model_results.get("macro_f1",        0.0)), 4),
    }

    return {
        "per_class": per_class_out,
        "macro":     macro,
        "accuracy":  round(float(model_results.get("accuracy", 0.0)), 4),
        "samples":   int(model_results.get("samples", 0)),
    }


# ---------------------------------------------------------------------------
# Multi-model comparison summary
# ---------------------------------------------------------------------------

def generate_model_comparison_summary(ablation_results: dict) -> list[dict]:
    """Build a flat comparison summary across all models.

    Parameters
    ----------
    ablation_results : dict
        ``{model_name: metrics_dict, ...}`` mapping — the same structure
        returned by
        :func:`~evaluation.emotion_model_evaluation.run_ablation_study`.
        The ``"meta"`` and ``"statistical_tests"`` keys (if present) are
        ignored.

    Returns
    -------
    list[dict]
        One row per model, each row containing ``model``, ``accuracy``,
        ``precision_macro``, ``recall_macro``, ``macro_f1``, and
        ``samples``.  Rows are ordered by descending ``macro_f1``.
    """
    rows: list[dict] = []
    skip = {"meta", "statistical_tests"}
    for model_name, metrics in ablation_results.items():
        if model_name in skip or not isinstance(metrics, dict):
            continue
        rows.append({
            "model":           model_name,
            "accuracy":        round(float(metrics.get("accuracy",        0.0)), 4),
            "precision_macro": round(float(metrics.get("precision_macro", 0.0)), 4),
            "recall_macro":    round(float(metrics.get("recall_macro",    0.0)), 4),
            "macro_f1":        round(float(metrics.get("macro_f1",        0.0)), 4),
            "samples":         int(metrics.get("samples", 0)),
        })
    # Stable sort: best macro F1 first
    rows.sort(key=lambda r: r["macro_f1"], reverse=True)
    return rows


# ---------------------------------------------------------------------------
# IEEE / Markdown table formatter
# ---------------------------------------------------------------------------

def _md_row(cells: list[str], widths: list[int]) -> str:
    """Format one Markdown table row with given column widths."""
    padded = [str(c).ljust(w) for c, w in zip(cells, widths)]
    return "| " + " | ".join(padded) + " |"


def _md_separator(widths: list[int]) -> str:
    """Format the Markdown header separator row."""
    return "| " + " | ".join("-" * w for w in widths) + " |"


def generate_paper_tables(
    ablation_results: dict,
    labels: list[str] | None = None,
) -> dict[str, str]:
    """Generate IEEE-style Markdown tables from ablation results.

    Produces two tables:

    1. **Model Comparison** — one row per model with accuracy, precision,
       recall, macro F1, and sample count.
    2. **Per-class (hybrid)** — per-class precision, recall, F1, and support
       for the hybrid model specifically (the primary model of interest).

    Parameters
    ----------
    ablation_results : dict
        ``{model_name: metrics_dict, ...}`` mapping.
    labels : list[str] or None
        Label ordering for the per-class table.

    Returns
    -------
    dict[str, str]
        ``{
            "model_comparison": "<markdown string>",
            "per_class_hybrid": "<markdown string>",
        }``
    """
    # ── Table 1: model comparison ──────────────────────────────────────────
    summary = generate_model_comparison_summary(ablation_results)
    t1_headers = ["Model", "Precision", "Recall", "F1", "Accuracy", "Samples"]
    t1_rows = [
        [
            row["model"],
            f"{row['precision_macro']:.4f}",
            f"{row['recall_macro']:.4f}",
            f"{row['macro_f1']:.4f}",
            f"{row['accuracy']:.4f}",
            str(row["samples"]),
        ]
        for row in summary
    ]
    t1_widths = [
        max(len(h), max((len(r[i]) for r in t1_rows), default=0))
        for i, h in enumerate(t1_headers)
    ]
    t1_lines = [
        _md_row(t1_headers, t1_widths),
        _md_separator(t1_widths),
        *[_md_row(r, t1_widths) for r in t1_rows],
    ]
    model_comparison_table = "\n".join(t1_lines)

    # ── Table 2: per-class for hybrid (or whichever model is available) ────
    skip = {"meta", "statistical_tests"}
    # Prefer "hybrid"; fall back to the first available model
    hybrid_metrics = None
    for candidate in ("hybrid", *[k for k in ablation_results if k not in skip]):
        if candidate not in skip and candidate in ablation_results:
            hybrid_metrics = ablation_results[candidate]
            hybrid_name = candidate
            break

    if hybrid_metrics is not None:
        clf_report = generate_classification_report(hybrid_metrics, labels)
        per_class = clf_report["per_class"]
        t2_headers = ["Class", "Precision", "Recall", "F1", "Support"]
        t2_rows = [
            [
                lbl,
                f"{m['precision']:.4f}",
                f"{m['recall']:.4f}",
                f"{m['f1']:.4f}",
                str(m["support"]),
            ]
            for lbl, m in per_class.items()
        ]
        # Macro row
        macro = clf_report["macro"]
        t2_rows.append([
            "**macro avg**",
            f"{macro['precision']:.4f}",
            f"{macro['recall']:.4f}",
            f"{macro['f1']:.4f}",
            str(clf_report["samples"]),
        ])
        t2_widths = [
            max(len(h), max((len(r[i]) for r in t2_rows), default=0))
            for i, h in enumerate(t2_headers)
        ]
        t2_lines = [
            f"**Per-class Classification Report — {hybrid_name}**",
            "",
            _md_row(t2_headers, t2_widths),
            _md_separator(t2_widths),
            *[_md_row(r, t2_widths) for r in t2_rows],
        ]
        per_class_table = "\n".join(t2_lines)
    else:
        per_class_table = ""

    return {
        "model_comparison": model_comparison_table,
        "per_class_hybrid": per_class_table,
    }


# ---------------------------------------------------------------------------
# Confusion-matrix visualisation (optional, matplotlib-gated)
# ---------------------------------------------------------------------------

def _plot_confusion_matrix(
    confusion: dict,
    labels: list[str],
    title: str,
    output_path: str,
) -> bool:
    """Save a confusion-matrix heatmap to *output_path*.

    Returns ``True`` on success, ``False`` when matplotlib is unavailable.
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return False

    matrix = np.array(
        [[confusion.get(t, {}).get(p, 0) for p in labels] for t in labels],
        dtype=float,
    )

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix, cmap="Blues")
    fig.colorbar(im, ax=ax)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(title)

    for i in range(len(labels)):
        for j in range(len(labels)):
            val = int(matrix[i, j])
            color = "white" if matrix[i, j] > matrix.max() / 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=7, color=color)

    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


# ---------------------------------------------------------------------------
# Top-level runner
# ---------------------------------------------------------------------------

def generate_report(
    dataset_or_results,
    *,
    max_samples: int | None = None,
    labels: list[str] | None = None,
    output_dir: str = ".",
    json_filename: str = "final_report.json",
    csv_filename: str = "final_report.csv",
    plot_confusion: bool = True,
    verbose: bool = True,
) -> dict:
    """Generate a research-paper-ready evaluation report.

    Accepts either:

    * A pre-computed ablation-study results dict (as returned by
      :func:`~evaluation.emotion_model_evaluation.run_ablation_study`), or
    * A raw dataset (file path ``str`` or pre-loaded ``list[dict]``), in
      which case a fresh ablation study is run first.

    Parameters
    ----------
    dataset_or_results : dict or str or list
        * **dict** — pre-computed ablation results (must contain model keys
          such as ``"keyword"``, ``"transformer"``, ``"hybrid"``).
        * **str** — path to a GoEmotions-formatted JSONL/CSV/JSON file.
        * **list** — pre-loaded list of ``{"text": ..., "label": ...}`` dicts.
    max_samples : int or None
        When *dataset_or_results* is a file path, cap the number of loaded
        samples.  Ignored otherwise.
    labels : list[str] or None
        Label set.  Defaults to ``SYSTEM_LABELS`` from the GoEmotions loader.
    output_dir : str
        Base output directory.  Artefacts are written to:

        * ``{output_dir}/results/{json_filename}``
        * ``{output_dir}/results/{csv_filename}``
        * ``{output_dir}/plots/confusion_<model>.png`` (when *plot_confusion*
          is ``True`` and matplotlib is available)
    json_filename : str
        Output JSON filename (default ``"final_report.json"``).
    csv_filename : str
        Output CSV filename (default ``"final_report.csv"``).
    plot_confusion : bool
        When ``True``, attempt to save a confusion-matrix heatmap for each
        model.
    verbose : bool
        When ``True``, print the paper tables and file paths to stdout.

    Returns
    -------
    dict
        ``{
            "meta":               {timestamp, dataset, samples, labels},
            "classification_reports": {model: classification_report_dict},
            "model_comparison":   [summary_row, ...],
            "paper_tables":       {table_name: markdown_string},
        }``

    Raises
    ------
    ValueError
        When *dataset_or_results* is a dataset and no samples could be loaded.
    """
    from datasets.goemotions_loader import SYSTEM_LABELS  # local import
    labels = labels or list(SYSTEM_LABELS)

    # ── 1. Resolve ablation results ───────────────────────────────────────
    if isinstance(dataset_or_results, dict):
        ablation_results = dataset_or_results
        dataset_name = ablation_results.get("meta", {}).get("dataset", "pre-computed")
        total_samples = ablation_results.get("meta", {}).get("samples", 0)
    else:
        from evaluation.emotion_model_evaluation import run_ablation_study  # local import
        ablation_results = run_ablation_study(
            dataset_or_results,
            max_samples=max_samples,
            labels=labels,
            output_dir=output_dir,
            run_stats=False,
            verbose=False,
        )
        dataset_name = ablation_results.get("meta", {}).get("dataset", "unknown")
        total_samples = ablation_results.get("meta", {}).get("samples", 0)

    # ── 2. Per-model classification reports ───────────────────────────────
    skip = {"meta", "statistical_tests"}
    classification_reports: dict[str, dict] = {}
    for model_name, metrics in ablation_results.items():
        if model_name in skip or not isinstance(metrics, dict):
            continue
        classification_reports[model_name] = generate_classification_report(
            metrics, labels
        )

    # ── 3. Model comparison summary ───────────────────────────────────────
    comparison = generate_model_comparison_summary(ablation_results)

    # ── 4. Paper tables ───────────────────────────────────────────────────
    tables = generate_paper_tables(ablation_results, labels)

    if verbose:
        print("\n=== Model Comparison Table ===")
        print(tables["model_comparison"])
        if tables.get("per_class_hybrid"):
            print("\n" + tables["per_class_hybrid"])

    # ── 5. Confusion-matrix plots ─────────────────────────────────────────
    plots_saved: list[str] = []
    if plot_confusion:
        plots_dir = os.path.join(output_dir, "plots")
        for model_name, metrics in ablation_results.items():
            if model_name in skip or not isinstance(metrics, dict):
                continue
            confusion = metrics.get("confusion_matrix", {})
            if not confusion:
                continue
            plot_path = os.path.join(plots_dir, f"confusion_{model_name}.png")
            saved = _plot_confusion_matrix(
                confusion, labels,
                title=f"Confusion Matrix — {model_name}",
                output_path=plot_path,
            )
            if saved:
                plots_saved.append(plot_path)
                logger.info("Confusion matrix saved to %s", plot_path)

    # ── 6. Build output payload ───────────────────────────────────────────
    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset":   dataset_name,
        "samples":   total_samples,
        "labels":    labels,
    }
    output = {
        "meta":                   meta,
        "classification_reports": classification_reports,
        "model_comparison":       comparison,
        "paper_tables":           tables,
    }

    # ── 7. Save JSON ──────────────────────────────────────────────────────
    results_dir = os.path.join(output_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    json_path = os.path.join(results_dir, json_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info("Final report saved to %s", json_path)
    if verbose:
        print(f"\nJSON report saved → {json_path}")

    # ── 8. Save CSV ───────────────────────────────────────────────────────
    csv_path = os.path.join(results_dir, csv_filename)
    _save_comparison_csv(comparison, csv_path)
    logger.info("CSV comparison saved to %s", csv_path)
    if verbose:
        print(f"CSV report saved  → {csv_path}")
        for p in plots_saved:
            print(f"Confusion plot    → {p}")

    return output


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def _save_comparison_csv(comparison: list[dict], path: str) -> None:
    """Write the model comparison list to a CSV file."""
    fieldnames = list(_SUMMARY_COLS)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in comparison:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
