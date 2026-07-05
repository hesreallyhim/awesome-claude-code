#!/usr/bin/env python3
"""Regenerate the recommend-resource issue-form Category dropdown from config.yaml.

config.yaml is the single source of truth: the dropdown lists every `submittable`
category (see the config.yaml schema header), in config order. This script rewrites
that options block so the two can never drift by hand. It runs in pre-commit and can
gate CI with --check.

    venv/bin/python scripts/sync_issue_form.py           # write if out of sync
    venv/bin/python scripts/sync_issue_form.py --check    # exit 1 if out of sync (no write)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from scripts import manage_categories as mc  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--check",
        action="store_true",
        help="Don't write; exit 1 if the dropdown is out of sync with config.yaml.",
    )
    args = p.parse_args(argv)

    if not mc.ISSUE_FORM_PATH.exists():
        print(f"ERROR: {mc.ISSUE_FORM_PATH} not found.", file=sys.stderr)
        return 1

    config_text = mc.CONFIG_PATH.read_text(encoding="utf-8")
    form_text = mc.ISSUE_FORM_PATH.read_text(encoding="utf-8")
    try:
        updated = mc.render_form(form_text, config_text)
    except mc.ConfigEditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    rel = mc.ISSUE_FORM_PATH.relative_to(BASE)
    if updated == form_text:
        return 0
    if args.check:
        print(
            f"ERROR: {rel} is out of sync with config.yaml. "
            "Run `make sync-form` and commit the result.",
            file=sys.stderr,
        )
        return 1
    mc.ISSUE_FORM_PATH.write_text(updated, encoding="utf-8")
    print(f"Updated {rel} from config.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
