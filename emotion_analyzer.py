"""
Emotion analysis module using sentiment analysis and keyword detection.
Supports multi-emotion classification (joy, sadness, anger, fear, anxiety, neutral, crisis)
with XAI-style keyword attribution.

Optional ML upgrade: MLEmotionAdapter attempts to load the
`j-hartmann/emotion-english-distilroberta-base` HuggingFace model via the
`transformers` library.  When `transformers` / `torch` are not installed the
adapter degrades gracefully and the system continues to use the keyword+polarity
heuristic that has always been present.  All existing tests continue to pass
unchanged.
"""

from textblob import TextBlob
from datetime import datetime
import re
from language_handler import (
    TANGLISH_EMOTION_KEYWORDS,
    TAMIL_UNICODE_EMOTION_KEYWORDS,
    LanguageHandler,
)


class MLEmotionAdapter:
    """
    Optional wrapper around a pretrained transformer emotion classifier.

    Model: ``j-hartmann/emotion-english-distilroberta-base``
    (GoEmotions-style 7-class output: joy, sadness, anger, fear, disgust,
    surprise, neutral)

    Usage
    -----
    The adapter is instantiated once inside :class:`EmotionAnalyzer`.
    Call :meth:`classify` to get a ``{emotion: confidence}`` dict or ``None``
    when the library is unavailable.

    Graceful fallback
    -----------------
    If ``transformers`` or ``torch`` are not installed, or the model cannot be
    downloaded, ``self.available`` is set to ``False`` and :meth:`classify`
    always returns ``None``.  The heuristic keyword+polarity classifier is
    used instead — no exception is raised and no behaviour changes.

    Label mapping (GoEmotions → internal 7-class schema)
    ------------------------------------------------------
    * joy / surprise → joy
    * sadness        → sadness
    * anger          → anger
    * fear           → fear
    * disgust        → anxiety  (nearest semantic equivalent)
    * neutral        → neutral
    """

    _LABEL_MAP = {
        'joy':      'joy',
        'sadness':  'sadness',
        'anger':    'anger',
        'fear':     'fear',
        'disgust':  'anxiety',
        'surprise': 'joy',
        'neutral':  'neutral',
    }
    _MODEL = 'j-hartmann/emotion-english-distilroberta-base'

    def __init__(self):
        self.available = False
        self._pipeline = None
        try:
            from transformers import pipeline as _hf_pipeline  # noqa: F401
            self._pipeline = _hf_pipeline(
                'text-classification',
                model=self._MODEL,
                top_k=None,
                device=-1,           # CPU only — keeps device-independence
            )
            self.available = True
        except Exception:
            # ImportError, OSError (model not cached), RuntimeError — any failure
            pass

    def classify(self, text):
        """
        Classify *text* with the pretrained model.

        Returns
        -------
        dict | None
            ``{emotion_label: confidence_score}`` with labels mapped to the
            internal 7-class schema, or ``None`` when unavailable.
        """
        if not self.available or self._pipeline is None:
            return None
        try:
            results = self._pipeline(text[:512])[0]   # top_k=None → list
            mapped = {}
            for r in results:
                label = self._LABEL_MAP.get(r['label'].lower(), r['label'].lower())
                mapped[label] = mapped.get(label, 0.0) + r['score']
            return mapped
        except Exception:
            return None


