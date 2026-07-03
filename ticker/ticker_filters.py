#!/usr/bin/env python3
"""Declarative exclusion filters for the Claude Code repo ticker (display side).

`full_name` is "owner/repo"; all matching is case-insensitive.

To add a filter: edit one of the lists below and re-run the ticker.
"""

from __future__ import annotations

# Exclude every repo owned by these accounts (the part before the "/"). Exact match.
EXCLUDE_OWNERS: set[str] = {
    "hesreallyhim",  # I don't include my own projects in the list - they are awesome enough.
    # This user is permanently banned from the repository for
    # egregious violation of the Code of Conduct - like, very egregious.
    "thedotmack",
}

# Exclude repos whose full name simply equals "claude-code" (or minor variants).
# This is in order to exclude malicious repositories that have historically
# been used to distribute malicious, modified versions of Claude Code.
EXCLUDE_NAME_EXACT: set[str] = {
    "claude-code",
    "claudecode",
    "claude_code",
    "claude.code",
}

# Exclude repos whose name CONTAINS any of these substrings.
EXCLUDE_NAME_CONTAINS: tuple[str, ...] = (
    # Exclude repos that likely contain the entire source code
    # of Claude Code - these are also popular vectors for malware.
    "source-code",
    "sourcecode",
    "source-map",
    "sourcemap",
)

# Escape hatch: exclude specific "owner/repo" full names outright.
EXCLUDE_FULL_NAMES: set[str] = set()


# --- matching (case-insensitive; substring/exact only, deliberately no regex) - #
_OWNERS = {owner.lower() for owner in EXCLUDE_OWNERS}
_NAMES_EXACT = {name.lower() for name in EXCLUDE_NAME_EXACT}
_NAME_CONTAINS = tuple(substring.lower() for substring in EXCLUDE_NAME_CONTAINS)
_FULL_NAMES = {full_name.lower() for full_name in EXCLUDE_FULL_NAMES}


def keep_repo(full_name: str) -> bool:
    """Return True if the repo passes every filter (i.e. should be shown)."""
    normalized = (full_name or "").strip().lower()
    if "/" not in normalized:
        return False
    owner, repo_name = normalized.split("/", 1)
    if normalized in _FULL_NAMES:
        return False
    if owner in _OWNERS:
        return False
    if repo_name in _NAMES_EXACT:
        return False
    if any(substring in repo_name for substring in _NAME_CONTAINS):
        return False
    return True


def filter_repos(repos: list[dict]) -> list[dict]:
    """Drop excluded repos from a list of dicts that each carry a 'full_name'."""
    return [repo for repo in repos if keep_repo(repo.get("full_name", ""))]
