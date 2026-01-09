#!/usr/bin/env python3
"""
Parse GitHub Issue form data from resource submissions.
Validates the data and returns structured JSON.
"""

import json
import os
import re
import sys
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
sys.path.insert(0, str(REPO_ROOT))

from scripts.categories.category_utils import category_manager
from scripts.validation.validate_single_resource import validate_single_resource


def parse_issue_body(issue_body: str) -> dict[str, str]:
    """
    Parse GitHub issue form body into structured data.

    GitHub issue forms are rendered as markdown with specific patterns:
    - Headers (###) indicate field labels
    - Values follow the headers
    - Checkboxes are rendered as - [x] or - [ ]
    """
    data = {}

    # Split into sections by ### headers
    sections = re.split(r"###\s+", issue_body)

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split("\n")
        if not lines:
            continue

        # First line is the field label
        label = lines[0].strip()

        # Rest is the value (skip empty lines)
        value_lines = [
            line
            for line in lines[1:]
            if line.strip() and not line.strip().startswith("_No response_")
        ]
        value = "\n".join(value_lines).strip()

        # Map form labels to data fields
        if "Display Name" in label:
            data["display_name"] = value
            data["_original_display_name"] = value  # Track original for warning
        elif "Category" in label and "Sub-Category" not in label:
            data["category"] = value
            # If this is a slash command, we'll validate/fix the display name later
        elif "Sub-Category" in label:
            # Set to "General" as default if empty or "None / Not Applicable"
            if not value or "None" in value or "Not Applicable" in value:
                data["subcategory"] = "General"
            else:
                # Strip the category prefix if present
                # (e.g., "Slash-Commands: " from "Slash-Commands: Context Loading & Priming")
                if ":" in value:
                    data["subcategory"] = value.split(":", 1)[1].strip()
                else:
                    data["subcategory"] = value
        elif "Primary Link" in label:
            data["primary_link"] = value
        elif "Secondary Link" in label:
            data["secondary_link"] = value
        elif "Author Name" in label:
            data["author_name"] = value
        elif "Author Link" in label:
            data["author_link"] = value
        elif "License" in label and "Other License" not in label:
            data["license"] = value
        elif "Other License" in label:
            if value:
                data["license"] = value  # Override with custom license
        elif "Description" in label:
            data["description"] = value

    # Fix slash command display names
    if data.get("category") == "Slash-Commands" and data.get("display_name"):
        display_name = data["display_name"]

        # Ensure it starts with a slash
        if not display_name.startswith("/"):
            display_name = "/" + display_name

        # Ensure it's a single string (no spaces, only hyphens, underscores, colons allowed)
        # Replace spaces with hyphens
        display_name = display_name.replace(" ", "-")

        # Remove any characters that aren't alphanumeric, slash, hyphen, underscore, or colon
        display_name = re.sub(r"[^a-zA-Z0-9/_:-]", "", display_name)

        # Ensure it's lowercase (convention for slash commands)
        display_name = display_name.lower()

        # Ensure only one leading slash - remove any extra slashes at the beginning
        while display_name.startswith("//"):
            display_name = display_name[1:]

        data["display_name"] = display_name

    return data


