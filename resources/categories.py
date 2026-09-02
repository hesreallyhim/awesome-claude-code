"""Category lookups backed by config.yaml (the single source of truth).

config.yaml is also consumed by generate_readme.py for ordering; here we read the
category names, used to validate the Category column on add / move / submit. The
per-category `prefix` key is vestigial and deliberately not read — resource IDs are
opaque hex (see ids.py), not {prefix}-{hash}.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config.yaml"

# How a sub-category is spelled as one issue-form dropdown option. GitHub issue
# forms have no dependent dropdowns, so the two levels are flattened into a
# single list and split apart again on the way back in (see split_option and
# scripts/manage_categories.form_options). Defined here because both the
# renderer and the parser must agree on it.
CATEGORY_SEPARATOR = " > "


def _categories() -> list[dict]:
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    return [c for c in (data.get("categories") or []) if isinstance(c, dict) and c.get("name")]


def category_names() -> list[str]:
    return [c["name"] for c in _categories()]


def subcategory_names(category: str) -> list[str]:
    """Sub-category names declared under `category`, in config order.

    Empty for an unknown category, or one with no `subcategories` key. Note that
    a resource may carry a Sub-Category that is not listed here — generate_readme
    still renders it (see the config.yaml schema header) — so this is the set of
    *offered* sub-categories, not the set of legal ones.
    """
    for c in _categories():
        if c["name"] == category:
            subs = c.get("subcategories") or []
            return [s["name"] for s in subs if isinstance(s, dict) and s.get("name")]
    return []


def split_option(value: str) -> tuple[str, str]:
    """Split a dropdown option into (category, sub_category).

    "Agent Orchestration > Ralph Wiggum" -> ("Agent Orchestration", "Ralph Wiggum")
    "Security"                           -> ("Security", "")

    Only the first separator splits, so a category or sub-category whose own name
    contains " > " still round-trips as long as the category name does not.
    """
    category, separator, sub = value.partition(CATEGORY_SEPARATOR)
    if not separator:
        return value.strip(), ""
    return category.strip(), sub.strip()
