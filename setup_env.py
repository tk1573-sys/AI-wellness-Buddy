#!/usr/bin/env python3
"""Setup script for the AI Wellness Buddy project.

Installs all required dependencies from requirements.txt and downloads
the corpora needed by TextBlob and NLTK.

Usage:
    python setup_env.py
"""
from __future__ import annotations

import subprocess
import sys
import os


def install_requirements() -> None:
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print(f"Installing dependencies from {req_file} ...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", req_file]
    )
    print("Dependencies installed successfully.\n")


def download_corpora() -> None:
    print("Downloading TextBlob corpora ...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "textblob.download_corpora"]
        )
    except subprocess.CalledProcessError as exc:
        print(
            f"WARNING: TextBlob corpora download failed ({exc}). "
            "You can retry manually: python -m textblob.download_corpora"
        )

    print("\nDownloading NLTK data ...")
    try:
        import nltk  # noqa: PLC0415
        for resource in ("brown", "punkt", "punkt_tab", "averaged_perceptron_tagger"):
            nltk.download(resource, quiet=True)
        print("NLTK data downloaded successfully.\n")
    except ImportError:
        print(
            "WARNING: NLTK is not importable. Make sure 'pip install -r requirements.txt' "
            "completed successfully before running this script."
        )


def main() -> None:
    install_requirements()
    download_corpora()
    print("Setup complete. You can now run the project:")
    print("  streamlit run ui_app.py          # Web UI")
    print("  python wellness_buddy.py         # CLI")
    print("  python run_emotion_benchmark.py  # Benchmark")


if __name__ == "__main__":
    main()
