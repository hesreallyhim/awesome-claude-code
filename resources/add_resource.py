#!/usr/bin/env python3
"""Add a single resource row to THE_RESOURCES_TABLE_NEW.csv.

Mints an opaque random ID, validates the Category
against config.yaml (fail-closed, the same invariant generate_readme.py enforces),
guards against duplicate links, and appends via the shared append_to_csv helper so
the row honors the canonical 12-column schema. This script's single responsibility is
the append; rendering README.md is generate_readme.py's job. The `make add-resource`
target chains the two so the CSV and the rendered list are always updated together
(there is no add-target that skips the regenerate). Use --dry-run to preview the ID
and placement without writing.

This is the local, single-entry counterpart to resources/create_resource_pr.py
(which runs the full approve -> branch -> commit -> PR flow in CI).

Usage:
    add_resource.py --display-name "cctop" --category "Session Monitors" \
        --link https://github.com/stefanprodan/cctop \
        --author-name stefanprodan --author-link https://github.com/stefanprodan \
        --description "A live top-style terminal monitor for Claude Code sessions." \
        [--subcategory "..."] [--dry-run] [--allow-duplicate]
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
from resources.ids import generate_resource_id  # noqa: E402
from resources.resource_utils import CSV_PATH, append_to_csv  # noqa: E402

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


def link_exists(link: str) -> bool:
    """True if any existing row already has this Link (dedupe guard)."""
    if not CSV_PATH.exists():
        return False
    target = link.strip()
    with CSV_PATH.open(encoding="utf-8", newline="") as fh:
        return any((row.get("Link") or "").strip() == target for row in csv.DictReader(fh))


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--display-name", required=True, help="Resource display name.")
    p.add_argument("--category", required=True, help="Category (must exist in config.yaml).")
    p.add_argument("--link", required=True, help="Canonical URL (drives the resource ID).")
    p.add_argument("--author-name", default="", help="Author / owner name.")
    p.add_argument("--author-link", default="", help="Author profile URL.")
    p.add_argument("--description", default="", help="One-line descriptive blurb.")
    p.add_argument("--subcategory", default="", help="Optional sub-category under --category.")
    p.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="Append even if a row with this link already exists.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved ID and placement without writing.",
    )
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
        # Generation is lenient (renders undeclared sub-categories after the
        # declared ones), so this is a nudge, not a hard error.
        print(
            f"note: sub-category {args.subcategory!r} is not declared under "
            f"{args.category!r} in config.yaml; it will still render, but to fix its "
            f"order run: make add-category CATEGORY={args.category!r} "
            f"SUB_CATEGORY={args.subcategory!r}",
            file=sys.stderr,
        )

    if not args.allow_duplicate and link_exists(args.link):
        print(
            f"ERROR: a row with link {args.link!r} already exists; refusing to add a "
            "duplicate. Pass --allow-duplicate to override.",
            file=sys.stderr,
        )
        return 1

    rid = generate_resource_id()
    placement = args.category + (f" / {args.subcategory}" if args.subcategory else "")

    if args.dry_run:
        print(f"[dry-run] would add {rid}: {args.display_name!r} -> {placement}")
        return 0

    row = {
        "id": rid,
        "display_name": args.display_name,
        "category": args.category,
        "subcategory": args.subcategory,
        "link": args.link,
        "author_name": args.author_name,
        "author_link": args.author_link,
        "description": args.description,
    }
    if not append_to_csv(row):
        print("ERROR: failed to append the row to the CSV.", file=sys.stderr)
        return 1

    print(f"Added {rid}: {args.display_name!r} -> {placement} in THE_RESOURCES_TABLE_NEW.csv.")
    print("Run `make generate` (chained by the make add-resource target) to update README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
