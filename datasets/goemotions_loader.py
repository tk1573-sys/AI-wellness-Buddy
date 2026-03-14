"""
GoEmotions dataset loader.

Loads the `GoEmotions <https://github.com/google-research/google-research/tree/master/goemotions>`_
dataset from JSONL or CSV files, cleans text samples, and maps the
fine-grained GoEmotions labels to the six system emotion classes used
by the AI Wellness Buddy (joy, sadness, anger, fear, anxiety, neutral).

Public API
----------
- ``GOEMOTIONS_LABEL_MAP`` — full mapping from GoEmotions labels → system labels
- ``load_goemotions(path, ...)`` — load & clean dataset, return ``(texts, labels)``
"""

from __future__ import annotations

import csv
import json
import re

# ── GoEmotions (28 classes) → system emotion classes ────────────────────
GOEMOTIONS_LABEL_MAP: dict[str, str] = {
    # joy-family
    "admiration": "joy",
    "amusement": "joy",
    "approval": "joy",
    "caring": "joy",
    "desire": "joy",
    "excitement": "joy",
    "gratitude": "joy",
    "joy": "joy",
    "love": "joy",
    "optimism": "joy",
    "pride": "joy",
    "relief": "joy",
    # sadness-family
    "disappointment": "sadness",
    "grief": "sadness",
    "remorse": "sadness",
    "sadness": "sadness",
    # anger-family
    "anger": "anger",
    "annoyance": "anger",
    "disapproval": "anger",
    "disgust": "anger",
    # fear-family
    "fear": "fear",
    # anxiety-family
    "confusion": "anxiety",
    "embarrassment": "anxiety",
    "nervousness": "anxiety",
    # neutral
    "neutral": "neutral",
    "realization": "neutral",
    "surprise": "neutral",
    "curiosity": "neutral",
}

# Canonical system labels
SYSTEM_LABELS: tuple[str, ...] = (
    "joy", "sadness", "anger", "fear", "anxiety", "neutral",
)


# ── Text cleaning ──────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Normalise whitespace, strip leading/trailing spaces."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Public API ─────────────────────────────────────────────────────────

def map_label(raw_label: str) -> str:
    """Map a single GoEmotions label to the system emotion class.

    Unknown labels default to ``'neutral'``.
    """
    return GOEMOTIONS_LABEL_MAP.get(raw_label.strip().lower(), "neutral")


def load_goemotions(
    path: str,
    *,
    text_key: str = "text",
    label_key: str = "labels",
    max_samples: int | None = None,
) -> list[dict[str, str]]:
    """Load a GoEmotions dataset file and return cleaned, mapped samples.

    Parameters
    ----------
    path : str
        Path to a ``.jsonl`` or ``.csv`` file.
    text_key : str
        Field name for the text column (default ``"text"``).
    label_key : str
        Field name for the label column (default ``"labels"``).
        Supports both string labels and list-of-string labels.
    max_samples : int or None
        When set, load at most this many samples (useful for quick runs).

    Returns
    -------
    list[dict[str, str]]
        Each element is ``{"text": <cleaned_text>, "label": <system_label>}``.
    """
    raw_rows: list[dict] = []

    if path.endswith(".csv"):
        raw_rows = _load_csv(path, text_key, label_key)
    elif path.endswith(".jsonl"):
        raw_rows = _load_jsonl(path, text_key, label_key)
    else:
        # Try JSON array
        raw_rows = _load_json(path, text_key, label_key)

    # Clean & map
    samples: list[dict[str, str]] = []
    for row in raw_rows:
        text = _clean_text(row.get("text", ""))
        if not text:
            continue
        label = row.get("label", "neutral")
        samples.append({"text": text, "label": label})
        if max_samples is not None and len(samples) >= max_samples:
            break

    return samples


# ── Private loaders ────────────────────────────────────────────────────

def _extract_label(row: dict, label_key: str) -> str:
    """Extract and map a label from a row dict."""
    raw = row.get(label_key, row.get("label", "neutral"))
    if isinstance(raw, list):
        raw = raw[0] if raw else "neutral"
    return map_label(str(raw))


def _load_jsonl(path: str, text_key: str, label_key: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            obj = json.loads(stripped)
            rows.append({
                "text": str(obj.get(text_key, "")),
                "label": _extract_label(obj, label_key),
            })
    return rows


def _load_csv(path: str, text_key: str, label_key: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "text": str(row.get(text_key, "")),
                "label": _extract_label(row, label_key),
            })
    return rows


def _load_json(path: str, text_key: str, label_key: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("data", [])
    rows = []
    for obj in data:
        rows.append({
            "text": str(obj.get(text_key, "")),
            "label": _extract_label(obj, label_key),
        })
    return rows
