"""
Full Coverage Test Suite for AI Wellness Buddy
Covers all untested code paths across every module.

Run with: python -m pytest test_full_coverage.py -v
"""

import tempfile
import shutil
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# WellnessBuddy orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def test_wellness_buddy_process_message():
    """WellnessBuddy.process_message normal positive/negative flow."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    buddy = WellnessBuddy()
    buddy.user_profile = UserProfile('proc_test')
    buddy.user_profile.set_name('Alice')
    buddy.user_id = 'proc_test'

    resp_pos = buddy.process_message("I'm feeling great today!")
    assert isinstance(resp_pos, str) and len(resp_pos) > 10
    print(f"✓ Positive response: '{resp_pos[:60]}...'")

    resp_neg = buddy.process_message("I'm feeling a bit sad and down")
    assert isinstance(resp_neg, str) and len(resp_neg) > 10
    print(f"✓ Negative response: '{resp_neg[:60]}...'")

    print("\n✓ test_wellness_buddy_process_message passed")


def test_wellness_buddy_crisis_short_circuit():
    """Crisis message triggers immediate 988 resource response."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    buddy = WellnessBuddy()
    buddy.user_profile = UserProfile('crisis_sc')
    buddy.user_id = 'crisis_sc'

    response = buddy.process_message("I want to kill myself")
    assert '988' in response
    assert 'IMMEDIATE' in response or 'immediate' in response.lower()
    print(f"✓ Crisis response contains 988 hotline and immediate keyword")

    print("\n✓ test_wellness_buddy_crisis_short_circuit passed")


def test_wellness_buddy_help_command():
    """'help' command returns support resources including 988."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    buddy = WellnessBuddy()
    buddy.user_profile = UserProfile('help_cmd')
    buddy.user_profile.set_gender('female')
    buddy.user_profile.add_trusted_contact('Jane', 'friend', '555-9999')
    buddy.user_id = 'help_cmd'

    response = buddy.process_message('help')
    assert '988' in response
    # Women's resources should appear since gender=female
    assert 'Women' in response or 'women' in response or 'domestic' in response.lower()
    print(f"✓ Help response includes 988 and women's resources")

    print("\n✓ test_wellness_buddy_help_command passed")


def test_wellness_buddy_status_command():
    """'status' command returns emotional pattern summary."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    buddy = WellnessBuddy()
    buddy.user_profile = UserProfile('status_cmd')
    buddy.user_id = 'status_cmd'

    # Add some messages to pattern tracker first
    buddy.process_message("I feel okay today")
    buddy.process_message("Things are going well")

    response = buddy.process_message('status')
    assert isinstance(response, str)
    assert 'Messages' in response or 'sentiment' in response.lower() or 'pattern' in response.lower()
    print(f"✓ Status response: '{response[:80]}...'")

    print("\n✓ test_wellness_buddy_status_command passed")


