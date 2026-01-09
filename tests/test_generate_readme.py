#!/usr/bin/env python3
"""Tests for README generation functions."""

import os
import sys
from datetime import datetime
from typing import Any

import pytest
import yaml

# Add repo root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.readme.helpers.readme_utils import (  # noqa: E402
    get_anchor_suffix_for_icon,
    parse_resource_date,
)
from scripts.readme.markup.minimal import (  # noqa: E402
    format_resource_entry,
    generate_section_content,
    generate_toc,
    generate_weekly_section,
)
from scripts.readme.markup.shared import load_announcements  # noqa: E402


def write_yaml(path: os.PathLike[str], data: Any) -> None:
    """Write YAML data to a file."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


class TestParseResourceDate:
    """Test cases for the parse_resource_date function."""

    def test_parse_date_only_format(self) -> None:
        """Test parsing YYYY-MM-DD format."""
        result = parse_resource_date("2025-08-07")
        expected = datetime(2025, 8, 7)
        assert result == expected

    def test_parse_date_with_timestamp_format(self) -> None:
        """Test parsing YYYY-MM-DD:HH-MM-SS format."""
        result = parse_resource_date("2025-08-07:18-26-57")
        expected = datetime(2025, 8, 7, 18, 26, 57)
        assert result == expected

    def test_parse_with_whitespace(self) -> None:
        """Test parsing with leading/trailing whitespace."""
        result = parse_resource_date("  2025-08-07  ")
        expected = datetime(2025, 8, 7)
        assert result == expected

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string returns None."""
        assert parse_resource_date("") is None

    def test_parse_none(self) -> None:
        """Test parsing None returns None."""
        assert parse_resource_date(None) is None

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "2025/08/07",  # Wrong separator
            "07-08-2025",  # Wrong order
            "2025-13-01",  # Invalid month
            "2025-08-32",  # Invalid day
            "not-a-date",  # Complete nonsense
            "2025-08-07 18:26:57",  # Space instead of colon
        ],
    )
    def test_parse_invalid_format(self, invalid_date: str) -> None:
        """Test parsing invalid date format returns None."""
        assert parse_resource_date(invalid_date) is None

    @pytest.mark.parametrize(
        "date_string, expected",
        [
            ("2025-08-05:11-48-39", datetime(2025, 8, 5, 11, 48, 39)),
            ("2025-07-29:18-37-05", datetime(2025, 7, 29, 18, 37, 5)),
            ("2025-08-07:00-00-00", datetime(2025, 8, 7, 0, 0, 0)),
            ("2025-12-31:23-59-59", datetime(2025, 12, 31, 23, 59, 59)),
        ],
    )
    def test_parse_various_timestamps(self, date_string: str, expected: datetime) -> None:
        """Test parsing various valid timestamp formats."""
        assert parse_resource_date(date_string) == expected

    def test_date_comparison(self) -> None:
        """Test that parsed dates can be compared correctly."""
        date1 = parse_resource_date("2025-08-07")
        date2 = parse_resource_date("2025-08-05")
        date3 = parse_resource_date("2025-08-07:18-26-57")

        assert date1 is not None and date2 is not None and date3 is not None
        assert date1 > date2
        assert date3 > date1  # Same date but with time
        assert not date2 > date1


class TestGetAnchorSuffix:
    """Test cases for the get_anchor_suffix_for_icon function."""

    @pytest.mark.parametrize("icon", ["", None])
    def test_no_icon(self, icon: str | None) -> None:
        """Test empty icon returns empty string."""
        assert get_anchor_suffix_for_icon(icon) == ""

    @pytest.mark.parametrize("icon", ["🎯", "💡", "🔧"])
    def test_simple_emoji(self, icon: str) -> None:
        """Test simple emoji returns dash."""
        assert get_anchor_suffix_for_icon(icon) == "-"

    def test_emoji_with_variation_selector(self) -> None:
        """Test emoji with VS-16 returns URL-encoded suffix."""
        # Classical Building emoji with VS-16
        assert get_anchor_suffix_for_icon("🏛️") == "-%EF%B8%8F"


