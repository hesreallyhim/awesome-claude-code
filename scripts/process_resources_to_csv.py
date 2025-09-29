"""Process awesome-claude-code resources into CSV format.

This script parses the awesome-claude-code README.md file and extracts
all curated resources (workflows, tooling, slash-commands, CLAUDE.md files,
and official documentation) into a structured CSV file. The CSV includes
metadata such as display names, categories, primary links, and author
information for each resource.

Resources are sorted alphabetically within each category and sub-category
to maintain a consistent ordering in the CSV output.

The script is designed to maintain the THE_RESOURCES_TABLE.csv file which
can be used for further analysis, validation, or tracking of the curated
resources in the awesome-claude-code repository.
"""

import csv
import re


def extract_resources_from_readme(readme_path="./README.md", limit=10):
    """Extract resource information from README.md.

    This function parses the awesome-claude-code README.md file to extract
    all listed resources including their display names, categories, URLs,
    and author information. Resources are identified by markdown links
    starting with backticks (e.g., [`Resource Name`](url)).

    Args:
        readme_path: Path to the README.md file (default: '../README.md')
        limit: Maximum number of resources to extract (default: 10)

    Returns:
        List of dictionaries containing resource metadata
    """
    resources = []

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    current_category = None
    current_subcategory = None
    resource_count = 0
    i = 0
    # Skip sub-headers that are not resource categories
    skip_sub_headers = ["Contents", "Table of Contents", "Contributing"]

    while i < len(lines) and resource_count < limit:
        line = lines[i]

        # Track main category headers (## )
        if line.startswith("## ") and not any(skip in line for skip in skip_sub_headers):
            current_category = line.replace("## ", "").strip()
            current_subcategory = None
            i += 1
            continue

        # Track subcategory headers (### )
        if line.startswith("### "):
            current_subcategory = line.replace("### ", "").strip()
            i += 1
            continue

        # Look for resource entries that start with [`
        if line.startswith("[`") and current_category:
            # Parse entries like:
            # [`Name`](url) by [Author](author_url)
            # Description on next line

            # Extract name and primary link
            name_match = re.match(r"\[`([^`]+)`\]\(([^)]+)\)", line)
            if name_match:
                display_name = name_match.group(1)
                primary_link = name_match.group(2)

                # Extract author info from the same line
                author_name = ""
                author_link = ""

                # Look for "by [Author](link)" pattern
                author_match = re.search(r"by \[([^\]]+)\]\(([^)]+)\)", line)
                if author_match:
                    author_name = author_match.group(1)
                    author_link = author_match.group(2)

                # Determine type
                if current_subcategory:
                    resource_type = f"{current_category} - {current_subcategory}"
                else:
                    resource_type = current_category

                resources.append(
                    {
                        "Display Name": display_name,
                        "Type": resource_type,
                        "Primary Link": primary_link,
                        "Secondary Link": "",
                        "Author Name": author_name,
                        "Author Link": author_link,
                        "Active": "",
                        "Last Checked": "",
                    }
                )

                resource_count += 1

        i += 1

    return resources


def append_to_csv(resources, csv_path="THE_RESOURCES_TABLE.csv"):
    """Append resources to the CSV file"""
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Display Name",
                "Type",
                "Primary Link",
                "Secondary Link",
                "Author Name",
                "Author Link",
                "Active",
                "Last Checked",
            ],
        )

        for resource in resources:
            writer.writerow(resource)


def sort_resources_by_category(resources):
    """Sort resources alphabetically within each category and sub-category.

    Args:
        resources: List of resource dictionaries

    Returns:
        List of resources sorted by Type, then by Display Name
    """
    # Sort by Type (category) first, then by Display Name
    return sorted(resources, key=lambda x: (x["Type"], x["Display Name"].lower()))


if __name__ == "__main__":
    # Extract all resources (no limit)
    resources = extract_resources_from_readme(limit=1000)  # High limit to get all

    # Sort resources alphabetically within categories
    resources = sort_resources_by_category(resources)

    # Display summary
    print(f"Found {len(resources)} resources to add\n")

    # Show category breakdown
    categories: dict[str, int] = {}
    for resource in resources:
        cat = resource["Type"]
        categories[cat] = categories.get(cat, 0) + 1

    print("Category breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # Clear existing entries (except header) and add all resources
    csv_path = "THE_RESOURCES_TABLE.csv"

    # Check if file exists
    import os

    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            header = f.readline()
    else:
        # Create header if file doesn't exist
        header = (
            "Display Name,Type,Primary Link,Secondary Link,"
            "Author Name,Author Link,Active,Last Checked\n"
        )

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(header)

    # Add to CSV
    append_to_csv(resources, csv_path)
    print(
        f"\nAdded {len(resources)} resources to {csv_path} "
        "(sorted alphabetically within categories)"
    )
