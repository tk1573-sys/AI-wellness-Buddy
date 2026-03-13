"""
Explainable AI (XAI) module for the AI Wellness Buddy emotion pipeline.

Provides lightweight, structured explanations for emotion predictions so
that users and researchers can understand *why* a particular emotion was
detected.  Functions are designed to add negligible latency to the
inference path.

Output format
-------------
::

    {
        "primary_emotion": "sadness",
        "confidence": 0.71,
        "key_indicators": ["overwhelmed", "lonely", "tired"],
        "sentiment_contribution": {
            "polarity": -0.45,
            "subjectivity": 0.72,
            "influence": "negative"
        },
        "model_source": "transformer + keyword hybrid"
    }
"""

from __future__ import annotations


# -----------------------------------------------------------------------
# Key-indicator extraction
# -----------------------------------------------------------------------

def extract_key_indicators(
    text: str,
    primary_emotion: str,
    emotion_keywords: dict[str, list[str]] | None = None,
    crisis_keywords: list[str] | None = None,
    max_indicators: int = 5,
) -> list[str]:
    """Return the top keyword indicators that drove the emotion prediction.

    Parameters
    ----------
    text : str
        The raw user message.
    primary_emotion : str
        The predicted emotion label (e.g. ``"sadness"``).
    emotion_keywords : dict, optional
        Mapping of emotion labels → keyword lists.  When *None* an empty
        dict is assumed.
    crisis_keywords : list, optional
        Separate list of crisis-specific keywords.
    max_indicators : int
        Maximum number of indicators to return.

    Returns
    -------
    list[str]
        Matched keywords, capped at *max_indicators*.
    """
    text_lower = text.lower()
    matched: list[str] = []

    if primary_emotion == "crisis" and crisis_keywords:
        matched = [kw for kw in crisis_keywords if kw in text_lower]
    elif emotion_keywords:
        keywords = emotion_keywords.get(primary_emotion, [])
        matched = [kw for kw in keywords if kw in text_lower]

    return matched[:max_indicators]


# -----------------------------------------------------------------------
# Sentiment contribution
# -----------------------------------------------------------------------

def get_sentiment_contribution(
    polarity: float,
    subjectivity: float,
) -> dict:
    """Summarise how sentiment polarity and subjectivity influenced the result.

    Returns
    -------
    dict
        ``polarity``, ``subjectivity``, and a human-readable ``influence``
        label (``"positive"``, ``"negative"``, or ``"neutral"``).
    """
    if polarity > 0.15:
        influence = "positive"
    elif polarity < -0.15:
        influence = "negative"
    else:
        influence = "neutral"

    return {
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4),
        "influence": influence,
    }


# -----------------------------------------------------------------------
# Model-source description
# -----------------------------------------------------------------------

def get_model_source(transformer_available: bool) -> str:
    """Return a human-readable label for the model(s) that contributed.

    Parameters
    ----------
    transformer_available : bool
        Whether the transformer pipeline was used for this prediction.
    """
    if transformer_available:
        return "transformer + keyword hybrid"
    return "keyword heuristic"


# -----------------------------------------------------------------------
# Structured explanation builder
# -----------------------------------------------------------------------

def generate_explanation(
    text: str,
    emotion_data: dict,
    *,
    emotion_keywords: dict[str, list[str]] | None = None,
    crisis_keywords: list[str] | None = None,
    transformer_available: bool = False,
) -> dict:
    """Build a structured XAI explanation dict for an emotion prediction.

    This is the main public entry point.  It combines keyword extraction,
    sentiment contribution, and model-source metadata into the canonical
    explanation format expected by the UI and API layers.

    Parameters
    ----------
    text : str
        Raw user input.
    emotion_data : dict
        The full result dict returned by
        ``EmotionAnalyzer.classify_emotion()``.
    emotion_keywords : dict, optional
        Emotion → keyword-list mapping (passed through from the analyser).
    crisis_keywords : list, optional
        Crisis keyword list (passed through from the analyser).
    transformer_available : bool
        Whether the transformer model was used.

    Returns
    -------
    dict
        Structured explanation with keys ``primary_emotion``,
        ``confidence``, ``key_indicators``, ``sentiment_contribution``,
        and ``model_source``.
    """
    primary = emotion_data.get("primary_emotion", "neutral")
    probs = emotion_data.get("emotion_probabilities", {})
    confidence = probs.get(primary, 0.0)

    indicators = extract_key_indicators(
        text,
        primary,
        emotion_keywords=emotion_keywords,
        crisis_keywords=crisis_keywords,
    )

    sentiment = get_sentiment_contribution(
        emotion_data.get("polarity", 0.0),
        emotion_data.get("subjectivity", 0.0),
    )

    return {
        "primary_emotion": primary,
        "confidence": round(confidence, 4),
        "key_indicators": indicators,
        "sentiment_contribution": sentiment,
        "model_source": get_model_source(transformer_available),
    }