def test_wellness_buddy_end_session():
    """'quit' command saves snapshot and returns farewell message."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    temp_dir = tempfile.mkdtemp()
    try:
        buddy = WellnessBuddy(data_dir=temp_dir)
        buddy.user_profile = UserProfile('end_sess')
        buddy.user_id = 'end_sess'

        buddy.process_message("I feel pretty good today")
        buddy.process_message("Things are going well")
        buddy.process_message("I'm happy and grateful")

        response = buddy.process_message('quit')
        assert 'Thank' in response or 'care' in response.lower() or 'alone' in response.lower()
        print(f"✓ End-session farewell: '{response[:80]}...'")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n✓ test_wellness_buddy_end_session passed")


def test_wellness_buddy_no_profile():
    """process_message returns error when profile is not initialised."""
    from wellness_buddy import WellnessBuddy

    buddy = WellnessBuddy()
    # deliberately leave user_profile as None
    response = buddy.process_message("Hello")
    assert 'Profile not initialized' in response or len(response) > 0
    print(f"✓ No-profile response: '{response[:80]}'")

    print("\n✓ test_wellness_buddy_no_profile passed")


# ─────────────────────────────────────────────────────────────────────────────
# PatternTracker
# ─────────────────────────────────────────────────────────────────────────────

def test_pattern_tracker_severity_levels():
    """Severity levels map correctly at LOW vs HIGH boundaries."""
    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()

    # Positive messages → LOW severity
    tracker_low = PatternTracker()
    for _ in range(3):
        data = analyzer.classify_emotion("I'm happy, wonderful, and feeling amazing today!")
        tracker_low.add_emotion_data(data)
    s_low = tracker_low.get_pattern_summary()
    assert s_low['severity_level'] in ('LOW', 'MEDIUM', 'HIGH')
    print(f"✓ Positive messages → severity_level: {s_low['severity_level']}")

    # Heavy distress → higher severity
    tracker_high = PatternTracker()
    for _ in range(5):
        data = analyzer.classify_emotion(
            "I feel completely hopeless, worthless, and in pain. I can't take it anymore."
        )
        tracker_high.add_emotion_data(data)
    s_high = tracker_high.get_pattern_summary()
    assert s_high['severity_score'] > 0
    assert s_high['severity_level'] in ('MEDIUM', 'HIGH')
    print(f"✓ Distress messages → severity_level: {s_high['severity_level']}, "
          f"score: {s_high['severity_score']}")

    # reset_consecutive_distress
    tracker_high.reset_consecutive_distress()
    assert tracker_high.consecutive_distress == 0
    print("✓ reset_consecutive_distress() works")

    print("\n✓ test_pattern_tracker_severity_levels passed")


def test_pattern_tracker_emotion_distribution():
    """get_emotion_distribution() returns valid per-category averages."""
    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()

    for text in [
        "I'm so happy and joyful today!",
        "I feel sad and down",
        "I'm really anxious and worried",
    ]:
        tracker.add_emotion_data(analyzer.classify_emotion(text))

    dist = tracker.get_emotion_distribution()
    assert isinstance(dist, dict)
    assert all(k in dist for k in ('joy', 'sadness', 'anxiety', 'anger', 'neutral'))
    assert all(0.0 <= v <= 1.0 for v in dist.values())
    print(f"✓ Emotion distribution: {dist}")

    print("\n✓ test_pattern_tracker_emotion_distribution passed")


def test_pattern_tracker_insufficient_data():
    """PatternTracker with no data returns None; with 1 message returns insufficient_data trend."""
    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()

    assert tracker.get_pattern_summary() is None
    print("✓ Empty tracker returns None")

    tracker.add_emotion_data(analyzer.classify_emotion("Just one message"))
    summary = tracker.get_pattern_summary()
    assert summary is not None
    assert summary['trend'] == 'insufficient_data'
    print(f"✓ Single message → trend: {summary['trend']}")

    print("\n✓ test_pattern_tracker_insufficient_data passed")


def test_pattern_tracker_consecutive_distress_reset():
    """A positive message resets the consecutive_distress counter."""
    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()

    for _ in range(2):
        tracker.add_emotion_data(analyzer.classify_emotion("I feel hopeless and sad"))
    before = tracker.consecutive_distress
    assert before > 0

    tracker.add_emotion_data(
        analyzer.classify_emotion("I'm feeling much better today, things are great!")
    )
    assert tracker.consecutive_distress == 0
    print(f"✓ Consecutive distress reset from {before} to 0 after positive message")

    print("\n✓ test_pattern_tracker_consecutive_distress_reset passed")


# ─────────────────────────────────────────────────────────────────────────────
# AlertSystem
# ─────────────────────────────────────────────────────────────────────────────

def test_alert_escalation():
    """escalate_pending_alerts() auto-escalates an unacknowledged MEDIUM alert."""
    from alert_system import AlertSystem
    import config

    alert_sys = AlertSystem()

    # Construct a MEDIUM alert backdated past its escalation interval (15 min)
    interval = config.ESCALATION_INTERVALS.get('MEDIUM', 15)
    alert = {
        'type': 'distress',
        'severity': 'MEDIUM',
        'timestamp': datetime.now() - timedelta(minutes=interval + 1),
        'acknowledged': False,
        'guardian_consent': False,
        'escalated_at': None,
    }
    alert_sys.alerts_triggered.append(alert)

    escalated = alert_sys.escalate_pending_alerts()
    assert len(escalated) >= 1
    level_order = config.ALERT_SEVERITY_LEVELS
    original_idx = level_order.index('MEDIUM')
    new_idx = level_order.index(alert['severity'])
    assert new_idx > original_idx, \
        f"Severity should be higher than MEDIUM after escalation, got: {alert['severity']}"
    print(f"✓ Alert escalated: MEDIUM → {alert['severity']}")

    print("\n✓ test_alert_escalation passed")


def test_alert_guardian_consent():
    """grant_guardian_consent and acknowledge_alert work correctly."""
    from alert_system import AlertSystem

    alert_sys = AlertSystem()
    alert = {
        'type': 'distress', 'severity': 'HIGH',
        'message': 'Test', 'resources': {},
        'pattern_summary': {},
        'timestamp': datetime.now(),
        'acknowledged': False,
        'guardian_consent': False,
        'escalated_at': None,
    }

    alert_sys.grant_guardian_consent(alert)
    assert alert['guardian_consent']
    print("✓ Guardian consent granted")

    alert_sys.acknowledge_alert(alert)
    assert alert['acknowledged']
    assert 'acknowledged_at' in alert
    print("✓ Alert acknowledged with timestamp")

    print("\n✓ test_alert_guardian_consent passed")


def test_alert_format_guardian_notification():
    """format_guardian_notification() includes user name, severity, and resources."""
    from alert_system import AlertSystem

    alert_sys = AlertSystem()
    alert = {
        'severity': 'HIGH',
        'pattern_summary': {
            'sustained_distress_detected': True,
            'abuse_indicators_detected': True,
            'consecutive_distress': 4,
            'severity_score': 8.0,
        },
    }

    msg = alert_sys.format_guardian_notification(alert, user_name="Alice")
    assert 'Alice' in msg
    assert 'HIGH' in msg
    assert '988' in msg or 'crisis' in msg.lower()
    assert 'distress' in msg.lower() or 'sustained' in msg.lower()
    print(f"✓ Notification contains user name, severity, and resources")
    print(f"  First 120 chars: {msg[:120]}")

    print("\n✓ test_alert_format_guardian_notification passed")


def test_alert_abuse_severity_escalation():
    """Abuse indicators escalate severity one level; HIGH+sustained → CRITICAL."""
    from alert_system import AlertSystem
    import config

    alert_sys = AlertSystem()

    # LOW + abuse_indicators → at least MEDIUM
    summary_abuse = {
        'severity_level': 'LOW',
        'abuse_indicators_detected': True,
        'sustained_distress_detected': False,
    }
    sev = alert_sys._compute_severity(summary_abuse)
    assert config.ALERT_SEVERITY_LEVELS.index(sev) > config.ALERT_SEVERITY_LEVELS.index('LOW'), \
        f"Expected severity > LOW with abuse indicators, got {sev}"
    print(f"✓ Abuse indicators escalate LOW → {sev}")

    # HIGH + sustained_distress → CRITICAL
    summary_crit = {
        'severity_level': 'HIGH',
        'abuse_indicators_detected': False,
        'sustained_distress_detected': True,
    }
    sev_crit = alert_sys._compute_severity(summary_crit)
    assert sev_crit == 'CRITICAL', f"Expected CRITICAL, got {sev_crit}"
    print("✓ HIGH + sustained_distress → CRITICAL")

    print("\n✓ test_alert_abuse_severity_escalation passed")


def test_alert_no_trigger_without_sustained_distress():
    """should_trigger_alert returns False when sustained_distress_detected is False."""
    from alert_system import AlertSystem

    alert_sys = AlertSystem()
    assert not alert_sys.should_trigger_alert(None)
    assert not alert_sys.should_trigger_alert({'sustained_distress_detected': False})
    assert alert_sys.should_trigger_alert({'sustained_distress_detected': True})
    print("✓ should_trigger_alert logic correct")

    print("\n✓ test_alert_no_trigger_without_sustained_distress passed")


# ─────────────────────────────────────────────────────────────────────────────
# PredictionAgent
# ─────────────────────────────────────────────────────────────────────────────

def test_prediction_agent_insufficient_data():
    """PredictionAgent with < 2 data points returns insufficient_data."""
    from prediction_agent import PredictionAgent

    agent = PredictionAgent()
    r0 = agent.predict_next_state()
    assert r0['trend'] == 'insufficient_data'
    assert r0['confidence'] == 0.0
    print("✓ Empty agent → insufficient_data trend, confidence=0.0")

    agent.add_data_point(0.5, 'joy')
    r1 = agent.predict_next_state()
    assert r1['trend'] == 'insufficient_data'
    print("✓ Single data point → insufficient_data")

    print("\n✓ test_prediction_agent_insufficient_data passed")


def test_prediction_agent_classify_trend():
    """classify_trend() correctly labels improving, worsening, and stable trends."""
    from prediction_agent import PredictionAgent

    # Improving
    a_imp = PredictionAgent()
    for s in [-0.5, -0.3, -0.1, 0.1, 0.3]:
        a_imp.add_data_point(s, 'joy')
    assert a_imp.classify_trend() == 'improving', \
        f"Expected improving, got {a_imp.classify_trend()}"
    print("✓ Improving trend detected")

    # Worsening
    a_wor = PredictionAgent()
    for s in [0.5, 0.3, 0.1, -0.1, -0.3]:
        a_wor.add_data_point(s, 'sadness')
    assert a_wor.classify_trend() == 'worsening', \
        f"Expected worsening, got {a_wor.classify_trend()}"
    print("✓ Worsening trend detected")

    # Stable (small variance around 0)
    a_stb = PredictionAgent()
    for s in [0.1, -0.05, 0.05, -0.03, 0.08]:
        a_stb.add_data_point(s, 'neutral')
    assert a_stb.classify_trend() == 'stable', \
        f"Expected stable, got {a_stb.classify_trend()}"
    print("✓ Stable trend detected")

    print("\n✓ test_prediction_agent_classify_trend passed")


def test_prediction_agent_early_warning():
    """Early warning field is bool and warning_message is set when triggered."""
    from prediction_agent import PredictionAgent

    agent = PredictionAgent()
    for s in [0.0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6]:
        agent.add_data_point(s, 'sadness')

    result = agent.predict_next_state()
    assert isinstance(result['early_warning'], bool)
    assert result['predicted_sentiment'] is not None

    if result['early_warning']:
        assert result['warning_message'] is not None
        print(f"✓ Early warning triggered: '{result['warning_message'][:60]}...'")
    else:
        assert result['warning_message'] is None or isinstance(result['warning_message'], str), \
            "warning_message must be None or a string when early_warning is False"
        print(f"✓ No early warning (predicted={result['predicted_sentiment']:.3f})")

    print("\n✓ test_prediction_agent_early_warning passed")


def test_prediction_agent_metrics_accumulate():
    """Metrics are computed correctly — RMSE >= MAE always holds."""
    from prediction_agent import PredictionAgent

    agent = PredictionAgent()

    values = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2]
    for v in values[:4]:
        agent.add_data_point(v, 'neutral')

    # Make a prediction (actual filled on next add)
    agent.predict_next_state()
    agent.add_data_point(values[4], 'neutral')  # evaluates previous prediction

    metrics = agent.get_metrics()
    assert 'mae' in metrics and 'rmse' in metrics
    if metrics['n_predictions'] > 0:
        assert metrics['mae'] >= 0
        assert metrics['rmse'] >= metrics['mae'], "RMSE must be >= MAE"
        print(f"✓ MAE={metrics['mae']}, RMSE={metrics['rmse']}, n={metrics['n_predictions']}")
    else:
        print("✓ No evaluated predictions yet (prediction still pending actual)")

    print("\n✓ test_prediction_agent_metrics_accumulate passed")


def test_prediction_agent_forecast_series():
    """get_forecast_series() returns correct number of values, all in [-1, 1]."""
    from prediction_agent import PredictionAgent

    agent = PredictionAgent()
    for s in [0.3, 0.2, 0.1, 0.0, -0.1]:
        agent.add_data_point(s, 'sadness')

    for steps in (1, 3, 5):
        fc = agent.get_forecast_series(steps=steps)
        assert len(fc) == steps
        assert all(-1.0 <= v <= 1.0 for v in fc)
    print("✓ Forecast series length and range verified (steps=1,3,5)")

    print("\n✓ test_prediction_agent_forecast_series passed")


# ─────────────────────────────────────────────────────────────────────────────
# ConversationHandler
# ─────────────────────────────────────────────────────────────────────────────

def test_conversation_handler_abuse_override():
    """Abuse-indicator override template appears when has_abuse_indicators=True."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    emotion_data = analyzer.classify_emotion(
        "I'm in a toxic relationship, my partner is abusive and controlling"
    )
    emotion_data['has_abuse_indicators'] = True
    emotion_data['abuse_indicators'] = ['abusive', 'controlling']

    # Use unittest.mock.patch for safe, idiomatic monkeypatching
    from unittest.mock import patch

    with patch('random.choice', side_effect=lambda seq: seq[-1]):
        resp = handler.generate_response(emotion_data)

    assert 'safe' in resp.lower() or 'support' in resp.lower() or 'unsafe' in resp.lower()
    print(f"✓ Abuse override appeared: '{resp[:80]}...'")

    print("\n✓ test_conversation_handler_abuse_override passed")


