"""
Statistical significance tests for emotion classifier comparison.

Uses paired t-tests (:func:`scipy.stats.ttest_rel`) to determine whether
performance differences between classifiers are statistically significant.
All tests are *paired* because every classifier is evaluated on **the same**
samples, making McNemar / paired-t the appropriate choice.

Public API
----------
- ``compute_p_value(model_a_scores, model_b_scores)``
- ``interpret_p_value(p_value, alpha)``
- ``run_significance_tests(dataset, ...)``
- ``SIGNIFICANCE_THRESHOLD``
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
from datetime import datetime, timezone

from scipy.stats import ttest_rel  # noqa: E402

logger = logging.getLogger(__name__)

# Ensure the project root is importable
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# The significance level used when no explicit alpha is supplied
SIGNIFICANCE_THRESHOLD: float = 0.05

__all__ = [
    "compute_p_value",
    "interpret_p_value",
    "run_significance_tests",
    "SIGNIFICANCE_THRESHOLD",
]


# ---------------------------------------------------------------------------
# Core statistical primitives
# ---------------------------------------------------------------------------

def compute_p_value(
    model_a_scores: list[float],
    model_b_scores: list[float],
):
    """Perform a paired t-test and return the full result object.

    Parameters
    ----------
    model_a_scores : list[float]
        Per-sample scores for model A (e.g. ``1.0`` correct, ``0.0``
        incorrect).  Must have the same length as *model_b_scores*.
    model_b_scores : list[float]
        Per-sample scores for model B.

    Returns
    -------
    scipy.stats._stats_py.TtestResult
        The result of :func:`scipy.stats.ttest_rel`.  Access ``.statistic``
        for the t-statistic and ``.pvalue`` for the two-tailed p-value.

    Raises
    ------
    ValueError
        When either list is empty or when the lists differ in length.
    """
    if not model_a_scores or not model_b_scores:
        raise ValueError("Score lists must not be empty.")
    if len(model_a_scores) != len(model_b_scores):
        raise ValueError(
            f"Score lists must have the same length: "
            f"{len(model_a_scores)} vs {len(model_b_scores)}"
        )
    return ttest_rel(model_a_scores, model_b_scores)


def interpret_p_value(
    p_value: float,
    alpha: float = SIGNIFICANCE_THRESHOLD,
) -> str:
    """Return a human-readable interpretation of a p-value.

    Parameters
    ----------
    p_value : float
        The p-value from a statistical test.
    alpha : float
        Significance level threshold (default ``0.05``).

    Returns
    -------
    str
        ``"statistically significant"`` when *p_value* < *alpha*,
        ``"not statistically significant"`` otherwise.
        When *p_value* is ``NaN`` (e.g. identical score arrays), returns
        ``"indeterminate (scores identical)"`` .
    """
    if math.isnan(p_value):
        return "indeterminate (scores identical)"
    if p_value < alpha:
        return "statistically significant"
    return "not statistically significant"


# ---------------------------------------------------------------------------
# Per-sample score collection
# ---------------------------------------------------------------------------

def _collect_per_sample_scores(
    eval_samples: list[tuple[str, str]],
    classifier_fn,
) -> list[float]:
    """Return a per-sample correctness vector (1.0 = correct, 0.0 = wrong).

    Parameters
    ----------
    eval_samples : list[(text, true_label)]
        Evaluation dataset in the same format used by
        :func:`research_evaluation.evaluate_classifier`.
    classifier_fn : callable
        A function ``text → predicted_label``.

    Returns
    -------
    list[float]
        One entry per sample.
    """
    from research_evaluation import normalize_emotion_label  # local import
    scores: list[float] = []
    for text, true_label in eval_samples:
        pred = normalize_emotion_label(classifier_fn(text))
        scores.append(1.0 if pred == true_label else 0.0)
    return scores


# ---------------------------------------------------------------------------
# High-level runner
# ---------------------------------------------------------------------------

def run_significance_tests(
    dataset,
    *,
    max_samples: int | None = None,
    labels: list[str] | None = None,
    output_dir: str = ".",
    results_filename: str = "statistical_significance.json",
    alpha: float = SIGNIFICANCE_THRESHOLD,
    verbose: bool = True,
) -> dict:
    """Compare hybrid vs transformer and hybrid vs keyword using paired t-tests.

    All three classifiers are scored on **the same** dataset so that the
    t-test uses genuine paired observations.

    Parameters
    ----------
    dataset : str or list
        Either a file-path string (GoEmotions JSONL/CSV/JSON) **or** a
        pre-loaded list of ``{"text": ..., "label": ...}`` dicts (as
        returned by :func:`~datasets.goemotions_loader.load_goemotions`).
    max_samples : int or None
        When *dataset* is a file path, cap the number of loaded samples.
    labels : list[str] or None
        Label set; defaults to ``SYSTEM_LABELS`` from the GoEmotions loader.
    output_dir : str
        Base directory.  Results are written to
        ``{output_dir}/results/{results_filename}``.
    results_filename : str
        Output JSON filename (default ``"statistical_significance.json"``).
    alpha : float
        Significance level (default ``0.05``).
    verbose : bool
        When ``True``, print a summary table to stdout.

    Returns
    -------
    dict
        A dict with keys:

        * ``meta`` — run metadata (timestamp, samples, alpha, …)
        * ``p_value_hybrid_vs_transformer`` — two-tailed p-value
        * ``p_value_hybrid_vs_keyword`` — two-tailed p-value
        * ``t_statistic_hybrid_vs_transformer`` — t-statistic
        * ``t_statistic_hybrid_vs_keyword`` — t-statistic
        * ``interpretation_hybrid_vs_transformer`` — significance string
        * ``interpretation_hybrid_vs_keyword`` — significance string

    Raises
    ------
    ValueError
        When no samples could be loaded from *dataset*.
    """
    from datasets.goemotions_loader import load_goemotions, SYSTEM_LABELS  # local import
    from evaluation.emotion_model_evaluation import get_classifier  # local import

    labels = labels or list(SYSTEM_LABELS)

    # ── 1. Load dataset once ───────────────────────────────────────────────
    if isinstance(dataset, str):
        logger.info("Loading dataset from %s (max_samples=%s)", dataset, max_samples)
        samples = load_goemotions(dataset, max_samples=max_samples)
        dataset_name = os.path.basename(dataset)
    else:
        samples = list(dataset)
        dataset_name = "pre-loaded"

    if not samples:
        raise ValueError("No samples could be loaded from the provided dataset.")

    eval_samples = [(s["text"], s["label"]) for s in samples]
    logger.info("Loaded %d evaluation samples for significance testing.", len(eval_samples))

    # ── 2. Collect per-sample correctness for each model ──────────────────
    logger.info("Collecting per-sample scores …")
    scores: dict[str, list[float]] = {}
    for mode in ("keyword", "transformer", "hybrid"):
        clf = get_classifier(mode)
        scores[mode] = _collect_per_sample_scores(eval_samples, clf)

    # ── 3. Paired t-tests ─────────────────────────────────────────────────
    result_hvt = compute_p_value(scores["hybrid"], scores["transformer"])
    result_hvk = compute_p_value(scores["hybrid"], scores["keyword"])

    p_hvt = float(result_hvt.pvalue)
    p_hvk = float(result_hvk.pvalue)
    t_hvt = float(result_hvt.statistic)
    t_hvk = float(result_hvk.statistic)

    interp_hvt = interpret_p_value(p_hvt, alpha)
    interp_hvk = interpret_p_value(p_hvk, alpha)

    # ── 4. Build output payload ────────────────────────────────────────────
    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset_name,
        "samples": len(eval_samples),
        "alpha": alpha,
        "labels": labels,
    }
    output = {
        "meta": meta,
        "p_value_hybrid_vs_transformer": p_hvt,
        "p_value_hybrid_vs_keyword": p_hvk,
        "t_statistic_hybrid_vs_transformer": t_hvt,
        "t_statistic_hybrid_vs_keyword": t_hvk,
        "interpretation_hybrid_vs_transformer": interp_hvt,
        "interpretation_hybrid_vs_keyword": interp_hvk,
    }

    # ── 5. Console summary ─────────────────────────────────────────────────
    if verbose:
        _print_significance_summary(output, alpha)

    # ── 6. Save JSON results ───────────────────────────────────────────────
    results_dir = os.path.join(output_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    json_path = os.path.join(results_dir, results_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info("Statistical significance results saved to %s", json_path)
    if verbose:
        print(f"\nResults saved → {json_path}")

    return output


# ---------------------------------------------------------------------------
# Console formatter
# ---------------------------------------------------------------------------

def _print_significance_summary(results: dict, alpha: float) -> None:
    """Print a compact significance summary table to stdout."""
    comparisons = [
        ("Hybrid vs Transformer", "hybrid_vs_transformer"),
        ("Hybrid vs Keyword",     "hybrid_vs_keyword"),
    ]
    sep = "-" * 68
    print(f"\nStatistical Significance (α = {alpha})")
    print(sep)
    print(f"{'Comparison':<28} {'t-stat':>10} {'p-value':>12} {'Result'}")
    print(sep)
    for label, key in comparisons:
        t_val = results.get(f"t_statistic_{key}", float("nan"))
        p_val = results.get(f"p_value_{key}", float("nan"))
        interp = results.get(f"interpretation_{key}", "")
        t_str = f"{t_val:.4f}" if not math.isnan(t_val) else "NaN"
        p_str = f"{p_val:.4f}" if not math.isnan(p_val) else "NaN"
        print(f"{label:<28} {t_str:>10} {p_str:>12}  {interp}")
    print(sep)
