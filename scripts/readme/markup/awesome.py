"""Awesome-list README markdown rendering helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from scripts.readme.helpers.readme_paths import asset_path_token
from scripts.readme.helpers.readme_utils import (
    generate_subcategory_anchor,
    generate_toc_anchor,
    parse_resource_date,
)


def format_resource_entry(row: dict, include_separator: bool = True) -> str:
    """Format resource in awesome list style."""
    _ = include_separator
    display_name = row["Display Name"]
    primary_link = row["Primary Link"]
    author_name = row.get("Author Name", "").strip()
    author_link = row.get("Author Link", "").strip()
    description = row.get("Description", "").strip()
    removed_from_origin = row.get("Removed From Origin", "").strip().upper() == "TRUE"

    entry_parts: list[str] = []

    if primary_link:
        entry_parts.append(f"[{display_name}]({primary_link})")
    else:
        entry_parts.append(display_name)

    if author_name:
        if author_link:
            entry_parts.append(f" by [{author_name}]({author_link})")
        else:
            entry_parts.append(f" by {author_name}")

    if description:
        desc = description.rstrip()
        if not desc.endswith((".", "!", "?")):
            desc += "."
        entry_parts.append(f" - {desc}")

    result = "- " + "".join(entry_parts)

    if removed_from_origin:
        result += " *(Removed from origin)*"

    return result


def generate_toc(categories: list[dict], csv_data: list[dict]) -> str:
    """Generate plain markdown TOC for awesome list style."""
    toc_lines: list[str] = []
    toc_lines.append("## Contents")
    toc_lines.append("")

    general_counter = 0

    for category in categories:
        section_title = category.get("name", "")
        icon = category.get("icon", "")
        subcategories = category.get("subcategories", [])

        anchor = generate_toc_anchor(section_title, icon=icon)
        display_title = f"{section_title} {icon}" if icon else section_title

        if subcategories:
            category_name = category.get("name", "")
            has_resources = any(r["Category"] == category_name for r in csv_data)

            if has_resources:
                toc_lines.append(f"- [{display_title}](#{anchor})")

                for subcat in subcategories:
                    sub_title = subcat["name"]

                    resources = [
                        r
                        for r in csv_data
                        if r["Category"] == category_name
                        and r.get("Sub-Category", "").strip() == sub_title
                    ]

                    if resources:
                        sub_anchor, general_counter = generate_subcategory_anchor(
                            sub_title, general_counter
                        )
                        toc_lines.append(f"  - [{sub_title}](#{sub_anchor})")
        else:
            toc_lines.append(f"- [{display_title}](#{anchor})")

    return "\n".join(toc_lines).strip()


def generate_weekly_section(csv_data: list[dict]) -> str:
    """Generate weekly section with plain markdown for awesome list."""
    lines: list[str] = []
    lines.append("## Latest Additions")
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

    for resource in latest_additions:
        lines.append(format_resource_entry(resource, include_separator=False))

    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_section_content(category: dict, csv_data: list[dict]) -> str:
    """Generate section with plain markdown headers in awesome list format."""
    lines: list[str] = []

    title = category.get("name", "")
    icon = category.get("icon", "")
    description = category.get("description", "").strip()
    category_name = category.get("name", "")
    subcategories = category.get("subcategories", [])

    header_text = f"{title} {icon}" if icon else title
    lines.append(f"## {header_text}")
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
            lines.append(f"### {sub_title}")
            lines.append("")

            for resource in resources:
                lines.append(format_resource_entry(resource, include_separator=False))

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_repo_ticker() -> str:
    """Generate the awesome-style animated SVG repo ticker."""
    return f"""<div align="center">

<img src="{asset_path_token("repo-ticker-awesome.svg")}" alt="Featured Claude Code Projects" width="100%">

</div>"""