class TestGenerateTOC:
    """Test cases for the generate_toc function."""

    def test_empty_categories(self) -> None:
        """Test TOC generation with no categories."""
        result = generate_toc([], [])

        # Check for main structure (open by default)
        assert "## Contents [🔝](#awesome-claude-code)" in result
        assert "<details open>" in result
        assert "<summary>Table of Contents</summary>" in result
        assert "</details>" in result

    def test_simple_categories(self) -> None:
        """Test TOC generation with simple categories (no subcategories)."""
        categories = [
            {"name": "Getting Started", "icon": "🚀"},
            {"name": "Resources", "icon": "📚"},
            {"name": "Tools", "icon": "🔧"},
        ]
        result = generate_toc(categories, [])

        # Check for main structure
        assert "<summary>Table of Contents</summary>" in result

        # Check for simple links (CLASSIC style adds extra dash for 🔝 back-to-top)
        assert "- [Getting Started](#getting-started--)" in result
        assert "- [Resources](#resources--)" in result
        assert "- [Tools](#tools--)" in result

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
        csv_data = [
            {"Category": "Configuration", "Sub-Category": "Basic Setup"},
            {"Category": "Configuration", "Sub-Category": "Advanced Options"},
        ]
        result = generate_toc(categories, csv_data)

        # Check for collapsible category with subcategories (open by default)
        assert "- <details open>" in result
        # CLASSIC style: icon suffix + extra dash for 🔝 back-to-top
        assert '  <summary><a href="#configuration-%EF%B8%8F-">Configuration</a>' in result

        # Check for subcategories (CLASSIC adds trailing dash for 🔝)
        assert "  - [Basic Setup](#basic-setup-)" in result
        assert "  - [Advanced Options](#advanced-options-)" in result

        # Check for simple category (CLASSIC adds extra dash for 🔝)
        assert "- [Simple Category](#simple-category-)" in result

    def test_special_characters_in_names(self) -> None:
        """Test TOC generation with special characters in category names."""
        categories = [
            {"name": "Tips & Tricks"},
            {"name": "CI/CD Tools"},
            {"name": "Node.js Resources"},
        ]
        result = generate_toc(categories, [])

        # Check that special characters are properly handled in anchors
        # CLASSIC style adds extra dash for 🔝 back-to-top
        assert "[Tips & Tricks](#tips--tricks-)" in result
        assert "[CI/CD Tools](#cicd-tools-)" in result
        assert "[Node.js Resources](#nodejs-resources-)" in result

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
        csv_data = [
            {"Category": "Documentation", "Sub-Category": "API Reference"},
            {"Category": "Documentation", "Sub-Category": "Tutorials"},
            {"Category": "Development", "Sub-Category": "Contributing"},
        ]
        result = generate_toc(categories, csv_data)

        lines = result.split("\n")

        # Should have main details wrapper (open by default)
        assert lines[0] == "## Contents [🔝](#awesome-claude-code)"
        assert lines[2] == "<details open>"
        assert lines[3] == "<summary>Table of Contents</summary>"

        # Check for simple categories (CLASSIC adds extra dash for 🔝)
        assert "- [Overview](#overview-)" in result
        assert "- [Community](#community--)" in result

        # Check for nested categories (CLASSIC: icon dash + 🔝 dash)
        assert '  <summary><a href="#documentation--">Documentation</a>' in result
        assert "  - [API Reference](#api-reference-)" in result
        assert "  - [Tutorials](#tutorials-)" in result

        # Count details blocks (main + 2 categories with subcategories) - all open by default
        assert result.count("<details open>") == 3
        assert result.count("</details>") == 3


