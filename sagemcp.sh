#!/bin/bash
# SageMCP CLI wrapper script

# Follow symlinks to get the real script location (macOS compatible)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# Use absolute path to the project directory
PROJECT_DIR="/Users/manikandan/Desktop/mvmcode/SageMCP"

# Activate the virtual environment and run sagemcp
source "$PROJECT_DIR/.venv/bin/activate"
exec "$PROJECT_DIR/.venv/bin/sagemcp" "$@"
