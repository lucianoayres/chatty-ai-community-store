#!/usr/bin/env python3

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime, timezone
from jsonschema import validate, ValidationError


class IndexGenerator:
    """Generates and updates the agent_index.json file."""

    def __init__(self, json_schema_path: str):
        """Initialize with path to JSON schema file."""
        self.json_schema_path = json_schema_path
        self.version = "1.0"

    def _create_entry(self, data: Dict, filename: str) -> Dict:
        """Create an index entry from agent data."""
        # Get ID from filename (remove .yaml extension)
        agent_id = os.path.splitext(filename)[0]

        entry = {
            "id": agent_id,
            "name": data["name"],
            "filename": filename,
            "description": data["description"],
            "emoji": data["emoji"],
            "created_at": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "tags": data["tags"]
        }

        # Add optional author field if present
        if "author" in data and data["author"]:
            entry["author"] = data["author"]

        return entry

    def generate_index(self, valid_data: List[Dict], valid_files: List[str]) -> Tuple[Dict, int, int]:
        """
        Generate new index from validated agent data.
        Returns: (new_index, added_count, updated_count)
        """
        # Load existing index if it exists
        existing_index = {}
        try:
            with open('agent_index.json', 'r', encoding='utf-8') as f:
                existing_index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_index = {"version": self.version,
                              "total_agents": 0, "files": []}

        # Create new index
        new_index = {
            "version": self.version,
            "total_agents": len(valid_files),
            "files": []
        }

        added_count = 0
        updated_count = 0

        # Process each valid agent
        for data, filename in zip(valid_data, valid_files):
            new_entry = self._create_entry(data, filename)

            # Check if agent already exists
            existing_entry = next(
                (entry for entry in existing_index.get("files", [])
                 if entry["id"] == new_entry["id"]),
                None
            )

            if existing_entry:
                # Preserve creation timestamp for existing entries
                new_entry["created_at"] = existing_entry["created_at"]
                updated_count += 1
            else:
                added_count += 1

            new_index["files"].append(new_entry)

        # Sort entries by ID for consistency
        new_index["files"].sort(key=lambda x: x["id"])

        return new_index, added_count, updated_count

    def save_index(self, index: Dict, filepath: str) -> None:
        """Save index to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Error saving index: {e}")
