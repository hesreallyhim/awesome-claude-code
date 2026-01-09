"""Visual README markup rendering helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from scripts.readme.helpers.readme_assets import (
    create_h3_svg_file,
    ensure_category_header_exists,
    ensure_separator_svg_exists,
    get_category_svg_filename,
    get_section_divider_svg,
    get_subcategory_svg_filename,
    save_resource_badge_svg,
)
from scripts.readme.helpers.readme_paths import asset_path_token
from scripts.readme.helpers.readme_utils import (
    generate_toc_anchor,
    parse_resource_date,
    sanitize_filename_from_anchor,
)
from scripts.utils.github_utils import parse_github_url
from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))


def format_resource_entry(
    row: dict,
    assets_dir: str | None = None,
    include_separator: bool = True,
) -> str:
    """Format a single resource entry with vintage manual styling for light mode."""
    display_name = row["Display Name"]
    primary_link = row["Primary Link"]
    author_name = row.get("Author Name", "").strip()
    description = row.get("Description", "").strip()
    removed_from_origin = row.get("Removed From Origin", "").strip().upper() == "TRUE"

    parts: list[str] = []

    if assets_dir:
        badge_filename = save_resource_badge_svg(display_name, author_name, assets_dir)
        parts.append(f'<a href="{primary_link}">')
        parts.append(f'<img src="{asset_path_token(badge_filename)}" alt="{display_name}">')
        parts.append("</a>")
    else:
        parts.append(f"[`{display_name}`]({primary_link})")
        if author_name:
            parts.append(f" by {author_name}")

    if description:
        parts.append("  \n")
        parts.append(f"_{description}_" + ("*" if removed_from_origin else ""))

    if removed_from_origin:
        parts.append("  \n")
        parts.append("<sub>* Removed from origin</sub>")

    if primary_link and not removed_from_origin:
        _, is_github, owner, repo = parse_github_url(primary_link)

        if is_github and owner and repo:
            base_url = "https://github-readme-stats-fork-orpin.vercel.app/api/pin/"
            stats_url = (
                f"{base_url}?repo={repo}&username={owner}&all_stats=true&stats_only=true"
                "&hide_border=true&bg_color=00000000&icon_color=FF0000&text_color=FF0000"
            )
            parts.append("  \n")
            parts.append(f"![GitHub Stats for {repo}]({stats_url})")

    if include_separator and assets_dir:
        separator_filename = ensure_separator_svg_exists(assets_dir)
        parts.append("\n\n")
        parts.append('<div align="center">')
        parts.append(f'<img src="{asset_path_token(separator_filename)}" alt="">')
        parts.append("</div>")
        parts.append("\n")

    return "".join(parts)


def generate_weekly_section(
    csv_data: list[dict],
    assets_dir: str | None = None,
) -> str:
    """Generate the latest additions section that appears above Contents."""
    lines: list[str] = []

    lines.append('<div align="center">')
    lines.append("  <picture>")
    lines.append(
        f'    <source media="(prefers-color-scheme: dark)" '
        f'srcset="{asset_path_token("latest-additions-header.svg")}">'
    )
    lines.append(
        f'    <source media="(prefers-color-scheme: light)" '
        f'srcset="{asset_path_token("latest-additions-header-light.svg")}">'
    )
    lines.append(
        f'    <img src="{asset_path_token("latest-additions-header-light.svg")}" '
        'alt="LATEST ADDITIONS">'
    )
    lines.append("  </picture>")
    lines.append("</div>")
    lines.append("")

    resources_sorted_by_date: list[tuple[datetime, dict]] = []
    for row in csv_data:
        date_added = row.get("Date Added", "").strip()
        if date_added:
            parsed_date = parse_resource_date(date_added)
            if parsed_date:
                resources_sorted_by_date.append((parsed_date, row))
    resources_sorted_by_date.sort(key=lambda x: x[0], reverse=True)

    latest_additions: list[dict] = []
    cutoff_date = datetime.now() - timedelta(days=7)
    for dated_resource in resources_sorted_by_date:
        if dated_resource[0] >= cutoff_date or len(latest_additions) < 3:
            latest_additions.append(dated_resource[1])
        else:
            break

    for resource in latest_additions:
        lines.append(
            format_resource_entry(
                resource,
                assets_dir=assets_dir,
                include_separator=False,
            )
        )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_toc_from_categories(
    categories: list[dict] | None = None,
    csv_data: list[dict] | None = None,
    general_map: dict | None = None,
) -> str:
    """Generate simple table of contents as vertical list of SVG rows."""
    if categories is None:
        from scripts.categories.category_utils import category_manager

        categories = category_manager.get_categories_for_readme()

    toc_header = f"""<!-- Directory Tree Terminal - Theme Adaptive -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{asset_path_token("toc-header.svg")}">
  <source media="(prefers-color-scheme: light)" srcset="{asset_path_token("toc-header-light-anim-scanline.svg")}">
  <img src="{asset_path_token("toc-header-light-anim-scanline.svg")}" alt="Directory Listing" height="48" \
