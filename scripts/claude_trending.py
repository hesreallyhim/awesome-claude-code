#!/usr/bin/env python3
"""
Claude Code Trending Repositories Tracker

This script identifies the top trending repositories related to "Claude Code" based on
a Laplace-smoothed proportional growth metric over the last 24 hours (configurable).

Configuration via environment variables:
  GITHUB_TOKEN: Required. GitHub personal access token for API access.
  WINDOW_HOURS: Optional. Time window in hours for tracking growth (default: 24).
  TOP_N: Optional. Number of top repositories to report (default: 5).
  SEARCH_EXCLUDE_MONET: Optional. Exclude art-related repos (default: true).
  MIN_PUSHED_SINCE: Optional. Minimum days since last push (default: 365).
  SEARCH_QUERIES: Optional. JSON array of custom search queries to override defaults.

Growth Metric:
  - new_stars_24h: Count of WatchEvent within WINDOW_HOURS from repo events API
  - new_forks_24h: Count of new forks within WINDOW_HOURS from forks API
  - star_growth_adj = new_stars_24h / (max(0, total_stars - new_stars_24h) + 10)
  - fork_growth_adj = new_forks_24h / (max(0, total_forks - new_forks_24h) + 5)
  - score = star_growth_adj + 0.5 * fork_growth_adj

Ranking:
  Primary: score (descending)
  Tiebreakers: new_stars_24h (descending), total_stars (descending)

Output:
  trending.csv at repository root with columns:
  generated_at_utc,full_name,html_url,description,language,total_stars,total_forks,
  new_stars_24h,new_forks_24h,star_growth_adj,fork_growth_adj,score
"""

import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

# Configuration from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
WINDOW_HOURS = int(os.getenv("WINDOW_HOURS", "24"))
TOP_N = int(os.getenv("TOP_N", "5"))
SEARCH_EXCLUDE_MONET = os.getenv("SEARCH_EXCLUDE_MONET", "true").lower() == "true"
MIN_PUSHED_SINCE = int(os.getenv("MIN_PUSHED_SINCE", "365"))
SEARCH_QUERIES_JSON = os.getenv("SEARCH_QUERIES", "")

# API settings
API_BASE = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# Default search queries
DEFAULT_QUERIES = [
    '"Claude Code" in:name,description,readme fork:false archived:false',
    "topic:claude-code fork:false archived:false",
    "topic:claude fork:false archived:false pushed:>2024-01-01",
    '"claude" "vscode" in:readme fork:false archived:false',
    '"claude" "code" in:readme fork:false archived:false',
]

# Rate limit handling
RATE_LIMIT_SLEEP = 2
MAX_RETRIES = 3


def log(msg: str) -> None:
    """Print log message with timestamp."""
    print(f"[{datetime.now(UTC).isoformat()}] {msg}", file=sys.stderr)


def make_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make GitHub API request with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if response.status_code == 403 and "rate limit" in response.text.lower():
                log("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                continue
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RATE_LIMIT_SLEEP * (attempt + 1))
            else:
                return None
    return None


def search_repositories(query: str) -> list[dict[str, Any]]:
    """Search for repositories using GitHub search API."""
    log(f"Searching: {query}")
    repos = []
    page = 1
    while True:
        data = make_request(
            f"{API_BASE}/search/repositories",
            params={"q": query, "per_page": 100, "page": page, "sort": "updated"},
        )
        if not data or "items" not in data:
            break
        repos.extend(data["items"])
        if len(data["items"]) < 100:
            break
        page += 1
        time.sleep(RATE_LIMIT_SLEEP)
    log(f"Found {len(repos)} repositories for query")
    return repos


def get_candidate_repos() -> list[dict[str, Any]]:
    """Fetch candidate repositories using multiple queries."""
    queries = DEFAULT_QUERIES
    if SEARCH_QUERIES_JSON:
        try:
            queries = json.loads(SEARCH_QUERIES_JSON)
        except json.JSONDecodeError:
            log("Warning: Invalid SEARCH_QUERIES JSON, using defaults")

    all_repos: dict[str, dict[str, Any]] = {}
    for query in queries:
        repos = search_repositories(query)
        for repo in repos:
            full_name = repo["full_name"]
            if full_name not in all_repos:
                all_repos[full_name] = repo
        time.sleep(RATE_LIMIT_SLEEP)

    log(f"Total unique repositories before filtering: {len(all_repos)}")

    # Apply filters
    cutoff_date = datetime.now(UTC) - timedelta(days=MIN_PUSHED_SINCE)
    filtered_repos = []
    for repo in all_repos.values():
        # Check pushed date
        pushed_at = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
        if pushed_at < cutoff_date:
            continue

        # Exclude Monet art-related repos if configured
        if SEARCH_EXCLUDE_MONET:
            name_lower = repo["name"].lower()
            desc_lower = (repo.get("description") or "").lower()
            if "monet" in name_lower or "monet" in desc_lower:
                continue

        filtered_repos.append(repo)

    log(f"Repositories after filtering: {len(filtered_repos)}")
    return filtered_repos


