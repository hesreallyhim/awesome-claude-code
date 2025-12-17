#!/usr/bin/env python3
"""
Generate dynamic stock ticker SVGs from repository data.

This script reads the repo ticker CSV and generates animated SVG files
with a random sampling of repositories for both dark and light themes.
Displays deltas for each metric with color coding.
"""

import csv
import random
from pathlib import Path
from typing import Any


def format_number(num: int) -> str:
    """
    Format a number with K/M suffix for display.

    Args:
        num: The number to format

    Returns:
        Formatted string (e.g., "1.2K", "15.3K")
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    else:
        return str(num)


def format_delta(delta: int) -> str:
    """
    Format a delta with +/- prefix.

    Args:
        delta: The delta value

    Returns:
        Formatted string (e.g., "+5", "-2", "0")
    """
    if delta > 0:
        return f"+{format_number(delta)}"
    elif delta < 0:
        return format_number(delta)
    else:
        return "0"


def truncate_repo_name(name: str, max_length: int = 20) -> str:
    """
    Truncate a repository name if it exceeds max_length.

    Args:
        name: The repository name to truncate
        max_length: Maximum length before truncation (default: 20)

    Returns:
        Truncated string with ellipsis if needed (e.g., "very-long-repositor...")
    """
    if len(name) <= max_length:
        return name
    return name[:max_length] + "..."


def get_delta_color(delta: int, colors: dict[str, str]) -> str:
    """
    Get color for delta based on value.

    Args:
        delta: The delta value
        colors: Color scheme dictionary

    Returns:
        Color string
    """
    if delta > 0:
        return colors["delta_positive"]
    elif delta < 0:
        return colors["delta_negative"]
    else:
        return colors["delta_neutral"]


def load_repos(csv_path: Path) -> list[dict[str, Any]]:
    """
    Load repository data from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of repository dictionaries
    """
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


def generate_repo_group(
    repo: dict[str, Any], x_offset: int, colors: dict[str, str], flip: bool
) -> str:
    """
    Generate SVG group element for a single repository.

    Args:
        repo: Repository data
        x_offset: X position offset for this group
        colors: Color scheme dictionary

    Returns:
        SVG group element as string
    """
    # Format deltas (commented out - unused but may be needed later)
    # stars_delta = format_delta(repo["stars_delta"])
    # watchers_delta = format_delta(repo["watchers_delta"])
    # forks_delta = format_delta(repo["forks_delta"])

    # Get delta colors (commented out - unused but may be needed later)
    # stars_delta_color = get_delta_color(repo["stars_delta"], colors)
    # watchers_delta_color = get_delta_color(repo["watchers_delta"], colors)
    # forks_delta_color = get_delta_color(repo["forks_delta"], colors)

    # Split full_name into owner and repo
    parts = repo["full_name"].split("/", 1)
    owner = parts[0] if len(parts) > 0 else ""
    repo_name = parts[1] if len(parts) > 1 else ""

    # Truncate repo name to avoid overlap with long names (slightly longer cutoff for mobile)
    truncated_repo_name = truncate_repo_name(repo_name, max_length=24)

    # Stars snippet placed after owner
    delta_text = format_delta(repo["stars_delta"])
    show_delta = delta_text != "0"
    approx_char_width = 12  # rough monospace estimate for 24px owner font
    owner_start_x = 140
    owner_font_size = 24

    def star_snippet(y_pos: int) -> str:
        star_str = f"{format_number(repo['stars'])} ⭐"
        delta_str = f" {delta_text}" if show_delta else ""
        metrics = f" | {star_str}{delta_str}"
        star_x = owner_start_x + (len(owner) * approx_char_width) + 22
        return f"""
        <text x="{star_x}" y="{y_pos}" font-family="'Courier New', monospace" font-size="16" font-weight="bold"
              fill="{colors["stars"]}">{metrics}</text>"""

    if not flip:
        # Names on top, owner just below
        return f"""      <!-- Repo: {repo["full_name"]} -->
      <g transform="translate({x_offset}, 0)">
        <!-- Repo name -->
        <text x="140" y="32" font-family="'Courier New', monospace" font-size="34" font-weight="bold"
              fill="{colors["text"]}">{truncated_repo_name}</text>
        <!-- Owner name -->
        <text x="{owner_start_x}" y="64" font-family="'Courier New', monospace" font-size="{owner_font_size}" font-weight="normal"
              fill="{colors["text"]}" opacity="1.0">{owner}</text>{star_snippet(64)}
      </g>"""
    else:
        # Owner on top, name just below (in lower half)
        return f"""      <!-- Repo: {repo["full_name"]} -->
      <g transform="translate({x_offset}, 0)">
        <!-- Owner name -->
        <text x="{owner_start_x}" y="102" font-family="'Courier New', monospace" font-size="{owner_font_size}" font-weight="normal"
              fill="{colors["text"]}" opacity="1.0">{owner}</text>{star_snippet(102)}
        <!-- Repo name -->
        <text x="140" y="132" font-family="'Courier New', monospace" font-size="34" font-weight="bold"
              fill="{colors["text"]}">{truncated_repo_name}</text>
      </g>"""


def generate_ticker_svg(repos: list[dict[str, Any]], theme: str = "dark") -> str:
    """
    Generate complete ticker SVG.

    Args:
        repos: List of repository data
        theme: "dark" or "light"

    Returns:
        Complete SVG as string
    """
    # Filter out repos owned by hesreallyhim
    filtered_repos = [r for r in repos if not r["full_name"].startswith("hesreallyhim/")]

    # Sample 10 random repos and duplicate for seamless scrolling
    sampled = random.sample(filtered_repos, min(10, len(filtered_repos)))

    # Color schemes
    if theme == "dark":
        colors = {
            "bg_start": "#001a00",
            "bg_mid": "#002200",
            "bg_opacity_start": "0.95",
            "bg_opacity_mid": "0.98",
            "border_1": "#33ff33",
            "border_2": "#00ffff",
            "border_3": "#66ff66",
            "border_4": "#00ff99",
            "label_bg": "#001100",
            "label_title": "#33ff33",
            "label_subtitle": "#00ffff",
            "pulse": "#33ff33",
            "text": "#ffffff",
            "stars": "#00ffff",
            "watchers": "#66ff66",
            "forks": "#00ff99",
            "fade_color": "#001a00",
            "delta_positive": "#33ff33",
            "delta_negative": "#ff3333",
            "delta_neutral": "#888888",
            "glow_blur": "0.1",
        }
    else:  # light
        colors = {
            "bg_start": "#fff8f0",
            "bg_mid": "#fff5eb",
            "bg_opacity_start": "0.98",
            "bg_opacity_mid": "1",
            "border_1": "#FF6B35",
            "border_2": "#9C4EFF",
            "border_3": "#FFD700",
            "border_4": "#FF6B35",
            "label_bg": "#fff0e6",
            "label_title": "#FF6B35",
            "label_subtitle": "#9C4EFF",
            "pulse": "#FF6B35",
            "text": "#2d2d2d",
            "stars": "#9C4EFF",
            "watchers": "#FF6B35",
            "forks": "#FFD700",
            "fade_color": "#fff8f0",
            "delta_positive": "#00aa00",
            "delta_negative": "#cc0000",
            "delta_neutral": "#888888",
            "glow_blur": "0.15",
        }

    # Generate repo groups: all 10 + first 4 repeated for seamless loop
    repo_groups = []
    x_pos = 0

    # All sampled repos
    for idx, repo in enumerate(sampled):
        group_svg = generate_repo_group(repo, x_pos, colors, flip=bool(idx % 2))
        repo_groups.append(group_svg)
        x_pos += 300  # Space between repos (compact stock ticker style)

    # Primary content width (what we scroll through before looping)
    primary_width = x_pos

    # Append first 4 repos to fill the visible gap during loop reset
    for idx, repo in enumerate(sampled[:4]):
        group_svg = generate_repo_group(repo, x_pos, colors, flip=bool(idx % 2))
        repo_groups.append(group_svg)
        x_pos += 300

    repos_svg = "\n".join(repo_groups)

    # Calculate animation duration based on primary content (10 repos)
    duration = max(28, primary_width // 55)  # slightly slower to aid legibility on mobile

    return f"""<svg width="900" height="150" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradient for ticker background -->
    <linearGradient id="tickerBg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors["bg_start"]};stop-opacity:{colors["bg_opacity_start"]}"/>
      <stop offset="50%" style="stop-color:{colors["bg_mid"]};stop-opacity:{colors["bg_opacity_mid"]}"/>
      <stop offset="100%" style="stop-color:{colors["bg_start"]};stop-opacity:{colors["bg_opacity_start"]}"/>
    </linearGradient>

    <!-- Gradient for border lines -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors["border_1"]};stop-opacity:0.85">
        <animate attributeName="stop-opacity" values="0.85;1;0.85" dur="2s" repeatCount="indefinite"/>
      </stop>
      <stop offset="33%" style="stop-color:{colors["border_2"]};stop-opacity:0.9">
        <animate attributeName="stop-opacity" values="0.9;1;0.9" dur="2.2s" repeatCount="indefinite"/>
      </stop>
      <stop offset="66%" style="stop-color:{colors["border_3"]};stop-opacity:0.85">
        <animate attributeName="stop-opacity" values="0.85;1;0.85" dur="1.8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" style="stop-color:{colors["border_4"]};stop-opacity:0.85">
        <animate attributeName="stop-opacity" values="0.85;1;0.85" dur="2s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>

    <!-- Text glow effect -->
    <filter id="textGlow">
      <feGaussianBlur stdDeviation="{colors["glow_blur"]}" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Strong glow for metrics -->
    <filter id="metricGlow">
      <feGaussianBlur stdDeviation="0.2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

  <!-- Edge fade effects -->
  <linearGradient id="leftFade" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" style="stop-color:{colors["fade_color"]};stop-opacity:1"/>
    <stop offset="100%" style="stop-color:{colors["fade_color"]};stop-opacity:0"/>
  </linearGradient>
  <linearGradient id="rightFade" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" style="stop-color:{colors["fade_color"]};stop-opacity:0"/>
    <stop offset="100%" style="stop-color:{colors["fade_color"]};stop-opacity:1"/>
  </linearGradient>
  </defs>

  <!-- Background panel -->
  <rect width="900" height="150" fill="url(#tickerBg)" rx="8"/>

  <!-- Top border -->
  <rect x="0" y="2" width="900" height="2" fill="url(#borderGrad)" rx="1"/>

  <!-- Bottom border -->
  <rect x="0" y="146" width="900" height="2" fill="url(#borderGrad)" rx="1"/>

  <!-- Midline for grouping reference -->
  <line x1="0" y1="75" x2="900" y2="75" stroke="{colors["border_2"]}" stroke-width="2" stroke-dasharray="8 6" opacity="0.6"/>

  <!-- Ticker label on left -->
  <rect x="0" y="0" width="120" height="150" fill="{colors["label_bg"]}" opacity="0.95" rx="8"/>
  <text x="60" y="46" font-family="'Courier New', monospace" font-size="18" font-weight="bold"
        fill="{colors["label_title"]}" text-anchor="middle" filter="url(#textGlow)">
    CLAUDE CODE
  </text>
  <text x="60" y="68" font-family="'Courier New', monospace" font-size="18" font-weight="bold"
        fill="{colors["label_subtitle"]}" text-anchor="middle" filter="url(#textGlow)">
    REPOS LIVE
  </text>
  <text x="60" y="92" font-family="'Courier New', monospace" font-size="14" font-weight="bold"
        fill="{colors["delta_positive"]}" text-anchor="middle">
    DAILY Δ
  </text>

  <!-- Animated pulse indicator -->
  <circle cx="60" cy="118" r="5" fill="{colors["pulse"]}" filter="url(#metricGlow)">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;1;0.6" dur="1.5s" repeatCount="indefinite"/>
  </circle>

  <!-- Divider line after label -->
  <rect x="122" y="18" width="2" height="114" fill="url(#borderGrad)" rx="1"/>

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
  <rect x="130" y="0" width="50" height="100" fill="url(#leftFade)"/>
  <rect x="850" y="0" width="50" height="100" fill="url(#rightFade)"/>
