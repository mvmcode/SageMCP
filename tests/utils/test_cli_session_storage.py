"""Tests for CLI session storage."""

import time
import pytest
from datetime import datetime, timedelta, timezone

from sage_mcp.utils.cli_session_storage import CLISessionStorage


@pytest.fixture
def storage():
    """Create a test CLI session storage."""
    return CLISessionStorage(expiry_seconds=2)  # Short expiry for testing


def test_storage_initialization(storage):
    """Test storage initialization."""
    assert storage._expiry_seconds == 2
    assert len(storage._sessions) == 0


def test_store_and_get_session(storage):
    """Test storing and retrieving a session."""
    session_id = "test-session-123"
    data = {
        "status": "success",
        "provider": "github",
        "user_id": "12345"
    }

    storage.store(session_id, data)
    result = storage.get(session_id, delete_after_read=False)

    assert result == data


def test_get_session_with_delete(storage):
    """Test retrieving a session with deletion."""
    session_id = "test-session-456"
    data = {"status": "success"}

    storage.store(session_id, data)
    result = storage.get(session_id, delete_after_read=True)

    assert result == data

    # Should not exist after read
    result2 = storage.get(session_id)
    assert result2 is None


def test_get_nonexistent_session(storage):
    """Test getting a session that doesn't exist."""
    result = storage.get("nonexistent-session")
    assert result is None


def test_session_expiry(storage):
    """Test that sessions expire after the configured time."""
    session_id = "expiring-session"
    data = {"status": "success"}

    storage.store(session_id, data)

    # Should exist immediately
    result = storage.get(session_id, delete_after_read=False)
    assert result == data

    # Wait for expiry
    time.sleep(2.5)

    # Should be expired now
    result = storage.get(session_id)
    assert result is None


def test_delete_session(storage):
    """Test deleting a session."""
    session_id = "delete-test"
    data = {"status": "success"}

    storage.store(session_id, data)
    storage.delete(session_id)

    result = storage.get(session_id)
    assert result is None


def test_delete_nonexistent_session(storage):
    """Test deleting a session that doesn't exist (should not raise)."""
    storage.delete("nonexistent-session")
    # Should not raise an exception


def test_cleanup_all_expired_sessions(storage):
    """Test cleaning up expired sessions."""
    # Store two sessions
    storage.store("session-1", {"data": "1"})
    time.sleep(1)
    storage.store("session-2", {"data": "2"})

    # Wait for first session to expire
    time.sleep(1.5)

    # Cleanup expired
    cleaned = storage.cleanup_all_expired()

    # Should have cleaned up 1 session
    assert cleaned == 1

    # First should be gone, second should still exist
    assert storage.get("session-1") is None
    assert storage.get("session-2") is not None


def test_get_stats(storage):
    """Test getting storage statistics."""
    # Store some sessions
    storage.store("session-1", {"data": "1"})
    storage.store("session-2", {"data": "2"})

    stats = storage.get_stats()

    assert stats["active_sessions"] == 2
    assert "expiry_seconds" in stats
    assert stats["expiry_seconds"] == 2

    # Wait for expiry
    time.sleep(2.5)
    stats = storage.get_stats()

    # After cleanup in get_stats, expired sessions should be removed
    assert stats["active_sessions"] == 0


def test_thread_safety_store_and_get(storage):
    """Test concurrent store and get operations."""
    import threading

    results = []
    errors = []

    def store_session(session_id):
        try:
            storage.store(session_id, {"id": session_id})
        except Exception as e:
            errors.append(e)

    def get_session(session_id):
        try:
            result = storage.get(session_id, delete_after_read=False)
            results.append(result)
        except Exception as e:
            errors.append(e)

    # Create threads
    threads = []
    for i in range(10):
        t1 = threading.Thread(target=store_session, args=(f"session-{i}",))
        t2 = threading.Thread(target=get_session, args=(f"session-{i}",))
        threads.extend([t1, t2])

    # Start all threads
    for t in threads:
        t.start()

    # Wait for completion
    for t in threads:
        t.join()

    # Should have no errors
    assert len(errors) == 0
    # Should have some successful retrievals
    assert len([r for r in results if r is not None]) > 0


def test_update_existing_session(storage):
    """Test updating an existing session."""
    session_id = "update-test"

    # Store initial data
    storage.store(session_id, {"status": "pending"})

    # Update with new data
    storage.store(session_id, {"status": "success", "data": "new"})

    result = storage.get(session_id)
    assert result["status"] == "success"
    assert result["data"] == "new"


def test_multiple_sessions(storage):
    """Test storing and managing multiple sessions."""
    sessions = {
        "session-1": {"user": "alice"},
        "session-2": {"user": "bob"},
        "session-3": {"user": "charlie"},
    }

    # Store all sessions
    for session_id, data in sessions.items():
        storage.store(session_id, data)

    # Retrieve all sessions
    for session_id, expected_data in sessions.items():
        result = storage.get(session_id, delete_after_read=False)
        assert result == expected_data

    # Check stats
    stats = storage.get_stats()
    assert stats["active_sessions"] == 3


def test_global_cli_session_storage():
    """Test the global cli_session_storage instance."""
    from sage_mcp.utils.cli_session_storage import cli_session_storage

    # Should be initialized
    assert cli_session_storage is not None
    assert isinstance(cli_session_storage, CLISessionStorage)

    # Test basic functionality
    cli_session_storage.store("test-global", {"test": "data"})
    result = cli_session_storage.get("test-global")
    assert result == {"test": "data"}
