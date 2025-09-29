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
from datetime import datetime

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
    """Apply overrides to a row if the resource ID has overrides configured."""
    resource_id = row.get(ID_HEADER_NAME, "")
    if not resource_id or resource_id not in overrides:
        return row, set(), False

    override_config = overrides[resource_id]
    locked_fields = set()
    skip_validation = override_config.get("skip_validation", False)

    # Apply each override
    for field, value in override_config.items():
        if field.endswith("_locked"):
            # Track locked fields
            base_field = field.replace("_locked", "")
            if override_config.get(field, False):
                locked_fields.add(base_field)
        elif field not in ["notes", "skip_validation"]:  # Skip notes and skip_validation fields
            # Apply override value
            if field == "license":
                row[LICENSE_HEADER_NAME] = value
            elif field == "active":
                row[ACTIVE_HEADER_NAME] = value
            elif field == "last_checked":
                row[LAST_CHECKED_HEADER_NAME] = value
            elif field == "last_modified":
                row[LAST_MODIFIED_HEADER_NAME] = value
            elif field == "description":
                row["Description"] = value

    return row, locked_fields, skip_validation


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
        commit_date = commit.get("committer", {}).get("date")
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
        if response.status_code == 200:
            commit_date = get_committer_date_from_response(response)
            if commit_date:
                return format_commit_date(commit_date)
    except Exception as e:
        print(f"Error fetching last modified date for {owner}/{repo}: {e}")
    return None


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
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            return False, str(e), None, None

    return False, "Max retries exceeded", None, None


def validate_links(csv_file, max_links=None, ignore_overrides=False):
    """
    Validate links in the CSV file and update the Active status and timestamp.
    """
    # Load overrides
    overrides = {} if ignore_overrides else load_overrides()

    # Read the CSV file
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    total_resources = len(rows)
    processed = 0
    broken_links = []
    newly_broken_links = []  # Track newly discovered broken links
    github_links = 0
    github_api_calls = 0
    override_count = 0
    locked_field_count = 0
    last_modified_updates = 0

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
        if "github.com" in primary_url:
            github_links += 1

        # Validate primary URL
        primary_valid, primary_status, license_info, last_modified = validate_url(primary_url)

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
    args = parser.parse_args()

    csv_file = INPUT_FILE
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)

    try:
        results = validate_links(csv_file, args.max_links, args.ignore_overrides)

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
