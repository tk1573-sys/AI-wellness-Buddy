"""
Research-grade dataset evaluation utilities.

Supports standard precision/recall/F1 evaluation for public emotion datasets:
- GoEmotions
- EmotionLines
- DailyDialog

Provides:
- ``load_emotion_dataset()``: Robust loader for .jsonl / .json / .csv with
  blank-line tolerance and per-line error reporting.
- ``evaluate_classifier()``: Full metric suite including precision, recall,
  macro/micro F1, confusion matrix, and ROC-AUC.
- ``evaluate_emotion_model()``: One-call helper for end-to-end benchmarking.
- ``format_summary_table()``: Plain-text table suitable for research papers.
"""

import csv
import json
from collections import defaultdict


_NORMALIZED_LABELS = {
    'happiness': 'joy',
    'joy': 'joy',
    'sadness': 'sadness',
    'sad': 'sadness',
    'anger': 'anger',
    'fear': 'fear',
    'anxiety': 'anxiety',
    'neutral': 'neutral',
    'surprise': 'joy',
    'disgust': 'anxiety',
    'suicidal': 'crisis',
    'crisis': 'crisis',
}

# Dataset-specific field mappings for well-known public benchmarks.
_DATASET_FIELD_MAPS = {
    'goemotions':   {'text_key': 'text',      'label_key': 'labels'},
    'emotionlines': {'text_key': 'utterance',  'label_key': 'emotion'},
    'dailydialog':  {'text_key': 'text',       'label_key': 'emotion'},
}


def normalize_emotion_label(label):
    return _NORMALIZED_LABELS.get(str(label).strip().lower(), 'neutral')


def _detect_dataset_type(path):
    """Return a dataset key from *_DATASET_FIELD_MAPS* if the filename matches."""
    lower = path.lower()
    for key in _DATASET_FIELD_MAPS:
        if key in lower:
            return key
    return None


def load_emotion_dataset(path, text_key='text', label_key='label',
                         dataset_type=None):
    """
    Load a dataset from .jsonl, .json, or .csv into ``[(text, label)]``.

    Parameters
    ----------
    path : str
        File path (.jsonl, .json, or .csv).
    text_key, label_key : str
        Column / field names.  Overridden automatically when *dataset_type*
        is provided or auto-detected from the filename.
    dataset_type : str or None
        One of ``'goemotions'``, ``'emotionlines'``, ``'dailydialog'``.
        When *None*, the loader attempts to detect the dataset from *path*.
    """
    # Auto-detect and apply dataset-specific field mappings.
    detected = dataset_type or _detect_dataset_type(path)
    if detected and detected in _DATASET_FIELD_MAPS:
        mapping = _DATASET_FIELD_MAPS[detected]
        text_key = mapping['text_key']
        label_key = mapping['label_key']

    samples = []
    if path.endswith('.csv'):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get(text_key, '').strip()
                label = normalize_emotion_label(row.get(label_key, 'neutral'))
                if text:
                    samples.append((text, label))
        return samples

    if path.endswith('.jsonl'):
        with open(path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    row = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON on line {line_no} of {path}: {exc}"
                    ) from exc
                text = str(row.get(text_key, '')).strip()
                labels = row.get('labels')
                if isinstance(labels, list) and labels:
                    label = normalize_emotion_label(labels[0])
                else:
                    label = normalize_emotion_label(
                        row.get(label_key, 'neutral')
                    )
                if text:
                    samples.append((text, label))
        return samples

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get('data', [])
    for row in data:
        text = str(row.get(text_key, '')).strip()
        label = normalize_emotion_label(row.get(label_key, 'neutral'))
        if text:
            samples.append((text, label))
    return samples


def evaluate_classifier(samples, classifier_fn, labels=None):
    """
    Evaluate a classifier function that maps text → predicted_label.

    Returns a dict with: samples, accuracy, macro/micro precision/recall/F1,
    per-class metrics, confusion_matrix, and roc_auc.
    """
    labels = labels or ['joy', 'sadness', 'anger', 'fear', 'anxiety', 'neutral', 'crisis']
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    label_counts = defaultdict(int)

    # Confusion matrix: confusion[true][pred] = count
    confusion = defaultdict(lambda: defaultdict(int))

    correct = 0
    predictions = []
    for text, true_label in samples:
        pred = normalize_emotion_label(classifier_fn(text))
        predictions.append((true_label, pred))
        confusion[true_label][pred] += 1
        label_counts[true_label] += 1
        if pred == true_label:
            correct += 1
            tp[pred] += 1
        else:
            fp[pred] += 1
            fn[true_label] += 1

    # --- per-class metrics ---
    per_class = {}
    for label in labels:
        precision = tp[label] / (tp[label] + fp[label]) if (tp[label] + fp[label]) else 0.0
        recall = tp[label] / (tp[label] + fn[label]) if (tp[label] + fn[label]) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        per_class[label] = {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1': round(f1, 4),
        }

    total = len(samples) if samples else 1

    # --- macro averages ---
    n_classes = len(per_class) or 1
    macro_p = sum(v['precision'] for v in per_class.values()) / n_classes
    macro_r = sum(v['recall'] for v in per_class.values()) / n_classes
    macro_f1 = sum(v['f1'] for v in per_class.values()) / n_classes

    # --- micro averages ---
    total_tp = sum(tp[l] for l in labels)
    total_fp = sum(fp[l] for l in labels)
    total_fn = sum(fn[l] for l in labels)
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0

    # --- confusion matrix as nested dict ---
    confusion_matrix = {
        true_label: dict(confusion[true_label]) for true_label in labels
    }

    # --- ROC-AUC approximation (one-vs-rest, binary per class) ---
    roc_auc = _compute_roc_auc(predictions, labels)

    return {
        'samples': len(samples),
        'accuracy': round(correct / total, 4),
        'macro_precision': round(macro_p, 4),
        'macro_recall': round(macro_r, 4),
        'macro_f1': round(macro_f1, 4),
        'micro_precision': round(micro_p, 4),
        'micro_recall': round(micro_r, 4),
        'micro_f1': round(micro_f1, 4),
        'per_class': per_class,
        'confusion_matrix': confusion_matrix,
        'roc_auc': roc_auc,
    }


