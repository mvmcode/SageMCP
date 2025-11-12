"""MCP testing and interaction commands."""

import json
import sys
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.syntax import Syntax

from sage_mcp.cli.client import APIError, SageMCPClient
from sage_mcp.cli.config import config_manager
from sage_mcp.cli.utils.output import (
    output_data,
    output_table_mcp_resources,
    output_table_mcp_tools,
    print_error,
    print_info,
    print_success,
)

app = typer.Typer(help="MCP testing and interaction commands")
console = Console()


def get_client(profile: Optional[str] = None) -> SageMCPClient:
    """Get API client for profile."""
    try:
        profile_config = config_manager.get_profile(profile)
        return SageMCPClient(profile_config)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


@app.command("info")
def get_info(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """Get MCP server info."""
    try:
        client = get_client(profile)
        info = client.get_mcp_info(tenant_slug, connector_id)

        output_data(info, format)

    except APIError as e:
        print_error(f"Failed to get MCP info: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("tools")
def list_tools(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    detailed: bool = typer.Option(False, help="Show detailed tool schemas"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List available MCP tools."""
    try:
        client = get_client(profile)
        tools = client.list_mcp_tools(tenant_slug, connector_id)

        if format == "table":
            # Get connector name for display
            try:
                connector = client.get_connector(tenant_slug, connector_id)
                connector_name = f"{tenant_slug}/{connector['name']}"
            except Exception:
                connector_name = f"{tenant_slug}/{connector_id}"

            output_table_mcp_tools(tools, connector_name)

            if detailed and tools:
                console.print("\n[bold]Tool Schemas:[/bold]\n")
                for tool in tools:
                    console.print(f"[cyan]{tool.get('name')}[/cyan]")
                    if tool.get("inputSchema"):
                        syntax = Syntax(
                            json.dumps(tool["inputSchema"], indent=2),
                            "json",
                            theme="monokai",
                        )
                        console.print(syntax)
                    console.print()
        else:
            output_data(tools, format)

    except APIError as e:
        print_error(f"Failed to list tools: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("resources")
def list_resources(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
) -> None:
    """List available MCP resources."""
    try:
        client = get_client(profile)
        resources = client.list_mcp_resources(tenant_slug, connector_id)

        if format == "table":
            # Get connector name for display
            try:
                connector = client.get_connector(tenant_slug, connector_id)
                connector_name = f"{tenant_slug}/{connector['name']}"
            except Exception:
                connector_name = f"{tenant_slug}/{connector_id}"

            output_table_mcp_resources(resources, connector_name)
        else:
            output_data(resources, format)

    except APIError as e:
        print_error(f"Failed to list resources: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("call")
def call_tool(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    tool_name: str = typer.Argument(..., help="Tool name"),
    args_json: Optional[str] = typer.Option(None, "--args", help="Arguments as JSON string"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Call an MCP tool."""
    try:
        # Parse arguments
        arguments = {}
        if args_json:
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON arguments: {e}")
                sys.exit(2)

        client = get_client(profile)
        result = client.call_mcp_tool(tenant_slug, connector_id, tool_name, arguments)

        print_success(f"Tool '{tool_name}' executed successfully")
        console.print("\n[bold]Result:[/bold]\n")

        # Pretty print result
        syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
        console.print(syntax)

    except APIError as e:
        print_error(f"Failed to call tool: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("read")
def read_resource(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    uri: str = typer.Argument(..., help="Resource URI"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Read an MCP resource."""
    try:
        client = get_client(profile)
        content = client.read_mcp_resource(tenant_slug, connector_id, uri)

        print_success(f"Resource '{uri}' read successfully")
        console.print("\n[bold]Content:[/bold]\n")
        console.print(content)

    except APIError as e:
        print_error(f"Failed to read resource: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("interactive")
def interactive_session(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Start an interactive MCP REPL session."""
    try:
        client = get_client(profile)

        # Get connector info
        try:
            connector = client.get_connector(tenant_slug, connector_id)
            connector_name = connector["name"]
            connector_type = connector["connector_type"]
        except Exception:
            connector_name = connector_id
            connector_type = "unknown"

        # Print welcome message
        console.print("\n[bold green]SageMCP Interactive Session[/bold green]")
        console.print(f"Tenant: [cyan]{tenant_slug}[/cyan] | Connector: [cyan]{connector_name}[/cyan] ([magenta]{connector_type}[/magenta])")
        console.print("Type 'help' for commands, 'exit' to quit\n")

        # REPL loop
        while True:
            try:
                # Get input
                line = console.input("[bold yellow]mcp>[/bold yellow] ").strip()

                if not line:
                    continue

                # Parse command
                parts = line.split(None, 1)
                command = parts[0].lower()

                # Handle commands
                if command in ["exit", "quit", "q"]:
                    console.print("[bold]Goodbye![/bold]")
                    break

                elif command == "help":
                    console.print("\n[bold]Available commands:[/bold]")
                    console.print("  [cyan]tools[/cyan]                    - List available tools")
                    console.print("  [cyan]resources[/cyan]                - List available resources")
                    console.print("  [cyan]call[/cyan] <tool> [args...]    - Call a tool with arguments")
                    console.print("  [cyan]read[/cyan] <uri>               - Read a resource")
                    console.print("  [cyan]info[/cyan]                     - Show MCP server info")
                    console.print("  [cyan]help[/cyan]                     - Show this help")
                    console.print("  [cyan]exit[/cyan]                     - Exit interactive session\n")

                elif command == "tools":
                    tools = client.list_mcp_tools(tenant_slug, connector_id)
                    console.print("\n[bold]Available tools:[/bold]")
                    for tool in tools:
                        console.print(f"  - [cyan]{tool.get('name')}[/cyan]: {tool.get('description', '')}")
                    console.print()

                elif command == "resources":
                    resources = client.list_mcp_resources(tenant_slug, connector_id)
                    console.print("\n[bold]Available resources:[/bold]")
                    for resource in resources:
                        console.print(f"  - [cyan]{resource.get('uri')}[/cyan]: {resource.get('name', '')}")
                    console.print()

                elif command == "info":
                    info = client.get_mcp_info(tenant_slug, connector_id)
                    syntax = Syntax(json.dumps(info, indent=2), "json", theme="monokai")
                    console.print(syntax)

                elif command == "call":
                    if len(parts) < 2:
                        print_error("Usage: call <tool_name> [args...]")
                        continue

                    # Parse tool name and arguments
                    args_str = parts[1].strip()
                    tool_parts = args_str.split(None, 1)
                    tool_name = tool_parts[0]

                    # Parse arguments (key=value format or JSON)
                    arguments = {}
                    if len(tool_parts) > 1:
                        args_input = tool_parts[1].strip()

                        # Try JSON first
                        if args_input.startswith("{"):
                            try:
                                arguments = json.loads(args_input)
                            except json.JSONDecodeError:
                                print_error("Invalid JSON arguments")
                                continue
                        else:
                            # Parse key=value pairs
                            for arg in args_input.split():
                                if "=" in arg:
                                    key, value = arg.split("=", 1)
                                    # Try to parse as JSON value
                                    try:
                                        arguments[key] = json.loads(value)
                                    except json.JSONDecodeError:
                                        arguments[key] = value

                    # Call tool
                    result = client.call_mcp_tool(tenant_slug, connector_id, tool_name, arguments)
                    syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
                    console.print(syntax)

                elif command == "read":
                    if len(parts) < 2:
                        print_error("Usage: read <uri>")
                        continue

                    uri = parts[1].strip()
                    content = client.read_mcp_resource(tenant_slug, connector_id, uri)
                    console.print(f"\n{content}\n")

                else:
                    print_error(f"Unknown command: {command}. Type 'help' for available commands.")

            except APIError as e:
                print_error(f"API Error: {e.message}")
            except KeyboardInterrupt:
                console.print("\n[bold]Use 'exit' to quit[/bold]")
            except EOFError:
                console.print("\n[bold]Goodbye![/bold]")
                break
            except Exception as e:
                print_error(f"Error: {e}")

    except APIError as e:
        print_error(f"Failed to start interactive session: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


@app.command("ping")
def ping_server(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    connector_id: str = typer.Argument(..., help="Connector ID"),
    profile: Optional[str] = typer.Option(None, help="Profile to use"),
) -> None:
    """Test MCP server connection."""
    try:
        client = get_client(profile)
        info = client.get_mcp_info(tenant_slug, connector_id)

        print_success("MCP server is reachable")
        console.print(f"Server: [cyan]{info.get('server_name')}[/cyan] v{info.get('server_version')}")
        console.print(f"Protocol: [cyan]{info.get('protocol_version')}[/cyan]")

    except APIError as e:
        print_error(f"MCP server is not reachable: {e.message}")
        sys.exit(3 if e.status_code and e.status_code < 500 else 4)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
