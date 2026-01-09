#!/usr/bin/env python3
"""
Unit tests for sort_resources.py script.

Tests cover:
- Sorting by category order
- Sorting by sub-category
- Sorting by display name
- Edge cases (empty CSV, missing fields)
- Category summary generation
"""

import csv
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.resources.sort_resources import sort_resources  # noqa


@pytest.fixture
def temp_csv() -> Generator[Path, None, None]:
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def sample_csv_data() -> list[dict[str, str]]:
    """Sample CSV data for testing."""
    return [
        {
            "ID": "cmd-001",
            "Display Name": "Zebra Command",
            "Category": "Slash-Commands",
            "Sub-Category": "Version Control & Git",
            "Primary Link": "https://example.com/zebra",
            "Author Name": "Author Z",
            "Author Link": "https://github.com/authorz",
            "Description": "Last alphabetically",
        },
        {
            "ID": "tool-001",
            "Display Name": "Alpha Tool",
            "Category": "Tooling",
            "Sub-Category": "",
            "Primary Link": "https://example.com/alpha",
            "Author Name": "Author A",
            "Author Link": "https://github.com/authora",
            "Description": "First alphabetically",
        },
        {
            "ID": "cmd-002",
            "Display Name": "Beta Command",
            "Category": "Slash-Commands",
            "Sub-Category": "Code Analysis & Testing",
            "Primary Link": "https://example.com/beta",
            "Author Name": "Author B",
            "Author Link": "https://github.com/authorb",
            "Description": "Second alphabetically",
        },
        {
            "ID": "wf-001",
            "Display Name": "Charlie Workflow",
            "Category": "Workflows & Knowledge Guides",
            "Sub-Category": "",
            "Primary Link": "https://example.com/charlie",
            "Author Name": "Author C",
            "Author Link": "https://github.com/authorc",
            "Description": "Third alphabetically",
        },
        {
            "ID": "cmd-003",
            "Display Name": "Alpha Command",
            "Category": "Slash-Commands",
            "Sub-Category": "Code Analysis & Testing",
            "Primary Link": "https://example.com/alphacmd",
            "Author Name": "Author AC",
            "Author Link": "https://github.com/authorac",
            "Description": "Should sort before Beta in same subcategory",
        },
    ]


