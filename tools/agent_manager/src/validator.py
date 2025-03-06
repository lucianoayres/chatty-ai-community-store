#!/usr/bin/env python3

import yaml
import yamale
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import os
import sys


class AgentValidator:
    def __init__(self, yaml_schema_path: str, error_log_path: str = "sync_errors.log"):
        """Initialize validator with schema and error log path."""
        self.error_log_path = error_log_path
        try:
            self.yaml_schema = yamale.make_schema(yaml_schema_path)
        except Exception as e:
            raise ValueError(f"Error loading YAML schema: {e}")

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
                yamale.validate(self.yaml_schema, [(data, filepath)])
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
