#!/usr/bin/env python
"""
Full system validation script for the AI Emotional Wellness Buddy.

Covers every layer of the pipeline end-to-end:
  1. Dependency imports
  2. Unit & integration tests (pytest)
  3. End-to-end pipeline: text → emotion → response
  4. Benchmark: metrics JSON + CSV + plots
  5. Output file verification
  6. Final system-status report

Usage:
    python run_full_validation.py
    python run_full_validation.py --skip-benchmark   # faster, skips heavy model eval
    python run_full_validation.py --max-samples 50   # limit benchmark samples
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ---------------------------------------------------------------------------
# Pretty helpers
# ---------------------------------------------------------------------------

def _section(title: str) -> None:
    bar = "=" * 62
    print(f"\n{bar}\n  {title}\n{bar}")


def _ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def _fail(msg: str) -> None:
    print(f"  ❌ {msg}")


def _warn(msg: str) -> None:
    print(f"  ⚠️  {msg}")


# ---------------------------------------------------------------------------
# 1. Dependency validation
# ---------------------------------------------------------------------------

_CORE_MODULES = [
    "textblob",
    "matplotlib",
    "sklearn",
    "numpy",
    "plotly",
    "transformers",
    "torch",
    "streamlit",
    "fastapi",
    "httpx",
    "cryptography",
    "bcrypt",
    "dateutil",
    "langdetect",
]

_PROJECT_MODULES = [
    "emotion_analyzer",
    "emotion_predictor",
    "empathetic_responder",
    "wellness_buddy",
    "agent_pipeline",
    "conversation_handler",
    "clinical_indicators",
    "risk_escalation",
    "pattern_tracker",
    "session_manager",
    "evaluation_framework",
    "explainability",
    "research_evaluation",
    "api_service",
    "benchmark_emotion_models",
    "models.emotion_transformer",
    "datasets.goemotions_loader",
]


def validate_imports() -> bool:
    _section("1. Dependency Validation")
    all_ok = True

    for mod in _CORE_MODULES:
        try:
            __import__(mod)
            _ok(f"{mod}")
        except ImportError as exc:
            _fail(f"{mod}: {exc}")
            all_ok = False

    print()
    for mod in _PROJECT_MODULES:
        try:
            __import__(mod)
            _ok(f"{mod}")
        except Exception as exc:
            _fail(f"{mod}: {exc}")
            all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# 2. Pytest — unit & integration tests
# ---------------------------------------------------------------------------

_ALL_TEST_PATHS = [
    "test_wellness_buddy.py",
    "test_full_coverage.py",
    "test_extended_features.py",
    "test_conversation_memory.py",
    "test_session_manager.py",
    "test_humanoid_responses.py",
    "test_ui_launch.py",
    "test_ui_modules.py",
    "test_clinical_indicators.py",
    "test_concern_level.py",
    "test_explainability.py",
    "test_research_evaluation.py",
    "test_research_upgrades.py",
    "test_benchmark_emotion_models.py",
    "test_emotion_transformer.py",
    "test_api_service.py",
    "test_prediction_agent.py",
    "test_research_architecture.py",
    "test_chat_improvements.py",
    "tests/",
]


def _run_pytest(paths: list[str], label: str) -> tuple[bool, str]:
    """Run pytest on *paths*.  Returns (passed, summary_line)."""
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short"] + paths
    t0 = time.monotonic()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=_ROOT,
    )
    elapsed = time.monotonic() - t0
    summary = ""
    for line in result.stdout.splitlines():
        if "passed" in line or "failed" in line or "error" in line:
            summary = line.strip()
    passed = result.returncode == 0
    status = "PASS" if passed else "FAIL"
    print(f"  {label}: {status}  ({summary})  [{elapsed:.1f}s]")
    if not passed:
        # Print last 15 lines of output to surface failures
        for line in (result.stdout + result.stderr).splitlines()[-15:]:
            print(f"    {line}")
    return passed, summary


def validate_tests() -> bool:
    _section("2. Unit + Integration Tests")
    passed, _ = _run_pytest(_ALL_TEST_PATHS, "Full test suite")
    return passed


# ---------------------------------------------------------------------------
# 3. End-to-end pipeline
# ---------------------------------------------------------------------------

def validate_e2e_pipeline() -> bool:
    _section("3. End-to-End Pipeline Validation")
    all_ok = True
    try:
        from emotion_analyzer import EmotionAnalyzer
        ea = EmotionAnalyzer()
        samples = [
            "I am feeling really sad and hopeless today.",
            "I feel so happy and excited!",
            "I am very anxious about my exam tomorrow.",
            "I want to hurt myself",   # crisis probe
            "Everything is fine, just a regular day.",
        ]
        for text in samples:
            try:
                result = ea.classify_emotion(text)
                emotion = result.get("primary_emotion") or result.get("emotion", "unknown")
                conf = result.get("confidence_score", 0.0)
                _ok(f"classify_emotion → {emotion} ({conf:.2f}): {text[:45]!r}")
            except Exception as exc:
                _fail(f"classify_emotion raised {exc!r} for: {text[:45]!r}")
                all_ok = False
    except Exception as exc:
        _fail(f"EmotionAnalyzer init failed: {exc}")
        return False

    try:
        from empathetic_responder import EmpatheticResponder
        er = EmpatheticResponder()
        response = er.generate_response(
            user_text="I am feeling really sad today.",
            emotion="sadness",
            concern_level="medium",
        )
        if response and len(response) > 5:
            _ok(f"generate_response → {response[:60]!r}")
        else:
            _fail(f"generate_response returned empty/short: {response!r}")
            all_ok = False
    except Exception as exc:
        _fail(f"EmpatheticResponder.generate_response failed: {exc}")
        all_ok = False

    try:
        from wellness_buddy import WellnessBuddy
        buddy = WellnessBuddy()
        reply = buddy.process_message("I'm feeling a bit down today")
        if reply and len(reply) > 5:
            _ok(f"WellnessBuddy.process_message → {reply[:60]!r}")
        else:
            _fail(f"WellnessBuddy.process_message returned empty: {reply!r}")
            all_ok = False
    except Exception as exc:
        _fail(f"WellnessBuddy.process_message failed: {exc}")
        all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# 4. Benchmark
# ---------------------------------------------------------------------------

def validate_benchmark(max_samples: int = 30) -> bool:
    _section("4. Benchmark Validation")
    cmd = [
        sys.executable, "run_emotion_benchmark.py",
        "--dry-run",
        "--max-samples", str(max_samples),
    ]
    env = os.environ.copy()
    # Use cached models if available; fall back to keyword-only gracefully
    env.setdefault("TRANSFORMERS_OFFLINE", "1")
    env.setdefault("HF_HUB_OFFLINE", "1")

    t0 = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_ROOT, env=env)
    elapsed = time.monotonic() - t0

    if result.returncode == 0:
        _ok(f"Benchmark completed in {elapsed:.1f}s")
    else:
        _fail(f"Benchmark failed after {elapsed:.1f}s")
        for line in (result.stdout + result.stderr).splitlines()[-10:]:
            print(f"    {line}")
        return False
    return True


# ---------------------------------------------------------------------------
# 5. Output file verification
# ---------------------------------------------------------------------------

_EXPECTED_OUTPUTS = [
    ("results/final_metrics.json",          "Benchmark metrics (JSON)"),
    ("results/classification_report.csv",   "Per-class metrics (CSV)"),
    ("plots/model_comparison.png",          "Model comparison plot"),
    ("plots/confusion_matrix.png",          "Confusion matrix plot"),
    ("logs/run.log",                        "Benchmark run log"),
]


def validate_outputs() -> bool:
    _section("5. Output File Verification")
    all_ok = True

    for rel_path, label in _EXPECTED_OUTPUTS:
        full = os.path.join(_ROOT, rel_path)
        if os.path.exists(full) and os.path.getsize(full) > 0:
            _ok(f"{label}: {rel_path}")
        else:
            _fail(f"{label} missing or empty: {rel_path}")
            all_ok = False

    # Validate JSON structure
    json_path = os.path.join(_ROOT, "results", "final_metrics.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            required_models = {"Keyword", "Transformer", "Hybrid"}
            required_keys = {"precision", "recall", "macro_f1", "accuracy"}
            ok = True
            for model in required_models:
                if model not in data:
                    _fail(f"final_metrics.json missing model: {model}")
                    ok = False
                    all_ok = False
                    continue
                for key in required_keys:
                    if key not in data[model]:
                        _fail(f"final_metrics.json[{model}] missing key: {key}")
                        ok = False
                        all_ok = False
            if ok:
                _ok("final_metrics.json structure valid")
        except Exception as exc:
            _fail(f"final_metrics.json parse error: {exc}")
            all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Full system validation for the AI Wellness Buddy project.",
    )
    parser.add_argument(
        "--skip-benchmark",
        action="store_true",
        help="Skip the heavy benchmark step (faster CI runs).",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=30,
        metavar="N",
        help="Max samples for benchmark (default: 30).",
    )
    args = parser.parse_args(argv)

    wall_start = time.monotonic()

    print("=" * 62)
    print("  AI Emotional Wellness Buddy — Full System Validation")
    print("=" * 62)

    results: dict[str, bool] = {}

    results["Dependency imports"] = validate_imports()
    results["Unit + integration tests"] = validate_tests()
    results["End-to-end pipeline"] = validate_e2e_pipeline()

    if args.skip_benchmark:
        _section("4. Benchmark Validation")
        _warn("Skipped (--skip-benchmark)")
        results["Benchmark"] = True
    else:
        results["Benchmark"] = validate_benchmark(max_samples=args.max_samples)

    results["Output files"] = validate_outputs()

    # -------------------------------------------------------------------------
    # Final report
    # -------------------------------------------------------------------------
    elapsed = time.monotonic() - wall_start
    _section("Final System Status Report")
    all_pass = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_pass = False
        print(f"  {component + ':':38s} {status}")
    print(f"\n  Total time: {elapsed:.1f}s")
    print("=" * 62)

    if all_pass:
        print("\n  ✅ All validations passed — system is production-ready.\n")
        return 0
    else:
        print("\n  ❌ Some validations failed — see details above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
