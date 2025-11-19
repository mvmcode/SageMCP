#!/usr/bin/env python3
"""
Example Python MCP Server for SageMCP

This is a minimal example of an external MCP server that can be hosted by SageMCP.
It demonstrates how to:
1. Create a simple MCP server using the Python MCP SDK
2. Access OAuth tokens injected by SageMCP
3. Define tools and execute them
4. Integrate with external APIs

To use this with SageMCP:
1. Upload this server or reference its path
2. Configure connector with:
   - runtime_type: "external_python"
   - runtime_command: '["python", "server.py"]'
   - package_path: "/path/to/this/directory"
"""

import os
import asyncio
from mcp.server import Server
from mcp import types


# Create MCP server
server = Server("example-python-server")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="echo",
            description="Echo back the input message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo"
                    }
                },
                "required": ["message"]
            }
        ),
        types.Tool(
            name="get_env_info",
            description="Get information about the runtime environment",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="check_oauth",
            description="Check if OAuth token is available (for testing)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute a tool."""

    if name == "echo":
        message = arguments.get("message", "")
        return [types.TextContent(
            type="text",
            text=f"Echo: {message}"
        )]

    elif name == "get_env_info":
        tenant_id = os.getenv("TENANT_ID", "not set")
        connector_id = os.getenv("CONNECTOR_ID", "not set")
        sagemcp_mode = os.getenv("SAGEMCP_MODE", "not set")

        info = f"""Runtime Environment Information:
- Tenant ID: {tenant_id}
- Connector ID: {connector_id}
- SageMCP Mode: {sagemcp_mode}
- Python Version: {os.sys.version}
"""
        return [types.TextContent(type="text", text=info)]

    elif name == "check_oauth":
        oauth_token = os.getenv("OAUTH_TOKEN", "")
        access_token = os.getenv("ACCESS_TOKEN", "")

        if oauth_token:
            masked_token = oauth_token[:8] + "..." + oauth_token[-4:]
            status = f"✓ OAuth token available (OAUTH_TOKEN): {masked_token}"
        elif access_token:
            masked_token = access_token[:8] + "..." + access_token[-4:]
            status = f"✓ OAuth token available (ACCESS_TOKEN): {masked_token}"
        else:
            status = "✗ No OAuth token found in environment"

        return [types.TextContent(type="text", text=status)]

    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="example://hello",
            name="Hello Resource",
            description="A simple example resource",
            mimeType="text/plain"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "example://hello":
        return "Hello from Python MCP Server!"
    else:
        raise ValueError(f"Unknown resource: {uri}")


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
