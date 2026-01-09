#!/usr/bin/env python3
"""
Single resource validation script for the Awesome Claude Code repository.
Validates a single resource before adding it to the CSV.

This script is used by the issue submission validator and manual validation
workflows to validate resources before they are committed to the CSV file.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
sys.path.insert(0, str(REPO_ROOT))

from scripts.validation.validate_links import validate_url


def validate_single_resource(
    *,
    primary_link: str,
    secondary_link: str = "",
    display_name: str = "",
    category: str = "",
    license: str = "NOT_FOUND",
    **kwargs: Any,
) -> tuple[bool, dict[str, Any], list[str]]:
    """
    Validate a single resource before adding to CSV.

    Args:
        primary_link: Required URL to validate
        secondary_link: Optional secondary URL
        display_name: Name of the resource
        category: Resource category
        license: License information (defaults to "NOT_FOUND")
        **kwargs: Additional fields that may be present in the resource

    Returns:
        Tuple of (is_valid, enriched_data, errors):
            - is_valid: Boolean indicating if resource passes validation
            - enriched_data: Original data enriched with license and last_modified info
            - errors: List of validation error messages
    """
    errors = []
    enriched_data = {
        "primary_link": primary_link,
        "secondary_link": secondary_link,
        "display_name": display_name,
        "category": category,
        "license": license,
        **kwargs,
    }

    # Validate primary link
    primary_url = primary_link.strip()
    if not primary_url:
        errors.append("Primary link is required")
        return False, enriched_data, errors

    print(f"Validating primary URL: {primary_url}")
    primary_valid, primary_status, license_info, last_modified = validate_url(primary_url)

    if not primary_valid:
        errors.append(f"Primary URL validation failed: {primary_status}")
    else:
        print("✓ Primary URL is valid")

        # Enrich with GitHub data if available
        if license_info and license_info != "NOT_FOUND":
            enriched_data["license"] = license_info
            print(f"✓ Found license: {license_info}")

        if last_modified:
            enriched_data["last_modified"] = last_modified
            print(f"✓ Found last modified date: {last_modified}")

    # Validate secondary link if present
    secondary_url = secondary_link.strip()
    if secondary_url:
        print(f"Validating secondary URL: {secondary_url}")
        secondary_valid, secondary_status, _, _ = validate_url(secondary_url)

        if not secondary_valid:
            errors.append(f"Secondary URL validation failed: {secondary_status}")
        else:
            print("✓ Secondary URL is valid")

    # Set active status
    is_valid = len(errors) == 0
    enriched_data["active"] = "TRUE" if is_valid else "FALSE"
    enriched_data["last_checked"] = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")

    return is_valid, enriched_data, errors


def validate_resource_from_dict(
    resource_dict: dict[str, str],
) -> tuple[bool, dict[str, Any], list[str]]:
    """
    Convenience function for validating a resource dictionary.
    Maps common field names to expected format.
    """
    # Extract known fields and pass the rest as kwargs
    is_valid, enriched_data, errors = validate_single_resource(
        primary_link=resource_dict.get("primary_link", ""),
        secondary_link=resource_dict.get("secondary_link", ""),
        display_name=resource_dict.get("display_name", ""),
        category=resource_dict.get("category", ""),
        license=resource_dict.get("license", "NOT_FOUND"),
        **{
            k: v
            for k, v in resource_dict.items()
            if k not in ["primary_link", "secondary_link", "display_name", "category", "license"]
        },
    )

    # Map enriched data back to original field names
    if "license" in enriched_data and enriched_data["license"] != "NOT_FOUND":
        resource_dict["license"] = enriched_data["license"]
    if "last_modified" in enriched_data:
        resource_dict["last_modified"] = enriched_data["last_modified"]
    if "last_checked" in enriched_data:
        resource_dict["last_checked"] = enriched_data["last_checked"]

    return is_valid, resource_dict, errors


def main():
    """
    Command-line interface for testing single resource validation.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Validate a single resource")
    parser.add_argument("url", help="Primary URL to validate")
    parser.add_argument("--secondary", help="Secondary URL to validate")
    parser.add_argument("--name", default="Test Resource", help="Resource name")
    args = parser.parse_args()

    print(f"\nValidating resource: {args.name}")
    print("=" * 50)

    is_valid, enriched_data, errors = validate_single_resource(
        primary_link=args.url,
        secondary_link=args.secondary or "",
        display_name=args.name,
        category="Test",
    )

    print("\nValidation Results:")
    print("=" * 50)
    print(f"Valid: {'✓ Yes' if is_valid else '✗ No'}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    print("\nEnriched Data:")
    for key, value in enriched_data.items():
        if value and key not in ["primary_link", "secondary_link", "display_name", "category"]:
            print(f"  {key}: {value}")

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
