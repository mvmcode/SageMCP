#!/bin/bash
# SageMCP CLI wrapper script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment and run sagemcp
source "$SCRIPT_DIR/.venv/bin/activate"
exec "$SCRIPT_DIR/.venv/bin/sagemcp" "$@"
