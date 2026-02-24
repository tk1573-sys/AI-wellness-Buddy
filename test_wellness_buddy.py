"""
Simple test script for AI Wellness Buddy
Demonstrates core functionality without requiring interactive input
"""

from emotion_analyzer import EmotionAnalyzer
from pattern_tracker import PatternTracker
from alert_system import AlertSystem
from conversation_handler import ConversationHandler
from user_profile import UserProfile
from data_store import DataStore
import tempfile
import shutil


def test_emotion_analysis():
    """Test emotion analysis functionality"""
    print("\n" + "="*70)
    print("TEST 1: Emotion Analysis")
    print("="*70)
    
    analyzer = EmotionAnalyzer()
    
    test_messages = [
        "I'm feeling great today! Everything is going well.",
        "I'm a bit worried about work, but managing.",
        "I feel so sad and alone. Nobody understands me.",
        "I'm trapped in this abusive relationship and don't know what to do."
    ]
    
    for msg in test_messages:
        result = analyzer.classify_emotion(msg)
        print(f"\nMessage: '{msg}'")
        print(f"  Emotion: {result['emotion']}")
        print(f"  Severity: {result['severity']}")
        print(f"  Polarity: {result['polarity']:.2f}")
        print(f"  Distress keywords: {result['distress_keywords']}")
        print(f"  Abuse indicators: {result['abuse_indicators']}")


def test_pattern_tracking():
    """Test pattern tracking and distress detection"""
    print("\n" + "="*70)
    print("TEST 2: Pattern Tracking & Distress Detection")
    print("="*70)
    
    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()
    
    # Simulate a series of distressing messages
    distress_messages = [
        "I'm feeling really down today",
        "Everything feels hopeless and I'm so sad",
        "I can't take this anymore, I feel worthless",
        "Still feeling terrible, nothing is getting better"
    ]
    
    for i, msg in enumerate(distress_messages, 1):
        emotion_data = analyzer.classify_emotion(msg)
        tracker.add_emotion_data(emotion_data)
        
        summary = tracker.get_pattern_summary()
        print(f"\nMessage {i}: '{msg}'")
        print(f"  Consecutive distress: {summary['consecutive_distress']}")
        print(f"  Sustained distress detected: {summary['sustained_distress_detected']}")
        print(f"  Trend: {summary['trend']}")


def test_alert_system():
    """Test alert triggering"""
    print("\n" + "="*70)
    print("TEST 3: Alert System")
    print("="*70)
    
    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()
    alert_system = AlertSystem()
    
    # Trigger sustained distress
    for _ in range(3):
        emotion_data = analyzer.classify_emotion("I feel so hopeless and sad")
        tracker.add_emotion_data(emotion_data)
    
    summary = tracker.get_pattern_summary()
    
    if alert_system.should_trigger_alert(summary):
        print("\n✓ Alert triggered successfully!")
        profile = UserProfile('test_user')
        profile.set_gender('female')
        
        alert = alert_system.trigger_distress_alert(summary, profile.get_profile())
        alert_message = alert_system.format_alert_message(alert)
        print("\nAlert Message:")
        print(alert_message)
    else:
        print("\n✗ Alert not triggered (unexpected)")


def test_conversation_handler():
    """Test conversation responses"""
    print("\n" + "="*70)
    print("TEST 4: Conversation Handler")
    print("="*70)
    
    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()
    
    test_messages = [
        "I'm having a wonderful day!",
        "Feeling kind of neutral, just okay.",
        "I'm really struggling with anxiety today.",
    ]
    
    for msg in test_messages:
        emotion_data = analyzer.classify_emotion(msg)
        handler.add_message(msg, emotion_data)
        response = handler.generate_response(emotion_data)
        
        print(f"\nUser: '{msg}'")
        print(f"Buddy: {response}")


def test_user_profile():
    """Test user profile management"""
    print("\n" + "="*70)
    print("TEST 5: User Profile & Specialized Support")
    print("="*70)
    
    profile = UserProfile('test_user')
    profile.set_gender('female')
    profile.set_relationship_status('married')
    
    # Test trusted contacts
    profile.add_trusted_contact('Sarah', 'best friend', '555-1234')
    profile.add_unsafe_contact('family/guardians')
    
    print(f"\nUser Profile Created:")
    print(f"  User ID: {profile.get_profile()['user_id']}")
    print(f"  Gender: {profile.get_profile()['gender']}")
    print(f"  Is female: {profile.is_female()}")
    print(f"  Needs women support: {profile.needs_women_support()}")
    print(f"  Has unsafe family: {profile.has_unsafe_family()}")
    print(f"  Trusted contacts: {len(profile.get_trusted_contacts())}")


