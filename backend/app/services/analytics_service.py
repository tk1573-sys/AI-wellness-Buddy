"""Analytics service — research-grade metrics and plot generation.

Computes:
- Emotion distribution with percentages
- Average confidence and personalization score
- Risk trend over time
- Research summary with baseline comparison and key findings
- Export-ready matplotlib plots (base64 PNG) for IEEE paper figures
"""

from __future__ import annotations

import base64
import io
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.emotion import EmotionLog
from app.utils import find_project_root

logger = logging.getLogger(__name__)

# Baseline comparisons use this fraction of earliest / latest sessions
_BASELINE_FRACTION = 0.25
# Emotions considered high-risk for summary statistics
_HIGH_RISK_EMOTIONS = frozenset({"crisis", "fear", "anxiety"})
# Minimum sessions required to produce a meaningful research summary
_MIN_SESSIONS_FOR_SUMMARY = 4

# Plot styling constants (used across all generated figures)
_PLOT_LINE_WIDTH = 1.5
_PLOT_MARKER_SIZE = 4
_COLOR_PRIMARY = "#4C72B0"    # blue — bar charts and primary lines
_COLOR_POSITIVE = "#55A868"   # green — confidence trend
_COLOR_RISK = "#C44E52"       # red — risk scores and alerts
_COLOR_MEAN_LINE = "#888888"  # grey — mean reference lines


# --------------------------------------------------------------------------- #
# Core analytics
# --------------------------------------------------------------------------- #

def compute_emotion_distribution(logs: list[EmotionLog]) -> list[dict[str, Any]]:
    """Return emotion counts and percentages, sorted by frequency descending."""
    total = len(logs)
    if total == 0:
        return []
    counts = Counter(log.primary_emotion for log in logs)
    return [
        {
            "emotion": emotion,
            "count": count,
            "percentage": round(count / total * 100, 2),
        }
        for emotion, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
    ]


def compute_average_confidence(logs: list[EmotionLog]) -> float:
    """Return mean confidence over all logs, rounded to 4 dp."""
    if not logs:
        return 0.0
    return round(sum(log.confidence for log in logs) / len(logs), 4)


def compute_average_personalization_score(logs: list[EmotionLog]) -> float:
    """Return mean personalization_score over all logs, rounded to 4 dp."""
    if not logs:
        return 0.0
    return round(sum(log.personalization_score for log in logs) / len(logs), 4)


def compute_risk_trend(logs: list[EmotionLog]) -> list[dict[str, Any]]:
    """Return daily average risk_score, ordered chronologically."""
    if not logs:
        return []

    daily: dict[str, list[float]] = {}
    for log in logs:
        day = (
            log.created_at.strftime("%Y-%m-%d")
            if log.created_at
            else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )
        daily.setdefault(day, []).append(log.risk_score)

    return [
        {"date": day, "avg_risk_score": round(sum(scores) / len(scores), 4)}
        for day, scores in sorted(daily.items())
    ]


# --------------------------------------------------------------------------- #
# Research summary
# --------------------------------------------------------------------------- #