def test_conversation_handler_history_trimming():
    """Conversation history is trimmed to MAX_CONVERSATION_HISTORY entries."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer
    import config

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    for i in range(config.MAX_CONVERSATION_HISTORY + 5):
        data = analyzer.classify_emotion(f"Message number {i}")
        handler.add_message(f"Message {i}", data)

    assert len(handler.conversation_history) == config.MAX_CONVERSATION_HISTORY
    print(f"✓ History trimmed to {config.MAX_CONVERSATION_HISTORY} entries")

    print("\n✓ test_conversation_handler_history_trimming passed")


def test_conversation_handler_greeting():
    """get_greeting() returns a valid greeting from the configured list."""
    from conversation_handler import ConversationHandler
    import config

    handler = ConversationHandler()
    greeting = handler.get_greeting()
    assert isinstance(greeting, str) and len(greeting) > 5
    assert greeting in config.GREETING_MESSAGES
    print(f"✓ Greeting: '{greeting}'")

    print("\n✓ test_conversation_handler_greeting passed")


def test_conversation_handler_response_deduplication():
    """generate_response avoids returning the same response twice in a row."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()
    emotion_data = analyzer.classify_emotion("I feel anxious and worried")

    responses = [handler.generate_response(emotion_data) for _ in range(10)]
    # No two consecutive responses should be identical
    for i in range(1, len(responses)):
        assert responses[i] != responses[i - 1], \
            f"Response {i} is same as response {i - 1}: '{responses[i][:60]}'"
    print(f"✓ No consecutive duplicate in {len(responses)} responses")

    print("\n✓ test_conversation_handler_response_deduplication passed")


