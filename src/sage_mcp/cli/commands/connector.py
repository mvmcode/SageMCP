"""Connector management commands."""

import sys
from typing import Optional

import typer

from sage_mcp.cli.client import APIError, SageMCPClient
from sage_mcp.cli.config import config_manager
from sage_mcp.cli.utils.output import (
    output_data,
    output_table_connector,
    output_table_connectors,
    print_error,
    print_success,
)
from sage_mcp.cli.utils.prompts import confirm, prompt_connector_create

app = typer.Typer(help="Connector management commands")


def get_client(profile: Optional[str] = None) -> SageMCPClient:
    """Get API client for profile."""
    try:
        profile_config = config_manager.get_profile(profile)
        return SageMCPClient(profile_config)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


@app.command("list")
def list_connectors(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List connectors for a tenant."""
    try:
        client = get_client(profile)
        connectors = client.list_connectors(tenant_slug)

        if format == "table":
            output_table_connectors(connectors, tenant_slug)
        else:
            output_data(connectors, format)

    except APIError as e:
        print_error(f"Failed to list connectors: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("show")
def show_connector(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Show connector details."""
    try:
        client = get_client(profile)
        connector = client.get_connector(tenant_slug, connector_id)

        if format == "table":
            output_table_connector(connector)
        else:
            output_data(connector, format)

    except APIError as e:
        print_error(f"Failed to get connector: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("create")
def create_connector(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_type: Optional[str] = typer.Option(None, help="Connector type"),
    name: Optional[str] = typer.Option(None, help="Display name"),
    description: Optional[str] = typer.Option(None, help="Description"),
    interactive: bool = typer.Option(True, help="Interactive mode"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Create a new connector."""
    try:
        # Interactive mode if no type/name provided
        if interactive and (not connector_type or not name):
            data = prompt_connector_create()
        else:
            if not connector_type or not name:
                print_error("--type and --name are required in non-interactive mode")
                sys.exit(2)

            data = {"connector_type": connector_type, "name": name}
            if description:
                data["description"] = description

        client = get_client(profile)
        connector = client.create_connector(tenant_slug, **data)

        print_success(f"Created connector: {connector['name']} ({connector['id']})")

        if format == "table":
            output_table_connector(connector)
        else:
            output_data(connector, format)

    except APIError as e:
        print_error(f"Failed to create connector: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("update")
def update_connector(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    name: Optional[str] = typer.Option(None, help="New display name"),
    description: Optional[str] = typer.Option(None, help="New description"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Update connector."""
    try:
        if not name and not description:
            print_error("At least one field must be specified to update")
            sys.exit(2)

        client = get_client(profile)
        connector = client.update_connector(
            tenant_slug, connector_id, name=name, description=description
        )

        print_success(f"Updated connector: {connector['name']}")

        if format == "table":
            output_table_connector(connector)
        else:
            output_data(connector, format)

    except APIError as e:
        print_error(f"Failed to update connector: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("delete")
def delete_connector(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    force: bool = typer.Option(False, help="Skip confirmation"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Delete connector."""
    try:
        if not force:
            if not confirm(f"Are you sure you want to delete connector '{connector_id}'?"):
                print_error("Cancelled")
                sys.exit(0)

        client = get_client(profile)
        result = client.delete_connector(tenant_slug, connector_id)

        print_success(f"Deleted connector: {connector_id}")

    except APIError as e:
        print_error(f"Failed to delete connector: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("toggle")
def toggle_connector(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Toggle connector enabled status."""
    try:
        client = get_client(profile)
        connector = client.toggle_connector(tenant_slug, connector_id)

        status = "enabled" if connector.get("is_enabled") else "disabled"
        print_success(f"Connector {connector['name']} is now {status}")

        if format == "table":
            output_table_connector(connector)
        else:
            output_data(connector, format)

    except APIError as e:
        print_error(f"Failed to toggle connector: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("types")
def list_connector_types() -> None:
    """List available connector types."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Available Connector Types")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="green")

    types = [
        ("github", "GitHub"),
        ("gitlab", "GitLab"),
        ("slack", "Slack"),
        ("jira", "Jira"),
        ("google_docs", "Google Docs"),
        ("notion", "Notion"),
        ("confluence", "Confluence"),
        ("linear", "Linear"),
        ("teams", "Microsoft Teams"),
        ("discord", "Discord"),
        ("zoom", "Zoom"),
    ]

    for type_id, name in types:
        table.add_row(type_id, name)

    console.print(table)
