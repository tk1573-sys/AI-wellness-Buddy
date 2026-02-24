"""
Evaluation Framework for AI Wellness Buddy — Experimental Validation.

Provides:
- Simulated distress scenario generators (gradual decline / sudden drop /
  recovery / stable-positive)
- OLS vs EWMA prediction benchmarking with MAE / RMSE
- Emotion detection accuracy metrics (precision / recall / F1)
- Statistical analysis helpers (t-test, Pearson correlation, confidence
  intervals, detection confusion-matrix metrics)

Usage (research / thesis experiments)
--------------------------------------
>>> from evaluation_framework import run_prediction_benchmark
>>> results = run_prediction_benchmark()
>>> for row in results:
...     print(row['scenario'], row['ols'], row['ewma'])

>>> from evaluation_framework import evaluate_heuristic_classifier
>>> from emotion_analyzer import EmotionAnalyzer
>>> report = evaluate_heuristic_classifier(EmotionAnalyzer())
>>> print(report['overall_accuracy'], report['macro_f1'])

Academic justification
-----------------------
The evaluation follows standard NLP benchmark methodology:
- Leave-one-out cross-validation (LOO-CV) for small sequence datasets
- Welch's two-sample t-test for statistical significance (unequal variances)
- Pearson r for drift–risk correlation analysis
- 95 % confidence intervals via normal approximation
"""

import math
import random

from prediction_agent import PredictionAgent, EWMAPredictor


# ============================================================================
# Simulated scenario generators
# ============================================================================

def generate_gradual_decline_scenario(n=15, start=0.4, end=-0.6):
    """
    Gradually declining sentiment over *n* steps (linear interpolation).

    Simulates a user whose emotional state worsens steadily over the
    observation window — typical of sustained situational stress.

    Parameters
    ----------
    n     : number of data points
    start : initial polarity value (positive)
    end   : final polarity value (negative)

    Returns
    -------
    list[float]
    """
    step = (end - start) / max(n - 1, 1)
    return [round(start + i * step, 4) for i in range(n)]


def generate_sudden_drop_scenario(n=15, baseline=0.3, drop=-0.8, drop_at=10):
    """
    Stable positive baseline followed by a sudden severe drop at *drop_at*.

    Simulates acute crisis events (bereavement, assault, acute episode) that
    would be missed by a trend model trained only on the initial stable period.

    Parameters
    ----------
    n        : total number of data points
    baseline : positive sentiment during stable period
    drop     : negative sentiment after the event
    drop_at  : index at which the drop occurs (0-based)
    """
    values = [baseline] * n
    for i in range(min(drop_at, n), n):
        values[i] = drop
    return [round(v, 4) for v in values]


def generate_recovery_pattern_scenario(n=15, low=-0.6, recovery=0.2):
    """
    Starts at a low (distressed) level and gradually recovers.

    Tests whether prediction models correctly identify *improving* trajectories
    so that positive drift does not trigger spurious distress alerts.

    Parameters
    ----------
    n        : number of data points
    low      : initial (distressed) polarity
    recovery : target (recovered) polarity
    """
    step = (recovery - low) / max(n - 1, 1)
    return [round(low + i * step, 4) for i in range(n)]


def generate_stable_positive_scenario(n=15, level=0.5, noise=0.08, seed=42):
    """
    Stable positive baseline with small random noise.

    Expected outcome: INFO / LOW risk, no pre-distress warning.
    Used as a negative control in detection-accuracy experiments.

    Parameters
    ----------
    n     : number of data points
    level : mean polarity
    noise : uniform ± noise amplitude
    seed  : random seed for reproducibility
    """
    rng = random.Random(seed)
    return [round(max(-1.0, min(1.0, level + rng.uniform(-noise, noise))), 4)
            for _ in range(n)]


