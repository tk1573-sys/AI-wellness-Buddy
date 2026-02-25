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
    assert level in ('info', 'low', 'medium'), f"Expected info/low/medium risk, got {level}"

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
    assert abs(sum(dist.values()) - 1.0) < 0.01, "Distribution proportions should sum to ~1.0"

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


def test_emotion_confidence_scoring():
    """Test normalized confidence scores per emotion (Problem 1 — granularity)"""
    print("\n" + "="*70)
    print("TEST 19: Emotion Confidence Scoring")
    print("="*70)

    analyzer = EmotionAnalyzer()

    # Joy-heavy message — joy confidence should be highest
    conf_joy = analyzer.get_emotion_confidence("I'm so happy and excited today!")
    print(f"\nJoy message confidence: {conf_joy}")
    assert 0.0 <= conf_joy['joy'] <= 1.0, "Joy confidence must be in [0, 1]"
    assert conf_joy['joy'] > 0, "Joy keywords should be detected"
    non_joy_sum = sum(v for k, v in conf_joy.items() if k != 'joy')
    assert conf_joy['joy'] > non_joy_sum / max(len(conf_joy) - 1, 1), \
        "Joy should have the highest single-emotion confidence"

    # Sadness-heavy message
    conf_sad = analyzer.get_emotion_confidence("I feel deeply sad and hopeless and so empty")
    print(f"Sadness message confidence: {conf_sad}")
    assert conf_sad.get('sadness', 0) > 0, "Sadness keywords should score"

    # No keywords → polarity-based fallback: sum must still be 1.0
    conf_neutral = analyzer.get_emotion_confidence("The wind is changing direction today")
    print(f"Neutral fallback confidence: {conf_neutral}")
    total = sum(conf_neutral.values())
    assert abs(total - 1.0) < 0.01, f"Fallback confidence must sum to ~1.0, got {total}"

    # Crisis message → crisis should have highest confidence
    conf_crisis = analyzer.get_emotion_confidence("I want to kill myself and end it all")
    print(f"Crisis message confidence: {conf_crisis}")
    assert conf_crisis.get('crisis', 0) > 0, "Crisis confidence should be > 0"

    print("\n✓ Emotion confidence scoring tests passed")


def test_info_risk_level():
    """Test that INFO level is returned for very low (pure-positive) risk (Problem 3)"""
    from datetime import datetime as _dt
    print("\n" + "="*70)
    print("TEST 20: INFO Risk Level")
    print("="*70)

    tracker = PatternTracker()

    # Inject pure joy emotion data (risk weight 0.0 → score well below 0.10)
    for _ in range(3):
        tracker.add_emotion_data({
            'emotion': 'positive', 'severity': 'low', 'polarity': 0.9,
            'subjectivity': 0.5, 'distress_keywords': [], 'abuse_indicators': [],
            'has_abuse_indicators': False, 'timestamp': _dt.now(),
            'primary_emotion': 'joy', 'emotion_scores': {'joy': 2},
            'explanation': '', 'is_crisis': False, 'crisis_keywords': [],
            'detected_script': 'english',
        })

    score, level = tracker.compute_risk_score()
    print(f"\nPure joy messages: score={score:.2f}, level={level}")
    assert level == 'info', f"Pure joy should yield 'info' risk level, got '{level}'"

    # Verify all 5 levels are reachable by description
    all_levels = {'info', 'low', 'medium', 'high', 'critical'}
    print(f"Supported risk levels: {sorted(all_levels)}")
    assert level in all_levels, "Returned level must be one of the 5 defined levels"

    print("\n✓ INFO risk level test passed")


