"""
evaluation.py — IEEE Benchmark Evaluation for AI Wellness Buddy.

Compares two model configurations on a labelled sample-conversation dataset:

  Baseline  : keyword-only (rule-based) classifier, no user-profile
               personalization.
  Proposed  : full hybrid (transformer + keyword, dynamic-α fusion) classifier
               augmented with user-profile personal-trigger matching.

Metrics
-------
  emotion_accuracy          – fraction of correct top-1 emotion predictions
  risk_detection_rate       – recall on crisis / high-distress samples
  personalization_score_avg – mean per-sample confidence boost from personal
                               triggers (trigger-matching samples only)

Logged per prediction
---------------------
  input_text          – original user utterance
  predicted_emotion   – model's top-1 emotion label
  actual_emotion      – ground-truth label from the test dataset
  risk_flag           – True when model detects crisis / severe distress
  response_type       – "crisis" | "high" | "medium" | "low" (concern level)

Output files
------------
  results/results.json  – full structured JSON report
  Comparison table printed to stdout.

Usage
-----
  python evaluation.py                # run with built-in sample dataset
  python evaluation.py --output dir/  # write results to a custom directory
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Sample test dataset
# Each entry: (text, true_label, has_personal_trigger)
#   true_label          : canonical emotion from {joy, sadness, anger, fear,
#                         anxiety, neutral, crisis}
#   has_personal_trigger: True when the text contains a user-profile trigger
#                         keyword (simulates personalisation relevance)
# ---------------------------------------------------------------------------

_TEST_DATASET: list[tuple[str, str, bool]] = [
    # -- joy --
    ("I feel so happy and excited about the new job!", "joy", False),
    ("What a wonderful and amazing day it has been", "joy", False),
    ("I am grateful and blessed to have such great friends", "joy", False),
    ("Everything is going great, I feel fantastic today", "joy", False),
    # -- sadness --
    ("I am so sad and lonely, nothing feels right anymore", "sadness", False),
    ("Crying all night, feeling heartbroken and empty inside", "sadness", False),
    ("I feel hopeless and depressed about my future", "sadness", False),
    ("The grief and loss I feel every day is overwhelming", "sadness", False),
    # -- anger --
    ("I am furious and angry about what happened at work", "anger", True),
    ("This is so frustrating, I hate this whole situation", "anger", False),
    ("I am livid and outraged by the unfair treatment", "anger", False),
    ("So irritated and annoyed with everything and everyone", "anger", False),
    # -- fear --
    ("I am scared and terrified of what might happen next", "fear", False),
    ("The dread and horror keep me up all night every night", "fear", False),
    ("I feel frightened and panicked about the upcoming exam", "fear", True),
    # -- anxiety --
    ("I am anxious and stressed about the upcoming deadline", "anxiety", True),
    ("Feeling overwhelmed and worried about my work situation", "anxiety", True),
    ("Can't sleep, racing thoughts about all the what-ifs", "anxiety", False),
    ("I feel tense and uneasy about my relationship problems", "anxiety", True),
    ("Everything feels urgent and I can't keep up with my exams", "anxiety", True),
    # -- neutral --
    ("Things are okay, just a normal day going by", "neutral", False),
    ("I am fine, nothing special happening right now", "neutral", False),
    ("Everything is average, getting by as usual today", "neutral", False),
    ("Just managing, not bad not great at the moment", "neutral", False),
    ("It was an ordinary day at the office", "neutral", True),
    # -- crisis --
    ("I want to kill myself, there is no reason to live anymore", "crisis", False),
    ("I can't cope, I want to end it all right now", "crisis", False),
    ("I have been thinking about suicide, nothing matters", "crisis", False),
    ("I feel so hopeless I just want to disappear forever", "crisis", False),
    ("I am going to hurt myself, I see no other way out", "crisis", False),
]

# User-profile personal triggers (simulates a user's known sensitive topics)
_PERSONAL_TRIGGERS: list[str] = [
    "exam", "deadline", "work", "relationship", "family",
]

# Emotion labels used in the system
_LABELS: list[str] = ["joy", "sadness", "anger", "fear", "anxiety", "neutral", "crisis"]

# Concern level mapping for response_type
_CRISIS_EMOTIONS: set[str] = {"crisis"}
_HIGH_EMOTIONS: set[str] = {"sadness", "fear", "anger"}
_MEDIUM_EMOTIONS: set[str] = {"anxiety"}


# ---------------------------------------------------------------------------
# Helper: classify with baseline (keyword-only) or personalized (hybrid)
# ---------------------------------------------------------------------------

def _build_classifiers():
    """Lazily import EmotionAnalyzer and return (baseline_fn, personalized_fn).

    baseline_fn(text)     -> dict  (keyword-only, no profile)
    personalized_fn(text) -> dict  (hybrid + personal-trigger boost)
    """
    from emotion_analyzer import EmotionAnalyzer

    _analyzer = EmotionAnalyzer()

    def _baseline(text: str) -> dict:
        return _analyzer.classify_emotion(text, fusion_mode="keyword_only")

    def _personalized(text: str) -> dict:
        result = _analyzer.classify_emotion(text, fusion_mode="hybrid")
        # Apply personal-trigger boost: if any trigger keyword appears in the
        # text, strengthen the confidence of the primary emotion to reflect
        # personalisation (adds 0.15 confidence, capped at 1.0).
        text_lower = text.lower()
        if any(t in text_lower for t in _PERSONAL_TRIGGERS):
            boost = 0.15
            base_conf = result.get("emotion_confidence", 0.0)
            result = dict(result)  # shallow copy
            result["emotion_confidence"] = min(1.0, base_conf + boost)
            result["personalization_boost"] = boost
        else:
            result = dict(result)
            result["personalization_boost"] = 0.0
        return result

    return _baseline, _personalized


# ---------------------------------------------------------------------------
# Prediction logger
# ---------------------------------------------------------------------------

def _log_prediction(
    text: str,
    result: dict,
    actual_emotion: str,
) -> dict:
    """Extract fields from a classify_emotion result into a log entry."""
    predicted_emotion = result.get("primary_emotion", "neutral")
    is_crisis = result.get("is_crisis", False) or predicted_emotion == "crisis"

    # Determine response_type from concern_level or emotion
    concern = result.get("concern_level", "")
    if concern == "critical" or predicted_emotion in _CRISIS_EMOTIONS:
        response_type = "crisis"
    elif concern == "high" or predicted_emotion in _HIGH_EMOTIONS:
        response_type = "high"
    elif concern == "medium" or predicted_emotion in _MEDIUM_EMOTIONS:
        response_type = "medium"
    else:
        response_type = "low"

    return {
        "input_text": text,
        "predicted_emotion": predicted_emotion,
        "actual_emotion": actual_emotion,
        "risk_flag": bool(is_crisis),
        "response_type": response_type,
        "emotion_confidence": round(result.get("emotion_confidence", 0.0), 4),
        "personalization_boost": round(result.get("personalization_boost", 0.0), 4),
    }


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------

def _compute_metrics(logs: list[dict], model_name: str) -> dict:
    """Compute emotion_accuracy, risk_detection_rate, per-class P/R/F1, etc."""
    labels = _LABELS
    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    fn: dict[str, int] = defaultdict(int)

    # Risk detection (crisis label = positive class)
    risk_tp = risk_fp = risk_fn = risk_tn = 0
    correct = 0

    for log in logs:
        pred = log["predicted_emotion"]
        true = log["actual_emotion"]
        risk_flag = log["risk_flag"]
        is_crisis_true = (true == "crisis")

        if pred == true:
            correct += 1
            tp[pred] += 1
        else:
            fp[pred] += 1
            fn[true] += 1

        # Risk detection metrics
        if is_crisis_true and risk_flag:
            risk_tp += 1
        elif not is_crisis_true and risk_flag:
            risk_fp += 1
        elif is_crisis_true and not risk_flag:
            risk_fn += 1
        else:
            risk_tn += 1

    n = len(logs)
    emotion_accuracy = round(correct / n, 4) if n else 0.0

    # Per-class metrics
    per_class: dict[str, dict] = {}
    for c in labels:
        p = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0.0
        r = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0.0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        per_class[c] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f, 4),
        }

    classes_with_support = [c for c in labels if (tp[c] + fn[c]) > 0]
    n_classes = len(classes_with_support) or 1
    macro_precision = round(
        sum(per_class[c]["precision"] for c in classes_with_support) / n_classes, 4
    )
    macro_recall = round(
        sum(per_class[c]["recall"] for c in classes_with_support) / n_classes, 4
    )
    macro_f1 = round(
        sum(per_class[c]["f1"] for c in classes_with_support) / n_classes, 4
    )

    # Risk detection rate = recall on crisis class
    risk_detection_rate = round(
        risk_tp / (risk_tp + risk_fn) if (risk_tp + risk_fn) > 0 else 0.0, 4
    )

    # Personalization score: mean boost for trigger-matching samples
    boosted = [log["personalization_boost"] for log in logs if log["personalization_boost"] > 0]
    personalization_score_avg = round(sum(boosted) / len(boosted), 4) if boosted else 0.0

    return {
        "model": model_name,
        "samples": n,
        "emotion_accuracy": emotion_accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "risk_detection_rate": risk_detection_rate,
        "personalization_score_avg": personalization_score_avg,
        "per_class_metrics": per_class,
        "risk_confusion": {
            "tp": risk_tp,
            "fp": risk_fp,
            "fn": risk_fn,
            "tn": risk_tn,
        },
    }


# ---------------------------------------------------------------------------
# Comparison table printer
# ---------------------------------------------------------------------------

def _print_comparison_table(
    baseline_metrics: dict,
    proposed_metrics: dict,
) -> str:
    """Format and return a human-readable comparison table."""
    col_a = "Baseline (keyword-only)"
    col_b = "Proposed (hybrid+triggers)"
    w = 28

    rows = [
        ("Metric", col_a, col_b),
        ("-" * 30, "-" * w, "-" * w),
        (
            "accuracy",
            f"{baseline_metrics['emotion_accuracy']:.4f}",
            f"{proposed_metrics['emotion_accuracy']:.4f}",
        ),
        (
            "precision (macro)",
            f"{baseline_metrics['macro_precision']:.4f}",
            f"{proposed_metrics['macro_precision']:.4f}",
        ),
        (
            "recall (macro)",
            f"{baseline_metrics['macro_recall']:.4f}",
            f"{proposed_metrics['macro_recall']:.4f}",
        ),
        (
            "F1-score (macro)",
            f"{baseline_metrics['macro_f1']:.4f}",
            f"{proposed_metrics['macro_f1']:.4f}",
        ),
        (
            "risk_detection_rate",
            f"{baseline_metrics['risk_detection_rate']:.4f}",
            f"{proposed_metrics['risk_detection_rate']:.4f}",
        ),
        (
            "personalization_score_avg",
            f"{baseline_metrics['personalization_score_avg']:.4f}",
            f"{proposed_metrics['personalization_score_avg']:.4f}",
        ),
    ]

    lines = []
    header_sep = "=" * (30 + w * 2 + 8)
    lines.append(header_sep)
    lines.append("  AI Wellness Buddy — IEEE Evaluation Results")
    lines.append(header_sep)
    for metric, val_a, val_b in rows:
        lines.append(f"  {metric:<30}  {val_a:<{w}}  {val_b:<{w}}")
    lines.append(header_sep)
    table = "\n".join(lines)
    print(table)
    return table


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_evaluation(
    dataset: list[tuple[str, str, bool]] | None = None,
    output_dir: str = "results",
) -> dict:
    """Run the full evaluation pipeline and return the results dict.

    Parameters
    ----------
    dataset : list of (text, true_label, has_trigger) triples, or None
        When *None*, the built-in sample dataset is used.
    output_dir : str
        Directory where ``results.json`` is written.

    Returns
    -------
    dict
        Full structured results (suitable for JSON serialisation).
    """
    if dataset is None:
        dataset = _TEST_DATASET

    os.makedirs(output_dir, exist_ok=True)

    print("\n🔄  Building classifiers …")
    baseline_fn, personalized_fn = _build_classifiers()

    # --- Run predictions ---------------------------------------------------
    baseline_logs: list[dict] = []
    proposed_logs: list[dict] = []

    print(f"▶  Evaluating {len(dataset)} samples …")
    for text, true_label, _has_trigger in dataset:
        b_result = baseline_fn(text)
        p_result = personalized_fn(text)
        baseline_logs.append(_log_prediction(text, b_result, true_label))
        proposed_logs.append(_log_prediction(text, p_result, true_label))

    # --- Compute metrics ----------------------------------------------------
    baseline_metrics = _compute_metrics(baseline_logs, "Baseline (keyword-only)")
    proposed_metrics = _compute_metrics(proposed_logs, "Proposed (hybrid+triggers)")

    # --- Print comparison table --------------------------------------------
    print()
    comparison_table = _print_comparison_table(baseline_metrics, proposed_metrics)

    # --- Assemble full result -----------------------------------------------
    timestamp = datetime.now(timezone.utc).isoformat()
    results = {
        "meta": {
            "timestamp": timestamp,
            "dataset_size": len(dataset),
            "labels": _LABELS,
            "personal_triggers": _PERSONAL_TRIGGERS,
        },
        "baseline": {
            "metrics": baseline_metrics,
            "predictions": baseline_logs,
        },
        "proposed": {
            "metrics": proposed_metrics,
            "predictions": proposed_logs,
        },
        "comparison_table": comparison_table,
    }

    # --- Save JSON ----------------------------------------------------------
    json_path = os.path.join(output_dir, "results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✅  Results saved to {json_path}")

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and run the evaluation."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate AI Wellness Buddy emotion models for IEEE paper results.\n\n"
            "Compares:\n"
            "  Baseline  : keyword-only (rule-based), no personalization\n"
            "  Proposed  : hybrid (transformer+keyword) + personal triggers\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output",
        default="results",
        metavar="DIR",
        help="Output directory for results.json (default: results/).",
    )
    args = parser.parse_args(argv)

    run_evaluation(output_dir=args.output)


if __name__ == "__main__":
    main()
