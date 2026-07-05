#!/usr/bin/env python3
"""Add, move, or remove a category / sub-category in config.yaml.

config.yaml is the single source of truth for category / sub-category ordering
(list order == render order). This script edits that file with targeted text
splicing so its header comments and formatting survive (a yaml.safe_load ->
yaml.dump round-trip would discard them).

Category edits also keep the recommend-resource issue-form Category dropdown
(.github/ISSUE_TEMPLATE/recommend-resource.yml) in sync. That dropdown is fully
derived from config.yaml: every `submittable` category, in config order (curated-only
sections like "From Anthropic" set `submittable: false`). The same rendering runs in
pre-commit via scripts/sync_issue_form.py. Pass --skip-issue-form to opt out here.

Regenerating README.md (Table of Contents, headings) is done afterwards by
`generate_readme.py`; the `make {add,move,remove}-category` targets chain the
steps so each operation is one command.

Usage:
    manage_categories.py add    --category "Testing & QA" --prefix testing [--order N]
    manage_categories.py add    --category Security --subcategory "Secrets Scanning" --order 2
    manage_categories.py move   --category "Meta-Skills" --order 15
    manage_categories.py remove --category "Linting"
    manage_categories.py remove --category Security --subcategory "Secrets Scanning"

ORDER is the 1-based position the entry should occupy in the resulting list
(among categories, or among a category's sub-categories). For `add` it may be
omitted to append; for `move` it is required.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

import yaml

BASE = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE / "config.yaml"
CSV_PATH = BASE / "THE_RESOURCES_TABLE_NEW.csv"
ISSUE_FORM_PATH = BASE / ".github" / "ISSUE_TEMPLATE" / "recommend-resource.yml"

# Line classifiers (indentation is significant in the config.yaml schema):
#   "categories:"            top-level key,  col 0
#   "  - name: ..."          category item,  dash at col 2, keys at col 4
#   "    subcategories:"     category key,   col 4
#   "      - name: ..."      sub item,       dash at col 6, keys at col 8
CATEGORIES_KEY_RE = re.compile(r"^categories:\s*$")
CAT_ITEM_RE = re.compile(r"^  - ")
CAT_NAME_RE = re.compile(r"^  - name:\s*(.+?)\s*$")
SUBCATS_KEY_RE = re.compile(r"^    subcategories:\s*$")
SUB_ITEM_RE = re.compile(r"^      - ")
SUB_NAME_RE = re.compile(r"^      - name:\s*(.+?)\s*$")
TOPLEVEL_RE = re.compile(r"^\S")  # any non-indented, non-blank line ends the list


class ConfigEditError(Exception):
    """Raised for user-facing problems (duplicate name, missing category, ...)."""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def slugify_prefix(name: str) -> str:
    """Derive a default id prefix from a category name (first alphanumeric word)."""
    words = re.findall(r"[A-Za-z0-9]+", name.lower())
    return words[0] if words else "cat"


def _yq(value: str) -> str:
    """Double-quote a scalar for YAML, escaping backslashes and quotes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _unquote(value: str) -> str:
    """Strip surrounding single/double quotes from a parsed YAML scalar token."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_structure(text: str) -> dict[str, Any]:
    """Parse config.yaml text into its data structure (for validation only)."""
    return yaml.safe_load(text) or {}


def existing_categories(text: str) -> list[dict[str, Any]]:
    data = load_structure(text)
    return [c for c in (data.get("categories") or []) if isinstance(c, dict)]


def active_resource_count(category: str) -> int:
    """Count Active CSV rows in `category` (used to guard category removal)."""
    if not CSV_PATH.exists():
        return 0
    with CSV_PATH.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return sum(
        1
        for r in rows
        if (r.get("Active") or "").strip().upper() == "TRUE"
        and (r.get("Category") or "").strip() == category
    )


# --------------------------------------------------------------------------- #
# Line-region utilities
# --------------------------------------------------------------------------- #
def _category_start_indices(lines: list[str]) -> list[int]:
    """Line indices where each top-level category item begins."""
    try:
        key_idx = next(i for i, ln in enumerate(lines) if CATEGORIES_KEY_RE.match(ln))
    except StopIteration as exc:  # pragma: no cover - config.yaml always has this
        raise ConfigEditError("config.yaml has no top-level 'categories:' key") from exc
    starts: list[int] = []
    for i in range(key_idx + 1, len(lines)):
        if TOPLEVEL_RE.match(lines[i]):  # dedented back to col 0 -> list is over
            break
        if CAT_ITEM_RE.match(lines[i]):
            starts.append(i)
    return starts


def _block_end(lines: list[str], start: int, sibling_starts: list[int]) -> int:
    """Exclusive end of the block beginning at `start`.

    The block runs until the next sibling item, the next dedent to col 0, or EOF,
    with any trailing blank lines excluded so insertions land against real content.
    """
    later = [s for s in sibling_starts if s > start]
    end = later[0] if later else len(lines)
    if not later:
        for i in range(start + 1, len(lines)):
            if TOPLEVEL_RE.match(lines[i]):
                end = i
                break
    while end > start + 1 and lines[end - 1].strip() == "":
        end -= 1
    return end


def _ensure_trailing_newline(lines: list[str], at: int) -> None:
    """Guarantee the line before an append-at-EOF insertion ends in a newline."""
    if at == len(lines) and lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"


def _find_category(lines: list[str], name: str) -> int:
    """Return the start-line index of category `name`, or raise ConfigEditError."""
    for s in _category_start_indices(lines):
        m = CAT_NAME_RE.match(lines[s])
        if m and _unquote(m.group(1)) == name:
            return s
    raise ConfigEditError(f"category {name!r} not found in config.yaml")


def _sub_item_starts(lines: list[str], subcats_idx: int, cend: int) -> list[int]:
    return [i for i in range(subcats_idx + 1, cend) if SUB_ITEM_RE.match(lines[i])]


def _insertion_point(starts: list[int], order: int | None, end_fallback: int) -> int:
    """Line at which to insert so the entry lands at 1-based `order`."""
    if order is not None and 1 <= order <= len(starts):
        return starts[order - 1]
    return end_fallback


# --------------------------------------------------------------------------- #
# Category edits
# --------------------------------------------------------------------------- #
def insert_category(
    text: str,
    name: str,
    prefix: str,
    description: str | None,
    order: int | None,
    submittable: bool = True,
) -> str:
    """Return config.yaml text with a new category spliced in at `order`."""
    for cat in existing_categories(text):
        if cat.get("name") == name:
            raise ConfigEditError(f"category {name!r} already exists in config.yaml")
        if cat.get("prefix") == prefix:
            raise ConfigEditError(
                f"prefix {prefix!r} is already used by {cat.get('name')!r}; "
                "pass a different PREFIX"
            )

    lines = text.splitlines(keepends=True)
    starts = _category_start_indices(lines)
    block = [f"  - name: {_yq(name)}\n", f"    prefix: {prefix}\n"]
    if description:
        block.append(f"    description: {_yq(description)}\n")
    if not submittable:
        block.append("    submittable: false\n")

    fallback = _block_end(lines, starts[-1], starts) if starts else len(lines)
    at = _insertion_point(starts, order, fallback)
    _ensure_trailing_newline(lines, at)
    lines[at:at] = block
    return "".join(lines)


def move_category(text: str, name: str, order: int | None) -> str:
    """Return config.yaml text with category `name` relocated to `order`."""
    lines = text.splitlines(keepends=True)
    idx = _find_category(lines, name)
    end = _block_end(lines, idx, _category_start_indices(lines))
    block = lines[idx:end]
    del lines[idx:end]

    starts = _category_start_indices(lines)
    fallback = _block_end(lines, starts[-1], starts) if starts else len(lines)
    at = _insertion_point(starts, order, fallback)
    _ensure_trailing_newline(lines, at)
    lines[at:at] = block
    return "".join(lines)


def remove_category(text: str, name: str) -> str:
    """Return config.yaml text with category `name` (and its block) removed."""
    lines = text.splitlines(keepends=True)
    idx = _find_category(lines, name)
    end = _block_end(lines, idx, _category_start_indices(lines))
    del lines[idx:end]
    return "".join(lines)


# --------------------------------------------------------------------------- #
# Sub-category edits
# --------------------------------------------------------------------------- #
def insert_subcategory(
    text: str, category: str, sub_name: str, description: str | None, order: int | None
) -> str:
    """Return config.yaml text with a new sub-category added under `category`."""
    lines = text.splitlines(keepends=True)
    cat_idx = _find_category(lines, category)
    cend = _block_end(lines, cat_idx, _category_start_indices(lines))

    for i in range(cat_idx + 1, cend):
        m = SUB_NAME_RE.match(lines[i])
        if m and _unquote(m.group(1)) == sub_name:
            raise ConfigEditError(
                f"sub-category {sub_name!r} already exists under {category!r}"
            )

    sub_block = [f"      - name: {_yq(sub_name)}\n"]
    if description:
        sub_block.append(f"        description: {_yq(description)}\n")

    subcats_idx = next(
        (i for i in range(cat_idx + 1, cend) if SUBCATS_KEY_RE.match(lines[i])), None
    )
    if subcats_idx is None:
        _ensure_trailing_newline(lines, cend)
        lines[cend:cend] = ["    subcategories:\n", *sub_block]
        return "".join(lines)

    sub_starts = _sub_item_starts(lines, subcats_idx, cend)
    fallback = _block_end(
        lines, subcats_idx, [subcats_idx, *_category_start_indices(lines)]
    )
    at = _insertion_point(sub_starts, order, fallback if sub_starts else cend)
    _ensure_trailing_newline(lines, at)
    lines[at:at] = sub_block
    return "".join(lines)


def _locate_subcategory(
    lines: list[str], category: str, sub_name: str
) -> tuple[int, int, int, int]:
    """Return (subcats_idx, cend, sub_start, sub_end) for a sub-category, or raise."""
    cat_idx = _find_category(lines, category)
    cend = _block_end(lines, cat_idx, _category_start_indices(lines))
    subcats_idx = next(
        (i for i in range(cat_idx + 1, cend) if SUBCATS_KEY_RE.match(lines[i])), None
    )
    if subcats_idx is None:
        raise ConfigEditError(f"category {category!r} has no sub-categories")
    sub_starts = _sub_item_starts(lines, subcats_idx, cend)
    for pos, s in enumerate(sub_starts):
        m = SUB_NAME_RE.match(lines[s])
        if m and _unquote(m.group(1)) == sub_name:
            sub_end = sub_starts[pos + 1] if pos + 1 < len(sub_starts) else cend
            return subcats_idx, cend, s, sub_end
    raise ConfigEditError(f"sub-category {sub_name!r} not found under {category!r}")


def move_subcategory(text: str, category: str, sub_name: str, order: int | None) -> str:
    """Return config.yaml text with `sub_name` relocated within `category`."""
    lines = text.splitlines(keepends=True)
    _, _, s, e = _locate_subcategory(lines, category, sub_name)
    block = lines[s:e]
    del lines[s:e]

    # Re-locate the subcategories region after deletion.
    cat_idx = _find_category(lines, category)
    cend = _block_end(lines, cat_idx, _category_start_indices(lines))
    subcats_idx = next(
        i for i in range(cat_idx + 1, cend) if SUBCATS_KEY_RE.match(lines[i])
    )
    sub_starts = _sub_item_starts(lines, subcats_idx, cend)
    at = _insertion_point(sub_starts, order, cend)
    _ensure_trailing_newline(lines, at)
    lines[at:at] = block
    return "".join(lines)


def remove_subcategory(text: str, category: str, sub_name: str) -> str:
    """Return config.yaml text with `sub_name` removed from `category`.

    If it was the last sub-category, the now-empty `subcategories:` key is dropped.
    """
    lines = text.splitlines(keepends=True)
    subcats_idx, _, s, e = _locate_subcategory(lines, category, sub_name)
    del lines[s:e]
    # If no sub-items remain, remove the empty `subcategories:` key line too.
    cat_idx = _find_category(lines, category)
    cend = _block_end(lines, cat_idx, _category_start_indices(lines))
    if not _sub_item_starts(lines, subcats_idx, cend):
        del lines[subcats_idx]
    return "".join(lines)


# --------------------------------------------------------------------------- #
# Issue-form dropdown sync
#
# The form is parsed as YAML to locate the Category dropdown robustly (by id), but
# only its `options:` lines are rewritten in place. A full yaml.dump round-trip is
# avoided on purpose: GitHub issue forms use irregular indentation that a uniform
# serializer would reformat wholesale, producing a huge, risky diff.
# --------------------------------------------------------------------------- #
CATEGORY_ID_RE = re.compile(r"^\s*id:\s*category\s*$")
OPTIONS_KEY_RE = re.compile(r"^(\s*)options:\s*$")
LIST_ITEM_RE = re.compile(r"^(\s*)-\s+(.+?)\s*$")


def current_form_options(form_text: str) -> list[str]:
    """The Category dropdown's current options (via YAML parse), for validation/tests."""
    data = yaml.safe_load(form_text) or {}
    for field in data.get("body", []) if isinstance(data, dict) else []:
        if (
            isinstance(field, dict)
            and field.get("id") == "category"
            and field.get("type") == "dropdown"
        ):
            opts = (field.get("attributes") or {}).get("options") or []
            return [str(o) for o in opts]
    raise ConfigEditError("issue form has no dropdown with id 'category'")


