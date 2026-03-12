"""
Research-grade dataset evaluation utilities.

Supports standard precision/recall/F1 evaluation for public emotion datasets:
- GoEmotions
- EmotionLines
- DailyDialog
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


def normalize_emotion_label(label):
    return _NORMALIZED_LABELS.get(str(label).strip().lower(), 'neutral')


def load_emotion_dataset(path, text_key='text', label_key='label'):
    """
    Load a dataset from .jsonl, .json, or .csv into [(text, label)].
    """
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
            for line in f:
                row = json.loads(line)
                text = str(row.get(text_key, '')).strip()
                labels = row.get('labels')
                if isinstance(labels, list) and labels:
                    label = normalize_emotion_label(labels[0])
                else:
                    label = normalize_emotion_label(row.get(label_key, 'neutral'))
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
    Evaluate a classifier function that maps text -> predicted_label.
    """
    labels = labels or ['joy', 'sadness', 'anger', 'fear', 'anxiety', 'neutral', 'crisis']
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    correct = 0
    for text, true_label in samples:
        pred = normalize_emotion_label(classifier_fn(text))
        if pred == true_label:
            correct += 1
            tp[pred] += 1
        else:
            fp[pred] += 1
            fn[true_label] += 1

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
    macro_p = sum(v['precision'] for v in per_class.values()) / len(per_class)
    macro_r = sum(v['recall'] for v in per_class.values()) / len(per_class)
    macro_f1 = sum(v['f1'] for v in per_class.values()) / len(per_class)

    return {
        'samples': len(samples),
        'accuracy': round(correct / total, 4),
        'macro_precision': round(macro_p, 4),
        'macro_recall': round(macro_r, 4),
        'macro_f1': round(macro_f1, 4),
        'per_class': per_class,
    }
