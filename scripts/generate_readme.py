#!/usr/bin/env python3
"""
Template-based README generator for the Awesome Claude Code repository.
Reads resource metadata from CSV and generates README using templates.
"""

import csv
import os
import shutil
import sys
from datetime import datetime, timedelta

import yaml  # type: ignore[import-untyped]


def load_template(template_path):
    """Load a template file."""
    with open(template_path, encoding="utf-8") as f:
        return f.read()


def load_announcements(template_dir):
    """Load announcements from the announcements.yaml file and format as markdown."""
    announcements_path = os.path.join(template_dir, "announcements.yaml")
    if os.path.exists(announcements_path):
        with open(announcements_path, encoding="utf-8") as f:
            announcements_data = yaml.safe_load(f)

        if not announcements_data:
            return ""

        # Format the YAML data into markdown with nested collapsible sections using lists
        markdown_lines = []

        # Make the entire announcements section collapsible
        markdown_lines.append("<details>")
        markdown_lines.append("<summary>View Announcements</summary>")
        markdown_lines.append("")

        # Use unordered list for first level indentation
        for entry in announcements_data:
            date = entry.get("date", "")
            title = entry.get("title", "")
            items = entry.get("items", [])

            # Make each date group a collapsible list item
            markdown_lines.append("- <details>")

            # Create summary for date group
            if title:
                markdown_lines.append(f"  <summary>{date} - {title}</summary>")
            else:
                markdown_lines.append(f"  <summary>{date}</summary>")

            markdown_lines.append("")

            # Use nested list for second level indentation
            # Process items - can be strings or objects with summary/text
            for item in items:
                if isinstance(item, str):
                    # Simple string item - render as nested bullet point
                    markdown_lines.append(f"  - {item}")
                elif isinstance(item, dict):
                    # Object with summary and text - render as collapsible details
                    summary = item.get("summary", "")
                    text = item.get("text", "")

                    if summary and text:
                        markdown_lines.append("  - <details>")
                        markdown_lines.append(f"    <summary>{summary}</summary>")
                        markdown_lines.append("")

                        # Handle multi-line text properly with triple nesting
                        text_lines = text.strip().split("\n")
                        for i, line in enumerate(text_lines):
                            if i == 0:
                                markdown_lines.append(f"    - {line}")
                            else:
                                # Continue paragraphs without bullet points
                                markdown_lines.append(f"      {line}")

                        markdown_lines.append("")
                        markdown_lines.append("    </details>")
                    elif summary:
                        # If only summary, just render as nested bullet point
                        markdown_lines.append(f"  - {summary}")
                    elif text:
                        # If only text, render as nested bullet point
                        markdown_lines.append(f"  - {text}")

                markdown_lines.append("")

            # Close date group details
            markdown_lines.append("  </details>")
            markdown_lines.append("")

        # Close main announcements details
        markdown_lines.append("</details>")

        return "\n".join(markdown_lines).strip()

    # Fallback to old .md file if YAML doesn't exist
    announcements_md_path = os.path.join(template_dir, "announcements.md")
    if os.path.exists(announcements_md_path):
        with open(announcements_md_path, encoding="utf-8") as f:
            return f.read().strip()

    return ""


def get_anchor_suffix_for_icon(icon):
    """
    Generate the appropriate anchor suffix for a section with an emoji icon.

    GitHub's markdown anchor generation for trailing emojis:
    1. Simple emojis (single Unicode codepoint): Stripped and replaced with a
       single dash "-"
    2. Emojis with variation selectors (U+FE00-FE0F): Base emoji is stripped
       and replaced with dash, variation selector becomes URL-encoded

    For example:
    - "## Tooling 🧰" → #tooling- (simple emoji becomes dash)
    - "## Official Documentation 🏛️" → #official-documentation-%EF%B8%8F
      (emoji becomes dash, VS-16 is URL-encoded)

    The 🏛️ emoji is actually two characters:
    - U+1F3DB (🏛) - Classical Building base character
    - U+FE0F - Variation Selector-16 (forces emoji presentation)

    Unicode has 16 variation selectors (U+FE00 to U+FE0F):
    - VS-1 to VS-15 (U+FE00-FE0E): Rarely used with emojis
    - VS-16 (U+FE0F): Common, forces colorful emoji presentation

    Args:
        icon: The emoji icon string from the category definition

    Returns:
        The appropriate suffix for the anchor link
        Examples: "-", "-%EF%B8%8F", "-%EF%B8%80", etc.
    """
    if not icon:
        # No icon means no suffix needed
        return ""

    # Check for any variation selector (U+FE00 to U+FE0F)
    # Note: We return after finding the first VS, as emojis typically have
    # only one variation selector. Multiple VSs in a single icon would be
    # extremely rare and likely invalid Unicode.
    vs_char = next((char for char in icon if 0xFE00 <= ord(char) <= 0xFE0F), None)
    if vs_char:
        # Found a variation selector - URL-encode it
        vs_bytes = vs_char.encode("utf-8")
        url_encoded = "".join(f"%{byte:02X}" for byte in vs_bytes)
        return f"-{url_encoded}"

    # No variation selector found - simple emoji gets replaced with dash
    return "-"


