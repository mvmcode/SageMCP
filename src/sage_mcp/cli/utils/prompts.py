"""Interactive prompt utilities."""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def confirm(message: str, default: bool = False) -> bool:
    """Prompt for confirmation.

    Args:
        message: Prompt message
        default: Default value

    Returns:
        User's confirmation
    """
    return Confirm.ask(message, default=default)


def prompt_text(
    message: str, default: Optional[str] = None, password: bool = False
) -> str:
    """Prompt for text input.

    Args:
        message: Prompt message
        default: Default value
        password: Hide input

    Returns:
        User's input
    """
    return Prompt.ask(message, default=default, password=password)


def prompt_choice(message: str, choices: List[str], default: Optional[str] = None) -> str:
    """Prompt for choice from list.

    Args:
        message: Prompt message
        choices: List of choices
        default: Default choice

    Returns:
        User's choice
    """
    return Prompt.ask(message, choices=choices, default=default)


def prompt_tenant_create() -> Dict[str, Any]:
    """Interactive prompt for creating a tenant.

    Returns:
        Dictionary with tenant data
    """
    console.print("\n[bold]Create New Tenant[/bold]\n")

    slug = prompt_text("Tenant slug (lowercase, alphanumeric, hyphens)")
    name = prompt_text("Display name")
    description = prompt_text("Description (optional)", default="")
    contact_email = prompt_text("Contact email (optional)", default="")

    data = {"slug": slug, "name": name}
    if description:
        data["description"] = description
    if contact_email:
        data["contact_email"] = contact_email

    return data


def prompt_connector_create(available_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """Interactive prompt for creating a connector.

    Args:
        available_types: Optional list of available connector types from API

    Returns:
        Dictionary with connector data
    """
    console.print("\n[bold]Create New Connector[/bold]\n")

    # Use provided types if available, otherwise use default list
    if available_types:
        connector_types = sorted(available_types)
    else:
        connector_types = [
            "github",
            "gitlab",
            "slack",
            "jira",
            "google_docs",
            "notion",
            "confluence",
            "linear",
            "teams",
            "discord",
            "zoom",
        ]

    connector_type = prompt_choice("Connector type", connector_types)
    name = prompt_text("Display name")
    description = prompt_text("Description (optional)", default="")

    data = {"connector_type": connector_type, "name": name}
    if description:
        data["description"] = description

    return data


def prompt_profile_create() -> Dict[str, Any]:
    """Interactive prompt for creating a profile.

    Returns:
        Dictionary with profile data
    """
    console.print("\n[bold]Create New Profile[/bold]\n")

    name = prompt_text("Profile name", default="default")
    base_url = prompt_text("API base URL", default="http://localhost:8000")
    api_key = prompt_text("API key (optional, press Enter to skip)", default="", password=True)

    data = {"name": name, "base_url": base_url}
    if api_key:
        data["api_key"] = api_key

    return data
