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


def test_multi_emotion_detection():
    """Test fine-grained multi-emotion detection and XAI explanation"""
    print("\n" + "="*70)
    print("TEST 10: Multi-Emotion Detection & XAI")
    print("="*70)

    analyzer = EmotionAnalyzer()

    cases = [
        ("I'm so happy and excited about life!", 'joy'),
        ("I feel deeply sad and empty inside", 'sadness'),
        ("I'm furious and so angry at this situation", 'anger'),
        ("I'm really scared and terrified of what might happen", 'fear'),
        ("I feel so anxious and overwhelmed by everything", 'anxiety'),
        ("I want to kill myself and end it all", 'crisis'),
    ]

    for text, expected_primary in cases:
        result = analyzer.classify_emotion(text)
        primary = result['primary_emotion']
        explanation = result['explanation']
        print(f"\nText: '{text}'")
        print(f"  Primary emotion: {primary}  (expected: {expected_primary})")
        print(f"  Coarse emotion:  {result['emotion']}")
        print(f"  Explanation:     {explanation}")
        assert primary == expected_primary, f"Expected '{expected_primary}', got '{primary}'"
        assert explanation, "Explanation should not be empty"

    # Crisis flag
    crisis_result = analyzer.classify_emotion("I want to kill myself")
    assert crisis_result['is_crisis'] is True, "Crisis flag should be True"
    assert crisis_result['crisis_keywords'], "Crisis keywords should be detected"

    print("\n✓ Multi-emotion detection tests passed")


def test_risk_scoring():
    """Test formula-based risk scoring system"""
    print("\n" + "="*70)
    print("TEST 11: Risk Scoring System")
    print("="*70)

    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()

    # Low risk — positive messages
    for msg in ["I'm happy today", "Life is great", "Feeling wonderful"]:
        tracker.add_emotion_data(analyzer.classify_emotion(msg))

    score, level = tracker.compute_risk_score()
    print(f"\nAfter positive messages: score={score:.2f}, level={level}")
    assert level in ('low', 'medium'), f"Expected low/medium risk, got {level}"

    # Build up to high risk
    tracker2 = PatternTracker()
    for msg in ["I feel so sad and hopeless", "I'm scared and anxious",
                "I feel trapped and afraid", "Everything is terrible"]:
        tracker2.add_emotion_data(analyzer.classify_emotion(msg))

    score2, level2 = tracker2.compute_risk_score()
    print(f"After distress messages: score={score2:.2f}, level={level2}")
    assert level2 in ('medium', 'high', 'critical'), f"Expected elevated risk, got {level2}"

    # Critical risk — crisis message
    tracker3 = PatternTracker()
    tracker3.add_emotion_data(analyzer.classify_emotion("I want to kill myself"))
    score3, level3 = tracker3.compute_risk_score()
    print(f"After crisis message: score={score3:.2f}, level={level3}")
    assert level3 in ('high', 'critical'), f"Expected high/critical, got {level3}"

    print("\n✓ Risk scoring tests passed")


def test_trend_modeling():
    """Test moving average, volatility, and stability index"""
    print("\n" + "="*70)
    print("TEST 12: Emotional Trend Modeling")
    print("="*70)

    from pattern_tracker import PatternTracker
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    tracker = PatternTracker()

    messages = [
        "I'm so happy today",
        "Feeling a bit down",
        "Great news!",
        "I'm a bit worried",
        "Things are looking up",
    ]
    for msg in messages:
        tracker.add_emotion_data(analyzer.classify_emotion(msg))

    ma = tracker.get_moving_average(window=3)
    print(f"\nMoving average (window=3): {[round(v, 3) for v in ma]}")
    assert len(ma) == len(messages) - 3 + 1, "Moving average length incorrect"

    volatility, stability = tracker.get_volatility_and_stability()
    print(f"Volatility: {volatility:.3f}, Stability index: {stability:.3f}")
    assert 0.0 <= volatility <= 1.0, "Volatility out of range"
    assert 0.0 <= stability <= 1.0, "Stability out of range"
    assert abs(volatility + stability - 1.0) < 0.001, "Volatility + Stability should equal 1"

    dist = tracker.get_emotion_distribution()
    print(f"Emotion distribution: {dist}")
    assert isinstance(dist, dict), "Distribution should be a dict"
    assert sum(dist.values()) == len(messages), "Distribution counts should sum to message count"

    print("\n✓ Trend modeling tests passed")


