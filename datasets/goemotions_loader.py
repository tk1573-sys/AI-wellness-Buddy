"""
GoEmotions dataset loader.

Loads the `GoEmotions <https://github.com/google-research/google-research/tree/master/goemotions>`_
dataset either from JSONL/CSV files or via the HuggingFace ``datasets`` library,
cleans text samples, and maps the fine-grained GoEmotions labels to the seven
system emotion classes used by the AI Wellness Buddy
(joy, sadness, anger, fear, anxiety, neutral, crisis).

Public API
----------
- ``GOEMOTIONS_LABEL_MAP`` — full mapping from GoEmotions labels → system labels
- ``load_goemotions(path, ...)`` — load & clean a local file, return list of dicts
- ``load_goemotions_hf(split, ...)`` — load via HuggingFace ``datasets`` library
"""

from __future__ import annotations

import csv
import json
import logging
import re

logger = logging.getLogger(__name__)

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

# Canonical system labels (includes crisis for completeness; GoEmotions
# samples will not produce crisis via label mapping, but the label is
# reserved for custom datasets and the overall system schema).
SYSTEM_LABELS: tuple[str, ...] = (
    "joy", "sadness", "anger", "fear", "anxiety", "neutral", "crisis",
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


# ── HuggingFace datasets loader ─────────────────────────────────────────

def load_goemotions_hf(
    split: str = "test",
    *,
    subset: str = "simplified",
    max_samples: int | None = None,
) -> list[dict[str, str]]:
    """Load GoEmotions from the HuggingFace ``datasets`` hub.

    Uses the ``go_emotions`` dataset (``google-research-datasets/go_emotions``).
    When the ``datasets`` library is not installed this function raises
    ``ImportError`` with a helpful message so callers can fall back to
    :func:`load_goemotions` (file-based loading).

    Parameters
    ----------
    split : str
        Dataset split — ``"train"``, ``"validation"``, or ``"test"``.
    subset : str
        Dataset configuration — ``"simplified"`` (28→1 label) or ``"raw"``.
    max_samples : int or None
        When set, truncate the loaded split to at most this many samples.

    Returns
    -------
    list[dict[str, str]]
        Each element is ``{"text": <cleaned_text>, "label": <system_label>}``.

    Raises
    ------
    ImportError
        If the ``datasets`` package is not installed.
    """
    try:
        from datasets import load_dataset  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "The 'datasets' package is required to use load_goemotions_hf(). "
            "Install it with: pip install datasets"
        ) from exc

    logger.info("Loading GoEmotions '%s' split from HuggingFace Hub …", split)
    ds = load_dataset("google-research-datasets/go_emotions", subset, split=split)

    # The 'simplified' subset exposes a 'labels' column with integer indices
    # into ds.features['labels'].feature.names (Sequence(ClassLabel).feature.names)
    try:
        label_names: list[str] = ds.features["labels"].feature.names
    except (AttributeError, KeyError) as exc:
        raise ValueError(
            f"Unexpected dataset schema — could not read label names from "
            f"ds.features['labels'].feature.names: {exc}"
        ) from exc

    samples: list[dict[str, str]] = []
    for row in ds:
        text = _clean_text(str(row.get("text", "")))
        if not text:
            continue
        raw_ids: list[int] = row.get("labels", [])
        if raw_ids:
            raw_label = label_names[raw_ids[0]]
        else:
            raw_label = "neutral"
        label = map_label(raw_label)
        samples.append({"text": text, "label": label})
        if max_samples is not None and len(samples) >= max_samples:
            break

    logger.info("Loaded %d samples from GoEmotions '%s' split.", len(samples), split)
    return samples
