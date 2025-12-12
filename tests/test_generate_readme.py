#!/usr/bin/env python3
"""Tests for README generation functions."""

import os
import sys
import tempfile
import unittest
from datetime import datetime
from typing import Any

import pytest
import yaml

pytest.skip("New README structure", allow_module_level=True)

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

try:
    from generate_readme import (  # type: ignore
        format_resource_entry,
        generate_section_content,
        generate_toc_from_categories,
        generate_weekly_section,
        get_anchor_suffix_for_icon,
        load_announcements,
        parse_resource_date,
    )
except ImportError:
    from scripts.generate_readme import (
        format_resource_entry,
        generate_section_content,
        generate_toc_from_categories,
        generate_weekly_section,
        get_anchor_suffix_for_icon,
        load_announcements,
        parse_resource_date,
    )


class TestParseResourceDate(unittest.TestCase):
    """Test cases for the parse_resource_date function."""

    def test_parse_date_only_format(self) -> None:
        """Test parsing YYYY-MM-DD format."""
        result = parse_resource_date("2025-08-07")
        expected = datetime(2025, 8, 7)
        self.assertEqual(result, expected)

    def test_parse_date_with_timestamp_format(self) -> None:
        """Test parsing YYYY-MM-DD:HH-MM-SS format."""
        result = parse_resource_date("2025-08-07:18-26-57")
        expected = datetime(2025, 8, 7, 18, 26, 57)
        self.assertEqual(result, expected)

    def test_parse_with_whitespace(self) -> None:
        """Test parsing with leading/trailing whitespace."""
        result = parse_resource_date("  2025-08-07  ")
        expected = datetime(2025, 8, 7)
        self.assertEqual(result, expected)

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string returns None."""
        result = parse_resource_date("")
        self.assertIsNone(result)

    def test_parse_none(self) -> None:
        """Test parsing None returns None."""
        result = parse_resource_date(None)
        self.assertIsNone(result)

    def test_parse_invalid_format(self) -> None:
        """Test parsing invalid date format returns None."""
        invalid_formats = [
            "2025/08/07",  # Wrong separator
            "07-08-2025",  # Wrong order
            "2025-13-01",  # Invalid month
            "2025-08-32",  # Invalid day
            "not-a-date",  # Complete nonsense
            "2025-08-07 18:26:57",  # Space instead of colon
        ]

        for invalid_date in invalid_formats:
            with self.subTest(invalid_date=invalid_date):
                result = parse_resource_date(invalid_date)
                self.assertIsNone(result, f"Expected None for invalid date: {invalid_date}")

    def test_parse_various_timestamps(self) -> None:
        """Test parsing various valid timestamp formats."""
        test_cases = [
            ("2025-08-05:11-48-39", datetime(2025, 8, 5, 11, 48, 39)),
            ("2025-07-29:18-37-05", datetime(2025, 7, 29, 18, 37, 5)),
            ("2025-08-07:00-00-00", datetime(2025, 8, 7, 0, 0, 0)),
            ("2025-12-31:23-59-59", datetime(2025, 12, 31, 23, 59, 59)),
        ]

        for date_string, expected in test_cases:
            with self.subTest(date_string=date_string):
                result = parse_resource_date(date_string)
                self.assertEqual(result, expected, f"Failed to parse: {date_string}")

    def test_date_comparison(self) -> None:
        """Test that parsed dates can be compared correctly."""
        date1 = parse_resource_date("2025-08-07")
        date2 = parse_resource_date("2025-08-05")
        date3 = parse_resource_date("2025-08-07:18-26-57")

        if date1 and date2 and date3:
            self.assertTrue(date1 > date2)
            self.assertTrue(date3 > date1)  # Same date but with time
            self.assertFalse(date2 > date1)


class TestGetAnchorSuffix(unittest.TestCase):
    """Test cases for the get_anchor_suffix_for_icon function."""

    def test_no_icon(self) -> None:
        """Test empty icon returns empty string."""
        self.assertEqual(get_anchor_suffix_for_icon(""), "")
        self.assertEqual(get_anchor_suffix_for_icon(None), "")

    def test_simple_emoji(self) -> None:
        """Test simple emoji returns dash."""
        self.assertEqual(get_anchor_suffix_for_icon("🎯"), "-")
        self.assertEqual(get_anchor_suffix_for_icon("💡"), "-")
        self.assertEqual(get_anchor_suffix_for_icon("🔧"), "-")

    def test_emoji_with_variation_selector(self) -> None:
        """Test emoji with VS-16 returns URL-encoded suffix."""
        # Classical Building emoji with VS-16
        self.assertEqual(get_anchor_suffix_for_icon("🏛️"), "-%EF%B8%8F")


class TestGenerateTOC(unittest.TestCase):
    """Test cases for the generate_toc_from_categories function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Mock the category_manager import
        self.original_modules = {}
        if "category_utils" in sys.modules:
            self.original_modules["category_utils"] = sys.modules["category_utils"]

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        # Restore original modules
        for module_name, module in self.original_modules.items():
            sys.modules[module_name] = module

    def _mock_category_manager(self, categories: list[dict[str, Any]]) -> Any:
        """Create a mock category_manager module."""
        from unittest.mock import MagicMock

        mock_manager = MagicMock()
        mock_manager.get_categories_for_readme.return_value = categories

        mock_module = MagicMock()
        mock_module.category_manager = mock_manager

        sys.modules["category_utils"] = mock_module
        return mock_manager

    def test_empty_categories(self) -> None:
        """Test TOC generation with no categories."""
        self._mock_category_manager([])

        result = generate_toc_from_categories()

        # Check for main structure (open by default)
        self.assertIn("<details open>", result)
        self.assertIn("<summary>Table of Contents</summary>", result)
        self.assertIn("</details>", result)

    def test_simple_categories(self) -> None:
        """Test TOC generation with simple categories (no subcategories)."""
        categories = [
            {"name": "Getting Started", "icon": "🚀"},
            {"name": "Resources", "icon": "📚"},
            {"name": "Tools", "icon": "🔧"},
        ]
        self._mock_category_manager(categories)

        result = generate_toc_from_categories()

        # Check for main structure
        self.assertIn("<summary>Table of Contents</summary>", result)

        # Check for simple links
        self.assertIn("- [Getting Started](#getting-started-)", result)
        self.assertIn("- [Resources](#resources-)", result)
        self.assertIn("- [Tools](#tools-)", result)

    def test_categories_with_subcategories(self) -> None:
        """Test TOC generation with categories containing subcategories."""
        categories: list[dict[str, Any]] = [
            {
                "name": "Configuration",
                "icon": "⚙️",
                "subcategories": [
                    {"name": "Basic Setup"},
                    {"name": "Advanced Options"},
                ],
            },
            {"name": "Simple Category"},  # No subcategories
        ]
        self._mock_category_manager(categories)

        result = generate_toc_from_categories()

        # Check for collapsible category with subcategories (open by default)
        self.assertIn("- <details open>", result)
        # All category headers now have "-" suffix for back-to-top links
        self.assertIn('  <summary><a href="#configuration-">Configuration</a>', result)

        # Check for subcategories (also have "-" suffix)
        self.assertIn("  - [Basic Setup](#basic-setup-)", result)
        self.assertIn("  - [Advanced Options](#advanced-options-)", result)

        # Check for simple category (also has "-" suffix)
        self.assertIn("- [Simple Category](#simple-category-)", result)

    def test_special_characters_in_names(self) -> None:
        """Test TOC generation with special characters in category names."""
        categories = [
            {"name": "Tips & Tricks"},
            {"name": "CI/CD Tools"},
            {"name": "Node.js Resources"},
        ]
        self._mock_category_manager(categories)

        result = generate_toc_from_categories()

        # Check that special characters are properly handled in anchors (all have "-" suffix)
        self.assertIn("[Tips & Tricks](#tips--tricks-)", result)
        self.assertIn("[CI/CD Tools](#cicd-tools-)", result)
        self.assertIn("[Node.js Resources](#nodejs-resources-)", result)

    def test_mixed_categories(self) -> None:
        """Test TOC with a mix of simple and nested categories."""
        categories: list[dict[str, Any]] = [
            {"name": "Overview"},
            {
                "name": "Documentation",
                "icon": "📖",
                "subcategories": [
                    {"name": "API Reference"},
                    {"name": "Tutorials"},
                ],
            },
            {"name": "Community", "icon": "👥"},
            {
                "name": "Development",
                "subcategories": [{"name": "Contributing"}],
            },
        ]
        self._mock_category_manager(categories)

        result = generate_toc_from_categories()

        # Check structure
        lines = result.split("\n")

        # Should have main details wrapper (open by default)
        self.assertEqual(lines[0], "<details open>")
        self.assertEqual(lines[1], "<summary>Table of Contents</summary>")

        # Check for simple categories (all have "-" suffix)
        self.assertIn("- [Overview](#overview-)", result)
        self.assertIn("- [Community](#community-)", result)

        # Check for nested categories (all have "-" suffix)
        self.assertIn('  <summary><a href="#documentation-">Documentation</a>', result)
        self.assertIn("  - [API Reference](#api-reference-)", result)
        self.assertIn("  - [Tutorials](#tutorials-)", result)

        # Count details blocks (main + 2 categories with subcategories) - all open by default
        self.assertEqual(result.count("<details open>"), 3)
        self.assertEqual(result.count("</details>"), 3)