def _locate_options_lines(lines: list[str]) -> tuple[int, int, str]:
    """Return (start, end, item_indent) of the Category dropdown's option items.

    Anchored on the `id: category` line, then its following `options:` key; the
    item indentation is read from the file rather than assumed.
    """
    try:
        id_idx = next(i for i, ln in enumerate(lines) if CATEGORY_ID_RE.match(ln))
    except StopIteration as exc:
        raise ConfigEditError("issue form has no dropdown with id 'category'") from exc
    opt_idx = opt_indent = None
    for i in range(id_idx + 1, len(lines)):
        m = OPTIONS_KEY_RE.match(lines[i])
        if m:
            opt_idx, opt_indent = i, m.group(1)
            break
        if TOPLEVEL_RE.match(lines[i]):  # left this field without seeing options:
            break
    if opt_idx is None or opt_indent is None:
        raise ConfigEditError("Category dropdown has no 'options:' block")

    start = opt_idx + 1
    end = start
    item_indent: str | None = None
    while end < len(lines):
        m = LIST_ITEM_RE.match(lines[end])
        if not m or len(m.group(1)) <= len(opt_indent):
            break
        item_indent = item_indent or m.group(1)
        end += 1
    return start, end, item_indent or (opt_indent + "  ")


def submittable_categories(config_text: str) -> list[str]:
    """Category names that belong in the issue-form dropdown, in config order.

    A category is submittable unless it sets `submittable: false` (curated-only,
    e.g. "From Anthropic").
    """
    return [
        c["name"]
        for c in existing_categories(config_text)
        if c.get("submittable", True)
    ]


