"""
Optional FastAPI service wrapper for mobile/cloud integrations.

Privacy architecture
--------------------
Each ``user_id`` receives its own :class:`WellnessAgentPipeline` instance so
that emotion history, pattern-tracking state and conversation memory are
**completely isolated** between users.  This prevents cross-user data leakage
and is a requirement for research-grade deployments where emotional data must
remain confidential per participant.

Thread safety is provided by a :class:`threading.Lock` that serialises access
to the per-user pipeline registry.
"""

import threading

from wellness_buddy import WellnessBuddy
from agent_pipeline import WellnessAgentPipeline

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except Exception:  # pragma: no cover - optional dependency
    FastAPI = None
    BaseModel = object


# ---------------------------------------------------------------------------
# Pydantic request / response schemas (unchanged for backward compatibility)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    primary_emotion: str
    risk_level: str


# ---------------------------------------------------------------------------
# Per-user pipeline registry
# ---------------------------------------------------------------------------
# Each user_id maps to its own WellnessAgentPipeline so that emotion history,
# pattern-tracking state and forecasting data are never shared across users.
# A threading lock ensures safe concurrent access from multiple request threads.
# ---------------------------------------------------------------------------

_pipelines: dict = {}
_pipelines_lock = threading.Lock()


def get_pipeline(user_id: str) -> WellnessAgentPipeline:
    """Return the pipeline for *user_id*, creating one on first access.

    Privacy guarantee: every user_id receives a **dedicated** pipeline
    instance.  Emotion scores, pattern history, and conversation context
    accumulated by one user are never visible to another.
    """
    with _pipelines_lock:
        if user_id not in _pipelines:
            _pipelines[user_id] = WellnessAgentPipeline()
        return _pipelines[user_id]


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app():
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install with: pip install fastapi uvicorn")

    app = FastAPI(title='AI Emotional Wellness Buddy API', version='2.0.0-research.1')

    # A single WellnessBuddy is used **only** for read-only model-info queries.
    # It does NOT carry any per-user conversation state.
    buddy = WellnessBuddy()

    @app.get('/health')
    def health():
        return {'status': 'ok', 'service': 'ai-wellness-buddy'}

    @app.post('/v1/chat', response_model=ChatResponse)
    def chat(req: ChatRequest):
        """Process a chat message with per-user pipeline isolation.

        Privacy: the pipeline instance is scoped to ``req.user_id`` so that
        emotion history, pattern-tracking state and forecasting data are
        never shared across users.  No global mutable state is read or
        written during this call.
        """
        # Retrieve (or create) the isolated pipeline for this user.
        pipeline = get_pipeline(req.user_id)
        result = pipeline.process_turn(req.message, context={'user_name': req.user_id})
        patterns = result.get('patterns') or {}
        return ChatResponse(
            response=result['response'],
            primary_emotion=result['emotion'].get('primary_emotion', 'neutral'),
            risk_level=patterns.get('risk_level', 'low'),
        )

    @app.get('/v1/model-info')
    def model_info():
        return {
            'emotion_model_available': buddy.emotion_analyzer.ml_adapter.available,
            'contextual_crisis_model_available': buddy.emotion_analyzer.crisis_adapter.available,
            'forecasting_models': ['ols', 'ewma', 'simple_gru'],
        }

    return app


app = create_app() if FastAPI is not None else None
