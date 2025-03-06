#!/usr/bin/env python3

import sys
import argparse
from src.validator import AgentValidator
from src.generator import IndexGenerator


def update_index(json_schema_path: str, yaml_schema_path: str) -> None:
    """
    Update the index.json file based on the agent YAML files.
    Part of the agent manager toolset that handles validation and indexing of agent configurations.
    """
    try:
        # Initialize validator and generator
        validator = AgentValidator(yaml_schema_path)
        generator = IndexGenerator(json_schema_path)

        # Validate all YAML files
        agents_dir = 'agents'
        valid_data, valid_files, error_count = validator.validate_directory(
            agents_dir)

        if not valid_files:
            print("No valid agent files found to process.", file=sys.stderr)
            sys.exit(1)

        # Generate new index
        try:
            new_index, added_count, updated_count = generator.generate_index(
                valid_data, valid_files)
        except ValueError as e:
            print(f"Error generating index: {e}", file=sys.stderr)
            sys.exit(1)

        # Save the updated index
        try:
            generator.save_index(new_index, 'index.json')
        except IOError as e:
            print(f"Error saving index: {e}", file=sys.stderr)
            sys.exit(1)

        # Print summary
        print(f"\nAgent management complete:")
        print(f"- Total agents: {len(valid_files)}")
        print(f"- New agents added: {added_count}")
        print(f"- Existing agents updated: {updated_count}")
        print(f"- Files with errors: {error_count}")
        if error_count > 0:
            print(f"  See {validator.error_log_path} for error details")

    except Exception as e:
        print(
            f"Unexpected error during agent management: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Manage and index agent configuration files')
    parser.add_argument('--schema', required=True,
                        help='Path to JSON schema file')
    parser.add_argument('--yaml-schema', required=True,
                        help='Path to YAML schema file')
    args = parser.parse_args()

    update_index(args.schema, args.yaml_schema)


if __name__ == "__main__":
    main()
