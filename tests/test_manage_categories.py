"""Coverage for scripts/manage_categories.py — the config.yaml category editor.

The pure edit functions operate on config.yaml *text* and must (a) land entries at
the requested 1-based position, (b) keep the file valid YAML, and (c) preserve the
header comment block (the reason edits are text splices, not yaml.dump round-trips).
The issue-form sync re-emits the dropdown in config order while preserving its
(subset) membership.

Run:  venv/bin/python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from scripts import manage_categories as mc  # noqa: E402

SAMPLE = """\
# header comment that must survive
# schema notes ...
categories:
  - name: "Alpha"
    prefix: alpha
  - name: "Beta"
    prefix: beta
  - name: "Gamma"
    prefix: gamma
"""

WITH_SUBS = """\
# header
categories:
  - name: "Alpha"
    prefix: alpha
    subcategories:
      - name: "One"
      - name: "Two"
      - name: "Three"
  - name: "Beta"
    prefix: beta
"""


def _names(text: str) -> list[str]:
    return [c["name"] for c in yaml.safe_load(text)["categories"]]


def _subs(text: str, category: str) -> list[str]:
    cat = next(c for c in yaml.safe_load(text)["categories"] if c["name"] == category)
    return [s["name"] for s in (cat.get("subcategories") or [])]


# --------------------------------------------------------------------------- #
# Add — categories
# --------------------------------------------------------------------------- #
def test_add_category_appends_when_order_omitted() -> None:
    assert _names(mc.insert_category(SAMPLE, "Delta", "delta", None, None)) == [
        "Alpha",
        "Beta",
        "Gamma",
        "Delta",
    ]


def test_add_category_at_order() -> None:
    assert _names(mc.insert_category(SAMPLE, "Delta", "delta", None, 2)) == [
        "Alpha",
        "Delta",
        "Beta",
        "Gamma",
    ]


def test_add_category_preserves_header() -> None:
    out = mc.insert_category(SAMPLE, "Delta", "delta", None, 1)
    assert out.startswith("# header comment that must survive")


def test_add_category_with_description() -> None:
    out = mc.insert_category(SAMPLE, "Delta", "delta", "A blurb.", None)
    delta = next(c for c in yaml.safe_load(out)["categories"] if c["name"] == "Delta")
    assert delta["description"] == "A blurb."


def test_add_duplicate_name_rejected() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.insert_category(SAMPLE, "Beta", "beta2", None, None)


def test_add_duplicate_prefix_rejected() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.insert_category(SAMPLE, "Brand New", "beta", None, None)


# --------------------------------------------------------------------------- #
# Move — categories (ORDER == final 1-based position)
# --------------------------------------------------------------------------- #
def test_move_category_forward() -> None:
    assert _names(mc.move_category(SAMPLE, "Alpha", 3)) == ["Beta", "Gamma", "Alpha"]


def test_move_category_backward() -> None:
    assert _names(mc.move_category(SAMPLE, "Gamma", 1)) == ["Gamma", "Alpha", "Beta"]


def test_move_category_same_position_is_noop() -> None:
    assert mc.move_category(SAMPLE, "Beta", 2) == SAMPLE


def test_move_category_carries_its_block() -> None:
    out = mc.move_category(WITH_SUBS, "Alpha", 2)
    assert _names(out) == ["Beta", "Alpha"]
    assert _subs(out, "Alpha") == ["One", "Two", "Three"]  # subcategories moved too


def test_move_missing_category_rejected() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.move_category(SAMPLE, "Nope", 1)


# --------------------------------------------------------------------------- #
# Remove — categories
# --------------------------------------------------------------------------- #
def test_remove_category() -> None:
    assert _names(mc.remove_category(SAMPLE, "Beta")) == ["Alpha", "Gamma"]


def test_remove_category_with_subs() -> None:
    out = mc.remove_category(WITH_SUBS, "Alpha")
    assert _names(out) == ["Beta"]


def test_remove_missing_category_rejected() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.remove_category(SAMPLE, "Nope")


# --------------------------------------------------------------------------- #
# Sub-categories: add / move / remove
# --------------------------------------------------------------------------- #
def test_add_subcategory_creates_key_when_absent() -> None:
    out = mc.insert_subcategory(SAMPLE, "Beta", "Sub One", None, None)
    assert _subs(out, "Beta") == ["Sub One"]
    assert _names(out) == ["Alpha", "Beta", "Gamma"]  # siblings untouched


def test_add_subcategory_at_order() -> None:
    out = mc.insert_subcategory(WITH_SUBS, "Alpha", "Mid", None, 2)
    assert _subs(out, "Alpha") == ["One", "Mid", "Two", "Three"]


def test_add_duplicate_subcategory_rejected() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.insert_subcategory(WITH_SUBS, "Alpha", "Two", None, None)


def test_move_subcategory() -> None:
    out = mc.move_subcategory(WITH_SUBS, "Alpha", "Three", 1)
    assert _subs(out, "Alpha") == ["Three", "One", "Two"]


def test_remove_subcategory() -> None:
    out = mc.remove_subcategory(WITH_SUBS, "Alpha", "Two")
    assert _subs(out, "Alpha") == ["One", "Three"]


def test_remove_last_subcategory_drops_the_key() -> None:
    text = WITH_SUBS
    for name in ("One", "Two", "Three"):
        text = mc.remove_subcategory(text, "Alpha", name)
    assert _subs(text, "Alpha") == []
    assert "subcategories:" not in text  # empty key removed
    assert yaml.safe_load(text)["categories"][0]["name"] == "Alpha"  # still valid


def test_move_subcategory_missing_rejected() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.move_subcategory(WITH_SUBS, "Beta", "Nope", 1)


# --------------------------------------------------------------------------- #
# Issue-form dropdown sync (config-driven via `submittable`)
# --------------------------------------------------------------------------- #
FORM = """\
name: Recommend a Resource
body:
  - type: dropdown
    id: category
    attributes:
      label: Category
      options:
        - "Old A"
        - "Old B"
    validations:
      required: true
