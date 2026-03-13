"""Tests for per-user pipeline isolation in api_service."""

import threading
from api_service import get_pipeline, _pipelines, _pipelines_lock


# ------------------------------------------------------------------
# get_pipeline basics
# ------------------------------------------------------------------

def test_get_pipeline_returns_pipeline():
    """get_pipeline must return a WellnessAgentPipeline instance."""
    from agent_pipeline import WellnessAgentPipeline
    # Clean up shared state for test isolation
    with _pipelines_lock:
        _pipelines.pop('__test_basic__', None)
    p = get_pipeline('__test_basic__')
    assert isinstance(p, WellnessAgentPipeline)
    with _pipelines_lock:
        _pipelines.pop('__test_basic__', None)


def test_get_pipeline_returns_same_instance():
    """Repeated calls with the same user_id must return the same object."""
    with _pipelines_lock:
        _pipelines.pop('__test_same__', None)
    p1 = get_pipeline('__test_same__')
    p2 = get_pipeline('__test_same__')
    assert p1 is p2
    with _pipelines_lock:
        _pipelines.pop('__test_same__', None)


# ------------------------------------------------------------------
# Per-user isolation
# ------------------------------------------------------------------

def test_different_users_get_different_pipelines():
    """Different user_ids must receive distinct pipeline instances."""
    with _pipelines_lock:
        _pipelines.pop('__test_alice__', None)
        _pipelines.pop('__test_bob__', None)
    pa = get_pipeline('__test_alice__')
    pb = get_pipeline('__test_bob__')
    assert pa is not pb
    with _pipelines_lock:
        _pipelines.pop('__test_alice__', None)
        _pipelines.pop('__test_bob__', None)


def test_user_state_isolation():
    """Emotion data added via one user's pipeline must NOT appear in another's."""
    with _pipelines_lock:
        _pipelines.pop('__test_iso_a__', None)
        _pipelines.pop('__test_iso_b__', None)

    pa = get_pipeline('__test_iso_a__')
    pb = get_pipeline('__test_iso_b__')

    # Process a message for user A — this should add pattern data to A only
    pa.process_turn("I am extremely sad and heartbroken")

    # User B's pattern tracker should have no recorded emotion entries
    assert len(pb.pattern_agent.tracker.emotion_history) == 0, (
        "User B's emotion history should be empty after only User A chatted"
    )

    # User A's pattern tracker should have exactly 1 entry
    assert len(pa.pattern_agent.tracker.emotion_history) == 1

    with _pipelines_lock:
        _pipelines.pop('__test_iso_a__', None)
        _pipelines.pop('__test_iso_b__', None)


# ------------------------------------------------------------------
# Thread safety
# ------------------------------------------------------------------

def test_concurrent_get_pipeline():
    """Concurrent get_pipeline calls for the same user must not create duplicates."""
    uid = '__test_conc__'
    with _pipelines_lock:
        _pipelines.pop(uid, None)

    results = []

    def fetch():
        results.append(get_pipeline(uid))

    threads = [threading.Thread(target=fetch) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All 10 threads should have received the exact same instance
    assert len(set(id(p) for p in results)) == 1, (
        "Concurrent calls should return the same pipeline instance"
    )
    with _pipelines_lock:
        _pipelines.pop(uid, None)


# ------------------------------------------------------------------
# Schema compatibility
# ------------------------------------------------------------------

def test_chat_request_schema():
    """ChatRequest must have user_id and message fields."""
    from api_service import ChatRequest
    try:
        # When pydantic is available
        req = ChatRequest(user_id='u1', message='hello')
        assert req.user_id == 'u1'
        assert req.message == 'hello'
    except TypeError:
        # Pydantic not installed — ChatRequest is a plain class.
        # Just verify the class has the expected annotations.
        assert 'user_id' in getattr(ChatRequest, '__annotations__', {})
        assert 'message' in getattr(ChatRequest, '__annotations__', {})


def test_chat_response_schema():
    """ChatResponse must have response, primary_emotion, risk_level fields."""
    from api_service import ChatResponse
    try:
        resp = ChatResponse(response='hi', primary_emotion='neutral', risk_level='low')
        assert resp.response == 'hi'
        assert resp.primary_emotion == 'neutral'
        assert resp.risk_level == 'low'
    except TypeError:
        # Pydantic not installed — just verify annotations.
        assert 'response' in getattr(ChatResponse, '__annotations__', {})
        assert 'primary_emotion' in getattr(ChatResponse, '__annotations__', {})
        assert 'risk_level' in getattr(ChatResponse, '__annotations__', {})
