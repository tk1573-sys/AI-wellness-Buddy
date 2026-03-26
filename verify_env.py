#!/usr/bin/env python3
"""Verify that all required libraries for AI Wellness Buddy are installed.

Run this after setting up the environment to confirm readiness:

    python verify_env.py

Exit code 0 → all packages present.
Exit code 1 → one or more packages are missing (printed to stderr).
"""
from __future__ import annotations

import importlib
import sys

# Mapping: import_name → pip install name (as listed in requirements.txt)
_REQUIRED: list[tuple[str, str]] = [
    ("textblob",      "textblob==0.17.1"),
    ("dateutil",      "python-dateutil==2.8.2"),
    ("streamlit",     "streamlit==1.28.0"),
    ("cryptography",  "cryptography==46.0.5"),
    ("gtts",          "gTTS==2.5.4"),
    ("speech_recognition", "SpeechRecognition==3.14.5"),
    ("langdetect",    "langdetect==1.0.9"),
    ("plotly",        "plotly==5.18.0"),
    ("matplotlib",    "matplotlib==3.7.0"),
    ("seaborn",       "seaborn==0.12.2"),
    ("sklearn",       "scikit-learn==1.3.2"),
    ("numpy",         "numpy==1.26.2"),
    ("transformers",  "transformers==4.48.0"),
    ("torch",         "torch==2.6.0"),
    ("bcrypt",        "bcrypt==3.2.2"),
]


def _check() -> list[str]:
    """Return a list of pip install specs for any missing package."""
    missing: list[str] = []
    for import_name, pip_spec in _REQUIRED:
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pip_spec)
    return missing


def main() -> int:
    missing = _check()
    if missing:
        print(
            "ERROR: The following required packages are missing:\n",
            file=sys.stderr,
        )
        for spec in missing:
            print(f"  - {spec}", file=sys.stderr)
        print(
            "\nInstall them with:\n"
            f"  pip install {' '.join(missing)}\n"
            "Or install everything at once:\n"
            "  pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    print("✅  All required packages are installed. Environment is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
