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


def test_personal_history_profile():
    """Test new personal history fields on UserProfile"""
    print("\n" + "="*70)
    print("TEST 8: Personal History Profile")
    print("="*70)

    profile = UserProfile('test_personal')
    profile.set_gender('female')
    profile.set_relationship_status('divorced')
    profile.set_family_background('Grew up in a single-parent household')
    profile.add_trauma_history('Lost a parent at a young age')
    profile.add_trauma_history('Ended an abusive relationship in 2022')
    profile.add_personal_trigger('abandonment')
    profile.add_personal_trigger('violence')
    profile.add_personal_trigger('violence')  # duplicate — should be ignored

    print(f"\nRelationship status: {profile.get_profile()['demographics']['relationship_status']}")
    print(f"Family background: {profile.get_profile()['demographics']['family_background']}")
    print(f"Trauma records: {len(profile.get_trauma_history())}")
    for t in profile.get_trauma_history():
        print(f"  • {t['description']}")
    print(f"Personal triggers: {profile.get_personal_triggers()}")
    assert len(profile.get_trauma_history()) == 2, "Should have 2 trauma records"
    assert len(profile.get_personal_triggers()) == 2, "Duplicate trigger should not be added"

    ctx = profile.get_personal_context()
    print(f"\nPersonal context: {ctx}")
    assert ctx['has_trauma_history'] is True
    assert ctx['trauma_count'] == 2
    assert ctx['marital_status'] == 'divorced'
    assert 'abandonment' in ctx['personal_triggers']
    print("\n✓ Personal history profile tests passed")


def test_personalized_responses():
    """Test that generate_response produces context-aware, humanoid responses"""
    print("\n" + "="*70)
    print("TEST 9: Personalized Responses")
    print("="*70)

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    # -- 1. Positive emotion with no context --
    msg = "I had a great day today!"
    emotion = analyzer.classify_emotion(msg)
    handler.add_message(msg, emotion)
    response = handler.generate_response(emotion)
    print(f"\nPositive (no context): {response}")
    assert response, "Response should not be empty"

    # -- 2. Distress with trauma context --
    ctx_trauma = {
        'gender': 'female',
        'marital_status': 'divorced',
        'family_background': 'difficult childhood',
        'has_trauma_history': True,
        'trauma_count': 2,
        'personal_triggers': ['abuse', 'violence'],
        'has_unsafe_family': False,
    }
    msg2 = "I feel completely worthless and hopeless"
    emotion2 = analyzer.classify_emotion(msg2)
    handler.add_message(msg2, emotion2)
    response2 = handler.generate_response(emotion2, ctx_trauma)
    print(f"\nDistress (with trauma context): {response2}")
    assert response2, "Response should not be empty"

    # -- 3. Trigger detection --
    ctx_trigger = {
        'gender': None,
        'marital_status': None,
        'family_background': None,
        'has_trauma_history': False,
        'trauma_count': 0,
        'personal_triggers': ['abuse'],
        'has_unsafe_family': False,
    }
    msg3 = "I experienced abuse in my childhood"
    emotion3 = analyzer.classify_emotion(msg3)
    handler.add_message(msg3, emotion3)
    response3 = handler.generate_response(emotion3, ctx_trigger)
    print(f"\nNegative (trigger detected): {response3}")
    assert 'sensitive' in response3.lower() or 'pace' in response3.lower(), \
        "Response should acknowledge the personal trigger"

    # -- 4. Divorced marital status with medium negative emotion --
    ctx_divorced = {
        'gender': None,
        'marital_status': 'divorced',
        'family_background': None,
        'has_trauma_history': False,
        'trauma_count': 0,
        'personal_triggers': [],
        'has_unsafe_family': False,
    }
    msg4 = "Today has been really hard and I feel empty"
    emotion4 = analyzer.classify_emotion(msg4)
    handler.add_message(msg4, emotion4)
    response4 = handler.generate_response(emotion4, ctx_divorced)
    print(f"\nNegative (divorced context): {response4}")
    assert response4, "Response should not be empty"

    print("\n✓ Personalized response tests passed")


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
        test_personal_history_profile()
        test_personalized_responses()
        
        print("\n" + "="*70)
        print("   ✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
