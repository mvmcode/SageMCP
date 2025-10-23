"""Test connectors module."""

from unittest.mock import Mock, patch

import pytest
from mcp import types

from sage_mcp.connectors.github import GitHubConnector
from sage_mcp.connectors.jira import JiraConnector
from sage_mcp.connectors.registry import ConnectorRegistry
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


class TestJiraConnector:
    """Test JiraConnector class."""

    def test_jira_connector_properties(self):
        """Test Jira connector properties."""
        connector = JiraConnector()

        assert connector.display_name == "Jira"
        assert "Jira" in connector.description
        assert connector.requires_oauth is True

    @pytest.mark.asyncio
    async def test_get_tools(self, sample_connector, sample_oauth_credential):
        """Test getting Jira tools."""
        connector = JiraConnector()

        tools = await connector.get_tools(sample_connector, sample_oauth_credential)

        assert len(tools) == 20  # Jira has 20 tools

        # Check that all tools have the correct naming convention
        for tool in tools:
            assert tool.name.startswith("jira_")
            assert isinstance(tool, types.Tool)
            assert tool.description is not None
            assert tool.inputSchema is not None

        # Check for specific tools
        tool_names = [tool.name for tool in tools]
        assert "jira_search_issues" in tool_names
        assert "jira_get_issue" in tool_names
        assert "jira_create_issue" in tool_names
        assert "jira_update_issue" in tool_names
        assert "jira_list_projects" in tool_names
        assert "jira_list_boards" in tool_names
        assert "jira_list_sprints" in tool_names
        assert "jira_search_users" in tool_names

    @pytest.mark.asyncio
    async def test_execute_tool_unknown(self, sample_connector, sample_oauth_credential):
        """Test executing unknown tool."""
        connector = JiraConnector()

        # Mock _get_cloud_id
        with patch.object(connector, '_get_cloud_id', return_value='test-cloud-id'):
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
        connector = JiraConnector()

        result = await connector.execute_tool(
            sample_connector,
            "search_issues",
            {},
            None
        )

        assert "Invalid or expired" in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_get_cloud_id(self, mock_request, sample_oauth_credential):
        """Test getting Jira cloud ID."""
        connector = JiraConnector()

        # Mock the Jira accessible resources response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "test-cloud-id-123",
                "name": "Test Jira Site",
                "url": "https://test.atlassian.net"
            }
        ]
        mock_request.return_value = mock_response

        cloud_id = await connector._get_cloud_id(sample_oauth_credential)

        assert cloud_id == "test-cloud-id-123"
        assert mock_request.called
        # Verify caching works
        cloud_id2 = await connector._get_cloud_id(sample_oauth_credential)
        assert cloud_id2 == "test-cloud-id-123"

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_search_issues(self, mock_request, sample_oauth_credential):
        """Test searching Jira issues."""
        connector = JiraConnector()

        # Mock the Jira API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 2,
            "issues": [
                {
                    "key": "PROJ-123",
                    "fields": {
                        "summary": "Test issue 1",
                        "status": {"name": "Open"}
                    }
                },
                {
                    "key": "PROJ-124",
                    "fields": {
                        "summary": "Test issue 2",
                        "status": {"name": "In Progress"}
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await connector._search_issues(
            "test-cloud-id",
            {"jql": "project = PROJ"},
            sample_oauth_credential
        )

        assert "PROJ-123" in result
        assert "PROJ-124" in result
        assert "Test issue 1" in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_create_issue(self, mock_request, sample_oauth_credential):
        """Test creating a Jira issue."""
        connector = JiraConnector()

        # Mock the Jira API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "PROJ-125",
            "id": "10001",
            "self": "https://test.atlassian.net/rest/api/3/issue/10001"
        }
        mock_request.return_value = mock_response

        result = await connector._create_issue(
            "test-cloud-id",
            {
                "project_key": "PROJ",
                "summary": "New test issue",
                "issue_type": "Bug",
                "description": "This is a test issue"
            },
            sample_oauth_credential
        )

        assert "PROJ-125" in result
        assert mock_request.called

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_get_transitions(self, mock_request, sample_oauth_credential):
        """Test getting issue transitions."""
        connector = JiraConnector()

        # Mock the Jira API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "transitions": [
                {
                    "id": "11",
                    "name": "In Progress",
                    "to": {"name": "In Progress"}
                },
                {
                    "id": "21",
                    "name": "Done",
                    "to": {"name": "Done"}
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await connector._get_transitions(
            "test-cloud-id",
            {"issue_key": "PROJ-123"},
            sample_oauth_credential
        )

        assert "In Progress" in result
        assert "Done" in result
        assert '"id": "11"' in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_list_projects(self, mock_request, sample_oauth_credential):
        """Test listing Jira projects."""
        connector = JiraConnector()

        # Mock the Jira API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "10000",
                "key": "PROJ",
                "name": "Test Project",
                "projectTypeKey": "software",
                "lead": {"displayName": "Test User"}
            }
        ]
        mock_request.return_value = mock_response

        result = await connector._list_projects(
            "test-cloud-id",
            {},
            sample_oauth_credential
        )

        assert "PROJ" in result
        assert "Test Project" in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_list_boards(self, mock_request, sample_oauth_credential):
        """Test listing Jira boards."""
        connector = JiraConnector()

        # Mock the Jira Agile API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "values": [
                {
                    "id": 1,
                    "name": "Test Board",
                    "type": "scrum",
                    "location": {"projectKey": "PROJ"}
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await connector._list_boards(
            "test-cloud-id",
            {},
            sample_oauth_credential
        )

        assert "Test Board" in result
        assert "scrum" in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_list_sprints(self, mock_request, sample_oauth_credential):
        """Test listing sprints."""
        connector = JiraConnector()

        # Mock the Jira Agile API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "values": [
                {
                    "id": 1,
                    "name": "Sprint 1",
                    "state": "active",
                    "startDate": "2024-01-01T00:00:00.000Z",
                    "endDate": "2024-01-14T00:00:00.000Z"
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await connector._list_sprints(
            "test-cloud-id",
            {"board_id": 1},
            sample_oauth_credential
        )

        assert "Sprint 1" in result
        assert "active" in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_search_users(self, mock_request, sample_oauth_credential):
        """Test searching users."""
        connector = JiraConnector()

        # Mock the Jira API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "accountId": "557058:12345",
                "displayName": "Test User",
                "emailAddress": "test@example.com",
                "active": True
            }
        ]
        mock_request.return_value = mock_response

        result = await connector._search_users(
            "test-cloud-id",
            {"query": "test"},
            sample_oauth_credential
        )

        assert "Test User" in result
        assert "557058:12345" in result

    @pytest.mark.asyncio
    @patch('sage_mcp.connectors.jira.JiraConnector._make_authenticated_request')
    async def test_add_comment(self, mock_request, sample_oauth_credential):
        """Test adding a comment."""
        connector = JiraConnector()

        # Mock the Jira API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "10001",
            "created": "2024-01-01T00:00:00.000Z",
            "author": {"displayName": "Test User"}
        }
        mock_request.return_value = mock_response

        result = await connector._add_comment(
            "test-cloud-id",
            {"issue_key": "PROJ-123", "body": "Test comment"},
            sample_oauth_credential
        )

        assert "10001" in result

    @pytest.mark.asyncio
    async def test_read_resource_project(self, sample_connector, sample_oauth_credential):
        """Test reading a project resource."""
        connector = JiraConnector()

        with patch.object(connector, '_get_cloud_id', return_value='test-cloud-id'):
            with patch.object(connector, '_make_authenticated_request') as mock_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "key": "PROJ",
                    "name": "Test Project"
                }
                mock_request.return_value = mock_response

                result = await connector.read_resource(
                    sample_connector,
                    "project/PROJ",
                    sample_oauth_credential
                )

                assert "PROJ" in result
                assert "Test Project" in result

    @pytest.mark.asyncio
    async def test_read_resource_issue(self, sample_connector, sample_oauth_credential):
        """Test reading an issue resource."""
        connector = JiraConnector()

        with patch.object(connector, '_get_cloud_id', return_value='test-cloud-id'):
            with patch.object(connector, '_make_authenticated_request') as mock_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "key": "PROJ-123",
                    "fields": {"summary": "Test issue"}
                }
                mock_request.return_value = mock_response

                result = await connector.read_resource(
                    sample_connector,
                    "issue/PROJ-123",
                    sample_oauth_credential
                )

                assert "PROJ-123" in result

    @pytest.mark.asyncio
    async def test_read_resource_invalid(self, sample_connector, sample_oauth_credential):
        """Test reading an invalid resource."""
        connector = JiraConnector()

        with patch.object(connector, '_get_cloud_id', return_value='test-cloud-id'):
            result = await connector.read_resource(
                sample_connector,
                "invalid",
                sample_oauth_credential
            )

            assert "Error" in result

    def test_validate_oauth_credential_valid(self, sample_oauth_credential):
        """Test validating valid OAuth credential."""
        connector = JiraConnector()

        assert connector.validate_oauth_credential(sample_oauth_credential) is True

    def test_validate_oauth_credential_none(self):
        """Test validating None OAuth credential."""
        connector = JiraConnector()

        assert connector.validate_oauth_credential(None) is False

    def test_validate_oauth_credential_inactive(self, sample_oauth_credential):
        """Test validating inactive OAuth credential."""
        connector = JiraConnector()

        sample_oauth_credential.is_active = False
        assert connector.validate_oauth_credential(sample_oauth_credential) is False

    def test_get_api_base_url(self):
        """Test constructing API base URL."""
        connector = JiraConnector()

        url = connector._get_api_base_url("test-cloud-id")
        assert url == "https://api.atlassian.com/ex/jira/test-cloud-id/rest/api/3"
