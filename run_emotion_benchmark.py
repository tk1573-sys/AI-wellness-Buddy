#!/usr/bin/env python3
"""Benchmark keyword, transformer, and hybrid emotion models on GoEmotions.

Saves precision, recall, macro F1, accuracy → results/final_metrics.json.
Usage: python run_emotion_benchmark.py [--dataset PATH] [--max-samples N] [--dry-run]
"""
from __future__ import annotations
import argparse, json, os, sys, tempfile  # noqa: E401

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from datasets.goemotions_loader import load_goemotions, SYSTEM_LABELS  # noqa: E402
from research_evaluation import evaluate_classifier                     # noqa: E402
from benchmark_emotion_models import (                                  # noqa: E402
    _make_keyword_classifier, _make_transformer_classifier,
    _make_hybrid_classifier, _SYNTHETIC_SAMPLES,
)

LABELS = list(SYSTEM_LABELS)


def save_plots(final: dict, plots_dir: str) -> None:
    """Generate and save benchmark plots for the IEEE paper.

    Parameters
    ----------
    final : dict
        ``{model_name: {precision, recall, macro_f1, accuracy, confusion_matrix}, ...}``
    plots_dir : str
        Directory where ``model_comparison.png`` and ``confusion_matrix.png``
        are written (created if it does not exist).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(plots_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Model comparison bar chart
    # ------------------------------------------------------------------
    model_names = list(final.keys())
    metrics = ["precision", "recall", "macro_f1", "accuracy"]
    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots()
    for i, metric in enumerate(metrics):
        values = [final[m][metric] for m in model_names]
        ax.bar(x + i * width, values, width, label=metric.replace("_", " ").title())

    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
    ax.set_xticklabels(model_names)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison")
    ax.legend()
    fig.tight_layout()
    comparison_path = os.path.join(plots_dir, "model_comparison.png")
    fig.savefig(comparison_path)
    plt.close(fig)
    print(f"✅ Model comparison plot saved to {comparison_path}")

    # ------------------------------------------------------------------
    # 2. Confusion matrix for the best model (highest macro_f1)
    # ------------------------------------------------------------------
    best_model = max(final, key=lambda m: final[m]["macro_f1"])
    cm_data = final[best_model].get("confusion_matrix", {})
    if cm_data:
        cm_labels = LABELS
        matrix = np.array(
            [[cm_data.get(t, {}).get(p, 0) for p in cm_labels] for t in cm_labels],
            dtype=float,
        )
        fig2, ax2 = plt.subplots()
        im = ax2.imshow(matrix, aspect="auto", cmap="Blues")
        ax2.set_xticks(range(len(cm_labels)))
        ax2.set_yticks(range(len(cm_labels)))
        ax2.set_xticklabels(cm_labels, rotation=45, ha="right")
        ax2.set_yticklabels(cm_labels)
        ax2.set_xlabel("Predicted")
        ax2.set_ylabel("True")
        ax2.set_title(f"Confusion Matrix — {best_model}")
        plt.colorbar(im, ax=ax2)
        for r in range(len(cm_labels)):
            for c in range(len(cm_labels)):
                ax2.text(c, r, int(matrix[r, c]), ha="center", va="center", fontsize=8)
        fig2.tight_layout()
        cm_path = os.path.join(plots_dir, "confusion_matrix.png")
        fig2.savefig(cm_path)
        plt.close(fig2)
        print(f"✅ Confusion matrix plot saved to {cm_path}")


def _write_synthetic_jsonl() -> str:
    """Write synthetic GoEmotions JSONL to a temp file; return its path."""
    fd, path = tempfile.mkstemp(suffix=".jsonl", prefix="goe_synth_")
    with os.fdopen(fd, "w") as fh:
        for text, label in _SYNTHETIC_SAMPLES:
            json.dump({"text": text, "labels": [label]}, fh)
            fh.write("\n")
    return path


def run(dataset_path=None, dry_run=False, max_samples=None):
    """Evaluate all three models; print table; save results/final_metrics.json."""
    os.makedirs(os.path.join(_ROOT, "results"), exist_ok=True)
    tmp = None
    if dry_run or not dataset_path:
        tmp = _write_synthetic_jsonl()
        dataset_path = tmp
    samples = load_goemotions(dataset_path, max_samples=max_samples)
    if tmp and os.path.exists(tmp):
        os.unlink(tmp)
    if not samples:
        print("⚠  No samples loaded — aborting.")
        return {}
    eval_pairs = [(s["text"], s["label"]) for s in samples]
    transformer_clf, _ = _make_transformer_classifier()
    hybrid_clf, _ = _make_hybrid_classifier()
    models = {
        "Keyword":     _make_keyword_classifier(),
        "Transformer": transformer_clf,
        "Hybrid":      hybrid_clf,
    }
    final: dict = {}
    for name, clf in models.items():
        r = evaluate_classifier(eval_pairs, clf, labels=LABELS)
        final[name] = {
            "precision": r["macro_precision"],
            "recall":    r["macro_recall"],
            "macro_f1":  r["macro_f1"],
            "accuracy":  r["accuracy"],
            "confusion_matrix": r.get("confusion_matrix", {}),
        }
    hdr = f"{'Model':<22} {'Precision':>10} {'Recall':>9} {'Macro F1':>10} {'Accuracy':>10}"
    sep = "-" * len(hdr)
    print(f"\n{'='*62}\nGoEmotions Benchmark  ({len(samples)} samples)\n{'='*62}")
    print(sep); print(hdr); print(sep)
    for name, m in final.items():
        print(f"{name:<22} {m['precision']:>10.4f} {m['recall']:>9.4f}"
              f" {m['macro_f1']:>10.4f} {m['accuracy']:>10.4f}")
    print(sep)
    out = os.path.join(_ROOT, "results", "final_metrics.json")
    json_metrics = {
        name: {k: v for k, v in m.items() if k != "confusion_matrix"}
        for name, m in final.items()
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(json_metrics, fh, indent=2)
    print(f"\n✅ Results saved to {out}")
    save_plots(final, os.path.join(_ROOT, "plots"))
    return final


def main(argv=None):
    p = argparse.ArgumentParser(description="Benchmark emotion models on GoEmotions.")
    p.add_argument("--dataset", metavar="PATH",
                   help="Path to GoEmotions dataset (.jsonl/.csv/.json).")
    p.add_argument("--dry-run", action="store_true",
                   help="Use built-in synthetic data (no file needed).")
    p.add_argument("--max-samples", type=int, default=None,
                   help="Limit number of samples evaluated.")
    args = p.parse_args(argv)
    run(dataset_path=args.dataset, dry_run=args.dry_run, max_samples=args.max_samples)


if __name__ == "__main__":
    main()
