#!/usr/bin/env python3
"""Update an existing resource's content fields in place (not its category).

Identifies the row by --id or --link (the current link) and sets any of
--new-link, --display-name, --author-name, --author-link, --description — rewriting
only that one CSV line; the ID, Category/Sub-Category, dates, and Active/Stale flags
are left untouched. Re-filing to a different category is move_resource.py's job. When
--new-link changes the link it is checked against the other rows so two resources can't
collide on one link. Rendering README.md is generate_readme.py's job; the
`make update-resource` target chains the two. Use --dry-run to preview.

Usage:
    update_resource.py (--id ID | --link URL) [--new-link URL] [--display-name NAME] \
        [--author-name NAME] [--author-link URL] [--description TEXT] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from resources.resource_utils import (  # noqa: E402
    COL_AUTHOR_LINK,
    COL_AUTHOR_NAME,
    COL_DESCRIPTION,
    COL_DISPLAY,
    COL_LINK,
    find_row_indices,
    read_lines,
    serialize_row,
    split_eol,
    write_lines,
)

# CLI flag -> (column index, human label). Order controls the dry-run/print order.
FIELD_COLS: dict[str, tuple[int, str]] = {
    "display_name": (COL_DISPLAY, "Display Name"),
    "new_link": (COL_LINK, "Link"),
    "author_name": (COL_AUTHOR_NAME, "Author Name"),
    "author_link": (COL_AUTHOR_LINK, "Author Link"),
    "description": (COL_DESCRIPTION, "Description"),
}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sel = p.add_mutually_exclusive_group(required=True)
    sel.add_argument("--id", help="Resource ID to update.")
    sel.add_argument("--link", help="Current Link of the resource to update.")
    p.add_argument("--new-link", dest="new_link", help="Replacement canonical URL.")
    p.add_argument("--display-name", dest="display_name", help="Replacement display name.")
    p.add_argument("--author-name", dest="author_name", help="Replacement author name.")
    p.add_argument("--author-link", dest="author_link", help="Replacement author URL.")
    p.add_argument("--description", help="Replacement description.")
    p.add_argument("--dry-run", action="store_true", help="Print the change without writing.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    setters = {key: getattr(args, key) for key in FIELD_COLS if getattr(args, key) is not None}
    if not setters:
        print(
            "ERROR: nothing to update — pass at least one of --new-link, --display-name, "
            "--author-name, --author-link, --description.",
            file=sys.stderr,
        )
        return 1

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
        print(f"ERROR: {len(matches)} rows match {selector}; refusing to update an ambiguous set.", file=sys.stderr)
        return 1

    idx = matches[0]

    # A new link must not collide with a *different* row.
    if "new_link" in setters:
        clashes = [i for i in find_row_indices(lines, link=setters["new_link"]) if i != idx]
        if clashes:
            print(
                f"ERROR: link {setters['new_link']!r} already belongs to another resource; "
                "refusing to create a duplicate.",
                file=sys.stderr,
            )
            return 1

    content, eol = split_eol(lines[idx])
    fields = next(csv.reader([content]))
    display = fields[COL_DISPLAY]

    changes: list[tuple[str, str, str]] = []
    for key, value in setters.items():
        col, label = FIELD_COLS[key]
        if fields[col] != value:
            changes.append((label, fields[col], value))
            fields[col] = value

    if not changes:
        print(f"note: {display!r} already has those values; nothing to do.")
        return 0

    if args.dry_run:
        print(f"[dry-run] {display!r}:")
        for label, old, new in changes:
            print(f"    {label}: {old!r}  ->  {new!r}")
        return 0

    lines[idx] = serialize_row(fields, eol)
    write_lines(lines)

    print(f"Updated {display!r} ({', '.join(label for label, _, _ in changes)}) in THE_RESOURCES_TABLE_NEW.csv.")
    print("Run `make generate` (chained by the make update-resource target) to update README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
