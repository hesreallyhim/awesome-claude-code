#!/usr/bin/env python3
"""Tests for flat list README generation functionality."""

import os
import sys
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_readme import (
    FLAT_CATEGORIES,
    FLAT_SORT_TYPES,
    ParameterizedFlatListGenerator,
    generate_flat_badges,
    parse_resource_date,
)


class TestFlatCategories(unittest.TestCase):
    """Test cases for FLAT_CATEGORIES configuration."""

    def test_all_category_exists(self):
        """Test that 'all' category exists and has None as csv_value."""
        self.assertIn("all", FLAT_CATEGORIES)
        csv_value, display, color = FLAT_CATEGORIES["all"]
        self.assertIsNone(csv_value)
        self.assertEqual(display, "All")

    def test_all_categories_have_required_fields(self):
        """Test all categories have (csv_value, display_name, color) tuple."""
        for slug, value in FLAT_CATEGORIES.items():
            with self.subTest(slug=slug):
                self.assertIsInstance(value, tuple)
                self.assertEqual(len(value), 3)
                csv_value, display, color = value
                self.assertIsInstance(display, str)
                self.assertTrue(color.startswith("#"))

    def test_expected_categories_exist(self):
        """Test that expected categories are defined."""
        expected = ["all", "tooling", "commands", "claude-md", "workflows",
                    "hooks", "skills", "styles", "statusline", "docs", "clients"]
        for cat in expected:
            self.assertIn(cat, FLAT_CATEGORIES, f"Missing category: {cat}")

    def test_category_count(self):
        """Test we have 11 categories."""
        self.assertEqual(len(FLAT_CATEGORIES), 11)


class TestFlatSortTypes(unittest.TestCase):
    """Test cases for FLAT_SORT_TYPES configuration."""

    def test_all_sort_types_exist(self):
        """Test all expected sort types are defined."""
        expected = ["az", "updated", "created", "releases"]
        for sort_type in expected:
            self.assertIn(sort_type, FLAT_SORT_TYPES)

    def test_sort_types_have_required_fields(self):
        """Test all sort types have (display, color, description) tuple."""
        for slug, value in FLAT_SORT_TYPES.items():
            with self.subTest(slug=slug):
                self.assertIsInstance(value, tuple)
                self.assertEqual(len(value), 3)
                display, color, description = value
                self.assertIsInstance(display, str)
                self.assertTrue(color.startswith("#"))
                self.assertIsInstance(description, str)

    def test_sort_type_count(self):
        """Test we have 4 sort types."""
        self.assertEqual(len(FLAT_SORT_TYPES), 4)


