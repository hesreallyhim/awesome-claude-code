"""Category lookups backed by config.yaml (the single source of truth).

config.yaml is also consumed by generate_readme.py for ordering; here we read the
category names (for validation) and per-category `prefix` (for resource IDs).
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config.yaml"


def _categories() -> list[dict]:
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    return [c for c in (data.get("categories") or []) if isinstance(c, dict) and c.get("name")]


def category_names() -> list[str]:
    return [c["name"] for c in _categories()]


def category_prefixes() -> dict[str, str]:
    """Map category name -> ID prefix (default 'res' if unset)."""
    return {c["name"]: c.get("prefix", "res") for c in _categories()}
