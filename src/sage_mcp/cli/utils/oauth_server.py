"""Local OAuth callback server for CLI OAuth flows."""

import secrets
import socket
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from rich.console import Console

console = Console()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callbacks."""

    # Class variables to store callback data
    auth_code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None
    callback_received = False

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET request from OAuth callback."""
        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Extract parameters
        if "code" in query_params:
            OAuthCallbackHandler.auth_code = query_params["code"][0]
        if "state" in query_params:
            OAuthCallbackHandler.state = query_params["state"][0]
        if "error" in query_params:
            OAuthCallbackHandler.error = query_params["error"][0]
        if "error_description" in query_params:
            OAuthCallbackHandler.error_description = query_params["error_description"][0]

        OAuthCallbackHandler.callback_received = True

        # Send response to browser
        if OAuthCallbackHandler.error:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html>
                <head><title>OAuth Error</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #d32f2f;">❌ Authorization Failed</h1>
                    <p style="font-size: 18px;">Error: {OAuthCallbackHandler.error}</p>
                    <p style="color: #666;">{OAuthCallbackHandler.error_description or 'No description provided'}</p>
                    <p style="margin-top: 30px;">You can close this window and return to your terminal.</p>
                </body>
            </html>
            """
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
                <head><title>OAuth Success</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #4caf50;">✅ Authorization Successful</h1>
                    <p style="font-size: 18px;">You can close this window and return to your terminal.</p>
                    <p style="color: #666;">The SageMCP CLI is completing the authentication process...</p>
                </body>
            </html>
            """

        self.wfile.write(html.encode())


class OAuthCallbackServer:
    """Local HTTP server for receiving OAuth callbacks."""

    def __init__(self, port: int = 0):
        """Initialize the OAuth callback server.

        Args:
            port: Port to listen on. If 0, a random available port is chosen.
        """
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.expected_state: Optional[str] = None

    def _find_free_port(self) -> int:
        """Find a free port to bind to.

        Returns:
            Available port number
        """
        if self.port != 0:
            return self.port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    def start(self) -> str:
        """Start the OAuth callback server.

        Returns:
            The callback URL (http://localhost:PORT/callback)
        """
        # Reset handler state
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.state = None
        OAuthCallbackHandler.error = None
        OAuthCallbackHandler.error_description = None
        OAuthCallbackHandler.callback_received = False

        # Generate expected state for CSRF protection
        self.expected_state = secrets.token_urlsafe(32)

        # Find available port
        self.port = self._find_free_port()

        # Create server
        self.server = HTTPServer(('localhost', self.port), OAuthCallbackHandler)

        # Start server in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        return f"http://localhost:{self.port}/callback"

    def wait_for_callback(self, timeout: int = 300) -> Dict[str, Optional[str]]:
        """Wait for OAuth callback to be received.

        Args:
            timeout: Maximum time to wait in seconds (default: 5 minutes)

        Returns:
            Dictionary with 'code', 'state', 'error', and 'error_description'

        Raises:
            TimeoutError: If callback not received within timeout
        """
        start_time = time.time()

        while not OAuthCallbackHandler.callback_received:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"OAuth callback not received within {timeout} seconds. "
                    "Please try again or check your OAuth configuration."
                )
            time.sleep(0.1)

        return {
            "code": OAuthCallbackHandler.auth_code,
            "state": OAuthCallbackHandler.state,
            "error": OAuthCallbackHandler.error,
            "error_description": OAuthCallbackHandler.error_description,
        }

    def stop(self) -> None:
        """Stop the OAuth callback server."""
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None

    def get_state(self) -> Optional[str]:
        """Get the expected state parameter for CSRF protection.

        Returns:
            State string
        """
        return self.expected_state

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures server is stopped."""
        self.stop()