def test_prediction_agent():
    """Test OLS prediction agent"""
    print("\n" + "="*70)
    print("TEST 13: Prediction Agent")
    print("="*70)

    from prediction_agent import PredictionAgent

    agent = PredictionAgent()

    # Insufficient data
    result = agent.predict_next_sentiment([0.1, 0.2])
    assert result is None, "Should return None for < 3 data points"
    print("\nInsufficient data → None (correct)")

    # Improving trend
    improving = [0.0, 0.1, 0.2, 0.3, 0.4]
    result_imp = agent.predict_next_sentiment(improving)
    print(f"Improving trend prediction: {result_imp}")
    assert result_imp is not None
    assert result_imp['predicted_value'] > 0.3, "Should predict higher value on upward trend"
    assert result_imp['trend_slope'] > 0, "Slope should be positive"

    # Declining trend
    declining = [0.4, 0.3, 0.2, 0.1, 0.0]
    result_dec = agent.predict_next_sentiment(declining)
    print(f"Declining trend prediction: {result_dec}")
    assert result_dec is not None
    assert result_dec['trend_slope'] < 0, "Slope should be negative"

    # Risk escalation
    risk_hist = [0.1, 0.2, 0.35, 0.5, 0.65]
    esc = agent.predict_risk_escalation(risk_hist)
    print(f"Risk escalation prediction: {esc}")
    assert esc is not None
    assert 'will_escalate' in esc
    assert 'recommendation' in esc

    print("\n✓ Prediction agent tests passed")


def test_gamification():
    """Test mood streak and wellness badges"""
    print("\n" + "="*70)
    print("TEST 14: Gamification — Mood Streak & Badges")
    print("="*70)

    profile = UserProfile('badge_test')
    profile.set_gender('female')

    # Test mood streak
    profile.update_mood_streak(0.5)   # positive
    profile.update_mood_streak(0.3)   # positive
    profile.update_mood_streak(-0.2)  # negative — resets streak
    assert profile.get_mood_streak() == 0, "Streak should reset on negative mood"

    profile.update_mood_streak(0.1)   # positive
    profile.update_mood_streak(0.2)   # positive
    profile.update_mood_streak(0.4)   # positive
    assert profile.get_mood_streak() == 3, "Streak should be 3"
    print(f"\nMood streak: {profile.get_mood_streak()} (expected 3)")

    # Response style
    profile.set_response_style('short')
    assert profile.get_response_style() == 'short'
    profile.set_response_style('invalid')  # should be ignored
    assert profile.get_response_style() == 'short', "Invalid style should be ignored"
    print(f"Response style: {profile.get_response_style()} (expected short)")

    # Badge awarding
    newly = profile.award_badge('first_step')
    assert newly is True, "Badge should be awarded first time"
    already = profile.award_badge('first_step')
    assert already is False, "Badge should not be awarded twice"

    profile.add_trusted_contact('Friend', 'best friend')
    profile.add_trauma_history('test trauma')
    awarded = profile.check_and_award_badges(session_avg_sentiment=0.3)
    print(f"Awarded badges: {awarded}")
    earned_ids = profile.get_badges()
    assert 'self_aware' in earned_ids, "self_aware badge should be awarded"
    assert 'connected' in earned_ids, "connected badge should be awarded"

    display = profile.get_badge_display()
    print(f"Badge display: {display}")
    assert len(display) > 0, "Should have at least one badge"

    print("\n✓ Gamification tests passed")


def test_bilingual_language_detection():
    """Test language detection: English, Tamil Unicode, and Tanglish."""
    from language_handler import LanguageHandler

    lh = LanguageHandler()

    # English
    assert lh.detect_script("I'm feeling very sad today") == 'english'
    print("✓ English detected correctly")

    # Tamil Unicode
    assert lh.detect_script("நான் மிகவும் துக்கமாக இருக்கிறேன்") == 'tamil'
    print("✓ Tamil Unicode detected correctly")

    # Tanglish
    assert lh.detect_script("naan romba kedachu feel panren") == 'tanglish'
    print("✓ Tanglish detected correctly")

    # Tanglish crisis
    assert lh.detect_script("ennaku saaga poiren theriuma") == 'tanglish'
    print("✓ Tanglish crisis script detected correctly")

    print("\n✓ Bilingual language detection tests passed")


