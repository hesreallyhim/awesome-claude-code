#!/usr/bin/env python3
"""Generate the animated Claude Code repo-ticker SVG.

Reads the sampled repo data (`data/repo-ticker.csv`) and renders a single
horizontally-scrolling ticker of Claude-Code-related GitHub projects into
`assets/repo-ticker.svg`.
"""

import csv
import os
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

try:
    from ticker.ticker_filters import filter_repos
except ImportError:  # when run directly: `python ticker/generate_ticker_svg.py`
    from ticker_filters import filter_repos

# This repo is flat (no `scripts` package / pyproject): anchor on the script's
# own location per project convention. ticker/ -> repo root is parents[1].
REPO_ROOT = Path(__file__).resolve().parents[1]

_STAR_DELTA_CACHE: dict[str, int] = {}


def fetch_recent_star_delta(
    full_name: str, token: str, since: datetime, cache: dict[str, int]
) -> int | None:
    """Fetch the number of stars added since the cutoff time."""
    if full_name in cache:
        return cache[full_name]

    owner, repo = full_name.split("/", 1)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    query = """
    query($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        stargazers(first: 100, after: $cursor, orderBy: {field: STARRED_AT, direction: DESC}) {
          edges { starredAt }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
    """

    delta = 0
    cursor: str | None = None
    cutoff = since.astimezone(UTC)

    while True:
        payload = {"query": query, "variables": {"owner": owner, "name": repo, "cursor": cursor}}
        response = requests.post(
            "https://api.github.com/graphql", json=payload, headers=headers, timeout=20
        )
        if response.status_code != 200:
            return None
        data = response.json()
        if "errors" in data:
            return None

        stargazers = data.get("data", {}).get("repository", {}).get("stargazers", {})
        edges = stargazers.get("edges", [])
        page_info = stargazers.get("pageInfo", {})

        for edge in edges:
            starred_at = edge.get("starredAt")
            if not starred_at:
                continue
            starred_dt = datetime.fromisoformat(starred_at.replace("Z", "+00:00"))
            if starred_dt < cutoff:
                cache[full_name] = delta
                return delta
            delta += 1

        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")

    cache[full_name] = delta
    return delta


def apply_recent_star_deltas(repos: list[dict[str, Any]]) -> None:
    """Replace stars_delta with counts from the last 24 hours when possible."""
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        return

    cutoff = datetime.now(UTC) - timedelta(days=1)
    for repo in repos:
        delta = fetch_recent_star_delta(repo["full_name"], token, cutoff, _STAR_DELTA_CACHE)
        if delta is not None:
            repo["stars_delta"] = delta


