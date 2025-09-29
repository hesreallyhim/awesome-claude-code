#!/usr/bin/env python3
"""
Unified category utilities for awesome-claude-code.
Provides a single source of truth for all category-related operations.

Usage:
    from category_utils import category_manager

    # Get all categories
    categories = category_manager.get_all_categories()

    # Get category by name
    cat = category_manager.get_category_by_name("Status Lines")
"""

import os

import yaml


class CategoryManager:
    """Singleton class for managing category definitions."""

    _instance = None
    _data = None

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the manager (only loads data once)."""
        if self._data is None:
            self._load_categories()

    def _load_categories(self):
        """Load category definitions from the unified YAML file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        categories_path = os.path.join(script_dir, "..", "templates", "categories.yaml")

        with open(categories_path, encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def get_all_categories(self):
        """Get list of all category names."""
        if self._data is None:
            return []
        return [cat["name"] for cat in self._data["categories"]]

    def get_category_prefixes(self):
        """Get mapping of category names to ID prefixes."""
        if self._data is None:
            return {}
        return {cat["name"]: cat["prefix"] for cat in self._data["categories"]}

    def get_category_by_name(self, name):
        """Get category configuration by name."""
        if not self._data or "categories" not in self._data:
            return None
        for cat in self._data["categories"]:
            if cat["name"] == name:
                return cat
        return None

    def get_category_by_id(self, cat_id):
        """Get category configuration by ID."""
        if not self._data or "categories" not in self._data:
            return None
        for cat in self._data["categories"]:
            if cat["id"] == cat_id:
                return cat
        return None

    def get_all_subcategories(self):
        """Get all subcategories with their parent category names."""
        subcategories = []

        if not self._data or "categories" not in self._data:
            return None

        for cat in self._data["categories"]:
            if "subcategories" in cat:
                for subcat in cat["subcategories"]:
                    subcategories.append(
                        {
                            "parent": cat["name"],
                            "name": subcat["name"],
                            "full_name": f"{cat['name']}: {subcat['name']}",
                        }
                    )

        return subcategories

    def get_subcategories_for_category(self, category_name):
        """Get subcategories for a specific category."""
        cat = self.get_category_by_name(category_name)
        if not cat or "subcategories" not in cat:
            return []

        return [subcat["name"] for subcat in cat["subcategories"]]

    def validate_category_subcategory(self, category, subcategory):
        """Validate that a subcategory belongs to the given category."""
        if not subcategory:
            return True

        cat = self.get_category_by_name(category)
        if not cat:
            return False

        if "subcategories" not in cat:
            return False

        return any(subcat["name"] == subcategory for subcat in cat["subcategories"])

    def get_categories_for_readme(self):
        """Get categories in order for README generation."""
        if not self._data or "categories" not in self._data:
            return []
        categories = sorted(self._data["categories"], key=lambda x: x.get("order", 999))
        return categories

    def get_toc_config(self):
        """Get table of contents configuration."""
        return self._data.get("toc", {}) if self._data else {}


# Create singleton instance for import
category_manager = CategoryManager()
