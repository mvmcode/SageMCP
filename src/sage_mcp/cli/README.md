# SageMCP CLI

Command-line interface for managing the SageMCP multi-tenant MCP server platform.

## Installation

### From PyPI (when published)

```bash
# Install with CLI support
pip install sage-mcp[cli]
```

### From Source

```bash
cd SageMCP
pip install -e ".[cli]"
```

## Quick Start

### 1. Initialize Configuration

```bash
sagemcp init
```

This will walk you through setting up your first profile with your SageMCP server URL.

### 2. Manage Tenants

```bash
# List all tenants
sagemcp tenant list

# Create a new tenant
sagemcp tenant create --slug my-tenant --name "My Tenant"

# Show tenant details
sagemcp tenant show my-tenant
```

### 3. Manage Connectors

```bash
# List connectors for a tenant
sagemcp connector list my-tenant

# Create a GitHub connector
sagemcp connector create my-tenant --type github --name "GitHub Production"

# List available connector types
sagemcp connector types
```

### 4. Configure OAuth

```bash
# List available OAuth providers
sagemcp oauth providers

# Start OAuth flow (opens browser)
sagemcp oauth authorize my-tenant github

# List OAuth credentials
sagemcp oauth list my-tenant
```

### 5. Test MCP Tools

```bash
# List available tools
sagemcp mcp tools my-tenant <connector-id>

# Call a tool
sagemcp mcp call my-tenant <connector-id> github_list_repos

# Interactive REPL session
sagemcp mcp interactive my-tenant <connector-id>
```

## Command Reference

### Global Options

```bash
--profile TEXT          # Profile to use (default: "default")
--format [table|json|yaml]  # Output format
--help                  # Show help
```

### Configuration (`config`)

```bash
sagemcp config init              # Initialize configuration
sagemcp config list              # List all profiles
sagemcp config show [PROFILE]    # Show profile details
sagemcp config set KEY VALUE     # Set configuration value
sagemcp config delete PROFILE    # Delete a profile
```

### Tenants (`tenant`)

```bash
sagemcp tenant list              # List all tenants
sagemcp tenant show SLUG         # Show tenant details
sagemcp tenant create            # Create tenant (interactive)
sagemcp tenant update SLUG       # Update tenant
sagemcp tenant delete SLUG       # Delete tenant
```

### Connectors (`connector`)

```bash
sagemcp connector list TENANT               # List connectors
sagemcp connector show TENANT ID            # Show connector details
sagemcp connector create TENANT             # Create connector (interactive)
sagemcp connector update TENANT ID          # Update connector
sagemcp connector delete TENANT ID          # Delete connector
sagemcp connector toggle TENANT ID          # Toggle enabled status
sagemcp connector types                     # List available types
```

### OAuth (`oauth`)

```bash
sagemcp oauth providers                     # List OAuth providers
sagemcp oauth list TENANT                   # List credentials
sagemcp oauth authorize TENANT PROVIDER     # Start OAuth flow
sagemcp oauth revoke TENANT PROVIDER        # Revoke credentials
```

### MCP Testing (`mcp`)

```bash
sagemcp mcp info TENANT CONNECTOR           # Get MCP server info
sagemcp mcp tools TENANT CONNECTOR          # List available tools
sagemcp mcp resources TENANT CONNECTOR      # List available resources
sagemcp mcp call TENANT CONNECTOR TOOL      # Call a tool
sagemcp mcp read TENANT CONNECTOR URI       # Read a resource
sagemcp mcp interactive TENANT CONNECTOR    # Start REPL session
sagemcp mcp ping TENANT CONNECTOR           # Test connection
```

## Interactive REPL

The MCP interactive mode provides a REPL for testing MCP tools and resources:

```bash
$ sagemcp mcp interactive my-tenant github-connector

SageMCP Interactive Session
Tenant: my-tenant | Connector: GitHub Production (github)
Type 'help' for commands, 'exit' to quit

mcp> tools
Available tools:
  - github_list_repos: List repositories for authenticated user
  - github_get_repo: Get details of a specific repository
  - github_create_issue: Create a new issue in a repository
  ...

mcp> call github_list_repos
{
  "repositories": [
    {"name": "repo1", "full_name": "org/repo1"},
    {"name": "repo2", "full_name": "org/repo2"}
  ]
}

mcp> call github_create_issue owner=org repo=repo1 title="Bug fix"
{
  "issue": {
    "number": 123,
    "title": "Bug fix",
    "state": "open"
  }
}

mcp> exit
Goodbye!
```

### REPL Commands

