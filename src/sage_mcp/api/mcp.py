"""MCP API routes for multi-tenant support."""

import asyncio
import json

from fastapi import APIRouter, HTTPException, Request, WebSocket
from fastapi.responses import StreamingResponse

from ..mcp.transport import MCPTransport

router = APIRouter()


@router.websocket("/{tenant_slug}/mcp")
async def mcp_websocket(websocket: WebSocket, tenant_slug: str):
    """WebSocket endpoint for MCP protocol communication."""
    await websocket.accept()

    # Create transport for this tenant
    transport = MCPTransport(tenant_slug)

    # Handle the WebSocket connection
    await transport.handle_websocket(websocket)


@router.post("/{tenant_slug}/mcp")
async def mcp_http(tenant_slug: str, request: Request):
    """HTTP endpoint for MCP protocol communication."""
    try:
        # Parse the JSON-RPC message
        message = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Create transport for this tenant
    transport = MCPTransport(tenant_slug)

    # Handle the message
    response = await transport.handle_http_message(message)

    return response


@router.get("/{tenant_slug}/mcp/sse")
async def mcp_sse(tenant_slug: str):
    """Server-Sent Events endpoint for MCP protocol communication."""

    async def event_stream():
        # Create a queue for messages
        message_queue = asyncio.Queue()

        # Create transport for this tenant
        transport = MCPTransport(tenant_slug)

        # Start SSE handling in background
        sse_task = asyncio.create_task(transport.handle_sse(message_queue))

        try:
            while True:
                # Wait for a message
                message = await message_queue.get()

                # Check if it's an error
                if "error" in message:
                    yield f"event: error\ndata: {json.dumps(message)}\n\n"
                    break

                # Send the message
                yield f"event: message\ndata: {json.dumps(message)}\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            sse_task.cancel()
            try:
                await sse_task
            except asyncio.CancelledError:
                pass

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/{tenant_slug}/mcp/info")
async def mcp_info(tenant_slug: str):
    """Get MCP server information for a tenant."""
    # Create transport to check if tenant exists
    transport = MCPTransport(tenant_slug)

    if not await transport.initialize():
        raise HTTPException(status_code=404, detail="Tenant not found or inactive")

    return {
        "tenant": tenant_slug,
        "server_name": "sage-mcp",
        "server_version": "0.1.0",
        "protocol_version": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True}
        },
        "connectors": [
            {
                "type": conn.connector_type.value,
                "name": conn.name,
                "enabled": conn.is_enabled
            }
            for conn in transport.mcp_server.connectors
        ]
    }
