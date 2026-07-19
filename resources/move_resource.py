#!/usr/bin/env python3
"""Re-file an existing resource: change its Category and Sub-Category in place.

Identifies the row by --id or --link, validates the target Category against
config.yaml (fail-closed, the same invariant generate_readme.py enforces), and
rewrites only that one CSV line — every other row stays byte-for-byte untouched, and
the moved row keeps its ID, dates, description, and all other columns. Moving to a new
category clears the Sub-Category unless a new --subcategory is given (an old
sub-category rarely belongs under a new parent). Rendering README.md is
generate_readme.py's job; the `make move-resource` target chains the two. Use
--dry-run to preview without writing.

Usage:
    move_resource.py (--id ID | --link URL) --category "New Category" \
        [--subcategory "Sub"] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from resources.categories import category_names  # noqa: E402
from resources.resource_utils import (  # noqa: E402
    COL_CATEGORY,
    COL_DISPLAY,
    COL_SUBCATEGORY,
    find_row_indices,
    read_lines,
    serialize_row,
    split_eol,
    write_lines,
)

CONFIG_PATH = BASE / "config.yaml"


def subcategories_for(category: str) -> list[str]:
    """Declared sub-category names under `category` in config.yaml (may be empty)."""
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    for c in data.get("categories") or []:
        if isinstance(c, dict) and c.get("name") == category:
            return [
                s["name"]
                for s in (c.get("subcategories") or [])
                if isinstance(s, dict) and s.get("name")
            ]
    return []


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sel = p.add_mutually_exclusive_group(required=True)
    sel.add_argument("--id", help="Resource ID to move.")
    sel.add_argument("--link", help="Resource Link to move (alternative to --id).")
    p.add_argument("--category", required=True, help="Target Category (must exist in config.yaml).")
    p.add_argument("--subcategory", default="", help="Target Sub-Category (default: cleared).")
    p.add_argument("--dry-run", action="store_true", help="Print the change without writing.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    known = category_names()
    if args.category not in known:
        print(
            f"ERROR: category {args.category!r} is not declared in config.yaml.\n"
            "Add it first (`make add-category`) or fix the name.",
            file=sys.stderr,
        )
        print(f"Known categories: {', '.join(known)}", file=sys.stderr)
        return 1

    if args.subcategory and args.subcategory not in subcategories_for(args.category):
        print(
            f"note: sub-category {args.subcategory!r} is not declared under "
            f"{args.category!r} in config.yaml; it will still render, but to fix its "
            f"order run: make add-category CATEGORY={args.category!r} "
            f"SUB_CATEGORY={args.subcategory!r}",
            file=sys.stderr,
        )

    lines = read_lines()
    selector = f"id {args.id!r}" if args.id else f"link {args.link!r}"
    try:
        matches = find_row_indices(lines, id=args.id or "", link=args.link or "")
    except ValueError as e:
        print(f"ERROR: {e}. Refusing to edit — handle it manually.", file=sys.stderr)
        return 1

    if not matches:
        print(f"ERROR: no resource found with {selector}.", file=sys.stderr)
        return 1
    if len(matches) > 1:
        print(f"ERROR: {len(matches)} rows match {selector}; refusing to move an ambiguous set.", file=sys.stderr)
        return 1

    idx = matches[0]
    content, eol = split_eol(lines[idx])
    fields = next(csv.reader([content]))
    old = (fields[COL_CATEGORY], fields[COL_SUBCATEGORY])
    new = (args.category, args.subcategory)
    display = fields[COL_DISPLAY]

    def _fmt(cat: str, sub: str) -> str:
        return cat + (f" / {sub}" if sub else "")

    if old == new:
        print(f"note: {display!r} is already in {_fmt(*new)}; nothing to do.")
        return 0

    if args.dry_run:
        print(f"[dry-run] {display!r}: {_fmt(*old)}  ->  {_fmt(*new)}")
        return 0

    fields[COL_CATEGORY], fields[COL_SUBCATEGORY] = args.category, args.subcategory
    lines[idx] = serialize_row(fields, eol)
    write_lines(lines)

    print(f"Moved {display!r}: {_fmt(*old)}  ->  {_fmt(*new)} in THE_RESOURCES_TABLE_NEW.csv.")
    print("Run `make generate` (chained by the make move-resource target) to update README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
