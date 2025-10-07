"""Test configuration module."""

import pytest
import os
from unittest.mock import patch

from sage_mcp.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings(secret_key="test-secret")
        
        assert settings.app_name == "Sage MCP"
        assert settings.app_version == "0.1.0"
        assert settings.debug is False
        assert settings.environment == "development"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.access_token_expire_minutes == 30
        assert settings.refresh_token_expire_days == 7
        assert settings.mcp_server_timeout == 30
        assert settings.mcp_max_connections_per_tenant == 10
        
    def test_settings_from_env(self):
        """Test settings from environment variables."""
        env_vars = {
            "DEBUG": "true",
            "ENVIRONMENT": "testing",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "SECRET_KEY": "test-secret-key",
            "GITHUB_CLIENT_ID": "test-github-id",
            "GITHUB_CLIENT_SECRET": "test-github-secret",
            "BASE_URL": "http://test.example.com"
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.debug is True
            assert settings.environment == "testing"
            assert settings.host == "127.0.0.1"
            assert settings.port == 9000
            assert settings.secret_key == "test-secret-key"
            assert settings.github_client_id == "test-github-id"
            assert settings.github_client_secret == "test-github-secret"
            assert settings.base_url == "http://test.example.com"
    
    def test_secret_key_validation(self):
        """Test secret key validation and generation."""
        # Test with empty secret key (should generate one)
        settings = Settings()
        assert len(settings.secret_key) > 0
        
        # Test with provided secret key
        settings = Settings(secret_key="my-secret")
        assert settings.secret_key == "my-secret"
    
    def test_database_url_validation(self):
        """Test database URL validation."""
        settings = Settings(
            secret_key="test",
            database_url="postgresql://user:pass@localhost:5432/testdb"
        )
        assert "postgresql://user:pass@localhost:5432/testdb" in str(settings.database_url)
    
    def test_oauth_settings(self):
        """Test OAuth settings."""
        settings = Settings(
            secret_key="test",
            github_client_id="github-id",
            gitlab_client_id="gitlab-id",
            google_client_id="google-id"
        )
        
        assert settings.github_client_id == "github-id"
        assert settings.gitlab_client_id == "gitlab-id"
        assert settings.google_client_id == "google-id"


class TestGetSettings:
    """Test get_settings function."""
    
    def test_settings_caching(self):
        """Test that settings are cached."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same instance due to lru_cache
        assert settings1 is settings2