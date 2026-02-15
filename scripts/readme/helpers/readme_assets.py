"""SVG asset generation and file helpers for README generation."""

from __future__ import annotations

import glob
import os
import re

from scripts.readme.helpers.readme_utils import format_category_dir_name
from scripts.readme.svg_templates.badges import (
    generate_resource_badge_svg,
    render_flat_category_badge_svg,
    render_flat_sort_badge_svg,
)
from scripts.readme.svg_templates.dividers import (
    generate_desc_box_light_svg,
    generate_section_divider_light_svg,
)
from scripts.readme.svg_templates.dividers import (
    generate_entry_separator_svg as _generate_entry_separator_svg,
)
from scripts.readme.svg_templates.headers import (
    generate_category_header_light_svg,
    render_h2_svg,
    render_h3_svg,
)
from scripts.readme.svg_templates.toc import (
    _normalize_svg_root,
    generate_toc_header_light_svg,
    generate_toc_row_light_svg,
    generate_toc_row_svg,
    generate_toc_sub_light_svg,
    generate_toc_sub_svg,
)


def create_h2_svg_file(text: str, filename: str, assets_dir: str, icon: str = "") -> str:
    """Create an animated hero-centered H2 header SVG file."""
    svg_content = render_h2_svg(text, icon=icon)

    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def create_h3_svg_file(text: str, filename: str, assets_dir: str) -> str:
    """Create an animated minimal-inline H3 header SVG file."""
    svg_content = render_h3_svg(text)

    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)
        if not svg_content.endswith("\n"):
            f.write("\n")

    return filename


def ensure_category_header_exists(
    category_id: str,
    title: str,
    section_number: str,
    assets_dir: str,
    icon: str = "",
    always_regenerate: bool = True,
) -> tuple[str, str]:
    """Ensure category header SVGs exist, generating them if needed."""
    safe_name = category_id.replace("-", "_")
    dark_filename = f"header_{safe_name}.svg"
    light_filename = f"header_{safe_name}-light-v3.svg"

    dark_path = os.path.join(assets_dir, dark_filename)
    if always_regenerate or not os.path.exists(dark_path):
        create_h2_svg_file(title, dark_filename, assets_dir, icon=icon)

    light_path = os.path.join(assets_dir, light_filename)
    if always_regenerate or not os.path.exists(light_path):
        svg_content = generate_category_header_light_svg(title, section_number)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return (dark_filename, light_filename)


def ensure_section_divider_exists(variant: int, assets_dir: str) -> tuple[str, str]:
    """Ensure section divider SVG exists, generating if needed."""
    dark_filename = "section-divider-alt2.svg"
    light_filename = f"section-divider-light-manual-v{variant}.svg"

    light_path = os.path.join(assets_dir, light_filename)
    if not os.path.exists(light_path):
        svg_content = generate_section_divider_light_svg(variant)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return (dark_filename, light_filename)


def ensure_desc_box_exists(position: str, assets_dir: str) -> str:
    """Ensure desc box SVG exists, generating if needed."""
    filename = f"desc-box-{position}-light.svg"
    filepath = os.path.join(assets_dir, filename)

    if not os.path.exists(filepath):
        svg_content = generate_desc_box_light_svg(position)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return filename


def ensure_toc_row_exists(
    category_id: str,
    directory_name: str,
    description: str,
    assets_dir: str,
    always_regenerate: bool = True,
) -> str:
    """Ensure TOC row SVG exists, generating if needed."""
    filename = f"toc-row-{category_id}.svg"
    filepath = os.path.join(assets_dir, filename)

    if always_regenerate or not os.path.exists(filepath):
        svg_content = generate_toc_row_svg(directory_name, description)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return filename