def generate_volatile_scenario(n=20, seed=7):
    """
    Highly volatile sequence oscillating between positive and negative.

    Tests stability-index and volatility computation.  High volatility should
    produce a lower stability_index and potentially elevated risk score.
    """
    rng = random.Random(seed)
    polarity = 0.0
    history = []
    for _ in range(n):
        polarity += rng.uniform(-0.5, 0.5)
        polarity = max(-1.0, min(1.0, polarity))
        history.append(round(polarity, 4))
    return history


# ============================================================================
# Basic statistical helpers
# ============================================================================

def compute_mae(predicted, actual):
    """
    Mean Absolute Error between two equal-length lists.

    MAE = (1/n) × Σ |p_i − a_i|

    Returns ``None`` when inputs are empty or of unequal length.
    """
    if not predicted or len(predicted) != len(actual):
        return None
    return round(sum(abs(p - a) for p, a in zip(predicted, actual)) / len(predicted), 4)


def compute_rmse(predicted, actual):
    """
    Root Mean Squared Error.

    RMSE = √( (1/n) × Σ (p_i − a_i)² )

    More sensitive to large individual errors than MAE; useful for detecting
    scenarios where a model occasionally makes very poor predictions.
    """
    if not predicted or len(predicted) != len(actual):
        return None
    mse = sum((p - a) ** 2 for p, a in zip(predicted, actual)) / len(predicted)
    return round(math.sqrt(mse), 4)


def compute_correlation(x, y):
    """
    Pearson product-moment correlation coefficient between *x* and *y*.

    Used to measure the strength of the linear relationship between
    drift score and distress risk level across sessions.

    Returns value in [-1, 1] or ``None`` for degenerate inputs.
    """
    n = len(x)
    if n != len(y) or n < 2:
        return None
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    den_x = sum((xi - x_mean) ** 2 for xi in x) ** 0.5
    den_y = sum((yi - y_mean) ** 2 for yi in y) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return round(num / (den_x * den_y), 4)


def compute_confidence_interval(values, confidence=0.95):
    """
    Compute mean and 95 % (or other) confidence interval using the
    normal approximation (suitable when n ≥ 30; acceptable for n ≥ 10).

    Returns
    -------
    dict : {'mean': float, 'ci_lower': float, 'ci_upper': float, 'std': float}
    """
    n = len(values)
    if n < 2:
        return None
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    std = math.sqrt(variance)
    # z-score for the given confidence level (normal approximation)
    z = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}.get(confidence, 1.960)
    margin = z * std / math.sqrt(n)
    return {
        'mean':     round(mean, 4),
        'ci_lower': round(mean - margin, 4),
        'ci_upper': round(mean + margin, 4),
        'std':      round(std, 4),
        'n':        n,
    }


def run_t_test(group_a, group_b):
    """
    Welch's two-sample t-test (does not assume equal variances).

    Used to test statistical significance of OLS vs EWMA performance
    differences and heuristic vs ML classifier accuracy.

    Returns
    -------
    (t_statistic, p_value) or (None, None) for degenerate inputs.

    p-value is computed via scipy.stats if available, otherwise via a
    normal-distribution approximation (accurate for large n).
    """
    n_a, n_b = len(group_a), len(group_b)
    if n_a < 2 or n_b < 2:
        return None, None

    mean_a = sum(group_a) / n_a
    mean_b = sum(group_b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in group_a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in group_b) / (n_b - 1)

    se = math.sqrt(var_a / n_a + var_b / n_b)
    if se == 0:
        return 0.0, 1.0

    t = (mean_a - mean_b) / se

    try:
        from scipy import stats
        df = ((var_a / n_a + var_b / n_b) ** 2
              / ((var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)))
        p = float(2 * stats.t.sf(abs(t), df))
    except ImportError:
        # Normal approximation (accurate for |t| and large df)
        p = 2 * (1 - _normal_cdf(abs(t)))

    return round(t, 4), round(p, 6)


