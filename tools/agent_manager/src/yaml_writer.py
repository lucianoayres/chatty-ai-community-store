#!/usr/bin/env python3

import yaml
import re
from typing import Dict, Any, List
from collections import OrderedDict
import tempfile
import os


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
    def _should_use_literal_block(value: str, field_name: str, system_message_literal_style=None) -> bool:
        """Determine if a string should use the literal block style (|)."""
        # For system_message, use the original style if specified
        if field_name == 'system_message' and system_message_literal_style is not None:
            return system_message_literal_style
        # Otherwise, use literal block if multiline or long
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
    def _prepare_data(data: Dict[str, Any], system_message_literal_style=None) -> OrderedDict:
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
                    if YAMLWriter._should_use_literal_block(value, field, system_message_literal_style):
                        ordered_data[field] = LiteralString(value)
                    else:
                        ordered_data[field] = value
                else:
                    ordered_data[field] = value

        return ordered_data

    @staticmethod
    def _format_tags(tags_list):
        """Format tags list with proper indentation."""
        if not tags_list:
            return "tags: []"

        result = "tags:"
        for tag in tags_list:
            result += f"\n  - {tag}"
        return result

    @staticmethod
    def write_file(filepath: str, data: Dict, system_message_literal_style=None) -> None:
        """Write data to a YAML file with consistent field ordering and formatting."""
        # Early return if data is None to prevent clearing files
        if data is None:
            raise IOError("Cannot write None data to YAML file")

        try:
            # Create a new OrderedDict to maintain field order exactly as specified in FIELD_ORDER
            final_output = OrderedDict()

            # Process each field in the specified order
            for field in YAMLWriter.FIELD_ORDER:
                if field in data:
                    if field == 'tags' and isinstance(data['tags'], list):
                        # Skip tags for now, we'll handle them specially later
                        pass
                    elif field == 'system_message' and system_message_literal_style is True:
                        # Skip system_message for now if it should use literal style
                        pass
                    else:
                        # Normal processing for all other fields
                        value = data[field]
                        if isinstance(value, str):
                            # Normalize line breaks for system_message field
                            if field == 'system_message':
                                value = YAMLWriter._normalize_line_breaks(
                                    value)
                            # Check if literal block style should be used
                            if YAMLWriter._should_use_literal_block(value, field, system_message_literal_style):
                                final_output[field] = LiteralString(value)
                            else:
                                final_output[field] = value
                        else:
                            final_output[field] = value

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

            # Build a manually formatted YAML string to ensure proper order and formatting
            yaml_content = ""

            # First write all normal fields (not tags or system_message with literal style)
            temp_output = OrderedDict()
            for field, value in final_output.items():
                temp_output[field] = value

            if temp_output:
                yaml_content = yaml.safe_dump(
                    temp_output,
                    allow_unicode=True,
                    default_flow_style=False,
                    width=float('inf'),
                    indent=2,
                    sort_keys=False
                ).rstrip()

            # Now manually add any special fields in the correct position
            final_content = []

            for field in YAMLWriter.FIELD_ORDER:
                if field == 'system_message' and 'system_message' in data and system_message_literal_style is True:
                    # Add system_message with literal block style
                    system_message = data['system_message']
                    normalized_message = YAMLWriter._normalize_line_breaks(
                        system_message)

                    system_content = "system_message: |"
                    for line in normalized_message.split('\n'):
                        system_content += f"\n  {line}"

                    final_content.append(system_content)

                elif field == 'tags' and 'tags' in data and isinstance(data['tags'], list):
                    # Add tags with proper indentation
                    tags_content = data['tags']
                    tags_formatted = YAMLWriter._format_tags(tags_content)
                    final_content.append(tags_formatted)

                elif field in final_output:
                    # Extract this field from the yaml_content
                    field_pattern = f"{field}:"
                    lines = yaml_content.split('\n')
                    field_content = []

                    found = False
                    for i, line in enumerate(lines):
                        if line.startswith(field_pattern):
                            found = True
                            field_content.append(line)

                            # Also add any indented lines that follow this field
                            j = i + 1
                            while j < len(lines) and (lines[j].startswith('  ') or not lines[j].strip()):
                                field_content.append(lines[j])
                                j += 1

                    if found:
                        final_content.append('\n'.join(field_content))

            # Write the final content to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(final_content))
                f.write('\n')  # End file with newline

        except Exception as e:
            raise IOError(f"Error writing YAML file: {e}")
