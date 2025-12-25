#!/usr/bin/env python3
"""
Link validation script with override support for the Awesome Claude Code repository.
Validates resource URLs and updates CSV with current status, respecting manual overrides.

Features:
- Validates Primary/Secondary Link URLs using HTTP requests
- Supports GitHub API for repository URLs with license detection
- Fetches last modified dates for GitHub resources using Commits API
- Implements exponential backoff retry logic
- Respects field overrides from resource-overrides.yaml
- Updates CSV with Active status, Last Checked timestamp, and Last Modified date
- Provides detailed logging and broken link summary
- GitHub Action mode for CI/CD integration
"""

import argparse
import csv
import json
import logging
import os
import random
import re
import sys
import time
from datetime import UTC, datetime, timedelta

import requests
import yaml  # type: ignore[import-untyped]
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

USER_AGENT = "awesome-claude-code Link Validator/2.0"
INPUT_FILE = "THE_RESOURCES_TABLE.csv"
OUTPUT_FILE = "THE_RESOURCES_TABLE.csv"
OVERRIDE_FILE = "templates/resource-overrides.yaml"
PRIMARY_LINK_HEADER_NAME = "Primary Link"
SECONDARY_LINK_HEADER_NAME = "Secondary Link"
ACTIVE_HEADER_NAME = "Active"
LAST_CHECKED_HEADER_NAME = "Last Checked"
LAST_MODIFIED_HEADER_NAME = "Last Modified"
LICENSE_HEADER_NAME = "License"
ID_HEADER_NAME = "ID"
STALE_HEADER_NAME = "Stale"
STALE_DAYS = 90
VERBOSE = False
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

PRINT_FILE = None