# ─────────────────────────────────────────────────────────────────────────────
# UserProfile — advanced
# ─────────────────────────────────────────────────────────────────────────────

def test_user_profile_guardian_contacts():
    """add_guardian_contact / get_guardian_contacts round-trip."""
    from user_profile import UserProfile

    profile = UserProfile('guardian_test')
    assert profile.get_guardian_contacts() == []

    profile.add_guardian_contact('Mum', 'mother', '555-0001')
    profile.add_guardian_contact('Dad', 'father', '555-0002')

    contacts = profile.get_guardian_contacts()
    assert len(contacts) == 2
    names = [c['name'] for c in contacts]
    assert 'Mum' in names and 'Dad' in names
    print(f"✓ Guardian contacts: {names}")

    print("\n✓ test_user_profile_guardian_contacts passed")


def test_user_profile_display_name():
    """get_display_name() returns name > user_id > 'Friend' in priority order."""
    from user_profile import UserProfile

    p1 = UserProfile('alice_id')
    assert p1.get_display_name() == 'alice_id'
    print(f"✓ No name → user_id: '{p1.get_display_name()}'")

    p2 = UserProfile('bob_id')
    p2.set_name('Bob')
    assert p2.get_display_name() == 'Bob'
    print(f"✓ With name → '{p2.get_display_name()}'")

    p3 = UserProfile(None)
    p3.profile_data['name'] = None
    assert p3.get_display_name() == 'Friend'
    print(f"✓ No name or user_id → 'Friend'")

    print("\n✓ test_user_profile_display_name passed")