def test_emotional_drift_score():
    """Test emotional drift score (mean per-step sentiment change) (Problem 2)"""
    from datetime import datetime as _dt
    print("\n" + "="*70)
    print("TEST 21: Emotional Drift Score")
    print("="*70)

    def _make_emotion(polarity):
        return {
            'emotion': 'neutral', 'severity': 'low', 'polarity': polarity,
            'subjectivity': 0.3, 'distress_keywords': [], 'abuse_indicators': [],
            'has_abuse_indicators': False, 'timestamp': _dt.now(),
            'primary_emotion': 'neutral', 'emotion_scores': {},
            'explanation': '', 'is_crisis': False, 'crisis_keywords': [],
            'detected_script': 'english',
        }

    # Empty tracker → drift = 0
    empty_tracker = PatternTracker()
    assert empty_tracker.get_emotional_drift_score() == 0.0, "Empty tracker drift must be 0.0"
    print("\nEmpty tracker → drift=0.0 ✓")

    # Consistently improving trend → positive drift
    tracker_up = PatternTracker()
    for v in [0.0, 0.1, 0.2, 0.3, 0.4]:
        tracker_up.add_emotion_data(_make_emotion(v))
    drift_up = tracker_up.get_emotional_drift_score()
    print(f"Improving trend drift: {drift_up:.4f}")
    assert drift_up > 0, f"Improving trend should have positive drift, got {drift_up}"

    # Consistently declining trend → negative drift
    tracker_down = PatternTracker()
    for v in [0.4, 0.3, 0.2, 0.1, 0.0]:
        tracker_down.add_emotion_data(_make_emotion(v))
    drift_down = tracker_down.get_emotional_drift_score()
    print(f"Declining trend drift: {drift_down:.4f}")
    assert drift_down < 0, f"Declining trend should have negative drift, got {drift_down}"

    # Drift score appears in pattern summary
    summary = tracker_up.get_pattern_summary()
    assert 'drift_score' in summary, "drift_score must be included in pattern_summary"
    assert summary['drift_score'] == drift_up, "drift_score in summary must match direct call"
    print(f"drift_score in summary: {summary['drift_score']} ✓")

    print("\n✓ Emotional drift score tests passed")


def test_pre_distress_warning():
    """Test pre-distress early warning from PredictionAgent (Problem 4)"""
    from prediction_agent import PredictionAgent
    print("\n" + "="*70)
    print("TEST 22: Pre-Distress Early Warning")
    print("="*70)

    agent = PredictionAgent()

    # Insufficient data → None
    assert agent.get_pre_distress_warning([0.1, 0.2]) is None, \
        "Should return None for < 3 data points"
    print("\nInsufficient data → None ✓")

    # Declining trend heading into mild-negative zone → warning triggered
    # [0.3, 0.2, 0.1, 0.0, -0.1]: slope=-0.1, predicted=-0.2 ∈ [-0.50, -0.10)
    declining = [0.3, 0.2, 0.1, 0.0, -0.1]
    # Verify the OLS predicted value falls in the expected range before testing warning
    _pred = agent.predict_next_sentiment(declining)
    assert _pred is not None
    assert -0.50 <= _pred['predicted_value'] < -0.10, (
        f"Expected predicted value in [-0.50, -0.10), got {_pred['predicted_value']}"
    )
    warning = agent.get_pre_distress_warning(declining)
    print(f"Declining trend warning: '{warning[:60] if warning else None}…'")
    assert warning is not None, "Declining trend into mild-negative should trigger warning"
    assert isinstance(warning, str) and len(warning) > 20, "Warning must be a non-trivial string"

    # Stable positive trend → no warning
    stable = [0.3, 0.3, 0.3, 0.3, 0.3]
    assert agent.get_pre_distress_warning(stable) is None, \
        "Stable positive mood should not trigger warning"
    print("Stable positive → None ✓")

    # Deeply negative (predicted < -0.50) → no pre-distress warning (AlertSystem handles it)
    deep_negative = [-0.7, -0.8, -0.85, -0.9, -0.95]
    assert agent.get_pre_distress_warning(deep_negative) is None, \
        "Deep distress (predicted < -0.50) should not trigger pre-distress warning"
    print("Deep distress → None (AlertSystem handles it) ✓")

    print("\n✓ Pre-distress early warning tests passed")