class TestLoadAnnouncements(unittest.TestCase):
    """Test cases for the load_announcements function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_empty_announcements(self) -> None:
        """Test loading empty announcements."""
        # Create empty YAML file
        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            f.write("")

        result = load_announcements(self.temp_dir)
        self.assertEqual(result, "")

    def test_simple_string_announcement(self) -> None:
        """Test announcements with simple string items."""
        announcements_data = [
            {
                "date": "2025-09-12",
                "title": "Test Announcements",
                "items": ["First announcement", "Second announcement"],
            }
        ]

        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(announcements_data, f)

        result = load_announcements(self.temp_dir)

        # Check for header and main structure
        self.assertIn("### Announcements [🔝](#awesome-claude-code)", result)
        self.assertIn("<details open>", result)
        self.assertIn("<summary>View Announcements</summary>", result)

        # Check for date group
        self.assertIn("- <details open>", result)
        self.assertIn("<summary>2025-09-12 - Test Announcements</summary>", result)

        # Check for items
        self.assertIn("  - First announcement", result)
        self.assertIn("  - Second announcement", result)

    def test_collapsible_announcement_items(self) -> None:
        """Test announcements with collapsible summary/text items."""
        announcements_data = [
            {
                "date": "2025-09-12",
                "title": "Feature Updates",
                "items": [
                    {
                        "summary": "New feature added",
                        "text": "This is a detailed description of the new feature.",
                    },
                    {
                        "summary": "Bug fix",
                        "text": "Fixed a critical bug in the system.",
                    },
                ],
            }
        ]

        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(announcements_data, f)

        result = load_announcements(self.temp_dir)

        # Check for header
        self.assertIn("### Announcements [🔝](#awesome-claude-code)", result)

        # Check for nested collapsible items
        self.assertIn("  - <details open>", result)
        self.assertIn("    <summary>New feature added</summary>", result)
        self.assertIn("    - This is a detailed description of the new feature.", result)
        self.assertIn("    <summary>Bug fix</summary>", result)
        self.assertIn("    - Fixed a critical bug in the system.", result)

    def test_multi_line_text_in_announcements(self) -> None:
        """Test announcements with multi-line text content."""
        announcements_data = [
            {
                "date": "2025-09-15",
                "title": "Important Notice",
                "items": [
                    {
                        "summary": "Multi-line announcement",
                        "text": (
                            "Line 1 of the announcement.\n\nLine 2 with a gap.\n\nLine 3 final."
                        ),
                    }
                ],
            }
        ]

        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(announcements_data, f)

        result = load_announcements(self.temp_dir)

        # Check for header
        self.assertIn("### Announcements [🔝](#awesome-claude-code)", result)

        # Check that multi-line text is properly formatted
        self.assertIn("    - Line 1 of the announcement.", result)
        self.assertIn("      Line 2 with a gap.", result)
        self.assertIn("      Line 3 final.", result)

    def test_mixed_announcement_types(self) -> None:
        """Test announcements with mixed item types."""
        announcements_data = [
            {
                "date": "2025-09-20",
                "items": [  # No title
                    "Simple string item",
                    {"summary": "Collapsible item", "text": "Detailed content here"},
                    {"summary": "Summary only item"},  # No text
                    {"text": "Text only item"},  # No summary
                ],
            }
        ]

        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(announcements_data, f)

        result = load_announcements(self.temp_dir)

        # Check for header
        self.assertIn("### Announcements [🔝](#awesome-claude-code)", result)

        # Check for date without title
        self.assertIn("<summary>2025-09-20</summary>", result)

        # Check for various item types
        self.assertIn("  - Simple string item", result)
        self.assertIn("    <summary>Collapsible item</summary>", result)
        self.assertIn("    - Detailed content here", result)
        self.assertIn("  - Summary only item", result)
        self.assertIn("  - Text only item", result)

    def test_multiple_date_groups(self) -> None:
        """Test announcements with multiple date groups."""
        announcements_data = [
            {
                "date": "2025-09-10",
                "title": "Week 1",
                "items": ["Announcement 1"],
            },
            {
                "date": "2025-09-17",
                "title": "Week 2",
                "items": ["Announcement 2"],
            },
        ]

        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(announcements_data, f)

        result = load_announcements(self.temp_dir)

        # Check for header
        self.assertIn("### Announcements [🔝](#awesome-claude-code)", result)

        # Check for both date groups
        self.assertIn("<summary>2025-09-10 - Week 1</summary>", result)
        self.assertIn("<summary>2025-09-17 - Week 2</summary>", result)

        # Verify proper nesting structure
        self.assertEqual(result.count("- <details open>"), 2)  # Two date groups
        self.assertEqual(result.count("</details>"), 3)  # Main + 2 date groups

    def test_markdown_in_announcements(self) -> None:
        """Test that markdown formatting is preserved in announcements."""
        announcements_data = [
            {
                "date": "2025-09-12",
                "title": "Markdown Test",
                "items": [
                    {
                        "summary": "Test with markdown",
                        "text": "This has **bold** text and [a link](https://example.com).",
                    }
                ],
            }
        ]

        yaml_path = os.path.join(self.temp_dir, "announcements.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(announcements_data, f)

        result = load_announcements(self.temp_dir)

        # Check for header
        self.assertIn("### Announcements [🔝](#awesome-claude-code)", result)

        # Check that markdown is preserved
        self.assertIn("**bold**", result)
        self.assertIn("[a link](https://example.com)", result)

    def test_nonexistent_directory(self) -> None:
        """Test loading from a directory with no announcement files."""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)

        result = load_announcements(empty_dir)
        self.assertEqual(result, "")


class TestGenerateSectionContent(unittest.TestCase):
    """Test cases for the generate_section_content function."""

    def test_simple_category_with_resources(self) -> None:
        """Test generating a simple category section with resources."""
        category = {"name": "Tools", "icon": "🔧"}
        csv_data = [
            {
                "Category": "Tools",
                "Sub-Category": "",
                "Display Name": "Tool 1",
                "Primary Link": "https://example.com/tool1",
                "Author Name": "Author 1",
                "Author Link": "",
                "Description": "A useful tool",
                "License": "MIT",
            }
        ]

        result = generate_section_content(category, csv_data)

        # Categories without subcategories should be wrapped in details
        self.assertIn("<details open>", result)
        self.assertIn("</details>", result)

        # Check for summary with h2
        self.assertIn(
            '<summary><h2>Tools 🔧 <a href="#awesome-claude-code">🔝</a></h2></summary>', result
        )

        # Check for resource content
        self.assertIn("[`Tool 1`](https://example.com/tool1)", result)
        self.assertIn("A useful tool", result)

    def test_category_with_description(self) -> None:
        """Test generating a category with a description."""
        category = {
            "name": "Resources",
            "icon": "📚",
            "description": "Helpful resources for developers",
        }
        csv_data: list[dict[str, Any]] = []

        result = generate_section_content(category, csv_data)

        # Categories without subcategories should be wrapped in details
        self.assertIn("<details open>", result)
        self.assertIn(
            '<summary><h2>Resources 📚 <a href="#awesome-claude-code">🔝</a></h2></summary>', result
        )
        self.assertIn("Helpful resources for developers", result)
        self.assertIn("</details>", result)

    def test_category_with_subcategories(self) -> None:
        """Test generating a category with subcategories."""
        category = {
            "name": "Documentation",
            "icon": "📖",
            "subcategories": [
                {"name": "Tutorials"},
                {"name": "API Reference"},
            ],
        }
        csv_data = [
            {
                "Category": "Documentation",
                "Sub-Category": "Tutorials",
                "Display Name": "Getting Started",
                "Primary Link": "https://example.com/tutorial",
                "Author Name": "",
                "Author Link": "",
                "Description": "",
                "License": "",
            },
            {
                "Category": "Documentation",
                "Sub-Category": "API Reference",
                "Display Name": "API Docs",
                "Primary Link": "https://example.com/api",
                "Author Name": "",
                "Author Link": "",
                "Description": "",
                "License": "",
            },
        ]

        result = generate_section_content(category, csv_data)

        # Categories WITH subcategories should NOT be wrapped in details at the main level
        self.assertIn("## Documentation 📖 [🔝](#awesome-claude-code)", result)
        self.assertNotIn("<summary><h2>Documentation 📖", result)

        # Check for subcategory details wrappers
        self.assertEqual(result.count("<details open>"), 2)  # Only 2 subcategories
        self.assertIn(
            '<summary><h3>Tutorials <a href="#awesome-claude-code">🔝</a></h3></summary>', result
        )
        self.assertIn(
            '<summary><h3>API Reference <a href="#awesome-claude-code">🔝</a></h3></summary>',
            result,
        )

        # Check for resources in subcategories
        self.assertIn("[`Getting Started`](https://example.com/tutorial)", result)
        self.assertIn("[`API Docs`](https://example.com/api)", result)

        # Check closing tags
        self.assertEqual(result.count("</details>"), 2)

    def test_category_with_main_and_sub_resources(self) -> None:
        """Test a category with resources at both main and sub levels."""
        category = {
            "name": "Mixed",
            "subcategories": [{"name": "Subcategory"}],
        }
        csv_data = [
            {
                "Category": "Mixed",
                "Sub-Category": "",
                "Display Name": "Main Resource",
                "Primary Link": "https://example.com/main",
                "Author Name": "",
                "Author Link": "",
                "Description": "",
                "License": "",
            },
            {
                "Category": "Mixed",
                "Sub-Category": "Subcategory",
                "Display Name": "Sub Resource",
                "Primary Link": "https://example.com/sub",
                "Author Name": "",
                "Author Link": "",
                "Description": "",
                "License": "",
            },
        ]

        result = generate_section_content(category, csv_data)

        # Check for main resource before subcategory
        main_idx = result.index("Main Resource")
        sub_idx = result.index("Sub Resource")
        self.assertTrue(main_idx < sub_idx, "Main resource should come before subcategory")

        # Categories WITH subcategories should have regular header
        self.assertIn("## Mixed", result)
        # Only subcategory should be in details
        self.assertEqual(result.count("<details open>"), 1)  # Only 1 subcategory

    def test_category_without_icon(self) -> None:
        """Test generating a category without an icon."""
        category = {"name": "Plain Category"}
        csv_data: list[dict[str, Any]] = []

        result = generate_section_content(category, csv_data)

        # Categories without subcategories should be wrapped in details
        self.assertIn("<details open>", result)
        self.assertIn(
            '<summary><h2>Plain Category <a href="#awesome-claude-code">🔝</a></h2></summary>',
            result,
        )
        self.assertIn("</details>", result)

    def test_empty_subcategory_not_rendered(self) -> None:
        """Test that subcategories without resources are not rendered."""
        category = {
            "name": "Test",
            "subcategories": [
                {"name": "Empty Sub"},
                {"name": "Has Resources"},
            ],
        }
        csv_data = [
            {
                "Category": "Test",
                "Sub-Category": "Has Resources",
                "Display Name": "Resource",
                "Primary Link": "https://example.com",
                "Author Name": "",
                "Author Link": "",
                "Description": "",
                "License": "",
            }
        ]

        result = generate_section_content(category, csv_data)

        # Empty subcategory should not be present
        self.assertNotIn("Empty Sub", result)

        # Subcategory with resources should be present
        self.assertIn("Has Resources", result)

        # Categories WITH subcategories have regular headers
        self.assertIn("## Test", result)
        # Should only have 1 details block (the subcategory with resources)
        self.assertEqual(result.count("<details open>"), 1)


class TestBackToTopButtons(unittest.TestCase):
    """Test cases for back-to-top button functionality."""

    def test_weekly_section_has_back_to_top(self) -> None:
        """Test that the weekly section header has a back-to-top button."""
        csv_data: list[dict[str, str]] = []
        result = generate_weekly_section(csv_data)

        # Check that the header contains the back-to-top link
        self.assertIn("## This Week's Additions ✨ [🔝](#awesome-claude-code)", result)

    def test_category_without_subcategories_has_html_anchor(self) -> None:
        """Test categories without subcategories have HTML anchor in summary."""
        category = {"name": "Test Category", "icon": "🧪", "description": "Test description"}
        csv_data: list[dict[str, str]] = []

        result = generate_section_content(category, csv_data)

        # Should use HTML <a> tag inside summary
        self.assertIn(
            '<summary><h2>Test Category 🧪 <a href="#awesome-claude-code">🔝</a></h2></summary>',
            result,
        )
        # Should NOT have markdown link
        self.assertNotIn("[🔝](#awesome-claude-code)</h2></summary>", result)

    def test_category_without_icon_has_back_to_top(self) -> None:
        """Test categories without icons still get back-to-top buttons."""
        category = {"name": "No Icon Category", "description": "Test description"}
        csv_data: list[dict[str, str]] = []

        result = generate_section_content(category, csv_data)

        # Should have HTML anchor without icon
        self.assertIn(
            '<summary><h2>No Icon Category <a href="#awesome-claude-code">🔝</a></h2></summary>',
            result,
        )

    def test_category_with_subcategories_has_markdown_link(self) -> None:
        """Test categories with subcategories have markdown link (not in summary)."""
        category = {
            "name": "Main Category",
            "icon": "📁",
            "subcategories": [{"name": "Sub One"}, {"name": "Sub Two"}],
        }
        csv_data: list[dict[str, str]] = []

        result = generate_section_content(category, csv_data)

        # Main category should have markdown link (it's a regular header, not in summary)
        self.assertIn("## Main Category 📁 [🔝](#awesome-claude-code)", result)
        # Should NOT have HTML anchor for main category
        self.assertNotIn("## Main Category 📁 <a href=", result)

    def test_subcategory_has_html_anchor(self) -> None:
        """Test subcategories have HTML anchor in their summary tags."""
        category = {"name": "Main", "icon": "📁", "subcategories": [{"name": "Subcategory Test"}]}
        csv_data = [
            {
                "Category": "Main",
                "Sub-Category": "Subcategory Test",
                "Display Name": "Test Resource",
                "Primary Link": "https://example.com",
                "Active": "TRUE",
            }
        ]

        result = generate_section_content(category, csv_data)

        # Subcategory should use HTML anchor inside summary
        self.assertIn(
            '<summary><h3>Subcategory Test <a href="#awesome-claude-code">🔝</a></h3></summary>',
            result,
        )
        # Should NOT have markdown link in subcategory summary
        self.assertNotIn("[🔝](#awesome-claude-code)</h3></summary>", result)

    def test_multiple_subcategories_all_have_anchors(self) -> None:
        """Test that all subcategories get back-to-top anchors."""
        category = {
            "name": "Parent",
            "subcategories": [{"name": "First Sub"}, {"name": "Second Sub"}, {"name": "Third Sub"}],
        }
        csv_data = [
            {
                "Category": "Parent",
                "Sub-Category": sub["name"],
                "Display Name": f"Resource for {sub['name']}",
                "Primary Link": "https://example.com",
                "Active": "TRUE",
            }
            for sub in category["subcategories"]
        ]

        result = generate_section_content(category, csv_data)

        # All subcategories should have HTML anchors
        self.assertIn(
            '<summary><h3>First Sub <a href="#awesome-claude-code">🔝</a></h3></summary>', result
        )
        self.assertIn(
            '<summary><h3>Second Sub <a href="#awesome-claude-code">🔝</a></h3></summary>', result
        )
        self.assertIn(
            '<summary><h3>Third Sub <a href="#awesome-claude-code">🔝</a></h3></summary>', result
        )

        # Count that we have exactly 3 back-to-top anchors in summaries
        anchor_count = result.count('<a href="#awesome-claude-code">🔝</a></h3></summary>')
        self.assertEqual(anchor_count, 3)

    def test_back_to_top_preserves_existing_structure(self) -> None:
        """Test that adding back-to-top doesn't break existing structure."""
        category = {
            "name": "Complete Test",
            "icon": "✅",
            "description": "A complete category",
            "subcategories": [{"name": "Complete Sub"}],
        }
        csv_data = [
            {
                "Category": "Complete Test",
                "Sub-Category": "",
                "Display Name": "Main Resource",
                "Primary Link": "https://example.com/main",
                "Active": "TRUE",
                "Description": "Main description",
            },
            {
                "Category": "Complete Test",
                "Sub-Category": "Complete Sub",
                "Display Name": "Sub Resource",
                "Primary Link": "https://example.com/sub",
                "Active": "TRUE",
                "Description": "Sub description",
            },
        ]

        result = generate_section_content(category, csv_data)

        # Check structure is preserved
        self.assertIn("## Complete Test ✅ [🔝](#awesome-claude-code)", result)
        self.assertIn("A complete category", result)
        self.assertIn("[`Main Resource`](https://example.com/main)", result)
        self.assertIn("Main description", result)
        self.assertIn("<details open>", result)
        self.assertIn(
            '<summary><h3>Complete Sub <a href="#awesome-claude-code">🔝</a></h3></summary>', result
        )
        self.assertIn("[`Sub Resource`](https://example.com/sub)", result)
        self.assertIn("Sub description", result)
        self.assertIn("</details>", result)