def _normal_cdf(z):
    """Standard normal cumulative distribution function (approximation)."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ============================================================================
# Detection / classification metrics
# ============================================================================

def compute_detection_metrics(tp, fp, tn, fn):
    """
    Compute standard binary-classification metrics from a confusion matrix.

    Parameters
    ----------
    tp, fp, tn, fn : int  (true/false positives/negatives)

    Returns
    -------
    dict : precision, recall (sensitivity), specificity, f1_score, accuracy
    """
    precision   = tp / (tp + fp)       if (tp + fp) > 0       else 0.0
    recall      = tp / (tp + fn)       if (tp + fn) > 0       else 0.0
    specificity = tn / (tn + fp)       if (tn + fp) > 0       else 0.0
    f1          = (2 * precision * recall / (precision + recall)
                   if (precision + recall) > 0 else 0.0)
    accuracy    = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
    return {
        'precision':   round(precision,   4),
        'recall':      round(recall,      4),
        'specificity': round(specificity, 4),
        'f1_score':    round(f1,          4),
        'accuracy':    round(accuracy,    4),
    }


# ============================================================================
# Prediction model benchmarking
# ============================================================================

def run_prediction_benchmark(scenarios=None):
    """
    Benchmark OLS vs EWMA predictors on the provided *scenarios*.

    Uses leave-one-out cross-validation on the last third of each scenario
    sequence (training on the first two-thirds, evaluating on the rest).

    Parameters
    ----------
    scenarios : dict[str, list[float]] | None
        Mapping of scenario name → sentiment history.
        Defaults to the four canonical distress scenarios.

    Returns
    -------
    list[dict]
        Each entry: ``{'scenario', 'n_test', 'ols': {mae, rmse}, 'ewma': {mae, rmse}}``

    Research use
    ------------
    Results populate Table 5.2 and Figure 5.1 in the thesis.  The t-test
    p-value between OLS MAE and EWMA MAE vectors is reported in Section 5.2.
    """
    if scenarios is None:
        scenarios = {
            'gradual_decline':  generate_gradual_decline_scenario(),
            'sudden_drop':      generate_sudden_drop_scenario(),
            'recovery':         generate_recovery_pattern_scenario(),
            'stable_positive':  generate_stable_positive_scenario(),
        }

    ols_agent  = PredictionAgent()
    ewma_agent = EWMAPredictor(alpha=0.3)
    results = []

    for name, history in scenarios.items():
        split      = max(3, len(history) * 2 // 3)
        train_end  = split
        test_slice = history[train_end:]

        ols_preds, ewma_preds, actuals = [], [], []
        for i in range(len(test_slice)):
            window   = history[:train_end + i]
            ols_r    = ols_agent.predict_next_sentiment(window)
            ewma_r   = ewma_agent.predict_next(window)
            if ols_r is not None and ewma_r is not None:
                ols_preds.append(ols_r['predicted_value'])
                ewma_preds.append(ewma_r)
                actuals.append(test_slice[i])

        row = {
            'scenario': name,
            'n_test':   len(actuals),
            'ols':  {
                'mae':  compute_mae(ols_preds, actuals),
                'rmse': compute_rmse(ols_preds, actuals),
            },
            'ewma': {
                'mae':  compute_mae(ewma_preds, actuals),
                'rmse': compute_rmse(ewma_preds, actuals),
            },
        }
        results.append(row)

    return results


# ============================================================================
# Heuristic classifier evaluation
# ============================================================================

#: Built-in benchmark drawn from GoEmotions representative patterns.
#: Shared with emotion_analyzer._BENCHMARK_TEST_CASES for consistency.
_BENCHMARK_TEST_CASES = [
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


def evaluate_heuristic_classifier(analyzer, test_cases=None):
    """
    Run the keyword+polarity heuristic emotion classifier on *test_cases*.

    Computes per-class precision / recall / F1 and macro averages.

    Parameters
    ----------
    analyzer   : EmotionAnalyzer instance
    test_cases : list[tuple[str, str]] | None  (defaults to benchmark above)

    Returns
    -------
    dict
        ``per_class_metrics`` — dict[emotion → {precision, recall, f1}]
        ``overall_accuracy``  — float
        ``macro_precision``   — float
        ``macro_recall``      — float
        ``macro_f1``          — float
        ``test_cases``        — int

    Research use
    ------------
    These figures appear in Table 5.1 (Emotion Detection Accuracy) of the
    thesis, column "Heuristic (Rule-Based)".  A companion column,
    "Transformer ML (when available)", is populated by
    ``EmotionAnalyzer.classify_emotion_ml()`` on the same benchmark.
    """
    if test_cases is None:
        test_cases = _BENCHMARK_TEST_CASES

    emotion_classes = ['joy', 'sadness', 'anger', 'fear', 'anxiety', 'neutral', 'crisis']
    tp = {c: 0 for c in emotion_classes}
    fp = {c: 0 for c in emotion_classes}
    fn = {c: 0 for c in emotion_classes}

    for text, true_label in test_cases:
        result = analyzer.classify_emotion(text)
        pred   = result.get('primary_emotion', 'neutral')
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

    totals   = len(test_cases)
    correct  = sum(tp.values())
    macro_p  = sum(v['precision'] for v in per_class.values()) / len(emotion_classes)
    macro_r  = sum(v['recall']    for v in per_class.values()) / len(emotion_classes)
    macro_f  = sum(v['f1']        for v in per_class.values()) / len(emotion_classes)

    return {
        'per_class_metrics': per_class,
        'overall_accuracy':  round(correct / totals, 4),
        'macro_precision':   round(macro_p, 4),
        'macro_recall':      round(macro_r, 4),
        'macro_f1':          round(macro_f, 4),
        'test_cases':        totals,
    }


# ============================================================================
# Risk detection simulation
# ============================================================================

def simulate_risk_detection_on_scenarios():
    """
    Run the PatternTracker risk scoring pipeline on all canonical scenarios
    and return a summary table for the thesis evaluation chapter.

    Returns
    -------
    list[dict]
        Each entry: ``{'scenario', 'risk_score', 'risk_level',
        'stability_index', 'drift_score', 'emotion_distribution'}``
    """
    from pattern_tracker import PatternTracker
    from datetime import datetime

    def _make_emotion(polarity):
        primary = 'joy' if polarity > 0.2 else ('neutral' if polarity > -0.1
                                                 else 'sadness')
        return {
            'emotion': 'positive' if polarity > 0 else 'negative',
            'severity': 'low' if polarity > 0 else 'medium',
            'polarity': polarity,
            'subjectivity': 0.5,
            'distress_keywords': [],
            'abuse_indicators': [],
            'has_abuse_indicators': False,
            'timestamp': datetime.now(),
            'primary_emotion': primary,
            'emotion_scores': {},
            'explanation': '',
            'is_crisis': False,
            'crisis_keywords': [],
            'detected_script': 'english',
        }

    scenarios = {
        'gradual_decline':  generate_gradual_decline_scenario(),
        'sudden_drop':      generate_sudden_drop_scenario(),
        'recovery':         generate_recovery_pattern_scenario(),
        'stable_positive':  generate_stable_positive_scenario(),
        'volatile':         generate_volatile_scenario(),
    }

    results = []
    for name, history in scenarios.items():
        tracker = PatternTracker()
        for v in history:
            tracker.add_emotion_data(_make_emotion(v))

        score, level = tracker.compute_risk_score()
        _, stability = tracker.get_volatility_and_stability()
        drift        = tracker.get_emotional_drift_score()
        distribution = tracker.get_emotion_distribution()

        results.append({
            'scenario':          name,
            'risk_score':        score,
            'risk_level':        level,
            'stability_index':   stability,
            'drift_score':       drift,
            'emotion_distribution': distribution,
        })

    return results