def ensure_toc_sub_exists(
    subcat_id: str,
    directory_name: str,
    description: str,
    assets_dir: str,
    always_regenerate: bool = True,
) -> str:
    """Ensure TOC subcategory SVG exists, generating if needed."""
    filename = f"toc-sub-{subcat_id}.svg"
    filepath = os.path.join(assets_dir, filename)

    if always_regenerate or not os.path.exists(filepath):
        svg_content = generate_toc_sub_svg(directory_name, description)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return filename


def get_category_svg_filename(category_id: str) -> str:
    """Map category ID to SVG filename."""
    svg_map = {
        "skills": "toc-row-skills.svg",
        "workflows": "toc-row-workflows.svg",
        "tooling": "toc-row-tooling.svg",
        "statusline": "toc-row-statusline.svg",
        "hooks": "toc-row-custom.svg",
        "slash-commands": "toc-row-commands.svg",
        "claude-md-files": "toc-row-config.svg",
        "alternative-clients": "toc-row-clients.svg",
        "official-documentation": "toc-row-docs.svg",
    }
    return svg_map.get(category_id, f"toc-row-{category_id}.svg")


def get_subcategory_svg_filename(subcat_id: str) -> str:
    """Map subcategory ID to SVG filename."""
    svg_map = {
        "general": "toc-sub-general.svg",
        "ide-integrations": "toc-sub-ide.svg",
        "usage-monitors": "toc-sub-monitors.svg",
        "orchestrators": "toc-sub-orchestrators.svg",
        "config-managers": "toc-sub-config-managers.svg",
        "version-control-git": "toc-sub-git.svg",
        "code-analysis-testing": "toc-sub-code-analysis.svg",
        "context-loading-priming": "toc-sub-context.svg",
        "documentation-changelogs": "toc-sub-documentation.svg",
        "ci-deployment": "toc-sub-ci.svg",
        "project-task-management": "toc-sub-project-mgmt.svg",
        "miscellaneous": "toc-sub-misc.svg",
        "language-specific": "toc-sub-language.svg",
        "domain-specific": "toc-sub-domain.svg",
        "project-scaffolding-mcp": "toc-sub-scaffolding.svg",
        "ralph-wiggum": "toc-sub-ralph-wiggum.svg",
    }
    return svg_map.get(subcat_id, f"toc-sub-{subcat_id}.svg")


def get_category_header_svg(category_id: str) -> tuple[str, str]:
    """Map category ID to pre-made header SVG filenames (dark and light variants)."""
    header_map = {
        "skills": ("header_agent_skills.svg", "header_agent_skills-light-v3.svg"),
        "workflows": (
            "header_workflows_knowledge_guides.svg",
            "header_workflows_knowledge_guides-light-v3.svg",
        ),
        "tooling": ("header_tooling.svg", "header_tooling-light-v3.svg"),
        "statusline": ("header_status_lines.svg", "header_status_lines-light-v3.svg"),
        "hooks": ("header_hooks.svg", "header_hooks-light-v3.svg"),
        "slash-commands": (
            "header_slash_commands.svg",
            "header_slash_commands-light-v3.svg",
        ),
        "claude-md-files": (
            "header_claudemd_files.svg",
            "header_claudemd_files-light-v3.svg",
        ),
        "alternative-clients": (
            "header_alternative_clients.svg",
            "header_alternative_clients-light-v3.svg",
        ),
        "official-documentation": (
            "header_official_documentation.svg",
            "header_official_documentation-light-v3.svg",
        ),
    }
    return header_map.get(
        category_id, (f"header_{category_id}.svg", f"header_{category_id}-light-v3.svg")
    )


_section_divider_counter = 0


def get_section_divider_svg() -> tuple[str, str]:
    """Get the next section divider SVG filenames."""
    global _section_divider_counter
    variant = (_section_divider_counter % 3) + 1
    _section_divider_counter += 1
    return ("section-divider-alt2.svg", f"section-divider-light-manual-v{variant}.svg")


