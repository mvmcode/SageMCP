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
    """Start OAuth authorization flow.

    This command opens your browser to authorize with the OAuth provider.
    The backend handles the OAuth callback and the CLI polls for the result.
    """
    try:
        import uuid
        import time

        client = get_client(profile)

        # Generate unique CLI session ID
        session_id = f"cli-session-{uuid.uuid4()}"

        print_info(f"Starting OAuth authorization for {provider}...")
        print_info(f"Session ID: {session_id}\n")

        # Build auth URL with CLI session ID in state
        # The backend will detect this and store the result for polling
        auth_url = client.get_oauth_auth_url(
            tenant_slug,
            provider,
            redirect_uri=None,  # Use backend's default callback
            state=session_id     # Session ID as state parameter
        )

        print_info(f"Authorization URL: {auth_url}\n")

        if browser:
            print_info("Opening browser for authorization...")
            webbrowser.open(auth_url)
        else:
            print_info("Please open this URL in your browser to authorize:")
            print(auth_url)

        print_info("\nWaiting for authorization (timeout: 5 minutes)...")
        print_info("Please complete the authorization in your browser.\n")

        # Poll for result
        max_attempts = 60  # 5 minutes (60 * 5 seconds)
        poll_interval = 5  # seconds

        for attempt in range(max_attempts):
            try:
                # Try to get the session result
                result = client.get_cli_session_result(session_id)

                # Success!
                if result.get("status") == "success":
                    print_success(f"\n✓ Successfully authorized {provider} for tenant '{tenant_slug}'")
                    print_info(f"Provider User: {result.get('provider_username', 'N/A')}")
                    print_info(f"Provider User ID: {result.get('provider_user_id', 'N/A')}")

                    if result.get('expires_at'):
                        print_info(f"Token expires: {result['expires_at']}")

                    print_info("\nYou can now use this connector with MCP tools.")
                    return

                # Error in OAuth flow
                elif result.get("status") == "error":
                    print_error(f"OAuth authorization failed: {result.get('error', 'Unknown error')}")
                    if result.get('error_description'):
                        print_error(f"Details: {result['error_description']}")
                    sys.exit(3)

            except APIError as e:
                # 404 means session not ready yet, keep polling
                if e.status_code == 404:
                    if attempt % 6 == 0:  # Print progress every 30 seconds
                        dots = "." * (attempt // 6 % 4)
                        print(f"Still waiting{dots}    ", end="\r", flush=True)
                    time.sleep(poll_interval)
                    continue
                else:
                    # Other errors are real problems
                    raise

        # Timeout
        print_error("\n\nAuthorization timed out after 5 minutes.")
        print_info("\nTroubleshooting tips:")
        print_info("  1. Make sure you completed the authorization in your browser")
        print_info("  2. Check that your OAuth app configuration is correct")
        print_info("  3. Verify OAuth credentials are set (env vars or tenant config)")
        print_info("  4. Check backend logs for errors")
        sys.exit(3)

    except APIError as e:
        print_error(f"Failed to authorize: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except KeyboardInterrupt:
        print_error("\n\nAuthorization cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@app.command("status")
def oauth_status(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    provider: Optional[str] = typer.Argument(None, help="OAuth provider (optional)"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Check OAuth authorization status for a tenant.

    If provider is specified, shows status for that provider only.
    Otherwise, shows status for all providers.
    """
    try:
        client = get_client(profile)

        if provider:
            # Check status for specific provider
            try:
                credential = client.get_oauth_credential(tenant_slug, provider)
                print_success(f"✓ {provider} is authorized for tenant '{tenant_slug}'")
                print_info(f"Provider User: {credential.get('provider_username', 'N/A')}")
                print_info(f"Provider User ID: {credential.get('provider_user_id', 'N/A')}")
                print_info(f"Active: {credential.get('is_active', False)}")

                if credential.get('expires_at'):
                    print_info(f"Expires: {credential['expires_at']}")

                if format != "table":
                    output_data(credential, format)

            except APIError as e:
                if e.status_code == 404:
                    print_error(f"✗ {provider} is NOT authorized for tenant '{tenant_slug}'")
                    print_info(f"Run: sagemcp oauth authorize {tenant_slug} {provider}")
                    sys.exit(1)
                else:
                    raise

        else:
            # Check status for all providers
            credentials = client.list_oauth_credentials(tenant_slug)

            if format == "table":
                output_table_oauth_credentials(credentials, tenant_slug)
            else:
                output_data(credentials, format)

            if not credentials:
                print_info(f"\nNo OAuth providers authorized for tenant '{tenant_slug}'")
                print_info("Run: sagemcp oauth providers  # to see available providers")
                print_info("Run: sagemcp oauth authorize <tenant> <provider>  # to authorize")

    except APIError as e:
        print_error(f"Failed to check OAuth status: {e.message}")
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


@app.command("config-set")
def config_set(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    provider: str = typer.Argument(..., help="OAuth provider (github, slack, etc.)"),
    client_id: str = typer.Option(..., help="OAuth client ID"),
    client_secret: str = typer.Option(..., help="OAuth client secret"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Set OAuth configuration for a tenant.

    This allows you to configure tenant-specific OAuth credentials
    instead of using global environment variables.

    Example:
        sagemcp oauth config-set my-tenant github \\
            --client-id Iv1.abc123 \\
            --client-secret 1234567890abcdef
    """
    try:
        client = get_client(profile)

        print_info(f"Setting OAuth config for {provider}...")

        config = client.create_oauth_config(
            tenant_slug,
            provider,
            client_id,
            client_secret
        )

        print_success(f"✓ OAuth configuration set for {provider}")
        print_info(f"Provider: {config.get('provider')}")
        print_info(f"Client ID: {config.get('client_id')}")
        print_info(f"Active: {config.get('is_active', True)}")

        if format != "table":
            output_data(config, format)

        print_info(f"\nYou can now authorize: sagemcp oauth authorize {tenant_slug} {provider}")

    except APIError as e:
        print_error(f"Failed to set OAuth config: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("config-list")
def config_list(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List OAuth configurations for a tenant.

    Shows tenant-specific OAuth app configurations.
    """
    try:
        client = get_client(profile)
        configs = client.list_oauth_configs(tenant_slug)

        if format == "table":
            from rich.console import Console
            from rich.table import Table

            console = Console()
            table = Table(title=f"OAuth Configurations for '{tenant_slug}'")
            table.add_column("Provider", style="cyan")
            table.add_column("Client ID", style="green")
            table.add_column("Active", style="yellow")
            table.add_column("Created", style="blue")

            for config in configs:
                table.add_row(
                    config.get('provider', 'N/A'),
                    config.get('client_id', 'N/A'),
                    "✓" if config.get('is_active', True) else "✗",
                    config.get('created_at', 'N/A')[:10] if config.get('created_at') else 'N/A'
                )

            console.print(table)
        else:
            output_data(configs, format)

        if not configs:
            print_info(f"\nNo OAuth configurations found for tenant '{tenant_slug}'")
            print_info("Using global environment variables instead (if configured)")

    except APIError as e:
        print_error(f"Failed to list OAuth configs: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("config-delete")
def config_delete(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    provider: str = typer.Argument(..., help="OAuth provider"),
    force: bool = typer.Option(False, help="Skip confirmation"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Delete OAuth configuration for a tenant.

    This removes the tenant-specific OAuth configuration.
    The system will fall back to global environment variables if configured.
    """
    try:
        if not force:
            if not confirm(
                f"Are you sure you want to delete {provider} OAuth config for tenant '{tenant_slug}'?"
            ):
                print_error("Cancelled")
                sys.exit(0)

        client = get_client(profile)
        result = client.delete_oauth_config(tenant_slug, provider)

        print_success(f"✓ Deleted {provider} OAuth configuration")
        print_info(result.get("message", ""))
        print_info("\nSystem will now use global environment variables (if configured)")

    except APIError as e:
        print_error(f"Failed to delete OAuth config: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
