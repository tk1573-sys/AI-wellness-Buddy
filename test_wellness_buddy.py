"""
Simple test script for AI Wellness Buddy
Demonstrates core functionality without requiring interactive input
"""

from emotion_analyzer import EmotionAnalyzer
from pattern_tracker import PatternTracker
from alert_system import AlertSystem
from conversation_handler import ConversationHandler
from user_profile import UserProfile


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
        profile = UserProfile()
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
    
    profile = UserProfile()
    profile.set_gender('female')
    profile.set_relationship_status('married')
    
    print(f"\nUser Profile Created:")
    print(f"  Gender: {profile.get_profile()['gender']}")
    print(f"  Is female: {profile.is_female()}")
    print(f"  Needs women support: {profile.needs_women_support()}")


def test_full_workflow():
    """Test complete workflow with abuse detection"""
    print("\n" + "="*70)
    print("TEST 6: Full Workflow - Abuse Detection & Alert")
    print("="*70)
    
    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()
    alert_system = AlertSystem()
    handler = ConversationHandler()
    profile = UserProfile()
    profile.set_gender('female')
    
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
            alert_message = alert_system.format_alert_message(alert)
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
