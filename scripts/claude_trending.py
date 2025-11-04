#!/usr/bin/env python3
"""
Daily trending repositories script for Claude Code projects.

Configuration (via environment variables):
- GITHUB_TOKEN (required): GitHub Personal Access Token for API access
- WINDOW_HOURS (optional, default: 24): Time window in hours for counting new stars/forks
- TOP_N (optional, default: 5): Number of top trending repositories to include
- SEARCH_EXCLUDE_MONET (optional, default: "true"): Exclude art-related noise
- MIN_PUSHED_SINCE (optional, default: 365): Minimum days since last push
- SEARCH_QUERIES (optional): JSON array of custom search queries to override defaults

The script:
1. Searches GitHub for Claude Code related repositories using multiple targeted queries
2. Deduplicates and filters results
3. Counts new stars (WatchEvent) and forks within the time window
4. Computes Laplace-smoothed proportional growth metrics
5. Calculates composite score and ranks repositories
6. Writes the top N results to trending.csv in the repository root

Output CSV format:
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


def get_env_config() -> dict[str, Any]:
    """Parse configuration from environment variables."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    return {
        "token": token,
        "window_hours": int(os.environ.get("WINDOW_HOURS", "24")),
        "top_n": int(os.environ.get("TOP_N", "5")),
        "exclude_monet": os.environ.get("SEARCH_EXCLUDE_MONET", "true").lower() == "true",
        "min_pushed_since_days": int(os.environ.get("MIN_PUSHED_SINCE", "365")),
        "custom_queries": json.loads(os.environ.get("SEARCH_QUERIES", "[]")),
    }


def get_default_search_queries() -> list[str]:
    """Return default search queries for Claude Code repositories."""
    return [
        '"Claude Code" in:name,description,readme fork:false archived:false',
        "topic:claude-code fork:false archived:false",
        "topic:claude fork:false archived:false pushed:>2024-01-01",
        '"claude" "vscode" in:readme fork:false archived:false',
        '"claude" "code" in:readme fork:false archived:false',
    ]


def search_repositories(query: str, token: str) -> list[dict[str, Any]]:
    """Search GitHub repositories using the given query."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    results = []
    page = 1
    per_page = 100

    while True:
        url = (
            f"https://api.github.com/search/repositories?q={query}&per_page={per_page}&page={page}"
        )
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 403 and "rate limit" in response.text.lower():
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            if reset_time:
                wait_time = max(reset_time - time.time(), 0) + 5
                print(f"Rate limit hit, waiting {wait_time:.0f} seconds...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            else:
                print("Rate limit exceeded, cannot continue", file=sys.stderr)
                break

        if response.status_code != 200:
            print(
                f"Search query failed with status {response.status_code}: {query}",
                file=sys.stderr,
            )
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        results.extend(items)

        # GitHub search API has a maximum of 1000 results
        if len(results) >= data.get("total_count", 0) or len(results) >= 1000:
            break

        page += 1
        time.sleep(1)  # Be polite to the API

    return results


def deduplicate_and_filter(
    repos: list[dict[str, Any]], exclude_monet: bool, min_pushed_since_days: int
) -> list[dict[str, Any]]:
    """Deduplicate by full_name and apply filters."""
    seen = set()
    filtered = []
    cutoff_date = datetime.now(UTC) - timedelta(days=min_pushed_since_days)

    for repo in repos:
        full_name = repo.get("full_name", "")
        if not full_name or full_name in seen:
            continue

        seen.add(full_name)

        # Exclude Monet-related noise
        if exclude_monet:
            name = repo.get("name", "").lower()
            description = repo.get("description", "") or ""
            description_lower = description.lower()
            if "monet" in name or "monet" in description_lower:
                continue

        # Check last push date
        pushed_at = repo.get("pushed_at")
        if pushed_at:
            try:
                pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                if pushed_date < cutoff_date:
                    continue
            except (ValueError, AttributeError):
                continue

        filtered.append(repo)

    return filtered


def count_new_stars(repo_full_name: str, token: str, window_hours: int) -> int:
    """Count new stars (WatchEvent) within the time window using repo events API."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    cutoff_time = datetime.now(UTC) - timedelta(hours=window_hours)
    url = f"https://api.github.com/repos/{repo_full_name}/events"
    page = 1
    new_stars = 0

    while page <= 10:  # Limit to 10 pages to avoid excessive API calls
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 403 and "rate limit" in response.text.lower():
            time.sleep(60)  # Wait and retry
            continue

        if response.status_code != 200:
            break

        events = response.json()
        if not events:
            break

        for event in events:
            if event.get("type") == "WatchEvent":
                created_at = event.get("created_at")
                if created_at:
                    try:
                        event_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if event_time >= cutoff_time:
                            new_stars += 1
                        else:
                            # Events are sorted by newest first, so we can stop
                            return new_stars
                    except (ValueError, AttributeError):
                        continue

        page += 1
        time.sleep(0.5)  # Be polite

    return new_stars


