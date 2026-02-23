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
