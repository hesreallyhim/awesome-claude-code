"""GitHub-related utilities shared across scripts."""

from __future__ import annotations

import json
import os
import re
from urllib.parse import quote

from github import Auth, Github

_DEFAULT_SECONDS_BETWEEN_REQUESTS = 0.5
_DEFAULT_GITHUB_USER_AGENT = "awesome-claude-code bot"
_GITHUB_CLIENTS: dict[tuple[str | None, str | None, float], Github] = {}


def _normalize_repo_name(repo: str) -> str:
    if repo.endswith(".git"):
        return repo[: -len(".git")]
    return repo


def get_github_client(
    token: str | None = None,
    user_agent: str = _DEFAULT_GITHUB_USER_AGENT,
    seconds_between_requests: float = _DEFAULT_SECONDS_BETWEEN_REQUESTS,
) -> Github:
    """Return a cached PyGithub client with optional pacing."""
    key = (token, user_agent, seconds_between_requests)
    if key not in _GITHUB_CLIENTS:
        auth = Auth.Token(token) if token else None
        _GITHUB_CLIENTS[key] = Github(
            auth=auth,
            user_agent=user_agent,
            seconds_between_requests=seconds_between_requests,
        )
    return _GITHUB_CLIENTS[key]


def github_request_json(
    api_url: str,
    params: dict[str, object] | None = None,
    token: str | None = None,
    user_agent: str = _DEFAULT_GITHUB_USER_AGENT,
    seconds_between_requests: float = _DEFAULT_SECONDS_BETWEEN_REQUESTS,
) -> tuple[int, dict[str, object], object | None]:
    """Request JSON from the GitHub API using PyGithub's requester."""
    if token is None:
        token = os.getenv("GITHUB_TOKEN") or None
    client = get_github_client(
        token=token,
        user_agent=user_agent,
        seconds_between_requests=seconds_between_requests,
    )
    status, headers, body = client.requester.requestJson(
        "GET",
        api_url,
        parameters=params,
        headers={"Accept": "application/vnd.github+json"},
    )
    if not body:
        return status, headers, None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = body
    return status, headers, data


def parse_github_url(url: str) -> tuple[str, bool, str | None, str | None]:
    """
    Parse GitHub URL and return API endpoint if it's a GitHub repository content URL.
    Returns (api_url, is_github, owner, repo) tuple.
    """
    # Match GitHub blob or tree URLs - capture everything after /blob/ or /tree/ as one group
    github_pattern = r"https://github\.com/([^/]+)/([^/]+)/(blob|tree)/(.+)"
    match = re.match(github_pattern, url)

    if match:
        owner, repo, _, branch_and_path = match.groups()  # _ is blob_or_tree, which we don't need
        repo = _normalize_repo_name(repo)

        # Split on the first occurrence of a path starting with . or containing a file extension
        # Common patterns: .github/, .claude/, src/, file.ext
        parts = branch_and_path.split("/")

        # Find where the file path likely starts
        branch_parts = []
        path_parts: list[str] = []
        found_path_start = False

        for i, part in enumerate(parts):
            if not found_path_start:
                # Check if this looks like the start of a file path
                if (
                    part.startswith(".")  # Hidden directories like .github, .claude
                    or "." in part  # Files with extensions
                    or part in ["src", "lib", "bin", "scripts", "docs", "test", "tests"]
                ):  # Common directories
                    found_path_start = True
                    path_parts = parts[i:]
                else:
                    branch_parts.append(part)

        # If we didn't find an obvious path start, treat the last part as the path
        if not path_parts and parts:
            branch_parts = parts[:-1] if len(parts) > 1 else parts
            path_parts = parts[-1:] if len(parts) > 1 else []

        branch = "/".join(branch_parts) if branch_parts else "main"
        path = "/".join(path_parts)

        # URL-encode the branch name to handle slashes
        encoded_branch = quote(branch, safe="")
        api_url = (
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={encoded_branch}"
        )
        return api_url, True, owner, repo

    # Check if it's a repository root URL
    github_repo_pattern = r"https://github\.com/([^/]+)/([^/]+)(?:/.*)?$"
    match = re.match(github_repo_pattern, url)
    if match:
        owner, repo = match.groups()
        repo = _normalize_repo_name(repo)
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        return api_url, True, owner, repo

    return url, False, None, None


def parse_github_resource_url(url: str) -> dict[str, str] | None:
    """
    Parse GitHub URL and extract owner, repo, branch, and path.
    Returns a dict with keys: owner, repo, branch, path, type.
    """
    patterns = {
        # File in repository
        "file": r"https://github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+)",
        # Directory in repository
        "dir": r"https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)",
        # Repository root
        "repo": r"https://github\.com/([^/]+)/([^/]+)/?$",
        # Gist
        "gist": r"https://gist\.github\.com/([^/]+)/([^/#]+)",
    }

    for url_type, pattern in patterns.items():
        match = re.match(pattern, url)
        if match:
            if url_type == "gist":
                return {
                    "type": "gist",
                    "owner": match.group(1),
                    "gist_id": match.group(2),
                }
            elif url_type == "repo":
                return {
                    "type": "repo",
                    "owner": match.group(1),
                    "repo": _normalize_repo_name(match.group(2)),
                }
            else:
                return {
                    "type": url_type,
                    "owner": match.group(1),
                    "repo": _normalize_repo_name(match.group(2)),
                    "branch": match.group(3),
                    "path": match.group(4),
                }

    return None
