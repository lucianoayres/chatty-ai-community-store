#!/usr/bin/env python3

import yaml
import re
from typing import Dict, Any, List
from collections import OrderedDict


class LiteralString(str):
    """String that will use literal block style (|) in YAML."""
    pass


class YAMLWriter:
    """Handles writing YAML files with consistent formatting."""

    # Define the standard field order for agent YAML files
    FIELD_ORDER = [
        'name',
        'emoji',
        'description',
        'system_message',
        'label_color',
        'text_color',
        'is_default',
        'tags',
        'author'  # Optional field
    ]

    @staticmethod
    def _literal_presenter(dumper: yaml.Dumper, data: LiteralString) -> yaml.ScalarNode:
        """Present string in literal block style (|)."""
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

    @staticmethod
    def _should_use_literal_block(value: str, field_name: str) -> bool:
        """Determine if a string should use the literal block style (|)."""
        # Never use literal block style for system_message field
        if field_name == 'system_message':
            return False
        # For other fields, use literal block if multiline or long
        return '\n' in value or len(value) > 80

    @staticmethod
    def _normalize_line_breaks(value: str) -> str:
        """
        Normalize consecutive line breaks in text.
        Keeps single line breaks intact.
        Reduces multiple consecutive line breaks (2+) to a single line break.
        """
        # Split the text into lines
        lines = value.split('\n')
        normalized_lines = []

        # Keep track of consecutive empty lines
        empty_line_count = 0

        for line in lines:
            if line.strip() == '':
                # This is an empty line
                empty_line_count += 1
            else:
                # This is a non-empty line
                # If we had empty lines before, add one empty line
                if empty_line_count > 0:
                    normalized_lines.append('')
                # Reset counter
                empty_line_count = 0
                # Add the current line
                normalized_lines.append(line)

        # If the text ends with empty lines, preserve one
        if empty_line_count > 0:
            normalized_lines.append('')

        # Join the lines back together
        return '\n'.join(normalized_lines)

    @staticmethod
    def _prepare_data(data: Dict[str, Any]) -> OrderedDict:
        """Prepare data for YAML dumping by marking multi-line strings and ordering fields."""
        # Create an ordered dictionary with fields in the correct order
        ordered_data = OrderedDict()

        # Add fields in the specified order
        for field in YAMLWriter.FIELD_ORDER:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    # Normalize line breaks for system_message field
                    if field == 'system_message':
                        value = YAMLWriter._normalize_line_breaks(value)
                    # Check if literal block style should be used
                    if YAMLWriter._should_use_literal_block(value, field):
                        ordered_data[field] = LiteralString(value)
                    else:
                        ordered_data[field] = value
                else:
                    ordered_data[field] = value

        return ordered_data

    @staticmethod
    def write_file(filepath: str, data: Dict) -> None:
        """Write data to a YAML file with consistent field ordering and formatting."""
        # Early return if data is None to prevent clearing files
        if data is None:
            raise IOError("Cannot write None data to YAML file")

        try:
            # Register the literal string presenter
            yaml.add_representer(
                LiteralString, YAMLWriter._literal_presenter, Dumper=yaml.SafeDumper)

            # Add representer for OrderedDict to maintain order
            yaml.add_representer(
                OrderedDict,
                lambda dumper, data: dumper.represent_mapping(
                    'tag:yaml.org,2002:map', data.items()),
                Dumper=yaml.SafeDumper
            )

            # Prepare the data
            prepared_data = YAMLWriter._prepare_data(data)

            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    prepared_data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    width=float('inf'),  # Prevent line wrapping
                    indent=2,
                    sort_keys=False  # Don't sort keys, maintain our order
                )
        except Exception as e:
            raise IOError(f"Error writing YAML file: {e}")
