#!/usr/bin/env python3
"""Tests for generating alternative README outputs for root styles."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.readme.generators.base import ReadmeGenerator  # noqa: E402
from scripts.readme.helpers import readme_config  # noqa: E402
from scripts.readme.helpers.readme_paths import resolve_asset_tokens  # noqa: E402
from scripts.readme.markup import visual as visual_markup  # noqa: E402


class DummyReadmeGenerator(ReadmeGenerator):
    """Minimal generator for output path tests."""

    def __init__(
        self,
        csv_path: str,
        template_dir: str,
        assets_dir: str,
        repo_root: str,
        style_id: str,
        output_filename: str,
        template_filename: str,
    ) -> None:
        super().__init__(csv_path, template_dir, assets_dir, repo_root)
        self._style_id = style_id
        self._output_filename = output_filename
        self._template_filename = template_filename

    @property
    def template_filename(self) -> str:
        return self._template_filename

    @property
    def output_filename(self) -> str:
        return self._output_filename

    @property
    def style_id(self) -> str:
        return self._style_id

    def load_csv_data(self) -> list[dict]:
        return []

    def load_categories(self) -> list[dict]:
        return []

    def load_overrides(self) -> dict:
        return {}

    def load_announcements(self) -> str:
        return ""

    def load_footer(self) -> str:
        return ""

    def build_general_anchor_map(self) -> dict:
        return {}

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        _ = row, include_separator
        return ""

    def generate_toc(self) -> str:
        return ""

    def generate_weekly_section(self) -> str:
        return ""

    def generate_section_content(self, category: dict, section_index: int) -> str:
        _ = category, section_index
        return ""


def _write_template(template_dir: Path, filename: str) -> None:
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / filename).write_text(
        "{{STYLE_SELECTOR}}\n<img src=\"{{ASSET_PATH('logo.svg')}}\">",
        encoding="utf-8",
    )


def _write_pyproject(repo_root: Path) -> None:
    (repo_root / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")


def _configure_styles(monkeypatch: pytest.MonkeyPatch, root_style: str) -> None:
    monkeypatch.setitem(readme_config.CONFIG, "readme", {"root_style": root_style})
    monkeypatch.setitem(
        readme_config.CONFIG,
        "styles",
        {
            "extra": {
                "name": "Extra",
                "badge": "badge-style-extra.svg",
                "highlight_color": "#000000",
                "filename": "README_EXTRA.md",
            },
            "classic": {
                "name": "Classic",
                "badge": "badge-style-classic.svg",
                "highlight_color": "#000000",
                "filename": "README_CLASSIC.md",
            },
        },
    )
    monkeypatch.setitem(readme_config.CONFIG, "style_order", ["extra", "classic"])


def test_root_classic_creates_alternative_copy(tmp_path: Path, monkeypatch) -> None:
    _configure_styles(monkeypatch, root_style="classic")
    _write_pyproject(tmp_path)

    template_dir = tmp_path / "templates"
    _write_template(template_dir, "README_CLASSIC.template.md")
    (tmp_path / "assets").mkdir()

    generator = DummyReadmeGenerator(
        csv_path=str(tmp_path / "data.csv"),
        template_dir=str(template_dir),
        assets_dir=str(tmp_path / "assets"),
        repo_root=str(tmp_path),
        style_id="classic",
        output_filename="README_ALTERNATIVES/README_CLASSIC.md",
        template_filename="README_CLASSIC.template.md",
    )

    generator.generate()
    generator.generate(output_path="README.md")

    root_readme = tmp_path / "README.md"
    alt_readme = tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md"

    assert root_readme.exists()
    assert alt_readme.exists()

    root_content = root_readme.read_text(encoding="utf-8")
    alt_content = alt_readme.read_text(encoding="utf-8")

    assert 'src="assets/' in root_content
    assert 'src="../assets/' not in root_content
    assert 'src="../assets/' in alt_content


def test_root_extra_creates_alternative_copy(tmp_path: Path, monkeypatch) -> None:
    _configure_styles(monkeypatch, root_style="extra")
    _write_pyproject(tmp_path)

    template_dir = tmp_path / "templates"
    _write_template(template_dir, "README_EXTRA.template.md")
    (tmp_path / "assets").mkdir()

    generator = DummyReadmeGenerator(
        csv_path=str(tmp_path / "data.csv"),
        template_dir=str(template_dir),
        assets_dir=str(tmp_path / "assets"),
        repo_root=str(tmp_path),
        style_id="extra",
        output_filename="README_ALTERNATIVES/README_EXTRA.md",
        template_filename="README_EXTRA.template.md",
    )

    generator.generate()
    generator.generate(output_path="README.md")

    root_readme = tmp_path / "README.md"
    alt_readme = tmp_path / "README_ALTERNATIVES" / "README_EXTRA.md"

    assert root_readme.exists()
    assert alt_readme.exists()

    root_content = root_readme.read_text(encoding="utf-8")
    alt_content = alt_readme.read_text(encoding="utf-8")

    assert 'src="assets/' in root_content
    assert 'src="../assets/' not in root_content
    assert 'src="../assets/' in alt_content


def test_visual_weekly_section_uses_asset_prefix(tmp_path: Path) -> None:
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()

    csv_data = [
        {
            "Display Name": "Test Resource",
            "Primary Link": "https://github.com/example/repo",
            "Author Name": "Author",
            "Description": "Description",
            "Removed From Origin": "FALSE",
            "Date Added": "2025-01-01",
        }
    ]

    output = visual_markup.generate_weekly_section(csv_data, assets_dir=str(assets_dir))
    resolved = resolve_asset_tokens(
        output,
        tmp_path / "README_ALTERNATIVES" / "README_EXTRA.md",
        tmp_path,
    )

    assert 'src="../assets/' in resolved
    assert 'srcset="../assets/' in resolved
    assert 'src="assets/' not in resolved
    assert 'srcset="assets/' not in resolved