"""

# Beta is curated-only (submittable: false); Delta is a normal submittable category.
FORM_CONFIG = """\
categories:
  - name: "Alpha"
  - name: "Beta"
    submittable: false
  - name: "Gamma"
  - name: "Delta"
"""


def test_render_form_lists_submittable_in_config_order() -> None:
    out = mc.render_form(FORM, FORM_CONFIG)
    # config drives membership entirely: prior options are replaced, Beta excluded.
    assert mc.current_form_options(out) == ["Alpha", "Gamma", "Delta"]


def test_render_form_preserves_item_indentation() -> None:
    out = mc.render_form(FORM, FORM_CONFIG)
    assert '        - "Alpha"' in out  # 8-space item indent read from the form


def test_render_form_reorders_to_config_order() -> None:
    reordered = 'categories:\n  - name: "Delta"\n  - name: "Alpha"\n'
    assert mc.current_form_options(mc.render_form(FORM, reordered)) == [
        "Delta",
        "Alpha",
    ]


def test_render_form_missing_dropdown_raises() -> None:
    with pytest.raises(mc.ConfigEditError):
        mc.render_form("name: X\nbody: []\n", FORM_CONFIG)


def test_submittable_categories_excludes_flagged() -> None:
    assert mc.submittable_categories(FORM_CONFIG) == ["Alpha", "Gamma", "Delta"]


def test_add_not_submittable_writes_flag() -> None:
    out = mc.insert_category(FORM_CONFIG, "Zed", "zed", None, None, submittable=False)
    zed = next(c for c in yaml.safe_load(out)["categories"] if c["name"] == "Zed")
    assert zed["submittable"] is False


def test_live_issue_form_is_in_sync_with_config() -> None:
    """Drift guard: the committed dropdown must equal render_form(config)."""
    form_text = mc.ISSUE_FORM_PATH.read_text(encoding="utf-8")
    config_text = mc.CONFIG_PATH.read_text(encoding="utf-8")
    assert mc.render_form(form_text, config_text) == form_text


# --------------------------------------------------------------------------- #
# Helpers / live config
# --------------------------------------------------------------------------- #
def test_slugify_prefix() -> None:
    assert mc.slugify_prefix("Testing & QA") == "testing"
    assert mc.slugify_prefix("Design & UI/UX") == "design"


def test_live_config_roundtrips_through_edits() -> None:
    """Add then remove on the real config.yaml returns identical text."""
    text = mc.CONFIG_PATH.read_text(encoding="utf-8")
    added = mc.insert_category(text, "Zzz Temp", "zzztemp", None, 5)
    assert yaml.safe_load(added)["categories"][4]["name"] == "Zzz Temp"
    restored = mc.remove_category(added, "Zzz Temp")
    assert restored == text
