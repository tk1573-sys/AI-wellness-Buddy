"""Root-level pytest configuration.

Sets HuggingFace offline flags so that tests never attempt to contact the
Hub API.  The cached model weights are always used, which avoids rate-limit
errors (HTTP 429) and keeps test runs reproducible in CI/CD environments
that do not have internet access.
"""
import os

# Prevent transformers / huggingface_hub from querying the Hub during tests.
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
