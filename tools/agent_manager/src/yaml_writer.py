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
    def write_file(filepath: str, data: Dict, system_message_literal_style=None) -> None:
        """Write data to a YAML file with consistent field ordering and formatting."""
        # Early return if data is None to prevent clearing files
        if data is None:
            raise IOError("Cannot write None data to YAML file")

        try:
            # Determine field order (to properly place system_message when writing)
            field_order = []
            for field in YAMLWriter.FIELD_ORDER:
                if field != 'system_message' and field in data:
                    field_order.append(field)

            # Special handling for system_message to preserve its original format
            system_message = None
            if 'system_message' in data and system_message_literal_style is True:
                system_message = data['system_message']
                # Create a temporary copy without system_message for normal processing
                data_copy = {k: v for k, v in data.items() if k !=
                             'system_message'}
            else:
                data_copy = data

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
            prepared_data = YAMLWriter._prepare_data(
                data_copy, system_message_literal_style)

            # Instead of using temp files and complex logic, let's build the YAML directly
            # This gives us precise control over newlines

            # Start with an empty string
            yaml_content = ""

            # Add fields before system_message
            if 'system_message' in data:
                # Find where system_message should be in the order
                system_message_index = YAMLWriter.FIELD_ORDER.index(
                    'system_message')

                # Create ordered data for fields before system_message
                before_system = OrderedDict()
                for field in YAMLWriter.FIELD_ORDER:
                    if field == 'system_message':
                        break
                    if field in prepared_data:
                        before_system[field] = prepared_data[field]

                # Create ordered data for fields after system_message
                after_system = OrderedDict()
                system_found = False
                for field in YAMLWriter.FIELD_ORDER:
                    if field == 'system_message':
                        system_found = True
                        continue
                    if system_found and field in prepared_data:
                        after_system[field] = prepared_data[field]

                # Write system_message with the | style manually
                normalized_message = YAMLWriter._normalize_line_breaks(
                    system_message)

                # Convert to YAML string
                before_yaml = yaml.safe_dump(
                    before_system,
                    allow_unicode=True,
                    default_flow_style=False,
                    width=float('inf'),
                    indent=2,
                    sort_keys=False
                ).rstrip()  # Remove trailing newlines

                yaml_content += before_yaml

                # Add exactly one newline if we have content
                if before_yaml:
                    yaml_content += "\n"

                # Add system_message with literal block style
                yaml_content += "system_message: |"

                # Process the message content
                lines = normalized_message.split('\n')

                # Write all lines with proper indentation (simplest approach)
                for line in lines:
                    yaml_content += f"\n  {line}"

                # Add fields after system_message
                if after_system:
                    # Add exactly one newline before the next field
                    yaml_content += "\n"

                    # Convert to YAML string
                    after_yaml = yaml.safe_dump(
                        after_system,
                        allow_unicode=True,
                        default_flow_style=False,
                        width=float('inf'),
                        indent=2,
                        sort_keys=False
                    )

                    # Add the after content
                    yaml_content += after_yaml
            else:
                # Normal processing for everything else
                yaml_content = yaml.safe_dump(
                    prepared_data,
                    allow_unicode=True,
                    default_flow_style=False,
                    width=float('inf'),  # Prevent line wrapping
                    indent=2,
                    sort_keys=False  # Don't sort keys, maintain our order
                )

            # Write the final content to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
        except Exception as e:
            # If we have a system_message that should use literal style
            if system_message is not None:
                # We need to write all fields in the correct order
                # Find where system_message should be in the order
                system_message_index = YAMLWriter.FIELD_ORDER.index(
                    'system_message')

                # Create ordered data for fields before system_message
                before_system = OrderedDict()
                for field in YAMLWriter.FIELD_ORDER:
                    if field == 'system_message':
                        break
                    if field in prepared_data:
                        before_system[field] = prepared_data[field]

                # Create ordered data for fields after system_message
                after_system = OrderedDict()
                system_found = False
                for field in YAMLWriter.FIELD_ORDER:
                    if field == 'system_message':
                        system_found = True
                        continue
                    if system_found and field in prepared_data:
                        after_system[field] = prepared_data[field]

                # Write system_message with the | style manually
                normalized_message = YAMLWriter._normalize_line_breaks(
                    system_message)

                # Rather than manually handling field formatting, let's create temporary files
                # and concatenate them to have precise control over spacing

                # Create temp files for each section
                temp_before = None
                temp_after = None

                if before_system:
                    temp_before = tempfile.NamedTemporaryFile(
                        mode='w+', delete=False)
                    yaml.safe_dump(
                        before_system,
                        temp_before,
                        allow_unicode=True,
                        default_flow_style=False,
                        width=float('inf'),
                        indent=2,
                        sort_keys=False,
                        explicit_end=False,
                        explicit_start=False
                    )
                    temp_before.close()

                if after_system:
                    temp_after = tempfile.NamedTemporaryFile(
                        mode='w+', delete=False)
                    yaml.safe_dump(
                        after_system,
                        temp_after,
                        allow_unicode=True,
                        default_flow_style=False,
                        width=float('inf'),
                        indent=2,
                        sort_keys=False,
                        explicit_end=False,
                        explicit_start=False
                    )
                    temp_after.close()

                # Now write the final file with exact control over spacing
                with open(filepath, 'w', encoding='utf-8') as final_file:
                    # Write fields before system_message
                    if temp_before:
                        with open(temp_before.name, 'r') as before_file:
                            content = before_file.read().rstrip('\n')
                            final_file.write(content)
                            if content:  # Only add newline if there was content
                                final_file.write('\n')

                    # Write system_message with exact formatting - ensure no trailing blank line
                    final_file.write('system_message: |')

                    # Process the message content
                    lines = normalized_message.split('\n')

                    # Write all lines with proper indentation (simplest approach)
                    for line in lines:
                        final_file.write(f"\n  {line}")

                    # Add fields after system_message
                    if temp_after:
                        # Read the after content
                        with open(temp_after.name, 'r') as after_file:
                            content = after_file.read().strip()
                            if content:  # Only if there's actual content
                                # Add exactly one newline to separate fields
                                final_file.write('\n')
                                final_file.write(content)
                # Clean up temp files
                if temp_before:
                    os.unlink(temp_before.name)
                if temp_after:
                    os.unlink(temp_after.name)
            else:
                # Normal processing for everything else
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
