"""
Modular AI agent pipeline for the AI Emotional Wellness Buddy.

Pipeline stages:
1) Emotion analysis agent
2) Pattern tracking agent
3) Forecasting agent
4) Alert decision agent
5) Response generation agent
"""

from emotion_analyzer import EmotionAnalyzer
from pattern_tracker import PatternTracker
from prediction_agent import PredictionAgent, compare_models
from alert_system import AlertSystem
from conversation_handler import ConversationHandler


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


class WellnessAgentPipeline:
    """
    Orchestrates the full multi-agent processing pipeline.
    """

    def __init__(self):
        self.emotion_agent = EmotionAnalysisAgent()
        self.pattern_agent = PatternTrackingAgent()
        self.forecast_agent = ForecastingAgent()
        self.alert_agent = AlertDecisionAgent()
        self.response_agent = ResponseGenerationAgent()

    def process_turn(self, user_message, user_profile=None, context=None):
        emotion_data = self.emotion_agent.run(user_message)
        pattern_summary = self.pattern_agent.run(emotion_data)
        sentiment_history = list(self.pattern_agent.tracker.sentiment_history)
        forecasting = self.forecast_agent.run(sentiment_history)
        alert = self.alert_agent.run(pattern_summary, user_profile=user_profile)
        response = self.response_agent.run(user_message, emotion_data, context=context)
        return {
            'emotion': emotion_data,
            'patterns': pattern_summary,
            'forecasting': forecasting,
            'alert': alert,
            'response': response,
        }