def validate_parsed_data(data: dict[str, str]) -> tuple[bool, list[str], list[str]]:
    """
    Validate the parsed data meets all requirements.
    Returns (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Check required fields
    required_fields = [
        "display_name",
        "category",
        "primary_link",
        "author_name",
        "author_link",
        "description",
    ]

    for field in required_fields:
        if not data.get(field, "").strip():
            errors.append(f"Required field '{field}' is missing or empty")

    # Validate category
    valid_categories = category_manager.get_all_categories()
    if data.get("category") not in valid_categories:
        errors.append(
            f"Invalid category: {data.get('category')}. "
            f"Must be one of: {', '.join(valid_categories)}"
        )

    # Sub-category validation is no longer needed since we strip the prefix
    # The form already ensures subcategories match their parent categories

    # Check if slash command display name was modified
    if (
        data.get("category") == "Slash-Commands"
        and "_original_display_name" in data
        and data["display_name"] != data["_original_display_name"]
    ):
        warnings.append(
            f"Display name was automatically corrected from "
            f"'{data['_original_display_name']}' to '{data['display_name']}'. "
            "Slash commands must start with '/' and contain no spaces."
        )

    # Additional validation for slash commands - check for multiple slashes
    if data.get("category") == "Slash-Commands" and data.get("display_name"):
        display_name = data["display_name"]
        # Check if there are multiple slashes anywhere in the command
        slash_count = display_name.count("/")
        if slash_count > 1:
            errors.append(
                f"Slash command '{display_name}' contains multiple slashes. "
                "Slash commands must have exactly one slash at the beginning."
            )

    # Validate URLs
    url_fields = ["primary_link", "secondary_link", "author_link"]
    for field in url_fields:
        value = data.get(field, "").strip()
        if value and field != "secondary_link":  # secondary is optional
            if not value.startswith("https://"):
                errors.append(f"{field} must start with https://")
            elif " " in value:
                errors.append(f"{field} contains spaces")

    # Validate license
    if data.get("license") == "No License / Not Specified":
        data["license"] = "NOT_FOUND"
        warnings.append("No license specified - consider adding one for open source projects")

    # Check description length
    description = data.get("description", "")
    if len(description) > 500:
        errors.append("Description is too long (max 500 characters)")
    elif len(description) < 10:
        errors.append("Description is too short (min 10 characters)")

    # Check for common issues
    if data.get("display_name", "").lower() in ["test", "testing", "example"]:
        warnings.append("Display name appears to be a test entry")

    return len(errors) == 0, errors, warnings


def check_for_duplicates(data: dict[str, str]) -> list[str]:
    """Check if resource already exists in the CSV."""
    warnings: list[str] = []

    csv_path = os.path.join(REPO_ROOT, "THE_RESOURCES_TABLE.csv")
    if not os.path.exists(csv_path):
        return warnings

    import csv

    primary_link = data.get("primary_link", "").lower()
    display_name = data.get("display_name", "").lower()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for duplicate URL
            if row.get("Primary Link", "").lower() == primary_link:
                warnings.append(
                    f"A resource with this primary link already exists: {row.get('Display Name')}"
                )
            # Check for similar names
            elif row.get("Display Name", "").lower() == display_name:
                warnings.append(
                    f"A resource with the same name already exists: {row.get('Display Name')}"
                )

    return warnings


def main():
    """Main entry point for the script."""
    # Get issue body from environment variable
    issue_body = os.environ.get("ISSUE_BODY", "")
    if not issue_body:
        print(json.dumps({"valid": False, "errors": ["No issue body provided"], "data": {}}))
        return 1

    # Parse the issue body
    parsed_data = parse_issue_body(issue_body)

    # Check if --validate flag is passed
    validate_mode = "--validate" in sys.argv

    if validate_mode:
        # Full validation mode
        is_valid, errors, warnings = validate_parsed_data(parsed_data)

        # Check for duplicates
        duplicate_warnings = check_for_duplicates(parsed_data)
        warnings.extend(duplicate_warnings)

        # If basic validation passed, do URL validation
        if is_valid and parsed_data.get("primary_link"):
            url_valid, enriched_data, url_errors = validate_single_resource(
                primary_link=parsed_data.get("primary_link", ""),
                secondary_link=parsed_data.get("secondary_link", ""),
                display_name=parsed_data.get("display_name", ""),
                category=parsed_data.get("category", ""),
                license=parsed_data.get("license", "NOT_FOUND"),
                subcategory=parsed_data.get("subcategory", ""),
                author_name=parsed_data.get("author_name", ""),
                author_link=parsed_data.get("author_link", ""),
                description=parsed_data.get("description", ""),
            )

            if not url_valid:
                is_valid = False
                errors.extend(url_errors)
            else:
                # Update with enriched data (license from GitHub, etc.)
                parsed_data.update(enriched_data)

        # Remove temporary tracking field
        if "_original_display_name" in parsed_data:
            del parsed_data["_original_display_name"]

        result = {"valid": is_valid, "errors": errors, "warnings": warnings, "data": parsed_data}
    else:
        # Simple parse mode - just return the parsed data
        # Remove temporary tracking field
        if "_original_display_name" in parsed_data:
            del parsed_data["_original_display_name"]
        result = parsed_data

    # Print compact JSON (no newlines) to make it easier to extract
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