def generate_research_summary(logs: list[EmotionLog]) -> dict[str, Any]:
    """Auto-generate key findings, improvement percentages, and insights.

    Compares the earliest ``_BASELINE_FRACTION`` sessions (baseline) with the
    most recent ``_BASELINE_FRACTION`` sessions (current) to calculate
    improvements.  Falls back gracefully when there are too few sessions.
    """
    n = len(logs)
    total_sessions = n

    if n < _MIN_SESSIONS_FOR_SUMMARY:
        return {
            "total_sessions": total_sessions,
            "key_findings": ["Insufficient data — collect more sessions for a full summary."],
            "improvement_percentage": None,
            "risk_detection_improvement": None,
            "confidence_improvement": None,
            "insights": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # Split into baseline and current windows
    window = max(1, int(n * _BASELINE_FRACTION))
    baseline_logs = logs[:window]
    current_logs = logs[-window:]

    # Average metrics per window
    baseline_risk = sum(l.risk_score for l in baseline_logs) / len(baseline_logs)
    current_risk = sum(l.risk_score for l in current_logs) / len(current_logs)
    baseline_conf = sum(l.confidence for l in baseline_logs) / len(baseline_logs)
    current_conf = sum(l.confidence for l in current_logs) / len(current_logs)
    baseline_pers = sum(l.personalization_score for l in baseline_logs) / len(baseline_logs)
    current_pers = sum(l.personalization_score for l in current_logs) / len(current_logs)

    # Risk detection improvement (lower risk in current = system working better)
    if baseline_risk > 0:
        risk_improvement_pct = round((baseline_risk - current_risk) / baseline_risk * 100, 1)
    else:
        risk_improvement_pct = 0.0

    # Confidence improvement
    if baseline_conf > 0:
        conf_improvement_pct = round((current_conf - baseline_conf) / baseline_conf * 100, 1)
    else:
        conf_improvement_pct = 0.0

    # Personalization improvement
    if baseline_pers > 0:
        pers_improvement_pct = round((current_pers - baseline_pers) / baseline_pers * 100, 1)
    else:
        pers_improvement_pct = 0.0

    # High-risk session rate
    high_risk_count = sum(1 for l in logs if l.is_high_risk)
    high_risk_rate = round(high_risk_count / n * 100, 1)

    # Build human-readable key findings
    key_findings: list[str] = []

    if risk_improvement_pct > 0:
        key_findings.append(
            f"The proposed system improved risk detection by {abs(risk_improvement_pct):.1f}% "
            "compared to baseline."
        )
    elif risk_improvement_pct < 0:
        key_findings.append(
            f"Risk scores increased by {abs(risk_improvement_pct):.1f}% relative to baseline, "
            "indicating escalating distress trends."
        )
    else:
        key_findings.append("Risk scores remained stable compared to baseline.")

    if conf_improvement_pct > 0:
        key_findings.append(
            f"Prediction confidence improved by {abs(conf_improvement_pct):.1f}% over the "
            "observation period."
        )
    elif conf_improvement_pct < 0:
        key_findings.append(
            f"Prediction confidence decreased by {abs(conf_improvement_pct):.1f}%, suggesting "
            "higher input diversity."
        )

    if pers_improvement_pct > 0:
        key_findings.append(
            f"Personalization score increased by {abs(pers_improvement_pct):.1f}%, reflecting "
            "improved user-specific calibration."
        )

    key_findings.append(
        f"High-risk emotion sessions accounted for {high_risk_rate:.1f}% of all sessions "
        f"across {total_sessions} total interactions."
    )

    # Insights
    emotion_counter = Counter(l.primary_emotion for l in logs)
    dominant_emotion, dominant_count = emotion_counter.most_common(1)[0]
    insights: list[str] = [
        f"The most frequently detected emotion was '{dominant_emotion}' "
        f"({round(dominant_count / n * 100, 1)}% of sessions).",
        f"Mean prediction confidence: {round(current_conf, 3):.3f} "
        f"(baseline: {round(baseline_conf, 3):.3f}).",
        f"Mean personalization score: {round(current_pers, 3):.3f} "
        f"(baseline: {round(baseline_pers, 3):.3f}).",
    ]

    return {
        "total_sessions": total_sessions,
        "key_findings": key_findings,
        "improvement_percentage": risk_improvement_pct,
        "risk_detection_improvement": risk_improvement_pct,
        "confidence_improvement": conf_improvement_pct,
        "personalization_improvement": pers_improvement_pct,
        "insights": insights,
        "baseline_avg_risk": round(baseline_risk, 4),
        "current_avg_risk": round(current_risk, 4),
        "baseline_avg_confidence": round(baseline_conf, 4),
        "current_avg_confidence": round(current_conf, 4),
        "high_risk_session_rate_pct": high_risk_rate,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def save_research_summary(summary: dict[str, Any]) -> Path:
    """Persist research summary as JSON to the results/ directory."""
    results_dir = find_project_root() / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "research_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return output_path


# --------------------------------------------------------------------------- #
# Plot generation
# --------------------------------------------------------------------------- #

def _try_import_matplotlib():
    """Return pyplot module or None when matplotlib is not installed."""
    try:
        import matplotlib  # noqa: PLC0415
        matplotlib.use("Agg")  # non-interactive backend
        import matplotlib.pyplot as plt  # noqa: PLC0415
        return plt
    except ImportError:
        logger.warning("matplotlib not available — plots will be skipped")
        return None


def generate_plots(logs: list[EmotionLog]) -> dict[str, str | None]:
    """Return a dict of {plot_name: base64_png_string | None}.

    Generates three plots:
    - ``emotion_distribution``: horizontal bar chart of emotion counts
    - ``confidence_trend``: line chart of confidence over sessions
    - ``risk_progression``: line chart of risk_score over sessions
    """
    plt = _try_import_matplotlib()
    if plt is None or not logs:
        return {
            "emotion_distribution": None,
            "confidence_trend": None,
            "risk_progression": None,
        }

    try:
        import matplotlib.ticker as ticker  # noqa: PLC0415

        plots: dict[str, str | None] = {}

        # ── 1. Emotion distribution ─────────────────────────────────────── #
        counts = Counter(log.primary_emotion for log in logs)
        emotions = list(counts.keys())
        values = list(counts.values())
        # Sort by count ascending so largest bar appears at top
        pairs = sorted(zip(emotions, values), key=lambda x: x[1])
        emotions_sorted, values_sorted = zip(*pairs) if pairs else ([], [])

        fig, ax = plt.subplots(figsize=(8, max(3, len(emotions_sorted) * 0.6)))
        bars = ax.barh(emotions_sorted, values_sorted, color=_COLOR_PRIMARY, edgecolor="white")
        ax.set_xlabel("Session Count")
        ax.set_title("Emotion Distribution", fontsize=13, fontweight="bold")
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.bar_label(bars, padding=3, fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        plots["emotion_distribution"] = _fig_to_b64(fig, plt)

        # ── 2. Confidence trend ─────────────────────────────────────────── #
        session_indices = list(range(1, len(logs) + 1))
        confidences = [log.confidence for log in logs]

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(session_indices, confidences, marker="o",
                linewidth=_PLOT_LINE_WIDTH, markersize=_PLOT_MARKER_SIZE,
                color=_COLOR_POSITIVE, label="Confidence")
        ax.axhline(
            sum(confidences) / len(confidences),
            linestyle="--", color=_COLOR_MEAN_LINE, linewidth=1, label="Mean"
        )
        ax.set_xlabel("Session")
        ax.set_ylabel("Confidence")
        ax.set_title("Prediction Confidence Trend", fontsize=13, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        plots["confidence_trend"] = _fig_to_b64(fig, plt)

        # ── 3. Risk progression ─────────────────────────────────────────── #
        risk_scores = [log.risk_score for log in logs]

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(session_indices, risk_scores, marker="s",
                linewidth=_PLOT_LINE_WIDTH, markersize=_PLOT_MARKER_SIZE,
                color=_COLOR_RISK, label="Risk Score")
        ax.fill_between(session_indices, risk_scores, alpha=0.15, color=_COLOR_RISK)
        ax.axhline(
            sum(risk_scores) / len(risk_scores),
            linestyle="--", color=_COLOR_MEAN_LINE, linewidth=1, label="Mean"
        )
        ax.set_xlabel("Session")
        ax.set_ylabel("Risk Score")
        ax.set_title("Risk Score Progression", fontsize=13, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        plots["risk_progression"] = _fig_to_b64(fig, plt)

        return plots

    except Exception:
        logger.exception("Plot generation failed")
        return {
            "emotion_distribution": None,
            "confidence_trend": None,
            "risk_progression": None,
        }


def _fig_to_b64(fig: Any, plt: Any) -> str:
    """Render a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
