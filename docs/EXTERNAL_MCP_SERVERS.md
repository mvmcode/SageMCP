# External MCP Server Support - Phase 1 MVP

## Overview

SageMCP now supports hosting **external MCP servers** from any runtime (Python, Node.js, Go, custom binaries) alongside native Python connectors. This transforms SageMCP from a connector platform into a **generic MCP hosting platform**.

**Status**: Phase 1 MVP Complete ✅

## What Changed

### Architecture

```
Before (Native Only):
Client → SageMCP → Native Python Connectors → External APIs

After (Hybrid):
Client → SageMCP → Native Python Connectors → External APIs
                 → External MCP Servers (Python/Node.js/Go/etc.)
```

### Key Features (Phase 1 MVP)

✅ **Support Any MCP Server**: Python, Node.js, Go, or any binary that speaks MCP over stdio
✅ **Multi-Tenancy**: Isolated processes per tenant
✅ **OAuth Injection**: Automatic credential forwarding via environment variables
✅ **Process Management**: Auto-start, health checks, auto-restart (max 3 attempts)
✅ **Unified Interface**: External tools appear alongside native connectors
✅ **Zero Breaking Changes**: Existing native connectors work unchanged
✅ **API Management**: Full CRUD for external MCP servers

## Database Schema

### New Fields in `connectors` Table

```sql
ALTER TABLE connectors
  ADD COLUMN runtime_type VARCHAR(50) DEFAULT 'native' NOT NULL,
  ADD COLUMN runtime_command TEXT,
  ADD COLUMN runtime_env TEXT,
  ADD COLUMN package_path TEXT;
```

### New Table: `mcp_processes`

```sql
CREATE TABLE mcp_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID REFERENCES connectors(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    pid INTEGER,
    runtime_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_health_check TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    restart_count INTEGER DEFAULT 0,
    cpu_limit_millicores INTEGER,
    memory_limit_mb INTEGER
);
```

## Runtime Types

```python
class ConnectorRuntimeType(enum.Enum):
    NATIVE = "native"                    # In-process Python (existing)
    EXTERNAL_PYTHON = "external_python"  # Python MCP SDK server
    EXTERNAL_NODEJS = "external_nodejs"  # Node.js @modelcontextprotocol/sdk
    EXTERNAL_GO = "external_go"          # Go MCP implementation
    EXTERNAL_CUSTOM = "external_custom"  # Any binary with MCP over stdio
```

## Usage Examples

### 1. Deploy Custom Python MCP Server

```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants/my-tenant/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "custom",
    "name": "Custom API Integration",
    "description": "Internal API integration",
    "runtime_type": "external_python",
    "runtime_command": "[\"python\", \"server.py\"]",
    "package_path": "/opt/mcp-servers/custom-api",
    "configuration": {
      "api_base_url": "https://api.internal.company.com"
    },
    "is_enabled": true
  }'
```

### 2. Deploy Community Node.js MCP Server

```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants/my-tenant/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "custom",
    "name": "GitHub Community Server",
    "description": "Community-maintained GitHub integration",
    "runtime_type": "external_nodejs",
    "runtime_command": "[\"npx\", \"@modelcontextprotocol/server-github\"]",
    "runtime_env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "{{OAUTH_TOKEN}}"
    },
    "is_enabled": true
  }'
```

### 3. Check Process Status

```bash
curl http://localhost:8000/api/v1/admin/connectors/{connector-id}/process/status
```

Response:
```json
{
  "connector_id": "uuid",
  "tenant_id": "uuid",
  "pid": 12345,
  "runtime_type": "external_nodejs",
  "status": "running",
  "started_at": "2025-11-16T10:00:00Z",
  "last_health_check": "2025-11-16T10:05:30Z",
  "error_message": null,
  "restart_count": 0
}
```

### 4. Restart External Server

```bash
curl -X POST http://localhost:8000/api/v1/admin/connectors/{connector-id}/process/restart
```

### 5. Terminate External Server

```bash
curl -X DELETE http://localhost:8000/api/v1/admin/connectors/{connector-id}/process
```

## Environment Variables (Injected Automatically)

SageMCP injects these environment variables into external MCP servers:

