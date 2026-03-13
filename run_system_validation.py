#!/usr/bin/env python
"""
System validation script for the AI Emotional Wellness Buddy.

Runs all validation steps and prints a final summary report suitable for
inclusion in a research-grade reproducibility check.

Usage:
    python run_system_validation.py
"""

import importlib
import subprocess
import sys
import os

# Ensure project root is on the path
_PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def _run_pytest(paths: list[str], label: str) -> bool:
    """Run pytest on *paths* and return True on success."""
    cmd = [sys.executable, '-m', 'pytest', '-q', '--tb=short'] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_PROJECT_ROOT)
    if result.returncode == 0:
        # Count passed tests from the summary line (e.g. "12 passed")
        for line in result.stdout.splitlines():
            if 'passed' in line:
                print(f"  {label}: PASS  ({line.strip()})")
                return True
        print(f"  {label}: PASS")
        return True
    else:
        print(f"  {label}: FAIL")
        # Show last few lines of output for debugging
        for line in (result.stdout + result.stderr).splitlines()[-8:]:
            print(f"    {line}")
        return False


# ------------------------------------------------------------------
# Validation steps
# ------------------------------------------------------------------

def validate_model_loading() -> bool:
    """Check that core models instantiate."""
    _section("Model Loading")
    try:
        from models.emotion_transformer import EmotionTransformer
        et = EmotionTransformer()
        probs = et.classify("test input")
        assert isinstance(probs, dict) and len(probs) > 0
        print("  Emotion Transformer: PASS")
        return True
    except Exception as exc:
        print(f"  Emotion Transformer: FAIL ({exc})")
        return False


def validate_emotion_tests() -> bool:
    _section("Emotion Model Tests")
    return _run_pytest(['tests/test_emotion_model.py'], 'Emotion Model')


def validate_forecasting_tests() -> bool:
    _section("Forecasting Module Tests")
    return _run_pytest(['tests/test_forecasting.py'], 'Forecasting Module')


def validate_pipeline_tests() -> bool:
    _section("Pipeline Execution Tests")
    return _run_pytest(['tests/test_pipeline.py'], 'Pipeline Execution')


def validate_api_tests() -> bool:
    _section("API Service Tests")
    return _run_pytest(['tests/test_api.py'], 'API Service')


def validate_evaluation_tests() -> bool:
    _section("Evaluation Framework Tests")
    return _run_pytest(['tests/test_evaluation.py'], 'Evaluation Framework')


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("  AI Emotional Wellness Buddy — System Validation")
    print("=" * 60)

    results: dict[str, bool] = {}

    results['Model Loading'] = validate_model_loading()
    results['Emotion Model'] = validate_emotion_tests()
    results['Forecasting Module'] = validate_forecasting_tests()
    results['Pipeline Execution'] = validate_pipeline_tests()
    results['API Service'] = validate_api_tests()
    results['Evaluation Framework'] = validate_evaluation_tests()

    # ---- Summary ----
    print("\n")
    print("=" * 60)
    print("  System Validation Report")
    print("=" * 60)
    all_pass = True
    for component, passed in results.items():
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            all_pass = False
        print(f"  {component + ':':30s} {status}")
    print("=" * 60)

    if all_pass:
        print("\n  ✅ All validations passed.\n")
        return 0
    else:
        print("\n  ❌ Some validations failed — see details above.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
