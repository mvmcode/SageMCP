"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from sage_mcp.cli.commands.tenant import app as tenant_app


runner = CliRunner()


@pytest.fixture
def mock_client():
    """Mock SageMCPClient."""
    with patch("sage_mcp.cli.commands.tenant.get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_list_tenants_success(mock_client):
    """Test listing tenants successfully."""
    mock_client.list_tenants.return_value = [
        {"slug": "test", "name": "Test Tenant", "is_active": True}
    ]

    result = runner.invoke(tenant_app, ["list"])

    assert result.exit_code == 0
    mock_client.list_tenants.assert_called_once()


def test_show_tenant_success(mock_client):
    """Test showing tenant details successfully."""
    mock_client.get_tenant.return_value = {
        "slug": "test",
        "name": "Test Tenant",
        "is_active": True,
    }

    result = runner.invoke(tenant_app, ["show", "test"])

    assert result.exit_code == 0
    mock_client.get_tenant.assert_called_once_with("test")


def test_create_tenant_non_interactive(mock_client):
    """Test creating tenant in non-interactive mode."""
    mock_client.create_tenant.return_value = {
        "slug": "test",
        "name": "Test Tenant",
        "is_active": True,
    }

    result = runner.invoke(
        tenant_app,
        ["create", "--slug", "test", "--name", "Test Tenant", "--no-interactive"],
    )

    assert result.exit_code == 0
    mock_client.create_tenant.assert_called_once()


def test_update_tenant_success(mock_client):
    """Test updating tenant successfully."""
    mock_client.update_tenant.return_value = {
        "slug": "test",
        "name": "Updated Name",
        "is_active": True,
    }

    result = runner.invoke(tenant_app, ["update", "test", "--name", "Updated Name"])

    assert result.exit_code == 0
    mock_client.update_tenant.assert_called_once()


def test_delete_tenant_with_force(mock_client):
    """Test deleting tenant with force flag."""
    result = runner.invoke(tenant_app, ["delete", "test", "--force"])

    assert result.exit_code == 0
    mock_client.delete_tenant.assert_called_once_with("test")


def test_update_tenant_no_fields():
    """Test updating tenant with no fields fails."""
    result = runner.invoke(tenant_app, ["update", "test"])

    assert result.exit_code == 2