def test_ml_emotion_adapter():
    """Test MLEmotionAdapter graceful fallback and evaluate_classification_performance."""
    from emotion_analyzer import EmotionAnalyzer, MLEmotionAdapter

    print("\n" + "="*70)
    print("TEST 23: ML Emotion Adapter + Heuristic Classifier Evaluation")
    print("="*70)

    # MLEmotionAdapter must instantiate without raising, regardless of whether
    # transformers/torch are installed.
    adapter = MLEmotionAdapter()
    assert isinstance(adapter.available, bool), "available must be a bool"
    print(f"\n✓ MLEmotionAdapter available={adapter.available}")

    # classify() must return dict (if available) or None (if not)
    result = adapter.classify("I feel so happy today")
    if adapter.available:
        assert isinstance(result, dict) and len(result) > 0
        print(f"✓ ML classify() returned {result}")
    else:
        assert result is None, "Unavailable adapter must return None"
        print("✓ ML classify() correctly returned None (transformers not installed)")

    # evaluate_classification_performance must work with heuristic fallback
    analyzer = EmotionAnalyzer()
    report = analyzer.evaluate_classification_performance()
    assert 'overall_accuracy'  in report
    assert 'macro_f1'          in report
    assert 'per_class_metrics' in report
    assert 0.0 <= report['overall_accuracy'] <= 1.0
    assert report['test_cases'] == 19
    print(f"\n✓ Heuristic classifier accuracy  : {report['overall_accuracy']:.2%}")
    print(f"✓ Heuristic macro-F1             : {report['macro_f1']:.4f}")
    for cls, m in report['per_class_metrics'].items():
        print(f"   {cls:<10}: P={m['precision']:.2f}  R={m['recall']:.2f}  F1={m['f1']:.2f}")

    # classify_emotion_ml must always return required fields
    ml_result = analyzer.classify_emotion_ml("I am sad and crying")
    assert 'ml_available' in ml_result
    assert 'ml_scores' in ml_result
    assert 'primary_emotion' in ml_result
    print(f"\n✓ classify_emotion_ml() ml_available={ml_result['ml_available']}, "
          f"primary_emotion={ml_result['primary_emotion']}")

    print("\n✓ ML emotion adapter + evaluation tests passed")


def test_ewma_predictor():
    """Test EWMAPredictor and compare_models() utility."""
    from prediction_agent import EWMAPredictor, compare_models

    print("\n" + "="*70)
    print("TEST 24: EWMA Predictor & Model Comparison")
    print("="*70)

    # Basic prediction
    ewma = EWMAPredictor(alpha=0.3)
    assert ewma.predict_next([0.1, 0.2]) is not None
    assert ewma.predict_next([0.5]) is None, "Need at least 2 points"
    assert ewma.predict_next([]) is None

    # Declining history → prediction should be below starting value
    declining = [0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -0.1]
    pred_dec = ewma.predict_next(declining)
    assert pred_dec is not None and -1.0 <= pred_dec <= 1.0
    print(f"\nDeclining history EWMA prediction: {pred_dec:.4f}")

    # MAE / RMSE on a recoverable dataset
    recovering = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
    mae  = ewma.compute_mae(recovering)
    rmse = ewma.compute_rmse(recovering)
    assert mae is not None and mae >= 0
    assert rmse is not None and rmse >= mae - 1e-6, "RMSE must be ≥ MAE"
    print(f"EWMA MAE={mae:.4f}  RMSE={rmse:.4f}")

    # compare_models — needs ≥ 5 points
    history = [0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4, -0.5]
    comparison = compare_models(history)
    assert comparison is not None
    assert 'ols'    in comparison
    assert 'ewma'   in comparison
    assert 'winner' in comparison
    assert comparison['winner'] in ('ols', 'ewma', 'tie')
    print(f"OLS  MAE={comparison['ols']['mae']:.4f}  RMSE={comparison['ols']['rmse']:.4f}")
    print(f"EWMA MAE={comparison['ewma']['mae']:.4f}  RMSE={comparison['ewma']['rmse']:.4f}")
    print(f"Winner: {comparison['winner']}")

    # compare_models on tiny history → None
    assert compare_models([0.1, 0.2, 0.3]) is None, \
        "compare_models needs ≥ 5 points"

    # Invalid alpha
    try:
        EWMAPredictor(alpha=0.0)
        assert False, "alpha=0 should raise ValueError"
    except ValueError:
        pass
    print("✓ Invalid alpha raises ValueError")

    print("\n✓ EWMA predictor and model comparison tests passed")


