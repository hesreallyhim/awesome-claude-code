#!/usr/bin/env python3
"""Tests for flat list README generation functionality."""

import csv
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add repo root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.readme.generators.flat import (  # noqa: E402
    FLAT_CATEGORIES,
    FLAT_SORT_TYPES,
    ParameterizedFlatListGenerator,
)
from scripts.readme.helpers.readme_assets import generate_flat_badges  # noqa: E402
from scripts.readme.helpers.readme_paths import resolve_asset_tokens  # noqa: E402


@dataclass
class FlatListEnv:
    """Filesystem paths for flat list generator tests."""

    root: Path
    template_dir: Path
    assets_dir: Path
    csv_path: Path


DEFAULT_ROWS = [
    {
        "ID": "test-1",
        "Display Name": "Test Resource",
        "Category": "Tooling",
        "Sub-Category": "General",
        "Primary Link": "https://github.com/test/repo",
        "Author Name": "Test Author",
        "Author Link": "https://github.com/testauthor",
        "Description": "A test resource",
        "Active": "TRUE",
        "Last Modified": "2025-01-01",
        "Repo Created": "2024-06-01",
    },
    {
        "ID": "test-2",
        "Display Name": "Another Resource",
        "Category": "Hooks",
        "Sub-Category": "General",
        "Primary Link": "https://github.com/test/hooks",
        "Author Name": "Hook Author",
        "Author Link": "https://github.com/hookauthor",
        "Description": "A hooks resource",
        "Active": "TRUE",
        "Last Modified": "2025-01-15",
        "Repo Created": "2024-12-01",
    },
]

