# Node.js/TypeScript MCP Server Example

A minimal example of an external MCP server written in TypeScript that can be hosted by SageMCP.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build the TypeScript code:
```bash
npm run build
```

3. Test locally (optional):
```bash
npm start
# The server will communicate via stdin/stdout
```

## Deploy to SageMCP

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants/my-tenant/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "custom",
    "name": "Node.js Example Server",
    "description": "Example Node.js MCP server",
    "runtime_type": "external_nodejs",
    "runtime_command": "[\"node\", \"build/server.js\"]",
    "package_path": "/path/to/examples/external-mcp-servers/nodejs-example",
    "is_enabled": true
  }'
```

### Using npx (for published packages)

```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants/my-tenant/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "custom",
    "name": "GitHub MCP Server",
    "description": "Community GitHub MCP server",
    "runtime_type": "external_nodejs",
    "runtime_command": "[\"npx\", \"@modelcontextprotocol/server-github\"]",
    "runtime_env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "{{OAUTH_TOKEN}}"
    },
    "is_enabled": true
  }'
```

## Available Tools

- **greet**: Greet a user by name
- **get_env_info**: Get information about the runtime environment
- **check_oauth**: Check if OAuth token is available
- **fetch_data**: Fetch data from an external API using OAuth token

## Environment Variables

SageMCP automatically injects these environment variables:

- `OAUTH_TOKEN`: OAuth access token for the tenant
- `ACCESS_TOKEN`: Alternative name for OAuth token
- `TENANT_ID`: ID of the tenant
- `CONNECTOR_ID`: ID of the connector
- `SAGEMCP_MODE`: Set to "hosted" when running in SageMCP
- `SAGEMCP_API_BASE`: Base URL for SageMCP API

## Example: Using Community MCP Servers

You can use any community MCP server from npm. Here are some examples:

### GitHub Server

```json
{
  "connector_type": "custom",
  "name": "GitHub MCP Server",
  "runtime_type": "external_nodejs",
  "runtime_command": "[\"npx\", \"@modelcontextprotocol/server-github\"]",
  "runtime_env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "{{OAUTH_TOKEN}}"
  }
}
```

### PostgreSQL Server

```json
{
  "connector_type": "custom",
  "name": "PostgreSQL MCP Server",
  "runtime_type": "external_nodejs",
  "runtime_command": "[\"npx\", \"@modelcontextprotocol/server-postgres\"]",
  "runtime_env": {
    "POSTGRES_CONNECTION_STRING": "{{CONFIG_DATABASE_URL}}"
  },
  "configuration": {
    "database_url": "postgresql://user:pass@localhost:5432/db"
  }
}
```

## Testing

Once deployed, you can test the tools via Claude Desktop or any MCP client:

```javascript
// List tools
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

// Call greet tool
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
  "name": "greet",
  "arguments": {"name": "Alice"}
}}

// Check OAuth
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
  "name": "check_oauth",
  "arguments": {}
}}
```
