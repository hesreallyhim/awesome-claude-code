"""Coverage for the badge-notification logic (no network).

Pins the pure pieces: repo parsing (URL + slug), extracting the target from an
approved-resource PR body, the issue body, and dry-run skip rules. The network path
(issue creation) isn't unit-tested.

Run:  venv/bin/python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from scripts.badges import badge_notification as bn  # noqa: E402

# PR body exactly as resources/create_resource_pr.py -> generate_pr_content renders it.
PR_BODY = """### Resource Information

- **Display Name**: Cool Tool
- **Category**: Skills
- **Sub-Category**: N/A
- **Link**: https://github.com/owner/cool-tool
- **Author**: [me](https://github.com/me)

### Description

Does things.

---

Resolves #42
"""


def test_parse_repo_url_and_slug() -> None:
    assert bn.parse_repo("https://github.com/o/r") == ("o", "r")
    assert bn.parse_repo("https://github.com/o/r.git") == ("o", "r")
    assert bn.parse_repo("https://github.com/o/r/") == ("o", "r")
    assert bn.parse_repo("o/r") == ("o", "r")  # slug form (workflow_dispatch input)
    assert bn.parse_repo("https://github.com/o/r/tree/main") is None  # deep path
    assert bn.parse_repo("https://gitlab.com/o/r") is None
    assert bn.parse_repo("not a repo") is None


def test_extract_pr_target() -> None:
    link, name = bn.extract_pr_target(PR_BODY)
    assert link == "https://github.com/owner/cool-tool"
    assert name == "Cool Tool"


def test_extract_pr_target_empty() -> None:
    assert bn.extract_pr_target("") == ("", "")
    assert bn.extract_pr_target("no fields here") == ("", "")


def test_issue_body_has_name_badge_and_list_link() -> None:
    body = bn.issue_body("Cool Tool")
    assert "**Cool Tool**" in body
    assert bn.LIST_URL in body
    assert "awesome.re/mentioned-badge.svg" in body
    assert "One-time notification" in body


def test_notify_dry_run_rules() -> None:
    import requests

    s = requests.Session()
    assert "skip (Anthropic)" in bn.notify(
        s, "anthropics/claude-code", "", dry_run=True
    )
    assert "skip (not a github repo)" in bn.notify(
        s, "https://youtu.be/x", "", dry_run=True
    )
    assert "would open issue on o/r for 'R'" in bn.notify(s, "o/r", "R", dry_run=True)
    # falls back to repo name when no display name given
    assert "for 'r'" in bn.notify(s, "https://github.com/o/r", "", dry_run=True)
