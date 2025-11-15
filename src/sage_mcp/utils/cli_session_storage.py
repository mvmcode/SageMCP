"""In-memory storage for CLI OAuth session results.

This module provides temporary storage for OAuth results that the CLI
can poll for. Sessions expire after 5 minutes.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from threading import Lock


class CLISessionStorage:
    """Thread-safe in-memory storage for CLI OAuth sessions."""

    def __init__(self, expiry_seconds: int = 300):
        """Initialize storage.

        Args:
            expiry_seconds: How long to keep sessions (default: 5 minutes)
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._expiry_seconds = expiry_seconds

    def store(self, session_id: str, data: Dict[str, Any]) -> None:
        """Store session data.

        Args:
            session_id: Unique session identifier
            data: Session data to store
        """
        with self._lock:
            self._sessions[session_id] = {
                "data": data,
                "expires_at": time.time() + self._expiry_seconds,
                "created_at": datetime.utcnow().isoformat()
            }
            # Clean up expired sessions
            self._cleanup_expired()

    def get(self, session_id: str, delete_after_read: bool = True) -> Optional[Dict[str, Any]]:
        """Retrieve session data.

        Args:
            session_id: Session identifier
            delete_after_read: Whether to delete session after reading (default: True)

        Returns:
            Session data if found and not expired, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if not session:
                return None

            # Check if expired
            if time.time() > session["expires_at"]:
                del self._sessions[session_id]
                return None

            data = session["data"]

            # Delete if requested (one-time use)
            if delete_after_read:
                del self._sessions[session_id]

            return data

    def delete(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def _cleanup_expired(self) -> None:
        """Remove expired sessions (called internally)."""
        now = time.time()
        expired = [
            sid for sid, session in self._sessions.items()
            if now > session["expires_at"]
        ]
        for sid in expired:
            del self._sessions[sid]

    def cleanup_all_expired(self) -> int:
        """Manually cleanup all expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            before = len(self._sessions)
            self._cleanup_expired()
            after = len(self._sessions)
            return before - after

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with session count and other stats
        """
        with self._lock:
            self._cleanup_expired()
            return {
                "active_sessions": len(self._sessions),
                "expiry_seconds": self._expiry_seconds
            }


# Global instance
cli_session_storage = CLISessionStorage()