def load_overrides():
    """Load override configuration from YAML file."""
    if not os.path.exists(OVERRIDE_FILE):
        return {}

    with open(OVERRIDE_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if data is None:
            return {}
        logger.info(f"Loaded overrides from {OVERRIDE_FILE} - overrides: {data}")
        return data.get("overrides", {})


def apply_overrides(row, overrides):
    """Apply overrides to a row if the resource ID has overrides configured.

    Any field set in the override configuration is automatically locked,
    preventing validation scripts from updating it. The skip_validation flag
    has highest precedence - if set, the entire resource is skipped.
    """
    resource_id = row.get(ID_HEADER_NAME, "")
    if not resource_id or resource_id not in overrides:
        return row, set(), False

    override_config = overrides[resource_id]
    locked_fields = set()
    skip_validation = override_config.get("skip_validation", False)

    # Apply each override and auto-lock the field
    for field, value in override_config.items():
        # Skip special control/metadata fields
        if field in ["skip_validation", "notes"]:
            continue

        # Skip any legacy *_locked flags (no longer needed)
        if field.endswith("_locked"):
            continue

        # Apply override value and automatically lock the field
        if field == "license":
            row[LICENSE_HEADER_NAME] = value
            locked_fields.add("license")
        elif field == "active":
            row[ACTIVE_HEADER_NAME] = value
            locked_fields.add("active")
        elif field == "last_checked":
            row[LAST_CHECKED_HEADER_NAME] = value
            locked_fields.add("last_checked")
        elif field == "last_modified":
            row[LAST_MODIFIED_HEADER_NAME] = value
            locked_fields.add("last_modified")
        elif field == "description":
            row["Description"] = value
            locked_fields.add("description")

    return row, locked_fields, skip_validation


def parse_last_modified_date(value):
    """Parse date strings into timezone-aware datetimes (UTC)."""
    if not value:
        return None

    value = str(value).strip()
    if not value:
        return None

    try:
        normalized_value = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized_value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        pass

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d:%H-%M-%S")
        return parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def is_stale(last_modified, stale_days=STALE_DAYS):
    """Return True if the resource is stale or last_modified is missing."""
    if last_modified is None:
        return True

    if last_modified.tzinfo is None:
        last_modified = last_modified.replace(tzinfo=UTC)

    now = datetime.now(UTC)
    return now - last_modified > timedelta(days=stale_days)


def ensure_stale_column(fieldnames, rows):
    """Ensure the Stale column exists and rows have default values."""
    fieldnames_list = list(fieldnames or [])
    if STALE_HEADER_NAME not in fieldnames_list:
        fieldnames_list.append(STALE_HEADER_NAME)

    for row in rows:
        row.setdefault(STALE_HEADER_NAME, "")

    return fieldnames_list, rows


def parse_github_url(url) -> tuple[str, bool, str | None, str | None]:
    """
    Parse GitHub URL and return API endpoint if it's a GitHub repository content URL.
    Returns (api_url, is_github, owner, repo) tuple.
    """
    from urllib.parse import quote

    # Match GitHub blob or tree URLs - capture everything after /blob/ or /tree/ as one group
    github_pattern = r"https://github\.com/([^/]+)/([^/]+)/(blob|tree)/(.+)"
    match = re.match(github_pattern, url)

    if match:
        owner, repo, _, branch_and_path = match.groups()  # _ is blob_or_tree, which we don't need

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
    github_repo_pattern = r"https://github\.com/([^/]+)/([^/]+)/?$"
    match = re.match(github_repo_pattern, url)
    if match:
        owner, repo = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        return api_url, True, owner, repo

    return url, False, None, None


def get_github_license(owner, repo):
    """Fetch license information from GitHub API."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            license_info = data.get("license")
            if license_info and license_info.get("spdx_id"):
                return license_info["spdx_id"]
    except Exception:
        pass
    return "NOT_FOUND"


def get_committer_date_from_response(
    response: requests.Response,
) -> str | None:
    """Extract committer date from GitHub API response."""
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        # Get the committer date from the latest commit
        commit = data[0]
        commit_date = (
            commit.get("commit", {}).get("committer", {}).get("date")
            or commit.get("commit", {}).get("author", {}).get("date")
            or commit.get("committer", {}).get("date")
            or commit.get("author", {}).get("date")
        )
        return commit_date
    return None


def format_commit_date(commit_date: str) -> str:
    """Format commit date from ISO format to YYYY-MM-DD:HH-MM-SS."""
    from datetime import datetime

    dt = datetime.fromisoformat(commit_date.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d:%H-%M-%S")


def get_github_last_modified(owner, repo, path=None):
    """Fetch last modified date for a GitHub file or repository."""
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": 1, "path": path} if path else {"per_page": 1}
        response = requests.get(api_url, headers=HEADERS, params=params, timeout=10)
        if VERBOSE:
            print(
                f"[github-commits] owner={owner} repo={repo} path={path or ''} "
                f"status={response.status_code} reason={response.reason}"
            )
            try:
                print(f"[github-commits-body] {response.json()}")
            except Exception:
                print(f"[github-commits-body-raw] {response.text}")
        if response.status_code == 200:
            commit_date = get_committer_date_from_response(response)
            if commit_date:
                return format_commit_date(commit_date)
    except Exception as e:
        print(f"Error fetching last modified date for {owner}/{repo}: {e}")
    return None


def get_github_commit_dates(owner: str, repo: str) -> tuple[str | None, str | None]:
    """Fetch the first (oldest) and last (newest) commit dates for a GitHub repository.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name

    Returns:
        Tuple of (first_commit_date, last_commit_date) in YYYY-MM-DD:HH-MM-SS format,
        or (None, None) if the dates cannot be fetched.
    """
    first_commit_date = None
    last_commit_date = None

    try:
        # Get the last (most recent) commit
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": 1}
        response = requests.get(api_url, headers=HEADERS, params=params, timeout=10)

        if response.status_code == 200:
            commit_date = get_committer_date_from_response(response)
            if commit_date:
                last_commit_date = format_commit_date(commit_date)

            # Check Link header for pagination to get total pages
            link_header = response.headers.get("Link", "")
            # Parse the last page number from Link header
            # Format: <url>; rel="next", <url?page=N>; rel="last"
            import re

            last_page_match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if last_page_match:
                last_page = int(last_page_match.group(1))
                # Fetch the first (oldest) commit from the last page
                params = {"per_page": 1, "page": last_page}
                response = requests.get(api_url, headers=HEADERS, params=params, timeout=10)
                if response.status_code == 200:
                    commit_date = get_committer_date_from_response(response)
                    if commit_date:
                        first_commit_date = format_commit_date(commit_date)
            else:
                # Only one page of commits, so first = last
                first_commit_date = last_commit_date

    except Exception as e:
        print(f"Error fetching commit dates for {owner}/{repo}: {e}")

    return first_commit_date, last_commit_date


def get_github_commit_dates_from_url(url: str) -> tuple[str | None, str | None]:
    """Fetch commit dates from a GitHub URL.

    Args:
        url: GitHub repository URL

    Returns:
        Tuple of (first_commit_date, last_commit_date) in YYYY-MM-DD:HH-MM-SS format,
        or (None, None) if the URL is not a GitHub URL or dates cannot be fetched.
    """
    _, is_github, owner, repo = parse_github_url(url)
    if not is_github or not owner or not repo:
        return None, None
    return get_github_commit_dates(owner, repo)


def get_github_latest_release(owner: str, repo: str) -> tuple[str | None, str | None]:
    """Fetch the latest release date and version from GitHub Releases API.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name

    Returns:
        Tuple of (release_date, version) in (YYYY-MM-DD:HH-MM-SS, tag_name) format,
        or (None, None) if no releases are found.
    """
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = requests.get(api_url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            published_at = data.get("published_at")
            tag_name = data.get("tag_name")
            if published_at:
                release_date = format_commit_date(published_at)
                return release_date, tag_name
        elif response.status_code == 404:
            # No releases found, try tags as fallback
            return get_github_latest_tag(owner, repo)
    except Exception as e:
        print(f"Error fetching GitHub release for {owner}/{repo}: {e}")

    return None, None


def get_github_latest_tag(owner: str, repo: str) -> tuple[str | None, str | None]:
    """Fetch the latest tag date and version from GitHub Tags API (fallback).

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name

    Returns:
        Tuple of (tag_date, tag_name) in (YYYY-MM-DD:HH-MM-SS, tag_name) format,
        or (None, None) if no tags are found.
    """
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        response = requests.get(api_url, headers=HEADERS, params={"per_page": 1}, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                tag = data[0]
                tag_name = tag.get("name")
                commit_sha = tag.get("commit", {}).get("sha")
                if commit_sha:
                    # Fetch the commit to get the date
                    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
                    commit_response = requests.get(commit_url, headers=HEADERS, timeout=10)
                    if commit_response.status_code == 200:
                        commit_data = commit_response.json()
                        commit_date = (
                            commit_data.get("commit", {}).get("committer", {}).get("date")
                            or commit_data.get("commit", {}).get("author", {}).get("date")
                        )
                        if commit_date:
                            return format_commit_date(commit_date), tag_name
    except Exception as e:
        print(f"Error fetching GitHub tags for {owner}/{repo}: {e}")

    return None, None


def get_npm_latest_release(package_name: str) -> tuple[str | None, str | None]:
    """Fetch the latest release date and version from npm registry.

    Args:
        package_name: npm package name (e.g., 'lodash' or '@scope/package')

    Returns:
        Tuple of (release_date, version) in (YYYY-MM-DD:HH-MM-SS, version) format,
        or (None, None) if the package is not found.
    """
    try:
        # Handle scoped packages
        encoded_name = package_name.replace("/", "%2F")
        api_url = f"https://registry.npmjs.org/{encoded_name}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            dist_tags = data.get("dist-tags", {})
            latest_version = dist_tags.get("latest")
            if latest_version:
                time_info = data.get("time", {})
                release_time = time_info.get(latest_version)
                if release_time:
                    release_date = format_commit_date(release_time)
                    return release_date, latest_version
    except Exception as e:
        print(f"Error fetching npm release for {package_name}: {e}")

    return None, None


def get_pypi_latest_release(package_name: str) -> tuple[str | None, str | None]:
    """Fetch the latest release date and version from PyPI.

    Args:
        package_name: PyPI package name

    Returns:
        Tuple of (release_date, version) in (YYYY-MM-DD:HH-MM-SS, version) format,
        or (None, None) if the package is not found.
    """
    try:
        api_url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            version = data.get("info", {}).get("version")
            releases = data.get("releases", {})
            if version and version in releases:
                release_files = releases[version]
                if release_files:
                    # Get the upload time from the first file
                    upload_time = release_files[0].get("upload_time_iso_8601")
                    if upload_time:
                        release_date = format_commit_date(upload_time)
                        return release_date, version
    except Exception as e:
        print(f"Error fetching PyPI release for {package_name}: {e}")

    return None, None


def get_crates_latest_release(crate_name: str) -> tuple[str | None, str | None]:
    """Fetch the latest release date and version from crates.io (Rust).

    Args:
        crate_name: Rust crate name

    Returns:
        Tuple of (release_date, version) in (YYYY-MM-DD:HH-MM-SS, version) format,
        or (None, None) if the crate is not found.
    """
    try:
        api_url = f"https://crates.io/api/v1/crates/{crate_name}"
        headers_with_ua = {"User-Agent": USER_AGENT}
        response = requests.get(api_url, headers=headers_with_ua, timeout=10)

        if response.status_code == 200:
            data = response.json()
            crate_info = data.get("crate", {})
            newest_version = crate_info.get("newest_version")
            updated_at = crate_info.get("updated_at")
            if newest_version and updated_at:
                release_date = format_commit_date(updated_at)
                return release_date, newest_version
    except Exception as e:
        print(f"Error fetching crates.io release for {crate_name}: {e}")

    return None, None


def get_homebrew_latest_release(formula_name: str) -> tuple[str | None, str | None]:
    """Fetch the latest version from Homebrew Formulae API.

    Note: Homebrew doesn't provide release dates, only version numbers.
    We return the version but no date.

    Args:
        formula_name: Homebrew formula name

    Returns:
        Tuple of (None, version) - no date available from Homebrew API,
        or (None, None) if the formula is not found.
    """
    try:
        api_url = f"https://formulae.brew.sh/api/formula/{formula_name}.json"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            versions = data.get("versions", {})
            stable = versions.get("stable")
            if stable:
                # Homebrew doesn't provide release dates, but we have the version
                return None, stable
    except Exception as e:
        print(f"Error fetching Homebrew release for {formula_name}: {e}")

    return None, None


def get_github_readme_version(owner: str, repo: str) -> tuple[str | None, str | None]:
    """Fallback: Try to extract version from GitHub README or CHANGELOG.

    Searches for version patterns like "v1.2.3", "version 1.2.3", etc.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name

    Returns:
        Tuple of (None, version) - no reliable date from README parsing,
        or (None, None) if no version found.
    """
    try:
        # Try to fetch README
        for readme_name in ["README.md", "README", "readme.md", "Readme.md"]:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{readme_name}"
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # README content is base64 encoded
                import base64

                content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")

                # Search for version patterns
                version_patterns = [
                    r"version[:\s]+[\"']?v?(\d+\.\d+(?:\.\d+)?)[\"']?",
                    r"latest[:\s]+[\"']?v?(\d+\.\d+(?:\.\d+)?)[\"']?",
                    r"\[v?(\d+\.\d+(?:\.\d+)?)\]",  # Badge format
                    r"v(\d+\.\d+(?:\.\d+)?)",  # Simple v1.2.3
                ]
                for pattern in version_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        return None, f"v{match.group(1)}"
                break
    except Exception as e:
        print(f"Error fetching README for {owner}/{repo}: {e}")

    return None, None


def detect_package_info(url: str, display_name: str = "") -> tuple[str | None, str | None]:
    """Detect package registry and name from URL or display name.

    Args:
        url: Primary URL of the resource
        display_name: Display name of the resource (for npm/pypi detection)

    Returns:
        Tuple of (registry_type, package_name) where registry_type is one of:
        'npm', 'pypi', 'crates', 'homebrew', 'github-releases', or None if not detected.
    """
    url_lower = url.lower() if url else ""

    # Check for npm package URL
    npm_patterns = [
        r"npmjs\.com/package/([^/?\s]+)",
        r"npmjs\.org/package/([^/?\s]+)",
    ]
    for pattern in npm_patterns:
        match = re.search(pattern, url_lower)
        if match:
            return "npm", match.group(1)

    # Check for PyPI package URL
    pypi_patterns = [
        r"pypi\.org/project/([^/?\s]+)",
        r"pypi\.python\.org/pypi/([^/?\s]+)",
    ]
    for pattern in pypi_patterns:
        match = re.search(pattern, url_lower)
        if match:
            return "pypi", match.group(1)

    # Check for crates.io (Rust) URL
    crates_patterns = [
        r"crates\.io/crates/([^/?\s]+)",
    ]
    for pattern in crates_patterns:
        match = re.search(pattern, url_lower)
        if match:
            return "crates", match.group(1)

    # Check for Homebrew URL
    homebrew_patterns = [
        r"formulae\.brew\.sh/formula/([^/?\s]+)",
        r"brew\.sh/.*formula.*[/=]([^/?\s&]+)",
    ]
    for pattern in homebrew_patterns:
        match = re.search(pattern, url_lower)
        if match:
            return "homebrew", match.group(1)

    # Check for GitHub URL - use releases API
    _, is_github, owner, repo = parse_github_url(url)
    if is_github and owner and repo:
        return "github-releases", f"{owner}/{repo}"

    return None, None


def get_latest_release_info(
    url: str, display_name: str = ""
) -> tuple[str | None, str | None, str | None]:
    """Fetch the latest release date and version from the appropriate registry.

    Tries multiple sources in order of reliability:
    1. Package registries (npm, PyPI, crates.io, Homebrew)
    2. GitHub Releases API
    3. GitHub Tags API (fallback)
    4. README version parsing (last resort)

    Args:
        url: Primary URL of the resource
        display_name: Display name of the resource

    Returns:
        Tuple of (release_date, version, source) where:
        - release_date is in YYYY-MM-DD:HH-MM-SS format (may be None for some sources)
        - version is the version/tag string
        - source is 'npm', 'pypi', 'crates', 'homebrew', 'github-releases', 'readme', or None
    """
    registry_type, package_name = detect_package_info(url, display_name)

    if registry_type == "npm":
        release_date, version = get_npm_latest_release(package_name)
        if release_date:
            return release_date, version, "npm"

    elif registry_type == "pypi":
        release_date, version = get_pypi_latest_release(package_name)
        if release_date:
            return release_date, version, "pypi"

    elif registry_type == "crates":
        release_date, version = get_crates_latest_release(package_name)
        if release_date:
            return release_date, version, "crates"

    elif registry_type == "homebrew":
        release_date, version = get_homebrew_latest_release(package_name)
        if version:
            # Homebrew doesn't provide dates, but we have the version
            return release_date, version, "homebrew"

    elif registry_type == "github-releases":
        owner, repo = package_name.split("/", 1)
        release_date, version = get_github_latest_release(owner, repo)
        if release_date:
            return release_date, version, "github-releases"

        # Fallback: Try README parsing for version (no date available)
        _, readme_version = get_github_readme_version(owner, repo)
        if readme_version:
            return None, readme_version, "readme"

    return None, None, None


def validate_url(url, max_retries=5):
    """
    Validate a URL with exponential backoff retry logic.
    Returns (is_valid, status_code, license_info, last_modified).
    """
    if not url or url.strip() == "":
        return True, None, None, None  # Empty URLs are considered valid

    # Convert GitHub URLs to API endpoints
    api_url, is_github, owner, repo = parse_github_url(url)

    for attempt in range(max_retries):
        try:
            if is_github:
                response = requests.get(api_url, headers=HEADERS, timeout=10)
            else:
                response = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)

            if is_github and VERBOSE:
                print(
                    f"[github] url={url} api={api_url} status={response.status_code} "
                    f"reason={response.reason}"
                )
                try:
                    print(f"[github-body] {response.json()}")
                except Exception:
                    print(f"[github-body-raw] {response.text}")

            # Check if we hit GitHub rate limit
            if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                if remaining == 0:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                    print(f"GitHub rate limit hit. Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue

            # Success cases
            if response.status_code < 400:
                license_info = None
                last_modified = None
                if is_github and response.status_code == 200:
                    # Extract owner/repo/path from original URL
                    # Try to match file URL first
                    file_match = re.match(
                        r"https://github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)", url
                    )
                    if file_match:
                        owner, repo, path = file_match.groups()
                        license_info = get_github_license(owner, repo)
                        last_modified = get_github_last_modified(owner, repo, path)
                    else:
                        # Try repository URL
                        repo_match = re.match(r"https://github\.com/([^/]+)/([^/]+)", url)
                        if repo_match:
                            owner, repo = repo_match.groups()
                            license_info = get_github_license(owner, repo)
                            last_modified = get_github_last_modified(owner, repo)
                return True, response.status_code, license_info, last_modified

            # Client errors (except rate limit) don't need retry
            if 400 <= response.status_code < 500 and response.status_code != 403:
                print(f"Client error {response.status_code} {response.reason} for URL: {url}")
                return False, response.status_code, None, None

            # Server errors - retry with backoff
            if response.status_code >= 500 and attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue

            return False, response.status_code, None, None

        except requests.exceptions.RequestException as e:
            print(f"[error] request failed for {url}: {e}")
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            return False, str(e), None, None

    return False, "Max retries exceeded", None, None


def validate_links(csv_file, max_links=None, ignore_overrides=False, verbose=False):
    """
    Validate links in the CSV file and update the Active status and timestamp.
    """
    global VERBOSE
    VERBOSE = verbose

    # Load overrides
    overrides = {} if ignore_overrides else load_overrides()

    print(f"GITHUB_TOKEN available: {'yes' if GITHUB_TOKEN else 'no'}")

    # Read the CSV file
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    fieldnames, rows = ensure_stale_column(fieldnames, rows)

    total_resources = len(rows)
    processed = 0
    broken_links = []
    newly_broken_links = []  # Track newly discovered broken links
    github_links = 0
    github_api_calls = 0
    override_count = 0
    locked_field_count = 0
    last_modified_updates = 0
    stale_resources = []
    newly_stale_resources = []

    print(f"Starting validation of {total_resources} resources...")
    if overrides and not ignore_overrides:
        print(f"Loaded {len(overrides)} resource overrides")

    for _, row in enumerate(rows):
        if max_links and processed >= max_links:
            print(f"\nReached maximum link limit ({max_links}). Stopping validation.")
            break

        # Apply overrides
        row, locked_fields, skip_validation = apply_overrides(row, overrides)
        if locked_fields:
            override_count += 1
            locked_field_count += len(locked_fields)

        # Skip entire validation if skip_validation is true
        if skip_validation:
            print(f"Skipping {row['Display Name']} - validation disabled by override")
            continue

        # Skip validation for locked fields
        if "active" in locked_fields and "last_checked" in locked_fields:
            print(f"Skipping {row['Display Name']} - fields locked by override")
            continue

        primary_url = row.get(PRIMARY_LINK_HEADER_NAME, "").strip()
        # secondary_url = row.get(SECONDARY_LINK_HEADER_NAME, "").strip()  # Ignoring secondary URLs

        # Track GitHub links
        is_github_link = "github.com" in primary_url.lower()
        if is_github_link:
            github_links += 1

        # Validate primary URL
        primary_valid, primary_status, license_info, last_modified = validate_url(primary_url)

        previous_stale = row.get(STALE_HEADER_NAME, "").upper() == "TRUE"

        # Update license if found and not locked
        if license_info and "license" not in locked_fields:
            row[LICENSE_HEADER_NAME] = license_info
            github_api_calls += 1

        # Update last modified if found and not locked
        if last_modified and "last_modified" not in locked_fields:
            row[LAST_MODIFIED_HEADER_NAME] = last_modified
            github_api_calls += 1
            last_modified_updates += 1

        # Validate secondary URL if present
        # secondary_valid = True
        # if secondary_url:
        #     secondary_valid, _, _, _ = validate_url(secondary_url)  # Ignoring secondary URLs

        # Check previous status before updating
        was_active = row.get(ACTIVE_HEADER_NAME, "TRUE").upper() == "TRUE"
        # Update Active status if not locked
        if "active" not in locked_fields:
            # is_active = primary_valid and secondary_valid  # Original logic included secondary URL
            is_active = primary_valid  # Now only depends on primary URL validity
            row[ACTIVE_HEADER_NAME] = "TRUE" if is_active else "FALSE"
        else:
            is_active = row[ACTIVE_HEADER_NAME].upper() == "TRUE"

        # Update timestamp if not locked
        if "last_checked" not in locked_fields:
            row[LAST_CHECKED_HEADER_NAME] = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")

        # Track broken links
        if not is_active and "active" not in locked_fields:
            link_info = {
                "name": row.get("Display Name", "Unknown"),
                "primary_url": primary_url,
                "primary_status": primary_status,
                # "secondary_url": secondary_url if not secondary_valid else None,
                # No longer tracking secondary URLs
            }
            broken_links.append(link_info)

            # Check if this is a newly discovered broken link
            if was_active:
                newly_broken_links.append(link_info)
                print(f"❌ NEW: {row.get('Display Name', 'Unknown')}: {primary_status}")
            else:
                print(f"Already broken: {row.get('Display Name', 'Unknown')}: {primary_status}")
        elif not is_active and "active" in locked_fields:
            print(f"🔒 {row.get('Display Name', 'Unknown')}: Inactive (locked by override)")
        else:
            print(f"✓ {row.get('Display Name', 'Unknown')}")

        last_modified_value = last_modified or row.get(LAST_MODIFIED_HEADER_NAME, "")
        parsed_last_modified = parse_last_modified_date(last_modified_value)
        days_since = (
            (datetime.now(UTC) - parsed_last_modified).days if parsed_last_modified else "unknown"
        )
        print(
            f"    Last Modified: {last_modified_value if last_modified_value else 'n/a'}"
            f" - {days_since} days"
        )
        if is_github_link and not last_modified_value:
            print("    (debug) missing last_modified from GitHub response")

        if is_github_link and is_active:
            if is_stale(parsed_last_modified):
                row[STALE_HEADER_NAME] = "TRUE"
            else:
                row[STALE_HEADER_NAME] = "FALSE"

        current_stale = row.get(STALE_HEADER_NAME, "").upper() == "TRUE"
        if current_stale:
            stale_resources.append(
                {
                    "name": row.get("Display Name", "Unknown"),
                    "days_since": days_since,
                }
            )
        if current_stale and not previous_stale:
            newly_stale_resources.append(
                {
                    "name": row.get("Display Name", "Unknown"),
                    "days_since": days_since,
                }
            )

        processed += 1

    # Write updated CSV
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        assert fieldnames is not None
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    print("\nValidation complete!")
    print(f"Total resources: {total_resources}")
    print(f"Processed: {processed}")
    print(f"GitHub links: {github_links}")
    print(f"GitHub API calls: {github_api_calls}")
    if last_modified_updates:
        print(f"Last modified dates fetched: {last_modified_updates}")
    if override_count:
        print(f"Resources with overrides: {override_count}")
        print(f"Total locked fields: {locked_field_count}")
    print(f"Total broken links: {len(broken_links)}")
    print(f"Newly broken links: {len(newly_broken_links)}")
    print(f"Total stale resources: {len(stale_resources)}")

    # Print broken links
    if newly_broken_links:
        print("\nNEWLY broken links:")
        for link in newly_broken_links:
            print(f"  - {link['name']}: {link['primary_url']} ({link['primary_status']})")

    if broken_links:
        print("\nAll broken links:")
        for link in broken_links:
            print(f"  - {link['name']}: {link['primary_url']} ({link['primary_status']})")
            # if link.get("secondary_url"):  # No longer reporting secondary URLs
            #     print(f"    Secondary: {link['secondary_url']}")

    if stale_resources:
        print("\nStale resources:")
        for res in stale_resources:
            print(f"  - {res['name']}: {res['days_since']} days")
    else:
        print("\nStale resources: none")

    if newly_stale_resources:
        print("\nNewly stale resources:")
        for res in newly_stale_resources:
            print(f"  - {res['name']}: {res['days_since']} days")
    else:
        print("\nNewly stale resources: none")

    return {
        "total": total_resources,
        "processed": processed,
        "broken": len(broken_links),
        "newly_broken": len(newly_broken_links),
        "github_links": github_links,
        "github_api_calls": github_api_calls,
        "override_count": override_count,
        "locked_fields": locked_field_count,
        "broken_links": broken_links,
        "newly_broken_links": newly_broken_links,
        "timestamp": datetime.now().strftime("%Y-%m-%d:%H-%M-%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="Validate links in THE_RESOURCES_TABLE.csv")
    parser.add_argument("--max-links", type=int, help="Maximum number of links to validate")
    parser.add_argument("--github-action", action="store_true", help="Run in GitHub Action mode")
    parser.add_argument(
        "--ignore-overrides", action="store_true", help="Ignore override configuration"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose GitHub API responses (for debugging)",
    )
    args = parser.parse_args()

    csv_file = INPUT_FILE
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)

    try:
        results = validate_links(csv_file, args.max_links, args.ignore_overrides, args.verbose)

        if args.github_action:
            # Output JSON for GitHub Action
            # Always print the JSON results for capture by the workflow
            print(json.dumps(results))

            # Also write to GITHUB_OUTPUT if available
            # github_output = os.getenv("GITHUB_OUTPUT")
            # if github_output:
            with open("validation_results.json", "w") as f:
                json.dump(results, f)

            # Set action failure if broken links found
            if results["newly_broken"] > 0:
                print(f"\n::error::Found {results['newly_broken']} newly broken links")
                sys.exit(1)

        # Exit with error code if broken links found
        sys.exit(1 if results["newly_broken"] > 0 else 0)

    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
