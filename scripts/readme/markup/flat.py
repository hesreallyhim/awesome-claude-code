"""Flat list README markup rendering helpers."""

from __future__ import annotations

from scripts.readme.helpers.readme_paths import asset_path_token
from scripts.readme.helpers.readme_utils import extract_github_owner_repo


def generate_shields_badges(owner: str, repo: str) -> str:
    """Generate shields.io badge HTML for a GitHub repository."""
    badge_types = [
        ("stars", f"https://img.shields.io/github/stars/{owner}/{repo}"),
        ("forks", f"https://img.shields.io/github/forks/{owner}/{repo}"),
        ("issues", f"https://img.shields.io/github/issues/{owner}/{repo}"),
        ("prs", f"https://img.shields.io/github/issues-pr/{owner}/{repo}"),
        ("created", f"https://img.shields.io/github/created-at/{owner}/{repo}"),
        ("last-commit", f"https://img.shields.io/github/last-commit/{owner}/{repo}"),
        ("release-date", f"https://img.shields.io/github/release-date/{owner}/{repo}"),
        ("version", f"https://img.shields.io/github/v/release/{owner}/{repo}"),
        ("license", f"https://img.shields.io/github/license/{owner}/{repo}"),
    ]

    badges = []
    for alt, url in badge_types:
        badges.append(f'<img src="{url}?style=flat-square" alt="{alt}">')

    return " ".join(badges)


def generate_sort_navigation(
    category_slug: str,
    sort_type: str,
    sort_types: dict,
) -> str:
    """Generate sort option badges."""
    lines = ['<p align="center">']
    for slug, (display, color, _) in sort_types.items():
        filename = f"README_FLAT_{category_slug.upper()}_{slug.upper()}.md"
        is_selected = slug == sort_type
        style = f' style="border: 3px solid {color}; border-radius: 6px;"' if is_selected else ""
        lines.append(
            f'  <a href="{filename}"><img src="{asset_path_token(f"badge-sort-{slug}.svg")}" '
            f'alt="{display}" height="48"{style}></a>'
        )
    lines.append("</p>")
    return "\n".join(lines)


def generate_category_navigation(
    category_slug: str,
    sort_type: str,
    categories: dict,
) -> str:
    """Generate category filter badges."""
    lines = ['<p align="center">']
    for slug, (_, display, color) in categories.items():
        filename = f"README_FLAT_{slug.upper()}_{sort_type.upper()}.md"
        is_selected = slug == category_slug
        style = f' style="border: 2px solid {color}; border-radius: 4px;"' if is_selected else ""
        lines.append(
            f'  <a href="{filename}"><img src="{asset_path_token(f"badge-cat-{slug}.svg")}" '
            f'alt="{display}" height="28"{style}></a>'
        )
    lines.append("</p>")
    return "\n".join(lines)


def generate_navigation(
    category_slug: str,
    sort_type: str,
    categories: dict,
    sort_types: dict,
) -> str:
    """Generate combined navigation (sort + category)."""
    sort_nav = generate_sort_navigation(category_slug, sort_type, sort_types)
    cat_nav = generate_category_navigation(category_slug, sort_type, categories)
    _, _, sort_desc = sort_types[sort_type]
    _, cat_display, _ = categories[category_slug]

    current_info = f"**{cat_display}** sorted {sort_desc}"
    if sort_type == "releases":
        current_info += " (past 30 days)"

    return f"""{sort_nav}
<p align="center"><strong>Category:</strong></p>
{cat_nav}
<p align="center"><em>Currently viewing: {current_info}</em></p>"""


def generate_resources_table(sorted_resources: list[dict], sort_type: str) -> str:
    """Generate the resources table as HTML with shields.io badges for GitHub resources."""
    if not sorted_resources:
        if sort_type == "releases":
            return "*No releases in the past 30 days for this category.*"
        return "*No resources found in this category.*"

    lines: list[str] = ["<table>", "<thead>", "<tr>"]

    if sort_type == "releases":
        num_cols = 5
        lines.extend(
            [
                "<th>Resource</th>",
                "<th>Version</th>",
                "<th>Source</th>",
                "<th>Release Date</th>",
                "<th>Description</th>",
            ]
        )
    else:
        num_cols = 4
        lines.extend(
            [
                "<th>Resource</th>",
                "<th>Category</th>",
                "<th>Sub-Category</th>",
                "<th>Description</th>",
            ]
        )

    lines.extend(["</tr>", "</thead>", "<tbody>"])

    for row in sorted_resources:
        display_name = row.get("Display Name", "").strip()
        primary_link = row.get("Primary Link", "").strip()
        author_name = row.get("Author Name", "").strip()
        author_link = row.get("Author Link", "").strip()

        if primary_link:
            resource_html = f'<a href="{primary_link}"><b>{display_name}</b></a>'
        else:
            resource_html = f"<b>{display_name}</b>"

        if author_name and author_link:
            author_html = f'<a href="{author_link}">{author_name}</a>'
        else:
            author_html = author_name or ""

        resource_cell = f"{resource_html}<br>by {author_html}" if author_html else resource_html

        lines.append("<tr>")
        lines.append(f"<td>{resource_cell}</td>")

        if sort_type == "releases":
            version = row.get("Release Version", "").strip() or "-"
            source = row.get("Release Source", "").strip()
            source_display = {
                "github-releases": "GitHub",
                "npm": "npm",
                "pypi": "PyPI",
                "crates": "crates.io",
                "homebrew": "Homebrew",
                "readme": "README",
            }.get(source, source or "-")
            release_date = row.get("Latest Release", "")[:10] if row.get("Latest Release") else "-"
            description = row.get("Description", "").strip()

            lines.append(f"<td>{version}</td>")
            lines.append(f"<td>{source_display}</td>")
            lines.append(f"<td>{release_date}</td>")
            lines.append(f"<td>{description}</td>")
        else:
            category = row.get("Category", "").strip() or "-"
            sub_category = row.get("Sub-Category", "").strip() or "-"
            description = row.get("Description", "").strip()

            lines.append(f"<td>{category}</td>")
            lines.append(f"<td>{sub_category}</td>")
            lines.append(f"<td>{description}</td>")

        lines.append("</tr>")

        if primary_link:
            github_info = extract_github_owner_repo(primary_link)
            if github_info:
                owner, repo = github_info
                badges = generate_shields_badges(owner, repo)
                lines.append("<tr>")
                lines.append(f'<td colspan="{num_cols}">{badges}</td>')
                lines.append("</tr>")

    lines.extend(["</tbody>", "</table>"])
    return "\n".join(lines)


def get_default_template() -> str:
    """Return default template content."""
    return """<!--lint disable remark-lint:awesome-badge-->

{{STYLE_SELECTOR}}

# Awesome Claude Code (Flat)

[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)

A flat list view of all resources. Category: **{{CATEGORY_NAME}}** | Sorted: {{SORT_DESC}}

---

## Sort By:

{{NAVIGATION}}

---

## Resources
{{RELEASES_DISCLAIMER}}
{{RESOURCES_TABLE}}

---

**Total Resources:** {{RESOURCE_COUNT}}

**Last Generated:** {{GENERATED_DATE}}
"""