def render_form(form_text: str, config_text: str) -> str:
    """Return the issue form with its Category dropdown regenerated from config.

    The options become exactly the submittable categories, in config order —
    config.yaml is the single source of truth. Raises ConfigEditError if the form
    has no `id: category` dropdown.
    """
    current_form_options(form_text)  # validate structure via YAML parse
    lines = form_text.splitlines(keepends=True)
    start, end, indent = _locate_options_lines(lines)
    lines[start:end] = [
        f"{indent}- {_yq(n)}\n" for n in submittable_categories(config_text)
    ]
    return "".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="action", required=True)

    def add_common(sp: argparse.ArgumentParser, *, order_required: bool) -> None:
        sp.add_argument(
            "--category", required=True, help="Category name (heading text)."
        )
        sp.add_argument(
            "--subcategory", help="Operate on this sub-category of --category."
        )
        sp.add_argument(
            "--order",
            type=int,
            required=order_required,
            help="1-based target position among categories (or sub-categories).",
        )
        sp.add_argument(
            "--skip-issue-form",
            action="store_true",
            help="Don't touch the recommend-resource issue-form dropdown.",
        )
        sp.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the resulting config.yaml to stdout without writing.",
        )

    a = sub.add_parser("add", help="Add a category or sub-category.")
    add_common(a, order_required=False)
    a.add_argument("--prefix", help="Id prefix for a new category (default: derived).")
    a.add_argument("--description", help="Optional blurb rendered under the heading.")
    a.add_argument(
        "--not-submittable",
        action="store_true",
        help="Mark a new category curated-only (kept out of the issue-form dropdown).",
    )

    m = sub.add_parser("move", help="Move a category or sub-category to --order.")
    add_common(m, order_required=True)

    r = sub.add_parser("remove", help="Remove a category or sub-category.")
    add_common(r, order_required=False)
    r.add_argument(
        "--force",
        action="store_true",
        help="Remove a category even if Active resources still reference it.",
    )
    return p


