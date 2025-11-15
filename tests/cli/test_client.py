"""Tests for CLI API client."""

import pytest
from unittest.mock import Mock, patch

from sage_mcp.cli.client import APIError, SageMCPClient
from sage_mcp.cli.config import ProfileConfig


@pytest.fixture
def profile_config():
    """Create a test profile config."""
    return ProfileConfig(
        base_url="http://test.example.com",
        api_key="test-key",
        timeout=30,
    )


@pytest.fixture
def client(profile_config):
    """Create a test client."""
    return SageMCPClient(profile_config)


def test_client_initialization(client, profile_config):
    """Test client initialization."""
    assert client.config == profile_config
    assert client.base_url == "http://test.example.com"
    assert client.timeout == 30
    assert client.api_key == "test-key"


def test_client_get_headers(client):
    """Test header generation."""
    headers = client._get_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Authorization"] == "Bearer test-key"


def test_client_get_headers_no_api_key():
    """Test headers without API key."""
    config = ProfileConfig(base_url="http://test.com")
    client = SageMCPClient(config)

    headers = client._get_headers()
    assert "Authorization" not in headers


@patch("httpx.Client")
def test_list_tenants_success(mock_client_class, client):
    """Test successful tenant listing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"slug": "tenant1", "name": "Tenant 1"},
        {"slug": "tenant2", "name": "Tenant 2"},
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client

    tenants = client.list_tenants()

    assert len(tenants) == 2
    assert tenants[0]["slug"] == "tenant1"
    assert tenants[1]["slug"] == "tenant2"


@patch("httpx.Client")
def test_create_tenant_success(mock_client_class, client):
    """Test successful tenant creation."""
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "slug": "new-tenant",
        "name": "New Tenant",
        "is_active": True,
    }
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client

    tenant = client.create_tenant("new-tenant", "New Tenant")

    assert tenant["slug"] == "new-tenant"
    assert tenant["name"] == "New Tenant"
    assert tenant["is_active"] is True


@patch("httpx.Client")
def test_api_error_handling(mock_client_class, client):
    """Test API error handling."""
    import httpx

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"detail": "Tenant not found"}

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.get.return_value = mock_response
    mock_client.get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not found", request=Mock(), response=mock_response
    )
    mock_client_class.return_value = mock_client

    with pytest.raises(APIError) as exc_info:
        client.get_tenant("missing-tenant")

    assert "Tenant not found" in str(exc_info.value.message)
    assert exc_info.value.status_code == 404


def test_ping_success(client):
    """Test successful ping."""
    with patch("httpx.Client") as mock_client_class:
        mock_response = Mock()
        mock_response.status_code = 200

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = client.ping()
        assert result is True


def test_ping_failure(client):
    """Test failed ping."""
    with patch("httpx.Client") as mock_client_class:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get.side_effect = Exception("Connection error")
        mock_client_class.return_value = mock_client

        result = client.ping()
        assert result is False


def test_get_oauth_auth_url(client):
    """Test OAuth authorization URL generation."""
    url = client.get_oauth_auth_url(
        "test-tenant",
        "github",
        redirect_uri="http://localhost:8080/callback",
        state="test-state-123"
    )

    assert url.startswith("http://test.example.com/api/v1/oauth/test-tenant/auth/github")
    assert "custom_redirect_uri=http://localhost:8080/callback" in url
    assert "custom_state=test-state-123" in url


def test_get_oauth_auth_url_without_params(client):
    """Test OAuth URL generation without optional parameters."""
    url = client.get_oauth_auth_url("test-tenant", "github")

    assert url == "http://test.example.com/api/v1/oauth/test-tenant/auth/github"


@patch("httpx.Client")
def test_get_cli_session_result_success(mock_client_class, client):
    """Test successful CLI session result retrieval."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "provider": "github",
        "provider_user_id": "12345"
    }
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client

    result = client.get_cli_session_result("cli-session-abc123")

    assert result["status"] == "success"
    assert result["provider"] == "github"
    mock_client.get.assert_called_once_with(
        "http://test.example.com/api/v1/oauth/cli-sessions/cli-session-abc123",
        headers=client._get_headers()
    )


@patch("httpx.Client")
def test_list_oauth_configs(mock_client_class, client):
    """Test listing OAuth configurations."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"provider": "github", "client_id": "abc123", "is_active": True},
        {"provider": "slack", "client_id": "xyz789", "is_active": True}
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client

    configs = client.list_oauth_configs("test-tenant")

    assert len(configs) == 2
    assert configs[0]["provider"] == "github"
    assert configs[1]["provider"] == "slack"


@patch("httpx.Client")
def test_create_oauth_config(mock_client_class, client):
    """Test creating OAuth configuration."""
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "provider": "github",
        "client_id": "new-client-id",
        "is_active": True
    }
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client

    config = client.create_oauth_config(
        "test-tenant",
        "github",
        "new-client-id",
        "new-client-secret"
    )

    assert config["provider"] == "github"
    assert config["client_id"] == "new-client-id"


@patch("httpx.Client")
def test_delete_oauth_config(mock_client_class, client):
    """Test deleting OAuth configuration."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Configuration deleted"}
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.delete.return_value = mock_response
    mock_client_class.return_value = mock_client

    result = client.delete_oauth_config("test-tenant", "github")

    assert result["message"] == "Configuration deleted"
    mock_client.delete.assert_called_once()


@patch("httpx.Client")
def test_get_available_connector_types(mock_client_class, client):
    """Test getting available connector types."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "github", "name": "GitHub"},
        {"id": "slack", "name": "Slack"},
        {"id": "jira", "name": "Jira"}
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client

    types = client.get_available_connector_types()

    assert types == ["github", "slack", "jira"]
