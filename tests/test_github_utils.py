#!/usr/bin/env python3
"""Tests for GitHub utility parsing helpers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.github_utils import parse_github_resource_url, parse_github_url  # noqa: E402


def test_parse_github_url_blob_with_slash_branch() -> None:
    url = "https://github.com/owner/repo/blob/feature/with/slash/README.md"
    api_url, is_github, owner, repo = parse_github_url(url)
    assert is_github is True
    assert owner == "owner"
    assert repo == "repo"
    assert (
        api_url
        == "https://api.github.com/repos/owner/repo/contents/README.md?ref=feature%2Fwith%2Fslash"
    )


def test_parse_github_url_tree_docs_path() -> None:
    url = "https://github.com/owner/repo/tree/main/docs"
    api_url, is_github, owner, repo = parse_github_url(url)
    assert is_github is True
    assert owner == "owner"
    assert repo == "repo"
    assert api_url == "https://api.github.com/repos/owner/repo/contents/docs?ref=main"


def test_parse_github_url_repo_root() -> None:
    url = "https://github.com/owner/repo.git"
    api_url, is_github, owner, repo = parse_github_url(url)
    assert is_github is True
    assert owner == "owner"
    assert repo == "repo"
    assert api_url == "https://api.github.com/repos/owner/repo"


def test_parse_github_url_non_github() -> None:
    url = "https://example.com/foo"
    api_url, is_github, owner, repo = parse_github_url(url)
    assert is_github is False
    assert owner is None
    assert repo is None
    assert api_url == url


def test_parse_github_resource_url_file_and_raw() -> None:
    url = "https://github.com/owner/repo/blob/main/dir/file.txt"
    parsed = parse_github_resource_url(url)
    assert parsed == {
        "type": "file",
        "owner": "owner",
        "repo": "repo",
        "branch": "main",
        "path": "dir/file.txt",
    }

    raw_url = "https://github.com/owner/repo/raw/main/file.txt"
    parsed_raw = parse_github_resource_url(raw_url)
    assert parsed_raw == {
        "type": "file",
        "owner": "owner",
        "repo": "repo",
        "branch": "main",
        "path": "file.txt",
    }


def test_parse_github_resource_url_dir_repo_gist() -> None:
    dir_url = "https://github.com/owner/repo/tree/main/docs"
    parsed_dir = parse_github_resource_url(dir_url)
    assert parsed_dir == {
        "type": "dir",
        "owner": "owner",
        "repo": "repo",
        "branch": "main",
        "path": "docs",
    }

    repo_url = "https://github.com/owner/repo"
    parsed_repo = parse_github_resource_url(repo_url)
    assert parsed_repo == {"type": "repo", "owner": "owner", "repo": "repo"}

    gist_url = "https://gist.github.com/owner/abcdef"
    parsed_gist = parse_github_resource_url(gist_url)
    assert parsed_gist == {"type": "gist", "owner": "owner", "gist_id": "abcdef"}


def test_parse_github_resource_url_normalizes_repo_name() -> None:
    repo_url = "https://github.com/owner/repo.git"
    parsed = parse_github_resource_url(repo_url)
    assert parsed == {"type": "repo", "owner": "owner", "repo": "repo"}


def test_parse_github_resource_url_non_github() -> None:
    assert parse_github_resource_url("https://example.com") is None
