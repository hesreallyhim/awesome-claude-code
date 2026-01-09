"""Shared utility helpers for README generation."""

from __future__ import annotations

import re
from datetime import datetime


def extract_github_owner_repo(url: str) -> tuple[str, str] | None:
    """Extract owner and repo from any GitHub URL."""
    patterns = [
        r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",  # repo root
        r"github\.com/([^/]+)/([^/]+)/(?:blob|tree|issues|pull|releases)",  # with path
        r"github\.com/([^/]+)/([^/]+)/?",  # general fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner, repo = match.groups()[:2]
            repo = repo.split("/")[0].split("?")[0].split("#")[0]
            if owner and repo:
                return (owner, repo)
    return None


def format_stars(num: int) -> str:
    """Format star count with K/M suffix."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(num)


def format_delta(delta: int) -> str:
    """Format delta with +/- prefix."""
    if delta > 0:
        return f"+{delta}"
    if delta < 0:
        return str(delta)
    return ""


def get_anchor_suffix_for_icon(icon: str | None) -> str:
    """Generate the anchor suffix for a section with a trailing emoji icon.

    GitHub strips simple emoji codepoints and turns them into a dash. If the emoji
    includes a variation selector (U+FE00 to U+FE0F), the variation selector is
    URL-encoded and appended after the dash.
    """
    if not icon:
        return ""

    vs_char = next((char for char in icon if 0xFE00 <= ord(char) <= 0xFE0F), None)
    if vs_char:
        vs_bytes = vs_char.encode("utf-8")
        url_encoded = "".join(f"%{byte:02X}" for byte in vs_bytes)
        return f"-{url_encoded}"

    return "-"


def generate_toc_anchor(
    title: str,
    icon: str | None = None,
    has_back_to_top_in_heading: bool = False,
) -> str:
    """Generate a TOC anchor for a heading.

    Centralizes anchor generation logic across all README styles.

    Args:
        title: The heading text (e.g., "Agent Skills")
        icon: Optional trailing emoji icon (e.g., "🤖"). Each emoji adds a dash.
        has_back_to_top_in_heading: True if heading contains 🔝 back-to-top link,
            which adds an additional trailing dash to the anchor.

    Returns:
        The anchor string without the leading '#' (e.g., "agent-skills-")
    """
    base = title.lower().replace(" ", "-").replace("&", "").replace("/", "").replace(".", "")
    suffix = get_anchor_suffix_for_icon(icon)
    back_to_top_suffix = "-" if has_back_to_top_in_heading else ""
    return f"{base}{suffix}{back_to_top_suffix}"


def generate_subcategory_anchor(
    title: str,
    general_counter: int = 0,
    has_back_to_top_in_heading: bool = False,
) -> tuple[str, int]:
    """Generate a TOC anchor for a subcategory heading.

    Handles the special case of multiple "General" subcategories which need
    unique anchors (general, general-1, general-2, etc.).

    Args:
        title: The subcategory name (e.g., "General", "IDE Integrations")
        general_counter: Current count of "General" subcategories seen so far
        has_back_to_top_in_heading: True if heading contains 🔝 back-to-top link

    Returns:
        Tuple of (anchor_string, updated_general_counter)
    """
    base = title.lower().replace(" ", "-").replace("&", "").replace("/", "")
    back_to_top_suffix = "-" if has_back_to_top_in_heading else ""

    if title == "General":
        if general_counter == 0:
            anchor = f"general{back_to_top_suffix}"
        else:
            # GitHub uses double-dash before counter when back-to-top present
            separator = "-" if has_back_to_top_in_heading else ""
            anchor = f"general-{separator}{general_counter}"
        return anchor, general_counter + 1

    return f"{base}{back_to_top_suffix}", general_counter


def sanitize_filename_from_anchor(anchor: str) -> str:
    """Convert an anchor string to a tidy filename fragment."""
    name = anchor.rstrip("-")
    name = name.replace("-", "_")
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def build_general_anchor_map(categories: list[dict], csv_data: list[dict] | None = None) -> dict:
    """Build a map of (category, 'General') -> anchor string shared by TOC and body."""
    general_map: dict[tuple[str, str], str] = {}

    for category in categories:
        category_name = category.get("name", "")
        category_id = category.get("id", "")
        subcategories = category.get("subcategories", [])

        for subcat in subcategories:
            sub_title = subcat["name"]
            if sub_title != "General":
                continue

            include_subcategory = True
            if csv_data is not None:
                resources = [
                    r
                    for r in csv_data
                    if r["Category"] == category_name
                    and r.get("Sub-Category", "").strip() == sub_title
                ]
                include_subcategory = bool(resources)

            if not include_subcategory:
                continue

            anchor = f"{category_id}-general"
            general_map[(category_id, sub_title)] = anchor

    return general_map


def parse_resource_date(date_string: str | None) -> datetime | None:
    """Parse a date string that may include timestamp information."""
    if not date_string:
        return None

    date_string = date_string.strip()

    date_formats = [
        "%Y-%m-%d:%H-%M-%S",
        "%Y-%m-%d",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None


def format_category_dir_name(name: str, category_id: str | None = None) -> str:
    """Convert category name to display text for TOC rows."""
    overrides = {
        "workflows": "WORKFLOWS_&_GUIDES/",
    }
    if category_id and category_id in overrides:
        return overrides[category_id]

    slug = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()
    return slug + "/"
