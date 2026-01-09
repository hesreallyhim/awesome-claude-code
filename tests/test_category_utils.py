#!/usr/bin/env python3
"""
Unit tests for the CategoryManager class.
"""

import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.categories.category_utils import CategoryManager  # noqa: E402


def create_test_categories() -> dict[str, Any]:
    """Create test category data."""
    return {
        "categories": [
            {
                "id": "cat1",
                "name": "Category One",
                "prefix": "c1",
                "icon": "🔵",
                "description": "First test category",
                "order": 2,
                "subcategories": [
                    {"id": "sub1", "name": "Subcategory A"},
                    {"id": "sub2", "name": "Subcategory B"},
                ],
            },
            {
                "id": "cat2",
                "name": "Category Two",
                "prefix": "c2",
                "icon": "🟢",
                "description": "Second test category",
                "order": 1,
            },
            {
                "id": "cat3",
                "name": "Category Three",
                "prefix": "c3",
                "icon": "🔴",
                "description": "Third test category",
                "order": 3,
                "subcategories": [
                    {"id": "sub3", "name": "Subcategory C"},
                ],
            },
        ],
        "toc": {
            "style": "test",
            "symbol": "►",
            "subsymbol": "▸",
            "indent": "  ",
            "subindent": "    ",
        },
    }


def test_get_all_categories() -> None:
    """Test getting all category names."""
    # Create a new instance with test data
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    categories = manager.get_all_categories()

    # Check we have the expected test categories
    assert "Category One" in categories
    assert "Category Two" in categories
    assert "Category Three" in categories
    assert len(categories) == 3


def test_get_category_prefixes() -> None:
    """Test getting category ID prefixes."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    prefixes = manager.get_category_prefixes()

    # Check mappings from our test data
    assert prefixes["Category One"] == "c1"
    assert prefixes["Category Two"] == "c2"
    assert prefixes["Category Three"] == "c3"
    assert len(prefixes) == 3


def test_get_category_by_name() -> None:
    """Test retrieving category by name."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    # Test existing category
    cat_one = manager.get_category_by_name("Category One")
    assert cat_one is not None
    assert cat_one["id"] == "cat1"
    assert cat_one["prefix"] == "c1"
    assert cat_one["icon"] == "🔵"
    assert len(cat_one["subcategories"]) == 2

    # Test non-existent category
    nonexistent = manager.get_category_by_name("NonExistent")
    assert nonexistent is None


def test_get_category_by_id() -> None:
    """Test retrieving category by ID."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    # Test existing category
    cat_two = manager.get_category_by_id("cat2")
    assert cat_two is not None
    assert cat_two["name"] == "Category Two"
    assert cat_two["prefix"] == "c2"
    assert "subcategories" not in cat_two  # No subcategories

    # Test non-existent category
    nonexistent = manager.get_category_by_id("nonexistent")
    assert nonexistent is None


def test_get_all_subcategories() -> None:
    """Test getting all subcategories with parent info."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    subcategories = manager.get_all_subcategories()

    # Check we have the right number of subcategories
    assert subcategories and len(subcategories) == 3  # sub1, sub2, sub3

    # Check subcategory structure
    sub_a = (
        next((s for s in subcategories if s["name"] == "Subcategory A"), None)
        if subcategories
        else None
    )
    assert sub_a is not None
    assert sub_a["parent"] == "Category One"
    assert sub_a["full_name"] == "Category One: Subcategory A"

    sub_c = (
        next((s for s in subcategories if s["name"] == "Subcategory C"), None)
        if subcategories
        else None
    )
    assert sub_c is not None
    assert sub_c["parent"] == "Category Three"


