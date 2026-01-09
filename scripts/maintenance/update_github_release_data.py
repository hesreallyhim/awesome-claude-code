#!/usr/bin/env python3
"""
Update Last Modified and GitHub release info for active GitHub repos in THE_RESOURCES_TABLE.csv.

Uses two GitHub REST API calls per repository:
- /repos/{owner}/{repo}/commits?per_page=1 (latest commit on default branch)
- /repos/{owner}/{repo}/releases/latest (latest release)
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

from scripts.utils.repo_root import find_repo_root

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


REPO_ROOT = find_repo_root(Path(__file__))
DEFAULT_CSV_PATH = os.path.join(REPO_ROOT, "THE_RESOURCES_TABLE.csv")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
USER_AGENT = "awesome-claude-code GitHub Release Sync/1.0"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def format_commit_date(commit_date: str | None) -> str | None:
    if not commit_date:
        return None
    try:
        dt = datetime.fromisoformat(commit_date.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d:%H-%M-%S")
    except ValueError:
        return None


def parse_github_repo(url: str | None) -> tuple[str | None, str | None]:
    if not url or not isinstance(url, str):
        return None, None
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url.strip())
    if not match:
        return None, None
    owner, repo = match.groups()
    repo = repo.split("?", 1)[0].split("#", 1)[0]
    repo = repo.removesuffix(".git")
    return owner, repo


def github_get(url: str, params: dict | None = None) -> requests.Response:
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        sleep_time = max(reset_time - int(time.time()), 0) + 1
        logger.warning("GitHub rate limit hit. Sleeping for %s seconds.", sleep_time)
        time.sleep(sleep_time)
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    return response


def fetch_last_commit_date(owner: str, repo: str) -> tuple[str | None, str]:
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = github_get(api_url, params={"per_page": 1})

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            commit = data[0]
            commit_date = (
                commit.get("commit", {}).get("committer", {}).get("date")
                or commit.get("commit", {}).get("author", {}).get("date")
                or commit.get("committer", {}).get("date")
                or commit.get("author", {}).get("date")
            )
            return format_commit_date(commit_date), "ok"
        return None, "empty"
    if response.status_code == 404:
        return None, "not_found"
    return None, f"http_{response.status_code}"


def fetch_latest_release(owner: str, repo: str) -> tuple[str | None, str | None, str]:
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = github_get(api_url)

    if response.status_code == 200:
        data = response.json()
        published_at = data.get("published_at") or data.get("created_at")
        return format_commit_date(published_at), data.get("tag_name"), "ok"
    if response.status_code == 404:
        return None, None, "no_release"
    return None, None, f"http_{response.status_code}"


def update_release_data(csv_path: str, max_rows: int | None = None, dry_run: bool = False) -> None:
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    required_columns = ["Last Modified", "Latest Release", "Release Version", "Release Source"]
    for column in required_columns:
        if column not in fieldnames:
            fieldnames.append(column)

    processed = 0
    skipped = 0
    updated = 0
    errors = 0

    for _, row in enumerate(rows):
        if max_rows and processed >= max_rows:
            logger.info("Reached max limit (%s). Stopping.", max_rows)
            break

        if row.get("Active", "").strip().upper() != "TRUE":
            skipped += 1
            continue

        primary_link = (row.get("Primary Link") or "").strip()
        owner, repo = parse_github_repo(primary_link)
        if not owner or not repo:
            skipped += 1
            continue

        processed += 1
        display_name = row.get("Display Name", primary_link)
        logger.info("[%s] Updating %s (%s/%s)", processed, display_name, owner, repo)

        row_changed = False

        commit_date, commit_status = fetch_last_commit_date(owner, repo)
        if commit_status == "not_found":
            logger.warning("Repository not found: %s/%s", owner, repo)
        elif commit_date and row.get("Last Modified") != commit_date:
            row["Last Modified"] = commit_date
            row_changed = True

        release_date, release_version, release_status = fetch_latest_release(owner, repo)
        if release_status == "no_release":
            if row.get("Latest Release") or row.get("Release Version") or row.get("Release Source"):
                row["Latest Release"] = ""
                row["Release Version"] = ""
                row["Release Source"] = ""
                row_changed = True
        elif release_status == "ok":
            new_release_date = release_date or ""
            new_release_version = release_version or ""
            new_release_source = "github-releases" if (release_date or release_version) else ""
            if row.get("Latest Release") != new_release_date:
                row["Latest Release"] = new_release_date
                row_changed = True
            if row.get("Release Version") != new_release_version:
                row["Release Version"] = new_release_version
                row_changed = True
            if row.get("Release Source") != new_release_source:
                row["Release Source"] = new_release_source
                row_changed = True
        else:
            logger.warning(
                "Release fetch failed for %s/%s (status: %s)",
                owner,
                repo,
                release_status,
            )
            errors += 1

        if row_changed:
            updated += 1

    if dry_run:
        logger.info("[DRY RUN] No changes written to CSV.")
        return

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Updated rows: %s", updated)
    logger.info("Skipped rows: %s", skipped)
    logger.info("Errors: %s", errors)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update GitHub commit and release data for active resources"
    )
    parser.add_argument(
        "--csv-file",
        default=DEFAULT_CSV_PATH,
        help="Path to THE_RESOURCES_TABLE.csv",
    )
    parser.add_argument("--max", type=int, help="Process at most N resources")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes")
    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        logger.error("CSV file not found: %s", args.csv_file)
        sys.exit(1)

    update_release_data(args.csv_file, max_rows=args.max, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
