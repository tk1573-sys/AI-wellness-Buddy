"""
Modular AI agent pipeline for the AI Emotional Wellness Buddy.

Pipeline stages:
1) Emotion analysis agent
2) Pattern tracking agent
3) Forecasting agent
4) Alert decision agent
5) Response generation agent
6) Intervention decision agent
7) Clinical indicators (computed post-pipeline for research output)
"""

from emotion_analyzer import EmotionAnalyzer
from pattern_tracker import PatternTracker
from prediction_agent import PredictionAgent, compare_models
from alert_system import AlertSystem
from conversation_handler import ConversationHandler
from clinical_indicators import (
    compute_clinical_indicators,
    compute_emotional_risk,
    compute_cdi,
    detect_escalation,
    DISCLAIMER as CLINICAL_DISCLAIMER,
)
from intervention_engine import InterventionEngine
from emotion_analytics import EmotionAnalyticsLogger


class EmotionAnalysisAgent:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer or EmotionAnalyzer()

    def run(self, user_message):
        return self.analyzer.classify_emotion_ml(user_message)


class PatternTrackingAgent:
    def __init__(self, tracker=None):
        self.tracker = tracker or PatternTracker()

    def run(self, emotion_data):
        self.tracker.add_emotion_data(emotion_data)
        return self.tracker.get_pattern_summary()


class ForecastingAgent:
    def __init__(self, predictor=None, research_mode=False):
        self.predictor = predictor or PredictionAgent()
        self.research_mode = research_mode

    def run(self, sentiment_history):
        if not sentiment_history:
            return None
        forecast = self.predictor.predict_next_sentiment(sentiment_history)
        model_comparison = (
            compare_models(sentiment_history, research_mode=self.research_mode)
            if len(sentiment_history) >= 5 else None
        )
        return {
            'forecast': forecast,
            'model_comparison': model_comparison,
        }


class AlertDecisionAgent:
    def __init__(self, alert_system=None):
        self.alert_system = alert_system or AlertSystem()

    def run(self, pattern_summary, user_profile=None):
        if pattern_summary and self.alert_system.should_trigger_alert(pattern_summary):
            return self.alert_system.trigger_distress_alert(pattern_summary, user_profile=user_profile)
        return None


class ResponseGenerationAgent:
    def __init__(self, conversation_handler=None):
        self.conversation_handler = conversation_handler or ConversationHandler()

    def run(self, user_message, emotion_data, context=None):
        self.conversation_handler.add_message(user_message, emotion_data)
        return self.conversation_handler.generate_response(emotion_data, user_context=context)


class InterventionAgent:
    """Decide which coping interventions to recommend."""

    def __init__(self, engine=None):
        self.engine = engine or InterventionEngine()

    def run(self, risk_level, primary_emotion, clinical_indicators=None):
        return self.engine.recommend(risk_level, primary_emotion, clinical_indicators)


class WellnessAgentPipeline:
    """
    Orchestrates the full multi-agent processing pipeline.

    ``process_turn()`` returns a research-ready structured dict that
    includes emotion data, pattern summary, forecasting, alerts,
    clinical indicators, emotional risk index, CDI, escalation, and
    the response.  When a ``user_profile`` is supplied, personal triggers
    and demographic context are wired into response generation so that the
    personalization engine influences the output.
    """

    def __init__(self, analytics_logger: EmotionAnalyticsLogger | None = None):
        self.emotion_agent = EmotionAnalysisAgent()
        self.pattern_agent = PatternTrackingAgent()
        self.forecast_agent = ForecastingAgent()
        self.alert_agent = AlertDecisionAgent()
        self.response_agent = ResponseGenerationAgent()
        self.intervention_agent = InterventionAgent()
        self.analytics_logger = analytics_logger or EmotionAnalyticsLogger()

    def process_turn(self, user_message, user_profile=None, context=None):
        # ── Determine pipeline mode for research logging ──────────────────
        mode = "personalized" if user_profile is not None else "baseline"

        # ── Build user context by merging profile context with caller context ─
        # When a user_profile is provided we extract personal_triggers and
        # demographic fields so that ConversationHandler can personalise its
        # response.  The caller-supplied ``context`` (chat history list) is
        # preserved under the 'context' key.
        if user_profile is not None:
            profile_ctx = user_profile.get_personal_context()
            merged_context: dict = dict(profile_ctx)
            merged_context["response_style"] = user_profile.get_response_style()
            merged_context["user_name"] = user_profile.get_display_name()
            if context is not None:
                merged_context["context"] = context
        else:
            # Always use a dict so ConversationHandler receives a consistent type.
            # Wrap a chat-history list under the 'context' key if provided.
            if isinstance(context, list):
                merged_context = {"context": context}
            elif isinstance(context, dict):
                merged_context = dict(context)
            else:
                merged_context = {}

        emotion_data = self.emotion_agent.run(user_message)
        pattern_summary = self.pattern_agent.run(emotion_data)
        sentiment_history = list(self.pattern_agent.tracker.sentiment_history)
        forecasting = self.forecast_agent.run(sentiment_history)
        alert = self.alert_agent.run(pattern_summary, user_profile=user_profile)
        response = self.response_agent.run(user_message, emotion_data, context=merged_context)

        # Clinical indicators + weighted emotional risk index
        emotion_history = list(self.pattern_agent.tracker.emotion_history)
        clinical = compute_clinical_indicators(emotion_history)
        emotional_risk = compute_emotional_risk(
            emotion_data, clinical, pattern_summary,
        )

        # Clinical Distress Index (CDI)
        cdi = compute_cdi(emotion_data, clinical, pattern_summary)

        # Escalation detection
        escalation = detect_escalation(emotion_history)

        # Intervention recommendation
        interventions = self.intervention_agent.run(
            emotional_risk['risk_level'],
            emotion_data.get('primary_emotion', 'neutral'),
            clinical,
        )

        # ── Research evaluation logging ───────────────────────────────────
        user_id = getattr(user_profile, 'user_id', None) if user_profile else None
        self.analytics_logger.log_interaction(
            user_message=user_message,
            emotion_data=emotion_data,
            cdi=cdi,
            escalation=escalation,
            response=response if isinstance(response, str) else "",
            mode=mode,
            user_id=user_id,
        )

        return {
            'emotion': emotion_data,
            'concern_level': emotion_data.get('concern_level', 'low'),
            'clinical_indicators': clinical,
            'risk_score': emotional_risk['risk_score'],
            'risk_level': emotional_risk['risk_level'],
            'cdi': cdi,
            'escalation': escalation,
            'interventions': interventions,
            'patterns': pattern_summary,
            'forecasting': forecasting,
            'alert': alert,
            'response': response,
            'disclaimer': CLINICAL_DISCLAIMER,
        }