def test_get_subcategories_for_category() -> None:
    """Test getting subcategories for a specific category."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    # Category with subcategories
    cat_one_subs = manager.get_subcategories_for_category("Category One")
    assert "Subcategory A" in cat_one_subs
    assert "Subcategory B" in cat_one_subs
    assert len(cat_one_subs) == 2

    # Category without subcategories
    cat_two_subs = manager.get_subcategories_for_category("Category Two")
    assert cat_two_subs == []

    # Non-existent category
    nonexistent_subs = manager.get_subcategories_for_category("NonExistent")
    assert nonexistent_subs == []


def test_validate_category_subcategory() -> None:
    """Test validation of category-subcategory relationships."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    # Valid combinations
    assert manager.validate_category_subcategory("Category One", "Subcategory A") is True
    assert manager.validate_category_subcategory("Category Three", "Subcategory C") is True

    # No subcategory (always valid for existing categories)
    assert manager.validate_category_subcategory("Category Two", "") is True
    assert manager.validate_category_subcategory("Category Two", None) is True

    # Invalid combinations
    assert manager.validate_category_subcategory("Category One", "Subcategory C") is False
    assert manager.validate_category_subcategory("Category Two", "Subcategory A") is False
    assert manager.validate_category_subcategory("NonExistent", "Something") is False


def test_get_categories_for_readme() -> None:
    """Test getting categories ordered for README generation."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    categories = manager.get_categories_for_readme()

    # Check ordering - should be sorted by 'order' field
    assert categories[0]["id"] == "cat2"  # order: 1
    assert categories[1]["id"] == "cat1"  # order: 2
    assert categories[2]["id"] == "cat3"  # order: 3

    # All categories should be present
    assert len(categories) == 3


def test_get_toc_config() -> None:
    """Test getting table of contents configuration."""
    manager = CategoryManager()
    CategoryManager._data = create_test_categories()

    toc_config = manager.get_toc_config()

    # Check test TOC settings
    assert toc_config["style"] == "test"
    assert toc_config["symbol"] == "►"
    assert toc_config["subsymbol"] == "▸"
    assert toc_config["indent"] == "  "
    assert toc_config["subindent"] == "    "


def test_singleton_behavior() -> None:
    """Test that CategoryManager behaves as a singleton."""
    # Create new instances
    instance1 = CategoryManager()
    instance2 = CategoryManager()

    # They should be the same object
    assert instance1 is instance2


def test_loading_from_file() -> None:
    """Test loading categories from a YAML file."""
    # Create a temporary YAML file with test data
    test_data = create_test_categories()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(test_data, f)
        temp_path = f.name

    try:
        # Patch the _load_categories method to load from our temp file
        original_load = CategoryManager._load_categories

        def mock_load(self: Any) -> None:
            with open(temp_path, encoding="utf-8") as f:
                type(self)._data = yaml.safe_load(f)

        CategoryManager._load_categories = mock_load  # type: ignore[method-assign]

        # Create a fresh instance (reset singleton)
        CategoryManager._instance = None
        CategoryManager._data = None

        manager = CategoryManager()

        # Verify data was loaded correctly
        categories = manager.get_all_categories()
        assert len(categories) == 3
        assert "Category One" in categories

        # Restore original method
        CategoryManager._load_categories = original_load  # type: ignore[method-assign]
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_robustness_with_missing_fields() -> None:
    """Test that the manager handles missing optional fields gracefully."""
    manager = CategoryManager()
    CategoryManager._data = {
        "categories": [
            {
                "id": "minimal",
                "name": "Minimal Category",
                "prefix": "min",
                # No icon, description, order, or subcategories
            },
            {
                "id": "partial",
                "name": "Partial Category",
                "prefix": "par",
                "icon": "🟡",
                # No description or order
                "subcategories": [],
            },
        ],
        "toc": {
            "style": "minimal",
            # Other fields missing
        },
    }

    # Should not crash when accessing categories
    categories = manager.get_all_categories()
    assert len(categories) == 2

    # Should handle missing subcategories gracefully
    subs = manager.get_subcategories_for_category("Minimal Category")
    assert subs == []

    # TOC config should have some defaults or handle missing fields
    toc = manager.get_toc_config()
    assert toc["style"] == "minimal"


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_get_all_categories,
        test_get_category_prefixes,
        test_get_category_by_name,
        test_get_category_by_id,
        test_get_all_subcategories,
        test_get_subcategories_for_category,
        test_validate_category_subcategory,
        test_get_categories_for_readme,
        test_get_toc_config,
        test_singleton_behavior,
        test_loading_from_file,
        test_robustness_with_missing_fields,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\nTests: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