def _apply(args: argparse.Namespace, text: str) -> tuple[str, str]:
    """Dispatch to the right edit; return (new_text, human_summary)."""
    cat, sub = args.category, args.subcategory
    if args.action == "add":
        if sub:
            if args.prefix:
                print("note: --prefix is ignored for sub-categories.", file=sys.stderr)
            return (
                insert_subcategory(text, cat, sub, args.description, args.order),
                f"sub-category {sub!r} under {cat!r}",
            )
        prefix = args.prefix or slugify_prefix(cat)
        return (
            insert_category(
                text,
                cat,
                prefix,
                args.description,
                args.order,
                submittable=not args.not_submittable,
            ),
            f"category {cat!r} (prefix {prefix!r})",
        )
    if args.action == "move":
        if sub:
            return move_subcategory(text, cat, sub, args.order), f"sub-category {sub!r}"
        return move_category(text, cat, args.order), f"category {cat!r}"
    # remove
    if sub:
        return remove_subcategory(text, cat, sub), f"sub-category {sub!r} from {cat!r}"
    if not args.force:
        n = active_resource_count(cat)
        if n:
            raise ConfigEditError(
                f"category {cat!r} still has {n} Active resource(s); reassign them "
                "or pass --force (generation fails closed on orphaned categories)"
            )
    return remove_category(text, cat), f"category {cat!r}"