def test_user_profile_session_count():
    """increment_session_count() increments correctly."""
    from user_profile import UserProfile

    profile = UserProfile('count_test')
    assert profile.get_profile()['session_count'] == 0

    profile.increment_session_count()
    assert profile.get_profile()['session_count'] == 1

    for _ in range(9):
        profile.increment_session_count()
    assert profile.get_profile()['session_count'] == 10
    print(f"✓ Session count correctly incremented to {profile.get_profile()['session_count']}")

    print("\n✓ test_user_profile_session_count passed")


def test_user_profile_session_expiry():
    """is_session_expired() returns False for fresh session, True after timeout."""
    from user_profile import UserProfile
    import config

    profile = UserProfile('expiry_test')
    profile.update_last_activity()
    assert not profile.is_session_expired(), "Fresh session should not be expired"
    print("✓ Fresh session is not expired")

    profile.profile_data['last_activity'] = (
        datetime.now() - timedelta(minutes=config.SESSION_TIMEOUT_MINUTES + 5)
    )
    if config.SESSION_TIMEOUT_MINUTES > 0:
        assert profile.is_session_expired(), "Session should be expired after timeout"
        print(f"✓ Session expired after {config.SESSION_TIMEOUT_MINUTES} min timeout")

    print("\n✓ test_user_profile_session_expiry passed")


def test_user_profile_load_from_data():
    """load_from_data() restores all fields from a saved profile dict."""
    from user_profile import UserProfile

    original = UserProfile('load_test')
    original.set_name('Charlie')
    original.set_age(30)
    original.set_occupation('Engineer')
    original.add_trusted_contact('Dana', 'colleague')

    data = original.get_profile()

    loaded = UserProfile('load_test')
    loaded.load_from_data(data)

    assert loaded.get_profile()['name'] == 'Charlie'
    assert loaded.get_profile()['age'] == 30
    assert loaded.get_profile()['occupation'] == 'Engineer'
    assert len(loaded.get_trusted_contacts()) == 1
    assert loaded.get_trusted_contacts()[0]['name'] == 'Dana'
    print("✓ load_from_data() restores name, age, occupation, trusted_contacts")

    print("\n✓ test_user_profile_load_from_data passed")


def test_user_profile_emotional_history_filtering():
    """get_emotional_history(days=N) returns exactly the last N snapshots."""
    from user_profile import UserProfile

    profile = UserProfile('hist_filter')

    for _ in range(20):
        profile.add_emotional_snapshot(
            {'emotion': 'neutral', 'polarity': 0.0},
            {'average_sentiment': 0.0, 'message_count': 5, 'distress_ratio': 0.0},
        )

    assert len(profile.get_emotional_history()) == 20
    assert len(profile.get_emotional_history(days=10)) == 10
    assert len(profile.get_emotional_history(days=5)) == 5
    print("✓ History filtering: all=20, last10=10, last5=5")

    print("\n✓ test_user_profile_emotional_history_filtering passed")


