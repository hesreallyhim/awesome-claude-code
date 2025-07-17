#!/usr/bin/env python3
"""
Template-based README generator for the Awesome Claude Code repository.
Reads resource metadata from CSV and generates README using templates.
"""

import csv
import os
import shutil
import sys
from datetime import datetime

import yaml  # type: ignore[import-untyped]


def load_template(template_path):
    """Load a template file."""
    with open(template_path, encoding="utf-8") as f:
        return f.read()


def load_structure(structure_path):
    """Load the README structure configuration."""
    with open(structure_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_toc_from_structure(structure):
    """Generate table of contents based on structure configuration."""
    toc_config = structure.get("toc", {})
    sections = structure.get("sections", [])

    symbol = toc_config.get("symbol", "▪")
    subsymbol = toc_config.get("subsymbol", "▫")
    indent = toc_config.get("indent", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
    subindent = toc_config.get("subindent", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")

    toc_lines = []

    for section in sections:
        # Main section link
        section_title = section["title"]
        anchor = section_title.lower().replace(" ", "-").replace("&", "").replace("/", "").replace(".", "")

        toc_lines.append(f"{symbol}{indent}[{section_title}](#{anchor}-)  ")

        # Subsections
        subsections = section.get("subsections", [])
        for subsection in subsections:
            sub_title = subsection["title"]
            sub_anchor = sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")
            toc_lines.append(f"{subindent}{subsymbol}{indent}[{sub_title}](#{sub_anchor})  ")

    return "\n".join(toc_lines)


def format_resource_entry(row):
    """Format a single resource entry."""
    display_name = row["Display Name"]
    primary_link = row["Primary Link"]
    secondary_link = row.get("Secondary Link", "").strip()
    author_name = row.get("Author Name", "").strip()
    author_link = row.get("Author Link", "").strip()
    description = row.get("Description", "").strip()
    license_info = row.get("License", "").strip()

    # Build the entry
    entry_parts = [f"[`{display_name}`]({primary_link})"]

    # Add secondary link if present
    if secondary_link:
        entry_parts.append(f" ([link]({secondary_link}))")

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


def generate_section_content(section, csv_data):
    """Generate content for a section based on CSV data."""
    lines = []

    # Add section title
    title = section.get("title", "")
    icon = section.get("icon", "")
    if icon:
        lines.append(f"## {title} {icon}")
    else:
        lines.append(f"## {title}")

    # Add section description if present
    description = section.get("description", "").strip()
    if description:
        lines.append("")
        lines.append(description)

    # Get resources for this section
    category = section.get("category", "")
    subsections = section.get("subsections", [])

    if not subsections:
        # No subsections - render all resources for this category
        resources = [r for r in csv_data if r["Category"] == category and not r.get("Sub-Category", "").strip()]
        if resources:
            lines.append("")
            for resource in resources:
                lines.append(format_resource_entry(resource))
                lines.append("")
    else:
        # Has subsections - first render main category resources without subcategory
        main_resources = [r for r in csv_data if r["Category"] == category and not r.get("Sub-Category", "").strip()]
        if main_resources:
            lines.append("")
            for resource in main_resources:
                lines.append(format_resource_entry(resource))
                lines.append("")

        # Then render each subsection
        for subsection in subsections:
            sub_title = subsection["title"]
            sub_category = subsection["sub_category"]

            resources = [
                r for r in csv_data if r["Category"] == category and r.get("Sub-Category", "").strip() == sub_category
            ]

            if resources:
                lines.append("")
                lines.append(f"### {sub_title}")
                lines.append("")

                for resource in resources:
                    lines.append(format_resource_entry(resource))
                    lines.append("")

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
    # Create backup of existing README
    backup_path = create_backup(output_path)

    # Load template and structure
    template_path = os.path.join(template_dir, "README.template.md")
    structure_path = os.path.join(template_dir, "readme-structure.yaml")

    template = load_template(template_path)
    structure = load_structure(structure_path)
    overrides = load_overrides(template_dir)

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
    toc_content = generate_toc_from_structure(structure)

    # Generate body sections
    body_sections = []
    for section in structure.get("sections", []):
        if section.get("source") == "csv":
            section_content = generate_section_content(section, csv_data)
            body_sections.append(section_content)

    # Replace placeholders in template
    readme_content = template
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
        resource_count, backup_path = generate_readme_from_templates(csv_path, template_dir, output_path)
        print(f"✅ README.md generated successfully at {os.path.abspath(output_path)}")
        print(f"📊 Generated README with {resource_count} active resources")
        if backup_path:
            print(f"📁 Backup saved at: {backup_path}")
    except Exception as e:
        print(f"❌ Error generating README: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
