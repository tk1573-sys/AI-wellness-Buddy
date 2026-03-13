from emotion_analyzer import EmotionAnalyzer
from prediction_agent import SimpleGRUForecaster, compare_models
from pattern_tracker import PatternTracker
from research_evaluation import evaluate_classifier
from agent_pipeline import WellnessAgentPipeline


def test_emotion_probabilities_and_contextual_fields_present():
    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel very anxious and scared today")
    assert 'emotion_probabilities' in result
    assert 'crisis_probability' in result
    assert 'suicidal_ideation_probability' in result
    assert abs(sum(result['emotion_probabilities'].values()) - 1.0) < 1e-3 or result['is_crisis']


def test_simple_gru_forecaster_and_model_comparison():
    history = [0.4, 0.3, 0.25, 0.1, 0.0, -0.1, -0.2, -0.25, -0.3]
    model = SimpleGRUForecaster(lookback=3, epochs=80)
    pred = model.predict_next(history)
    assert pred is not None
    assert -1.0 <= pred <= 1.0

    comparison = compare_models(history, research_mode=True)
    assert comparison is not None
    assert 'neural' in comparison


def test_advanced_pattern_metrics_are_reported():
    tracker = PatternTracker(window_size=10)
    for polarity in [0.2, -0.1, -0.4, -0.5, -0.2, 0.0]:
        tracker.add_emotion_data({
            'emotion': 'negative' if polarity < -0.1 else 'neutral',
            'severity': 'medium' if polarity < -0.1 else 'low',
            'polarity': polarity,
            'primary_emotion': 'sadness' if polarity < -0.1 else 'neutral',
            'is_crisis': False,
            'has_abuse_indicators': False,
        })
    summary = tracker.get_pattern_summary()
    assert 'emotional_volatility_index' in summary
    assert 'emotional_recovery_rate' in summary
    assert 'stress_persistence_score' in summary
    assert 'behavioral_drift_score' in summary


def test_research_evaluation_metrics():
    samples = [
        ("I am happy today", "joy"),
        ("I feel very sad", "sadness"),
        ("I am angry", "anger"),
        ("I am worried", "anxiety"),
    ]

    def classifier_fn(text):
        analyzer = EmotionAnalyzer()
        return analyzer.classify_emotion(text)['primary_emotion']

    report = evaluate_classifier(samples, classifier_fn)
    assert report['samples'] == 4
    assert 'macro_f1' in report
    assert 'per_class' in report


def test_agent_pipeline_process_turn():
    pipeline = WellnessAgentPipeline()
    result = pipeline.process_turn("I feel overwhelmed and lonely")
    assert 'emotion' in result
    assert 'patterns' in result
    assert 'forecasting' in result
    assert 'alert' in result
    assert 'response' in result
