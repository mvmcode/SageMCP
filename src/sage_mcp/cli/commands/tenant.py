"""Tenant management commands."""

import sys
from typing import Optional

import typer

from sage_mcp.cli.client import APIError, SageMCPClient
from sage_mcp.cli.config import config_manager
from sage_mcp.cli.utils.output import (
    output_data,
    output_table_tenant,
    output_table_tenants,
    print_error,
    print_success,
)
from sage_mcp.cli.utils.prompts import confirm, prompt_tenant_create

app = typer.Typer(help="Tenant management commands")


def get_client(profile: Optional[str] = None) -> SageMCPClient:
    """Get API client for profile."""
    try:
        profile_config = config_manager.get_profile(profile)
        return SageMCPClient(profile_config)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


@app.command("list")
def list_tenants(
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List all tenants."""
    try:
        client = get_client(profile)
        tenants = client.list_tenants()

        if format == "table":
            output_table_tenants(tenants)
        else:
            output_data(tenants, format)

    except APIError as e:
        print_error(f"Failed to list tenants: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("show")
def show_tenant(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Show tenant details."""
    try:
        client = get_client(profile)
        tenant = client.get_tenant(tenant_slug)

        if format == "table":
            output_table_tenant(tenant)
        else:
            output_data(tenant, format)

    except APIError as e:
        print_error(f"Failed to get tenant: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("create")
def create_tenant(
    slug: Optional[str] = typer.Option(None, help="Tenant slug"),
    name: Optional[str] = typer.Option(None, help="Display name"),
    description: Optional[str] = typer.Option(None, help="Description"),
    contact_email: Optional[str] = typer.Option(None, help="Contact email"),
    interactive: bool = typer.Option(True, help="Interactive mode"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Create a new tenant."""
    try:
        # Interactive mode if no slug/name provided
        if interactive and (not slug or not name):
            data = prompt_tenant_create()
        else:
            if not slug or not name:
                print_error("--slug and --name are required in non-interactive mode")
                sys.exit(2)

            data = {"slug": slug, "name": name}
            if description:
                data["description"] = description
            if contact_email:
                data["contact_email"] = contact_email

        client = get_client(profile)
        tenant = client.create_tenant(**data)

        print_success(f"Created tenant: {tenant['slug']}")

        if format == "table":
            output_table_tenant(tenant)
        else:
            output_data(tenant, format)

    except APIError as e:
        print_error(f"Failed to create tenant: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("update")
def update_tenant(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    name: Optional[str] = typer.Option(None, help="New display name"),
    description: Optional[str] = typer.Option(None, help="New description"),
    contact_email: Optional[str] = typer.Option(None, help="New contact email"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Update tenant."""
    try:
        if not name and not description and contact_email is None:
            print_error("At least one field must be specified to update")
            sys.exit(2)

        client = get_client(profile)
        tenant = client.update_tenant(
            tenant_slug, name=name, description=description, contact_email=contact_email
        )

        print_success(f"Updated tenant: {tenant['slug']}")

        if format == "table":
            output_table_tenant(tenant)
        else:
            output_data(tenant, format)

    except APIError as e:
        print_error(f"Failed to update tenant: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("delete")
def delete_tenant(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    force: bool = typer.Option(False, help="Skip confirmation"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Delete tenant."""
    try:
        if not force:
            if not confirm(
                f"Are you sure you want to delete tenant '{tenant_slug}'? This will delete all connectors and credentials."
            ):
                print_error("Cancelled")
                sys.exit(0)

        client = get_client(profile)
        result = client.delete_tenant(tenant_slug)

        print_success(f"Deleted tenant: {tenant_slug}")

    except APIError as e:
        print_error(f"Failed to delete tenant: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
