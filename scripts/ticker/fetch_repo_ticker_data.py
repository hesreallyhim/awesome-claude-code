#!/usr/bin/env python3
"""
Fetch GitHub repository data for the stock ticker banner.

This script queries the GitHub Search API for repositories matching
"claude code" or "claude-code" in their name, readme, or description,
calculates deltas compared to previous data, and saves the results to CSV.
"""

import csv
import os
import sys
from pathlib import Path
from typing import Any

import requests

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))


def load_previous_data(csv_path: Path) -> dict[str, dict[str, int]]:
    """
    Load previous repository data from CSV file.

    Args:
        csv_path: Path to previous CSV file

    Returns:
        Dictionary mapping full_name to metrics dict
    """
    if not csv_path.exists():
        return {}

    previous = {}
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            previous[row["full_name"]] = {
                "stars": int(row["stars"]),
                "watchers": int(row["watchers"]),
                "forks": int(row["forks"]),
            }

    print(f"✓ Loaded {len(previous)} repositories from previous data")
    return previous


def fetch_repos(token: str) -> list[dict[str, Any]]:
    """
    Fetch repositories from GitHub Search API.

    Args:
        token: GitHub authentication token

    Returns:
        List of repository data dictionaries
    """
    # GitHub Search API endpoint
    url = "https://api.github.com/search/repositories"

    # Search query
    query = '"claude code" claude-code in:name,readme,description'

    # Parameters for the API request
    params: dict[str, str | int] = {
        "q": query,
        "per_page": 100,  # Maximum results per page
        "page": 1,
        "sort": "relevance",  # Sort by relevance (default)
    }

    # Headers with authentication
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        repos = []
        for item in data.get("items", []):
            repos.append(
                {
                    "full_name": item["full_name"],
                    "stars": item["stargazers_count"],
                    "watchers": item["watchers_count"],
                    "forks": item["forks_count"],
                    "url": item["html_url"],
                }
            )

        print(f"✓ Fetched {len(repos)} repositories from search")
        return repos

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data from GitHub API: {e}", file=sys.stderr)
        sys.exit(1)


def calculate_deltas(
    repos: list[dict[str, Any]],
    previous: dict[str, dict[str, int]],
) -> list[dict[str, Any]]:
    """
    Calculate deltas for each repository compared to previous data.

    For repos not in previous data:
    - If there is no previous baseline at all, set deltas to 0.
    - Otherwise, treat the repo as new and set deltas to current values.

    Args:
        repos: List of current repository data
        previous: Dictionary of previous repository data
    Returns:
        List of repository data with deltas
    """
    repos_with_deltas = []
    has_previous = bool(previous)

    for repo in repos:
        full_name = repo["full_name"]

        if full_name in previous:
            # Calculate deltas from previous data
            prev = previous[full_name]
            repo["stars_delta"] = repo["stars"] - prev["stars"]
            repo["watchers_delta"] = repo["watchers"] - prev["watchers"]
            repo["forks_delta"] = repo["forks"] - prev["forks"]
        else:
            # New repo vs previous snapshot.
            # If there is no prior snapshot, use 0 deltas as a baseline.
            if not has_previous:
                repo["stars_delta"] = 0
                repo["watchers_delta"] = 0
                repo["forks_delta"] = 0
            else:
                repo["stars_delta"] = repo["stars"]
                repo["watchers_delta"] = repo["watchers"]
                repo["forks_delta"] = repo["forks"]

        repos_with_deltas.append(repo)

    return repos_with_deltas


def save_to_csv(repos: list[dict[str, Any]], output_path: Path) -> None:
    """
    Save repository data to CSV file.

    Args:
        repos: List of repository data dictionaries
        output_path: Path to output CSV file
    """
    # Create data directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    with output_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "full_name",
            "stars",
            "watchers",
            "forks",
            "stars_delta",
            "watchers_delta",
            "forks_delta",
            "url",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(repos)

    print(f"✓ Saved {len(repos)} repositories to {output_path}")


def main() -> None:
    """Main function to orchestrate the data fetching and saving."""
    # Get GitHub token from environment
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("✗ GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Load previous data
    previous_path = REPO_ROOT / "data" / "repo-ticker-previous.csv"
    previous_data = load_previous_data(previous_path)

    # Fetch repository data
    print("Fetching repository data from GitHub API...")
    repos = fetch_repos(token)

    # Calculate deltas
    print("Calculating deltas...")
    repos_with_deltas = calculate_deltas(repos, previous_data)

    # Save to CSV
    output_path = REPO_ROOT / "data" / "repo-ticker.csv"
    save_to_csv(repos_with_deltas, output_path)


if __name__ == "__main__":
    main()
