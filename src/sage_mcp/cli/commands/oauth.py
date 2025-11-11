"""OAuth management commands."""

import sys
import webbrowser
from typing import Optional

import typer

from sage_mcp.cli.client import APIError, SageMCPClient
from sage_mcp.cli.config import config_manager
from sage_mcp.cli.utils.output import (
    output_data,
    output_table_oauth_credentials,
    output_table_oauth_providers,
    print_error,
    print_info,
    print_success,
)
from sage_mcp.cli.utils.prompts import confirm

app = typer.Typer(help="OAuth management commands")


def get_client(profile: Optional[str] = None) -> SageMCPClient:
    """Get API client for profile."""
    try:
        profile_config = config_manager.get_profile(profile)
        return SageMCPClient(profile_config)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


@app.command("providers")
def list_providers(
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List available OAuth providers."""
    try:
        client = get_client(profile)
        providers = client.list_oauth_providers()

        if format == "table":
            output_table_oauth_providers(providers)
        else:
            output_data(providers, format)

    except APIError as e:
        print_error(f"Failed to list providers: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("list")
def list_credentials(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List OAuth credentials for a tenant."""
    try:
        client = get_client(profile)
        credentials = client.list_oauth_credentials(tenant_slug)

        if format == "table":
            output_table_oauth_credentials(credentials, tenant_slug)
        else:
            output_data(credentials, format)

    except APIError as e:
        print_error(f"Failed to list OAuth credentials: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("authorize")
def authorize(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    provider: str = typer.Argument(..., help="OAuth provider"),
    browser: bool = typer.Option(True, help="Open browser automatically"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Start OAuth authorization flow."""
    try:
        client = get_client(profile)
        auth_url = client.get_oauth_auth_url(tenant_slug, provider)

        print_info(f"OAuth authorization URL for {provider}:")
        print(auth_url)

        if browser:
            print_info("Opening browser...")
            webbrowser.open(auth_url)
        else:
            print_info("Please open this URL in your browser to authorize")

        print_info(
            "After authorization, the credentials will be stored automatically"
        )

    except APIError as e:
        print_error(f"Failed to get authorization URL: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("revoke")
def revoke_credentials(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    provider: str = typer.Argument(..., help="OAuth provider"),
    force: bool = typer.Option(False, help="Skip confirmation"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Revoke OAuth credentials."""
    try:
        if not force:
            if not confirm(
                f"Are you sure you want to revoke {provider} credentials for tenant '{tenant_slug}'?"
            ):
                print_error("Cancelled")
                sys.exit(0)

        client = get_client(profile)
        result = client.revoke_oauth_credential(tenant_slug, provider)

        print_success(f"Revoked {provider} credentials")
        print_info(result.get("message", ""))

    except APIError as e:
        print_error(f"Failed to revoke credentials: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