def _compute_roc_auc(predictions, labels):
    """
    Compute a macro-averaged ROC-AUC approximation using one-vs-rest binary
    classification per label.

    Each class is scored as a binary task (correct-class vs. everything else)
    to produce a per-class AUC estimate.  The macro average is the unweighted
    mean across classes.  This avoids requiring probability outputs from the
    classifier while still providing a useful ranking metric.
    """
    per_class_auc = {}
    for label in labels:
        # binary: 1 if true_label == label, score 1 if pred == label
        y_true = []
        y_score = []
        for true_label, pred in predictions:
            y_true.append(1 if true_label == label else 0)
            y_score.append(1 if pred == label else 0)
        auc = _binary_auc(y_true, y_score)
        if auc is not None:
            per_class_auc[label] = round(auc, 4)
    if not per_class_auc:
        return None
    macro_auc = sum(per_class_auc.values()) / len(per_class_auc)
    return {
        'per_class': per_class_auc,
        'macro': round(macro_auc, 4),
    }


def _binary_auc(y_true, y_score):
    """
    AUC for binary labels/scores using the trapezoidal rule.

    Returns *None* when only one class is present (AUC is undefined).
    """
    positives = sum(y_true)
    negatives = len(y_true) - positives
    if positives == 0 or negatives == 0:
        return None

    # Sort descending by score, breaking ties by putting positive first
    paired = sorted(zip(y_score, y_true), key=lambda p: (-p[0], -p[1]))
    tp = 0
    fp = 0
    auc = 0.0
    prev_fpr = 0.0
    prev_tpr = 0.0
    for score, label in paired:
        if label == 1:
            tp += 1
        else:
            fp += 1
        fpr = fp / negatives
        tpr = tp / positives
        auc += (fpr - prev_fpr) * (tpr + prev_tpr) / 2.0
        prev_fpr = fpr
        prev_tpr = tpr
    return auc


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------

def evaluate_emotion_model(dataset_path, classifier_fn=None, dataset_type=None,
                           labels=None):
    """
    End-to-end helper: load dataset → classify → evaluate → return report.

    Parameters
    ----------
    dataset_path : str
        Path to a .jsonl / .json / .csv evaluation dataset.
    classifier_fn : callable or None
        A function ``text -> predicted_label``.  When *None* the default
        :class:`EmotionAnalyzer` keyword classifier is used.
    dataset_type : str or None
        One of ``'goemotions'``, ``'emotionlines'``, ``'dailydialog'``.
    labels : list[str] or None
        Label set; defaults to the standard 7 emotions.

    Returns
    -------
    dict
        Full evaluation report (same schema as ``evaluate_classifier``).
    """
    if classifier_fn is None:
        from emotion_analyzer import EmotionAnalyzer
        _analyzer = EmotionAnalyzer()
        classifier_fn = lambda text: _analyzer.classify_emotion(text)['primary_emotion']

    samples = load_emotion_dataset(dataset_path, dataset_type=dataset_type)
    return evaluate_classifier(samples, classifier_fn, labels=labels)


def format_summary_table(report):
    """
    Format an evaluation *report* as a plain-text table suitable for
    inclusion in research papers or console output.

    Example output::

        ┌─────────┬───────────┬────────┬────────┐
        │ Class   │ Precision │ Recall │   F1   │
        ├─────────┼───────────┼────────┼────────┤
        │ joy     │    0.8500 │ 0.9000 │ 0.8743 │
        │ sadness │    0.7200 │ 0.6800 │ 0.6994 │
        ...
        ├─────────┼───────────┼────────┼────────┤
        │ MACRO   │    0.7800 │ 0.7600 │ 0.7699 │
        │ MICRO   │    0.8100 │ 0.8100 │ 0.8100 │
        └─────────┴───────────┴────────┴────────┘

    Returns
    -------
    str
        Formatted table string.
    """
    per_class = report.get('per_class', {})
    lines = []
    header = f"{'Class':<12} {'Precision':>9} {'Recall':>9} {'F1':>9}"
    sep = '-' * len(header)
    lines.append(sep)
    lines.append(header)
    lines.append(sep)
    for label, metrics in per_class.items():
        lines.append(
            f"{label:<12} {metrics['precision']:>9.4f} "
            f"{metrics['recall']:>9.4f} {metrics['f1']:>9.4f}"
        )
    lines.append(sep)
    lines.append(
        f"{'MACRO':<12} {report.get('macro_precision', 0):>9.4f} "
        f"{report.get('macro_recall', 0):>9.4f} "
        f"{report.get('macro_f1', 0):>9.4f}"
    )
    lines.append(
        f"{'MICRO':<12} {report.get('micro_precision', 0):>9.4f} "
        f"{report.get('micro_recall', 0):>9.4f} "
        f"{report.get('micro_f1', 0):>9.4f}"
    )
    lines.append(sep)
    lines.append(f"Samples: {report.get('samples', 0)}  "
                 f"Accuracy: {report.get('accuracy', 0):.4f}")
    roc = report.get('roc_auc')
    if roc:
        lines.append(f"ROC-AUC (macro): {roc.get('macro', 'N/A')}")
    lines.append(sep)
    return '\n'.join(lines)
