"""
Emotion model evaluation pipeline.

Wraps the core metric computations from :mod:`research_evaluation` and the
GoEmotions dataset loader from :mod:`datasets.goemotions_loader` into a
single evaluation entry-point.

Public API
----------
- ``evaluate_emotion_model(dataset_path, classifier_fn, ...)``
- ``compute_metrics(y_true, y_pred, labels)``
"""

from __future__ import annotations

import sys
import os

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
    SYSTEM_LABELS,
)

# Re-export for convenience
__all__ = [
    "evaluate_emotion_model",
    "compute_metrics",
    "format_summary_table",
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
            return _analyzer.classify_emotion(text)["primary_emotion"]

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