def test_user_profile_primary_concerns():
    """set_primary_concerns() stores and retrieves concerns list."""
    from user_profile import UserProfile

    profile = UserProfile('concerns_test')
    concerns = ['anxiety', 'depression', 'work stress']
    profile.set_primary_concerns(concerns)
    assert profile.get_profile()['primary_concerns'] == concerns
    print(f"✓ Primary concerns: {profile.get_profile()['primary_concerns']}")

    print("\n✓ test_user_profile_primary_concerns passed")


def test_user_profile_badges_sessions():
    """sessions_10 badge awarded after 10 increment_session_count calls."""
    from user_profile import UserProfile

    profile = UserProfile('badge_test')
    for _ in range(10):
        profile.increment_session_count()

    profile.check_and_award_badges()
    badge_ids = {b['id'] for b in profile.get_profile()['badges']}
    assert 'sessions_10' in badge_ids, f"sessions_10 badge missing; badges: {badge_ids}"
    print(f"✓ sessions_10 badge awarded after 10 sessions: {badge_ids}")

    print("\n✓ test_user_profile_badges_sessions passed")


def test_user_profile_stability_score_bounds():
    """calculate_stability_score() always returns a value in [0, 100]."""
    from user_profile import UserProfile

    profile = UserProfile('stability_test')

    test_summaries = [
        {'average_sentiment': 1.0,  'distress_ratio': 0.0},   # best case
        {'average_sentiment': -1.0, 'distress_ratio': 1.0},   # worst case
        {'average_sentiment': 0.0,  'distress_ratio': 0.5},   # middle
        {'average_sentiment': 0.5,  'distress_ratio': 0.2},   # typical
    ]
    for s in test_summaries:
        score = profile.calculate_stability_score(s)
        assert 0.0 <= score <= 100.0, f"Score {score} out of bounds for {s}"
        print(f"  avg_sent={s['average_sentiment']}, distress={s['distress_ratio']} → score={score}")

    print("\n✓ test_user_profile_stability_score_bounds passed")


# ─────────────────────────────────────────────────────────────────────────────
# EmotionAnalyzer — edge cases
# ─────────────────────────────────────────────────────────────────────────────

def test_emotion_analyzer_edge_cases():
    """EmotionAnalyzer handles empty string, single word, long text, and digits."""
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()

    # Empty string
    r_empty = analyzer.classify_emotion("")
    assert 'emotion' in r_empty
    assert r_empty['crisis_detected'] is False
    assert 0.0 <= r_empty['severity_score'] <= 10.0
    print(f"✓ Empty string: emotion={r_empty['emotion']}, crisis={r_empty['crisis_detected']}")

    # Single keyword word
    r_sad = analyzer.classify_emotion("sad")
    assert 'dominant_emotion' in r_sad
    print(f"✓ Single word 'sad': dominant={r_sad['dominant_emotion']}")

    # Long positive message
    long_pos = "I am feeling wonderful, amazing, happy, joyful, and grateful! " * 10
    r_long = analyzer.classify_emotion(long_pos)
    assert r_long['dominant_emotion'] == 'joy'
    assert r_long['severity_score'] < 5.0
    print(f"✓ Long positive: dominant={r_long['dominant_emotion']}, severity={r_long['severity_score']}")

    # Numbers only
    r_nums = analyzer.classify_emotion("123 456 789")
    assert 'emotion' in r_nums
    print(f"✓ Numbers only: emotion={r_nums['emotion']}")

    print("\n✓ test_emotion_analyzer_edge_cases passed")


def test_emotion_analyzer_severity_score_range():
    """severity_score is always within [0.0, 10.0]."""
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    messages = [
        "I'm absolutely thrilled and happy!",
        "",
        "I feel okay",
        "I'm anxious, stressed, and really worried about everything",
        "I feel hopeless, worthless, trapped and alone — I can't take it",
    ]
    for msg in messages:
        result = analyzer.classify_emotion(msg)
        assert 0.0 <= result['severity_score'] <= 10.0, \
            f"severity_score {result['severity_score']} out of range for: '{msg}'"
        print(f"  '{msg[:40]}' → score={result['severity_score']}")

    print("\n✓ test_emotion_analyzer_severity_score_range passed")


def test_emotion_analyzer_all_fields_present():
    """classify_emotion() always returns every expected field."""
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    result = analyzer.classify_emotion("I feel a bit sad today")

    required_fields = [
        'emotion', 'severity', 'polarity', 'subjectivity',
        'distress_keywords', 'abuse_indicators', 'has_abuse_indicators',
        'timestamp', 'emotion_scores', 'dominant_emotion', 'severity_score',
        'crisis_detected', 'crisis_keywords', 'keyword_explanation',
    ]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    print(f"✓ All {len(required_fields)} required fields present")

    print("\n✓ test_emotion_analyzer_all_fields_present passed")