class TestLoadAnnouncements:
    """Test cases for the load_announcements function."""

    def test_empty_announcements(self, tmp_path) -> None:
        """Test loading empty announcements."""
        yaml_path = tmp_path / "announcements.yaml"
        yaml_path.write_text("", encoding="utf-8")

        result = load_announcements(str(tmp_path))
        assert result == ""

    def test_simple_string_announcement(self, tmp_path) -> None:
        """Test announcements with simple string items."""
        announcements_data = [
            {
                "date": "2025-09-12",
                "title": "Test Announcements",
                "items": ["First announcement", "Second announcement"],
            }
        ]

        yaml_path = tmp_path / "announcements.yaml"
        write_yaml(yaml_path, announcements_data)

        result = load_announcements(str(tmp_path))

        # Check for header and main structure
        assert "### Announcements [🔝](#awesome-claude-code)" in result
        assert "<details open>" in result
        assert "<summary>View Announcements</summary>" in result

        # Check for date group
        assert "- <details open>" in result
        assert "<summary>2025-09-12 - Test Announcements</summary>" in result

        # Check for items
        assert "  - First announcement" in result
        assert "  - Second announcement" in result

    def test_collapsible_announcement_items(self, tmp_path) -> None:
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

        yaml_path = tmp_path / "announcements.yaml"
        write_yaml(yaml_path, announcements_data)

        result = load_announcements(str(tmp_path))

        # Check for header
        assert "### Announcements [🔝](#awesome-claude-code)" in result

        # Check for nested collapsible items
        assert "  - <details open>" in result
        assert "    <summary>New feature added</summary>" in result
        assert "    - This is a detailed description of the new feature." in result
        assert "    <summary>Bug fix</summary>" in result
        assert "    - Fixed a critical bug in the system." in result

    def test_multi_line_text_in_announcements(self, tmp_path) -> None:
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

        yaml_path = tmp_path / "announcements.yaml"
        write_yaml(yaml_path, announcements_data)

        result = load_announcements(str(tmp_path))

        # Check for header
        assert "### Announcements [🔝](#awesome-claude-code)" in result

        # Check that multi-line text is properly formatted
        assert "    - Line 1 of the announcement." in result
        assert "      Line 2 with a gap." in result
        assert "      Line 3 final." in result

    def test_mixed_announcement_types(self, tmp_path) -> None:
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

        yaml_path = tmp_path / "announcements.yaml"
        write_yaml(yaml_path, announcements_data)

        result = load_announcements(str(tmp_path))

        # Check for header
        assert "### Announcements [🔝](#awesome-claude-code)" in result

        # Check for date without title
        assert "<summary>2025-09-20</summary>" in result

        # Check for various item types
        assert "  - Simple string item" in result
        assert "    <summary>Collapsible item</summary>" in result
        assert "    - Detailed content here" in result
        assert "  - Summary only item" in result
        assert "  - Text only item" in result

    def test_multiple_date_groups(self, tmp_path) -> None:
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

        yaml_path = tmp_path / "announcements.yaml"
        write_yaml(yaml_path, announcements_data)

        result = load_announcements(str(tmp_path))

        # Check for header
        assert "### Announcements [🔝](#awesome-claude-code)" in result

        # Check for both date groups
        assert "<summary>2025-09-10 - Week 1</summary>" in result
        assert "<summary>2025-09-17 - Week 2</summary>" in result

        # Verify proper nesting structure
        assert result.count("- <details open>") == 2  # Two date groups
        assert result.count("</details>") == 3  # Main + 2 date groups

    def test_markdown_in_announcements(self, tmp_path) -> None:
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

        yaml_path = tmp_path / "announcements.yaml"
        write_yaml(yaml_path, announcements_data)

        result = load_announcements(str(tmp_path))

        # Check for header
        assert "### Announcements [🔝](#awesome-claude-code)" in result

        # Check that markdown is preserved
        assert "**bold**" in result
        assert "[a link](https://example.com)" in result

    def test_nonexistent_directory(self, tmp_path) -> None:
        """Test loading from a directory with no announcement files."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = load_announcements(str(empty_dir))
        assert result == ""


class TestGenerateSectionContent:
    """Test cases for the generate_section_content function."""

    def test_simple_category_with_resources(self) -> None:
        """Test generating a simple category section with resources."""
        category = {
            "name": "Tools",
            "icon": "🔧",
            "subcategories": [{"name": "General"}],
        }
        csv_data = [
            {
                "Category": "Tools",
                "Sub-Category": "General",
                "Display Name": "Tool 1",
                "Primary Link": "https://example.com/tool1",
                "Author Name": "Author 1",
                "Author Link": "",
                "Description": "A useful tool",
                "License": "MIT",
            }
        ]

        result = generate_section_content(category, csv_data)

        # Header with back-to-top link
        assert "## Tools 🔧 [🔝](#awesome-claude-code)" in result
        assert "<details open>" in result

        # Check for resource content
        assert "[`Tool 1`](https://example.com/tool1)" in result
        assert "A useful tool" in result

    def test_category_with_description(self) -> None:
        """Test generating a category with a description."""
        category = {
            "name": "Resources",
            "icon": "📚",
            "description": "Helpful resources for developers",
        }
        csv_data: list[dict[str, Any]] = []

        result = generate_section_content(category, csv_data)

        assert "## Resources 📚 [🔝](#awesome-claude-code)" in result
        assert "> Helpful resources for developers" in result

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
        assert "## Documentation 📖 [🔝](#awesome-claude-code)" in result
        assert "<summary><h2>Documentation 📖" not in result

        # Check for subcategory details wrappers
        assert result.count("<details open>") == 2  # Only 2 subcategories
        assert (
            '<summary><h3>Tutorials <a href="#awesome-claude-code">🔝</a></h3></summary>' in result
        )
        assert (
            '<summary><h3>API Reference <a href="#awesome-claude-code">🔝</a></h3></summary>'
            in result
        )

        # Check for resources in subcategories
        assert "[`Getting Started`](https://example.com/tutorial)" in result
        assert "[`API Docs`](https://example.com/api)" in result

        # Check closing tags
        assert result.count("</details>") == 2

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

        # Main-level resources are not rendered in minimal mode
        assert "Main Resource" not in result
        assert "Sub Resource" in result

        assert "## Mixed [🔝](#awesome-claude-code)" in result
        assert result.count("<details open>") == 1

    def test_category_without_icon(self) -> None:
        """Test generating a category without an icon."""
        category = {"name": "Plain Category"}
        csv_data: list[dict[str, Any]] = []

        result = generate_section_content(category, csv_data)

        assert "## Plain Category [🔝](#awesome-claude-code)" in result

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
        assert "Empty Sub" not in result

        # Subcategory with resources should be present
        assert "Has Resources" in result

        # Categories WITH subcategories have regular headers
        assert "## Test [🔝](#awesome-claude-code)" in result
        # Should only have 1 details block (the subcategory with resources)
        assert result.count("<details open>") == 1


class TestBackToTopButtons:
    """Test cases for back-to-top button functionality."""

    def test_weekly_section_has_back_to_top(self) -> None:
        """Test that the weekly section header has a back-to-top button."""
        csv_data: list[dict[str, str]] = []
        result = generate_weekly_section(csv_data)

        # Check that the header contains the back-to-top link
        assert "## Latest Additions ✨ [🔝](#awesome-claude-code)" in result

    def test_category_without_subcategories_has_html_anchor(self) -> None:
        """Test categories without subcategories render markdown back-to-top links."""
        category = {
            "name": "Test Category",
            "icon": "🧪",
            "description": "Test description",
        }
        csv_data: list[dict[str, str]] = []

        result = generate_section_content(category, csv_data)

        assert "## Test Category 🧪 [🔝](#awesome-claude-code)" in result
        assert "<summary><h2>" not in result

    def test_category_without_icon_has_back_to_top(self) -> None:
        """Test categories without icons still get back-to-top buttons."""
        category = {"name": "No Icon Category", "description": "Test description"}
        csv_data: list[dict[str, str]] = []

        result = generate_section_content(category, csv_data)

        assert "## No Icon Category [🔝](#awesome-claude-code)" in result

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
        assert "## Main Category 📁 [🔝](#awesome-claude-code)" in result
        # Should NOT have HTML anchor for main category
        assert "## Main Category 📁 <a href=" not in result

    def test_subcategory_has_html_anchor(self) -> None:
        """Test subcategories have HTML anchor in their summary tags."""
        category = {
            "name": "Main",
            "icon": "📁",
            "subcategories": [{"name": "Subcategory Test"}],
        }
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
        assert (
            '<summary><h3>Subcategory Test <a href="#awesome-claude-code">🔝</a></h3></summary>'
            in result
        )
        # Should NOT have markdown link in subcategory summary
        assert "[🔝](#awesome-claude-code)</h3></summary>" not in result

    def test_multiple_subcategories_all_have_anchors(self) -> None:
        """Test that all subcategories get back-to-top anchors."""
        category: dict[str, Any] = {
            "name": "Parent",
            "subcategories": [
                {"name": "First Sub"},
                {"name": "Second Sub"},
                {"name": "Third Sub"},
            ],
        }
        subcategories = category.get("subcategories", [])
        csv_data = [
            {
                "Category": "Parent",
                "Sub-Category": sub["name"],
                "Display Name": f"Resource for {sub['name']}",
                "Primary Link": "https://example.com",
                "Active": "TRUE",
            }
            for sub in subcategories
            if isinstance(sub, dict)
        ]

        result = generate_section_content(category, csv_data)

        # All subcategories should have HTML anchors
        assert (
            '<summary><h3>First Sub <a href="#awesome-claude-code">🔝</a></h3></summary>' in result
        )
        assert (
            '<summary><h3>Second Sub <a href="#awesome-claude-code">🔝</a></h3></summary>' in result
        )
        assert (
            '<summary><h3>Third Sub <a href="#awesome-claude-code">🔝</a></h3></summary>' in result
        )

        # Count that we have exactly 3 back-to-top anchors in summaries
        anchor_count = result.count('<a href="#awesome-claude-code">🔝</a></h3></summary>')
        assert anchor_count == 3

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

        assert "## Complete Test ✅ [🔝](#awesome-claude-code)" in result
        assert "> A complete category" in result
        assert "<details open>" in result
        assert (
            '<summary><h3>Complete Sub <a href="#awesome-claude-code">🔝</a></h3></summary>'
            in result
        )
        assert "[`Sub Resource`](https://example.com/sub)" in result
        assert "Sub description" in result
        assert "</details>" in result


class TestFormatResourceEntryGitHubStats:
    """Test GitHub stats disclosure functionality in format_resource_entry."""

    def test_github_resource_with_stats(self) -> None:
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
        assert "<details>" in result
        assert "📊 GitHub Stats" in result
        assert (
            "https://github-readme-stats-fork-orpin.vercel.app"
            "/api/pin/?repo=repo&username=owner&all_stats=true&stats_only=true" in result
        )

    def test_non_github_resource_no_stats(self) -> None:
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
        assert "<details>" not in result
        assert "GitHub Stats" not in result

    def test_github_blob_url_with_stats(self) -> None:
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
        assert "<details>" in result
        assert "repo=repo&username=owner" in result

    def test_github_tree_url_with_stats(self) -> None:
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
        assert "<details>" in result
        assert "repo=repo&username=owner" in result

    def test_empty_primary_link_no_stats(self) -> None:
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
        assert "<details>" not in result
        assert "GitHub Stats" not in result
