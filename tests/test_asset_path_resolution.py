#!/usr/bin/env python3
"""Tests for asset token resolution behavior."""

from pathlib import Path

from scripts.readme.helpers.readme_paths import (
    asset_path_token,
    ensure_generated_header,
    resolve_asset_tokens,
)


def test_resolve_asset_tokens_root(tmp_path: Path) -> None:
    content = f'<img src="{asset_path_token("logo.svg")}">'
    resolved = resolve_asset_tokens(content, tmp_path / "README.md", tmp_path)
    assert 'src="assets/logo.svg"' in resolved


def test_resolve_asset_tokens_alternative(tmp_path: Path) -> None:
    content = f'<img src="{asset_path_token("logo.svg")}">'
    resolved = resolve_asset_tokens(
        content, tmp_path / "README_ALTERNATIVES" / "README_EXTRA.md", tmp_path
    )
    assert 'src="../assets/logo.svg"' in resolved


def test_resolve_asset_tokens_asset_scheme(tmp_path: Path) -> None:
    content = '<img src="asset:badge.svg">'
    resolved = resolve_asset_tokens(content, tmp_path / "README.md", tmp_path)
    assert 'src="assets/badge.svg"' in resolved


def test_ensure_generated_header() -> None:
    content = "Hello\n"
    updated = ensure_generated_header(content)
    assert updated.startswith("<!-- GENERATED FILE: do not edit directly -->\n")
