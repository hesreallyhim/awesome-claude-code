"""Minimal README markdown rendering helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from scripts.readme.helpers.readme_utils import (
    generate_subcategory_anchor,
    generate_toc_anchor,
    parse_resource_date,
)
from scripts.utils.github_utils import parse_github_url


def format_resource_entry(row: dict, include_separator: bool = True) -> str:
    """Format resource as plain markdown with collapsible GitHub stats."""
    _ = include_separator
    display_name = row["Display Name"]
    primary_link = row["Primary Link"]
    author_name = row.get("Author Name", "").strip()
    author_link = row.get("Author Link", "").strip()
    description = row.get("Description", "").strip()
    license_info = row.get("License", "").strip()
    removed_from_origin = row.get("Removed From Origin", "").strip().upper() == "TRUE"

    entry_parts = [f"[`{display_name}`]({primary_link})"]

    if author_name:
        if author_link:
            entry_parts.append(f" &nbsp; by &nbsp; [{author_name}]({author_link})")
        else:
            entry_parts.append(f" &nbsp; by &nbsp; {author_name}")

    entry_parts.append("  ")

    if license_info and license_info != "NOT_FOUND":
        entry_parts.append(f"&nbsp;&nbsp;⚖️&nbsp;&nbsp;{license_info}")

    result = "".join(entry_parts)

    if description:
        result += f"  \n{description}" + ("*  " if removed_from_origin else "")

    if removed_from_origin:
        result += "\n<sub>* Removed from origin</sub>"

    if primary_link and not removed_from_origin:
        _, is_github, owner, repo = parse_github_url(primary_link)
        if is_github and owner and repo:
            base_url = "https://github-readme-stats-fork-orpin.vercel.app/api/pin/"
            stats_url = f"{base_url}?repo={repo}&username={owner}&all_stats=true&stats_only=true"
            result += "\n\n<details>"
            result += "\n<summary>📊 GitHub Stats</summary>"
            result += f"\n\n![GitHub Stats for {repo}]({stats_url})"
            result += "\n\n</details>"
            result += "\n<br>"

    return result


def generate_toc(categories: list[dict], csv_data: list[dict]) -> str:
    """Generate plain markdown nested details TOC."""
    toc_lines: list[str] = []
    toc_lines.append("## Contents [🔝](#awesome-claude-code)")
    toc_lines.append("")
    toc_lines.append("<details open>")
    toc_lines.append("<summary>Table of Contents</summary>")
    toc_lines.append("")

    general_counter = 0
    # CLASSIC style headings include [🔝](#awesome-claude-code) which adds another dash
    has_back_to_top = True

    for category in categories:
        section_title = category.get("name", "")
        icon = category.get("icon", "")
        subcategories = category.get("subcategories", [])

        anchor = generate_toc_anchor(
            section_title, icon=icon, has_back_to_top_in_heading=has_back_to_top
        )

        if subcategories:
            toc_lines.append("- <details open>")
            toc_lines.append(f'  <summary><a href="#{anchor}">{section_title}</a></summary>')
            toc_lines.append("")

            for subcat in subcategories:
                sub_title = subcat["name"]

                category_name = category.get("name", "")
                resources = [
                    r
                    for r in csv_data
                    if r["Category"] == category_name
                    and r.get("Sub-Category", "").strip() == sub_title
                ]

                if resources:
                    sub_anchor, general_counter = generate_subcategory_anchor(
                        sub_title, general_counter, has_back_to_top_in_heading=has_back_to_top
                    )
                    toc_lines.append(f"  - [{sub_title}](#{sub_anchor})")

            toc_lines.append("")
            toc_lines.append("  </details>")
        else:
            toc_lines.append(f"- [{section_title}](#{anchor})")

        toc_lines.append("")

    toc_lines.append("</details>")
    return "\n".join(toc_lines).strip()


def generate_weekly_section(csv_data: list[dict]) -> str:
    """Generate weekly section with plain markdown."""
    lines: list[str] = []
    lines.append("## Latest Additions ✨ [🔝](#awesome-claude-code)")
    lines.append("")

    resources_sorted_by_date: list[tuple[datetime, dict]] = []
    for row in csv_data:
        date_added = row.get("Date Added", "").strip()
        if date_added:
            parsed_date = parse_resource_date(date_added)
            if parsed_date:
                resources_sorted_by_date.append((parsed_date, row))
    resources_sorted_by_date.sort(key=lambda x: x[0], reverse=True)

    latest_additions: list[dict[str, str]] = []
    cutoff_date = datetime.now() - timedelta(days=7)
    for dated_resource in resources_sorted_by_date:
        if dated_resource[0] >= cutoff_date or len(latest_additions) < 3:
            latest_additions.append(dated_resource[1])
        else:
            break

    lines.append("")
    for resource in latest_additions:
        lines.append(format_resource_entry(resource, include_separator=False))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_section_content(category: dict, csv_data: list[dict]) -> str:
    """Generate section with plain markdown headers."""
    lines: list[str] = []

    title = category.get("name", "")
    icon = category.get("icon", "")
    description = category.get("description", "").strip()
    category_name = category.get("name", "")
    subcategories = category.get("subcategories", [])

    header_text = f"{title} {icon}" if icon else title
    lines.append(f"## {header_text} [🔝](#awesome-claude-code)")
    lines.append("")

    if description:
        lines.append(f"> {description}")
        lines.append("")

    for subcat in subcategories:
        sub_title = subcat["name"]
        resources = [
            r
            for r in csv_data
            if r["Category"] == category_name and r.get("Sub-Category", "").strip() == sub_title
        ]

        if resources:
            lines.append("<details open>")
            lines.append(
                f'<summary><h3>{sub_title} <a href="#awesome-claude-code">🔝</a></h3></summary>'
            )
            lines.append("")

            for resource in resources:
                lines.append(format_resource_entry(resource, include_separator=False))
                lines.append("")

            lines.append("</details>")
            lines.append("")

    lines.append("<br>")
    return "\n".join(lines).rstrip() + "\n"