def generate_toc_from_categories():
    """Generate table of contents based on category definitions."""
    from category_utils import category_manager

    categories = category_manager.get_categories_for_readme()

    toc_lines = []

    # Make the entire TOC collapsible (open by default)
    toc_lines.append("<details open>")
    toc_lines.append("<summary>Table of Contents</summary>")
    toc_lines.append("")

    # Use unordered list for categories
    for category in categories:
        # Main section link
        section_title = category["name"]
        anchor = (
            section_title.lower()
            .replace(" ", "-")
            .replace("&", "")
            .replace("/", "")
            .replace(".", "")
        )

        # Get the appropriate anchor suffix based on the category's icon
        icon = category.get("icon", "")
        anchor_suffix = get_anchor_suffix_for_icon(icon)

        # Check if this category has subcategories
        subcategories = category.get("subcategories", [])

        if subcategories:
            # Make category collapsible if it has subcategories (open by default)
            toc_lines.append("- <details open>")
            toc_lines.append(
                f'  <summary><a href="#{anchor}{anchor_suffix}">{section_title}</a></summary>'
            )
            toc_lines.append("")

            # Add subcategories as nested list
            for subcat in subcategories:
                sub_title = subcat["name"]
                sub_anchor = sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")
                toc_lines.append(f"  - [{sub_title}](#{sub_anchor})")

            toc_lines.append("")
            toc_lines.append("  </details>")
        else:
            # Simple link if no subcategories
            toc_lines.append(f"- [{section_title}](#{anchor}{anchor_suffix})")

        toc_lines.append("")

    # Close main TOC details
    toc_lines.append("</details>")

    return "\n".join(toc_lines).strip()


def format_resource_entry(row):
    """Format a single resource entry."""
    display_name = row["Display Name"]
    primary_link = row["Primary Link"]
    author_name = row.get("Author Name", "").strip()
    author_link = row.get("Author Link", "").strip()
    description = row.get("Description", "").strip()
    license_info = row.get("License", "").strip()

    # Build the entry
    entry_parts = [f"[`{display_name}`]({primary_link})"]

    # Add author information
    if author_name:
        if author_link:
            entry_parts.append(f" &nbsp; by &nbsp; [{author_name}]({author_link})")
        else:
            entry_parts.append(f" &nbsp; by &nbsp; {author_name}")

    entry_parts.append("  ")  # Add double-space for Markdown newline

    # Add license if not empty and not "NOT_FOUND"
    if license_info and license_info != "NOT_FOUND":
        entry_parts.append(f"&nbsp;&nbsp;⚖️&nbsp;&nbsp;{license_info}")

    # Add description on new line if present
    result = "".join(entry_parts)
    if description:
        result += f"  \n{description}"

    return result


