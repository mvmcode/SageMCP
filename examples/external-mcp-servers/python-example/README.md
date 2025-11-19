# Python MCP Server Example

A minimal example of an external MCP server that can be hosted by SageMCP.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Test locally (optional):
```bash
python server.py
# The server will communicate via stdin/stdout
```

## Deploy to SageMCP

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants/my-tenant/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "custom",
    "name": "Python Example Server",
    "description": "Example Python MCP server",
    "runtime_type": "external_python",
    "runtime_command": "[\"python\", \"server.py\"]",
    "package_path": "/path/to/examples/external-mcp-servers/python-example",
    "is_enabled": true
  }'
```

### Via CLI (if implemented)

```bash
sagemcp connector add-external my-tenant \
  --name "Python Example Server" \
  --runtime python \
  --command "python server.py" \
  --working-dir /path/to/examples/external-mcp-servers/python-example
```

## Available Tools

- **echo**: Echo back an input message
- **get_env_info**: Get information about the runtime environment (tenant ID, connector ID, etc.)
- **check_oauth**: Check if OAuth token is available

## Environment Variables

SageMCP automatically injects these environment variables:

- `OAUTH_TOKEN`: OAuth access token for the tenant
- `ACCESS_TOKEN`: Alternative name for OAuth token
- `TENANT_ID`: ID of the tenant
- `CONNECTOR_ID`: ID of the connector
- `SAGEMCP_MODE`: Set to "hosted" when running in SageMCP
- `SAGEMCP_API_BASE`: Base URL for SageMCP API

## Testing

Once deployed, you can test the tools via Claude Desktop or any MCP client:

```javascript
// List tools
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

// Call echo tool
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
  "name": "echo",
  "arguments": {"message": "Hello from SageMCP!"}
}}

// Check OAuth
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
  "name": "check_oauth",
  "arguments": {}
}}
```