def test_tanglish_emotion_detection():
    """Test that Tanglish and Tamil keyword-based emotions are detected correctly."""
    from emotion_analyzer import EmotionAnalyzer
    from language_handler import LanguageHandler

    analyzer = EmotionAnalyzer()
    lh = LanguageHandler()

    # Tanglish sadness
    result = analyzer.classify_emotion("naan romba kedachu feel panren, valikudu")
    assert result['detected_script'] == 'tanglish', "Should detect Tanglish script"
    assert result['primary_emotion'] in ('sadness', 'anxiety', 'fear', 'anger'), (
        f"Tanglish sad message should be a negative emotion, got {result['primary_emotion']}"
    )
    print(f"✓ Tanglish sadness → primary_emotion={result['primary_emotion']}")

    # Tanglish joy
    result_joy = analyzer.classify_emotion("naan romba santhosham, super ah irukken")
    assert result_joy['detected_script'] == 'tanglish'
    assert result_joy['primary_emotion'] == 'joy', (
        f"Tanglish joy message should be 'joy', got {result_joy['primary_emotion']}"
    )
    print(f"✓ Tanglish joy → primary_emotion={result_joy['primary_emotion']}")

    # Tamil Unicode sadness
    result_ta = analyzer.classify_emotion("நான் மிகவும் துக்கமாக இருக்கிறேன்")
    assert result_ta['detected_script'] == 'tamil', "Should detect Tamil Unicode"
    print(f"✓ Tamil Unicode sadness → detected_script={result_ta['detected_script']}, "
          f"primary_emotion={result_ta['primary_emotion']}")

    # Tanglish language handler keywords
    tanglish_kws = lh.get_tanglish_keywords_for_emotion('sadness')
    assert len(tanglish_kws) > 0, "Should have Tanglish sadness keywords"
    assert 'kedachu' in tanglish_kws
    print(f"✓ Tanglish keyword list for 'sadness' has {len(tanglish_kws)} entries")

    print("\n✓ Tanglish emotion detection tests passed")


def test_bilingual_responses():
    """Test that language-aware responses are generated correctly."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer
    from user_profile import UserProfile

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    # Tamil response
    profile_ta = UserProfile('test_tamil_user')
    profile_ta.set_language_preference('tamil')
    ctx_ta = profile_ta.get_personal_context()
    ctx_ta['response_style'] = 'balanced'

    emotion_data = analyzer.classify_emotion("நான் மிகவும் துக்கமாக இருக்கிறேன்")
    emotion_data['primary_emotion'] = 'sadness'  # force for test
    handler.add_message("test", emotion_data)
    response_ta = handler.generate_response(emotion_data, ctx_ta)
    assert isinstance(response_ta, str) and len(response_ta) > 5
    print(f"✓ Tamil response generated: '{response_ta[:80]}…'")

    # Bilingual response
    profile_bi = UserProfile('test_bilingual_user')
    profile_bi.set_language_preference('bilingual')
    ctx_bi = profile_bi.get_personal_context()
    ctx_bi['response_style'] = 'balanced'

    response_bi = handler.generate_response(emotion_data, ctx_bi)
    assert isinstance(response_bi, str) and len(response_bi) > 5
    print(f"✓ Bilingual response generated: '{response_bi[:80]}…'")

    # English response (default)
    profile_en = UserProfile('test_english_user')
    ctx_en = profile_en.get_personal_context()
    ctx_en['response_style'] = 'balanced'
    response_en = handler.generate_response(emotion_data, ctx_en)
    assert isinstance(response_en, str) and len(response_en) > 5
    print(f"✓ English response generated: '{response_en[:80]}…'")

    # Verify language_preference is stored/retrieved correctly
    profile_ta.set_language_preference('tamil')
    assert profile_ta.get_language_preference() == 'tamil'
    profile_ta.set_language_preference('invalid')  # silently ignored: 'invalid' not in SUPPORTED_LANGUAGES
    assert profile_ta.get_language_preference() == 'tamil', "Unsupported language must leave preference unchanged"
    print("✓ Language preference set/get/validation works")

    print("\n✓ Bilingual response tests passed")


def test_voice_handler():
    """Test VoiceHandler: TTS availability and _strip_markdown helper."""
    from voice_handler import VoiceHandler, _strip_markdown

    vh = VoiceHandler()
    # Availability flags are booleans
    assert isinstance(vh.tts_available, bool)
    assert isinstance(vh.stt_available, bool)
    print(f"✓ VoiceHandler: tts_available={vh.tts_available}, stt_available={vh.stt_available}")

    # Markdown stripping
    raw = "I'm **really** glad! 😊\n\n_(Analysis: Detected 'joy' due to keywords: happy)_"
    clean = _strip_markdown(raw)
    assert '**' not in clean, "Bold markers should be removed"
    assert '_(Analysis:' not in clean, "XAI annotation should be removed"
    assert 'glad' in clean, "Core text should be preserved"
    print(f"✓ _strip_markdown works: '{clean[:60]}…'")

    # TTS with empty input returns None
    result = vh.text_to_speech("", 'english')
    assert result is None, "Empty text TTS should return None"
    print("✓ TTS with empty text returns None")

    # STT with empty bytes returns ''
    result_stt = vh.transcribe_audio(b'', 'english')
    assert result_stt == '', "Empty audio STT should return ''"
    print("✓ STT with empty bytes returns empty string")

    print("\n✓ Voice handler tests passed")


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
        test_multi_emotion_detection()
        test_risk_scoring()
        test_trend_modeling()
        test_prediction_agent()
        test_gamification()
        test_bilingual_language_detection()
        test_tanglish_emotion_detection()
        test_bilingual_responses()
        test_voice_handler()
        
        print("\n" + "="*70)
        print("   ✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