def _verify(text: str, args: argparse.Namespace) -> None:
    """Re-parse the edited text and confirm the intended end-state."""
    cats = existing_categories(text)
    cat = next((c for c in cats if c.get("name") == args.category), None)
    if args.action == "remove" and not args.subcategory:
        if cat is not None:
            raise ValueError(f"{args.category!r} still present after remove")
        return
    if cat is None:
        raise ValueError(f"{args.category!r} missing after edit")
    if args.subcategory:
        subs = {
            s.get("name")
            for s in (cat.get("subcategories") or [])
            if isinstance(s, dict)
        }
        present = args.subcategory in subs
        if args.action == "remove" and present:
            raise ValueError(f"{args.subcategory!r} still present after remove")
        if args.action != "remove" and not present:
            raise ValueError(f"{args.subcategory!r} missing after edit")


def _sync_form(config_text: str) -> None:
    """Best-effort issue-form dropdown regen from config; never fatal (config is truth)."""
    if not ISSUE_FORM_PATH.exists():
        print(
            f"note: {ISSUE_FORM_PATH.name} not found; skipped form sync.",
            file=sys.stderr,
        )
        return
    form_text = ISSUE_FORM_PATH.read_text(encoding="utf-8")
    try:
        updated = render_form(form_text, config_text)
    except ConfigEditError as exc:
        print(
            f"WARNING: issue-form not synced ({exc}); fix it by hand.", file=sys.stderr
        )
        return
    if updated != form_text:
        ISSUE_FORM_PATH.write_text(updated, encoding="utf-8")
        print("Updated the recommend-resource issue-form dropdown.")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.order is not None and args.order < 1:
        print("ERROR: --order must be a positive (1-based) integer.", file=sys.stderr)
        return 2

    text = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        new_text, summary = _apply(args, text)
    except ConfigEditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        load_structure(new_text)  # must still be valid YAML
        _verify(new_text, args)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"ERROR: refusing to write invalid config.yaml ({exc}).", file=sys.stderr)
        return 1

    if args.dry_run:
        sys.stdout.write(new_text)
        return 0

    CONFIG_PATH.write_text(new_text, encoding="utf-8")
    verb = {"add": "Added", "move": "Moved", "remove": "Removed"}[args.action]
    where = "" if args.order is None else f" to position {args.order}"
    print(f"{verb} {summary}{where} in config.yaml.")

    # Only category-level edits affect the issue-form dropdown.
    if not args.subcategory and not args.skip_issue_form:
        _sync_form(new_text)

    print("Run `make generate` (chained by the make target) to update README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