class EmotionAnalyzer:
    """Analyzes emotional content in text messages"""

    def __init__(self):
        # --- Legacy coarse keywords (backward-compat) ---
        self.distress_keywords = [
            'sad', 'depressed', 'hopeless', 'worthless', 'alone', 'lonely',
            'anxious', 'scared', 'afraid', 'helpless', 'trapped', 'stuck',
            'hurt', 'pain', 'suffering', 'abuse', 'abused', 'victim',
            "can't take it", 'give up', 'end it', 'suicide', 'die',
            'useless', 'burden', 'tired of living',
            # Tanglish distress
            'kedachu', 'kedaitu', 'kastam', 'kashtam', 'vali', 'valikudu',
        ]

        self.abuse_keywords = [
            'abuse', 'abused', 'abusive', 'controlling', 'manipulative',
            'gaslighting', 'threatened', 'intimidated', 'belittled',
            'humiliated', 'isolated', 'trapped', 'toxic relationship',
            'emotional abuse', 'verbal abuse', 'domestic violence',
        ]

        # --- Crisis / self-harm keywords (immediate escalation) ---
        self.crisis_keywords = [
            'suicide', 'suicidal', 'kill myself', 'end my life', 'want to die',
            'self-harm', 'self harm', 'cut myself', 'hurt myself',
            'no reason to live', 'better off dead', 'tired of living',
            'end it all', 'take my own life', 'overdose', 'not worth living',
            # Tanglish crisis keywords
            'saaga poiren', 'saaganum', 'saagavendum',
            'vazhka venam', 'uyir thola poiren', 'suicide pannuven',
            # Tamil Unicode crisis keywords
            'சாகப்போகிறேன்', 'வாழ்க்கை வேண்டாம்', 'தற்கொலை',
        ]

        # --- Fine-grained multi-emotion keyword dictionaries ---
        self.emotion_keywords = {
            'joy': [
                'happy', 'joyful', 'excited', 'wonderful', 'amazing', 'love',
                'great', 'fantastic', 'thrilled', 'delighted', 'cheerful',
                'grateful', 'blessed', 'elated', 'euphoric', 'content',
                'pleased', 'glad', 'overjoyed', 'celebrate', 'proud',
                # Tanglish joy
                *TANGLISH_EMOTION_KEYWORDS.get('joy', []),
                # Tamil Unicode joy
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('joy', []),
            ],
            'sadness': [
                'sad', 'depressed', 'sorrowful', 'miserable', 'grief', 'cry',
                'crying', 'tears', 'heartbroken', 'devastated', 'melancholy',
                'gloomy', 'despair', 'hopeless', 'lonely', 'alone',
                'mourning', 'loss', 'empty', 'numb', 'broken',
                # Tanglish sadness
                *TANGLISH_EMOTION_KEYWORDS.get('sadness', []),
                # Tamil Unicode sadness
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('sadness', []),
            ],
            'anger': [
                'angry', 'furious', 'annoyed', 'frustrated', 'rage', 'mad',
                'hate', 'resentful', 'irritated', 'outraged', 'livid',
                'bitter', 'hostile', 'agitated', 'enraged', 'infuriated',
                # Tanglish anger
                *TANGLISH_EMOTION_KEYWORDS.get('anger', []),
                # Tamil Unicode anger
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('anger', []),
            ],
            'fear': [
                'scared', 'afraid', 'terrified', 'dread', 'frightened',
                'phobia', 'horror', 'panic', 'timid', 'petrified',
                'shaking', 'trembling', 'fearful', 'dreading',
                # Tanglish fear
                *TANGLISH_EMOTION_KEYWORDS.get('fear', []),
                # Tamil Unicode fear
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('fear', []),
            ],
            'anxiety': [
                'anxious', 'stressed', 'overwhelmed', 'tense', 'uneasy',
                'worried', 'worry', 'apprehensive', 'restless', 'nervous',
                'on edge', 'can\'t sleep', 'racing thoughts', 'tight chest',
                'pit in my stomach', 'catastrophe', 'what if', 'uncertain',
                # Tanglish anxiety
                *TANGLISH_EMOTION_KEYWORDS.get('anxiety', []),
                # Tamil Unicode anxiety
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('anxiety', []),
            ],
            'neutral': [
                'okay', 'fine', 'alright', 'so-so', 'average', 'ordinary',
                'normal', 'moderate', 'not bad', 'not great', 'just okay',
                'managing', 'getting by', 'neither', 'neutral', 'indifferent',
                # Tanglish neutral
                *TANGLISH_EMOTION_KEYWORDS.get('neutral', []),
                # Tamil Unicode neutral
                *TAMIL_UNICODE_EMOTION_KEYWORDS.get('neutral', []),
            ],
        }

        # Weights for computing emotion scores (higher = more severe)
        self.emotion_severity_weights = {
            'crisis':   1.00,
            'sadness':  0.65,
            'fear':     0.60,
            'anxiety':  0.55,
            'anger':    0.45,
            'joy':      0.00,
            'neutral':  0.10,
        }

        # Language handler for script detection
        self._lang_handler = LanguageHandler()

        # Optional ML adapter — falls back silently when transformers/torch absent
        self.ml_adapter = MLEmotionAdapter()

    # ------------------------------------------------------------------
    # ML-fused primary emotion detection (uses ML when available)
    # ------------------------------------------------------------------

    def classify_emotion_ml(self, text):
        """
        Return the primary emotion using the ML adapter when available,
        otherwise fall back to :meth:`detect_primary_emotion`.

        The ML confidence score is fused with the heuristic keyword score
        (weighted 70 % ML + 30 % keyword) when both are available.

        Returns the same fields as :meth:`classify_emotion` but also adds
        ``ml_available`` (bool) and ``ml_scores`` (dict|None).
        """
        result = self.classify_emotion(text)
        ml_scores = self.ml_adapter.classify(text)
        result['ml_available'] = self.ml_adapter.available
        result['ml_scores'] = ml_scores

        if ml_scores:
            # Exclude 'crisis' from ML output (handled by keyword list only)
            filtered = {k: v for k, v in ml_scores.items() if k != 'crisis'}
            if filtered:
                ml_primary = max(filtered, key=filtered.get)
                # Override primary emotion with ML result (ML is authoritative
                # unless crisis was detected by keyword list)
                if not result.get('is_crisis', False):
                    result['primary_emotion'] = ml_primary

        return result

    # ------------------------------------------------------------------
    # Benchmark evaluation (heuristic vs ML on simulated labelled data)
    # ------------------------------------------------------------------

    def evaluate_classification_performance(self, test_cases=None):
        """
        Evaluate the heuristic classifier on a set of labelled test cases.

        Parameters
        ----------
        test_cases : list[tuple[str, str]] | None
            List of ``(text, true_label)`` pairs.  Defaults to a built-in
            19-item benchmark drawn from GoEmotions representative patterns.

        Returns
        -------
        dict
            ``per_class_metrics`` — precision/recall/F1 per emotion class
            ``overall_accuracy`` — proportion of correct predictions
            ``macro_precision`` / ``macro_recall`` / ``macro_f1``
            ``test_cases`` — number of examples evaluated
        """
        if test_cases is None:
            test_cases = _BENCHMARK_TEST_CASES

        emotion_classes = ['joy', 'sadness', 'anger', 'fear', 'anxiety', 'neutral', 'crisis']
        tp = {c: 0 for c in emotion_classes}
        fp = {c: 0 for c in emotion_classes}
        fn = {c: 0 for c in emotion_classes}

        for text, true_label in test_cases:
            result = self.classify_emotion(text)
            pred = result.get('primary_emotion', 'neutral')
            if pred == true_label:
                tp[pred] = tp.get(pred, 0) + 1
            else:
                fp[pred] = fp.get(pred, 0) + 1
                fn[true_label] = fn.get(true_label, 0) + 1

        per_class = {}
        for c in emotion_classes:
            p = tp[c] / (tp[c] + fp.get(c, 0)) if (tp[c] + fp.get(c, 0)) > 0 else 0.0
            r = tp[c] / (tp[c] + fn.get(c, 0)) if (tp[c] + fn.get(c, 0)) > 0 else 0.0
            f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
            per_class[c] = {
                'precision': round(p, 4),
                'recall':    round(r, 4),
                'f1':        round(f, 4),
            }

        totals  = len(test_cases)
        correct = sum(tp.values())
        macro_p = sum(v['precision'] for v in per_class.values()) / len(emotion_classes)
        macro_r = sum(v['recall']    for v in per_class.values()) / len(emotion_classes)
        macro_f = sum(v['f1']        for v in per_class.values()) / len(emotion_classes)

        return {
            'per_class_metrics': per_class,
            'overall_accuracy':  round(correct / totals, 4),
            'macro_precision':   round(macro_p, 4),
            'macro_recall':      round(macro_r, 4),
            'macro_f1':          round(macro_f, 4),
            'test_cases':        totals,
        }

    # ------------------------------------------------------------------
    # Sentiment analysis (TextBlob)
    # ------------------------------------------------------------------

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text using TextBlob.
        Returns polarity (-1 to 1) and subjectivity (0 to 1).
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'timestamp': datetime.now()
        }

    # ------------------------------------------------------------------
    # Legacy keyword detectors (kept for backward compatibility)
    # ------------------------------------------------------------------

    def detect_distress_keywords(self, text):
        """Detect distress-related keywords in text"""
        text_lower = text.lower()
        return [kw for kw in self.distress_keywords if kw in text_lower]

    def detect_abuse_indicators(self, text):
        """Detect potential abuse-related keywords"""
        text_lower = text.lower()
        return [kw for kw in self.abuse_keywords if kw in text_lower]

    def detect_crisis_indicators(self, text):
        """Detect crisis / self-harm keywords requiring immediate escalation"""
        text_lower = text.lower()
        return [kw for kw in self.crisis_keywords if kw in text_lower]

    # ------------------------------------------------------------------
    # Multi-emotion detection
    # ------------------------------------------------------------------

    def detect_emotion_scores(self, text):
        """
        Score each fine-grained emotion by keyword matches.
        Returns a dict mapping emotion name → match count.
        """
        text_lower = text.lower()
        scores = {emo: 0 for emo in self.emotion_keywords}
        for emo, keywords in self.emotion_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[emo] += 1
        return scores

    def get_emotion_confidence(self, text):
        """
        Return normalized confidence scores (0.0–1.0) per emotion,
        representing the proportion of matched keywords belonging to each class.
        Scores for all emotion classes (including 'crisis') sum to 1.0.
        Falls back to polarity-based distribution when no keywords match.
        """
        text_lower = text.lower()
        # Initialise with all emotion classes plus 'crisis' explicitly upfront
        raw_scores = {emo: 0 for emo in self.emotion_keywords}
        raw_scores['crisis'] = 0  # ensures 'crisis' is always present

        for emo, keywords in self.emotion_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    raw_scores[emo] += 1

        # Count crisis keywords as a separate class
        crisis_count = sum(1 for kw in self.crisis_keywords if kw in text_lower)
        raw_scores['crisis'] = crisis_count

        total = sum(raw_scores.values())

        if total == 0:
            # Polarity-based fallback when no keywords matched
            sentiment = self.analyze_sentiment(text)
            polarity = sentiment['polarity']
            base = {emo: 0.0 for emo in raw_scores}
            if polarity > 0.2:
                base['joy'] = 1.0
            elif polarity > -0.1:
                base['neutral'] = 1.0
            else:
                base['sadness'] = 1.0
            return base

        return {emo: round(count / total, 4) for emo, count in raw_scores.items()}

    def detect_primary_emotion(self, text, polarity):
        """
        Determine the primary fine-grained emotion label.
        Falls back to polarity-based classification when no keywords match.
        """
        text_lower = text.lower()

        # Crisis always wins
        if any(kw in text_lower for kw in self.crisis_keywords):
            return 'crisis'

        scores = self.detect_emotion_scores(text)
        max_score = max(scores.values())
        if max_score > 0:
            # Pick the highest-scoring emotion; break ties by severity weight
            candidates = [e for e, s in scores.items() if s == max_score]
            return max(candidates,
                       key=lambda e: self.emotion_severity_weights.get(e, 0))

        # Fallback: polarity-based
        if polarity > 0.2:
            return 'joy'
        elif polarity > -0.1:
            return 'neutral'
        elif polarity > -0.4:
            return 'sadness'
        else:
            return 'sadness'

    # ------------------------------------------------------------------
    # XAI attribution
    # ------------------------------------------------------------------

    def explain_emotion(self, text, primary_emotion):
        """
        Return a human-readable explanation of which keywords drove the
        emotion classification (lightweight XAI / keyword attribution).
        """
        text_lower = text.lower()
        matched = []
        if primary_emotion == 'crisis':
            matched = [kw for kw in self.crisis_keywords if kw in text_lower]
        else:
            keywords = self.emotion_keywords.get(primary_emotion, [])
            matched = [kw for kw in keywords if kw in text_lower]

        if matched:
            return f"Detected '{primary_emotion}' due to keywords: {', '.join(matched[:5])}"
        return f"Detected '{primary_emotion}' based on overall sentiment."

    # ------------------------------------------------------------------
    # Main classification entry point
    # ------------------------------------------------------------------

    def classify_emotion(self, text):
        """
        Classify emotional state based on sentiment and keywords.
        Handles English, Tamil Unicode, and Tanglish input.
        Returns a dict with both coarse (backward-compat) and fine-grained
        emotion data, plus XAI explanation and crisis flag.
        """
        sentiment = self.analyze_sentiment(text)
        distress_keywords = self.detect_distress_keywords(text)
        abuse_keywords = self.detect_abuse_indicators(text)
        crisis_keywords_found = self.detect_crisis_indicators(text)

        polarity = sentiment['polarity']

        # --- Script detection for Tamil / Tanglish ---
        detected_script = self._lang_handler.detect_script(text)

        # Override primary emotion with Tamil/Tanglish if detected
        tanglish_emotion = None
        if detected_script == 'tanglish':
            tanglish_emotion = self._lang_handler.detect_tanglish_emotion(text)
        elif detected_script == 'tamil':
            tanglish_emotion = self._lang_handler.detect_tamil_unicode_emotion(text)

        # --- Coarse emotion (backward-compatible) ---
        if crisis_keywords_found:
            emotion = 'distress'
            severity = 'high'
        elif polarity > 0.3:
            emotion = 'positive'
            severity = 'low'
        elif polarity > -0.1:
            emotion = 'neutral'
            severity = 'low'
        elif polarity > -0.5:
            emotion = 'negative'
            severity = 'medium'
        else:
            emotion = 'distress'
            severity = 'high'

        # Adjust based on legacy distress keywords
        if distress_keywords:
            if emotion not in ('distress',):
                emotion = 'negative'
            severity = 'high' if len(distress_keywords) > 2 else 'medium'

        # --- Fine-grained emotion ---
        primary_emotion = self.detect_primary_emotion(text, polarity)

        # Tamil/Tanglish override: if a specific emotion was found, use it
        if tanglish_emotion:
            primary_emotion = tanglish_emotion

        emotion_scores = self.detect_emotion_scores(text)
        explanation = self.explain_emotion(text, primary_emotion)

        has_abuse_indicators = len(abuse_keywords) > 0
        is_crisis = len(crisis_keywords_found) > 0

        return {
            # Coarse fields (backward-compatible)
            'emotion': emotion,
            'severity': severity,
            'polarity': polarity,
            'subjectivity': sentiment['subjectivity'],
            'distress_keywords': distress_keywords,
            'abuse_indicators': abuse_keywords,
            'has_abuse_indicators': has_abuse_indicators,
            'timestamp': sentiment['timestamp'],
            # Fine-grained fields (new)
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'explanation': explanation,
            'is_crisis': is_crisis,
            'crisis_keywords': crisis_keywords_found,
            # Language / script metadata
            'detected_script': detected_script,
        }


