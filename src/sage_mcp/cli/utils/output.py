"""Output formatting utilities."""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from rich.console import Console
from rich.table import Table

console = Console()


def format_datetime(dt: Any) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime string or object

    Returns:
        Formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt

    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M")

    return str(dt)


def format_boolean(value: bool) -> str:
    """Format boolean for display.

    Args:
        value: Boolean value

    Returns:
        Checkmark or X
    """
    return "✓" if value else "✗"


def output_json(data: Any) -> None:
    """Output data as JSON.

    Args:
        data: Data to output
    """
    console.print_json(json.dumps(data, indent=2, default=str))


def output_yaml(data: Any) -> None:
    """Output data as YAML.

    Args:
        data: Data to output
    """
    print(yaml.dump(data, default_flow_style=False, sort_keys=False))


def output_table_tenants(tenants: List[Dict[str, Any]]) -> None:
    """Output tenants as a table.

    Args:
        tenants: List of tenant dictionaries
    """
    table = Table(title="Tenants")
    table.add_column("Slug", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Active", style="yellow")
    table.add_column("Contact Email")
    table.add_column("Created")

    for tenant in tenants:
        table.add_row(
            tenant["slug"],
            tenant["name"],
            format_boolean(tenant.get("is_active", True)),
            tenant.get("contact_email") or "-",
            format_datetime(tenant.get("created_at", "")),
        )

    console.print(table)


def output_table_tenant(tenant: Dict[str, Any]) -> None:
    """Output single tenant details.

    Args:
        tenant: Tenant dictionary
    """
    table = Table(title=f"Tenant: {tenant['slug']}")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Slug", tenant["slug"])
    table.add_row("Name", tenant["name"])
    table.add_row("Description", tenant.get("description") or "-")
    table.add_row("Active", format_boolean(tenant.get("is_active", True)))
    table.add_row("Contact Email", tenant.get("contact_email") or "-")
    table.add_row("Created", format_datetime(tenant.get("created_at", "")))
    table.add_row("Updated", format_datetime(tenant.get("updated_at", "")))

    console.print(table)


def output_table_connectors(connectors: List[Dict[str, Any]], tenant_slug: str) -> None:
    """Output connectors as a table.

    Args:
        connectors: List of connector dictionaries
        tenant_slug: Tenant slug
    """
    table = Table(title=f"Connectors for tenant: {tenant_slug}")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Enabled", style="yellow")
    table.add_column("Created")

    for connector in connectors:
        # Truncate ID for display
        connector_id = connector["id"]
        short_id = connector_id[:8] + "..." if len(connector_id) > 8 else connector_id

        table.add_row(
            short_id,
            connector["connector_type"],
            connector["name"],
            format_boolean(connector.get("is_enabled", True)),
            format_datetime(connector.get("created_at", "")),
        )

    console.print(table)


def output_table_connector(connector: Dict[str, Any]) -> None:
    """Output single connector details.

    Args:
        connector: Connector dictionary
    """
    table = Table(title=f"Connector: {connector['name']}")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("ID", connector["id"])
    table.add_row("Type", connector["connector_type"])
    table.add_row("Name", connector["name"])
    table.add_row("Description", connector.get("description") or "-")
    table.add_row("Enabled", format_boolean(connector.get("is_enabled", True)))
    table.add_row("Created", format_datetime(connector.get("created_at", "")))
    table.add_row("Updated", format_datetime(connector.get("updated_at", "")))

    if connector.get("configuration"):
        table.add_row("Configuration", json.dumps(connector["configuration"], indent=2))

    console.print(table)


def output_table_oauth_credentials(
    credentials: List[Dict[str, Any]], tenant_slug: str
) -> None:
    """Output OAuth credentials as a table.

    Args:
        credentials: List of credential dictionaries
        tenant_slug: Tenant slug
    """
    table = Table(title=f"OAuth Credentials for tenant: {tenant_slug}")
    table.add_column("Provider", style="cyan")
    table.add_column("User ID", style="green")
    table.add_column("Username", style="green")
    table.add_column("Scopes")
    table.add_column("Status", style="yellow")
    table.add_column("Expires")

    for cred in credentials:
        # Determine status
        status = "✓" if cred.get("is_active") else "✗"
        if cred.get("expires_at"):
            try:
                expires = datetime.fromisoformat(cred["expires_at"].replace("Z", "+00:00"))
                if expires < datetime.now(expires.tzinfo):
                    status = "⚠ Expired"
            except Exception:
                pass

        table.add_row(
            cred["provider"],
            cred.get("provider_user_id") or "-",
            cred.get("provider_username") or "-",
            cred.get("scopes") or "-",
            status,
            format_datetime(cred.get("expires_at", "")) if cred.get("expires_at") else "Never",
        )

    console.print(table)


def output_table_oauth_providers(providers: List[Dict[str, Any]]) -> None:
    """Output OAuth providers as a table.

    Args:
        providers: List of provider dictionaries
    """
    table = Table(title="Available OAuth Providers")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Configured", style="yellow")
    table.add_column("Scopes")

    for provider in providers:
        table.add_row(
            provider["id"],
            provider["name"],
            format_boolean(provider.get("configured", False)),
            ", ".join(provider.get("scopes", [])),
        )

    console.print(table)


def output_table_mcp_tools(tools: List[Dict[str, Any]], connector_name: str) -> None:
    """Output MCP tools as a table.

    Args:
        tools: List of tool dictionaries
        connector_name: Connector name
    """
    table = Table(title=f"MCP Tools for: {connector_name}")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Description", style="green")

    for tool in tools:
        table.add_row(
            tool.get("name", ""),
            tool.get("description", ""),
        )

    console.print(table)
    console.print(f"\nTotal: {len(tools)} tools")


def output_table_mcp_resources(
    resources: List[Dict[str, Any]], connector_name: str
) -> None:
    """Output MCP resources as a table.

    Args:
        resources: List of resource dictionaries
        connector_name: Connector name
    """
    table = Table(title=f"MCP Resources for: {connector_name}")
    table.add_column("URI", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")

    for resource in resources:
        table.add_row(
            resource.get("uri", ""),
            resource.get("name", ""),
            resource.get("description", ""),
        )

    console.print(table)
    console.print(f"\nTotal: {len(resources)} resources")


def output_data(
    data: Any, format_type: str = "table", table_func: Optional[callable] = None
) -> None:
    """Output data in specified format.

    Args:
        data: Data to output
        format_type: Output format (table, json, yaml)
        table_func: Optional function to format as table
    """
    if format_type == "json":
        output_json(data)
    elif format_type == "yaml":
        output_yaml(data)
    elif format_type == "table" and table_func:
        table_func(data)
    else:
        # Fallback to JSON
        output_json(data)


def print_error(message: str) -> None:
    """Print error message.

    Args:
        message: Error message
    """
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print success message.

    Args:
        message: Success message
    """
    console.print(f"[bold green]Success:[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print warning message.

    Args:
        message: Warning message
    """
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print info message.

    Args:
        message: Info message
    """
    console.print(f"[bold blue]Info:[/bold blue] {message}")
