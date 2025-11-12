# SageMCP CLI Installation Guide

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Access to a running SageMCP server

## Installation Methods

### Method 1: Install from Source (Development)

This is the recommended method for development and testing:

```bash
# Clone the repository
git clone https://github.com/mvmcode/SageMCP.git
cd SageMCP

# Install with CLI support in editable mode
pip install -e ".[cli]"

# Verify installation
sagemcp --version
```

### Method 2: Install from PyPI (When Published)

Once the package is published to PyPI:

```bash
# Install the latest version
pip install sage-mcp[cli]

# Or install a specific version
pip install sage-mcp[cli]==0.1.0
```

### Method 3: Install with All Dependencies

For development with all optional features:

```bash
# Install with CLI and dev dependencies
pip install -e ".[cli,dev]"
```

## Dependencies

The CLI installation includes:

- **typer[all]** - CLI framework with rich formatting
- **rich** - Beautiful terminal output
- **pyyaml** - YAML parsing and generation
- **toml** - TOML configuration file support
- **httpx** - HTTP client (already in base dependencies)

## Post-Installation Setup

### 1. Initialize Configuration

```bash
sagemcp init
```

This will:
- Create `~/.sage-mcp/` directory
- Generate default configuration file
- Walk you through profile setup

### 2. Configure Your First Profile

During initialization, you'll be prompted for:
- **Profile name** (default: "default")
- **API base URL** (e.g., http://localhost:8000)
- **API key** (optional, for authenticated access)

Example:

```
Welcome to SageMCP CLI!

Create New Profile

Profile name [default]: default
API base URL [http://localhost:8000]: http://localhost:8000
API key (optional, press Enter to skip):

Configuration initialized with profile 'default'
```

### 3. Verify Server Connection

```bash
sagemcp version --verbose
```

Expected output:

```
SageMCP CLI v0.1.0
Python: 3.11.5
API URL: http://localhost:8000
Server: reachable ✓
```

## Configuration File

The CLI stores configuration in `~/.sage-mcp/config.toml`:

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

## Multiple Environments

Set up profiles for different environments:

```bash
# Development
sagemcp config init --profile dev --base-url http://localhost:8000

# Staging
sagemcp config init --profile staging --base-url https://staging.sagemcp.com

# Production
sagemcp config init --profile prod --base-url https://api.sagemcp.com

# Switch between profiles
sagemcp tenant list --profile prod
```

## Shell Completion (Optional)

Enable tab completion for your shell:

### Bash

```bash
sagemcp --install-completion bash
source ~/.bashrc
```

### Zsh

```bash
sagemcp --install-completion zsh
source ~/.zshrc
```

### Fish

```bash
sagemcp --install-completion fish
```

## Upgrading

### From Source

```bash
cd SageMCP
git pull
pip install -e ".[cli]" --upgrade
```

### From PyPI

```bash
pip install sage-mcp[cli] --upgrade
```

## Uninstallation

```bash
# Uninstall the package
pip uninstall sage-mcp

# Optionally remove configuration
rm -rf ~/.sage-mcp/
```

## Troubleshooting

### Command Not Found

If `sagemcp` is not found after installation:

```bash
# Check if it's installed
pip list | grep sage-mcp

# Try using the alternate command
sagemcp --version

# Or run as module
python -m sage_mcp.cli.main --version

# Check your PATH
echo $PATH

# Reinstall
pip install -e ".[cli]" --force-reinstall
```

### Import Errors

If you get import errors:

```bash
# Ensure all dependencies are installed
pip install typer[all] rich pyyaml toml

# Or reinstall with CLI extras
pip install -e ".[cli]" --force-reinstall
```

### Permission Errors

If you get permission errors:

```bash
# Use user installation
pip install --user -e ".[cli]"

# Or use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[cli]"
```

### Configuration Issues

If configuration is corrupted:

```bash
# Backup existing config
cp ~/.sage-mcp/config.toml ~/.sage-mcp/config.toml.backup

# Remove and reinitialize
rm ~/.sage-mcp/config.toml
sagemcp init
```

## Development Installation

For contributing to the CLI:

```bash
# Clone the repository
git clone https://github.com/mvmcode/SageMCP.git
cd SageMCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[cli,dev]"

# Run tests
pytest tests/cli/ -v

# Check code style
black src/sage_mcp/cli/
flake8 src/sage_mcp/cli/
```

## Next Steps

After installation:

1. **Read the documentation**: [CLI README](README.md)
2. **Try examples**: Start with `sagemcp tenant list`
3. **Explore commands**: Use `sagemcp --help`
4. **Read the design**: [CLI Design Document](../../../docs/cli-design.md)

## Getting Help

- Run `sagemcp --help` for command overview
- Run `sagemcp COMMAND --help` for command-specific help
- Check [GitHub Issues](https://github.com/mvmcode/SageMCP/issues)
- Join our [Discord](https://discord.gg/kpHzRzmy)

## System Requirements

- **OS**: Linux, macOS, Windows (with WSL recommended)
- **Python**: 3.11+
- **Disk Space**: ~50 MB for CLI dependencies
- **Network**: Internet connection for API access
- **Terminal**: Any modern terminal with Unicode support
