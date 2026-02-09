#!/usr/bin/env python3
"""End-to-end tests for the full README generation pipeline.

These tests exercise the complete flow: load CSV -> sort resources ->
generate all README styles -> verify outputs are valid and consistent.
They use the real project data (CSV, templates, categories) rather than
mocks, so they catch integration issues that unit tests miss.
"""

from __future__ import annotations

import csv
import re
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.categories.category_utils import CategoryManager  # noqa: E402
from scripts.readme.generate_readme import (  # noqa: E402
    PRIMARY_STYLE_IDS,
    STYLE_GENERATORS,
    build_root_generator,
)
from scripts.readme.generators.flat import (  # noqa: E402
    ParameterizedFlatListGenerator,
)
from scripts.readme.helpers.readme_config import get_root_style  # noqa: E402
from scripts.resources.sort_resources import sort_resources  # noqa: E402
from scripts.utils.repo_root import find_repo_root  # noqa: E402

REPO_ROOT = find_repo_root(Path(__file__))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def repo_paths() -> dict[str, str]:
    """Return commonly used paths from the real repo."""
    return {
        "csv": str(REPO_ROOT / "THE_RESOURCES_TABLE.csv"),
        "templates": str(REPO_ROOT / "templates"),
        "assets": str(REPO_ROOT / "assets"),
        "root": str(REPO_ROOT),
    }


@pytest.fixture(scope="module")
def csv_data() -> list[dict[str, str]]:
    """Load the real CSV data once for the module."""
    csv_path = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def active_resources(csv_data: list[dict[str, str]]) -> list[dict[str, str]]:
    """Filter to only active resources."""
    return [row for row in csv_data if row.get("Active", "").upper() == "TRUE"]


