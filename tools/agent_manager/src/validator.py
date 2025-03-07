#!/usr/bin/env python3

import yaml
import yamale
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import os
import sys
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
            # First, check if the system_message uses literal block style in the original file
            original_content = ""
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Better detection of literal block style for system_message
            uses_literal_style = False
            import re
            # Match system_message: | with possible whitespace
            if re.search(r'system_message\s*:\s*\|', original_content):
                uses_literal_style = True

            # Load and validate the YAML content
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
                # Pass the information about the original literal style
                if 'system_message' in data:
                    YAMLWriter.write_file(
                        filepath, data, system_message_literal_style=uses_literal_style)
                else:
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