class TestFormatResourceEntryGitHubStats(unittest.TestCase):
    """Test GitHub stats disclosure functionality in format_resource_entry."""

    def test_github_resource_with_stats(self):
        """Test that GitHub resources get stats disclosure."""
        row = {
            "Display Name": "Test Resource",
            "Primary Link": "https://github.com/owner/repo",
            "Description": "Test description",
            "Author Name": "Test Author",
            "Author Link": "https://github.com/testauthor",
            "License": "MIT",
        }

        result = format_resource_entry(row)

        # Check for disclosure element
        self.assertIn("<details>", result)
        self.assertIn("📊 GitHub Stats", result)
        self.assertIn(
            "https://github-readme-stats-plus-theta.vercel.app/api/pin/?repo=repo&username=owner&all_stats=true&stats_only=true&hide_border=true&bg_color=00000000&icon_color=FF0000&text_color=FF0000",
            result,
        )

    def test_non_github_resource_no_stats(self):
        """Test that non-GitHub resources don't get stats disclosure."""
        row = {
            "Display Name": "Test Resource",
            "Primary Link": "https://example.com/resource",
            "Description": "Test description",
            "Author Name": "Test Author",
            "Author Link": "",
            "License": "",
        }

        result = format_resource_entry(row)

        # Should not have disclosure element
        self.assertNotIn("<details>", result)
        self.assertNotIn("GitHub Stats", result)

    def test_github_blob_url_with_stats(self):
        """Test GitHub blob URLs also get stats."""
        row = {
            "Display Name": "Test Resource",
            "Primary Link": "https://github.com/owner/repo/blob/main/.claude/commands",
            "Description": "Test description",
            "Author Name": "",
            "Author Link": "",
            "License": "",
        }

        result = format_resource_entry(row)

        # Check for disclosure element with correct owner/repo
        self.assertIn("<details>", result)
        self.assertIn("repo=repo&username=owner", result)

    def test_github_tree_url_with_stats(self):
        """Test GitHub tree URLs also get stats."""
        row = {
            "Display Name": "Test Resource",
            "Primary Link": "https://github.com/owner/repo/tree/main/.claude/commands",
            "Description": "Test description",
            "Author Name": "",
            "Author Link": "",
            "License": "",
        }

        result = format_resource_entry(row)

        # Check for disclosure element with correct owner/repo
        self.assertIn("<details>", result)
        self.assertIn("repo=repo&username=owner", result)

    def test_empty_primary_link_no_stats(self):
        """Test that resources without primary link don't get stats."""
        row = {
            "Display Name": "Test Resource",
            "Primary Link": "",
            "Description": "Test description",
            "Author Name": "",
            "Author Link": "",
            "License": "",
        }

        result = format_resource_entry(row)

        # Should not have disclosure element
        self.assertNotIn("<details>", result)
        self.assertNotIn("GitHub Stats", result)


if __name__ == "__main__":
    unittest.main()