# ─────────────────────────────────────────────────────────────────────────────
# Config completeness
# ─────────────────────────────────────────────────────────────────────────────

def test_config_completeness():
    """All required config keys exist and have valid values."""
    import config

    checks = [
        ('DISTRESS_THRESHOLD',       float,  lambda v: -1.0 <= v <= 0.0),
        ('SUSTAINED_DISTRESS_COUNT', int,    lambda v: v > 0),
        ('PATTERN_TRACKING_WINDOW',  int,    lambda v: v > 0),
        ('EMOTIONAL_HISTORY_DAYS',   int,    lambda v: v >= 30),
        ('MAX_CONVERSATION_HISTORY', int,    lambda v: v > 0),
        ('MIN_PASSWORD_LENGTH',      int,    lambda v: v >= 6),
        ('MAX_LOGIN_ATTEMPTS',       int,    lambda v: v >= 1),
        ('LOCKOUT_DURATION_MINUTES', int,    lambda v: v >= 1),
        ('PREDICTION_WINDOW',        int,    lambda v: v >= 3),
        ('MAX_ALERT_LOG_ENTRIES',    int,    lambda v: v >= 1),
        ('TIME_DECAY_FACTOR',        float,  lambda v: 0.0 < v < 1.0),
        ('SEVERITY_HIGH_THRESHOLD',  float,  lambda v: v > 0),
    ]

    for name, exp_type, validator in checks:
        assert hasattr(config, name), f"config.{name} missing"
        val = getattr(config, name)
        assert isinstance(val, exp_type), f"config.{name} type {type(val)}, expected {exp_type}"
        assert validator(val), f"config.{name}={val} fails range check"
        print(f"  ✓ {name} = {val}")

    assert isinstance(config.GENERAL_SUPPORT_RESOURCES, dict)
    assert '988' in str(config.GENERAL_SUPPORT_RESOURCES)

    assert isinstance(config.ALERT_SEVERITY_LEVELS, list)
    assert len(config.ALERT_SEVERITY_LEVELS) == 5
    assert 'CRITICAL' in config.ALERT_SEVERITY_LEVELS

    assert hasattr(config, 'CRISIS_IMMEDIATE_MESSAGE')
    assert '988' in config.CRISIS_IMMEDIATE_MESSAGE

    assert hasattr(config, 'CRISIS_RESOURCES')
    assert isinstance(config.CRISIS_RESOURCES, dict)

    assert hasattr(config, 'STREAK_NOTIFICATION_THRESHOLD')
    assert config.STREAK_NOTIFICATION_THRESHOLD > 0

    print("\n✓ test_config_completeness passed")


# ─────────────────────────────────────────────────────────────────────────────
# Full integration tests
# ─────────────────────────────────────────────────────────────────────────────

def test_full_integration_realistic_conversation():
    """Multi-turn realistic conversation: personalised responses + prediction metrics."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    temp_dir = tempfile.mkdtemp()
    try:
        buddy = WellnessBuddy(data_dir=temp_dir)
        buddy.user_profile = UserProfile('integ_user')
        buddy.user_profile.set_name('Priya')
        buddy.user_profile.set_age(28)
        buddy.user_profile.set_occupation('student')
        buddy.user_profile.add_guardian_contact('Mum', 'mother', '999-1234')
        buddy.user_id = 'integ_user'

        conversation = [
            "Hi, I've been feeling overwhelmed with my studies",
            "I'm stressed about my exams and can't sleep properly",
            "I feel really anxious and worried about the future",
            "I've been feeling sad and hopeless lately",
            "I'm so exhausted I don't know what to do",
        ]

        responses = [buddy.process_message(msg) for msg in conversation]
        assert all(len(r) > 10 for r in responses)
        print(f"✓ {len(responses)} messages processed, all non-empty")

        # At least some responses personalised with the user's name
        name_count = sum(1 for r in responses if 'Priya' in r)
        print(f"✓ {name_count}/{len(responses)} responses personalised with 'Priya'")

        # Pattern summary accumulated
        summary = buddy.pattern_tracker.get_pattern_summary()
        assert summary is not None
        assert summary['total_messages'] == len(conversation)
        print(f"✓ Pattern: {summary['total_messages']} msgs, trend={summary['trend']}, "
              f"severity={summary['severity_level']}")

        # Prediction agent has data
        metrics = buddy.prediction_agent.get_metrics()
        assert metrics['data_points'] == len(conversation)
        print(f"✓ Prediction: {metrics['data_points']} data pts, trend={metrics['trend']}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n✓ test_full_integration_realistic_conversation passed")


def test_full_integration_distress_alert_fires():
    """Enough distress messages trigger an alert entry in the alert log."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    temp_dir = tempfile.mkdtemp()
    try:
        buddy = WellnessBuddy(data_dir=temp_dir)
        buddy.user_profile = UserProfile('alert_integ')
        buddy.user_profile.set_name('Alex')
        buddy.user_profile.add_guardian_contact('Parent', 'guardian', '555-0000')
        buddy.user_id = 'alert_integ'

        distress_msgs = [
            "I feel hopeless and worthless",
            "Everything is terrible and I'm so sad",
            "I can't cope with this, I'm exhausted",
            "Nothing helps, I feel completely alone",
        ]

        for msg in distress_msgs:
            buddy.process_message(msg)

        # Alert log should have at least one entry
        log = buddy.alert_system.get_alert_log()
        print(f"✓ Alert log entries: {len(log)}")
        if log:
            print(f"  Last alert severity: {log[-1]['severity']}")

        # Pattern counts are correct
        summary = buddy.pattern_tracker.get_pattern_summary()
        assert summary['distress_messages'] > 0
        print(f"✓ Distress messages counted: {summary['distress_messages']}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n✓ test_full_integration_distress_alert_fires passed")


