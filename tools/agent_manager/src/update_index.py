#!/usr/bin/env python3

import sys
import argparse
from validator import AgentValidator
from generator import IndexGenerator
import os


def update_index(json_schema_path: str, yaml_schema_path: str, tag_definitions_path: str = None) -> None:
    """
    Update the agent_index.json file based on the agent YAML files.
    Part of the agent manager toolset that handles validation and indexing of agent configurations.

    Args:
        json_schema_path: Path to the JSON schema file for the index
        yaml_schema_path: Path to the YAML schema file for agents
        tag_definitions_path: Path to the tag definitions JSON file (optional)
    """
    try:
        # Initialize validator and generator
        validator = AgentValidator(yaml_schema_path, tag_definitions_path)
        generator = IndexGenerator(json_schema_path)

        # Validate all YAML files
        agents_dir = 'agents'

        # Debug: List all files in the agents directory
        print("\nDebug: Files in agents directory:")
        for f in os.listdir(agents_dir):
            print(f"  - {f}")

        valid_data, valid_files, error_count = validator.validate_directory(
            agents_dir)

        # Debug: Show validation results details
        print("\nDebug: Validation results:")
        print(f"  Valid files count: {len(valid_files)}")
        print(f"  Valid files: {', '.join(valid_files)}")
        print(f"  Error count: {error_count}")

        if not valid_files:
            print("No valid agent files found to process.", file=sys.stderr)
            sys.exit(1)

        # Generate new index
        try:
            new_index, added_count, updated_count = generator.generate_index(
                valid_data, valid_files)

            # Add author field for entries where it exists in YAML
            for i, (data, filename) in enumerate(zip(valid_data, valid_files)):
                if 'author' in data and data['author']:
                    # Find the corresponding entry in the index
                    for entry in new_index['files']:
                        if entry['filename'] == filename:
                            entry['author'] = data['author']
                            break

        except ValueError as e:
            print(f"Error generating index: {e}", file=sys.stderr)
            sys.exit(1)

        # Save the updated index
        try:
            generator.save_index(new_index, 'agent_index.json')
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
    parser.add_argument('--tag-definitions', required=False,
                        help='Path to tag definitions JSON file')
    args = parser.parse_args()

    update_index(args.schema, args.yaml_schema, args.tag_definitions)


if __name__ == "__main__":
    main()