def normalize_toc_svgs(assets_dir: str) -> None:
    """Normalize TOC row/sub SVGs to enforce consistent display height/anchoring."""
    patterns = ["toc-row-*.svg", "toc-sub-*.svg", "toc-header*.svg"]
    for pattern in patterns:
        for path in glob.glob(os.path.join(assets_dir, pattern)):
            with open(path, encoding="utf-8") as f:
                content = f.read()

            match = re.search(r"<svg[^>]*>", content)
            if not match:
                continue

            root_tag = match.group(0)
            is_header = "toc-header" in os.path.basename(path)
            target_width = 400
            target_height = 48 if is_header else 40

            normalized_tag = _normalize_svg_root(root_tag, target_width, target_height)
            if normalized_tag != root_tag:
                content = content.replace(root_tag, normalized_tag, 1)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)


def regenerate_main_toc_svgs(categories: list[dict], assets_dir: str) -> None:
    """Regenerate main category TOC row SVGs with standardized styling."""
    for category in categories:
        display_dir = format_category_dir_name(category.get("name", ""), category.get("id", ""))
        description = category.get("description", "")

        dark_filename = get_category_svg_filename(category.get("id", ""))
        dark_path = os.path.join(assets_dir, dark_filename)
        svg_content = generate_toc_row_svg(display_dir, description)
        with open(dark_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        light_path = dark_path.replace(".svg", "-light-anim-scanline.svg")
        light_svg = generate_toc_row_light_svg(display_dir, description)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(light_svg)


def regenerate_sub_toc_svgs(categories: list[dict], assets_dir: str) -> None:
    """Regenerate subcategory TOC SVGs to keep sizing consistent."""
    for category in categories:
        subcats = category.get("subcategories", [])
        for subcat in subcats:
            display_dir = subcat.get("name", "")
            description = subcat.get("description", "")
            dark_filename = get_subcategory_svg_filename(subcat.get("id", ""))
            dark_path = os.path.join(assets_dir, dark_filename)
            svg_content = generate_toc_sub_svg(display_dir, description)
            with open(dark_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            light_path = dark_path.replace(".svg", "-light-anim-scanline.svg")
            light_svg = generate_toc_sub_light_svg(display_dir, description)
            with open(light_path, "w", encoding="utf-8") as f:
                f.write(light_svg)


def regenerate_toc_header(assets_dir: str) -> None:
    """Regenerate the light-mode TOC header for consistent sizing."""
    light_header_path = os.path.join(assets_dir, "toc-header-light-anim-scanline.svg")
    light_header_svg = generate_toc_header_light_svg()
    with open(light_header_path, "w", encoding="utf-8") as f:
        f.write(light_header_svg)


def save_resource_badge_svg(display_name: str, author_name: str, assets_dir: str) -> str:
    """Save a resource name SVG badge to the assets directory and return the filename."""
    safe_name = re.sub(r"[^a-zA-Z0-9]", "-", display_name.lower())
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    filename = f"badge-{safe_name}.svg"

    svg_content = generate_resource_badge_svg(display_name, author_name)

    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)
        if not svg_content.endswith("\n"):
            f.write("\n")

    return filename


def generate_entry_separator_svg() -> str:
    """Generate a small separator SVG between entries in vintage manual style."""
    return _generate_entry_separator_svg()


def ensure_separator_svg_exists(assets_dir: str) -> str:
    """Return the animated entry separator SVG filename."""
    _ = assets_dir
    return "entry-separator-light-animated.svg"


def generate_flat_badges(assets_dir: str, sort_types: dict, categories: dict) -> None:
    """Generate all sort and category badge SVGs."""
    for slug, (display, color, _) in sort_types.items():
        svg = render_flat_sort_badge_svg(display, color)
        filepath = os.path.join(assets_dir, f"badge-sort-{slug}.svg")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)

    for slug, (_, display, color) in categories.items():
        width = max(70, len(display) * 10 + 30)
        svg = render_flat_category_badge_svg(display, color, width)
        filepath = os.path.join(assets_dir, f"badge-cat-{slug}.svg")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)