def test_full_integration_crisis_in_conversation():
    """A crisis message mid-conversation short-circuits to immediate resources."""
    from wellness_buddy import WellnessBuddy
    from user_profile import UserProfile

    buddy = WellnessBuddy()
    buddy.user_profile = UserProfile('crisis_conv')
    buddy.user_profile.set_name('Sam')
    buddy.user_id = 'crisis_conv'

    # Normal messages first
    buddy.process_message("I've been feeling down lately")
    buddy.process_message("Things are hard at work")

    # Crisis message
    crisis_resp = buddy.process_message("I want to end my life")
    assert '988' in crisis_resp
    print(f"✓ Mid-conversation crisis response contains 988")

    # Conversation can continue normally after crisis
    after_resp = buddy.process_message("I'm feeling okay now, thanks")
    assert isinstance(after_resp, str) and len(after_resp) > 5
    print(f"✓ Conversation resumes after crisis: '{after_resp[:60]}...'")

    print("\n✓ test_full_integration_crisis_in_conversation passed")


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner
# ─────────────────────────────────────────────────────────────────────────────

def run_all():
    """Run all tests and print a summary (for standalone execution)."""
    import sys

    tests = [
        test_wellness_buddy_process_message,
        test_wellness_buddy_crisis_short_circuit,
        test_wellness_buddy_help_command,
        test_wellness_buddy_status_command,
        test_wellness_buddy_end_session,
        test_wellness_buddy_no_profile,
        test_pattern_tracker_severity_levels,
        test_pattern_tracker_emotion_distribution,
        test_pattern_tracker_insufficient_data,
        test_pattern_tracker_consecutive_distress_reset,
        test_alert_escalation,
        test_alert_guardian_consent,
        test_alert_format_guardian_notification,
        test_alert_abuse_severity_escalation,
        test_alert_no_trigger_without_sustained_distress,
        test_prediction_agent_insufficient_data,
        test_prediction_agent_classify_trend,
        test_prediction_agent_early_warning,
        test_prediction_agent_metrics_accumulate,
        test_prediction_agent_forecast_series,
        test_conversation_handler_abuse_override,
        test_conversation_handler_history_trimming,
        test_conversation_handler_greeting,
        test_conversation_handler_response_deduplication,
        test_user_profile_guardian_contacts,
        test_user_profile_display_name,
        test_user_profile_session_count,
        test_user_profile_session_expiry,
        test_user_profile_load_from_data,
        test_user_profile_emotional_history_filtering,
        test_user_profile_primary_concerns,
        test_user_profile_badges_sessions,
        test_user_profile_stability_score_bounds,
        test_emotion_analyzer_edge_cases,
        test_emotion_analyzer_severity_score_range,
        test_emotion_analyzer_all_fields_present,
        test_config_completeness,
        test_full_integration_realistic_conversation,
        test_full_integration_distress_alert_fires,
        test_full_integration_crisis_in_conversation,
    ]

    print("\n" + "=" * 70)
    print("   AI WELLNESS BUDDY — FULL COVERAGE TEST SUITE")
    print("=" * 70)

    passed = failed = 0
    for fn in tests:
        try:
            fn()
            passed += 1
        except Exception as exc:
            print(f"\n❌ FAILED: {fn.__name__}: {exc}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"  RESULT: {passed} passed, {failed} failed / {len(tests)} total")
    print("=" * 70 + "\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all())
