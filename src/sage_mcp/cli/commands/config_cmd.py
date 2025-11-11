"""Configuration management commands."""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from sage_mcp.cli.config import config_manager
from sage_mcp.cli.utils.output import print_error, print_success
from sage_mcp.cli.utils.prompts import confirm, prompt_profile_create

app = typer.Typer(help="Configuration management commands")
console = Console()


@app.command("init")
def init_config(
    interactive: bool = typer.Option(True, help="Interactive mode"),
    profile: str = typer.Option("default", help="Profile name"),
    base_url: str = typer.Option("http://localhost:8000", help="API base URL"),
    api_key: Optional[str] = typer.Option(None, help="API key"),
) -> None:
    """Initialize CLI configuration."""
    try:
        # Check if config already exists
        config_manager.ensure_config_dir()

        if config_manager.config_file.exists():
            if not confirm(
                "Configuration file already exists. Do you want to reinitialize?"
            ):
                print_error("Cancelled")
                sys.exit(0)

        # Interactive mode
        if interactive:
            data = prompt_profile_create()
            profile = data.get("name", "default")
            base_url = data.get("base_url", "http://localhost:8000")
            api_key = data.get("api_key")

        # Create profile
        config_manager.add_profile(profile, base_url, api_key)

        # Set as default
        config_manager.set_default_profile(profile)

        print_success(f"Configuration initialized with profile '{profile}'")
        console.print(f"Config file: [cyan]{config_manager.config_file}[/cyan]")

    except Exception as e:
        print_error(f"Failed to initialize configuration: {e}")
        sys.exit(1)


@app.command("list")
def list_profiles(
    show_secrets: bool = typer.Option(False, help="Show API keys/secrets"),
) -> None:
    """List all profiles."""
    try:
        config = config_manager.load()
        profiles = config.profiles

        if not profiles:
            console.print("[yellow]No profiles found. Run 'sagemcp config init' to create one.[/yellow]")
            return

        table = Table(title="CLI Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("Base URL", style="green")
        table.add_column("API Key", style="yellow")
        table.add_column("Default", style="magenta")

        for name, profile in profiles.items():
            is_default = "✓" if name == config.settings.default_profile else ""

            # Mask API key unless show_secrets is True
            api_key_display = "-"
            if profile.api_key:
                if show_secrets:
                    api_key_display = profile.api_key
                else:
                    api_key_display = f"{profile.api_key[:4]}...{profile.api_key[-4:]}" if len(profile.api_key) > 8 else "****"

            table.add_row(name, profile.base_url, api_key_display, is_default)

        console.print(table)

    except Exception as e:
        print_error(f"Failed to list profiles: {e}")
        sys.exit(1)


@app.command("show")
def show_profile(
    profile: Optional[str] = typer.Argument(None, help="Profile name (default: current default)"),
) -> None:
    """Show profile details."""
    try:
        config = config_manager.load()

        if profile is None:
            profile = config.settings.default_profile

        if profile not in config.profiles:
            print_error(f"Profile '{profile}' not found")
            sys.exit(1)

        prof = config.profiles[profile]

        table = Table(title=f"Profile: {profile}")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Base URL", prof.base_url)
        table.add_row("API Key", prof.api_key if prof.api_key else "-")
        table.add_row("Output Format", prof.output_format)
        table.add_row("Timeout", str(prof.timeout))

        console.print(table)

    except Exception as e:
        print_error(f"Failed to show profile: {e}")
        sys.exit(1)


@app.command("set")
def set_value(
    key: str = typer.Argument(..., help="Configuration key (e.g., base_url, api_key)"),
    value: str = typer.Argument(..., help="Configuration value"),
    profile: Optional[str] = typer.Option(None, help="Profile name"),
) -> None:
    """Set configuration value."""
    try:
        config = config_manager.load()

        # Get profile
        profile_name = profile or config.settings.default_profile
        if profile_name not in config.profiles:
            print_error(f"Profile '{profile_name}' not found")
            sys.exit(1)

        prof = config.profiles[profile_name]

        # Set value
        if key == "base_url":
            prof.base_url = value
        elif key == "api_key":
            prof.api_key = value
        elif key == "output_format":
            prof.output_format = value
        elif key == "timeout":
            prof.timeout = int(value)
        else:
            print_error(f"Unknown configuration key: {key}")
            sys.exit(1)

        # Save
        config_manager.save(config)

        print_success(f"Set {key} = {value} for profile '{profile_name}'")

    except ValueError as e:
        print_error(f"Invalid value: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to set configuration: {e}")
        sys.exit(1)


@app.command("delete")
def delete_profile(
    profile: str = typer.Argument(..., help="Profile name"),
    force: bool = typer.Option(False, help="Skip confirmation"),
) -> None:
    """Delete a profile."""
    try:
        if not force:
            if not confirm(f"Are you sure you want to delete profile '{profile}'?"):
                print_error("Cancelled")
                sys.exit(0)

        config_manager.delete_profile(profile)
        print_success(f"Deleted profile: {profile}")

    except ValueError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to delete profile: {e}")
        sys.exit(1)
