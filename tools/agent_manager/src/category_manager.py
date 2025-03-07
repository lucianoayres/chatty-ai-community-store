#!/usr/bin/env python3

import yaml
from typing import Dict, List, Set
import os


class CategoryManager:
    """Manages and validates agent categories."""

    def __init__(self, categories_file: str):
        """Initialize with path to categories definition file."""
        self.categories_file = categories_file
        self.categories = self._load_categories()

    def _load_categories(self) -> Dict:
        """Load categories from YAML file."""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict) or 'categories' not in data:
                    raise ValueError("Invalid categories file format")
                return data['categories']
        except Exception as e:
            raise ValueError(f"Error loading categories: {e}")

    def get_valid_categories(self) -> Set[str]:
        """Get set of valid category keys."""
        return set(self.categories.keys())

    def validate_categories(self, categories: List[str]) -> bool:
        """
        Validate a list of categories against known valid categories.
        Returns True if all categories are valid, False otherwise.
        """
        valid_categories = self.get_valid_categories()
        return all(category in valid_categories for category in categories)

    def get_category_info(self, category: str) -> Dict:
        """Get information about a specific category."""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
        return self.categories[category]

    def list_categories(self) -> List[Dict]:
        """
        List all categories with their information.
        Returns a list of dicts with category key and info.
        """
        return [
            {"key": key, **info}
            for key, info in self.categories.items()
        ]

    def get_categories_by_example(self, agent_name: str) -> List[str]:
        """
        Find potential categories for an agent based on example matches.
        Returns a list of category keys where the agent name matches an example.
        """
        matching_categories = []
        for cat_key, cat_info in self.categories.items():
            if agent_name in cat_info.get('examples', []):
                matching_categories.append(cat_key)
        return matching_categories