- `tools` - List available tools
- `resources` - List available resources
- `call <tool> [args...]` - Call a tool with arguments
- `read <uri>` - Read a resource
- `info` - Show MCP server info
- `help` - Show help
- `exit` - Exit REPL

## Output Formats

The CLI supports three output formats:

### Table (default)

```bash
sagemcp tenant list
```

```
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Slug       ┃ Name         ┃ Active ┃ Created       ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ my-tenant  │ My Tenant    │ ✓      │ 2025-11-10    │
└────────────┴──────────────┴────────┴───────────────┘
```

### JSON

```bash
sagemcp tenant list --format json
```

```json
[
  {
    "slug": "my-tenant",
    "name": "My Tenant",
    "is_active": true,
    "created_at": "2025-11-10T10:00:00Z"
  }
]
```

### YAML

```bash
sagemcp tenant list --format yaml
```

```yaml
- slug: my-tenant
  name: My Tenant
  is_active: true
  created_at: '2025-11-10T10:00:00Z'
```

## Configuration File

The CLI stores configuration in `~/.sage-mcp/config.toml`:

```toml
[profiles.default]
base_url = "http://localhost:8000"
api_key = ""
output_format = "table"
timeout = 30

[profiles.production]
base_url = "https://api.sagemcp.com"
api_key = "your-api-key"
output_format = "json"
timeout = 60

[settings]
default_profile = "default"
auto_update = true
log_level = "INFO"
```

## Multiple Profiles

Manage multiple environments with profiles:

```bash
# Create a production profile
sagemcp config init --profile production --base-url https://api.sagemcp.com

# Use production profile
sagemcp tenant list --profile production

# Set as default
sagemcp config set default_profile production
```

## Examples

### Create a Complete Tenant Setup

```bash
# Create tenant
sagemcp tenant create --slug acme-corp --name "Acme Corporation"

# Add GitHub connector
sagemcp connector create acme-corp --type github --name "GitHub"

# Configure OAuth
sagemcp oauth authorize acme-corp github

# Test the connector
sagemcp mcp tools acme-corp <connector-id>
```

### Batch Operations

```bash
# Create multiple tenants
for tenant in tenant1 tenant2 tenant3; do
  sagemcp tenant create --slug $tenant --name "Tenant $tenant" --no-interactive
done

# List all and export to JSON
sagemcp tenant list --format json > tenants.json
```

### CI/CD Integration

```bash
#!/bin/bash
set -e

# Configure CLI
sagemcp config init --no-interactive \
  --base-url "$SAGEMCP_URL" \
  --api-key "$SAGEMCP_API_KEY"

# Create tenant
sagemcp tenant create \
  --slug "$TENANT_SLUG" \
  --name "$TENANT_NAME" \
  --no-interactive

# Create connector
CONNECTOR_ID=$(sagemcp connector create "$TENANT_SLUG" \
  --type github \
  --name "GitHub" \
  --no-interactive \
  --format json | jq -r '.id')

# Verify
sagemcp mcp ping "$TENANT_SLUG" "$CONNECTOR_ID"
```

## Error Handling

The CLI uses exit codes for automation:

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - API error (4xx)
- `4` - Server error (5xx)
- `5` - Network error

Example:

```bash
if sagemcp tenant show my-tenant; then
  echo "Tenant exists"
else
  echo "Tenant not found (exit code: $?)"
fi
```

## Troubleshooting

### Connection Issues

```bash
# Test server connectivity
sagemcp version --verbose

# Check configuration
sagemcp config show
```

### Authentication Errors

```bash
# Verify API key is set
sagemcp config show | grep "API Key"

# Update API key
sagemcp config set api_key "your-new-key"
```

### OAuth Issues

```bash
# Check OAuth credentials
sagemcp oauth list my-tenant

# Re-authorize
sagemcp oauth revoke my-tenant github
sagemcp oauth authorize my-tenant github
```

## Development

### Running from Source

```bash
# Install in development mode
pip install -e ".[cli,dev]"

# Run CLI
sagemcp --help

# Or directly
python -m sage_mcp.cli.main --help
```

### Testing

```bash
# Run CLI tests
pytest tests/cli/

# Test specific command
pytest tests/cli/test_tenant.py -v
```

## Documentation

- [CLI Design Document](../../../docs/cli-design.md) - Detailed design and architecture
- [Main README](../../../README.md) - SageMCP platform overview
- [API Documentation](../../../docs/architecture.md) - Backend API reference

## Support

- GitHub Issues: https://github.com/mvmcode/SageMCP/issues
- Discord: https://discord.gg/kpHzRzmy

## License

Apache 2.0 - See [LICENSE](../../../LICENSE) for details