def format_number(num: int) -> str:
    """Format a number with a K/M suffix (e.g. "1.2K", "15.3K")."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    else:
        return str(num)


def format_delta(delta: int) -> str:
    """Format a delta with a +/- prefix (e.g. "+5", "-2", "0")."""
    if delta > 0:
        return f"+{format_number(delta)}"
    elif delta < 0:
        return format_number(delta)
    else:
        return "0"


def truncate_repo_name(name: str, max_length: int = 20) -> str:
    """Truncate a repository name with an ellipsis if it exceeds max_length."""
    if len(name) <= max_length:
        return name
    return name[:max_length] + "..."


def load_repos(csv_path: Path) -> list[dict[str, Any]]:
    """Load repository data from the ticker CSV."""
    repos = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            repos.append(
                {
                    "full_name": row["full_name"],
                    "stars": int(row["stars"]),
                    "watchers": int(row["watchers"]),
                    "forks": int(row["forks"]),
                    "stars_delta": int(row.get("stars_delta", 0)),
                    "watchers_delta": int(row.get("watchers_delta", 0)),
                    "forks_delta": int(row.get("forks_delta", 0)),
                }
            )
    return repos


def generate_repo_group(repo: dict[str, Any], x_offset: int, flip: bool) -> str:
    """Generate the SVG group for a single repository (clean, minimal styling)."""
    parts = repo["full_name"].split("/", 1)
    owner = parts[0] if len(parts) > 0 else ""
    repo_name = parts[1] if len(parts) > 1 else ""

    truncated_repo_name = truncate_repo_name(repo_name, max_length=24)

    delta_text = format_delta(repo["stars_delta"])
    # show_delta = delta_text != "0"
    show_delta = False
    approx_char_width = 12
    owner_start_x = 140
    owner_font_size = 24

    text_color = "#24292e"  # GitHub dark
    owner_color = "#586069"  # GitHub secondary
    stars_color = "#6a737d"  # muted gray
    delta_positive = "#22863a"
    delta_negative = "#cb2431"

    if repo["stars_delta"] > 0:
        delta_color = delta_positive
    elif repo["stars_delta"] < 0:
        delta_color = delta_negative
    else:
        delta_color = stars_color

    font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

    def star_snippet(y_pos: int) -> str:
        star_str = f"{format_number(repo['stars'])} ★"
        delta_str = f" {delta_text}" if show_delta else ""
        star_x = owner_start_x + (len(owner) * approx_char_width) + 22
        result = f"""
        <text x="{star_x}" y="{y_pos}" font-family="{font_family}" font-size="16" font-weight="500"
              fill="{stars_color}">| {star_str}</text>"""
        if show_delta:
            delta_x = star_x + (len(f"| {star_str}") * 9) + 5
            result += f"""
        <text x="{delta_x}" y="{y_pos}" font-family="{font_family}" font-size="16" font-weight="500"
              fill="{delta_color}">{delta_str}</text>"""
        return result

    if not flip:
        # Repo name on top, owner just below.
        return f"""      <!-- Repo: {repo["full_name"]} -->
      <g transform="translate({x_offset}, 0)">
        <!-- Repo name -->
        <text x="140" y="32" font-family="{font_family}" font-size="34" font-weight="600"
              fill="{text_color}">{truncated_repo_name}</text>
        <!-- Owner name -->
        <text x="{owner_start_x}" y="64" font-family="{font_family}" font-size="{owner_font_size}" font-weight="400"
              fill="{owner_color}">{owner}</text>{star_snippet(64)}
      </g>"""
    else:
        # Owner on top, repo name just below (lower half).
        return f"""      <!-- Repo: {repo["full_name"]} -->
      <g transform="translate({x_offset}, 0)">
        <!-- Owner name -->
        <text x="{owner_start_x}" y="102" font-family="{font_family}" font-size="{owner_font_size}" font-weight="400"
              fill="{owner_color}">{owner}</text>{star_snippet(102)}
        <!-- Repo name -->
        <text x="140" y="132" font-family="{font_family}" font-size="34" font-weight="600"
              fill="{text_color}">{truncated_repo_name}</text>
      </g>"""


def generate_ticker_svg(repos: list[dict[str, Any]]) -> str:
    """Generate the complete horizontally-scrolling ticker SVG."""
    # Apply the declarative exclusion filters (ticker/ticker_filters.py), then sample.
    filtered_repos = filter_repos(repos)
    sampled = random.sample(filtered_repos, min(10, len(filtered_repos)))
    # apply_recent_star_deltas(sampled)

    repo_groups = []
    x_pos = 0
    for idx, repo in enumerate(sampled):
        repo_groups.append(generate_repo_group(repo, x_pos, flip=bool(idx % 2)))
        x_pos += 300  # spacing between repos
    primary_width = x_pos  # what we scroll through before looping

    # Repeat the first 4 to fill the visible gap during the loop reset.
    for idx, repo in enumerate(sampled[:4]):
        repo_groups.append(generate_repo_group(repo, x_pos, flip=bool(idx % 2)))
        x_pos += 300

    repos_svg = "\n".join(repo_groups)
    duration = max(28, primary_width // 55)  # slightly slower for mobile legibility

    bg_color = "#ffffff"
    border_color = "#e1e4e8"
    label_bg = "#f6f8fa"
    label_title = "#24292e"
    label_subtitle = "#586069"
    fade_color = "#ffffff"

    return f"""<svg width="900" height="150" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Edge fade effects -->
    <linearGradient id="leftFade" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{fade_color};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:{fade_color};stop-opacity:0"/>
    </linearGradient>
    <linearGradient id="rightFade" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{fade_color};stop-opacity:0"/>
      <stop offset="100%" style="stop-color:{fade_color};stop-opacity:1"/>
    </linearGradient>
  </defs>

  <!-- Clean background -->
  <rect width="900" height="150" fill="{bg_color}" rx="8"/>

  <!-- Top border -->
  <rect x="0" y="2" width="900" height="1" fill="{border_color}"/>

  <!-- Bottom border -->
  <rect x="0" y="147" width="900" height="1" fill="{border_color}"/>

  <!-- Midline for grouping reference -->
  <line x1="0" y1="75" x2="900" y2="75" stroke="{border_color}" stroke-width="1" stroke-dasharray="8 6" opacity="0.6"/>

  <!-- Ticker label on left -->
  <rect x="0" y="0" width="120" height="150" fill="{label_bg}" rx="8"/>
  <text x="60" y="50" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" font-weight="600"
        fill="{label_title}" text-anchor="middle">CLAUDE CODE</text>
  <text x="60" y="72" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" font-weight="600"
        fill="{label_subtitle}" text-anchor="middle">PROJECTS</text>
  <text x="60" y="100" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="12" font-weight="500"
        fill="{label_subtitle}" text-anchor="middle">Daily Δ</text>

  <!-- Simple indicator dot -->
  <circle cx="60" cy="122" r="4" fill="#22863a" opacity="0.8"/>

  <!-- Divider line after label -->
  <rect x="122" y="18" width="1" height="114" fill="{border_color}"/>

  <!-- Scrolling ticker content area -->
  <clipPath id="tickerClip">
    <rect x="130" y="0" width="770" height="150"/>
  </clipPath>

  <g clip-path="url(#tickerClip)">
    <!-- Single ticker strip with seamless loop (10 repos + first 4 repeated) -->
    <g id="tickerItems">
      <animateTransform
        attributeName="transform"
        attributeType="XML"
        type="translate"
        from="0 0"
        to="-{primary_width} 0"
        dur="{duration}s"
        repeatCount="indefinite"/>

{repos_svg}
    </g>
  </g>

  <!-- Edge fade effects -->
  <rect x="130" y="0" width="50" height="150" fill="url(#leftFade)"/>
  <rect x="850" y="0" width="50" height="150" fill="url(#rightFade)"/>
</svg>"""


def main() -> None:
    """Regenerate the ticker SVG from the sampled repo data."""
    csv_path = REPO_ROOT / "data" / "repo-ticker.csv"
    output_path = REPO_ROOT / "assets" / "repo-ticker.svg"

    if not csv_path.exists():
        print(f"⚠ CSV not found at {csv_path}; keeping the existing ticker SVG")
        return

    print(f"Loading repository data from {csv_path}...")
    repos = load_repos(csv_path)
    print(f"✓ Loaded {len(repos)} repositories")
    if not repos:
        print("⚠ No repositories in CSV; keeping the existing ticker SVG")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_ticker_svg(repos), encoding="utf-8")
    print(f"✓ Generated ticker: {output_path}")


if __name__ == "__main__":
    main()
