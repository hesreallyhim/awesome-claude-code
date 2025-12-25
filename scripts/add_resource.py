#!/usr/bin/env python3
"""Interactive script to add new resources to THE_RESOURCES_TABLE.csv"""

import csv
import os
import sys
from datetime import datetime

# Import validation function
try:
    from validate_single_resource import (
        validate_resource_from_dict,  # type: ignore[import-not-found]
    )
except ImportError:
    from .validate_single_resource import validate_resource_from_dict

# Import category manager
try:
    from category_utils import category_manager  # type: ignore[import-not-found]
except ImportError:
    from .category_utils import category_manager


def clear_screen():
    """Clear terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Print script header"""
    print("=" * 60)
    print("AWESOME CLAUDE CODE - Resource Submission Tool")
    print("=" * 60)
    print()
    print("IMPORTANT: Submit only ONE resource at a time.")
    print("Multiple resources require separate pull requests.")
    print()


def get_resource_type():
    """Display menu and get resource type selection"""
    # Get categories from the centralized configuration
    categories = category_manager.get_all_categories()

    # Filter out "Official Documentation" as it's not for user submissions
    categories = [cat for cat in categories if cat != "Official Documentation"]

    print("Select the type of resource:")
    print()
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")
    print()

    while True:
        try:
            choice = input(f"Enter your choice (1-{len(categories)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(categories)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_display_name(category):
    """Get display name based on category"""
    print()
    if category == "Slash-Commands":
        name = input("Enter the slash command name (e.g., /commit): ").strip()
        if not name.startswith("/"):
            name = "/" + name
        return name
    elif category == "CLAUDE.md Files":
        name = input("Enter the repository/project name: ").strip()
        return name
    elif category == "Tooling":
        name = input("Enter the tool name: ").strip()
        return name
    elif category == "Alternative Clients":
        name = input("Enter the client name: ").strip()
        return name
    elif category == "Workflows & Knowledge Guides":
        print("Enter a brief name for the workflow (max 50 characters):")
        name = input("> ").strip()[:50]
        return name
    elif category == "Hooks":
        print("Enter a brief name for the hook(s) (max 50 characters):")
        name = input("> ").strip()[:50]
        return name
    elif category == "Agent Skills":
        print("Enter a brief name for the skill (max 50 characters):")
        name = input("> ").strip()[:50]
        return name
    elif category == "Status Lines":
        print("Enter a brief name for the status line (max 50 characters):")
        name = input("> ").strip()[:50]
        return name
    elif category == "Output Styles":
        print("Enter a brief name for the output style (max 50 characters):")
        name = input("> ").strip()[:50]
        return name
    else:
        # Fallback for any other category
        print(f"Enter a name for the {category} resource:")
        name = input("> ").strip()[:50]
        return name


def get_subcategory(category):
    """Get subcategory if applicable"""
    # Get subcategories from the centralized configuration
    options = category_manager.get_subcategories_for_category(category)

    if not options:
        return "General"

    # If only "General" is available, return it directly
    if len(options) == 1 and options[0] == "General":
        return "General"

    print()
    print(f"Select a subcategory for {category}:")
    print()
    for i, subcat in enumerate(options, 1):
        print(f"  {i}. {subcat}")
    print()

    while True:
        try:
            choice = input(f"Enter your choice (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_url(prompt):
    """Get and validate URL input"""
    while True:
        url = input(prompt).strip()
        if url.startswith("https://"):
            return url
        else:
            print("Please enter a valid URL starting with https://")


def get_license():
    """Get license information"""
    print()
    print("Enter the license (optional but recommended):")
    print("Examples: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, AGPL-3.0")
    print("Press Enter to skip if unknown")
    license_input = input("> ").strip()
    return license_input if license_input else "NOT_FOUND"


def get_description():
    """Get resource description"""
    print()
    print("Enter a brief description (1-2 sentences maximum):")
    print("Tip: Focus on what the resource does and its key features")
    description = input("> ").strip()
    # Escape quotes for CSV
    return description.replace('"', '""')


def generate_id(display_name, primary_link, category):
    """Generate ID using shared resource_id module"""
    from resource_id import generate_resource_id

    return generate_resource_id(display_name, primary_link, category)


def confirm_submission(data):
    """Display summary and get confirmation"""
    print()
    print("=" * 60)
    print("SUBMISSION SUMMARY")
    print("=" * 60)
    print(f"ID: {data['id']}")
    print(f"Display Name: {data['display_name']}")
    print(f"Category: {data['category']}")
    if data["subcategory"]:
        print(f"Subcategory: {data['subcategory']}")
    print(f"Primary Link: {data['primary_link']}")
    if data["secondary_link"]:
        print(f"Secondary Link: {data['secondary_link']}")
    print(f"Author: {data['author_name']}")
    print(f"Author Link: {data['author_link']}")
    print(f"License: {data['license']}")
    print(f"Description: {data['description']}")
    print("=" * 60)
    print()

    while True:
        confirm = input("Submit this resource? (yes/no): ").strip().lower()
        if confirm in ["yes", "y"]:
            return True
        elif confirm in ["no", "n"]:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def append_to_csv(data):
    """Append the new resource to THE_RESOURCES_TABLE.csv"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(script_dir), "THE_RESOURCES_TABLE.csv")

    # Prepare row data (must match CSV column order)
    row = [
        data["id"],
        data["display_name"],
        data["category"],
        data["subcategory"],
        data["primary_link"],
        data["secondary_link"],
        data["author_name"],
        data["author_link"],
        data.get("active", "TRUE"),  # Active
        data.get("date_added", datetime.now().strftime("%Y-%m-%d:%H-%M-%S")),  # Date Added
        data.get("last_modified", ""),  # Last Modified
        data.get("last_checked", datetime.now().strftime("%Y-%m-%d:%H-%M-%S")),  # Last Checked
        data["license"],
        data["description"],
        data.get("removed_from_origin", "FALSE"),  # Removed From Origin
        data.get("stale", "FALSE"),  # Stale
        data.get("repo_created", ""),  # Repo Created (first commit date from GitHub)
        data.get("latest_release", ""),  # Latest Release date
        data.get("release_version", ""),  # Release Version (e.g., v1.2.3)
        data.get("release_source", ""),  # Release Source (npm, pypi, github-releases)
    ]

    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False


def generate_pr_content(data):
    """Generate PR template content"""
    is_github = "github.com" in data["primary_link"]

    content = f"""### Resource Information

- **Display Name**: {data["display_name"]}
- **Category**: {data["category"]}
- **Sub-Category**: {data["subcategory"] if data["subcategory"] else "N/A"}
- **Primary Link**: {data["primary_link"]}
- **Author Name**: {data["author_name"]}
- **Author Link**: {data["author_link"]}
- **License**: {data["license"] if data["license"] else "Not specified"}

### Description

{data["description"]}

### Automated Notification

- [{"x" if is_github else " "}] This is a GitHub-hosted resource and will receive an automatic
  notification issue when merged

### Checklist for New Resources

- [x] Used `make add-resource` or `python scripts/add_resource.py` to add the resource
- [ ] Ran `make generate` to update README.md
- [x] Verified link works and points to correct resource
- [x] Description is concise (1-2 sentences max)"""

    return content


def save_pr_content(content):
    """Save PR content to a file"""
    pr_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", ".pr_template_content.md"
    )
    try:
        with open(pr_file, "w", encoding="utf-8") as f:
            f.write(content)
        return pr_file
    except Exception as e:
        print(f"Warning: Could not save PR template content: {e}")
        return None


def main():
    """Main function"""
    clear_screen()
    print_header()

    # Collect information
    category = get_resource_type()
    display_name = get_display_name(category)
    subcategory = (
        get_subcategory(category)
        if category in ["Slash-Commands", "CLAUDE.md Files", "Tooling"]
        else "General"
    )

    print()
    primary_link = get_url("Enter the primary link to the resource: ")

    print()
    secondary_link_prompt = "Enter a secondary link (optional, press Enter to skip): "
    secondary_link = input(secondary_link_prompt).strip()
    if secondary_link and not secondary_link.startswith(("http://", "https://")):
        print("Invalid URL format. Skipping secondary link.")
        secondary_link = ""

    print()
    author_name = input("Enter the author's name or GitHub username: ").strip()

    print()
    author_link = get_url("Enter a link to the author (e.g., GitHub profile): ")

    license_info = get_license()
    description = get_description()

    # Generate ID
    resource_id = generate_id(display_name, primary_link, category)

    # Prepare data
    data = {
        "id": resource_id,
        "display_name": display_name,
        "category": category,
        "subcategory": subcategory,
        "primary_link": primary_link,
        "secondary_link": secondary_link,
        "author_name": author_name,
        "author_link": author_link,
        "license": license_info,
        "description": description,
    }

    # Validate the resource before confirmation
    print()
    print("Validating resource...")
    print("=" * 60)

    is_valid, validated_data, errors = validate_resource_from_dict(data)

    if not is_valid:
        print()
        print("✗ Validation failed!")
        print()
        print("The following issues were found:")
        for error in errors:
            print(f"  - {error}")
        print()
        print("Please fix these issues and try again.")
        sys.exit(1)

    # Update data with enriched information from validation
    data = validated_data

    print()
    print("✓ All validation checks passed!")
    print()

    # Confirm and submit
    if confirm_submission(data):
        if append_to_csv(data):
            print()
            print("✓ Resource successfully added to THE_RESOURCES_TABLE.csv!")

            # Generate and save PR content
            pr_content = generate_pr_content(data)
            pr_file = save_pr_content(pr_content)

            print()
            print("Next steps:")
            print("1. Run 'make generate' to update the README.md")
            if pr_file:
                print("2. Copy content from .pr_template_content.md into your PR description")
                print("3. Create a pull request with your changes")
            else:
                print("2. Create a pull request with your changes")
            print()
            print("Remember: If you have more resources to add, create separate PRs for each one.")
            print()

            if "github.com" in data["primary_link"]:
                print(
                    "Note: Once merged, an automated issue will be created on the GitHub repository"
                )
                print("      to notify them of their inclusion in Awesome Claude Code.")
                print()
        else:
            print()
            print("✗ Failed to add resource. Please check the error message above.")
            sys.exit(1)
    else:
        print()
        print("Submission cancelled.")


if __name__ == "__main__":
    main()
