#!/usr/bin/env python3
"""
Benchmark the transformer-based emotion classifier on the GoEmotions dataset.

Pipeline
--------
1. Load GoEmotions dataset (via :mod:`datasets.goemotions_loader`)
2. Run emotion transformer predictions
3. Compute evaluation metrics (precision, recall, macro F1, accuracy, confusion matrix)
4. Save results to ``results/emotion_model_benchmark.json``
5. Optionally save confusion-matrix visualisation to ``plots/``

Usage
-----
::

    # Benchmark on a real GoEmotions file
    python run_emotion_benchmark.py --dataset path/to/goemotions.jsonl

    # Dry-run with synthetic data (no dataset file needed)
    python run_emotion_benchmark.py --dry-run

    # Limit sample count for quick iteration
    python run_emotion_benchmark.py --dataset data.jsonl --max-samples 1000

    # Export session results
    python run_emotion_benchmark.py --dry-run --export-results results/session_emotion_analysis.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

# Ensure the project root is importable
_PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from datasets.goemotions_loader import load_goemotions, SYSTEM_LABELS  # noqa: E402
from evaluation.emotion_model_evaluation import (                      # noqa: E402
    evaluate_emotion_model,
    compute_metrics,
    format_summary_table,
)
from benchmark_emotion_models import (                                 # noqa: E402
    save_confusion_matrix_image,
    render_confusion_matrix_text,
    _SYNTHETIC_SAMPLES,
)


# ── Synthetic dataset helper ───────────────────────────────────────────

def _create_synthetic_goemotions_file() -> str:
    """Write synthetic samples in GoEmotions JSONL format and return path."""
    fd, path = tempfile.mkstemp(suffix=".jsonl", prefix="goemotions_synth_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for text, label in _SYNTHETIC_SAMPLES:
            json.dump({"text": text, "labels": [label]}, f)
            f.write("\n")
    return path


# ── CSV export ─────────────────────────────────────────────────────────

def export_results_csv(
    samples: list[dict[str, str]],
    predictions: list[str],
    confidences: list[float],
    output_path: str,
) -> None:
    """Write per-sample results to a CSV file.

    Columns: timestamp, text, true_label, predicted_emotion, confidence.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "text", "true_label",
            "predicted_emotion", "confidence",
        ])
        for sample, pred, conf in zip(samples, predictions, confidences):
            writer.writerow([
                ts, sample["text"], sample["label"], pred, f"{conf:.4f}",
            ])


# ── Main benchmark ─────────────────────────────────────────────────────

def run(
    dataset_path: str | None = None,
    dry_run: bool = False,
    max_samples: int | None = None,
    export_csv_path: str | None = None,
) -> dict:
    """Run the emotion model benchmark pipeline.

    Returns the evaluation report dict.
    """
    results_dir = os.path.join(_PROJECT_ROOT, "results")
    plots_dir = os.path.join(_PROJECT_ROOT, "plots")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    # ── Resolve dataset ──────────────────────────────────────────────
    temp_path: str | None = None
    if dry_run or not dataset_path:
        temp_path = _create_synthetic_goemotions_file()
        dataset_path = temp_path

    # ── Load samples ─────────────────────────────────────────────────
    samples = load_goemotions(dataset_path, max_samples=max_samples)
    if not samples:
        print("⚠  No samples loaded — aborting.")
        return {"error": "No samples loaded"}

    # ── Build classifier ─────────────────────────────────────────────
    from models.emotion_transformer import EmotionTransformer

    _et = EmotionTransformer()

    predictions: list[str] = []
    confidences: list[float] = []

    def _classifier(text: str) -> str:
        probs = _et.classify(text)
        best = max(probs, key=probs.get)
        predictions.append(best)
        confidences.append(probs.get(best, 0.0))
        return best

    # ── Evaluate ─────────────────────────────────────────────────────
    eval_samples = [(s["text"], s["label"]) for s in samples]
    from research_evaluation import evaluate_classifier
    report = evaluate_classifier(eval_samples, _classifier, labels=list(SYSTEM_LABELS))

    report["dataset"] = "GoEmotions"
    report["precision_macro"] = report.get("macro_precision", 0.0)
    report["recall_macro"] = report.get("macro_recall", 0.0)
    report["transformer_available"] = _et.available

    # ── Print summary ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"GoEmotions Benchmark  ({report['samples']} samples)")
    print(f"Transformer available: {_et.available}")
    print(f"{'='*60}")
    print(format_summary_table(report))

    # ── Confusion matrix ─────────────────────────────────────────────
    cm = report.get("confusion_matrix", {})
    img = save_confusion_matrix_image(
        cm, list(SYSTEM_LABELS), "Emotion Transformer", plots_dir,
    )
    if img:
        print(f"\nConfusion matrix saved: {img}")
    else:
        print("\nConfusion matrix (text):")
        print(render_confusion_matrix_text(cm, list(SYSTEM_LABELS)))

    # ── Save JSON report ─────────────────────────────────────────────
    json_path = os.path.join(results_dir, "emotion_model_benchmark.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n✅ Results saved to {json_path}")

    # ── Optional CSV export ──────────────────────────────────────────
    if export_csv_path:
        export_results_csv(samples, predictions, confidences, export_csv_path)
        print(f"✅ Per-sample results exported to {export_csv_path}")

    # ── Cleanup ──────────────────────────────────────────────────────
    if temp_path and os.path.exists(temp_path):
        os.unlink(temp_path)

    return report


# ── CLI entry point ────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark emotion model on GoEmotions dataset.",
    )
    parser.add_argument(
        "--dataset", metavar="PATH",
        help="Path to GoEmotions dataset file (.jsonl, .csv, .json).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Use built-in synthetic data (no dataset file needed).",
    )
    parser.add_argument(
        "--max-samples", type=int, default=None,
        help="Limit the number of samples to evaluate.",
    )
    parser.add_argument(
        "--export-results", metavar="PATH", default=None,
        help="Export per-sample results to a CSV file.",
    )
    args = parser.parse_args(argv)

    run(
        dataset_path=args.dataset,
        dry_run=args.dry_run,
        max_samples=args.max_samples,
        export_csv_path=args.export_results,
    )


if __name__ == "__main__":
    main()