| Variable | Description | Example |
|----------|-------------|---------|
| `OAUTH_TOKEN` | OAuth access token | `ghp_abc123...` |
| `ACCESS_TOKEN` | Alternative name | Same as OAUTH_TOKEN |
| `TENANT_ID` | Tenant UUID | `f47ac10b-58cc-4372-a567-0e02b2c3d479` |
| `CONNECTOR_ID` | Connector UUID | `a1b2c3d4-...` |
| `SAGEMCP_MODE` | Always "hosted" | `hosted` |
| `SAGEMCP_API_BASE` | SageMCP API URL | `http://localhost:8000` |
| `CONFIG_*` | User config values | `CONFIG_API_BASE_URL=...` |

### Using Configuration Values

From `connector.configuration`:
```json
{
  "configuration": {
    "api_base_url": "https://api.example.com",
    "timeout": "30"
  }
}
```

Becomes environment variables:
```bash
CONFIG_API_BASE_URL=https://api.example.com
CONFIG_TIMEOUT=30
```

## Process Lifecycle

```
┌─────────────────┐
│ Connector       │
│ Created         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ First Tool      │
│ Request         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Process Manager │
│ Starts Process  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MCP Initialize  │
│ Handshake       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RUNNING         │
│ (Health checks  │
│  every 30s)     │
└────────┬────────┘
         │
         ├─ Healthy ──► Continue
         │
         ├─ Unhealthy ──► Restart (max 3)
         │
         └─ Max Restarts ──► ERROR (manual intervention)
```

## Architecture Components

### 1. GenericMCPConnector

**Location**: `src/sage_mcp/runtime/generic_connector.py`

Wraps external MCP server processes:
- Spawns process with configured command
- Communicates via JSON-RPC over stdin/stdout
- Forwards `tools/list`, `tools/call`, `resources/list`, `resources/read`
- Handles OAuth token injection
- Manages process lifecycle

### 2. MCPProcessManager

**Location**: `src/sage_mcp/runtime/process_manager.py`

Manages all external MCP processes:
- Process pooling (reuse across requests)
- Health checks every 30 seconds
- Auto-restart on failure (max 3 attempts)
- Database state tracking
- Graceful shutdown on app termination

### 3. ConnectorRegistry (Updated)

**Location**: `src/sage_mcp/connectors/registry.py`

Routes to native or external connectors:
- `get_connector()` - Returns native connector
- `get_connector_for_config()` - Returns native OR GenericMCPConnector based on runtime_type

### 4. API Endpoints (New)

**Location**: `src/sage_mcp/api/admin.py`

- `GET /connectors/{id}/process/status` - Get process status
- `POST /connectors/{id}/process/restart` - Restart process
- `DELETE /connectors/{id}/process` - Terminate process

## Migration

### Automatic Migration on Startup

The migration runs automatically via `create_tables()` in `main.py`.

### Manual Migration

```python
import asyncio
from src.sage_mcp.database.migrations import upgrade_add_external_mcp_runtime

asyncio.run(upgrade_add_external_mcp_runtime())
```

### Backward Compatibility

✅ All existing connectors default to `runtime_type = 'native'`
✅ No API changes for existing endpoints
✅ Native connectors work exactly as before
✅ Zero downtime migration

## Performance Considerations

### Latency

| Operation | Native Connector | External MCP Server | Overhead |
|-----------|------------------|---------------------|----------|
| Tool call | 10-20ms | 30-50ms | ~20-30ms |
| Resource read | 10-20ms | 30-50ms | ~20-30ms |

**Recommendation**: Use native connectors for high-throughput, low-latency needs.

### Memory

| Type | Memory per Instance |
|------|---------------------|
| Native connector | ~50-100MB (shared across tenants) |
| External Python server | ~50-200MB per tenant |
| External Node.js server | ~50-200MB per tenant |

**Example**: 10 tenants × 3 external servers = 30 processes ≈ 1.5-6GB RAM

### Scaling

- **Process pooling**: Processes are reused across requests
- **Lazy initialization**: Processes start on first tool request
- **Health checks**: Auto-restart failed processes
- **Resource limits**: CPU/memory limits (Phase 2)

## Security

### Process Isolation

✅ Each external MCP server runs in separate process
✅ stdio-only communication (no network access to other tenants)
✅ Environment variable injection (tokens not in command args)
✅ Process cleanup on shutdown

### OAuth Token Security

✅ Tokens passed via environment variables (not visible in `ps`)
✅ Tokens removed from memory on process termination
✅ Audit logs track token usage (Phase 2)
✅ Short-lived tokens with auto-refresh (Phase 2)

