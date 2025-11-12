# SageMCP CLI Quick Start Guide

## Installation (30 seconds)

```bash
cd SageMCP
pip install -e ".[cli]"
sagemcp --version
```

## First-Time Setup (1 minute)

```bash
# Interactive setup wizard
sagemcp init
```

Answer the prompts:
- Profile name: `default` (or your choice)
- API base URL: `http://localhost:8000` (or your server)
- API key: Leave blank or enter if you have one

## Essential Commands (Copy & Paste Ready)

### 1. List Everything

```bash
# List all tenants
sagemcp tenant list

# List connectors for a tenant
sagemcp connector list <tenant-slug>

# List OAuth credentials
sagemcp oauth list <tenant-slug>

# List available connector types
sagemcp connector types

# List OAuth providers
sagemcp oauth providers
```

### 2. Create a Tenant

```bash
# Interactive (recommended for beginners)
sagemcp tenant create

# Non-interactive (for scripts)
sagemcp tenant create --slug my-app --name "My Application" --no-interactive
```

### 3. Add a Connector

```bash
# Interactive
sagemcp connector create <tenant-slug>

# Non-interactive (GitHub example)
sagemcp connector create my-app --type github --name "GitHub Production" --no-interactive
```

### 4. Setup OAuth

```bash
# Start OAuth flow (opens browser)
sagemcp oauth authorize <tenant-slug> github

# Example
sagemcp oauth authorize my-app github
```

### 5. Test MCP Tools

```bash
# List available tools
sagemcp mcp tools <tenant-slug> <connector-id>

# Call a tool
sagemcp mcp call <tenant-slug> <connector-id> <tool-name> --args '{"key":"value"}'

# Example: List GitHub repos
sagemcp mcp call my-app <connector-id> github_list_repos
```

### 6. Interactive REPL (Most Fun!)

```bash
sagemcp mcp interactive <tenant-slug> <connector-id>
```

In the REPL:
```
mcp> tools                          # See available tools
mcp> call github_list_repos         # Call a tool
mcp> resources                      # See resources
mcp> help                           # Get help
mcp> exit                           # Exit
```

## Common Workflows

### Complete Setup from Scratch

```bash
# 1. Initialize CLI
sagemcp init

# 2. Create tenant
sagemcp tenant create --slug prod --name "Production"

# 3. Add GitHub connector
sagemcp connector create prod --type github --name "GitHub"
# Note the connector ID from output

# 4. Setup OAuth
sagemcp oauth authorize prod github

# 5. Test it
sagemcp mcp tools prod <connector-id>
sagemcp mcp interactive prod <connector-id>
```

### Multiple Environments

```bash
# Setup profiles
sagemcp config init --profile dev --base-url http://localhost:8000
sagemcp config init --profile prod --base-url https://api.example.com

# Use specific profile
sagemcp tenant list --profile prod
sagemcp connector list my-tenant --profile dev
```

### Export Configuration

```bash
# Export tenants to JSON
sagemcp tenant list --format json > tenants.json

# Export specific tenant
sagemcp tenant show my-tenant --format yaml > tenant.yaml
```

## Output Formats

```bash
# Table (default, pretty)
sagemcp tenant list

# JSON (for scripts)
sagemcp tenant list --format json

# YAML (human-friendly)
sagemcp tenant list --format yaml
```

## Get Help Anytime

```bash
# General help
sagemcp --help

# Command group help
sagemcp tenant --help
sagemcp connector --help
sagemcp oauth --help
sagemcp mcp --help

# Specific command help
sagemcp tenant create --help
sagemcp mcp call --help
```

## Troubleshooting

### Can't connect to server?

```bash
# Check configuration
sagemcp config show

# Test connection
sagemcp version --verbose

# Update server URL
sagemcp config set base_url http://your-server:8000
```

### Forgot your connector ID?

```bash
# List connectors (shows IDs)
sagemcp connector list <tenant-slug>

# Or use JSON format for full IDs
sagemcp connector list <tenant-slug> --format json
```

### Need to switch profiles?

```bash
# List all profiles
sagemcp config list

# Use different profile for one command
sagemcp tenant list --profile production

# Set new default
sagemcp config set default_profile production
```

## Pro Tips

1. **Use tab completion**: Run `sagemcp --install-completion` for your shell

2. **Alias common commands**: Add to your `.bashrc` or `.zshrc`:
   ```bash
   alias st='sagemcp tenant list'
   alias sc='sagemcp connector list'
   ```

3. **Pipe JSON output**:
   ```bash
   sagemcp tenant list --format json | jq '.[] | .slug'
   ```

4. **Use in scripts**:
   ```bash
   #!/bin/bash
   if sagemcp tenant show my-tenant 2>/dev/null; then
     echo "Tenant exists"
   else
     sagemcp tenant create --slug my-tenant --name "My Tenant" --no-interactive
   fi
   ```

5. **Interactive mode for exploration**: Use `--interactive` (default) when learning, `--no-interactive` for automation

## Next Steps

- **Read full docs**: `cat src/sage_mcp/cli/README.md`
- **Explore design**: `cat docs/cli-design.md`
- **Try the REPL**: `sagemcp mcp interactive <tenant> <connector>`
- **Build automation**: Export JSON and use in scripts

## Common Use Cases

### DevOps Engineer
```bash
# CI/CD pipeline
sagemcp tenant create --slug $CI_PROJECT_NAME --name "$CI_PROJECT_NAME" --no-interactive
sagemcp connector create $CI_PROJECT_NAME --type github --name "CI GitHub" --no-interactive
```

### Developer
```bash
# Local testing
sagemcp mcp interactive local-dev github-connector
# Play with tools interactively
```

### System Administrator
```bash
# Audit and monitoring
sagemcp tenant list --format json | jq 'length'
sagemcp oauth list my-tenant
```

## Keyboard Shortcuts (REPL)

- `Ctrl+C` - Interrupt (shows help message)
- `Ctrl+D` - Exit
- Type `exit` or `quit` - Exit gracefully
- Up/Down arrows - Command history (if available)

## Success Checklist

- [ ] Installed CLI successfully
- [ ] Ran `sagemcp init`
- [ ] Listed tenants
- [ ] Created a tenant
- [ ] Added a connector
- [ ] Configured OAuth
- [ ] Tested MCP tools
- [ ] Tried interactive REPL

Once you've checked all boxes, you're ready to use SageMCP CLI like a pro!

## Quick Reference Card

| Task | Command |
|------|---------|
| Initialize | `sagemcp init` |
| List tenants | `sagemcp tenant list` |
| Create tenant | `sagemcp tenant create` |
| List connectors | `sagemcp connector list TENANT` |
| Create connector | `sagemcp connector create TENANT` |
| Setup OAuth | `sagemcp oauth authorize TENANT PROVIDER` |
| List tools | `sagemcp mcp tools TENANT CONNECTOR` |
| Interactive mode | `sagemcp mcp interactive TENANT CONNECTOR` |
| Get help | `sagemcp --help` |
| Check version | `sagemcp version --verbose` |

---

**Ready to go?** Start with: `sagemcp init`