def count_new_forks(repo_full_name: str, token: str, window_hours: int) -> int:
    """Count new forks within the time window using forks API."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    cutoff_time = datetime.now(UTC) - timedelta(hours=window_hours)
    url = f"https://api.github.com/repos/{repo_full_name}/forks"
    page = 1
    new_forks = 0

    while page <= 10:  # Limit to 10 pages
        params = {"sort": "newest", "per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 403 and "rate limit" in response.text.lower():
            time.sleep(60)
            continue

        if response.status_code != 200:
            break

        forks = response.json()
        if not forks:
            break

        for fork in forks:
            created_at = fork.get("created_at")
            if created_at:
                try:
                    fork_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if fork_time >= cutoff_time:
                        new_forks += 1
                    else:
                        # Forks are sorted newest first, stop when older than window
                        return new_forks
                except (ValueError, AttributeError):
                    continue

        page += 1
        time.sleep(0.5)

    return new_forks


def compute_metrics(repo: dict[str, Any], new_stars: int, new_forks: int) -> dict[str, Any]:
    """Compute Laplace-smoothed proportional growth metrics and composite score."""
    total_stars = repo.get("stargazers_count", 0)
    total_forks = repo.get("forks_count", 0)

    # Adjusted proportional growth with Laplace smoothing
    star_growth_adj = new_stars / (max(0, total_stars - new_stars) + 10)
    fork_growth_adj = new_forks / (max(0, total_forks - new_forks) + 5)

    # Composite score
    score = star_growth_adj + 0.5 * fork_growth_adj

    return {
        "full_name": repo.get("full_name", ""),
        "html_url": repo.get("html_url", ""),
        "description": (repo.get("description") or "").replace("\n", " ").replace('"', '""'),
        "language": repo.get("language") or "",
        "total_stars": total_stars,
        "total_forks": total_forks,
        "new_stars_24h": new_stars,
        "new_forks_24h": new_forks,
        "star_growth_adj": round(star_growth_adj, 4),
        "fork_growth_adj": round(fork_growth_adj, 4),
        "score": round(score, 4),
    }


def process_repository(
    repo: dict[str, Any], token: str, window_hours: int
) -> dict[str, Any] | None:
    """Process a single repository: count new stars/forks and compute metrics."""
    try:
        full_name = repo.get("full_name", "")
        print(f"Processing {full_name}...", file=sys.stderr)

        new_stars = count_new_stars(full_name, token, window_hours)
        new_forks = count_new_forks(full_name, token, window_hours)

        return compute_metrics(repo, new_stars, new_forks)
    except Exception as e:
        print(f"Error processing {repo.get('full_name', 'unknown')}: {e}", file=sys.stderr)
        return None


def main() -> None:
    """Main execution function."""
    config = get_env_config()

    # Get search queries
    queries = config["custom_queries"] if config["custom_queries"] else get_default_search_queries()

    print(f"Searching with {len(queries)} queries...", file=sys.stderr)

    # Search and collect repositories
    all_repos = []
    for query in queries:
        print(f"Executing query: {query}", file=sys.stderr)
        repos = search_repositories(query, config["token"])
        all_repos.extend(repos)
        print(f"Found {len(repos)} repositories", file=sys.stderr)
        time.sleep(2)  # Be polite between queries

    print(f"Total repositories before filtering: {len(all_repos)}", file=sys.stderr)

    # Deduplicate and filter
    filtered_repos = deduplicate_and_filter(
        all_repos, config["exclude_monet"], config["min_pushed_since_days"]
    )
    print(f"Repositories after deduplication and filtering: {len(filtered_repos)}", file=sys.stderr)

    # Process repositories in parallel
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(process_repository, repo, config["token"], config["window_hours"]): repo
            for repo in filtered_repos
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # Sort by score (desc), then new_stars_24h (desc), then total_stars (desc)
    results.sort(key=lambda x: (x["score"], x["new_stars_24h"], x["total_stars"]), reverse=True)

    # Take top N
    top_results = results[: config["top_n"]]

    print(f"\nTop {len(top_results)} trending repositories:", file=sys.stderr)
    for i, result in enumerate(top_results, 1):
        print(
            f"{i}. {result['full_name']} (score: {result['score']}, "
            f"new stars: {result['new_stars_24h']}, total stars: {result['total_stars']})",
            file=sys.stderr,
        )

    # Write to CSV
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trending.csv")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
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
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in top_results:
            row = {"generated_at_utc": generated_at}
            row.update(result)
            writer.writerow(row)

    print(f"\n✅ Successfully wrote {len(top_results)} results to {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