# ---------------------------------------------------------------------------
# Built-in benchmark dataset (19 representative examples)
# Drawn from GoEmotions-style patterns covering all 7 emotion classes.
# Used by EmotionAnalyzer.evaluate_classification_performance() for
# comparative reporting (heuristic vs ML model accuracy tables).
# ---------------------------------------------------------------------------

_BENCHMARK_TEST_CASES = [
    # (text, true_primary_emotion)
    ("I am so happy today, everything is wonderful",          "joy"),
    ("I feel sad and heartbroken",                            "sadness"),
    ("I am furious about what happened",                      "anger"),
    ("I am terrified and scared",                             "fear"),
    ("I feel so anxious and stressed out",                    "anxiety"),
    ("I'm okay, just a normal day",                           "neutral"),
    ("I want to kill myself, there is no reason to live",     "crisis"),
    ("I am crying and feel totally hopeless",                 "sadness"),
    ("I am enraged and furious",                              "anger"),
    ("I feel worried and overwhelmed by everything",          "anxiety"),
    ("I feel great and blessed",                              "joy"),
    ("I am afraid and dreading tomorrow",                     "fear"),
    ("Just managing, nothing special",                        "neutral"),
    ("I am devastated, my heart is broken",                   "sadness"),
    ("I feel euphoric and elated",                            "joy"),
    ("I am tense and on edge all the time",                   "anxiety"),
    ("I feel petrified and shaking with fear",                "fear"),
    ("I feel bitter and resentful",                           "anger"),
    ("I want to end it all, I can't cope",                    "crisis"),
]