</svg>"""


def main() -> None:
    """Main function to generate ticker SVGs."""
    repo_root = Path(__file__).parent.parent
    csv_path = repo_root / "data" / "repo-ticker.csv"
    output_dir = repo_root / "assets"

    # Check if CSV exists
    if not csv_path.exists():
        print(f"⚠ CSV file not found at {csv_path}")
        print("⚠ Using static ticker SVGs (already created)")
        return

    # Load repos
    print(f"Loading repository data from {csv_path}...")
    repos = load_repos(csv_path)
    print(f"✓ Loaded {len(repos)} repositories")

    if len(repos) == 0:
        print("⚠ No repositories found in CSV")
        print("⚠ Using static ticker SVGs (already created)")
        return

    # Generate SVGs
    print("Generating ticker SVGs...")

    # Dark theme
    dark_svg = generate_ticker_svg(repos, "dark")
    dark_path = output_dir / "repo-ticker.svg"
    with dark_path.open("w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"✓ Generated dark theme: {dark_path}")

    # Light theme
    light_svg = generate_ticker_svg(repos, "light")
    light_path = output_dir / "repo-ticker-light.svg"
    with light_path.open("w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"✓ Generated light theme: {light_path}")

    print("✓ Ticker SVGs generated successfully!")


if __name__ == "__main__":
    main()
