"""
Transformer-based emotion classifier with lazy loading and rule-based fallback.

Model
-----
``j-hartmann/emotion-english-distilroberta-base`` (GoEmotions-style 7-class
output: joy, sadness, anger, fear, disgust, surprise, neutral) mapped to the
internal schema used by the rest of the AI Wellness Buddy system.

Design principles
-----------------
* **Lazy loading** – the heavy transformer pipeline is only downloaded and
  initialised on the first call to :meth:`classify`, not at import time.
* **CPU inference** – ``device=-1`` ensures the model runs on CPU so the
  module works on machines without a GPU.
* **Graceful fallback** – when ``transformers`` or ``torch`` are not
  installed (or the model cannot be fetched), the classifier automatically
  falls back to lightweight keyword-based emotion detection so callers
  always receive a valid probability distribution.
* **Normalised output** – every return value is a ``dict`` whose values
  sum to 1.0 (within floating-point tolerance).
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Cached pipeline loader – uses @st.cache_resource when Streamlit is
# available so that the heavy HuggingFace model is downloaded and
# initialised only once per process, surviving Streamlit script reruns.
# In non-Streamlit contexts (FastAPI, tests, CLI) a process-level dict
# cache prevents redundant model loads across multiple WellnessAgentPipeline
# instances in the same worker (critical for sub-2 s warm-request latency).
# ---------------------------------------------------------------------------

# Process-level model cache for non-Streamlit environments.
_PROCESS_PIPELINE_CACHE: dict[str, object] = {}


def _load_emotion_pipeline_impl(model_name: str):
    """Load the HuggingFace emotion pipeline (uncached helper)."""
    from transformers import pipeline as _hf_pipeline
    return _hf_pipeline(
        "text-classification",
        model=model_name,
        top_k=None,
        device=-1,
    )


try:
    import streamlit as _st

    @_st.cache_resource
    def load_emotion_pipeline(model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        """Streamlit-cached emotion pipeline loader."""
        return _load_emotion_pipeline_impl(model_name)
except Exception:
    # Streamlit not installed or not in a Streamlit runtime — use a
    # process-level dict so the model is loaded at most once per worker.
    def load_emotion_pipeline(model_name: str = "j-hartmann/emotion-english-distilroberta-base"):  # type: ignore[misc]
        """Process-cached emotion pipeline loader (non-Streamlit)."""
        if model_name not in _PROCESS_PIPELINE_CACHE:
            _PROCESS_PIPELINE_CACHE[model_name] = _load_emotion_pipeline_impl(model_name)
        return _PROCESS_PIPELINE_CACHE[model_name]


class EmotionTransformer:
    """Transformer-based emotion classifier with rule-based keyword fallback.

    Parameters
    ----------
    model_name : str, optional
        HuggingFace model identifier.  Defaults to
        ``j-hartmann/emotion-english-distilroberta-base``.
    """

    _DEFAULT_MODEL = "j-hartmann/emotion-english-distilroberta-base"

    # Maximum input length (characters) — the underlying DistilRoBERTa model
    # supports up to 512 word-piece tokens; character-level truncation is a
    # simple safeguard against excessively long inputs.
    _MAX_INPUT_LENGTH = 512

    # GoEmotions 7-class → internal schema mapping
    _LABEL_MAP: dict[str, str] = {
        "joy":      "joy",
        "sadness":  "sadness",
        "anger":    "anger",
        "fear":     "fear",
        "disgust":  "anxiety",   # nearest semantic equivalent
        "surprise": "joy",
        "neutral":  "neutral",
    }

    # Canonical emotion labels returned by the module
    EMOTIONS: tuple[str, ...] = (
        "joy", "sadness", "anger", "fear", "anxiety", "neutral",
    )

    # ---- lightweight keyword lists used by the rule-based fallback ----
    _KEYWORD_MAP: dict[str, list[str]] = {
        "joy": [
            "happy", "joyful", "excited", "wonderful", "amazing", "love",
            "great", "fantastic", "thrilled", "delighted", "cheerful",
            "grateful", "blessed", "elated", "euphoric", "content",
            "pleased", "glad", "overjoyed", "celebrate", "proud",
        ],
        "sadness": [
            "sad", "depressed", "sorrowful", "miserable", "grief", "cry",
            "crying", "tears", "heartbroken", "devastated", "melancholy",
            "gloomy", "despair", "hopeless", "lonely", "alone",
            "mourning", "loss", "empty", "numb", "broken",
        ],
        "anger": [
            "angry", "furious", "annoyed", "frustrated", "rage", "mad",
            "hate", "resentful", "irritated", "outraged", "livid",
            "bitter", "hostile", "agitated", "enraged", "infuriated",
        ],
        "fear": [
            "scared", "afraid", "terrified", "dread", "frightened",
            "phobia", "horror", "panic", "timid", "petrified",
            "shaking", "trembling", "fearful", "dreading",
        ],
        "anxiety": [
            "anxious", "stressed", "overwhelmed", "tense", "uneasy",
            "worried", "worry", "apprehensive", "restless", "nervous",
            "on edge", "can't sleep", "racing thoughts", "tight chest",
            "pit in my stomach", "catastrophe", "what if", "uncertain",
        ],
        "neutral": [
            "okay", "fine", "alright", "so-so", "average", "ordinary",
            "normal", "moderate", "not bad", "not great", "just okay",
            "managing", "getting by", "neither", "neutral", "indifferent",
        ],
    }

    # ------------------------------------------------------------------
    def __init__(self, model_name: str | None = None):
        self._model_name: str = model_name or self._DEFAULT_MODEL
        self._pipeline = None
        self._load_attempted: bool = False
        self._available: bool = False

        # Single-message inference cache (avoids multiple passes per message)
        self._cache_key: str | None = None
        self._cache_value: dict[str, float] | None = None

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def available(self) -> bool:
        """``True`` when the transformer pipeline is ready for inference."""
        if not self._load_attempted:
            self._try_load()
        return self._available

    # ------------------------------------------------------------------
    # Lazy loader
    # ------------------------------------------------------------------

    def _try_load(self) -> None:
        """Attempt to load the HuggingFace pipeline (once).

        Uses the module-level :func:`load_emotion_pipeline` which is
        decorated with ``@st.cache_resource`` when Streamlit is available,
        ensuring the heavy model is loaded only once per process.
        """
        if self._load_attempted:
            return
        self._load_attempted = True
        try:
            self._pipeline = load_emotion_pipeline(self._model_name)
            self._available = True
        except Exception:
            # ImportError, OSError (model not cached), RuntimeError, …
            self._available = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, text: str) -> dict[str, float]:
        """Return a normalised emotion probability distribution.

        When the transformer model is available the probabilities come from
        the model; otherwise a rule-based keyword count is used.

        Returns
        -------
        dict[str, float]
            Keys are emotion labels from :attr:`EMOTIONS`.
            Values are probabilities that sum to 1.0.
        """
        if not self._load_attempted:
            self._try_load()

        # Check single-message cache
        if self._cache_key is not None and self._cache_key == text:
            return dict(self._cache_value)  # return a copy

        if self._available and self._pipeline is not None:
            result = self._classify_transformer(text)
        else:
            result = self._classify_keywords(text)

        # Populate cache
        self._cache_key = text
        self._cache_value = result
        return dict(result)  # return a copy

    # ------------------------------------------------------------------
    # Internal classifiers
    # ------------------------------------------------------------------

    def _classify_transformer(self, text: str) -> dict[str, float]:
        """Run transformer inference and map labels to internal schema."""
        try:
            raw = self._pipeline(text[:self._MAX_INPUT_LENGTH])[0]
            mapped: dict[str, float] = {e: 0.0 for e in self.EMOTIONS}
            for entry in raw:
                label = self._LABEL_MAP.get(
                    entry["label"].lower(), entry["label"].lower(),
                )
                if label in mapped:
                    mapped[label] += entry["score"]
            return self._normalize(mapped)
        except Exception:
            # Any runtime failure → fall back to keywords
            return self._classify_keywords(text)

    def _classify_keywords(self, text: str) -> dict[str, float]:
        """Simple keyword-count classifier (rule-based fallback)."""
        text_lower = text.lower()
        scores: dict[str, float] = {e: 0.0 for e in self.EMOTIONS}
        for emotion, keywords in self._KEYWORD_MAP.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[emotion] += 1.0
        return self._normalize(scores)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(scores: dict[str, float]) -> dict[str, float]:
        """Normalise *scores* so values sum to 1.0.

        If all scores are zero a uniform distribution is returned.
        """
        total = sum(scores.values())
        if total == 0:
            n = len(scores)
            return {k: round(1.0 / n, 4) for k in scores}
        return {k: round(v / total, 4) for k, v in scores.items()}

    def invalidate_cache(self) -> None:
        """Clear the single-message inference cache."""
        self._cache_key = None
        self._cache_value = None

    def classify_keywords_only(self, text: str) -> dict[str, float]:
        """Return keyword-based probability distribution (no transformer).

        This is the public API for obtaining keyword-only predictions,
        useful for benchmarking the rule-based baseline independently.

        Returns
        -------
        dict[str, float]
            Keys are emotion labels from :attr:`EMOTIONS`.
            Values are probabilities that sum to 1.0.
        """
        return self._classify_keywords(text)
