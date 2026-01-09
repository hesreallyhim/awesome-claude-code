"""Shared base class and helpers for README generators."""

from __future__ import annotations

import contextlib
import csv
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from scripts.readme.helpers.readme_config import get_root_style
from scripts.readme.helpers.readme_paths import (
    ensure_generated_header,
    resolve_asset_tokens,
)
from scripts.readme.helpers.readme_utils import build_general_anchor_map
from scripts.readme.markup.shared import generate_style_selector, load_announcements
from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))


def load_template(template_path: str) -> str:
    """Load a template file."""
    with open(template_path, encoding="utf-8") as f:
        return f.read()


def load_overrides(template_dir: str) -> dict:
    """Load resource overrides."""
    override_path = os.path.join(template_dir, "resource-overrides.yaml")
    if not os.path.exists(override_path):
        return {}

    with open(override_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("overrides", {})


def apply_overrides(row: dict, overrides: dict) -> dict:
    """Apply overrides to a resource row."""
    resource_id = row.get("ID", "")
    if not resource_id or resource_id not in overrides:
        return row

    override_config = overrides[resource_id]

    for field, value in override_config.items():
        if field in ["skip_validation", "notes"]:
            continue
        if field.endswith("_locked"):
            continue

        if field == "license":
            row["License"] = value
        elif field == "active":
            row["Active"] = value
        elif field == "description":
            row["Description"] = value

    return row


def create_backup(file_path: str, keep_latest: int = 1) -> str | None:
    """Create a backup of the file if it exists, pruning older backups."""
    if not os.path.exists(file_path):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(REPO_ROOT, ".myob", "backups")
    os.makedirs(backup_dir, exist_ok=True)

    backup_filename = f"{os.path.basename(file_path)}.{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)

    shutil.copy2(file_path, backup_path)
    if keep_latest > 0:
        basename = os.path.basename(file_path)
        backups = []
        for name in os.listdir(backup_dir):
            if name.startswith(f"{basename}.") and name.endswith(".bak"):
                backups.append(os.path.join(backup_dir, name))
        backups.sort(key=os.path.getmtime, reverse=True)
        for stale_path in backups[keep_latest:]:
            with contextlib.suppress(OSError):
                os.remove(stale_path)
    return backup_path


class ReadmeGenerator(ABC):
    """Base class for README generation with shared logic."""

    def __init__(self, csv_path: str, template_dir: str, assets_dir: str, repo_root: str) -> None:
        self.csv_path = csv_path
        self.template_dir = template_dir
        self.assets_dir = assets_dir
        self.repo_root = repo_root
        self.csv_data: list[dict] = []
        self.categories: list[dict] = []
        self.overrides: dict = {}
        self.announcements: str = ""
        self.footer: str = ""
        self.general_anchor_map: dict = {}

    @property
    @abstractmethod
    def template_filename(self) -> str:
        """Return the template filename to use."""
        ...

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """Return the preferred output filename for this style."""
        ...

    @property
    @abstractmethod
    def style_id(self) -> str:
        """Return the style ID for this generator (extra, classic, awesome, flat)."""
        ...

    @property
    def is_root_style(self) -> bool:
        """Check if this generator produces the root README style."""
        return self.style_id == get_root_style()

    @property
    def resolved_output_path(self) -> str:
        """Get the resolved output path for this generator."""
        if self.output_filename == "README.md":
            return f"README_ALTERNATIVES/README_{self.style_id.upper()}.md"
        return self.output_filename

    def get_style_selector(self, output_path: Path) -> str:
        """Generate the style selector HTML for this README."""
        return generate_style_selector(self.style_id, output_path)

    @abstractmethod
    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format a single resource entry."""
        ...

    @abstractmethod
    def generate_toc(self) -> str:
        """Generate the table of contents."""
        ...

    @abstractmethod
    def generate_weekly_section(self) -> str:
        """Generate the weekly additions section."""
        ...

    @abstractmethod
    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate content for a category section."""
        ...

    def generate_repo_ticker(self) -> str:
        """Generate the repo ticker section."""
        return ""

    def generate_banner_image(self, output_path: Path) -> str:
        """Generate banner image HTML. Override in subclasses to add a banner."""
        _ = output_path
        return ""

    def load_csv_data(self) -> list[dict]:
        """Load and filter active resources from CSV."""
        csv_data = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = apply_overrides(row, self.overrides)
                if row["Active"].upper() == "TRUE":
                    csv_data.append(row)
        return csv_data

    def load_categories(self) -> list[dict]:
        """Load categories from the category manager."""
        from scripts.categories.category_utils import category_manager

        return category_manager.get_categories_for_readme()

    def load_overrides(self) -> dict:
        """Load resource overrides from YAML."""
        return load_overrides(self.template_dir)

    def load_announcements(self) -> str:
        """Load announcements from YAML."""
        return load_announcements(self.template_dir)

    def load_footer(self) -> str:
        """Load footer template from file."""
        footer_path = os.path.join(self.template_dir, "footer.template.md")
        try:
            with open(footer_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Warning: Footer template not found at {footer_path}")
            return ""

    def build_general_anchor_map(self) -> dict:
        """Build anchor map for General subcategories."""
        return build_general_anchor_map(self.categories, self.csv_data)

    def create_backup(self, output_path: str) -> str | None:
        """Create backup of existing file."""
        return create_backup(output_path)

    def generate(self, output_path: str | None = None) -> tuple[int, str | None]:
        """Generate the README to the default or provided output path."""
        resolved_path = output_path or self.resolved_output_path
        output_path = os.path.join(self.repo_root, resolved_path)
        self.overrides = self.load_overrides()
        self.csv_data = self.load_csv_data()
        self.categories = self.load_categories()
        self.announcements = self.load_announcements()
        self.footer = self.load_footer()
        self.general_anchor_map = self.build_general_anchor_map()

        template_path = os.path.join(self.template_dir, self.template_filename)
        template = load_template(template_path)

        toc_content = self.generate_toc()
        weekly_section = self.generate_weekly_section()

        body_sections = []
        for section_index, category in enumerate(self.categories):
            section_content = self.generate_section_content(category, section_index)
            body_sections.append(section_content)

        readme_content = template
        readme_content = readme_content.replace("{{ANNOUNCEMENTS}}", self.announcements)
        readme_content = readme_content.replace("{{WEEKLY_SECTION}}", weekly_section)
        readme_content = readme_content.replace("{{TABLE_OF_CONTENTS}}", toc_content)
        readme_content = readme_content.replace(
            "{{BODY_SECTIONS}}", "\n<br>\n\n".join(body_sections)
        )
        readme_content = readme_content.replace("{{FOOTER}}", self.footer)
        readme_content = readme_content.replace(
            "{{STYLE_SELECTOR}}", self.get_style_selector(Path(output_path))
        )
        readme_content = readme_content.replace("{{REPO_TICKER}}", self.generate_repo_ticker())
        readme_content = readme_content.replace(
            "{{BANNER_IMAGE}}", self.generate_banner_image(Path(output_path))
        )

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
                print(f"❌ Error writing {resolved_path}: {e}")
                print(f"   Backup preserved at: {backup_path}")
            raise

        return len(self.csv_data), backup_path

    @property
    def alternative_output_path(self) -> str:
        """Return the output path for this style under README_ALTERNATIVES/."""
        if self.output_filename == "README.md":
            return f"README_ALTERNATIVES/README_{self.style_id.upper()}.md"
        return self.output_filename
