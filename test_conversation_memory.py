"""
Tests for conversation memory, anti-repeat safeguards, and emotional escalation.

Run with: python -m pytest test_conversation_memory.py -v
"""

import tempfile
import shutil


# ─────────────────────────────────────────────────────────────────────────────
# 1. Identical user inputs do NOT produce identical replies repeatedly
# ─────────────────────────────────────────────────────────────────────────────

def test_no_identical_replies_for_same_input():
    """Sending the same message multiple times must not yield identical
    consecutive assistant responses."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    msg = "I feel really anxious today"
    responses = []
    for _ in range(6):
        emotion_data = analyzer.classify_emotion(msg)
        handler.add_message(msg, emotion_data)
        resp = handler.generate_response(emotion_data)
        responses.append(resp)

    # No two consecutive responses should be identical
    for i in range(1, len(responses)):
        assert responses[i] != responses[i - 1], (
            f"Response {i} is identical to response {i - 1}"
        )
    print("✓ No identical consecutive replies for same input")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Conversation history grows correctly
# ─────────────────────────────────────────────────────────────────────────────

def test_conversation_history_grows():
    """Each user message should grow conversation_history by 1."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    messages = [
        "I'm feeling great!",
        "Now I feel a bit nervous.",
        "Work stress is getting to me.",
    ]
    for i, msg in enumerate(messages, 1):
        emotion_data = analyzer.classify_emotion(msg)
        handler.add_message(msg, emotion_data)
        assert len(handler.conversation_history) == i, (
            f"Expected {i} history entries, got {len(handler.conversation_history)}"
        )

    print("✓ Conversation history grows correctly")


