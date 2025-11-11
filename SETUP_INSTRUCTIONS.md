# SageMCP CLI - Final Setup Instructions

## ✅ Setup Complete!

The SageMCP CLI is now installed and configured. Here's how to use it.

## Current Status

✅ **Wrapper script created:** `sagemcp.sh`
✅ **Symlink created:** `~/bin/sagemcp → sagemcp.sh`
✅ **PATH configured:** Added to `~/.zshrc`
✅ **All dependencies installed:** Virtual environment with typer, rich, etc.

## How to Use

### Option 1: Use `sagemcp` Command (Recommended)

After opening a **new terminal window** or running `source ~/.zshrc`:

```bash
sagemcp version
sagemcp --help
sagemcp connector types
sagemcp init
```

### Option 2: Use Wrapper Script Directly

From the project directory:

```bash
cd /Users/manikandan/Desktop/mvmcode/SageMCP
./sagemcp.sh version
./sagemcp.sh --help
```

### Option 3: With Virtual Environment

```bash
cd /Users/manikandan/Desktop/mvmcode/SageMCP
source .venv/bin/activate
sagemcp version
```

## Important: Restart Your Terminal

The PATH change in `~/.zshrc` only applies to new terminal sessions. To use `sagemcp` globally:

**Option A: Open a new terminal window**

**Option B: Reload your shell**
```bash
source ~/.zshrc
```

Then test:
```bash
sagemcp version
# Should output: SageMCP CLI v0.1.0
```

## Verify Installation

Run these commands to verify everything works:

```bash
# 1. Check PATH includes ~/bin
echo $PATH | grep "$HOME/bin" && echo "✅ PATH configured"

# 2. Check symlink exists
ls -l ~/bin/sagemcp && echo "✅ Symlink exists"

# 3. Test command
sagemcp version && echo "✅ CLI works"

# 4. Test with rich output
sagemcp connector types
```

## Quick Commands

```bash
# Show version
sagemcp version

# Show all commands
sagemcp --help

# Initialize configuration
sagemcp init

# List connector types (shows beautiful table)
sagemcp connector types

# Get help for specific command
sagemcp tenant --help
sagemcp connector --help
sagemcp oauth --help
sagemcp mcp --help
```

## Usage Examples

### When Backend is Running

```bash
# Start backend (in another terminal)
cd /Users/manikandan/Desktop/mvmcode/SageMCP
make up

# Use CLI
sagemcp tenant list
sagemcp tenant create --slug test --name "Test Tenant"
sagemcp connector list test
sagemcp connector create test --type github --name "GitHub"
```

### OAuth Flow

```bash
# List OAuth providers
sagemcp oauth providers

# Start OAuth flow (opens browser)
sagemcp oauth authorize <tenant-slug> github

# List credentials
sagemcp oauth list <tenant-slug>
```

### Interactive MCP REPL

```bash
# After creating tenant and connector
sagemcp mcp interactive <tenant-slug> <connector-id>

# In REPL:
mcp> tools                          # List tools
mcp> call github_list_repos         # Execute tool
mcp> resources                      # List resources
mcp> help                           # Show help
mcp> exit                           # Exit REPL
```

## Troubleshooting

### Command Not Found

If you get `command not found: sagemcp`:

1. **Check PATH:**
   ```bash
   echo $PATH | grep "$HOME/bin"
   ```

2. **Reload shell:**
   ```bash
   source ~/.zshrc
   ```

3. **Or open new terminal window**

4. **Use full path:**
   ```bash
   ~/bin/sagemcp version
   ```

### Permission Denied

If you get permission errors:

```bash
chmod +x /Users/manikandan/Desktop/mvmcode/SageMCP/sagemcp.sh
chmod +x ~/bin/sagemcp
```

### Script Not Working

If the wrapper script fails, use virtual environment directly:

```bash
cd /Users/manikandan/Desktop/mvmcode/SageMCP
source .venv/bin/activate
sagemcp version
```

## What Was Set Up

### 1. Wrapper Script (`sagemcp.sh`)

Location: `/Users/manikandan/Desktop/mvmcode/SageMCP/sagemcp.sh`

This script:
- Follows symlinks to find the project directory
- Activates the virtual environment
- Runs the `sagemcp` command
- Passes all arguments through

### 2. Symlink (`~/bin/sagemcp`)

Location: `/Users/manikandan/bin/sagemcp`

Points to: `/Users/manikandan/Desktop/mvmcode/SageMCP/sagemcp.sh`

### 3. PATH Configuration

Added to `~/.zshrc`:
```bash
export PATH="$HOME/bin:$PATH"
```

This makes `~/bin/sagemcp` available as `sagemcp` from anywhere.

### 4. Virtual Environment

Location: `/Users/manikandan/Desktop/mvmcode/SageMCP/.venv`

Contains all dependencies:
- typer (CLI framework)
- rich (terminal formatting)
- httpx (HTTP client)
- pyyaml (YAML support)
- toml (TOML parsing)
- All SageMCP dependencies

## File Locations

```
/Users/manikandan/
├── bin/
│   └── sagemcp                     # Symlink (global access)
├── .zshrc                          # PATH configuration
└── Desktop/mvmcode/SageMCP/
    ├── sagemcp.sh                  # Wrapper script
    ├── .venv/
    │   └── bin/
    │       └── sagemcp             # Actual CLI binary
    └── src/sage_mcp/cli/           # CLI source code
```

## Commit Changes

The CLI is ready! To commit these changes:

```bash
cd /Users/manikandan/Desktop/mvmcode/SageMCP
git add -A
git status  # Review changes
# Then commit with your message
```

## Next Steps

1. **Open a new terminal** or run `source ~/.zshrc`
2. **Test the command:** `sagemcp version`
3. **Initialize configuration:** `sagemcp init`
4. **Start backend:** `make up` (in another terminal)
5. **Use the CLI:** `sagemcp tenant list`
6. **Try interactive REPL:** `sagemcp mcp interactive <tenant> <connector>`

## Documentation

- **User Guide:** `src/sage_mcp/cli/README.md`
- **Quick Start:** `src/sage_mcp/cli/QUICKSTART.md`
- **Installation:** `src/sage_mcp/cli/INSTALLATION.md`
- **Design Doc:** `docs/cli-design.md`
- **PyPI Publishing:** `.github/docs/pypi-publishing.md`

## Summary

✅ CLI installed and working
✅ Command: `sagemcp`
✅ Version: 0.1.0
✅ Global access configured
✅ All dependencies installed
✅ Documentation complete

**To use:** Open a new terminal and type `sagemcp --help`

---

**Setup Date:** 2025-11-10
**Status:** ✅ Complete and Ready to Use
