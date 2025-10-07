"""Test connectors module."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from mcp import types

from sage_mcp.connectors.github import GitHubConnector
from sage_mcp.connectors.registry import ConnectorRegistry, register_connector
from sage_mcp.models.connector import ConnectorType


class TestConnectorRegistry:
    """Test ConnectorRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ConnectorRegistry()
        assert len(registry._connectors) == 0
        assert len(registry._connector_types) == 0
    
    def test_register_connector(self):
        """Test registering a connector."""
        registry = ConnectorRegistry()
        
        class TestConnector:
            def __init__(self):
                pass
            
            @property
            def name(self):
                return "test"
        
        registry.register(ConnectorType.GITHUB, TestConnector)
        
        assert len(registry._connectors) == 1
        assert len(registry._connector_types) == 1
        assert ConnectorType.GITHUB in registry._connector_types
        assert "test" in registry._connectors
    
    def test_get_connector(self):
        """Test getting a connector by type."""
        registry = ConnectorRegistry()
        
        class TestConnector:
            def __init__(self):
                pass
            
            @property
            def name(self):
                return "test"
        
        registry.register(ConnectorType.GITHUB, TestConnector)
        
        connector = registry.get_connector(ConnectorType.GITHUB)
        assert connector is not None
        assert connector.name == "test"
        
        # Test non-existent connector
        connector = registry.get_connector(ConnectorType.GITLAB)
        assert connector is None
    
    def test_get_connector_by_name(self):
        """Test getting a connector by name."""
        registry = ConnectorRegistry()
        
        class TestConnector:
            def __init__(self):
                pass
            
            @property
            def name(self):
                return "test"
        
        registry.register(ConnectorType.GITHUB, TestConnector)
        
        connector = registry.get_connector_by_name("test")
        assert connector is not None
        assert connector.name == "test"
        
        # Test non-existent connector
        connector = registry.get_connector_by_name("nonexistent")
        assert connector is None
    
    def test_list_connectors(self):
        """Test listing all connectors."""
        registry = ConnectorRegistry()
        
        class TestConnector:
            def __init__(self):
                pass
            
            @property
            def name(self):
                return "test"
        
        registry.register(ConnectorType.GITHUB, TestConnector)
        
        connectors = registry.list_connectors()
        assert len(connectors) == 1
        assert "test" in connectors
    
    def test_get_connector_info(self):
        """Test getting connector information."""
        registry = ConnectorRegistry()
        
        class TestConnector:
            def __init__(self):
                pass
            
            @property
            def name(self):
                return "test"
            
            @property
            def display_name(self):
                return "Test Connector"
            
            @property
            def description(self):
                return "A test connector"
            
            @property
            def requires_oauth(self):
                return True
        
        registry.register(ConnectorType.GITHUB, TestConnector)
        
        info = registry.get_connector_info(ConnectorType.GITHUB)
        assert info is not None
        assert info["name"] == "test"
        assert info["display_name"] == "Test Connector"
        assert info["description"] == "A test connector"
        assert info["requires_oauth"] is True
        assert info["type"] == "github"


class TestGitHubConnector:
    """Test GitHubConnector class."""
    
    def test_github_connector_properties(self):
        """Test GitHub connector properties."""
        connector = GitHubConnector()
        
        assert connector.display_name == "GitHub"
        assert "GitHub" in connector.description
        assert connector.requires_oauth is True
    
    @pytest.mark.asyncio
    async def test_get_tools(self, sample_connector, sample_oauth_credential):
        """Test getting GitHub tools."""
        connector = GitHubConnector()
        
        tools = await connector.get_tools(sample_connector, sample_oauth_credential)
        
        assert len(tools) > 0
        
        # Check that all tools have the correct naming convention
        for tool in tools:
            assert tool.name.startswith("github_")
            assert isinstance(tool, types.Tool)
            assert tool.description is not None
            assert tool.inputSchema is not None
        
        # Check for specific tools
        tool_names = [tool.name for tool in tools]
        assert "github_list_repositories" in tool_names
        assert "github_get_repository" in tool_names
        assert "github_list_issues" in tool_names
        assert "github_check_token_scopes" in tool_names
    
    @pytest.mark.asyncio
    async def test_execute_tool_unknown(self, sample_connector, sample_oauth_credential):
        """Test executing unknown tool."""
        connector = GitHubConnector()
        
        result = await connector.execute_tool(
            sample_connector,
            "unknown_tool",
            {},
            sample_oauth_credential
        )
        
        assert "Unknown tool" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_invalid_oauth(self, sample_connector):
        """Test executing tool with invalid OAuth."""
        connector = GitHubConnector()
        
        result = await connector.execute_tool(
            sample_connector,
            "list_repositories",
            {},
            None
        )
        
        assert "Invalid or expired" in result
    
    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.github.GitHubConnector._make_authenticated_request')
    async def test_check_token_scopes(self, mock_request, sample_connector, sample_oauth_credential):
        """Test checking token scopes."""
        connector = GitHubConnector()
        
        # Mock the GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 123456,
            "type": "User",
            "name": "Test User",
            "public_repos": 5
        }
        mock_response.headers = {
            "X-OAuth-Scopes": "repo, user:email, read:org",
            "X-Accepted-OAuth-Scopes": ""
        }
        mock_request.return_value = mock_response
        
        result = await connector._check_token_scopes(sample_oauth_credential)
        
        assert "testuser" in result
        assert "repo" in result
        assert "user:email" in result
        assert "read:org" in result
    
    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.github.GitHubConnector._make_authenticated_request')
    async def test_list_organizations(self, mock_request, sample_connector, sample_oauth_credential):
        """Test listing organizations."""
        connector = GitHubConnector()
        
        # Mock the GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "login": "testorg",
                "id": 789,
                "description": "Test Organization",
                "url": "https://api.github.com/orgs/testorg",
                "html_url": "https://github.com/testorg"
            }
        ]
        mock_request.return_value = mock_response
        
        result = await connector._list_organizations(sample_oauth_credential)
        
        assert "testorg" in result
        assert "total_count" in result
        assert "1" in result  # Should show 1 organization
    
    def test_validate_oauth_credential_valid(self, sample_oauth_credential):
        """Test validating valid OAuth credential."""
        connector = GitHubConnector()
        
        assert connector.validate_oauth_credential(sample_oauth_credential) is True
    
    def test_validate_oauth_credential_none(self):
        """Test validating None OAuth credential."""
        connector = GitHubConnector()
        
        assert connector.validate_oauth_credential(None) is False
    
    def test_validate_oauth_credential_inactive(self, sample_oauth_credential):
        """Test validating inactive OAuth credential."""
        connector = GitHubConnector()
        
        sample_oauth_credential.is_active = False
        assert connector.validate_oauth_credential(sample_oauth_credential) is False