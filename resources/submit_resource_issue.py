#!/usr/bin/env python3
"""Open a resource-submission issue from the CLI that ENTERS the validation pipeline.

Composes the same ### sections the recommend-resource GitHub form produces and creates
the issue via `gh`, applying the resource-submission + validation-pending labels so
validate-new-issue.yml runs on `opened` — the identical path a form submission takes.

Applying those labels needs triage/write access, so this is a maintainer/agent tool: an
unprivileged `gh` user can still open a label-less issue, but the validation job's label
guard skips it (the anti-spam design). Category is validated against config.yaml first
(fail closed) so a typo can't create a dead-on-arrival issue. An optional --subcategory
is emitted as a Sub-Category section (the parser reads it); the form itself has no such
field, so it's a convenience for pre-filing.

The body is handed to `gh` over stdin, so backticks / $ in the description are never seen
by a shell. For a description that a *caller's* shell would still mangle, pass
--description-file (a path) instead of --description. Use --dry-run to preview.

Usage:
    submit_resource_issue.py --display-name NAME --category CAT --link URL \
        --author-name NAME --author-link URL \
        (--description TEXT | --description-file PATH) \
        [--subcategory SUB] [--repo owner/repo] [--dry-run]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from resources.categories import category_names  # noqa: E402

LABELS = "resource-submission,validation-pending"
CHECKLIST = (
    "### Checklist\n\n"
    "- [x] I checked that this resource isn't already on the list\n"
    "- [x] All links are working and publicly accessible\n"
    "- [x] This resource is specific to Claude Code\n"
)


def compose_body(
    *,
    display_name: str,
    category: str,
    link: str,
    author_name: str,
    author_link: str,
    description: str,
    subcategory: str = "",
) -> str:
    """Render the recommend-resource issue body (the ### sections the form emits)."""

    def sec(label: str, value: str) -> str:
        return f"### {label}\n\n{value}\n"

    parts = [sec("Display Name", display_name), sec("Category", category)]
    if subcategory:
        parts.append(sec("Sub-Category", subcategory))
    parts += [
        sec("Link", link),
        sec("Author Name", author_name),
        sec("Author Link", author_link),
        sec("Description", description),
        CHECKLIST,
    ]
    return "\n".join(parts)


def _default_repo() -> str:
    """owner/repo of the current checkout's default remote (via gh), or ''."""
    r = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else ""


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--display-name", required=True)
    p.add_argument("--category", required=True, help="Must exist in config.yaml.")
    p.add_argument("--link", required=True)
    p.add_argument("--author-name", default="")
    p.add_argument("--author-link", default="")
    desc = p.add_mutually_exclusive_group()
    desc.add_argument("--description", default="")
    desc.add_argument("--description-file", help="Path to a file holding the description (backtick-safe).")
    p.add_argument("--subcategory", default="")
    p.add_argument("--repo", default="", help="owner/repo (default: current remote).")
    p.add_argument("--dry-run", action="store_true", help="Print body + command without creating.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    known = category_names()
    if args.category not in known:
        print(f"ERROR: category {args.category!r} is not declared in config.yaml.", file=sys.stderr)
        print(f"Known categories: {', '.join(known)}", file=sys.stderr)
        return 1

    description = args.description
    if args.description_file:
        try:
            description = Path(args.description_file).read_text(encoding="utf-8").strip()
        except OSError as e:
            print(f"ERROR: cannot read --description-file: {e}", file=sys.stderr)
            return 1
    if not description:
        print("ERROR: a description is required (--description or --description-file).", file=sys.stderr)
        return 1

    body = compose_body(
        display_name=args.display_name,
        category=args.category,
        link=args.link,
        author_name=args.author_name,
        author_link=args.author_link,
        description=description,
        subcategory=args.subcategory,
    )
    title = f"[Resource]: {args.display_name}"
    repo = args.repo or _default_repo()
    if not repo:
        print("ERROR: could not determine the target repo; pass --repo owner/repo.", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"[dry-run] gh issue create --repo {repo} --title {title!r} --label {LABELS} --body-file -")
        print("[dry-run] labels applied at creation → validate-new-issue.yml runs on `opened`.")
        print("----- issue body -----")
        print(body, end="")
        return 0

    result = subprocess.run(
        ["gh", "issue", "create", "--repo", repo, "--title", title, "--label", LABELS, "--body-file", "-"],
        input=body,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        print(
            "NOTE: applying the resource-submission label needs triage/write access on the repo. "
            "Without it gh refuses — an unprivileged user can only open a label-less issue, which the "
            "validator skips by design.",
            file=sys.stderr,
        )
        return 1

    print(result.stdout.strip())  # the created issue URL
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
