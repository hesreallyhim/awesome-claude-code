#!/usr/bin/env python3
"""Tests for minimal and visual README generators."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.readme.generators import minimal as minimal_module  # noqa: E402
from scripts.readme.generators import visual as visual_module  # noqa: E402
from scripts.readme.generators.minimal import MinimalReadmeGenerator  # noqa: E402
from scripts.readme.generators.visual import VisualReadmeGenerator  # noqa: E402


def test_minimal_generator_properties() -> None:
    generator = MinimalReadmeGenerator("csv", "templates", "assets", "repo")
    assert generator.template_filename == "README_CLASSIC.template.md"
    assert generator.output_filename == "README_ALTERNATIVES/README_CLASSIC.md"
    assert generator.style_id == "classic"


def test_minimal_generator_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    generator = MinimalReadmeGenerator("csv", "templates", "assets", "repo")
    generator.categories = [{"id": "cat"}]
    generator.csv_data = [{"Display Name": "Item"}]

    calls: dict[str, object] = {}

    def fake_format(row: dict, include_separator: bool = True) -> str:
        calls["format"] = (row, include_separator)
        return "ENTRY"

    def fake_toc(categories: list[dict], csv_data: list[dict]) -> str:
        calls["toc"] = (categories, csv_data)
        return "TOC"

    def fake_weekly(csv_data: list[dict]) -> str:
        calls["weekly"] = (csv_data,)
        return "WEEKLY"

    def fake_section(category: dict, csv_data: list[dict]) -> str:
        calls["section"] = (category, csv_data)
        return "SECTION"

    monkeypatch.setattr(minimal_module, "format_minimal_resource_entry", fake_format)
    monkeypatch.setattr(minimal_module, "generate_minimal_toc", fake_toc)
    monkeypatch.setattr(minimal_module, "generate_minimal_weekly_section", fake_weekly)
    monkeypatch.setattr(minimal_module, "generate_minimal_section_content", fake_section)

    assert generator.format_resource_entry({"id": 1}, include_separator=False) == "ENTRY"
    assert calls["format"] == ({"id": 1}, False)

    assert generator.generate_toc() == "TOC"
    assert calls["toc"] == (generator.categories, generator.csv_data)

    assert generator.generate_weekly_section() == "WEEKLY"
    assert calls["weekly"] == (generator.csv_data,)

    assert generator.generate_section_content({"id": "cat"}, section_index=3) == "SECTION"
    assert calls["section"] == ({"id": "cat"}, generator.csv_data)


def test_visual_generator_properties() -> None:
    generator = VisualReadmeGenerator("csv", "templates", "assets", "repo")
    assert generator.template_filename == "README_EXTRA.template.md"
    assert generator.output_filename == "README_ALTERNATIVES/README_EXTRA.md"
    assert generator.style_id == "extra"


def test_visual_generator_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    generator = VisualReadmeGenerator("csv", "templates", "assets", "repo")
    generator.categories = [{"id": "cat"}]
    generator.csv_data = [{"Display Name": "Item"}]
    generator.general_anchor_map = {"General": "general"}
    generator.assets_dir = "/assets"

    calls: dict[str, object] = {}

    def fake_format(row: dict, assets_dir: str, include_separator: bool = True) -> str:
        calls["format"] = (row, assets_dir, include_separator)
        return "ENTRY"

    def fake_toc(categories: list[dict], csv_data: list[dict], anchor_map: dict) -> str:
        calls["toc"] = (categories, csv_data, anchor_map)
        return "TOC"

    def fake_weekly(csv_data: list[dict], assets_dir: str) -> str:
        calls["weekly"] = (csv_data, assets_dir)
        return "WEEKLY"

    def fake_section(
        category: dict,
        csv_data: list[dict],
        anchor_map: dict,
        assets_dir: str,
        section_index: int,
    ) -> str:
        calls["section"] = (category, csv_data, anchor_map, assets_dir, section_index)
        return "SECTION"

    def fake_ticker() -> str:
        calls["ticker"] = True
        return "TICKER"

    monkeypatch.setattr(visual_module, "format_visual_resource_entry", fake_format)
    monkeypatch.setattr(visual_module, "generate_visual_toc", fake_toc)
    monkeypatch.setattr(visual_module, "generate_visual_weekly_section", fake_weekly)
    monkeypatch.setattr(visual_module, "generate_visual_section_content", fake_section)
    monkeypatch.setattr(visual_module, "generate_visual_repo_ticker", fake_ticker)

    assert generator.format_resource_entry({"id": 1}, include_separator=False) == "ENTRY"
    assert calls["format"] == ({"id": 1}, "/assets", False)

    assert generator.generate_toc() == "TOC"
    assert calls["toc"] == (generator.categories, generator.csv_data, generator.general_anchor_map)

    assert generator.generate_weekly_section() == "WEEKLY"
    assert calls["weekly"] == (generator.csv_data, "/assets")

    assert generator.generate_section_content({"id": "cat"}, section_index=2) == "SECTION"
    assert calls["section"] == (
        {"id": "cat"},
        generator.csv_data,
        generator.general_anchor_map,
        "/assets",
        2,
    )

    assert generator.generate_repo_ticker() == "TICKER"
    assert calls["ticker"] is True
