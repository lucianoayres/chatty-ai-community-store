#!/usr/bin/env python3

import yaml
import yamale
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import os
import sys
import argparse
from yaml_writer import YAMLWriter
from tag_manager import TagManager


class AgentValidator:
    def __init__(self, yaml_schema_path: str, tag_definitions_path: str = None, error_log_path: str = "sync_errors.log"):
        """Initialize validator with schema, tag definitions path, and error log path.

        Args:
            yaml_schema_path: Path to the YAML schema file for validation
            tag_definitions_path: Path to the tag definitions JSON file. If None, will look for
                                  'agent_tag_definitions.json' in the same directory as the schema.
            error_log_path: Path to write error logs to
        """
        self.error_log_path = error_log_path
        try:
            self.yaml_schema = yamale.make_schema(yaml_schema_path)

            # Use provided tag definitions path or default to looking in schema directory
            if tag_definitions_path is None:
                tag_definitions_path = os.path.join(
                    os.path.dirname(yaml_schema_path), 'agent_tag_definitions.json')

            self.tag_manager = TagManager(tag_definitions_path)
        except Exception as e:
            raise ValueError(f"Error initializing validator: {e}")

    def log_error(self, filename: str, error: str) -> None:
        """Log an error with timestamp."""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {filename}: {error}\n")
        except IOError as e:
            print(
                f"Warning: Could not write to error log: {e}", file=sys.stderr)

    def validate_yaml(self, filepath: str) -> Tuple[Dict, bool]:
        """Validate a single YAML file against schema."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                self.log_error(filepath, "YAML file must contain a dictionary")
                return None, False

            try:
                # Validate against schema
                yamale.validate(self.yaml_schema, [(data, filepath)])

                # Validate tags
                if 'tags' in data:
                    if not self.tag_manager.validate_tags(data['tags']):
                        invalid_tags = [t for t in data['tags']
                                        if t not in self.tag_manager.get_valid_tags()]
                        self.log_error(
                            filepath, f"Invalid tags: {', '.join(invalid_tags)}")
                        return None, False

                # Suggest tags if none provided
                if 'tags' not in data and 'name' in data:
                    suggested_tags = self.tag_manager.get_tags_by_example(
                        data['name'])
                    if suggested_tags:
                        print(
                            f"Suggested tags for {data['name']}: {', '.join(suggested_tags)}")

                # Only write the file if validation was successful
                YAMLWriter.write_file(filepath, data)
                return data, True

            except ValueError as e:
                self.log_error(
                    filepath, f"YAML schema validation error: {str(e)}")
                return None, False

        except yaml.YAMLError as e:
            self.log_error(filepath, f"YAML parsing error: {str(e)}")
            return None, False
        except FileNotFoundError:
            self.log_error(filepath, "File not found")
            return None, False
        except Exception as e:
            self.log_error(filepath, f"Unexpected error: {str(e)}")
            return None, False

    def validate_directory(self, directory: str) -> Tuple[List[Dict], List[str], int]:
        """
        Validate all YAML files in a directory.
        Returns: (valid_data_list, valid_files, error_count)
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        yaml_files = sorted(
            [f for f in os.listdir(directory) if f.endswith('.yaml')])
        valid_data = []
        valid_files = []
        error_count = 0

        for filename in yaml_files:
            filepath = os.path.join(directory, filename)
            data, is_valid = self.validate_yaml(filepath)

            if is_valid:
                valid_data.append(data)
                valid_files.append(filename)
            else:
                error_count += 1

        return valid_data, valid_files, error_count

    def print_validation_error(self, filename: str, error: str, output_format: str = "plain") -> None:
        """Print a validation error in the specified format."""
        if output_format == "github-actions":
            # GitHub Actions annotation format
            file_only = os.path.basename(filename)
            print(f"::error file={filename}::{error}")
        else:
            # Plain text format
            print(f"Error in {filename}: {error}")


def main():
    """Command line interface for the validator."""
    parser = argparse.ArgumentParser(
        description='Validate agent YAML files against schema')
    parser.add_argument('--yaml-schema', required=True,
                        help='Path to YAML schema file')
    parser.add_argument('--tag-definitions', required=False,
                        help='Path to tag definitions JSON file')
    parser.add_argument('--error-log', required=False,
                        default='sync_errors.log', help='Path for error log file')
    parser.add_argument('--file', help='Validate a single agent YAML file')
    parser.add_argument(
        '--directory', help='Validate all agent YAML files in a directory')
    parser.add_argument('--output-format', choices=['plain', 'github-actions'], default='plain',
                        help='Output format for validation results')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output with detailed error information')

    args = parser.parse_args()

    if not args.file and not args.directory:
        print("Error: You must specify either --file or --directory")
        sys.exit(1)

    try:
        validator = AgentValidator(
            args.yaml_schema,
            tag_definitions_path=args.tag_definitions,
            error_log_path=args.error_log
        )

        if args.file:
            # Validate a single file
            data, is_valid = validator.validate_yaml(args.file)

            if is_valid:
                print(f"✓ {args.file} is valid")
                sys.exit(0)
            else:
                if args.output_format == "github-actions":
                    print(f"::error file={args.file}::Validation failed")
                else:
                    print(f"✗ {args.file} failed validation")

                # If verbose mode is enabled, provide detailed error information
                if args.verbose:
                    print("\nValidation Errors:")
                    # Check for known error types
                    with open(args.error_log, 'r') as error_log:
                        for line in error_log:
                            if args.file in line:
                                print(f"  {line.strip()}")

                    # Check for missing required fields
                    try:
                        with open(args.file, 'r') as f:
                            file_data = yaml.safe_load(f)

                        # Check basic structure
                        if not isinstance(file_data, dict):
                            print("  Error: YAML file must contain a dictionary")
                        else:
                            # Check required fields
                            required_fields = ['name', 'emoji', 'description', 'system_message',
                                               'label_color', 'text_color', 'is_default']
                            missing_fields = [
                                field for field in required_fields if field not in file_data]
                            if missing_fields:
                                print(
                                    f"  Error: Missing required fields: {', '.join(missing_fields)}")

                            # Check tags if present
                            if 'tags' in file_data:
                                if not isinstance(file_data['tags'], list):
                                    print("  Error: 'tags' field must be a list")
                                elif not validator.tag_manager.validate_tags(file_data['tags']):
                                    invalid_tags = [t for t in file_data['tags']
                                                    if t not in validator.tag_manager.get_valid_tags()]
                                    print(
                                        f"  Error: Invalid tags: {', '.join(invalid_tags)}")
                    except Exception as e:
                        print(f"  Error analyzing file: {str(e)}")

                sys.exit(1)

        elif args.directory:
            # Validate all files in a directory
            valid_data, valid_files, error_count = validator.validate_directory(
                args.directory)

            print(
                f"Validation complete: {len(valid_files)} valid files, {error_count} errors")

            if args.verbose and error_count > 0:
                print("\nError details:")
                with open(args.error_log, 'r') as error_log:
                    for line in error_log:
                        if args.directory in line:
                            print(f"  {line.strip()}")

            if error_count > 0:
                sys.exit(1)
            else:
                sys.exit(0)

    except Exception as e:
        print(f"Error during validation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