style="height:48px;max-width:none;">
</picture>"""

    toc_lines = [
        '<div style="overflow-x:auto;white-space:nowrap;text-align:left;">',
        f'<div style="height:48px;width:400px;overflow:hidden;display:block;">{toc_header}</div>',
    ]

    for category in categories:
        section_title = category["name"]
        category_name = category.get("name", "")
        category_id = category.get("id", "")
        # EXTRA style uses explicit IDs with trailing dash (no icon in anchor)
        anchor = generate_toc_anchor(section_title, icon=None, has_back_to_top_in_heading=True)

        svg_filename = get_category_svg_filename(category_id)

        dark_svg = svg_filename
        light_svg = svg_filename.replace(".svg", "-light-anim-scanline.svg")
        toc_lines.append('<div style="height:40px;width:400px;overflow:hidden;display:block;">')
        toc_lines.append(f'<a href="#{anchor}">')
        toc_lines.append("  <picture>")
        toc_lines.append(
            f'    <source media="(prefers-color-scheme: dark)" srcset="{asset_path_token(dark_svg)}">'
        )
        toc_lines.append(
            f'    <source media="(prefers-color-scheme: light)" srcset="{asset_path_token(light_svg)}">'
        )
        toc_lines.append(
            f'    <img src="{asset_path_token(light_svg)}" alt="{section_title}" '
            'height="40" style="height:40px;max-width:none;">'
        )
        toc_lines.append("  </picture>")
        toc_lines.append("</a>")
        toc_lines.append("</div>")

        subcategories = category.get("subcategories", [])

        if subcategories:
            for subcat in subcategories:
                sub_title = subcat["name"]
                subcat_id = subcat.get("id", "")

                include_subcategory = True
                if csv_data is not None:
                    resources = [
                        r
                        for r in csv_data
                        if r["Category"] == category_name
                        and r.get("Sub-Category", "").strip() == sub_title
                    ]
                    include_subcategory = bool(resources)

                if include_subcategory:
                    sub_anchor = (
                        sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")
                    )

                    if sub_title == "General":
                        if general_map is not None:
                            sub_anchor = general_map.get((category_id, sub_title), "general")
                        else:
                            sub_anchor = f"{category_id}-general"

                    svg_filename = get_subcategory_svg_filename(subcat_id)

                    dark_svg = svg_filename
                    light_svg = svg_filename.replace(".svg", "-light-anim-scanline.svg")
                    toc_lines.append(
                        '<div style="height:40px;width:400px;overflow:hidden;display:block;">'
                    )
                    toc_lines.append(f'<a href="#{sub_anchor}">')
                    toc_lines.append("  <picture>")
                    toc_lines.append(
                        f'    <source media="(prefers-color-scheme: dark)" '
                        f'srcset="{asset_path_token(dark_svg)}">'
                    )
                    toc_lines.append(
                        f'    <source media="(prefers-color-scheme: light)" '
                        f'srcset="{asset_path_token(light_svg)}">'
                    )
                    toc_lines.append(
                        f'    <img src="{asset_path_token(light_svg)}" alt="{sub_title}" '
                        'height="40" style="height:40px;max-width:none;">'
                    )
                    toc_lines.append("  </picture>")
                    toc_lines.append("</a>")
                    toc_lines.append("</div>")

    toc_lines.append("</div>")

    return "\n".join(toc_lines).strip()


def generate_section_content(
    category: dict,
    csv_data: list[dict],
    general_map: dict | None = None,
    assets_dir: str | None = None,
    section_index: int = 0,
) -> str:
    """Generate content for a category based on CSV data."""
    lines: list[str] = []

    category_id = category.get("id", "")
    title = category.get("name", "")
    icon = category.get("icon", "")
    description = category.get("description", "").strip()
    category_name = category.get("name", "")
    subcategories = category.get("subcategories", [])

    dark_divider, light_divider = get_section_divider_svg()
    lines.append('<div align="center">')
    lines.append("  <picture>")
    lines.append(
        f'    <source media="(prefers-color-scheme: dark)" srcset="{asset_path_token(dark_divider)}">'
    )
    lines.append(
        f'    <source media="(prefers-color-scheme: light)" srcset="{asset_path_token(light_divider)}">'
    )
    lines.append(
        f'    <img src="{asset_path_token(light_divider)}" alt="" width="100%" style="max-width: 800px;">'
    )
    lines.append("  </picture>")
    lines.append("</div>")
    lines.append("")

    # EXTRA style uses explicit IDs with trailing dash (no icon in anchor)
    anchor_id = generate_toc_anchor(title, icon=None, has_back_to_top_in_heading=True)

    section_number = str(section_index + 1).zfill(2)
    display_title = title
    if category_id == "workflows":
        display_title = "Workflows & Guides"
    assert assets_dir is not None
    dark_header, light_header = ensure_category_header_exists(
        category_id,
        display_title,
        section_number,
        assets_dir,
        icon=icon,
        always_regenerate=True,
    )

    lines.append(f'<h2 id="{anchor_id}">')
    lines.append('<div align="center">')
    lines.append("  <picture>")
    lines.append(
        f'    <source media="(prefers-color-scheme: dark)" srcset="{asset_path_token(dark_header)}">'
    )
    lines.append(
        f'    <source media="(prefers-color-scheme: light)" srcset="{asset_path_token(light_header)}">'
    )
    lines.append(
        f'    <img src="{asset_path_token(light_header)}" alt="{title}" style="max-width: 600px;">'
    )
    lines.append("  </picture>")
    lines.append("</div>")
    lines.append("</h2>")
    lines.append('<div align="right"><a href="#awesome-claude-code">🔝 Back to top</a></div>')
    lines.append("")

    if description:
        lines.append("")
        lines.append('<div align="center">')
        lines.append("  <picture>")
        lines.append(
            f'    <source media="(prefers-color-scheme: dark)" '
            f'srcset="{asset_path_token("desc-box-top.svg")}">'
        )
        lines.append(
            f'    <source media="(prefers-color-scheme: light)" '
            f'srcset="{asset_path_token("desc-box-top-light.svg")}">'
        )
        lines.append(
            f'    <img src="{asset_path_token("desc-box-top-light.svg")}" alt="" '
            'width="100%" style="max-width: 900px;">'
        )
        lines.append("  </picture>")
        lines.append("</div>")
        lines.append(f"<h3 id='{anchor_id}' align='center'>{description}</h3>")
        lines.append('<div align="center">')
        lines.append("  <picture>")
        lines.append(
            f'    <source media="(prefers-color-scheme: dark)" '
            f'srcset="{asset_path_token("desc-box-bottom.svg")}">'
        )
        lines.append(
            f'    <source media="(prefers-color-scheme: light)" '
            f'srcset="{asset_path_token("desc-box-bottom-light.svg")}">'
        )
        lines.append(
            f'    <img src="{asset_path_token("desc-box-bottom-light.svg")}" alt="" '
            'width="100%" style="max-width: 900px;">'
        )
        lines.append("  </picture>")
        lines.append("</div>")

        for subcat in subcategories:
            sub_title = subcat["name"]

            resources = [
                r
                for r in csv_data
                if r["Category"] == category_name and r.get("Sub-Category", "").strip() == sub_title
            ]

            if resources:
                lines.append("")

                sub_anchor = sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")

                if sub_title == "General":
                    if general_map is not None:
                        sub_anchor = general_map.get((category_id, sub_title), "general")
                    else:
                        sub_anchor = f"{category_id}-general"

                sub_anchor_id = sub_anchor

                safe_filename = sanitize_filename_from_anchor(sub_anchor)
                svg_filename = f"subheader_{safe_filename}.svg"

                assets_root = str(REPO_ROOT / "assets")
                create_h3_svg_file(sub_title, svg_filename, assets_root)

                lines.append(f'<details open id="{sub_anchor_id}">')
                lines.append(
                    f'<summary><span><picture><img src="{asset_path_token(svg_filename)}" '
                    f'alt="{sub_title}" align="absmiddle"></picture></span></summary>'
                )
                lines.append("")

                for resource in resources:
                    lines.append(
                        format_resource_entry(
                            resource,
                            assets_dir=assets_dir,
                        )
                    )
                    lines.append("")

                lines.append("</details>")

    return "\n".join(lines).rstrip() + "\n"


def generate_repo_ticker() -> str:
    """Generate the animated SVG repo ticker for visual theme."""
    return f"""<div align="center">

<br />

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{asset_path_token("repo-ticker.svg")}">
  <source media="(prefers-color-scheme: light)" srcset="{asset_path_token("repo-ticker-light.svg")}">
  <img src="{asset_path_token("repo-ticker-light.svg")}" alt="Featured Claude Code Projects" width="100%">
</picture>

</div>"""