@pytest.fixture()
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory for generated files."""
    out = tmp_path / "output"
    out.mkdir()
    return out


# ---------------------------------------------------------------------------
# CSV & Data Integrity Tests
# ---------------------------------------------------------------------------


class TestCSVIntegrity:
    """Verify the source CSV is well-formed and usable."""

    REQUIRED_COLUMNS = {
        "ID",
        "Display Name",
        "Category",
        "Sub-Category",
        "Primary Link",
        "Active",
        "Description",
    }

    def test_csv_exists(self) -> None:
        csv_path = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
        assert csv_path.exists(), "THE_RESOURCES_TABLE.csv not found at repo root"

    def test_csv_has_required_columns(self, csv_data: list[dict[str, str]]) -> None:
        assert len(csv_data) > 0, "CSV is empty"
        actual_columns = set(csv_data[0].keys())
        missing = self.REQUIRED_COLUMNS - actual_columns
        assert not missing, f"CSV missing required columns: {missing}"

    def test_csv_has_active_resources(self, active_resources: list[dict[str, str]]) -> None:
        assert len(active_resources) > 10, (
            f"Expected >10 active resources, got {len(active_resources)}"
        )

    def test_all_active_resources_have_display_name(
        self, active_resources: list[dict[str, str]]
    ) -> None:
        missing = [row["ID"] for row in active_resources if not row.get("Display Name", "").strip()]
        assert not missing, f"Active resources without Display Name: {missing}"

    def test_all_active_resources_have_category(
        self, active_resources: list[dict[str, str]]
    ) -> None:
        missing = [
            row.get("Display Name", row.get("ID", "?"))
            for row in active_resources
            if not row.get("Category", "").strip()
        ]
        assert not missing, f"Active resources without Category: {missing}"

    def test_all_active_resources_have_primary_link(
        self, active_resources: list[dict[str, str]]
    ) -> None:
        missing = [
            row.get("Display Name", row.get("ID", "?"))
            for row in active_resources
            if not row.get("Primary Link", "").strip()
        ]
        assert not missing, f"Active resources without Primary Link: {missing}"

    def test_unique_ids(self, csv_data: list[dict[str, str]]) -> None:
        ids = [row["ID"] for row in csv_data if row.get("ID", "").strip()]
        dupes = [rid for rid in ids if ids.count(rid) > 1]
        assert not dupes, f"Duplicate resource IDs: {set(dupes)}"


# ---------------------------------------------------------------------------
# Sort Pipeline Tests
# ---------------------------------------------------------------------------


class TestSortPipeline:
    """Verify sorting produces valid, consistent output."""

    def test_sort_preserves_row_count(self, tmp_path: Path) -> None:
        """Sorting should not add or remove rows."""
        src = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
        work = tmp_path / "sort_test.csv"
        shutil.copy2(src, work)

        with open(work, newline="", encoding="utf-8") as f:
            before_count = sum(1 for _ in csv.reader(f)) - 1  # minus header

        sort_resources(work)

        with open(work, newline="", encoding="utf-8") as f:
            after_count = sum(1 for _ in csv.reader(f)) - 1

        assert before_count == after_count

    def test_sort_preserves_columns(self, tmp_path: Path) -> None:
        """Sorting should not alter the column set."""
        src = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
        work = tmp_path / "sort_test.csv"
        shutil.copy2(src, work)

        with open(work, newline="", encoding="utf-8") as f:
            before_cols = csv.DictReader(f).fieldnames

        sort_resources(work)

        with open(work, newline="", encoding="utf-8") as f:
            after_cols = csv.DictReader(f).fieldnames

        assert before_cols == after_cols

    def test_sort_is_idempotent(self, tmp_path: Path) -> None:
        """Sorting twice should produce the same result."""
        src = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
        work = tmp_path / "sort_test.csv"
        shutil.copy2(src, work)

        sort_resources(work)
        with open(work, encoding="utf-8") as f:
            first_sort = f.read()

        sort_resources(work)
        with open(work, encoding="utf-8") as f:
            second_sort = f.read()

        assert first_sort == second_sort, "Sorting is not idempotent"


# ---------------------------------------------------------------------------
# Category System Tests
# ---------------------------------------------------------------------------


class TestCategorySystem:
    """Verify category definitions are valid and complete."""

    def test_categories_yaml_exists(self) -> None:
        cats_path = REPO_ROOT / "templates" / "categories.yaml"
        assert cats_path.exists(), "categories.yaml not found"

    def test_categories_load_successfully(self) -> None:
        mgr = CategoryManager()
        categories = mgr.get_categories_for_readme()
        assert len(categories) > 0, "No categories loaded"

    def test_csv_categories_match_definitions(self, active_resources: list[dict[str, str]]) -> None:
        """Every category in the CSV should be defined in categories.yaml.

        Known gap: 'Output Styles' exists in the CSV but is not yet defined
        in categories.yaml.  This is tracked here so the test doesn't silently
        mask *new* undefined categories.
        """
        known_undefined = {"Output Styles"}

        # Reset the singleton to ensure fresh data (other tests may mutate it)
        CategoryManager._instance = None
        CategoryManager._data = None
        mgr = CategoryManager()
        categories = mgr.get_categories_for_readme()
        defined_names = {cat["name"] for cat in categories}

        csv_categories = {
            row["Category"] for row in active_resources if row.get("Category", "").strip()
        }

        undefined = csv_categories - defined_names - known_undefined
        assert not undefined, f"CSV categories not in categories.yaml: {undefined}"


# ---------------------------------------------------------------------------
# Full Generation Pipeline Tests
# ---------------------------------------------------------------------------


class TestGenerationPipeline:
    """End-to-end tests exercising the real generators with real data."""

    def test_generate_awesome_style(self, tmp_path: Path, repo_paths: dict[str, str]) -> None:
        """Generate the Awesome-style README and verify output."""
        gen_cls = STYLE_GENERATORS["awesome"]
        generator = gen_cls(
            repo_paths["csv"], repo_paths["templates"], repo_paths["assets"], str(tmp_path)
        )

        # We need pyproject.toml at tmp_path for repo_root detection in some helpers
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")

        # Copy templates needed
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        # Re-create generator pointing to tmp_path's template dir
        generator = gen_cls(repo_paths["csv"], str(tpl_dir), repo_paths["assets"], str(tmp_path))

        resource_count, _ = generator.generate()

        output_path = tmp_path / generator.resolved_output_path
        assert output_path.exists(), f"Output not created: {output_path}"

        content = output_path.read_text(encoding="utf-8")
        assert resource_count > 10, f"Expected >10 resources, got {resource_count}"
        assert len(content) > 1000, "Output is suspiciously short"
        assert "Awesome Claude Code" in content
        assert "## Contents" in content or "Table of Contents" in content

    def test_generate_classic_style(self, tmp_path: Path, repo_paths: dict[str, str]) -> None:
        """Generate the Classic-style README and verify output."""
        gen_cls = STYLE_GENERATORS["classic"]
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        generator = gen_cls(repo_paths["csv"], str(tpl_dir), repo_paths["assets"], str(tmp_path))

        resource_count, _ = generator.generate()
        output_path = tmp_path / generator.resolved_output_path
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert resource_count > 10
        assert len(content) > 1000

    def test_generate_extra_style(self, tmp_path: Path, repo_paths: dict[str, str]) -> None:
        """Generate the Extra/Visual-style README and verify output."""
        gen_cls = STYLE_GENERATORS["extra"]
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        generator = gen_cls(repo_paths["csv"], str(tpl_dir), repo_paths["assets"], str(tmp_path))

        resource_count, _ = generator.generate()
        output_path = tmp_path / generator.resolved_output_path
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert resource_count > 10
        assert len(content) > 1000

    def test_generate_flat_style(self, tmp_path: Path, repo_paths: dict[str, str]) -> None:
        """Generate a flat-style README (all categories, A-Z sort)."""
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        generator = ParameterizedFlatListGenerator(
            repo_paths["csv"],
            str(tpl_dir),
            repo_paths["assets"],
            str(tmp_path),
            category_slug="all",
            sort_type="az",
        )

        resource_count, _ = generator.generate()
        output_path = tmp_path / generator.resolved_output_path
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert resource_count > 10
        assert len(content) > 500

    def test_resource_count_consistent_across_styles(
        self, tmp_path: Path, repo_paths: dict[str, str]
    ) -> None:
        """All primary styles should report the same active resource count."""
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        counts: dict[str, int] = {}
        for style_id in PRIMARY_STYLE_IDS:
            gen_cls = STYLE_GENERATORS[style_id]
            generator = gen_cls(
                repo_paths["csv"], str(tpl_dir), repo_paths["assets"], str(tmp_path)
            )
            count, _ = generator.generate()
            counts[style_id] = count

        unique_counts = set(counts.values())
        assert len(unique_counts) == 1, f"Resource counts differ across styles: {counts}"

    def test_flat_category_filter(self, tmp_path: Path, repo_paths: dict[str, str]) -> None:
        """Flat generator with a category filter should produce fewer resources than 'all'."""
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        gen_all = ParameterizedFlatListGenerator(
            repo_paths["csv"],
            str(tpl_dir),
            repo_paths["assets"],
            str(tmp_path),
            category_slug="all",
            sort_type="az",
        )
        count_all, _ = gen_all.generate()

        gen_filtered = ParameterizedFlatListGenerator(
            repo_paths["csv"],
            str(tpl_dir),
            repo_paths["assets"],
            str(tmp_path),
            category_slug="tooling",
            sort_type="az",
        )
        count_filtered, _ = gen_filtered.generate()

        assert count_filtered > 0, "Tooling category has no resources"
        assert count_filtered < count_all, (
            f"Filtered count ({count_filtered}) should be < all ({count_all})"
        )


# ---------------------------------------------------------------------------
# Root README Generation Tests
# ---------------------------------------------------------------------------


class TestRootReadmeGeneration:
    """Test the root README generation (the final step of the pipeline)."""

    def test_build_root_generator_returns_correct_type(self, repo_paths: dict[str, str]) -> None:
        root_style = get_root_style()
        generator = build_root_generator(
            root_style,
            repo_paths["csv"],
            repo_paths["templates"],
            repo_paths["assets"],
            repo_paths["root"],
        )
        expected_cls = STYLE_GENERATORS[root_style]
        assert isinstance(generator, expected_cls)

    def test_root_readme_generated_at_repo_root(
        self, tmp_path: Path, repo_paths: dict[str, str]
    ) -> None:
        """The root README should be written to README.md at the output root."""
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        root_style = get_root_style()
        generator = build_root_generator(
            root_style,
            repo_paths["csv"],
            str(tpl_dir),
            repo_paths["assets"],
            str(tmp_path),
        )

        resource_count, _ = generator.generate(output_path="README.md")

        readme_path = tmp_path / "README.md"
        assert readme_path.exists(), "README.md not created at root"
        content = readme_path.read_text(encoding="utf-8")
        assert resource_count > 10
        assert "Awesome Claude Code" in content

    def test_root_readme_contains_style_selector(
        self, tmp_path: Path, repo_paths: dict[str, str]
    ) -> None:
        """Generated READMEs should include the style selector."""
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        root_style = get_root_style()
        generator = build_root_generator(
            root_style,
            repo_paths["csv"],
            str(tpl_dir),
            repo_paths["assets"],
            str(tmp_path),
        )
        generator.generate(output_path="README.md")

        content = (tmp_path / "README.md").read_text(encoding="utf-8")
        # Style selector should contain links to alternative styles
        assert "Pick Your Style" in content or "badge-style" in content


# ---------------------------------------------------------------------------
# Content Validation Tests
# ---------------------------------------------------------------------------


class TestOutputContentValidation:
    """Validate that generated content is structurally sound."""

    @pytest.fixture()
    def generated_readme(self, tmp_path: Path, repo_paths: dict[str, str]) -> str:
        """Generate a README and return its content."""
        (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
        tpl_dir = tmp_path / "templates"
        shutil.copytree(repo_paths["templates"], str(tpl_dir))

        root_style = get_root_style()
        generator = build_root_generator(
            root_style,
            repo_paths["csv"],
            str(tpl_dir),
            repo_paths["assets"],
            str(tmp_path),
        )
        generator.generate(output_path="README.md")
        return (tmp_path / "README.md").read_text(encoding="utf-8")

    def test_no_unresolved_template_tokens(self, generated_readme: str) -> None:
        """No {{TOKEN}} placeholders should remain in output."""
        tokens = re.findall(r"\{\{[A-Z_]+\}\}", generated_readme)
        assert not tokens, f"Unresolved template tokens: {tokens}"

    def test_contains_resource_links(self, generated_readme: str) -> None:
        """Output should contain HTTP(S) links to resources."""
        links = re.findall(r"https?://", generated_readme)
        assert len(links) > 20, f"Expected >20 links, got {len(links)}"

    def test_markdown_headings_present(self, generated_readme: str) -> None:
        """Output should have markdown headings for categories."""
        headings = re.findall(r"^##\s+.+", generated_readme, re.MULTILINE)
        assert len(headings) >= 3, f"Expected >= 3 headings, got {len(headings)}"

    def test_no_empty_sections(self, generated_readme: str) -> None:
        """Body category sections should have content between headings."""
        # Extract just the body sections (between first ## and the footer).
        # The footer and contribution sections legitimately have consecutive
        # headings, so we only check the resource body.
        lines = generated_readme.split("\n")
        body_start = None
        body_end = len(lines)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if body_start is None and stripped.startswith("## "):
                body_start = i
            # Stop at the footer/contribution area
            if "Contributing" in stripped or "Recommend a new resource" in stripped:
                body_end = i
                break

        if body_start is None:
            pytest.fail("No ## headings found in generated README")

        consecutive = 0
        for line in lines[body_start:body_end]:
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("### "):
                consecutive += 1
                if consecutive > 2:
                    pytest.fail(f"3+ consecutive headings detected near: {stripped}")
            elif stripped:
                consecutive = 0