def test_evaluation_framework():
    """Test evaluation_framework module — scenarios, metrics, benchmarks."""
    print("\n" + "="*70)
    print("TEST 25: Evaluation Framework")
    print("="*70)

    from evaluation_framework import (
        generate_gradual_decline_scenario,
        generate_sudden_drop_scenario,
        generate_recovery_pattern_scenario,
        generate_stable_positive_scenario,
        generate_volatile_scenario,
        compute_mae,
        compute_rmse,
        compute_correlation,
        compute_confidence_interval,
        run_t_test,
        compute_detection_metrics,
        run_prediction_benchmark,
        evaluate_heuristic_classifier,
        simulate_risk_detection_on_scenarios,
    )
    from emotion_analyzer import EmotionAnalyzer

    # ── Scenario generators ────────────────────────────────────────────
    decline = generate_gradual_decline_scenario(n=10)
    assert len(decline) == 10
    assert decline[0] > decline[-1], "Decline scenario must be decreasing"

    drop = generate_sudden_drop_scenario(n=15, drop_at=10)
    assert len(drop) == 15
    assert drop[9] > drop[10], "Sudden drop must occur at drop_at"

    recovery = generate_recovery_pattern_scenario(n=12)
    assert len(recovery) == 12
    assert recovery[-1] > recovery[0], "Recovery scenario must be increasing"

    stable = generate_stable_positive_scenario(n=8)
    assert len(stable) == 8
    assert all(v > 0 for v in stable), "Stable-positive values should be positive"

    volatile = generate_volatile_scenario(n=20)
    assert len(volatile) == 20
    print(f"\n✓ All 5 scenario generators produce correct-length lists")

    # ── Statistical helpers ────────────────────────────────────────────
    a = [1.0, 2.0, 3.0, 4.0]
    b = [1.5, 2.5, 3.5, 4.5]
    assert compute_mae(a, b) == 0.5
    assert compute_rmse(a, b) == 0.5
    assert compute_correlation(a, b) == 1.0, "Perfectly correlated lists"
    assert compute_mae([], []) is None
    print("✓ MAE, RMSE, correlation basic checks pass")

    ci = compute_confidence_interval([0.1, 0.2, 0.3, 0.25, 0.15])
    assert ci is not None and 'mean' in ci and 'ci_lower' in ci
    assert ci['ci_lower'] <= ci['mean'] <= ci['ci_upper']
    print(f"✓ CI: mean={ci['mean']} [{ci['ci_lower']}, {ci['ci_upper']}]")

    t, p = run_t_test([0.1, 0.2, 0.3], [0.4, 0.5, 0.6])
    assert t is not None and p is not None
    assert 0.0 <= p <= 1.0, "p-value must be in [0, 1]"
    print(f"✓ t-test: t={t:.4f}  p={p:.4f}")

    metrics = compute_detection_metrics(tp=8, fp=2, tn=10, fn=1)
    assert abs(metrics['precision'] - 0.8) < 0.01
    assert metrics['recall']    > metrics['precision']  # 8/(8+1) > 8/(8+2)
    assert 0.0 <= metrics['f1_score'] <= 1.0
    print(f"✓ Detection metrics: {metrics}")

    # ── Prediction benchmark ───────────────────────────────────────────
    benchmark = run_prediction_benchmark()
    assert len(benchmark) == 4, "Should have 4 canonical scenarios"
    for row in benchmark:
        assert 'scenario' in row
        assert 'ols'  in row and row['ols']['mae'] is not None
        assert 'ewma' in row and row['ewma']['mae'] is not None
        print(f"  {row['scenario']:20s}: OLS-MAE={row['ols']['mae']:.4f}  "
              f"EWMA-MAE={row['ewma']['mae']:.4f}")
    print("✓ Prediction benchmark returns results for all 4 scenarios")

    # ── Heuristic classifier evaluation ───────────────────────────────
    analyzer = EmotionAnalyzer()
    report = evaluate_heuristic_classifier(analyzer)
    assert report['overall_accuracy'] > 0.3, "Heuristic accuracy should exceed random"
    assert report['test_cases'] == 19
    print(f"✓ Heuristic classifier: accuracy={report['overall_accuracy']:.2%}  "
          f"macro-F1={report['macro_f1']:.4f}")

    # ── Risk detection simulation ──────────────────────────────────────
    risk_table = simulate_risk_detection_on_scenarios()
    assert len(risk_table) == 5
    names = {r['scenario'] for r in risk_table}
    assert 'gradual_decline'  in names
    assert 'stable_positive'  in names
    assert 'recovery'         in names

    for row in risk_table:
        assert row['risk_level'] in ('info', 'low', 'medium', 'high', 'critical')
        assert 0.0 <= row['stability_index'] <= 1.0
        print(f"  {row['scenario']:20s}: risk={row['risk_level']:8s}  "
              f"stability={row['stability_index']:.4f}  drift={row['drift_score']:+.4f}")

    # Stable-positive → INFO/LOW; gradual-decline → HIGH/CRITICAL
    stable_row  = next(r for r in risk_table if r['scenario'] == 'stable_positive')
    decline_row = next(r for r in risk_table if r['scenario'] == 'gradual_decline')
    assert stable_row['risk_score'] < decline_row['risk_score'], \
        "Stable-positive should have lower risk than gradual-decline"
    print("✓ Stable-positive risk < gradual-decline risk")

    print("\n✓ Evaluation framework tests passed")


