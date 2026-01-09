#!/usr/bin/env python3
"""
Repository health check script for the Awesome Claude Code repository.

This script checks active GitHub repositories listed in THE_RESOURCES_TABLE.csv for:
- Number of open issues
- Date of last push or PR merge (last updated)

Exits with error if any repository:
- Has not been updated in over 6 months AND
- Has more than 2 open issues

If a repository has been deleted, the script continues without exiting.
"""

import argparse
import csv
import logging
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

from scripts.utils.github_utils import parse_github_url
from scripts.utils.repo_root import find_repo_root

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
USER_AGENT = "awesome-claude-code Repository Health Check/1.0"
REPO_ROOT = find_repo_root(Path(__file__))
INPUT_FILE = REPO_ROOT / "THE_RESOURCES_TABLE.csv"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# Thresholds
MONTHS_THRESHOLD = 6
OPEN_ISSUES_THRESHOLD = 2


def get_repo_info(owner, repo):
    """
    Fetch repository information from GitHub API.
    Returns a dict with:
    - open_issues: number of open issues
    - last_updated: date of last push (ISO format string)
    - exists: whether the repo exists (False if 404)
    Returns None if API call fails for other reasons.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)

        if response.status_code == 404:
            logger.warning(f"Repository {owner}/{repo} not found (deleted or private)")
            return {"exists": False, "open_issues": 0, "last_updated": None}

        if response.status_code == 403:
            logger.error(f"Rate limit or forbidden for {owner}/{repo}")
            return None

        if response.status_code != 200:
            logger.error(f"Failed to fetch {owner}/{repo}: HTTP {response.status_code}")
            return None

        data = response.json()

        return {
            "exists": True,
            "open_issues": data.get("open_issues_count", data.get("open_issues", 0)),
            "last_updated": data.get("pushed_at"),  # ISO 8601 timestamp
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching repository info for {owner}/{repo}: {e}")
        return None


def is_outdated(last_updated_str, months_threshold):
    """
    Check if a repository hasn't been updated in more than months_threshold months.
    """
    if not last_updated_str:
        return True  # Consider it outdated if we don't have a date

    try:
        last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        threshold_date = now - timedelta(days=months_threshold * 30)
        return last_updated < threshold_date
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not parse date '{last_updated_str}': {e}")
        return True


def check_repos_health(
    csv_file, months_threshold=MONTHS_THRESHOLD, issues_threshold=OPEN_ISSUES_THRESHOLD
):
    """
    Check health of all active GitHub repositories in the CSV.
    Returns a list of problematic repos.
    """
    problematic_repos = []
    checked_repos = 0
    deleted_repos = []

    logger.info(f"Reading repository list from {csv_file}")

    try:
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Check if Active is TRUE
                active = row.get("Active", "").strip().upper()
                if active != "TRUE":
                    continue

                primary_link = row.get("Primary Link", "").strip()
                if not primary_link:
                    continue

                # Extract owner and repo from GitHub URL
                _, is_github, owner, repo = parse_github_url(primary_link)
                if not is_github or not owner or not repo:
                    # Not a GitHub repository URL
                    continue

                checked_repos += 1
                resource_name = row.get("Display Name", primary_link)
                logger.info(f"Checking {owner}/{repo} ({resource_name})")

                # Get repository information
                repo_info = get_repo_info(owner, repo)

                if repo_info is None:
                    # API error - log but continue
                    logger.warning(f"Could not fetch info for {owner}/{repo}, skipping")
                    continue

                if not repo_info["exists"]:
                    # Repository deleted - log but continue
                    deleted_repos.append(
                        {"name": resource_name, "url": primary_link, "owner": owner, "repo": repo}
                    )
                    continue

                # Check if repo is problematic
                open_issues = repo_info["open_issues"]
                last_updated = repo_info["last_updated"]
                outdated = is_outdated(last_updated, months_threshold)

                if outdated and open_issues > issues_threshold:
                    problematic_repos.append(
                        {
                            "name": resource_name,
                            "url": primary_link,
                            "owner": owner,
                            "repo": repo,
                            "open_issues": open_issues,
                            "last_updated": last_updated,
                        }
                    )
                    logger.warning(
                        f"⚠️  {owner}/{repo}: "
                        f"Last updated {last_updated or 'unknown'}, "
                        f"{open_issues} open issues"
                    )

    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        sys.exit(1)

    logger.info(f"\n{'=' * 60}")
    logger.info("Summary:")
    logger.info(f"  Total active GitHub repositories checked: {checked_repos}")
    logger.info(f"  Deleted/unavailable repositories: {len(deleted_repos)}")
    logger.info(f"  Problematic repositories: {len(problematic_repos)}")

    if deleted_repos:
        logger.info(f"\n{'=' * 60}")
        logger.info("Deleted/Unavailable Repositories:")
        for repo in deleted_repos:
            logger.info(f"  - {repo['name']} ({repo['owner']}/{repo['repo']})")

    return problematic_repos


def main():
    parser = argparse.ArgumentParser(
        description="Check health of GitHub repositories in THE_RESOURCES_TABLE.csv"
    )
    parser.add_argument(
        "--csv-file",
        default=INPUT_FILE,
        help=f"Path to CSV file (default: {INPUT_FILE})",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=MONTHS_THRESHOLD,
        help=f"Months threshold for outdated repos (default: {MONTHS_THRESHOLD})",
    )
    parser.add_argument(
        "--issues",
        type=int,
        default=OPEN_ISSUES_THRESHOLD,
        help=f"Open issues threshold (default: {OPEN_ISSUES_THRESHOLD})",
    )

    args = parser.parse_args()

    problematic_repos = check_repos_health(args.csv_file, args.months, args.issues)

    if problematic_repos:
        logger.error(f"\n{'=' * 60}")
        logger.error("❌ HEALTH CHECK FAILED")
        logger.error(
            f"Found {len(problematic_repos)} repository(ies) that have not been updated in over "
            f"{args.months} months and have more than {args.issues} open issues:\n"
        )

        for repo in problematic_repos:
            logger.error(f"  • {repo['name']}")
            logger.error(f"    URL: {repo['url']}")
            logger.error(f"    Last updated: {repo['last_updated'] or 'Unknown'}")
            logger.error(f"    Open issues: {repo['open_issues']}")
            logger.error("")

        sys.exit(1)
    else:
        logger.info(f"\n{'=' * 60}")
        logger.info("✅ HEALTH CHECK PASSED")
        logger.info("All active repositories are healthy!")
        sys.exit(0)


if __name__ == "__main__":
    main()
