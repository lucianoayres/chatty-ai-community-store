#!/bin/bash

# Agent Manager Tool
# This script manages the validation and indexing of agent configuration files
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
PROJECT_ROOT="$SCRIPT_DIR/../.."
JSON_SCHEMA_PATH="$PROJECT_ROOT/schemas/index.schema.json"
YAML_SCHEMA_PATH="$PROJECT_ROOT/schemas/agent.schema.yaml"
TAG_DEFINITIONS_PATH="$PROJECT_ROOT/tags.json"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install required packages
echo "Installing required packages..."
pip install pyyaml jsonschema yamale

# Verify schema files exist
if [ ! -f "$JSON_SCHEMA_PATH" ]; then
    echo "Error: JSON schema file not found: $JSON_SCHEMA_PATH"
    deactivate
    exit 1
fi

if [ ! -f "$YAML_SCHEMA_PATH" ]; then
    echo "Error: YAML schema file not found: $YAML_SCHEMA_PATH"
    deactivate
    exit 1
fi

if [ ! -f "$TAG_DEFINITIONS_PATH" ]; then
    echo "Warning: Tag definitions file not found: $TAG_DEFINITIONS_PATH"
    echo "Will use default location relative to schema path"
    TAG_DEFINITIONS_ARG=""
else
    TAG_DEFINITIONS_ARG="--tag-definitions $TAG_DEFINITIONS_PATH"
fi

# Run the agent manager
echo "Managing agents..."
cd "$PROJECT_ROOT"  # Move to project root
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
python3 "$SCRIPT_DIR/src/update_index.py" --schema "$JSON_SCHEMA_PATH" --yaml-schema "$YAML_SCHEMA_PATH" $TAG_DEFINITIONS_ARG

# Deactivate virtual environment
deactivate 