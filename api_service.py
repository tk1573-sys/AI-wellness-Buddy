"""
Optional FastAPI service wrapper for mobile/cloud integrations.
"""

from wellness_buddy import WellnessBuddy
from agent_pipeline import WellnessAgentPipeline

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except Exception:  # pragma: no cover - optional dependency
    FastAPI = None
    BaseModel = object


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    primary_emotion: str
    risk_level: str


def create_app():
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install with: pip install fastapi uvicorn")

    app = FastAPI(title='AI Emotional Wellness Buddy API', version='2.0.0-research.1')
    pipeline = WellnessAgentPipeline()
    buddy = WellnessBuddy()

    @app.get('/health')
    def health():
        return {'status': 'ok', 'service': 'ai-wellness-buddy'}

    @app.post('/v1/chat', response_model=ChatResponse)
    def chat(req: ChatRequest):
        # Lightweight stateless API turn using the modular pipeline.
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
