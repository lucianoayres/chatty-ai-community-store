#!/usr/bin/env python3

import json
from typing import Dict, List, Set
import os


class TagManager:
    """Manages and validates agent tags."""

    def __init__(self, tags_file: str):
        """Initialize with path to tags definition file."""
        self.tags_file = tags_file
        self.tags = self._load_tags()

    def _load_tags(self) -> Dict:
        """Load tags from JSON file."""
        try:
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict) or 'tags' not in data:
                    raise ValueError("Invalid tags file format")
                return data['tags']
        except Exception as e:
            raise ValueError(f"Error loading tags: {e}")

    def get_valid_tags(self) -> Set[str]:
        """Get set of valid tag keys."""
        return set(self.tags.keys())

    def validate_tags(self, tags: List[str]) -> bool:
        """
        Validate a list of tags against known valid tags.
        Returns True if all tags are valid, False otherwise.
        """
        valid_tags = self.get_valid_tags()
        return all(tag in valid_tags for tag in tags)

    def get_tag_info(self, tag: str) -> Dict:
        """Get information about a specific tag."""
        if tag not in self.tags:
            raise ValueError(f"Invalid tag: {tag}")
        return self.tags[tag]

    def list_tags(self) -> List[Dict]:
        """
        List all tags with their information.
        Returns a list of dicts with tag key and info.
        """
        return [
            {"key": key, **info}
            for key, info in self.tags.items()
        ]

    def get_tags_by_example(self, agent_name: str) -> List[str]:
        """
        Find potential tags for an agent based on example matches.
        Returns a list of tag keys where the agent name matches an example.
        """
        matching_tags = []
        for tag_key, tag_info in self.tags.items():
            if 'examples' in tag_info and agent_name in tag_info['examples']:
                matching_tags.append(tag_key)
        return matching_tags