def count_new_stars(owner: str, repo: str, window_start: datetime) -> int:
    """Count new stars (WatchEvent) within the time window."""
    count = 0
    page = 1
    while True:
        data = make_request(
            f"{API_BASE}/repos/{owner}/{repo}/events", params={"per_page": 100, "page": page}
        )
        if not data:
            break

        found_old = False
        for event in data:
            if event["type"] == "WatchEvent":
                created_at = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
                if created_at >= window_start:
                    count += 1
                else:
                    found_old = True
                    break
            # Check if this event is too old
            event_time = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            if event_time < window_start:
                found_old = True
                break

        if found_old or len(data) < 100:
            break
        page += 1
        time.sleep(RATE_LIMIT_SLEEP)

    return count


def count_new_forks(owner: str, repo: str, window_start: datetime) -> int:
    """Count new forks within the time window."""
    count = 0
    page = 1
    while True:
        data = make_request(
            f"{API_BASE}/repos/{owner}/{repo}/forks",
            params={"sort": "newest", "per_page": 100, "page": page},
        )
        if not data:
            break

        found_old = False
        for fork in data:
            created_at = datetime.fromisoformat(fork["created_at"].replace("Z", "+00:00"))
            if created_at >= window_start:
                count += 1
            else:
                found_old = True
                break

        if found_old or len(data) < 100:
            break
        page += 1
        time.sleep(RATE_LIMIT_SLEEP)

    return count


def calculate_metrics(repo: dict[str, Any], window_start: datetime) -> dict[str, Any]:
    """Calculate growth metrics for a repository."""
    owner = repo["owner"]["login"]
    name = repo["name"]
    full_name = repo["full_name"]

    log(f"Processing {full_name}...")

    total_stars = repo["stargazers_count"]
    total_forks = repo["forks_count"]

    # Count new stars and forks
    new_stars = count_new_stars(owner, name, window_start)
    new_forks = count_new_forks(owner, name, window_start)

    # Calculate adjusted growth metrics with Laplace smoothing
    old_stars = max(0, total_stars - new_stars)
    star_growth_adj = new_stars / (old_stars + 10)

    old_forks = max(0, total_forks - new_forks)
    fork_growth_adj = new_forks / (old_forks + 5)

    # Composite score
    score = star_growth_adj + 0.5 * fork_growth_adj

    return {
        "full_name": full_name,
        "html_url": repo["html_url"],
        "description": (repo.get("description") or "").replace("\n", " ").replace("\r", " "),
        "language": repo.get("language") or "",
        "total_stars": total_stars,
        "total_forks": total_forks,
        "new_stars_24h": new_stars,
        "new_forks_24h": new_forks,
        "star_growth_adj": round(star_growth_adj, 4),
        "fork_growth_adj": round(fork_growth_adj, 4),
        "score": round(score, 4),
    }


def process_repo_parallel(repo: dict[str, Any], window_start: datetime) -> dict[str, Any] | None:
    """Wrapper for parallel processing with error handling."""
    try:
        return calculate_metrics(repo, window_start)
    except Exception as e:
        log(f"Error processing {repo['full_name']}: {e}")
        return None


def main() -> None:
    """Main entry point."""
    if not GITHUB_TOKEN:
        log("ERROR: GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    log("Starting Claude Code trending repositories tracker")
    log(f"Configuration: WINDOW_HOURS={WINDOW_HOURS}, TOP_N={TOP_N}")

    # Calculate time window
    now = datetime.now(UTC)
    window_start = now - timedelta(hours=WINDOW_HOURS)
    log(f"Window: {window_start.isoformat()} to {now.isoformat()}")

    # Get candidate repositories
    candidates = get_candidate_repos()
    if not candidates:
        log("No candidate repositories found")
        sys.exit(1)

    # Process repositories in parallel
    log(f"Processing {len(candidates)} repositories with ThreadPoolExecutor...")
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(process_repo_parallel, repo, window_start): repo for repo in candidates
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    if not results:
        log("No results after processing")
        sys.exit(1)

    # Sort by score (desc), then new_stars_24h (desc), then total_stars (desc)
    results.sort(key=lambda x: (-x["score"], -x["new_stars_24h"], -x["total_stars"]))

    # Take top N
    top_results = results[:TOP_N]
    log(f"Selected top {len(top_results)} repositories")

    # Write CSV
    output_path = "trending.csv"
    fieldnames = [
        "generated_at_utc",
        "full_name",
        "html_url",
        "description",
        "language",
        "total_stars",
        "total_forks",
        "new_stars_24h",
        "new_forks_24h",
        "star_growth_adj",
        "fork_growth_adj",
        "score",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in top_results:
            result["generated_at_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            writer.writerow(result)

    log(f"Wrote {len(top_results)} results to {output_path}")

    # Print summary
    print("\n=== Top Trending Repositories ===")
    for i, result in enumerate(top_results, 1):
        print(f"{i}. {result['full_name']} (score: {result['score']})")
        print(f"   Stars: {result['total_stars']} (+{result['new_stars_24h']})")
        print(f"   Forks: {result['total_forks']} (+{result['new_forks_24h']})")


if __name__ == "__main__":
    main()