class TestParameterizedFlatListGenerator(unittest.TestCase):
    """Test cases for ParameterizedFlatListGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.temp_dir, "templates")
        self.assets_dir = os.path.join(self.temp_dir, "assets")
        os.makedirs(self.template_dir)
        os.makedirs(self.assets_dir)

        # Create a minimal CSV file
        self.csv_path = os.path.join(self.temp_dir, "test.csv")
        self._create_test_csv()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_test_csv(self, rows=None):
        """Create a test CSV file."""
        if rows is None:
            rows = [
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

        import csv
        fieldnames = list(rows[0].keys()) if rows else []
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_output_filename_format(self):
        """Test output filename follows expected pattern."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="az"
        )
        self.assertEqual(
            generator.output_filename,
            "README_ALTERNATIVES/README_FLAT_ALL_AZ.md"
        )

    def test_output_filename_with_different_params(self):
        """Test output filename with various category/sort combinations."""
        test_cases = [
            ("tooling", "updated", "README_ALTERNATIVES/README_FLAT_TOOLING_UPDATED.md"),
            ("hooks", "releases", "README_ALTERNATIVES/README_FLAT_HOOKS_RELEASES.md"),
            ("claude-md", "created", "README_ALTERNATIVES/README_FLAT_CLAUDE-MD_CREATED.md"),
        ]
        for cat, sort_type, expected in test_cases:
            with self.subTest(cat=cat, sort_type=sort_type):
                generator = ParameterizedFlatListGenerator(
                    self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
                    category_slug=cat, sort_type=sort_type
                )
                self.assertEqual(generator.output_filename, expected)

    def test_get_filtered_resources_all(self):
        """Test filtering with 'all' category returns all resources."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="az"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        self.assertEqual(len(resources), 2)

    def test_get_filtered_resources_specific_category(self):
        """Test filtering with specific category."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="tooling", sort_type="az"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["Display Name"], "Test Resource")

    def test_get_filtered_resources_hooks_category(self):
        """Test filtering with hooks category."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="hooks", sort_type="az"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["Display Name"], "Another Resource")

    def test_sort_resources_alphabetical(self):
        """Test alphabetical sorting."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="az"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # "Another Resource" should come before "Test Resource"
        self.assertEqual(sorted_resources[0]["Display Name"], "Another Resource")
        self.assertEqual(sorted_resources[1]["Display Name"], "Test Resource")

    def test_sort_resources_by_updated(self):
        """Test sorting by last modified date."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="updated"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # "Another Resource" (2025-01-15) should come before "Test Resource" (2025-01-01)
        self.assertEqual(sorted_resources[0]["Display Name"], "Another Resource")
        self.assertEqual(sorted_resources[1]["Display Name"], "Test Resource")

    def test_sort_resources_by_created(self):
        """Test sorting by repo creation date."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="created"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # "Another Resource" (2024-12-01) should come before "Test Resource" (2024-06-01)
        self.assertEqual(sorted_resources[0]["Display Name"], "Another Resource")
        self.assertEqual(sorted_resources[1]["Display Name"], "Test Resource")

    def test_generate_sort_navigation(self):
        """Test sort navigation badge generation."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="az"
        )
        nav = generator.generate_sort_navigation()

        # Check for all sort options
        self.assertIn("README_FLAT_ALL_AZ", nav)
        self.assertIn("README_FLAT_ALL_UPDATED", nav)
        self.assertIn("README_FLAT_ALL_CREATED", nav)
        self.assertIn("README_FLAT_ALL_RELEASES", nav)

        # Check current selection has border
        self.assertIn('style="border: 3px solid #6366f1', nav)  # az color

        # Check asset paths use ../assets/ (one level up)
        self.assertIn('src="../assets/badge-sort-az.svg"', nav)

    def test_generate_category_navigation(self):
        """Test category navigation badge generation."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="hooks", sort_type="az"
        )
        nav = generator.generate_category_navigation()

        # Check for category links (should maintain current sort type)
        self.assertIn("README_FLAT_ALL_AZ", nav)
        self.assertIn("README_FLAT_TOOLING_AZ", nav)
        self.assertIn("README_FLAT_HOOKS_AZ", nav)

        # Check hooks has border (current selection)
        self.assertIn('style="border: 2px solid #f97316', nav)  # hooks color

        # Check asset paths use ../assets/ (one level up)
        self.assertIn('src="../assets/badge-cat-hooks.svg"', nav)

    def test_generate_resources_table_standard(self):
        """Test resources table generation for non-releases view."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="az"
        )
        generator.csv_data = generator.load_csv_data()
        table = generator.generate_resources_table()

        # Check header
        self.assertIn("| Resource | Category | Sub-Category | Description |", table)

        # Check stacked format
        self.assertIn("[**Another Resource**]", table)
        self.assertIn("<br>by [Hook Author]", table)

        # Check full description (no truncation)
        self.assertIn("A hooks resource", table)

    def test_generate_resources_table_empty_category(self):
        """Test resources table for empty category."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="clients", sort_type="az"  # No clients in test data
        )
        generator.csv_data = generator.load_csv_data()
        table = generator.generate_resources_table()

        self.assertIn("No resources found in this category", table)

    def test_default_template_has_correct_paths(self):
        """Test default template uses correct relative paths."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="az"
        )
        template = generator._get_default_template()

        # Check paths use ../ for root and ../assets/ for assets
        self.assertIn('href="../"', template)  # Links to repo root
        self.assertIn('src="../assets/', template)
        self.assertIn('href="README_CLASSIC.md"', template)  # Same folder
        self.assertIn('href="README_FLAT_ALL_AZ.md"', template)  # Same folder

    def test_releases_disclaimer_in_template(self):
        """Test releases view includes disclaimer."""
        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="releases"
        )
        generator.csv_data = generator.load_csv_data()

        # Mock the generate method partially
        template = generator._get_default_template()
        self.assertIn("{{RELEASES_DISCLAIMER}}", template)


class TestGenerateFlatBadges(unittest.TestCase):
    """Test cases for generate_flat_badges function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_creates_sort_badges(self):
        """Test that sort badges are created."""
        generate_flat_badges(self.temp_dir)

        for slug in FLAT_SORT_TYPES:
            badge_path = os.path.join(self.temp_dir, f"badge-sort-{slug}.svg")
            self.assertTrue(os.path.exists(badge_path), f"Missing badge: {badge_path}")

    def test_creates_category_badges(self):
        """Test that category badges are created."""
        generate_flat_badges(self.temp_dir)

        for slug in FLAT_CATEGORIES:
            badge_path = os.path.join(self.temp_dir, f"badge-cat-{slug}.svg")
            self.assertTrue(os.path.exists(badge_path), f"Missing badge: {badge_path}")

    def test_badge_is_valid_svg(self):
        """Test that generated badges are valid SVG."""
        generate_flat_badges(self.temp_dir)

        badge_path = os.path.join(self.temp_dir, "badge-sort-az.svg")
        with open(badge_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("<svg", content)
        self.assertIn("</svg>", content)
        self.assertIn("xmlns=", content)

    def test_sort_badge_contains_display_name(self):
        """Test sort badges contain correct display names."""
        generate_flat_badges(self.temp_dir)

        badge_path = os.path.join(self.temp_dir, "badge-sort-az.svg")
        with open(badge_path, "r", encoding="utf-8") as f:
            content = f.read()

        display_name = FLAT_SORT_TYPES["az"][0]
        self.assertIn(display_name, content)

    def test_category_badge_contains_display_name(self):
        """Test category badges contain correct display names."""
        generate_flat_badges(self.temp_dir)

        badge_path = os.path.join(self.temp_dir, "badge-cat-hooks.svg")
        with open(badge_path, "r", encoding="utf-8") as f:
            content = f.read()

        display_name = FLAT_CATEGORIES["hooks"][1]
        self.assertIn(display_name, content)


class TestReleasesSort(unittest.TestCase):
    """Test cases for releases sorting functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.temp_dir, "templates")
        self.assets_dir = os.path.join(self.temp_dir, "assets")
        os.makedirs(self.template_dir)
        os.makedirs(self.assets_dir)
        self.csv_path = os.path.join(self.temp_dir, "test.csv")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_csv_with_releases(self, rows):
        """Create CSV with release data."""
        import csv
        fieldnames = list(rows[0].keys()) if rows else []
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_releases_filter_recent(self):
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
        self._create_csv_with_releases(rows)

        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="releases"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        # Only recent release should be included
        self.assertEqual(len(sorted_resources), 1)
        self.assertEqual(sorted_resources[0]["Display Name"], "Recent Release")

    def test_releases_sort_order(self):
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
        self._create_csv_with_releases(rows)

        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="releases"
        )
        generator.csv_data = generator.load_csv_data()
        resources = generator.get_filtered_resources()
        sorted_resources = generator.sort_resources(resources)

        self.assertEqual(len(sorted_resources), 3)
        self.assertEqual(sorted_resources[0]["Display Name"], "Newest Release")
        self.assertEqual(sorted_resources[1]["Display Name"], "Middle Release")
        self.assertEqual(sorted_resources[2]["Display Name"], "Oldest Release")

    def test_releases_table_format(self):
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
        self._create_csv_with_releases(rows)

        generator = ParameterizedFlatListGenerator(
            self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
            category_slug="all", sort_type="releases"
        )
        generator.csv_data = generator.load_csv_data()
        table = generator.generate_resources_table()

        # Check header columns
        self.assertIn("| Resource | Version | Source | Release Date | Description |", table)

        # Check content
        self.assertIn("v1.2.3", table)
        self.assertIn("npm", table)
        self.assertIn("Test Package", table)


class TestCombinationGeneration(unittest.TestCase):
    """Test that all category × sort combinations work correctly."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.temp_dir, "templates")
        self.assets_dir = os.path.join(self.temp_dir, "assets")
        os.makedirs(self.template_dir)
        os.makedirs(self.assets_dir)

        self.csv_path = os.path.join(self.temp_dir, "test.csv")
        self._create_minimal_csv()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_minimal_csv(self):
        """Create minimal CSV for testing."""
        import csv
        rows = [
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
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def test_all_combinations_instantiate(self):
        """Test all 44 combinations can be instantiated."""
        count = 0
        for cat_slug in FLAT_CATEGORIES:
            for sort_type in FLAT_SORT_TYPES:
                with self.subTest(category=cat_slug, sort=sort_type):
                    generator = ParameterizedFlatListGenerator(
                        self.csv_path, self.template_dir, self.assets_dir, self.temp_dir,
                        category_slug=cat_slug, sort_type=sort_type
                    )
                    self.assertIsNotNone(generator)
                    count += 1

        self.assertEqual(count, 44)

    def test_total_combinations(self):
        """Test that we expect 44 total combinations (11 × 4)."""
        expected = len(FLAT_CATEGORIES) * len(FLAT_SORT_TYPES)
        self.assertEqual(expected, 44)


if __name__ == "__main__":
    unittest.main()
