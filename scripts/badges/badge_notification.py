#!/usr/bin/env python3
"""Open a one-time "featured in Awesome Claude Code" welcome issue on a resource's repo.

Two entry points, both single-repo (no CSV/ID coupling):
  * the notify-on-merge workflow, when an approved resource PR (opened by
    github-actions[bot]) merges to main — the repo is read from the PR body's
    `- **Link**:` field (the create_resource_pr format); and
  * a manual workflow_dispatch with an OWNER/REPO (or URL) input.

Needs a *classic* PAT with `public_repo` scope in AWESOME_CC_PAT_PUBLIC_REPO (opening
issues on external repos needs a user token; a fine-grained PAT / GitHub App token is
limited to repos you own / where the app is installed). A dedicated bot account is
recommended. Uses only `requests`. Deliberately NOT idempotent: the pipeline adds once
so it notifies once; for manual runs it's on you to check a welcome issue doesn't
already exist (a rare case, and search API calls are rate-limited).

Usage:
  python scripts/badges/badge_notification.py --repo owner/name [--name "Name"]
  python scripts/badges/badge_notification.py --repo https://github.com/owner/name
  python scripts/badges/badge_notification.py --from-pr-body        # reads PR_BODY env
  # add --dry-run to print without calling the API (no token needed)
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import requests

LIST_URL = "https://github.com/hesreallyhim/awesome-claude-code"
ISSUE_TITLE = "🎉 Your project has been featured in Awesome Claude Code!"
LABEL = "awesome-claude-code"
API = "https://api.github.com"

URL_RE = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)
SLUG_RE = re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$")


def parse_repo(target: str) -> tuple[str, str] | None:
    """Return (owner, repo) from a github.com URL or an `owner/name` slug, else None."""
    t = (target or "").strip()
    m = URL_RE.match(t) or SLUG_RE.match(t)
    return (m.group(1), m.group(2)) if m else None


def extract_pr_target(pr_body: str) -> tuple[str, str]:
    """Pull (link, display_name) from an approved-resource PR body (create_resource_pr format)."""
    body = pr_body or ""
    link = re.search(r"\*\*Link\*\*:\s*(\S+)", body)
    name = re.search(r"\*\*Display Name\*\*:\s*(.+)", body)
    return (
        link.group(1).strip() if link else "",
        name.group(1).strip() if name else "",
    )


def issue_body(name: str) -> str:
    return f"""Hello! 👋

**{name}** has been featured in the [Awesome Claude Code]({LIST_URL}) list — a curated
collection of the best tools, skills, commands, and resources for Claude Code. Thanks for
contributing to the ecosystem!

If you'd like to show it off, feel free to add a badge to your README:

```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)]({LIST_URL})
```
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)]({LIST_URL})

No action is required — feel free to close this issue any time. 🙏

---
*One-time notification, sent because your project was added to Awesome Claude Code.*"""


def notify(session: requests.Session, target: str, name: str, dry_run: bool) -> str:
    owner_repo = parse_repo(target)
    if not owner_repo:
        return f"skip (not a github repo): {target!r}"
    owner, repo = owner_repo
    name = name or repo
    if "anthropic" in owner.lower():
        return f"skip (Anthropic): {owner}/{repo}"
    if dry_run:
        return f"[dry-run] would open issue on {owner}/{repo} for {name!r}"
    r = session.post(
        f"{API}/repos/{owner}/{repo}/issues",
        json={"title": ISSUE_TITLE, "body": issue_body(name), "labels": [LABEL]},
        timeout=30,
    )
    # Labels can 403/422 if the label doesn't exist or we lack label perms — retry plain.
    if r.status_code in (403, 422):
        r = session.post(
            f"{API}/repos/{owner}/{repo}/issues",
            json={"title": ISSUE_TITLE, "body": issue_body(name)},
            timeout=30,
        )
    if r.status_code == 201:
        return f"✅ notified {owner}/{repo}: {r.json()['html_url']}"
    return f"⚠️ could not notify {owner}/{repo} (HTTP {r.status_code}: {r.text[:120]})"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Send an Awesome Claude Code welcome issue."
    )
    p.add_argument("--repo", help="owner/name or a github.com URL.")
    p.add_argument(
        "--from-pr-body", action="store_true", help="Read PR_BODY env; extract Link."
    )
    p.add_argument("--name", default="", help="Display name (defaults to repo name).")
    p.add_argument(
        "--dry-run", action="store_true", help="Print the action; no API calls."
    )
    args = p.parse_args(argv)

    if args.from_pr_body:
        target, name = extract_pr_target(os.environ.get("PR_BODY", ""))
        name = args.name or name
    elif args.repo:
        target, name = args.repo, args.name
    else:
        p.error("provide --repo or --from-pr-body")

    if not parse_repo(target):
        print(f"No GitHub repo resolved (target={target!r}); nothing to do.")
        return 0

    session = requests.Session()
    if not args.dry_run:
        token = os.environ.get("AWESOME_CC_PAT_PUBLIC_REPO")
        if not token:
            print(
                "ERROR: AWESOME_CC_PAT_PUBLIC_REPO is required (PAT with public issues:write).",
                file=sys.stderr,
            )
            return 1
        session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            }
        )

    print(notify(session, target, name, args.dry_run))
    return 0  # never fail the merge over a notification


if __name__ == "__main__":
    raise SystemExit(main())
