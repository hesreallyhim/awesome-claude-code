"""Flat list README generator implementation."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from scripts.readme.generators.base import ReadmeGenerator, load_template
from scripts.readme.helpers.readme_paths import (
    ensure_generated_header,
    resolve_asset_tokens,
)
from scripts.readme.helpers.readme_utils import parse_resource_date
from scripts.readme.markup.flat import (
    generate_category_navigation as generate_flat_category_navigation,
)
from scripts.readme.markup.flat import (
    generate_navigation as generate_flat_navigation,
)
from scripts.readme.markup.flat import (
    generate_resources_table as generate_flat_resources_table,
)
from scripts.readme.markup.flat import (
    generate_sort_navigation as generate_flat_sort_navigation,
)
from scripts.readme.markup.flat import (
    get_default_template as get_flat_default_template,
)

# Category definitions: slug -> (csv_value, display_name, badge_color)
FLAT_CATEGORIES = {
    "all": (None, "All", "#71717a"),
    "tooling": ("Tooling", "Tooling", "#3b82f6"),
    "commands": ("Slash-Commands", "Commands", "#8b5cf6"),
    "claude-md": ("CLAUDE.md Files", "CLAUDE.md", "#ec4899"),
    "workflows": ("Workflows & Knowledge Guides", "Workflows", "#14b8a6"),
    "hooks": ("Hooks", "Hooks", "#f97316"),
    "skills": ("Agent Skills", "Skills", "#eab308"),
    "styles": ("Output Styles", "Styles", "#06b6d4"),
    "statusline": ("Status Lines", "Status", "#84cc16"),
    "docs": ("Official Documentation", "Docs", "#6366f1"),
    "clients": ("Alternative Clients", "Clients", "#f43f5e"),
}

# Sort type definitions: slug -> (display_name, badge_color, description)
FLAT_SORT_TYPES = {
    "az": ("A - Z", "#6366f1", "alphabetically by name"),
    "updated": ("UPDATED", "#f472b6", "by last updated date"),
    "created": ("CREATED", "#34d399", "by date created"),
    "releases": ("RELEASES", "#f59e0b", "by latest release (30 days)"),
}


class ParameterizedFlatListGenerator(ReadmeGenerator):
    """Unified generator for flat list READMEs with category filtering and sort options."""

    DAYS_THRESHOLD = 30  # For releases filter

    def __init__(
        self,
        csv_path: str,
        template_dir: str,
        assets_dir: str,
        repo_root: str,
        category_slug: str = "all",
        sort_type: str = "az",
    ) -> None:
        super().__init__(csv_path, template_dir, assets_dir, repo_root)
        self.category_slug = category_slug
        self.sort_type = sort_type
        self._category_info = FLAT_CATEGORIES.get(category_slug, FLAT_CATEGORIES["all"])
        self._sort_info = FLAT_SORT_TYPES.get(sort_type, FLAT_SORT_TYPES["az"])

    @property
    def template_filename(self) -> str:
        return "README_FLAT.template.md"

    @property
    def output_filename(self) -> str:
        return (
            f"README_ALTERNATIVES/README_FLAT_{self.category_slug.upper()}"
            f"_{self.sort_type.upper()}.md"
        )

    @property
    def style_id(self) -> str:
        return "flat"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Not used for flat list."""
        _ = include_separator
        return ""

    def generate_toc(self) -> str:
        """Not used for flat list."""
        return ""

    def generate_weekly_section(self) -> str:
        """Not used for flat list."""
        return ""

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Not used for flat list."""
        _ = category, section_index
        return ""

    def get_filtered_resources(self) -> list[dict]:
        """Get resources filtered by category."""
        csv_category_value = self._category_info[0]
        if csv_category_value is None:
            return list(self.csv_data)
        return [r for r in self.csv_data if r.get("Category", "").strip() == csv_category_value]

    def sort_resources(self, resources: list[dict]) -> list[dict]:
        """Sort resources according to sort_type."""
        if self.sort_type == "az":
            return sorted(resources, key=lambda x: (x.get("Display Name", "") or "").lower())
        if self.sort_type == "updated":
            with_dates = []
            for row in resources:
                last_modified = row.get("Last Modified", "").strip()
                parsed = parse_resource_date(last_modified) if last_modified else None
                with_dates.append((parsed, row))
            with_dates.sort(
                key=lambda x: (x[0] is None, x[0] if x[0] else datetime.min),
                reverse=True,
            )
            return [r for _, r in with_dates]
        if self.sort_type == "created":
            with_dates = []
            for row in resources:
                repo_created = row.get("Repo Created", "").strip()
                parsed = parse_resource_date(repo_created) if repo_created else None
                with_dates.append((parsed, row))
            with_dates.sort(
                key=lambda x: (x[0] is None, x[0] if x[0] else datetime.min),
                reverse=True,
            )
            return [r for _, r in with_dates]
        if self.sort_type == "releases":
            cutoff = datetime.now() - timedelta(days=self.DAYS_THRESHOLD)
            recent = []
            for row in resources:
                release_date_str = row.get("Latest Release", "")
                if not release_date_str:
                    continue
                try:
                    release_date = datetime.strptime(release_date_str, "%Y-%m-%d:%H-%M-%S")
                except ValueError:
                    continue
                if release_date >= cutoff:
                    row["_parsed_release_date"] = release_date
                    recent.append(row)
            recent.sort(key=lambda x: x.get("_parsed_release_date", datetime.min), reverse=True)
            return recent
        return resources

    def generate_sort_navigation(self) -> str:
        """Generate sort option badges."""
        return generate_flat_sort_navigation(
            self.category_slug,
            self.sort_type,
            FLAT_SORT_TYPES,
        )

    def generate_category_navigation(self) -> str:
        """Generate category filter badges."""
        return generate_flat_category_navigation(
            self.category_slug,
            self.sort_type,
            FLAT_CATEGORIES,
        )

    def generate_navigation(self) -> str:
        """Generate combined navigation (sort + category)."""
        return generate_flat_navigation(
            self.category_slug,
            self.sort_type,
            FLAT_CATEGORIES,
            FLAT_SORT_TYPES,
        )

    def generate_resources_table(self) -> str:
        """Generate the resources table as HTML with shields.io badges for GitHub resources."""
        resources = self.get_filtered_resources()
        sorted_resources = self.sort_resources(resources)
        return generate_flat_resources_table(sorted_resources, self.sort_type)

    def _get_default_template(self) -> str:
        """Return default template content."""
        return get_flat_default_template()

    def generate(self, output_path: str | None = None) -> tuple[int, str | None]:
        """Generate the flat list README for a category/sort pair."""
        resolved_path = output_path or self.resolved_output_path
        self.overrides = self.load_overrides()
        self.csv_data = self.load_csv_data()

        template_path = os.path.join(self.template_dir, self.template_filename)
        if not os.path.exists(template_path):
            template = self._get_default_template()
        else:
            template = load_template(template_path)

        resources = self.get_filtered_resources()
        sorted_resources = self.sort_resources(resources)
        navigation = generate_flat_navigation(
            self.category_slug,
            self.sort_type,
            FLAT_CATEGORIES,
            FLAT_SORT_TYPES,
        )
        resources_table = generate_flat_resources_table(sorted_resources, self.sort_type)

        generated_date = datetime.now().strftime("%Y-%m-%d")
        _, cat_display, _ = self._category_info
        _, _, sort_desc = self._sort_info

        releases_disclaimer = ""
        if self.sort_type == "releases":
            releases_disclaimer = (
                "\n> **Note:** Latest release data is pulled from GitHub Releases only. "
                "Projects without GitHub Releases will not show release info here. "
                "Please verify with the project directly.\n"
            )

        output_path = os.path.join(self.repo_root, resolved_path)

        readme_content = template
        readme_content = readme_content.replace(
            "{{STYLE_SELECTOR}}", self.get_style_selector(Path(output_path))
        )
        readme_content = readme_content.replace("{{NAVIGATION}}", navigation)
        readme_content = readme_content.replace("{{RELEASES_DISCLAIMER}}", releases_disclaimer)
        readme_content = readme_content.replace("{{RESOURCES_TABLE}}", resources_table)
        readme_content = readme_content.replace("{{RESOURCE_COUNT}}", str(len(sorted_resources)))
        readme_content = readme_content.replace("{{CATEGORY_NAME}}", cat_display)
        readme_content = readme_content.replace("{{SORT_DESC}}", sort_desc)
        readme_content = readme_content.replace("{{GENERATED_DATE}}", generated_date)

        readme_content = ensure_generated_header(readme_content)
        readme_content = resolve_asset_tokens(
            readme_content, Path(output_path), Path(self.repo_root)
        )
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        backup_path = self.create_backup(output_path)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
        except Exception as e:
            if backup_path:
                print(f"Error writing {resolved_path}: {e}")
                print(f"   Backup preserved at: {backup_path}")
            raise

        return len(sorted_resources), backup_path
