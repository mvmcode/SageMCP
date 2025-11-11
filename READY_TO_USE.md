# SageMCP CLI - Ready to Use! 🎉

## ✅ Setup Complete

Your SageMCP CLI is fully configured and ready to use!

## Quick Test

Open a **new terminal** and run:

```bash
sagemcp version
# Output: SageMCP CLI v0.1.0

sagemcp connector types
# Shows beautiful table of connector types

sagemcp config list
# Shows your configured profile
```

## What's Configured

✅ **CLI Command:** `sagemcp` (available globally)
✅ **Configuration:** `~/.sage-mcp/config.toml` created
✅ **Default Profile:** Configured with `http://localhost:8000`
✅ **PATH:** `~/bin` added to shell PATH
✅ **Dependencies:** All installed in virtual environment

## Configuration File

Location: `~/.sage-mcp/config.toml`

```toml
[profiles.default]
base_url = "http://localhost:8000"
api_key = ""
output_format = "table"
timeout = 30

[settings]
default_profile = "default"
auto_update = true
log_level = "INFO"
```

## Basic Commands

```bash
# Show version
sagemcp version

# Show help
sagemcp --help

# List connector types
sagemcp connector types

# Manage configuration
sagemcp config list
sagemcp config show

# When backend is running:
sagemcp tenant list
sagemcp tenant create --slug test --name "Test Tenant"
```

## Start Using with Backend

### 1. Start the Backend

In one terminal:
```bash
cd /Users/manikandan/Desktop/mvmcode/SageMCP
make up
```

### 2. Use the CLI

In another terminal (or the same terminal with `sagemcp` now available):
```bash
# List tenants
sagemcp tenant list

# Create a tenant
sagemcp tenant create --slug my-app --name "My Application"

# List connectors
sagemcp connector list my-app

# Create a GitHub connector
sagemcp connector create my-app --type github --name "GitHub"

# Setup OAuth
sagemcp oauth authorize my-app github

# Test MCP tools
sagemcp mcp tools my-app <connector-id>

# Interactive REPL
sagemcp mcp interactive my-app <connector-id>
```

## Interactive REPL Example

```bash
$ sagemcp mcp interactive my-app github-connector

SageMCP Interactive Session
Tenant: my-app | Connector: GitHub (github)
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

mcp> exit
Goodbye!
```

## Configuration Profiles

You can add more profiles for different environments:

```bash
# Edit config
vim ~/.sage-mcp/config.toml

# Or use sagemcp config commands
sagemcp config set base_url https://api.example.com --profile production

# Use different profile
sagemcp tenant list --profile production
```

## All Available Commands

```bash
sagemcp config       # Configuration management
  ├── init          # Initialize configuration
  ├── list          # List all profiles
  ├── show          # Show profile details
  ├── set           # Set configuration value
  └── delete        # Delete a profile

sagemcp tenant       # Tenant operations
  ├── list          # List all tenants
  ├── show          # Show tenant details
  ├── create        # Create new tenant
  ├── update        # Update tenant
  └── delete        # Delete tenant

sagemcp connector    # Connector management
  ├── list          # List connectors
  ├── show          # Show connector details
  ├── create        # Create connector
  ├── update        # Update connector
  ├── delete        # Delete connector
  ├── toggle        # Toggle enabled status
  └── types         # List available types

sagemcp oauth        # OAuth management
  ├── providers     # List OAuth providers
  ├── list          # List credentials
  ├── authorize     # Start OAuth flow
  └── revoke        # Revoke credentials

sagemcp mcp          # MCP testing
  ├── info          # Get server info
  ├── tools         # List tools
  ├── resources     # List resources
  ├── call          # Call a tool
  ├── read          # Read a resource
  ├── interactive   # Start REPL session
  └── ping          # Test connection
```

## Output Formats

The CLI supports multiple output formats:

```bash
# Table (default, pretty)
sagemcp tenant list

# JSON (for scripts)
sagemcp tenant list --format json

# YAML (human-friendly)
sagemcp tenant list --format yaml
```

## Troubleshooting

### Command Not Found

If `sagemcp` is not found:

1. **Open a new terminal** (PATH changes require new session)
2. Or reload shell: `source ~/.zshrc`
3. Or use full path: `~/bin/sagemcp version`

### Backend Not Running

If you get connection errors:

```bash
# Start the backend
cd /Users/manikandan/Desktop/mvmcode/SageMCP
make up

# Check it's running
curl http://localhost:8000/health
```

### Profile Errors

If you get "Profile not found" errors, the config file should now be created at `~/.sage-mcp/config.toml`

## Next Steps

1. ✅ Test the command: `sagemcp version`
2. ✅ View available connectors: `sagemcp connector types`
3. ✅ Start backend: `make up`
4. ✅ Create a tenant: `sagemcp tenant create`
5. ✅ Try interactive REPL: `sagemcp mcp interactive`

## Documentation

- **User Guide:** `src/sage_mcp/cli/README.md`
- **Quick Start:** `src/sage_mcp/cli/QUICKSTART.md`
- **Installation:** `src/sage_mcp/cli/INSTALLATION.md`
- **Setup Instructions:** `SETUP_INSTRUCTIONS.md`

## Commit Your Changes

Everything is ready! To commit:

```bash
cd /Users/manikandan/Desktop/mvmcode/SageMCP
git status
git add -A
git commit -m "feat: Add comprehensive CLI with PyPI publishing workflow"
git push origin main
```

---

**Status:** ✅ Ready to Use
**Command:** `sagemcp`
**Version:** 0.1.0
**Config:** `~/.sage-mcp/config.toml`
**Date:** 2025-11-10

🎉 **Enjoy your new CLI!**