### Code Execution Risks

⚠️ **Phase 1**: No sandboxing - users must trust external server code
✅ **Phase 2**: Resource limits (CPU/memory quotas)
✅ **Phase 3**: Static analysis, container sandboxing
✅ **Phase 4**: Review process for marketplace

## Testing

### Example Servers

Located in `examples/external-mcp-servers/`:

1. **Python Example** (`python-example/`)
   - Simple echo, env info, OAuth check tools
   - `python server.py`

2. **Node.js Example** (`nodejs-example/`)
   - Greet, env info, OAuth check, fetch tools
   - `npm install && npm run build && npm start`

### Manual Testing

1. **Start SageMCP**:
```bash
cd /home/user/SageMCP
python -m uvicorn src.sage_mcp.main:app --reload
```

2. **Create Tenant**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{"slug": "test", "name": "Test Tenant"}'
```

3. **Deploy External Server**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants/test/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "custom",
    "name": "Python Example",
    "runtime_type": "external_python",
    "runtime_command": "[\"python\", \"examples/external-mcp-servers/python-example/server.py\"]",
    "is_enabled": true
  }'
```

4. **Test Tools**:
```bash
# List tools
curl -X POST http://localhost:8000/api/v1/test/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

# Call echo tool
curl -X POST http://localhost:8000/api/v1/test/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "echo", "arguments": {"message": "Hello!"}}}'
```

## Troubleshooting

### Process Won't Start

**Check logs**:
```bash
# Process status
curl http://localhost:8000/api/v1/admin/connectors/{id}/process/status

# Look for error_message field
```

**Common issues**:
- Command not found → Check `runtime_command` path
- Permission denied → Ensure executable permissions
- Missing dependencies → Install in `package_path` directory
- Syntax error → Check server code

### Process Keeps Restarting

**Symptoms**: `restart_count` keeps increasing, status `ERROR`

**Causes**:
- Server crashes on startup
- Invalid MCP protocol responses
- Missing dependencies
- OAuth token issues

**Fix**:
```bash
# View stderr logs (check console where SageMCP runs)
# Fix issue in server code
# Restart process
curl -X POST http://localhost:8000/api/v1/admin/connectors/{id}/process/restart
```

### Tools Not Appearing

**Check**:
1. Connector is enabled: `is_enabled = true`
2. Process is running: Check status endpoint
3. MCP initialization succeeded: Check logs
4. Tool state not disabled: Check `connector_tool_states` table

## Next Steps (Future Phases)

### Phase 2: Production Hardening (2-3 weeks)

- [ ] Resource limits (CPU/memory quotas)
- [ ] Advanced health monitoring (heartbeat protocol)
- [ ] Structured logging from child processes
- [ ] OAuth token refresh support
- [ ] Exponential backoff for restarts

### Phase 3: Developer Experience (3-4 weeks)

- [ ] Package upload API (zip/tar.gz)
- [ ] S3/MinIO storage for packages
- [ ] Auto-detect runtime from package.json/requirements.txt
- [ ] UI for package management
- [ ] Templates and examples library

### Phase 4: Enterprise Features (4-6 weeks)

- [ ] Docker/Kubernetes runtime
- [ ] Marketplace for MCP servers
- [ ] Advanced security (Vault, network policies)
- [ ] Multi-region support
- [ ] Auto-scaling based on load

## Contributing

### Adding Support for New Runtimes

1. Add runtime type to `ConnectorRuntimeType` enum
2. Update documentation
3. Create example server
4. Test with real deployment

Example for Go:
```python
class ConnectorRuntimeType(enum.Enum):
    # ...
    EXTERNAL_GO = "external_go"
```

### Reporting Issues

Create GitHub issue with:
- Runtime type (Python, Node.js, etc.)
- Runtime command used
- Error message from process status
- Server code (if possible)
- SageMCP logs

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Node.js MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Design Document](./GENERIC_MCP_HOSTING_PLATFORM.md)

## Summary

**Phase 1 MVP** successfully transforms SageMCP into a generic MCP hosting platform while maintaining 100% backward compatibility with existing native connectors. Users can now:

✅ Deploy any MCP server (Python, Node.js, Go, custom)
✅ Access community MCP servers via npx
✅ Manage processes via API
✅ Automatic OAuth injection
✅ Health monitoring and auto-restart

**Next**: Production hardening (Phase 2) and developer experience improvements (Phase 3).
