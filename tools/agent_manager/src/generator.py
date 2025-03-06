#!/usr/bin/env python3

import json
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import os
from jsonschema import validate, ValidationError


class IndexGenerator:
    def __init__(self, json_schema_path: str):
        """Initialize generator with JSON schema."""
        try:
            with open(json_schema_path, 'r', encoding='utf-8') as f:
                self.json_schema = json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading JSON schema: {e}")

    def load_existing_index(self, filepath: str) -> Dict:
        """Load existing index.json or return default structure."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "version": "1.0",
                "total_agents": 0,
                "files": []
            }

    def create_entry(self, yaml_data: Dict, filename: str, existing_entry: Dict = None) -> Dict:
        """Create an index entry from YAML data."""
        entry = {
            "id": os.path.splitext(filename)[0],
            "name": yaml_data['name'],
            "filename": filename,
            "description": yaml_data['description'],
            "emoji": yaml_data['emoji']
        }

        # Use existing timestamp or create new one
        if existing_entry and 'created_at' in existing_entry:
            entry['created_at'] = existing_entry['created_at']
        else:
            entry['created_at'] = datetime.now(
                timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        return entry

    def generate_index(self, yaml_data_list: List[Dict], filenames: List[str],
                       existing_index_path: str = 'index.json') -> Tuple[Dict, int, int]:
        """
        Generate index from validated YAML data.
        Returns: (new_index_data, added_count, updated_count)
        """
        # Load existing index for timestamps
        existing_index = self.load_existing_index(existing_index_path)
        existing_entries = {
            entry['filename']: entry for entry in existing_index.get('files', [])}

        new_files = []
        added_count = 0
        updated_count = 0

        # Process each validated YAML file
        for yaml_data, filename in zip(yaml_data_list, filenames):
            existing_entry = existing_entries.get(filename)
            entry = self.create_entry(yaml_data, filename, existing_entry)

            if not existing_entry:
                added_count += 1
            elif entry != existing_entry:
                updated_count += 1

            new_files.append(entry)

        # Create new index data
        new_index_data = {
            "version": "1.0",
            "total_agents": len(new_files),
            "files": sorted(new_files, key=lambda x: x['id'])
        }

        # Validate against JSON schema
        try:
            validate(instance=new_index_data, schema=self.json_schema)
        except ValidationError as e:
            raise ValueError(
                f"Generated index fails schema validation: {e.message}")

        return new_index_data, added_count, updated_count

    def save_index(self, data: Dict, filepath: str) -> None:
        """Save index data to file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Error saving index file: {e}")