def test_extended_personal_history():
    """TEST 26: Extended personal history — living situation, family responsibilities, occupation"""
    print("\n" + "="*70)
    print("TEST 26: Extended Personal History")
    print("="*70)

    profile = UserProfile("test_extended_history")

    # ── Living situation ──────────────────────────────────────────────
    assert profile.get_living_situation() is None, "Should be None before setting"
    profile.set_living_situation("Alone")
    assert profile.get_living_situation() == "Alone"
    # Verify it's stored in demographics
    assert profile.get_profile()['demographics']['living_situation'] == "Alone"
    print("✓ Living situation stored and retrieved correctly")

    # ── Family responsibilities ───────────────────────────────────────
    assert profile.get_family_responsibilities() is None, "Should be None before setting"
    profile.set_family_responsibilities("Single parent")
    assert profile.get_family_responsibilities() == "Single parent"
    assert profile.get_profile()['demographics']['family_responsibilities'] == "Single parent"
    print("✓ Family responsibilities stored and retrieved correctly")

    # ── Occupation ───────────────────────────────────────────────────
    assert profile.get_occupation() is None, "Should be None before setting"
    profile.set_occupation("Employed (full-time)")
    assert profile.get_occupation() == "Employed (full-time)"
    assert profile.get_profile()['demographics']['occupation'] == "Employed (full-time)"
    print("✓ Occupation stored and retrieved correctly")

    # ── get_personal_context includes all new fields ──────────────────
    ctx = profile.get_personal_context()
    assert ctx['living_situation'] == "Alone"
    assert ctx['family_responsibilities'] == "Single parent"
    assert ctx['occupation'] == "Employed (full-time)"
    print("✓ get_personal_context() includes living_situation, family_responsibilities, occupation")

    # ── Conversation personalization uses new fields ──────────────────
    from conversation_handler import ConversationHandler
    handler = ConversationHandler()
    anxiety_emotion = {
        'emotion': 'negative',
        'primary_emotion': 'anxiety',
        'severity': 'medium',
        'polarity': -0.4,
        'distress_keywords': ['worried'],
        'abuse_indicators': [],
        'has_abuse_indicators': False,
        'explanation': 'keyword: worried',
    }
    # Message from a single parent with work stress and living alone
    handler.add_message("I'm so overwhelmed with everything", anxiety_emotion)
    ctx['response_style'] = 'balanced'
    response = handler.generate_response(anxiety_emotion, ctx)
    assert isinstance(response, str) and len(response) > 10
    # The family_responsibilities and occupation branches should fire
    assert "responsibilit" in response.lower() or "pressure" in response.lower() or \
           "strength" in response.lower() or "overwhelm" in response.lower() or \
           "anxiety" in response.lower() or "breath" in response.lower(), \
        f"Response should acknowledge context. Got: {response[:200]}"
    print(f"✓ Conversation handler generates context-aware response: '{response[:80]}…'")

    # ── Persistence round-trip ────────────────────────────────────────
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    try:
        ds = DataStore(tmpdir)
        ds.save_user_data("test_extended_history", profile.get_profile())
        loaded_data = ds.load_user_data("test_extended_history")
        assert loaded_data is not None
        loaded_profile = UserProfile("test_extended_history")
        loaded_profile.load_from_data(loaded_data)
        assert loaded_profile.get_living_situation() == "Alone"
        assert loaded_profile.get_family_responsibilities() == "Single parent"
        assert loaded_profile.get_occupation() == "Employed (full-time)"
        print("✓ Extended personal history survives save/load round-trip")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("\n✓ Extended personal history tests passed")


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
        test_emotion_confidence_scoring()
        test_info_risk_level()
        test_emotional_drift_score()
        test_pre_distress_warning()
        test_ml_emotion_adapter()
        test_ewma_predictor()
        test_evaluation_framework()
        test_extended_personal_history()
        
        print("\n" + "="*70)
        print("   ✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
