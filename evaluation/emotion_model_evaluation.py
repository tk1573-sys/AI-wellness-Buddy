"""
Emotion model evaluation pipeline.

Wraps the core metric computations from :mod:`research_evaluation` and the
GoEmotions dataset loader from :mod:`datasets.goemotions_loader` into a
single evaluation entry-point.

Public API
----------
- ``evaluate_emotion_model(dataset_path, classifier_fn, ...)``
- ``compute_metrics(y_true, y_pred, labels)``
- ``get_classifier(mode)``
- ``run_ablation_study(dataset, ...)``
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Ensure the project root is importable
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from research_evaluation import (        # noqa: E402
    evaluate_classifier,
    format_summary_table,
)
from datasets.goemotions_loader import (  # noqa: E402
    load_goemotions,
    load_goemotions_hf,
    SYSTEM_LABELS,
)

# The three modes compared in the ablation study
ABLATION_MODELS: tuple[str, ...] = ("keyword", "transformer", "hybrid")

# Re-export for convenience
__all__ = [
    "evaluate_emotion_model",
    "compute_metrics",
    "format_summary_table",
    "load_goemotions_hf",
    "get_classifier",
    "run_ablation_study",
    "ABLATION_MODELS",
    "SYSTEM_LABELS",
]


def compute_metrics(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str] | None = None,
) -> dict:
    """Compute precision, recall, macro F1, accuracy, and confusion matrix.

    Parameters
    ----------
    y_true : list[str]
        Ground-truth labels.
    y_pred : list[str]
        Predicted labels (same length as *y_true*).
    labels : list[str] or None
        Label set.  Defaults to :data:`SYSTEM_LABELS`.

    Returns
    -------
    dict
        ``accuracy``, ``precision_macro``, ``recall_macro``, ``macro_f1``,
        ``confusion_matrix``, etc.
    """
    labels = labels or list(SYSTEM_LABELS)

    # Build (text, true_label) tuples with a classifier that returns the
    # matching prediction.  This lets us reuse evaluate_classifier's
    # already-tested metric code.
    pred_iter = iter(y_pred)

    def _classifier(_text: str) -> str:
        return next(pred_iter)

    samples = [(f"sample_{i}", true) for i, true in enumerate(y_true)]
    report = evaluate_classifier(samples, _classifier, labels=labels)

    # Rename keys to match the schema expected by the problem statement
    return {
        "accuracy": report["accuracy"],
        "precision_macro": report["macro_precision"],
        "recall_macro": report["macro_recall"],
        "macro_f1": report["macro_f1"],
        "confusion_matrix": report.get("confusion_matrix", {}),
        "per_class": report.get("per_class", {}),
        "samples": report["samples"],
    }


def evaluate_emotion_model(
    dataset_path: str,
    classifier_fn=None,
    *,
    max_samples: int | None = None,
    labels: list[str] | None = None,
) -> dict:
    """End-to-end evaluation: load GoEmotions → classify → compute metrics.

    Parameters
    ----------
    dataset_path : str
        Path to a GoEmotions ``.jsonl``, ``.csv``, or ``.json`` file.
    classifier_fn : callable or None
        A function ``text → predicted_label``.  When *None* the default
        :class:`EmotionAnalyzer` keyword classifier is used.
    max_samples : int or None
        Limit dataset size for quick runs.
    labels : list[str] or None
        Label set.  Defaults to :data:`SYSTEM_LABELS`.

    Returns
    -------
    dict
        Full evaluation report with accuracy, precision_macro, recall_macro,
        macro_f1, confusion_matrix, etc.
    """
    labels = labels or list(SYSTEM_LABELS)

    if classifier_fn is None:
        from emotion_analyzer import EmotionAnalyzer
        _analyzer = EmotionAnalyzer()

        def _default_classifier(text: str) -> str:
            return _analyzer.classify_emotion_ml(text)["primary_emotion"]

        classifier_fn = _default_classifier

    samples = load_goemotions(dataset_path, max_samples=max_samples)
    if not samples:
        return {"error": "No samples loaded", "samples": 0}

    # Convert to the (text, label) format expected by evaluate_classifier
    eval_samples = [(s["text"], s["label"]) for s in samples]
    report = evaluate_classifier(eval_samples, classifier_fn, labels=labels)

    # Add convenience aliases
    report["precision_macro"] = report.get("macro_precision", 0.0)
    report["recall_macro"] = report.get("macro_recall", 0.0)
    report["dataset"] = os.path.basename(dataset_path)

    return report


# ---------------------------------------------------------------------------
# Classifier factory
# ---------------------------------------------------------------------------

def get_classifier(mode: str):
    """Return a ``text → label`` classifier function for the given *mode*.

    Parameters
    ----------
    mode : str
        One of ``"keyword"``, ``"transformer"``, or ``"hybrid"``.

        * **keyword** — rule-based keyword-count classifier (no ML model).
        * **transformer** — transformer-only classifier via
          :class:`models.emotion_transformer.EmotionTransformer` (falls
          back to keyword counting when the model is unavailable).
        * **hybrid** — production classifier: 75 % transformer + 25 %
          keyword heuristic via :class:`EmotionAnalyzer`.

    Returns
    -------
    callable
        A function ``(text: str) -> str`` that returns a system emotion label.

    Raises
    ------
    ValueError
        If *mode* is not one of the three recognised values.
    """
    mode = mode.strip().lower()
    if mode == "keyword":
        from models.emotion_transformer import EmotionTransformer
        _et = EmotionTransformer()

        def _keyword_classify(text: str) -> str:
            probs = _et.classify_keywords_only(text)
            if not probs:
                return "neutral"
            return max(probs, key=probs.get)

        return _keyword_classify

    if mode == "transformer":
        from models.emotion_transformer import EmotionTransformer
        _et = EmotionTransformer()

        def _transformer_classify(text: str) -> str:
            probs = _et.classify(text)
            if not probs:
                return "neutral"
            return max(probs, key=probs.get)

        return _transformer_classify

    if mode == "hybrid":
        from emotion_analyzer import EmotionAnalyzer
        _analyzer = EmotionAnalyzer()

        def _hybrid_classify(text: str) -> str:
            result = _analyzer.classify_emotion(text)
            return result.get("primary_emotion", "neutral")

        return _hybrid_classify

    raise ValueError(
        f"Unknown classifier mode {mode!r}. "
        f"Expected one of: {', '.join(ABLATION_MODELS)}"
    )


# ---------------------------------------------------------------------------
# Ablation study
# ---------------------------------------------------------------------------

def _format_comparison_table(ablation_results: dict) -> str:
    """Format an ablation comparison table for console output.

    Parameters
    ----------
    ablation_results : dict
        ``{model_name: metrics_dict, ...}`` as returned by
        :func:`run_ablation_study`.

    Returns
    -------
    str
        Printable comparison table.
    """
    col_w = 12
    header = (
        f"{'Model':<15} "
        f"{'Accuracy':>{col_w}} "
        f"{'Precision':>{col_w}} "
        f"{'Recall':>{col_w}} "
        f"{'Macro F1':>{col_w}}"
    )
    sep = "-" * len(header)
    lines = [sep, header, sep]
    for model_name, metrics in ablation_results.items():
        lines.append(
            f"{model_name:<15} "
            f"{metrics.get('accuracy', 0.0):>{col_w}.4f} "
            f"{metrics.get('precision_macro', 0.0):>{col_w}.4f} "
            f"{metrics.get('recall_macro', 0.0):>{col_w}.4f} "
            f"{metrics.get('macro_f1', 0.0):>{col_w}.4f}"
        )
    lines.append(sep)
    return "\n".join(lines)


def _save_comparison_csv(ablation_results: dict, path: str) -> None:
    """Write the ablation comparison to a CSV file.

    Parameters
    ----------
    ablation_results : dict
        ``{model_name: metrics_dict, ...}``
    path : str
        Destination file path (created/overwritten).
    """
    fieldnames = ["model", "accuracy", "precision_macro", "recall_macro", "macro_f1", "samples"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for model_name, metrics in ablation_results.items():
            writer.writerow({
                "model": model_name,
                "accuracy": metrics.get("accuracy", 0.0),
                "precision_macro": metrics.get("precision_macro", 0.0),
                "recall_macro": metrics.get("recall_macro", 0.0),
                "macro_f1": metrics.get("macro_f1", 0.0),
                "samples": metrics.get("samples", 0),
            })


def _plot_ablation_comparison(ablation_results: dict, output_path: str) -> bool:
    """Plot a grouped-bar comparison chart and save to *output_path*.

    Parameters
    ----------
    ablation_results : dict
        ``{model_name: metrics_dict, ...}``
    output_path : str
        Destination PNG path.

    Returns
    -------
    bool
        ``True`` when the plot was saved successfully; ``False`` when
        matplotlib is unavailable (caller should log a warning).
    """
    try:
        import matplotlib  # noqa: F401
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        return False

    metric_keys = ["accuracy", "precision_macro", "recall_macro", "macro_f1"]
    metric_labels = ["Accuracy", "Precision", "Recall", "Macro F1"]

    model_names = list(ablation_results.keys())
    n_models = len(model_names)
    n_metrics = len(metric_keys)

    import numpy as np  # noqa: PLC0415 — guarded by matplotlib import above
    x = np.arange(n_metrics)
    bar_width = 0.25
    offsets = [(i - (n_models - 1) / 2) * bar_width for i in range(n_models)]

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, model_name in enumerate(model_names):
        metrics = ablation_results[model_name]
        values = [metrics.get(k, 0.0) for k in metric_keys]
        bars = ax.bar(x + offsets[i], values, bar_width, label=model_name)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.3f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7,
            )

    ax.set_xlabel("Metric")
    ax.set_ylabel("Score")
    ax.set_title("Ablation Study — Emotion Classifier Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    ax.set_ylim(0, 1.12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


def run_ablation_study(
    dataset,
    *,
    max_samples: int | None = None,
    labels: list[str] | None = None,
    output_dir: str = ".",
    results_filename: str = "ablation_results.json",
    csv_filename: str = "ablation_comparison.csv",
    plot_filename: str = "ablation_comparison.png",
    run_stats: bool = True,
    verbose: bool = True,
) -> dict:
    """Run an ablation study comparing keyword, transformer, and hybrid models.

    All three classifiers are evaluated on **the same** dataset to ensure
    fair, deterministic comparison.

    Parameters
    ----------
    dataset : str or list[dict]
        Either a file path (``str``) to a GoEmotions-formatted JSONL/CSV file,
        or a pre-loaded list of ``{"text": ..., "label": ...}`` dicts.
    max_samples : int or None
        When *dataset* is a file path, limit the number of loaded samples.
        When *dataset* is a pre-loaded list this is ignored.
    labels : list[str] or None
        Label set.  Defaults to :data:`SYSTEM_LABELS`.
    output_dir : str
        Base output directory.  Results are saved to:

        * ``{output_dir}/results/{results_filename}``
        * ``{output_dir}/results/{csv_filename}``
        * ``{output_dir}/plots/{plot_filename}``
    results_filename : str
        JSON output filename (default ``"ablation_results.json"``).
    csv_filename : str
        CSV output filename (default ``"ablation_comparison.csv"``).
    plot_filename : str
        PNG chart filename (default ``"ablation_comparison.png"``).
    run_stats : bool
        When ``True`` (default), run paired t-tests comparing the hybrid
        model against transformer and keyword baselines.  Results are saved
        to ``{output_dir}/results/statistical_significance.json`` and merged
        into the returned payload under the key ``"statistical_tests"``.
    verbose : bool
        When ``True``, print the comparison table to stdout.

    Returns
    -------
    dict
        ``{model_name: metrics_dict, ...}`` for all three ablation models,
        plus ``"meta"`` containing run metadata (timestamp, sample count,
        dataset name, label set), and optionally ``"statistical_tests"``
        when *run_stats* is ``True``.

    Raises
    ------
    ValueError
        When no samples could be loaded from *dataset*.
    """
    labels = labels or list(SYSTEM_LABELS)

    # ── 1. Load dataset once ───────────────────────────────────────────────
    if isinstance(dataset, str):
        logger.info("Loading dataset from %s (max_samples=%s)", dataset, max_samples)
        samples = load_goemotions(dataset, max_samples=max_samples)
        dataset_name = os.path.basename(dataset)
    else:
        samples = list(dataset)
        dataset_name = "pre-loaded"

    if not samples:
        raise ValueError("No samples could be loaded from the provided dataset.")

    eval_samples = [(s["text"], s["label"]) for s in samples]
    logger.info("Loaded %d evaluation samples.", len(eval_samples))

    # ── 2. Run all three classifiers on the same data ─────────────────────
    ablation_results: dict = {}
    for mode in ABLATION_MODELS:
        logger.info("Running '%s' classifier …", mode)
        clf = get_classifier(mode)
        report = evaluate_classifier(eval_samples, clf, labels=labels)
        ablation_results[mode] = {
            "accuracy": report.get("accuracy", 0.0),
            "precision_macro": report.get("macro_precision", 0.0),
            "recall_macro": report.get("macro_recall", 0.0),
            "macro_f1": report.get("macro_f1", 0.0),
            "confusion_matrix": report.get("confusion_matrix", {}),
            "per_class": report.get("per_class", {}),
            "samples": report.get("samples", len(eval_samples)),
        }

    # ── 3. Comparison table ────────────────────────────────────────────────
    table = _format_comparison_table(ablation_results)
    if verbose:
        print("\nAblation Study Results")
        print(table)

    # ── 4. Save JSON results ───────────────────────────────────────────────
    from datetime import datetime, timezone  # local import for slim default path
    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset_name,
        "samples": len(eval_samples),
        "labels": labels,
        "models": list(ABLATION_MODELS),
    }
    output_payload = {"meta": meta, **ablation_results}

    results_dir = os.path.join(output_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    json_path = os.path.join(results_dir, results_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, default=str)
    logger.info("Ablation results saved to %s", json_path)
    if verbose:
        print(f"\nResults saved → {json_path}")

    # ── 5. Save CSV ────────────────────────────────────────────────────────
    csv_path = os.path.join(results_dir, csv_filename)
    _save_comparison_csv(ablation_results, csv_path)
    logger.info("CSV comparison saved to %s", csv_path)
    if verbose:
        print(f"CSV saved     → {csv_path}")

    # ── 6. Plot ────────────────────────────────────────────────────────────
    plots_dir = os.path.join(output_dir, "plots")
    plot_path = os.path.join(plots_dir, plot_filename)
    saved = _plot_ablation_comparison(ablation_results, plot_path)
    if saved:
        logger.info("Ablation chart saved to %s", plot_path)
        if verbose:
            print(f"Chart saved   → {plot_path}")
    else:
        logger.warning(
            "matplotlib/numpy not installed — skipping chart generation."
        )

    # ── 7. Statistical significance tests ─────────────────────────────────
    if run_stats:
        from evaluation.statistical_tests import run_significance_tests  # local import
        stat_results = run_significance_tests(
            samples,  # pre-loaded list — avoids re-reading from disk
            labels=labels,
            output_dir=output_dir,
            verbose=verbose,
        )
        output_payload["statistical_tests"] = stat_results

    return output_payload
