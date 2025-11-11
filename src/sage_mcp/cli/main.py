"""SageMCP CLI main entry point."""

import sys

import typer
from rich.console import Console

from sage_mcp.cli import __version__
from sage_mcp.cli.client import SageMCPClient
from sage_mcp.cli.commands import config_cmd, connector, mcp, oauth, tenant
from sage_mcp.cli.config import config_manager
from sage_mcp.cli.utils.output import print_error, print_info

# Create main app
app = typer.Typer(
    name="sagemcp",
    help="SageMCP CLI - Command-line interface for SageMCP platform",
    no_args_is_help=True,
)

console = Console()

# Add command groups
app.add_typer(config_cmd.app, name="config")
app.add_typer(tenant.app, name="tenant")
app.add_typer(connector.app, name="connector")
app.add_typer(oauth.app, name="oauth")
app.add_typer(mcp.app, name="mcp")


@app.command()
def version(
    verbose: bool = typer.Option(False, help="Show detailed version info"),
) -> None:
    """Show version information."""
    console.print(f"[bold]SageMCP CLI[/bold] v{__version__}")

    if verbose:
        console.print(f"Python: {sys.version.split()[0]}")

        # Try to get server info
        try:
            profile_config = config_manager.get_profile()
            client = SageMCPClient(profile_config)

            console.print(f"API URL: [cyan]{profile_config.base_url}[/cyan]")

            if client.ping():
                console.print("Server: [green]reachable ✓[/green]")
            else:
                console.print("Server: [red]not reachable ✗[/red]")

        except Exception:
            console.print("Server: [yellow]not configured[/yellow]")


@app.command()
def init() -> None:
    """Quick setup wizard for SageMCP CLI."""
    console.print("\n[bold green]Welcome to SageMCP CLI![/bold green]\n")
    console.print("This wizard will help you set up your CLI configuration.\n")

    # Initialize config
    from sage_mcp.cli.commands.config_cmd import init_config

    init_config()

    console.print("\n[bold]Quick Start:[/bold]")
    console.print("1. List tenants:      [cyan]sagemcp tenant list[/cyan]")
    console.print("2. Create tenant:     [cyan]sagemcp tenant create[/cyan]")
    console.print("3. List connectors:   [cyan]sagemcp connector list <tenant-slug>[/cyan]")
    console.print("4. Get help:          [cyan]sagemcp --help[/cyan]\n")


def main() -> None:
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