MINIMAL_ROWS = [
    {
        "ID": "test-1",
        "Display Name": "Test",
        "Category": "Tooling",
        "Sub-Category": "",
        "Primary Link": "https://example.com",
        "Author Name": "Author",
        "Author Link": "https://example.com/author",
        "Description": "Test",
        "Active": "TRUE",
        "Last Modified": "2025-01-01",
        "Repo Created": "2024-01-01",
    },
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write CSV rows to disk."""
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def create_env(tmp_path: Path, rows: list[dict[str, str]]) -> FlatListEnv:
    """Create a temp environment with CSV, templates, and assets."""
    template_dir = tmp_path / "templates"
    assets_dir = tmp_path / "assets"
    template_dir.mkdir()
    assets_dir.mkdir()
    csv_path = tmp_path / "test.csv"
    write_csv(csv_path, rows)

    return FlatListEnv(
        root=tmp_path,
        template_dir=template_dir,
        assets_dir=assets_dir,
        csv_path=csv_path,
    )


def make_generator(env: FlatListEnv, category_slug: str = "all", sort_type: str = "az"):
    """Create a generator instance using the provided env."""
    return ParameterizedFlatListGenerator(
        str(env.csv_path),
        str(env.template_dir),
        str(env.assets_dir),
        str(env.root),
        category_slug=category_slug,
        sort_type=sort_type,
    )


@pytest.fixture
def flat_list_env(tmp_path: Path) -> FlatListEnv:
    """Environment with default CSV rows."""
    return create_env(tmp_path, DEFAULT_ROWS)


class TestFlatCategories:
    """Test cases for FLAT_CATEGORIES configuration."""

    def test_all_category_exists(self) -> None:
        """Test that 'all' category exists and has None as csv_value."""
        assert "all" in FLAT_CATEGORIES
        csv_value, display, color = FLAT_CATEGORIES["all"]
        assert csv_value is None
        assert display == "All"

    def test_all_categories_have_required_fields(self) -> None:
        """Test all categories have (csv_value, display_name, color) tuple."""
        for _, value in FLAT_CATEGORIES.items():
            assert isinstance(value, tuple)
            assert len(value) == 3
            _, display, color = value
            assert isinstance(display, str)
            assert color.startswith("#")

    def test_expected_categories_exist(self) -> None:
        """Test that expected categories are defined."""
        expected = [
            "all",
            "tooling",
            "commands",
            "claude-md",
            "workflows",
            "hooks",
            "skills",
            "styles",
            "statusline",
            "docs",
            "clients",
        ]
        for cat in expected:
            assert cat in FLAT_CATEGORIES, f"Missing category: {cat}"

    def test_category_count(self) -> None:
        """Test we have 11 categories."""
        assert len(FLAT_CATEGORIES) == 11


class TestFlatSortTypes:
    """Test cases for FLAT_SORT_TYPES configuration."""

    def test_all_sort_types_exist(self) -> None:
        """Test all expected sort types are defined."""
        expected = ["az", "updated", "created", "releases"]
        for sort_type in expected:
            assert sort_type in FLAT_SORT_TYPES

    def test_sort_types_have_required_fields(self) -> None:
        """Test all sort types have (display, color, description) tuple."""
        for _, value in FLAT_SORT_TYPES.items():
            assert isinstance(value, tuple)
            assert len(value) == 3
            display, color, description = value
            assert isinstance(display, str)
            assert color.startswith("#")
            assert isinstance(description, str)

    def test_sort_type_count(self) -> None:
        """Test we have 4 sort types."""
        assert len(FLAT_SORT_TYPES) == 4


class TestParameterizedFlatListGenerator:
    """Test cases for ParameterizedFlatListGenerator class."""

    def test_output_filename_format(self, flat_list_env: FlatListEnv) -> None:
        """Test output filename follows expected pattern."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="az")
        assert generator.output_filename == "README_ALTERNATIVES/README_FLAT_ALL_AZ.md"

    @pytest.mark.parametrize(
        "cat_slug, sort_type, expected",
        [
            ("tooling", "updated", "README_ALTERNATIVES/README_FLAT_TOOLING_UPDATED.md"),
            ("hooks", "releases", "README_ALTERNATIVES/README_FLAT_HOOKS_RELEASES.md"),
            ("claude-md", "created", "README_ALTERNATIVES/README_FLAT_CLAUDE-MD_CREATED.md"),
        ],
    )
    def test_output_filename_with_different_params(
        self, flat_list_env: FlatListEnv, cat_slug: str, sort_type: str, expected: str
    ) -> None:
        """Test output filename with various category/sort combinations."""
        generator = make_generator(flat_list_env, category_slug=cat_slug, sort_type=sort_type)
        assert generator.output_filename == expected

    def test_get_filtered_resources_all(self, flat_list_env: FlatListEnv) -> None:
        """Test filtering with 'all' category returns all resources."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="az")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        assert len(resources) == 2

    def test_get_filtered_resources_specific_category(self, flat_list_env: FlatListEnv) -> None:
        """Test filtering with specific category."""
        generator = make_generator(flat_list_env, category_slug="tooling", sort_type="az")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        assert len(resources) == 1
        assert resources[0]["Display Name"] == "Test Resource"

    def test_get_filtered_resources_hooks_category(self, flat_list_env: FlatListEnv) -> None:
        """Test filtering with hooks category."""
        generator = make_generator(flat_list_env, category_slug="hooks", sort_type="az")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        assert len(resources) == 1
        assert resources[0]["Display Name"] == "Another Resource"

    def test_sort_resources_alphabetical(self, flat_list_env: FlatListEnv) -> None:
        """Test alphabetical sorting."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="az")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # "Another Resource" should come before "Test Resource"
        assert sorted_resources[0]["Display Name"] == "Another Resource"
        assert sorted_resources[1]["Display Name"] == "Test Resource"

    def test_sort_resources_by_updated(self, flat_list_env: FlatListEnv) -> None:
        """Test sorting by last modified date."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="updated")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # "Another Resource" (2025-01-15) should come before "Test Resource" (2025-01-01)
        assert sorted_resources[0]["Display Name"] == "Another Resource"
        assert sorted_resources[1]["Display Name"] == "Test Resource"

    def test_sort_resources_by_created(self, flat_list_env: FlatListEnv) -> None:
        """Test sorting by repo creation date."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="created")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # "Another Resource" (2024-12-01) should come before "Test Resource" (2024-06-01)
        assert sorted_resources[0]["Display Name"] == "Another Resource"
        assert sorted_resources[1]["Display Name"] == "Test Resource"

    def test_generate_sort_navigation(self, flat_list_env: FlatListEnv) -> None:
        """Test sort navigation badge generation."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="az")
        nav = generator.generate_sort_navigation()
        resolved = resolve_asset_tokens(
            nav,
            flat_list_env.root / "README_ALTERNATIVES" / "README_FLAT_ALL_AZ.md",
            flat_list_env.root,
        )

        # Check for all sort options
        assert "README_FLAT_ALL_AZ" in nav
        assert "README_FLAT_ALL_UPDATED" in nav
        assert "README_FLAT_ALL_CREATED" in nav
        assert "README_FLAT_ALL_RELEASES" in nav

        # Check current selection has border
        assert 'style="border: 3px solid #6366f1' in nav  # az color

        # Check asset paths use ../assets/ (one level up)
        assert 'src="../assets/badge-sort-az.svg"' in resolved

    def test_generate_category_navigation(self, flat_list_env: FlatListEnv) -> None:
        """Test category navigation badge generation."""
        generator = make_generator(flat_list_env, category_slug="hooks", sort_type="az")
        nav = generator.generate_category_navigation()
        resolved = resolve_asset_tokens(
            nav,
            flat_list_env.root / "README_ALTERNATIVES" / "README_FLAT_HOOKS_AZ.md",
            flat_list_env.root,
        )

        # Check for category links (should maintain current sort type)
        assert "README_FLAT_ALL_AZ" in nav
        assert "README_FLAT_TOOLING_AZ" in nav
        assert "README_FLAT_HOOKS_AZ" in nav

        # Check hooks has border (current selection)
        assert 'style="border: 2px solid #f97316' in nav  # hooks color

        # Check asset paths use ../assets/ (one level up)
        assert 'src="../assets/badge-cat-hooks.svg"' in resolved

    def test_generate_resources_table_standard(self, flat_list_env: FlatListEnv) -> None:
        """Test resources table generation for non-releases view."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="az")
        generator.csv_data = generator.load_csv_data()
        table = generator.generate_resources_table()

        # Check HTML table structure
        assert "<table>" in table
        assert "<thead>" in table
        assert "<th>Resource</th>" in table
        assert "<th>Category</th>" in table
        assert "<th>Sub-Category</th>" in table
        assert "<th>Description</th>" in table

        # Check stacked format (now HTML)
        assert "<b>Another Resource</b>" in table
        assert "<br>by" in table

        # Check full description (no truncation)
        assert "A hooks resource" in table

        # Check shields.io badges are present for GitHub resources
        assert "img.shields.io/github/stars" in table
        assert "?style=flat" in table

    def test_generate_resources_table_empty_category(self, flat_list_env: FlatListEnv) -> None:
        """Test resources table for empty category."""
        generator = make_generator(flat_list_env, category_slug="clients", sort_type="az")
        generator.csv_data = generator.load_csv_data()
        table = generator.generate_resources_table()

        assert "No resources found in this category" in table

    def test_default_template_has_correct_paths(self, flat_list_env: FlatListEnv) -> None:
        """Test default template uses style selector placeholder."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="az")
        template = generator._get_default_template()

        # Template should use {{STYLE_SELECTOR}} placeholder for dynamic path generation
        assert "{{STYLE_SELECTOR}}" in template

    def test_releases_disclaimer_in_template(self, flat_list_env: FlatListEnv) -> None:
        """Test releases view includes disclaimer."""
        generator = make_generator(flat_list_env, category_slug="all", sort_type="releases")
        generator.csv_data = generator.load_csv_data()

        template = generator._get_default_template()
        assert "{{RELEASES_DISCLAIMER}}" in template


class TestGenerateFlatBadges:
    """Test cases for generate_flat_badges function."""

    def test_creates_sort_badges(self, tmp_path: Path) -> None:
        """Test that sort badges are created."""
        generate_flat_badges(str(tmp_path), FLAT_SORT_TYPES, FLAT_CATEGORIES)

        for slug in FLAT_SORT_TYPES:
            badge_path = tmp_path / f"badge-sort-{slug}.svg"
            assert badge_path.exists(), f"Missing badge: {badge_path}"

    def test_creates_category_badges(self, tmp_path: Path) -> None:
        """Test that category badges are created."""
        generate_flat_badges(str(tmp_path), FLAT_SORT_TYPES, FLAT_CATEGORIES)

        for slug in FLAT_CATEGORIES:
            badge_path = tmp_path / f"badge-cat-{slug}.svg"
            assert badge_path.exists(), f"Missing badge: {badge_path}"

    def test_badge_is_valid_svg(self, tmp_path: Path) -> None:
        """Test that generated badges are valid SVG."""
        generate_flat_badges(str(tmp_path), FLAT_SORT_TYPES, FLAT_CATEGORIES)

        badge_path = tmp_path / "badge-sort-az.svg"
        content = badge_path.read_text(encoding="utf-8")

        assert "<svg" in content
        assert "</svg>" in content
        assert "xmlns=" in content

    def test_sort_badge_contains_display_name(self, tmp_path: Path) -> None:
        """Test sort badges contain correct display names."""
        generate_flat_badges(str(tmp_path), FLAT_SORT_TYPES, FLAT_CATEGORIES)

        badge_path = tmp_path / "badge-sort-az.svg"
        content = badge_path.read_text(encoding="utf-8")

        display_name = FLAT_SORT_TYPES["az"][0]
        assert display_name in content

    def test_category_badge_contains_display_name(self, tmp_path: Path) -> None:
        """Test category badges contain correct display names."""
        generate_flat_badges(str(tmp_path), FLAT_SORT_TYPES, FLAT_CATEGORIES)

        badge_path = tmp_path / "badge-cat-hooks.svg"
        content = badge_path.read_text(encoding="utf-8")

        display_name = FLAT_CATEGORIES["hooks"][1]
        assert display_name in content


class TestReleasesSort:
    """Test cases for releases sorting functionality."""

    def test_releases_filter_recent(self, tmp_path: Path) -> None:
        """Test that releases sort only includes recent releases."""
        now = datetime.now()
        recent = (now - timedelta(days=10)).strftime("%Y-%m-%d:%H-%M-%S")
        old = (now - timedelta(days=60)).strftime("%Y-%m-%d:%H-%M-%S")

        rows = [
            {
                "ID": "recent-1",
                "Display Name": "Recent Release",
                "Category": "Tooling",
                "Primary Link": "https://github.com/test/recent",
                "Author Name": "Author",
                "Author Link": "https://github.com/author",
                "Description": "Has recent release",
                "Active": "TRUE",
                "Latest Release": recent,
                "Release Version": "v1.0.0",
                "Release Source": "github-releases",
            },
            {
                "ID": "old-1",
                "Display Name": "Old Release",
                "Category": "Tooling",
                "Primary Link": "https://github.com/test/old",
                "Author Name": "Author",
                "Author Link": "https://github.com/author",
                "Description": "Has old release",
                "Active": "TRUE",
                "Latest Release": old,
                "Release Version": "v0.5.0",
                "Release Source": "github-releases",
            },
        ]
        env = create_env(tmp_path, rows)

        generator = make_generator(env, category_slug="all", sort_type="releases")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # Only recent release should be included
        assert len(sorted_resources) == 1
        assert sorted_resources[0]["Display Name"] == "Recent Release"

    def test_releases_sort_order(self, tmp_path: Path) -> None:
        """Test that releases are sorted by date (most recent first)."""
        now = datetime.now()
        day5 = (now - timedelta(days=5)).strftime("%Y-%m-%d:%H-%M-%S")
        day10 = (now - timedelta(days=10)).strftime("%Y-%m-%d:%H-%M-%S")
        day15 = (now - timedelta(days=15)).strftime("%Y-%m-%d:%H-%M-%S")

        rows = [
            {
                "ID": "mid",
                "Display Name": "Middle Release",
                "Category": "Tooling",
                "Primary Link": "https://github.com/test/mid",
                "Author Name": "Author",
                "Author Link": "https://github.com/author",
                "Description": "10 days ago",
                "Active": "TRUE",
                "Latest Release": day10,
                "Release Version": "v1.0.0",
                "Release Source": "github-releases",
            },
            {
                "ID": "newest",
                "Display Name": "Newest Release",
                "Category": "Tooling",
                "Primary Link": "https://github.com/test/new",
                "Author Name": "Author",
                "Author Link": "https://github.com/author",
                "Description": "5 days ago",
                "Active": "TRUE",
                "Latest Release": day5,
                "Release Version": "v2.0.0",
                "Release Source": "github-releases",
            },
            {
                "ID": "oldest",
                "Display Name": "Oldest Release",
                "Category": "Tooling",
                "Primary Link": "https://github.com/test/old",
                "Author Name": "Author",
                "Author Link": "https://github.com/author",
                "Description": "15 days ago",
                "Active": "TRUE",
                "Latest Release": day15,
                "Release Version": "v0.5.0",
                "Release Source": "github-releases",
            },
        ]
        env = create_env(tmp_path, rows)

        generator = make_generator(env, category_slug="all", sort_type="releases")
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        assert len(sorted_resources) == 3
        assert sorted_resources[0]["Display Name"] == "Newest Release"
        assert sorted_resources[1]["Display Name"] == "Middle Release"
        assert sorted_resources[2]["Display Name"] == "Oldest Release"

    def test_releases_table_format(self, tmp_path: Path) -> None:
        """Test releases table has correct columns."""
        now = datetime.now()
        recent = (now - timedelta(days=5)).strftime("%Y-%m-%d:%H-%M-%S")

        rows = [
            {
                "ID": "test-1",
                "Display Name": "Test Package",
                "Category": "Tooling",
                "Primary Link": "https://github.com/test/pkg",
                "Author Name": "Test Author",
                "Author Link": "https://github.com/testauthor",
                "Description": "A test package with release",
                "Active": "TRUE",
                "Latest Release": recent,
                "Release Version": "v1.2.3",
                "Release Source": "npm",
            },
        ]
        env = create_env(tmp_path, rows)

        generator = make_generator(env, category_slug="all", sort_type="releases")
        generator.csv_data = generator.load_csv_data()
        table = generator.generate_resources_table()

        # Check HTML table header columns
        assert "<table>" in table
        assert "<th>Resource</th>" in table
        assert "<th>Version</th>" in table
        assert "<th>Source</th>" in table
        assert "<th>Release Date</th>" in table
        assert "<th>Description</th>" in table

        # Check content
        assert "v1.2.3" in table
        assert "npm" in table
        assert "Test Package" in table

        # Check shields.io badges with colspan="5"
        assert 'colspan="5"' in table
        assert "img.shields.io/github/stars" in table


class TestCombinationGeneration:
    """Test that all category × sort combinations work correctly."""

    @pytest.mark.parametrize("cat_slug", FLAT_CATEGORIES)
    @pytest.mark.parametrize("sort_type", FLAT_SORT_TYPES)
    def test_all_combinations_instantiate(
        self, tmp_path: Path, cat_slug: str, sort_type: str
    ) -> None:
        """Test all 44 combinations can be instantiated."""
        env = create_env(tmp_path, MINIMAL_ROWS)
        generator = make_generator(env, category_slug=cat_slug, sort_type=sort_type)
        assert generator is not None

    def test_total_combinations(self) -> None:
        """Test that we expect 44 total combinations (11 × 4)."""
        expected = len(FLAT_CATEGORIES) * len(FLAT_SORT_TYPES)
        assert expected == 44