def write_csv(path: Path, data: list[dict[str, str]]) -> None:
    """Helper to write CSV data to a file."""
    if not data:
        path.write_text("")
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Helper to read CSV data from a file."""
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def set_category_order(monkeypatch: pytest.MonkeyPatch, categories: list[dict[str, Any]]) -> None:
    """Override category order for sorting tests."""
    monkeypatch.setattr(
        "scripts.categories.category_utils.category_manager.get_categories_for_readme",
        lambda: categories,
    )


def set_category_order_error(
    monkeypatch: pytest.MonkeyPatch, message: str = "Category manager error"
) -> None:
    """Force category manager to raise an error."""

    def _raise() -> None:
        raise Exception(message)

    monkeypatch.setattr(
        "scripts.categories.category_utils.category_manager.get_categories_for_readme",
        _raise,
    )


class TestSortResources:
    """Test cases for sort_resources function."""

    def test_sort_by_category_order(
        self,
        temp_csv: Path,
        sample_csv_data: list[dict[str, str]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that resources are sorted according to category order from category_utils."""
        # Mock category manager to provide a specific order
        mock_categories = [
            {"name": "Workflows & Knowledge Guides"},
            {"name": "Tooling"},
            {"name": "Slash-Commands"},
        ]

        set_category_order(monkeypatch, mock_categories)
        write_csv(temp_csv, sample_csv_data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)
        categories = [row["Category"] for row in sorted_data]

        # Check that categories appear in the specified order
        assert categories[0] == "Workflows & Knowledge Guides"
        assert categories[1] == "Tooling"
        assert categories[2:] == ["Slash-Commands"] * 3

    def test_sort_by_subcategory(
        self,
        temp_csv: Path,
        sample_csv_data: list[dict[str, str]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that resources within a category are sorted by sub-category."""
        set_category_order(monkeypatch, [{"name": "Slash-Commands"}])
        # Filter to just Slash-Commands for this test
        slash_commands = [d for d in sample_csv_data if d["Category"] == "Slash-Commands"]
        write_csv(temp_csv, slash_commands)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)
        subcategories = [row["Sub-Category"] for row in sorted_data]

        # "Code Analysis & Testing" should come before "Version Control & Git"
        assert subcategories[0] == "Code Analysis & Testing"
        assert subcategories[1] == "Code Analysis & Testing"
        assert subcategories[2] == "Version Control & Git"

    def test_sort_by_display_name(self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that resources within same category/subcategory are sorted by display name."""
        data = [
            {
                "ID": "cmd-003",
                "Display Name": "Zebra",
                "Category": "Same",
                "Sub-Category": "Same",
                "Primary Link": "https://example.com/z",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Z",
            },
            {
                "ID": "cmd-001",
                "Display Name": "Alpha",
                "Category": "Same",
                "Sub-Category": "Same",
                "Primary Link": "https://example.com/a",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "A",
            },
            {
                "ID": "cmd-002",
                "Display Name": "Beta",
                "Category": "Same",
                "Sub-Category": "Same",
                "Primary Link": "https://example.com/b",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "B",
            },
        ]

        set_category_order(monkeypatch, [{"name": "Same"}])
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)
        names = [row["Display Name"] for row in sorted_data]

        assert names == ["Alpha", "Beta", "Zebra"]

    def test_empty_subcategory_sorts_last(
        self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that empty sub-categories sort after filled ones."""
        data = [
            {
                "ID": "1",
                "Display Name": "No Subcat",
                "Category": "Test",
                "Sub-Category": "",
                "Primary Link": "https://example.com/1",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Empty subcat",
            },
            {
                "ID": "2",
                "Display Name": "Has Subcat",
                "Category": "Test",
                "Sub-Category": "Subcategory A",
                "Primary Link": "https://example.com/2",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Has subcat",
            },
        ]

        set_category_order(monkeypatch, [{"name": "Test"}])
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)

        # Item with subcategory should come first
        assert sorted_data[0]["Sub-Category"] == "Subcategory A"
        assert sorted_data[1]["Sub-Category"] == ""

    def test_unknown_category_sorts_last(
        self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that categories not in the predefined order sort last."""
        data = [
            {
                "ID": "1",
                "Display Name": "Unknown Cat",
                "Category": "Unknown Category",
                "Sub-Category": "",
                "Primary Link": "https://example.com/1",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Unknown",
            },
            {
                "ID": "2",
                "Display Name": "Known Cat",
                "Category": "Known",
                "Sub-Category": "",
                "Primary Link": "https://example.com/2",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Known",
            },
        ]

        set_category_order(monkeypatch, [{"name": "Known"}])
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)

        # Known category should come first
        assert sorted_data[0]["Category"] == "Known"
        assert sorted_data[1]["Category"] == "Unknown Category"

    def test_subcategory_yaml_order_sort(
        self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that subcategories are sorted by their defined order in YAML."""
        data = [
            {
                "ID": "1",
                "Display Name": "A",
                "Category": "Slash-Commands",
                "Sub-Category": "Miscellaneous",
                "Primary Link": "https://example.com/1",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "M",
            },
            {
                "ID": "2",
                "Display Name": "B",
                "Category": "Slash-Commands",
                "Sub-Category": "Version Control & Git",
                "Primary Link": "https://example.com/2",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "V",
            },
            {
                "ID": "3",
                "Display Name": "C",
                "Category": "Slash-Commands",
                "Sub-Category": "General",
                "Primary Link": "https://example.com/3",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "G",
            },
            {
                "ID": "4",
                "Display Name": "D",
                "Category": "Slash-Commands",
                "Sub-Category": "CI / Deployment",
                "Primary Link": "https://example.com/4",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "C",
            },
        ]

        # Mock the categories with subcategories in specific order
        mock_categories = [
            {
                "name": "Slash-Commands",
                "subcategories": [
                    {"name": "General"},
                    {"name": "Version Control & Git"},
                    {"name": "Code Analysis & Testing"},
                    {"name": "Context Loading & Priming"},
                    {"name": "Documentation & Changelogs"},
                    {"name": "CI / Deployment"},
                    {"name": "Project & Task Management"},
                    {"name": "Miscellaneous"},
                ],
            }
        ]

        set_category_order(monkeypatch, mock_categories)
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)
        subcats = [row["Sub-Category"] for row in sorted_data]

        # Should follow YAML order: General first, Version Control,
        # CI/Deployment, then Miscellaneous last
        assert subcats == [
            "General",
            "Version Control & Git",
            "CI / Deployment",
            "Miscellaneous",
        ]

    def test_case_insensitive_display_name_sort(
        self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that display name sorting is case-insensitive."""
        data = [
            {
                "ID": "1",
                "Display Name": "UPPERCASE",
                "Category": "Test",
                "Sub-Category": "",
                "Primary Link": "https://example.com/1",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Upper",
            },
            {
                "ID": "2",
                "Display Name": "lowercase",
                "Category": "Test",
                "Sub-Category": "",
                "Primary Link": "https://example.com/2",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Lower",
            },
            {
                "ID": "3",
                "Display Name": "MixedCase",
                "Category": "Test",
                "Sub-Category": "",
                "Primary Link": "https://example.com/3",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Mixed",
            },
        ]

        set_category_order(monkeypatch, [{"name": "Test"}])
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)
        names = [row["Display Name"] for row in sorted_data]

        # Should be sorted alphabetically regardless of case
        assert names == ["lowercase", "MixedCase", "UPPERCASE"]

    def test_empty_csv_file(self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test handling of empty CSV file."""
        # Create empty file
        temp_csv.write_text("")

        set_category_order(monkeypatch, [])
        # Should not raise an error
        sort_resources(temp_csv)

        # File should still be empty
        assert temp_csv.read_text() == ""

    def test_missing_fields_handled_gracefully(
        self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing fields in CSV rows are handled gracefully."""
        data = [
            {
                "ID": "1",
                "Display Name": "Complete",
                "Category": "Test",
                "Sub-Category": "Sub",
                "Primary Link": "https://example.com/1",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Complete row",
            },
            {
                "ID": "2",
                "Display Name": "Missing Category",
                # Missing Category field
                "Sub-Category": "Sub",
                "Primary Link": "https://example.com/2",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Missing category",
            },
            {
                "ID": "3",
                # Missing Display Name
                "Category": "Test",
                "Sub-Category": "Sub",
                "Primary Link": "https://example.com/3",
                "Author Name": "A",
                "Author Link": "https://github.com/a",
                "Description": "Missing name",
            },
        ]

        set_category_order(monkeypatch, [{"name": "Test"}])
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)

        # Should handle missing fields without crashing
        assert len(sorted_data) == 3
        # Missing display name should sort as empty string (first)
        assert sorted_data[0]["ID"] == "3"

    def test_category_manager_exception_handling(
        self,
        temp_csv: Path,
        sample_csv_data: list[dict[str, str]],
        capsys: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that exceptions from category_manager are handled gracefully."""
        set_category_order_error(monkeypatch, "Category manager error")
        write_csv(temp_csv, sample_csv_data)
        sort_resources(temp_csv)

        # Should still sort the file (alphabetically)
        sorted_data = read_csv(temp_csv)
        assert len(sorted_data) == len(sample_csv_data)

        # Check that warning was printed
        captured = capsys.readouterr()
        assert "Warning: Could not load category order" in captured.out
        assert "Using alphabetical sorting instead" in captured.out

    def test_preserve_all_csv_fields(self, temp_csv: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that all CSV fields are preserved after sorting."""
        data = [
            {
                "ID": "1",
                "Display Name": "Test",
                "Category": "Test",
                "Sub-Category": "",
                "Primary Link": "https://example.com/1",
                "Author Name": "Author",
                "Author Link": "https://github.com/author",
                "Description": "Description",
                "Extra Field 1": "Extra Value 1",
                "Extra Field 2": "Extra Value 2",
                "Active": "true",
                "Last Checked": "2024-01-01",
            }
        ]

        set_category_order(monkeypatch, [{"name": "Test"}])
        write_csv(temp_csv, data)
        sort_resources(temp_csv)

        sorted_data = read_csv(temp_csv)

        # All fields should be preserved
        assert sorted_data[0]["Extra Field 1"] == "Extra Value 1"
        assert sorted_data[0]["Extra Field 2"] == "Extra Value 2"
        assert sorted_data[0]["Active"] == "true"
        assert sorted_data[0]["Last Checked"] == "2024-01-01"

    def test_category_summary_output(
        self,
        temp_csv: Path,
        sample_csv_data: list[dict[str, str]],
        capsys: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that category summary is printed correctly."""
        set_category_order(
            monkeypatch,
            [
                {"name": "Workflows & Knowledge Guides"},
                {"name": "Tooling"},
                {"name": "Slash-Commands"},
            ],
        )
        write_csv(temp_csv, sample_csv_data)
        sort_resources(temp_csv)

        captured = capsys.readouterr()

        # Check summary output
        assert "Category Summary:" in captured.out
        assert "Workflows & Knowledge Guides:" in captured.out
        assert "(no sub-category): 1 items" in captured.out
        assert "Slash-Commands:" in captured.out
        assert "Code Analysis & Testing: 2 items" in captured.out
        assert "Version Control & Git: 1 items" in captured.out

    def test_multiple_sort_stability(
        self,
        temp_csv: Path,
        sample_csv_data: list[dict[str, str]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        Test that sorting multiple times produces the same result
        (stable sort).
        """
        set_category_order(
            monkeypatch,
            [
                {"name": "Workflows & Knowledge Guides"},
                {"name": "Tooling"},
                {"name": "Slash-Commands"},
            ],
        )
        write_csv(temp_csv, sample_csv_data)

        # Sort once
        sort_resources(temp_csv)
        first_sort = read_csv(temp_csv)

        # Sort again
        sort_resources(temp_csv)
        second_sort = read_csv(temp_csv)

        # Results should be identical
        assert first_sort == second_sort