def parse_resource_date(date_string):
    """Parse a date string that may include timestamp information.

    Handles formats:
    - YYYY-MM-DD
    - YYYY-MM-DD:HH-MM-SS

    Returns datetime object or None if parsing fails.
    """
    if not date_string:
        return None

    date_string = date_string.strip()

    # Try different date formats
    date_formats = [
        "%Y-%m-%d:%H-%M-%S",  # Full format with timestamp
        "%Y-%m-%d",  # Date only format
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None


def generate_weekly_section(csv_data):
    """Generate the weekly resources section that appears above Contents."""
    lines = []

    lines.append("## This Week's Additions ✨")
    lines.append("")
    lines.append("> Resources added in the past 7 days")

    # Get resources added in the past week
    one_week_ago = datetime.now() - timedelta(days=7)
    weekly_resources = []

    for resource in csv_data:
        date_added = resource.get("Date Added", "")
        resource_date = parse_resource_date(date_added)

        if resource_date and resource_date >= one_week_ago:
            weekly_resources.append(resource)

    if weekly_resources:
        lines.append("")
        # Sort by date added (newest first) using parsed dates
        weekly_resources.sort(
            key=lambda x: parse_resource_date(x.get("Date Added", "")) or datetime.min, reverse=True
        )

        for resource in weekly_resources:
            lines.append(format_resource_entry(resource))
            lines.append("")
    else:
        lines.append("")
        lines.append("*No new resources added this week.*")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_section_content(category, csv_data):
    """Generate content for a category based on CSV data."""
    lines = []

    # Get category details
    title = category.get("name", "")
    icon = category.get("icon", "")
    description = category.get("description", "").strip()
    category_name = category.get("name", "")
    subcategories = category.get("subcategories", [])

    # Add section title (header outside of disclosure)
    if icon:
        lines.append(f"## {title} {icon}")
    else:
        lines.append(f"## {title}")

    # Add section description if present
    if description:
        lines.append("")
        lines.append(description)

    # Create anchor for this section
    anchor = title.lower().replace(" ", "-").replace("&", "").replace("/", "").replace(".", "")
    anchor_suffix = get_anchor_suffix_for_icon(icon) if icon else ""
    full_anchor = f"#{anchor}{anchor_suffix}"

    # Start the main category disclosure element (open by default)
    lines.append("")
    lines.append("<details open>")
    lines.append(f'<summary><a href="{full_anchor}">View {title}</a></summary>')

    # Get resources for this section
    if not subcategories:
        # No subsections - render all resources for this category
        resources = [
            r
            for r in csv_data
            if r["Category"] == category_name and not r.get("Sub-Category", "").strip()
        ]
        if resources:
            lines.append("")
            for resource in resources:
                lines.append(format_resource_entry(resource))
                lines.append("")
    else:
        # Has subsections - first render main category resources without subcategory
        main_resources = [
            r
            for r in csv_data
            if r["Category"] == category_name and not r.get("Sub-Category", "").strip()
        ]
        if main_resources:
            lines.append("")
            for resource in main_resources:
                lines.append(format_resource_entry(resource))
                lines.append("")

        # Then render each subsection with header above disclosure
        for subcat in subcategories:
            sub_title = subcat["name"]

            resources = [
                r
                for r in csv_data
                if r["Category"] == category_name and r.get("Sub-Category", "").strip() == sub_title
            ]

            if resources:
                lines.append("")
                # Add subcategory header (outside disclosure)
                lines.append(f"### {sub_title}")

                # Create anchor for subcategory
                sub_anchor = sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")

                # Start subcategory disclosure element (open by default)
                lines.append("")
                lines.append("<details open>")
                lines.append(f'<summary><a href="#{sub_anchor}">View {sub_title}</a></summary>')
                lines.append("")

                for resource in resources:
                    lines.append(format_resource_entry(resource))
                    lines.append("")

                # Close subcategory disclosure element
                lines.append("</details>")

    # Close main category disclosure element
    lines.append("")
    lines.append("</details>")

    return "\n".join(lines).rstrip() + "\n"


def load_overrides(template_dir):
    """Load resource overrides."""
    override_path = os.path.join(template_dir, "resource-overrides.yaml")
    if not os.path.exists(override_path):
        return {}

    with open(override_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("overrides", {})


def apply_overrides(row, overrides):
    """Apply overrides to a resource row."""
    resource_id = row.get("ID", "")
    if not resource_id or resource_id not in overrides:
        return row

    override_config = overrides[resource_id]

    # Apply overrides (excluding locked flags and notes)
    for field, value in override_config.items():
        if not field.endswith("_locked") and field != "notes":
            if field == "license":
                row["License"] = value
            elif field == "active":
                row["Active"] = value
            elif field == "description":
                row["Description"] = value

    return row


def create_backup(file_path):
    """Create a backup of the file if it exists."""
    if not os.path.exists(file_path):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get the repository root (two levels up from scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    backup_dir = os.path.join(repo_root, ".myob", "backups")
    os.makedirs(backup_dir, exist_ok=True)

    backup_filename = f"{os.path.basename(file_path)}.{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)

    shutil.copy2(file_path, backup_path)
    return backup_path


def generate_readme_from_templates(csv_path, template_dir, output_path):
    """Generate README using template system."""
    from category_utils import category_manager

    # Create backup of existing README
    backup_path = create_backup(output_path)

    # Load template
    template_path = os.path.join(template_dir, "README.template.md")
    template = load_template(template_path)
    overrides = load_overrides(template_dir)
    announcements = load_announcements(template_dir)

    # Load CSV data
    csv_data = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Apply overrides
            row = apply_overrides(row, overrides)
            if row["Active"].upper() == "TRUE":
                csv_data.append(row)

    # Generate table of contents
    toc_content = generate_toc_from_categories()

    # Generate weekly section
    weekly_section = generate_weekly_section(csv_data)

    # Generate body sections
    body_sections = []
    categories = category_manager.get_categories_for_readme()
    for category in categories:
        section_content = generate_section_content(category, csv_data)
        body_sections.append(section_content)

    # Replace placeholders in template
    readme_content = template
    readme_content = readme_content.replace("{{ANNOUNCEMENTS}}", announcements)
    readme_content = readme_content.replace("{{WEEKLY_SECTION}}", weekly_section)
    readme_content = readme_content.replace("{{TABLE_OF_CONTENTS}}", toc_content)
    readme_content = readme_content.replace("{{BODY_SECTIONS}}", "\n<br>\n\n".join(body_sections))

    # Write output
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
    except Exception as e:
        if backup_path:
            print(f"❌ Error writing README: {e}")
            print(f"   Backup preserved at: {backup_path}")
        raise

    return len(csv_data), backup_path


def main():
    """Main entry point."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "THE_RESOURCES_TABLE.csv")
    template_dir = os.path.join(script_dir, "..", "templates")
    output_path = os.path.join(script_dir, "..", "README.md")

    print("=== Template-based README Generation ===")
    print("Generating README from templates and CSV...")

    try:
        resource_count, backup_path = generate_readme_from_templates(
            csv_path, template_dir, output_path
        )
        print(f"✅ README.md generated successfully at {os.path.abspath(output_path)}")
        print(f"📊 Generated README with {resource_count} active resources")
        if backup_path:
            print(f"📁 Backup saved at: {backup_path}")
    except Exception as e:
        print(f"❌ Error generating README: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
