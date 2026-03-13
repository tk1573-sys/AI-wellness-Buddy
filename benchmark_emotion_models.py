"""
Benchmarking pipeline for emotion detection models.

Compares three classification strategies on standard public datasets:

1. **Keyword heuristic** – rule-based keyword counting (no ML).
2. **Transformer model** – ``j-hartmann/emotion-english-distilroberta-base``
   via :class:`EmotionTransformer` (falls back to keyword counting when the
   model is unavailable).
3. **Hybrid model** – 70 % transformer + 30 % keyword heuristic, the default
   production pipeline in :class:`EmotionAnalyzer`.

Supported datasets
------------------
* `GoEmotions <https://github.com/google-research/google-research/tree/master/goemotions>`_
* `EmotionLines <http://doraemon.iis.sinica.edu.tw/emotionlines/>`_
* `DailyDialog <http://yanran.li/dailydialog.html>`_

Output
------
* ``evaluation_results.json`` – per-model evaluation report.
* Formatted comparison table printed to stdout.
* ``confusion_matrix_<model>.png`` – confusion-matrix heatmap per model
  (requires *plotly* or falls back to text rendering).

Usage
-----
::

    # Benchmark on a single dataset file
    python benchmark_emotion_models.py --dataset path/to/goemotions.jsonl

    # Benchmark on multiple datasets
    python benchmark_emotion_models.py \\
        --dataset data/goemotions.jsonl data/emotionlines.json data/dailydialog.jsonl

    # Specify output directory
    python benchmark_emotion_models.py --dataset data/goemotions.jsonl --output results/

    # Dry-run (synthetic data, no real dataset file needed)
    python benchmark_emotion_models.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone

from research_evaluation import (
    evaluate_classifier,
    format_summary_table,
    load_emotion_dataset,
    normalize_emotion_label,
)


# ---------------------------------------------------------------------------
# Canonical label set used throughout the Wellness Buddy system
# ---------------------------------------------------------------------------
LABELS: list[str] = [
    "joy", "sadness", "anger", "fear", "anxiety", "neutral", "crisis",
]


# ---------------------------------------------------------------------------
# Classifier factories
# ---------------------------------------------------------------------------

def _make_keyword_classifier():
    """Return a keyword-only classifier function (text → label)."""
    from models.emotion_transformer import EmotionTransformer

    _et = EmotionTransformer()
    # Force keyword-only mode regardless of transformer availability
    def _classify(text: str) -> str:
        probs = _et._classify_keywords(text)
        if not probs:
            return "neutral"
        return max(probs, key=probs.get)

    return _classify


def _make_transformer_classifier():
    """Return a transformer-only classifier function (text → label).

    When the transformer model is unavailable the keyword fallback inside
    :class:`EmotionTransformer` is used automatically, so the benchmark
    still runs (and the ``model_available`` flag in the output will be
    ``False``).
    """
    from models.emotion_transformer import EmotionTransformer

    _et = EmotionTransformer()
    def _classify(text: str) -> str:
        probs = _et.classify(text)
        if not probs:
            return "neutral"
        return max(probs, key=probs.get)

    return _classify, _et


def _make_hybrid_classifier():
    """Return the full hybrid classifier used in production.

    Uses :class:`EmotionAnalyzer` which internally blends 70 % transformer
    + 30 % keyword heuristic (or 50/50 when the transformer is unavailable).
    """
    from emotion_analyzer import EmotionAnalyzer

    _analyzer = EmotionAnalyzer()
    def _classify(text: str) -> str:
        result = _analyzer.classify_emotion(text)
        return result.get("primary_emotion", "neutral")

    return _classify, _analyzer


# ---------------------------------------------------------------------------
# Confusion matrix visualisation
# ---------------------------------------------------------------------------

def render_confusion_matrix_text(confusion: dict, labels: list[str]) -> str:
    """Render a confusion matrix as a plain-text grid.

    Parameters
    ----------
    confusion : dict
        ``{true_label: {pred_label: count, ...}, ...}``
    labels : list[str]
        Row/column ordering.

    Returns
    -------
    str
        Printable text table.
    """
    col_w = max(len(l) for l in labels)
    col_w = max(col_w, 5)
    header = " " * (col_w + 2) + "  ".join(f"{l:>{col_w}}" for l in labels)
    lines = [header]
    lines.append("-" * len(header))
    for true_label in labels:
        row_vals = confusion.get(true_label, {})
        cells = "  ".join(
            f"{row_vals.get(pred, 0):>{col_w}}" for pred in labels
        )
        lines.append(f"{true_label:<{col_w}}  {cells}")
    return "\n".join(lines)


def save_confusion_matrix_image(confusion: dict, labels: list[str],
                                model_name: str, output_dir: str) -> str | None:
    """Save a confusion-matrix heatmap as a PNG using plotly.

    Returns the output path, or *None* when plotly is unavailable.
    """
    try:
        import plotly.graph_objects as go  # noqa: F401
    except ImportError:
        return None

    # Build matrix as list-of-lists
    z = []
    for true_label in labels:
        row_data = confusion.get(true_label, {})
        z.append([row_data.get(pred, 0) for pred in labels])

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        colorscale="Blues",
        text=[[str(cell) for cell in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="True: %{y}<br>Pred: %{x}<br>Count: %{z}<extra></extra>",
    ))
    safe_name = model_name.replace(" ", "_").lower()
    fig.update_layout(
        title=f"Confusion Matrix — {model_name}",
        xaxis_title="Predicted",
        yaxis_title="True",
        width=600,
        height=500,
    )
    path = os.path.join(output_dir, f"confusion_matrix_{safe_name}.png")
    try:
        fig.write_image(path)
    except Exception:
        # kaleido / orca not installed – write as HTML instead
        html_path = os.path.join(
            output_dir, f"confusion_matrix_{safe_name}.html"
        )
        fig.write_html(html_path)
        return html_path
    return path


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def format_comparison_table(results: dict) -> str:
    """Format a cross-model comparison table.

    Parameters
    ----------
    results : dict
        ``{model_name: evaluation_report, ...}``

    Returns
    -------
    str
        Printable comparison table.
    """
    lines = []
    header = f"{'Model':<25} {'Accuracy':>10} {'Macro F1':>10} {'Micro F1':>10}"
    sep = "-" * len(header)
    lines.append(sep)
    lines.append(header)
    lines.append(sep)
    for model_name, report in results.items():
        lines.append(
            f"{model_name:<25} "
            f"{report.get('accuracy', 0):>10.4f} "
            f"{report.get('macro_f1', 0):>10.4f} "
            f"{report.get('micro_f1', 0):>10.4f}"
        )
    lines.append(sep)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Synthetic (dry-run) dataset
# ---------------------------------------------------------------------------

_SYNTHETIC_SAMPLES = [
    ("I feel so happy and excited about the new job!", "joy"),
    ("What a wonderful and amazing day it has been", "joy"),
    ("I am grateful and blessed to have such friends", "joy"),
    ("Everything is going great, I feel fantastic", "joy"),
    ("I am so sad and lonely, nothing feels right", "sadness"),
    ("Crying all night, feeling heartbroken and empty", "sadness"),
    ("I feel hopeless and depressed about the future", "sadness"),
    ("The grief and loss I feel is overwhelming", "sadness"),
    ("I am furious and angry about what happened", "anger"),
    ("This is so frustrating, I hate this situation", "anger"),
    ("I am livid and outraged by the injustice", "anger"),
    ("So irritated and annoyed with everything", "anger"),
    ("I am scared and terrified of what might happen", "fear"),
    ("The dread and horror keep me up at night", "fear"),
    ("I feel frightened and panicked about the future", "fear"),
    ("I am anxious and stressed about the exam", "anxiety"),
    ("Feeling overwhelmed and worried about everything", "anxiety"),
    ("Can't sleep, racing thoughts about what if scenarios", "anxiety"),
    ("I feel tense and uneasy about the situation", "anxiety"),
    ("Things are okay, just a normal day", "neutral"),
    ("I am fine, nothing special happening", "neutral"),
    ("Everything is average, getting by as usual", "neutral"),
    ("Just managing, not bad not great", "neutral"),
    ("It was an ordinary day at work", "neutral"),
]


def create_synthetic_dataset() -> str:
    """Write a temporary JSONL file with synthetic test samples.

    Returns the path to the temp file (caller should clean up).
    """
    fd, path = tempfile.mkstemp(suffix=".jsonl", prefix="benchmark_synthetic_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for text, label in _SYNTHETIC_SAMPLES:
            json.dump({"text": text, "label": label}, f)
            f.write("\n")
    return path


# ---------------------------------------------------------------------------
# Core benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark(
    dataset_paths: list[str] | None = None,
    output_dir: str = ".",
    dry_run: bool = False,
) -> dict:
    """Run the full benchmarking pipeline.

    Parameters
    ----------
    dataset_paths : list[str] or None
        Paths to evaluation datasets (.jsonl, .json, .csv).
        When *None* and *dry_run* is ``True``, a synthetic dataset is used.
    output_dir : str
        Directory for output files (created if it doesn't exist).
    dry_run : bool
        Use synthetic data for a quick sanity-check run.

    Returns
    -------
    dict
        Full benchmark results suitable for JSON serialisation.
    """
    os.makedirs(output_dir, exist_ok=True)

    # --- Resolve dataset paths ------------------------------------------------
    temp_path: str | None = None
    if dry_run or not dataset_paths:
        temp_path = create_synthetic_dataset()
        dataset_paths = [temp_path]

    # --- Build classifiers ---------------------------------------------------
    keyword_clf = _make_keyword_classifier()
    transformer_clf, _et = _make_transformer_classifier()
    hybrid_clf, _analyzer = _make_hybrid_classifier()

    models = {
        "Keyword Model": keyword_clf,
        "Transformer Model": transformer_clf,
        "Hybrid Model": hybrid_clf,
    }

    transformer_available = _et.available

    # --- Run evaluation per dataset × model ----------------------------------
    all_results: dict = {
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transformer_available": transformer_available,
            "labels": LABELS,
            "datasets": [os.path.basename(p) for p in dataset_paths],
        },
        "datasets": {},
    }

    for ds_path in dataset_paths:
        ds_name = os.path.basename(ds_path)
        samples = load_emotion_dataset(ds_path)
        if not samples:
            print(f"⚠  No samples loaded from {ds_path}, skipping.")
            continue

        print(f"\n{'='*60}")
        print(f"Dataset: {ds_name}  ({len(samples)} samples)")
        print(f"{'='*60}")

        ds_results: dict = {}
        for model_name, clf_fn in models.items():
            report = evaluate_classifier(samples, clf_fn, labels=LABELS)
            ds_results[model_name] = report

            # Confusion matrix visualisation
            cm = report.get("confusion_matrix", {})
            img_path = save_confusion_matrix_image(
                cm, LABELS, f"{model_name} – {ds_name}", output_dir,
            )

            # Per-model detailed table
            print(f"\n--- {model_name} ---")
            print(format_summary_table(report))
            if img_path:
                print(f"  Confusion matrix saved: {img_path}")
            else:
                print("\n  Confusion matrix (text):")
                print(render_confusion_matrix_text(cm, LABELS))

        all_results["datasets"][ds_name] = ds_results

        # Cross-model comparison
        print(f"\n  Comparison — {ds_name}")
        print(format_comparison_table(ds_results))

    # --- Write JSON output ---------------------------------------------------
    json_path = os.path.join(output_dir, "evaluation_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n✅ Results saved to {json_path}")

    # --- Clean up temp files -------------------------------------------------
    if temp_path and os.path.exists(temp_path):
        os.unlink(temp_path)

    return all_results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and run the benchmark."""
    parser = argparse.ArgumentParser(
        description="Benchmark emotion detection models on standard datasets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dataset", nargs="+", metavar="PATH",
        help="Path(s) to evaluation dataset files (.jsonl, .json, .csv).",
    )
    parser.add_argument(
        "--output", default=".", metavar="DIR",
        help="Output directory for evaluation_results.json and plots "
             "(default: current directory).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run on built-in synthetic data (no dataset file needed).",
    )
    args = parser.parse_args(argv)

    run_benchmark(
        dataset_paths=args.dataset,
        output_dir=args.output,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