def test_data_persistence():
    """Test data storage and retrieval"""
    print("\n" + "="*70)
    print("TEST 6: Data Persistence")
    print("="*70)
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create and save profile
        data_store = DataStore(temp_dir)
        profile = UserProfile('test_user_123')
        profile.set_gender('female')
        profile.add_trusted_contact('Jane', 'friend')
        
        data_store.save_user_data('test_user_123', profile.get_profile())
        print("\n✓ Profile saved")
        
        # Check if user exists
        exists = data_store.user_exists('test_user_123')
        print(f"✓ User exists check: {exists}")
        
        # Load profile
        loaded_data = data_store.load_user_data('test_user_123')
        if loaded_data:
            print(f"✓ Profile loaded")
            print(f"  Gender: {loaded_data.get('gender')}")
            print(f"  Trusted contacts: {len(loaded_data.get('trusted_contacts', []))}")
        
        # List users
        users = data_store.list_users()
        print(f"✓ Users in store: {users}")
        
        # Delete user
        deleted = data_store.delete_user_data('test_user_123')
        print(f"✓ User deleted: {deleted}")
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def test_full_workflow():
    """Test complete workflow with abuse detection"""
    print("\n" + "="*70)
    print("TEST 7: Full Workflow - Abuse Detection & Alert")
    print("="*70)
    
    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()
    alert_system = AlertSystem()
    handler = ConversationHandler()
    profile = UserProfile('test_user')
    profile.set_gender('female')
    profile.add_unsafe_contact('family/guardians')
    profile.add_trusted_contact('Sarah', 'best friend', '555-0123')
    
    # Simulate conversation with abuse indicators
    messages = [
        "My husband is always controlling everything I do",
        "I feel trapped and alone in my marriage",
        "He constantly belittles me and I feel worthless"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"User: '{msg}'")
        
        emotion_data = analyzer.classify_emotion(msg)
        tracker.add_emotion_data(emotion_data)
        handler.add_message(msg, emotion_data)
        
        response = handler.generate_response(emotion_data)
        print(f"Buddy: {response}")
        
        # Check for alert
        summary = tracker.get_pattern_summary()
        if alert_system.should_trigger_alert(summary):
            print("\n🚨 ALERT TRIGGERED 🚨")
            alert = alert_system.trigger_distress_alert(summary, profile.get_profile())
            alert_message = alert_system.format_alert_message(alert, profile.get_trusted_contacts())
            print(alert_message)
            tracker.reset_consecutive_distress()


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("   AI WELLNESS BUDDY - AUTOMATED TESTS")
    print("="*70)
    
    try:
        test_emotion_analysis()
        test_pattern_tracking()
        test_alert_system()
        test_conversation_handler()
        test_user_profile()
        test_data_persistence()
        test_full_workflow()
        
        print("\n" + "="*70)
        print("   ✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()


# ─────────────────────────────────────────────────────────────────────────────
# NEW MODULE TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_multi_emotion_classification():
    """Test Module 1: multi-emotion classification."""
    print("\n" + "="*70)
    print("TEST 8: Multi-Emotion Classification (Module 1)")
    print("="*70)

    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()

    cases = [
        ("I'm so happy and grateful today!", 'joy'),
        ("I'm really anxious and worried about everything", 'anxiety'),
        ("I feel so sad and hopeless", 'sadness'),
        ("I'm furious about what happened!", 'anger'),
    ]

    for text, expected_dominant in cases:
        result = analyzer.classify_emotion(text)
        scores = result['emotion_scores']
        dominant = result['dominant_emotion']
        severity_score = result['severity_score']
        print(f"\nText: '{text}'")
        print(f"  Dominant emotion: {dominant}  (expected: {expected_dominant})")
        print(f"  Scores: {scores}")
        print(f"  Severity score: {severity_score}/10")
        # Check new fields are present
        assert 'emotion_scores' in result, "emotion_scores missing"
        assert 'dominant_emotion' in result, "dominant_emotion missing"
        assert 'severity_score' in result, "severity_score missing"
        assert 0.0 <= result['severity_score'] <= 10.0, "severity_score out of range"
        # All legacy fields still present
        assert 'emotion' in result
        assert 'severity' in result

    print("\n✓ Multi-emotion classification test passed")


def test_time_weighted_distress():
    """Test Module 2: time-weighted severity scoring."""
    print("\n" + "="*70)
    print("TEST 9: Time-Weighted Distress Monitoring (Module 2)")
    print("="*70)

    from emotion_analyzer import EmotionAnalyzer
    from pattern_tracker import PatternTracker

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()

    messages = [
        "I'm okay today",
        "Feeling a bit down",
        "I'm really anxious and worried",
        "I feel hopeless and can't take it anymore",
    ]
    for msg in messages:
        data = analyzer.classify_emotion(msg)
        tracker.add_emotion_data(data)

    summary = tracker.get_pattern_summary()
    assert 'weighted_sentiment' in summary, "weighted_sentiment missing"
    assert 'severity_score' in summary, "severity_score missing"
    assert 'severity_level' in summary, "severity_level missing"
    assert 'emotion_distribution' in summary, "emotion_distribution missing"
    print(f"  Weighted sentiment: {summary['weighted_sentiment']:.4f}")
    print(f"  Severity score: {summary['severity_score']}/10")
    print(f"  Severity level: {summary['severity_level']}")
    print(f"  Emotion distribution: {summary['emotion_distribution']}")
    print("\n✓ Time-weighted distress monitoring test passed")


def test_prediction_agent():
    """Test Module 3: PredictionAgent."""
    print("\n" + "="*70)
    print("TEST 10: Pattern Prediction Agent (Module 3)")
    print("="*70)

    from prediction_agent import PredictionAgent

    agent = PredictionAgent()

    # Simulate declining sentiment
    sentiments = [0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3]
    for s in sentiments:
        agent.add_data_point(s, 'sadness')

    prediction = agent.predict_next_state()
    print(f"  Predicted next sentiment: {prediction['predicted_sentiment']}")
    print(f"  Trend: {prediction['trend']}")
    print(f"  Confidence: {prediction['confidence']}")
    print(f"  Early warning: {prediction['early_warning']}")

    assert 'predicted_sentiment' in prediction
    assert prediction['trend'] in ('improving', 'stable', 'worsening', 'insufficient_data')
    assert 0.0 <= prediction['confidence'] <= 1.0

    metrics = agent.get_metrics()
    print(f"  Metrics: {metrics}")
    assert 'mae' in metrics
    assert 'rmse' in metrics

    forecast = agent.get_forecast_series(steps=3)
    assert len(forecast) == 3
    print(f"  5-step forecast: {forecast}")
    print("\n✓ Prediction agent test passed")


def test_alert_severity_escalation():
    """Test Module 5: alert severity and escalation."""
    print("\n" + "="*70)
    print("TEST 11: Alert Severity & Escalation (Module 5)")
    print("="*70)

    from alert_system import AlertSystem
    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()
    alert_sys = AlertSystem()

    for _ in range(4):
        data = analyzer.classify_emotion("I feel hopeless and worthless")
        tracker.add_emotion_data(data)

    summary = tracker.get_pattern_summary()
    assert alert_sys.should_trigger_alert(summary)

    alert = alert_sys.trigger_distress_alert(summary, {'gender': 'male', 'user_id': 'tester'})
    print(f"  Alert severity: {alert['severity']}")
    assert 'severity' in alert
    assert alert['severity'] in ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')

    # Test acknowledge
    alert_sys.acknowledge_alert(alert)
    assert alert['acknowledged']

    # Test log
    log = alert_sys.get_alert_log()
    assert len(log) >= 1
    print(f"  Alert log entries: {len(log)}")
    print(f"  Log entry: {log[-1]}")
    print("\n✓ Alert severity & escalation test passed")


def test_password_protection():
    """Test profile password protection and lockout (for UI gate)."""
    import pytest
    import config as cfg
    print("\n" + "="*70)
    print("TEST 12: Password Protection")
    print("="*70)

    profile = UserProfile('secure_user')

    # No password set → verify_password() always returns True
    assert profile.verify_password('anything'), "No password should allow any input"
    print("✓ No-password profile allows access")

    # Set a password
    profile.set_password('MySecret99')
    assert profile.get_profile()['password_hash'] is not None
    assert profile.get_profile()['salt'] is not None
    print("✓ Password set (hash + salt stored)")

    # Correct password
    assert profile.verify_password('MySecret99'), "Correct password should return True"
    print("✓ Correct password accepted")

    # Wrong password
    result = profile.verify_password('WrongPass!')
    assert not result, "Wrong password should return False"
    print(f"✓ Wrong password rejected (failed_login_attempts={profile.get_profile()['failed_login_attempts']})")

    # Lockout after MAX_LOGIN_ATTEMPTS wrong attempts
    profile.reset_lockout()
    for _ in range(cfg.MAX_LOGIN_ATTEMPTS):
        profile.verify_password('wrong')
    assert profile.is_locked_out(), "Should be locked out after too many attempts"
    assert not profile.verify_password('MySecret99'), "Locked account should deny even correct password"
    print(f"✓ Lockout triggered after {cfg.MAX_LOGIN_ATTEMPTS} attempts")

    # Short-password rejection (use pytest.raises for idiomatic testing)
    with pytest.raises(ValueError):
        profile.set_password('short')
    print(f"✓ Short password rejected (min {cfg.MIN_PASSWORD_LENGTH} chars)")

    # Change password using reset_lockout() helper
    profile.reset_lockout()
    profile.set_password('NewSecret42')
    assert profile.verify_password('NewSecret42'), "New password should work"
    assert not profile.verify_password('MySecret99'), "Old password should not work"
    print("✓ Password changed successfully")

    # Remove password using remove_password()
    profile.remove_password()
    assert profile.get_profile()['password_hash'] is None
    assert not profile.get_profile()['security_enabled']
    assert profile.verify_password('anything'), "After removal, any input should be accepted"
    print("✓ Password removed — profile now unprotected")

    print("\n✓ Password protection test passed")


# ─────────────────────────────────────────────────────────────────────────────
# MODULES 8, 10, 11, 12, 13 TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_crisis_detection():
    """Test Module 11: Crisis Detection."""
    print("\n" + "="*70)
    print("TEST 13: Crisis Detection Module (Module 11)")
    print("="*70)

    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()

    # Message with clear crisis phrase
    crisis_msg = "I want to kill myself, I can't take it anymore"
    result = analyzer.classify_emotion(crisis_msg)
    assert result['crisis_detected'], "crisis_detected should be True"
    assert len(result['crisis_keywords']) > 0, "crisis_keywords should be non-empty"
    print(f"✓ Crisis detected: {result['crisis_keywords']}")

    # Normal distress message — should not be crisis
    normal_msg = "I feel so sad and hopeless"
    result2 = analyzer.classify_emotion(normal_msg)
    assert not result2['crisis_detected'], "crisis_detected should be False for non-crisis message"
    print("✓ Non-crisis message correctly not flagged as crisis")

    # Crisis detection also present in detect_crisis_phrases()
    phrases = analyzer.detect_crisis_phrases("end my life please")
    assert len(phrases) > 0, "detect_crisis_phrases should find 'end my life'"
    print(f"✓ detect_crisis_phrases works: {phrases}")

    print("\n✓ Crisis detection test passed")


def test_xai_keyword_explanation():
    """Test Module 8: Explainable AI keyword explanation."""
    print("\n" + "="*70)
    print("TEST 14: Explainable AI — Keyword Explanation (Module 8)")
    print("="*70)

    from emotion_analyzer import EmotionAnalyzer
    analyzer = EmotionAnalyzer()

    result = analyzer.classify_emotion("I feel so anxious and worried about everything")
    explanation = result.get('keyword_explanation', [])
    assert isinstance(explanation, list), "keyword_explanation should be a list"
    assert len(explanation) > 0, "Should have at least one keyword explanation"

    for item in explanation:
        assert 'word' in item, "Each item needs 'word'"
        assert 'emotion' in item, "Each item needs 'emotion'"
        assert 'contribution' in item, "Each item needs 'contribution'"

    emotions_found = {item['emotion'] for item in explanation}
    assert 'anxiety' in emotions_found, "Anxiety keywords should be in explanation"
    print(f"✓ Explanation items: {len(explanation)}")
    print(f"✓ Emotions in explanation: {emotions_found}")

    # Direct method call
    expl2 = analyzer.get_keyword_explanation("I am furious and angry")
    assert any(item['emotion'] == 'anger' for item in expl2), "anger should appear in explanation"
    print("✓ get_keyword_explanation() works correctly")

    print("\n✓ XAI keyword explanation test passed")


def test_gamification():
    """Test Module 13: Gamified Wellness Tracking."""
    print("\n" + "="*70)
    print("TEST 15: Gamified Wellness Tracking (Module 13)")
    print("="*70)

    from user_profile import UserProfile
    profile = UserProfile('gamify_test')

    # Initial state
    assert profile.get_profile()['mood_streak'] == 0
    assert profile.get_profile()['best_streak'] == 0
    assert profile.get_profile()['stability_score'] == 50.0
    assert isinstance(profile.get_profile()['badges'], list)
    print("✓ Initial gamification state correct")

    # Positive sessions increase streak
    for _ in range(3):
        profile.update_mood_streak(True)
    assert profile.get_profile()['mood_streak'] == 3
    assert profile.get_profile()['best_streak'] == 3
    print(f"✓ Streak after 3 positive sessions: {profile.get_profile()['mood_streak']}")

    # Negative session resets streak
    profile.update_mood_streak(False)
    assert profile.get_profile()['mood_streak'] == 0
    assert profile.get_profile()['best_streak'] == 3, "Best streak should not reset"
    print("✓ Negative session resets streak, best_streak preserved")

    # Check badges awarded (first_session + streak_3 at least)
    badges = profile.get_profile()['badges']
    badge_ids = {b['id'] for b in badges}
    assert 'streak_3' in badge_ids, "streak_3 badge should be awarded"
    print(f"✓ Badges awarded: {badge_ids}")

    # Stability score calculation
    summary = {'average_sentiment': 0.3, 'distress_ratio': 0.1}
    score = profile.calculate_stability_score(summary)
    assert 0 <= score <= 100
    print(f"✓ Stability score: {score}/100")

    # Response style
    profile.set_response_style('short')
    assert profile.get_profile()['response_style'] == 'short'
    profile.set_response_style('detailed')
    assert profile.get_profile()['response_style'] == 'detailed'
    profile.set_response_style('invalid')   # should not change
    assert profile.get_profile()['response_style'] == 'detailed'
    print("✓ Response style set/validated correctly")

    print("\n✓ Gamification test passed")


def test_rl_response_feedback():
    """Test Module 10: RL Response Feedback."""
    print("\n" + "="*70)
    print("TEST 16: RL Response Feedback (Module 10)")
    print("="*70)

    from user_profile import UserProfile
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    profile = UserProfile('rl_test')
    handler = ConversationHandler()
    analyzer = EmotionAnalyzer()

    # Generate a response
    emotion_data = analyzer.classify_emotion("I'm feeling a bit sad today")
    response = handler.generate_response(emotion_data, profile.get_profile())
    template_key = handler.get_last_template_key()
    assert template_key is not None, "Template key should be set after generate_response"
    print(f"✓ Template key retrieved: '{template_key}'")

    # Record positive feedback
    profile.record_response_feedback(template_key, positive=True)
    fb = profile.get_response_feedback()
    assert fb.get(template_key, 0) == 1, "Positive feedback should set score to 1"
    print(f"✓ Positive feedback recorded: {fb}")

    # Record negative feedback
    profile.record_response_feedback(template_key, positive=False)
    fb2 = profile.get_response_feedback()
    assert fb2.get(template_key, 0) == 0, "One negative + one positive = 0"
    print(f"✓ Negative feedback recorded, cumulative: {fb2}")

    # Response style: short
    profile.set_response_style('short')
    short_response = handler.generate_response(emotion_data, profile.get_profile())
    # short style: should not contain double newline follow-up
    assert "I'd love to hear more" not in short_response, "Short style should not have follow-up prompt"
    print(f"✓ Short-style response: '{short_response[:60]}...'")

    # Response style: detailed
    profile.set_response_style('detailed')
    detailed_response = handler.generate_response(emotion_data, profile.get_profile())
    assert "I'd love to hear more" in detailed_response, "Detailed style should have follow-up prompt"
    print("✓ Detailed-style response contains follow-up prompt")

    print("\n✓ RL response feedback test passed")


def test_privacy_export():
    """Test Module 12: Privacy — data export and removal."""
    print("\n" + "="*70)
    print("TEST 17: Privacy & Ethical AI — Data Export (Module 12)")
    print("="*70)

    import json
    from user_profile import UserProfile

    profile = UserProfile('privacy_test')
    profile.set_name("Alice")
    profile.set_age(25)
    profile.set_occupation("Student")
    profile.set_password("SecurePass99!")

    # Simulate what the UI does: export profile without password_hash / salt
    profile_data = profile.get_profile()
    export_data = {
        k: str(v) if not isinstance(v, (str, int, float, list, dict, bool, type(None))) else v
        for k, v in profile_data.items()
        if k not in ('password_hash', 'salt')
    }

    # Sensitive fields must be absent
    assert 'password_hash' not in export_data, "password_hash must not be in export"
    assert 'salt' not in export_data, "salt must not be in export"
    print("✓ password_hash and salt excluded from export")

    # Non-sensitive fields must be present
    assert export_data.get('name') == 'Alice'
    assert export_data.get('occupation') == 'Student'
    print("✓ Profile data present in export")

    # Export must be JSON-serialisable
    json_str = json.dumps(export_data, default=str)
    assert isinstance(json_str, str) and len(json_str) > 10
    print("✓ Export is valid JSON")

    # remove_password clears credentials
    profile.remove_password()
    assert profile.get_profile()['password_hash'] is None
    assert not profile.get_profile()['security_enabled']
    print("✓ remove_password clears credentials")

    print("\n✓ Privacy & data export test passed")
