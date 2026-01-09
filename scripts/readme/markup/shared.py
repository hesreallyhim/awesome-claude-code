"""Markdown/HTML rendering helpers shared across README styles."""

from __future__ import annotations

import os
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from scripts.readme.helpers.readme_config import CONFIG, get_style_selector_target
from scripts.readme.helpers.readme_paths import asset_path_token, resolve_relative_link


def generate_style_selector(
    current_style: str, output_path: Path, repo_root: Path | None = None
) -> str:
    """Generate the style selector HTML for a README."""
    styles = CONFIG.get("styles", {})
    style_order = CONFIG.get("style_order", ["extra", "classic", "flat", "awesome"])

    lines = ['<h3 align="center">Pick Your Style:</h3>', '<p align="center">']

    for style_id in style_order:
        style_config = styles.get(style_id, {})
        name = style_config.get("name", style_id.title())
        badge = style_config.get("badge", f"badge-style-{style_id}.svg")
        highlight_color = style_config.get("highlight_color", "#666666")

        target_path = Path(get_style_selector_target(style_id))
        href = resolve_relative_link(output_path, target_path, repo_root)

        if style_id == current_style:
            style_attr = f' style="border: 2px solid {highlight_color}; border-radius: 4px;"'
        else:
            style_attr = ""

        badge_src = asset_path_token(badge)
        lines.append(
            f'<a href="{href}"><img src="{badge_src}" alt="{name}" height="28"{style_attr}></a>'
        )

    lines.append("</p>")
    return "\n".join(lines)


def load_announcements(template_dir: str) -> str:
    """Load announcements from the announcements.yaml file and format as markdown."""
    announcements_path = os.path.join(template_dir, "announcements.yaml")
    if os.path.exists(announcements_path):
        with open(announcements_path, encoding="utf-8") as f:
            announcements_data = yaml.safe_load(f)

        if not announcements_data:
            return ""

        markdown_lines = []
        markdown_lines.append("### Announcements [🔝](#awesome-claude-code)")
        markdown_lines.append("")

        markdown_lines.append("<details open>")
        markdown_lines.append("<summary>View Announcements</summary>")
        markdown_lines.append("")

        for entry in announcements_data:
            date = entry.get("date", "")
            title = entry.get("title", "")
            items = entry.get("items", [])

            markdown_lines.append("- <details open>")

            if title:
                markdown_lines.append(f"  <summary>{date} - {title}</summary>")
            else:
                markdown_lines.append(f"  <summary>{date}</summary>")

            markdown_lines.append("")

            for item in items:
                if isinstance(item, str):
                    markdown_lines.append(f"  - {item}")
                elif isinstance(item, dict):
                    summary = item.get("summary", "")
                    text = item.get("text", "")

                    if summary and text:
                        markdown_lines.append("  - <details open>")
                        markdown_lines.append(f"    <summary>{summary}</summary>")
                        markdown_lines.append("")

                        text_lines = text.strip().split("\n")
                        for i, line in enumerate(text_lines):
                            if i == 0:
                                markdown_lines.append(f"    - {line}")
                            else:
                                markdown_lines.append(f"      {line}")

                        markdown_lines.append("")
                        markdown_lines.append("    </details>")
                    elif summary:
                        markdown_lines.append(f"  - {summary}")
                    elif text:
                        markdown_lines.append(f"  - {text}")

                markdown_lines.append("")

            markdown_lines.append("  </details>")
            markdown_lines.append("")

        markdown_lines.append("</details>")

        return "\n".join(markdown_lines).strip()

    return ""