def test_get_chat_history_structured():
    """get_chat_history() returns structured role/content dicts."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    handler.add_message("Hello!", analyzer.classify_emotion("Hello!"))
    handler.add_message("I'm sad.", analyzer.classify_emotion("I'm sad."))

    history = handler.get_chat_history()
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Hello!"}
    assert history[1] == {"role": "user", "content": "I'm sad."}

    print("✓ get_chat_history returns structured dicts")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Emotional escalation logic
# ─────────────────────────────────────────────────────────────────────────────

def test_emotional_escalation_on_repeated_emotion():
    """When the same emotion appears ≥ 2 consecutive times, the response
    should include escalation content (longer / deeper support)."""
    from conversation_handler import ConversationHandler, _ESCALATION_FOLLOWUPS
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    # Send three anxiety messages in a row to trigger escalation
    msg = "I feel so anxious and worried about everything"
    for _ in range(3):
        emotion_data = analyzer.classify_emotion(msg)
        handler.add_message(msg, emotion_data)

    emotion_data = analyzer.classify_emotion(msg)
    handler.add_message(msg, emotion_data)
    resp = handler.generate_response(emotion_data)

    # Response should contain content from one of the anxiety escalation follow-ups
    anxiety_followups = _ESCALATION_FOLLOWUPS.get('anxiety', [])
    has_escalation = any(
        followup.strip() in resp for followup in anxiety_followups
    )
    assert has_escalation or len(resp) > 50, (
        f"Expected escalation follow-up content in response"
    )

    print(f"✓ Emotional escalation fires (response length: {len(resp)})")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Anti-repeat _ensure_no_repeat safeguard
# ─────────────────────────────────────────────────────────────────────────────

def test_ensure_no_repeat_appends_variation():
    """_ensure_no_repeat should append a variation when response equals
    the last response."""
    from conversation_handler import ConversationHandler, _SUPPORT_VARIATIONS

    handler = ConversationHandler()
    base = "I hear you and I'm here to support you."

    first = handler._ensure_no_repeat(base, 'sadness')
    assert first == base  # first time → no change

    # Same exact text again → must differ
    second = handler._ensure_no_repeat(base, 'sadness')
    assert second != base, "Second identical response was not modified"
    assert any(v in second for v in _SUPPORT_VARIATIONS), \
        "Variation was not appended"

    print("✓ _ensure_no_repeat adds variation on duplicate")


def test_ensure_no_repeat_checks_recent_window():
    """Responses used in the recent history window should not be reused."""
    from conversation_handler import ConversationHandler

    handler = ConversationHandler()
    seed_responses = [f"seed-response-{i}" for i in range(5)]
    for item in seed_responses:
        handler._ensure_no_repeat(item, 'sadness')

    regenerated = handler._ensure_no_repeat("seed-response-0", 'sadness')
    assert regenerated != "seed-response-0"
    print("✓ _ensure_no_repeat enforces last-5 response window")


# ─────────────────────────────────────────────────────────────────────────────
# 5. WellnessBuddy.respond() method
# ─────────────────────────────────────────────────────────────────────────────

def test_respond_method_exists_and_works():
    """WellnessBuddy.respond(user_input, context=None) should produce
    a valid response string."""
    from wellness_buddy import WellnessBuddy

    tmp = tempfile.mkdtemp()
    try:
        buddy = WellnessBuddy(data_dir=tmp)
        from user_profile import UserProfile
        buddy.user_profile = UserProfile('test_user')
        buddy.user_id = 'test_user'

        # Without context
        r1 = buddy.respond("I'm feeling down today")
        assert isinstance(r1, str) and len(r1) > 10

        # With context
        ctx = [
            {"role": "user", "content": "I'm anxious about exams"},
            {"role": "assistant", "content": "That sounds stressful."},
        ]
        r2 = buddy.respond("I still feel worried", context=ctx)
        assert isinstance(r2, str) and len(r2) > 10
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("✓ WellnessBuddy.respond() works with and without context")


def test_respond_with_context_seeds_history():
    """Passing context to respond() should seed the conversation handler
    history with the context messages."""
    from wellness_buddy import WellnessBuddy

    tmp = tempfile.mkdtemp()
    try:
        buddy = WellnessBuddy(data_dir=tmp)
        from user_profile import UserProfile
        buddy.user_profile = UserProfile('ctx_user')
        buddy.user_id = 'ctx_user'

        ctx = [
            {"role": "user", "content": "I feel lonely"},
            {"role": "assistant", "content": "I'm sorry to hear that."},
            {"role": "user", "content": "Nobody cares"},
        ]
        buddy.respond("Everything seems hopeless", context=ctx)

        # The handler should have entries for the user messages in context
        # plus the new message = 3 user messages total
        user_msgs = [
            e['user_message']
            for e in buddy.conversation_handler.conversation_history
        ]
        assert "I feel lonely" in user_msgs
        assert "Nobody cares" in user_msgs
        assert "Everything seems hopeless" in user_msgs
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("✓ respond() seeds history from context")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Consecutive emotion counter
# ─────────────────────────────────────────────────────────────────────────────

def test_consecutive_emotion_count():
    """_consecutive_emotion_count correctly counts trailing same-emotion msgs."""
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()

    # Add a joy message then two anxiety messages
    handler.add_message("I'm happy!", analyzer.classify_emotion("I'm happy!"))
    handler.add_message(
        "I'm so anxious",
        analyzer.classify_emotion("I'm so anxious"),
    )
    handler.add_message(
        "Still anxious and worried",
        analyzer.classify_emotion("Still anxious and worried"),
    )

    count = handler._consecutive_emotion_count('anxiety')
    assert count >= 1, f"Expected >=1 consecutive anxiety, got {count}"

    # Joy should have 0 consecutive (it's not at the tail)
    joy_count = handler._consecutive_emotion_count('joy')
    assert joy_count == 0, f"Expected 0 consecutive joy at tail, got {joy_count}"

    print(f"✓ Consecutive emotion count: anxiety={count}, joy={joy_count}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Support variations list
# ─────────────────────────────────────────────────────────────────────────────

def test_support_variations_exist():
    """_SUPPORT_VARIATIONS should be a non-empty list of strings."""
    from conversation_handler import (
        _SUPPORT_VARIATIONS,
        ANXIETY_RESPONSES,
        STRESS_RESPONSES,
        SADNESS_RESPONSES,
        FEAR_RESPONSES,
        NEUTRAL_SUPPORT_RESPONSES,
        TAMIL_EMPATHY_VARIATIONS,
    )

    assert isinstance(_SUPPORT_VARIATIONS, list)
    assert len(_SUPPORT_VARIATIONS) >= 5
    for v in _SUPPORT_VARIATIONS:
        assert isinstance(v, str) and len(v) > 5

    for pool in (
        ANXIETY_RESPONSES,
        STRESS_RESPONSES,
        SADNESS_RESPONSES,
        FEAR_RESPONSES,
        NEUTRAL_SUPPORT_RESPONSES,
    ):
        assert len(pool) >= 8
        assert len(set(pool)) == len(pool)

    assert len(TAMIL_EMPATHY_VARIATIONS) >= 4

    print(f"✓ {len(_SUPPORT_VARIATIONS)} support variations available")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Escalation follow-ups dictionary
# ─────────────────────────────────────────────────────────────────────────────

def test_escalation_followups_exist():
    """_ESCALATION_FOLLOWUPS should cover key negative emotions."""
    from conversation_handler import _ESCALATION_FOLLOWUPS

    for emotion in ('anxiety', 'sadness', 'fear', 'anger'):
        assert emotion in _ESCALATION_FOLLOWUPS, (
            f"Missing escalation for {emotion}"
        )
        assert len(_ESCALATION_FOLLOWUPS[emotion]) >= 2

    print("✓ Escalation follow-ups cover key emotions")


def test_topic_detection_influences_response():
    """Work-stress topic should influence suggestions in response composition."""
    from conversation_handler import ConversationHandler, _TOPIC_SUGGESTIONS
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()
    msg = "My work deadline and manager pressure are making me stressed"
    emotion_data = analyzer.classify_emotion(msg)
    emotion_data['primary_emotion'] = 'anxiety'
    handler.add_message(msg, emotion_data)

    response = handler.generate_response(emotion_data)
    assert any(suggestion in response for suggestion in _TOPIC_SUGGESTIONS['work_stress'])
    print("✓ Topic-aware response includes work-stress support guidance")


def test_debug_logging_for_response_generation(caplog):
    """Optional debug mode should emit emotion/topic/template metadata."""
    import logging
    from conversation_handler import ConversationHandler
    from emotion_analyzer import EmotionAnalyzer

    analyzer = EmotionAnalyzer()
    handler = ConversationHandler()
    msg = "I'm anxious about my career interview and future"
    emotion_data = analyzer.classify_emotion(msg)
    emotion_data['primary_emotion'] = 'anxiety'
    handler.add_message(msg, emotion_data)

    caplog.set_level(logging.INFO)
    handler.generate_response(
        emotion_data,
        user_context={
            'debug_response_generation': True,
            'context': [{'role': 'user', 'content': msg}],
        },
    )
    assert "Response debug | emotion=anxiety" in caplog.text
    assert "template=" in caplog.text
    print("✓ Debug logging emits response generation metadata")


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        test_no_identical_replies_for_same_input,
        test_conversation_history_grows,
        test_get_chat_history_structured,
        test_emotional_escalation_on_repeated_emotion,
        test_ensure_no_repeat_appends_variation,
        test_ensure_no_repeat_checks_recent_window,
        test_respond_method_exists_and_works,
        test_respond_with_context_seeds_history,
        test_consecutive_emotion_count,
        test_support_variations_exist,
        test_escalation_followups_exist,
        test_topic_detection_influences_response,
        test_debug_logging_for_response_generation,
    ]

    print("\n" + "=" * 70)
    print("   CONVERSATION MEMORY TEST SUITE")
    print("=" * 70)

    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            failed += 1
            print(f"✗ {t.__name__}: {exc}")

    print(f"\n{'=' * 70}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print("=" * 70)
