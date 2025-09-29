#!/usr/bin/env python3
"""
Validate new resource additions for pre-push hook.

This script checks that exactly one line has been added to THE_RESOURCES_TABLE.csv
when comparing the current branch to upstream/main, then validates that resource.
"""

import csv
import io
import os
import subprocess
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import validation functions from validate_links
try:
    from validate_links import (  # type: ignore[import-not-found]
        ACTIVE_HEADER_NAME,
        ID_HEADER_NAME,
        LAST_CHECKED_HEADER_NAME,
        LAST_MODIFIED_HEADER_NAME,
        LICENSE_HEADER_NAME,
        PRIMARY_LINK_HEADER_NAME,
        SECONDARY_LINK_HEADER_NAME,
        apply_overrides,
        load_overrides,
        validate_url,
    )
except ImportError:
    print("Error: Could not import from validate_links.py")
    sys.exit(1)

CSV_FILE = "THE_RESOURCES_TABLE.csv"
UPSTREAM_REMOTE = os.environ.get("AWESOME_CC_UPSTREAM_REMOTE", "upstream")


def run_git_command(cmd: list[str]) -> tuple[bool, str]:
    """Run a git command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)


def get_csv_headers() -> list[str] | None:
    """Get CSV headers from the current file."""
    if not os.path.exists(CSV_FILE):
        return None

    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            return next(reader)
        except StopIteration:
            return None


def parse_csv_line(line: str, headers: list[str]) -> dict[str, str] | None:
    """Parse a CSV line into a dictionary using the provided headers."""
    try:
        # Use csv.reader to properly handle quoted fields
        reader = csv.reader(io.StringIO(line))
        values = next(reader)

        if len(values) != len(headers):
            return None

        return dict(zip(headers, values, strict=False))
    except Exception:
        return None


def check_upstream_remote() -> bool:
    """Check if upstream remote exists."""
    success, output = run_git_command(["git", "remote", "get-url", UPSTREAM_REMOTE])
    if not success:
        print(f"Error: Upstream remote '{UPSTREAM_REMOTE}' not found")
        print("Please add the upstream remote:")
        print(
            f"  git remote add {UPSTREAM_REMOTE} https://github.com/hesreallyhim/awesome-claude-code.git"
        )
        return False
    return True


def get_csv_diff_stats() -> tuple[int, list[str]]:
    """Get the number of lines added to CSV when comparing to upstream/main."""
    # Get diff between current branch and upstream/main
    success, diff_output = run_git_command(
        ["git", "diff", f"{UPSTREAM_REMOTE}/main", "--", CSV_FILE]
    )

    if not success:
        print(f"Error: Could not get diff against {UPSTREAM_REMOTE}/main")
        print("Make sure you have fetched the latest upstream changes:")
        print(f"  git fetch {UPSTREAM_REMOTE}")
        return -1, []

    # Count added lines (lines starting with +, excluding the header)
    added_lines = []
    for line in diff_output.splitlines():
        if (
            line.startswith("+")
            and not line.startswith("+++")
            and not line[1:].startswith("ID,Display Name,")
        ):
            added_lines.append(line[1:])  # Remove the + prefix

    return len(added_lines), added_lines


def parse_resource_from_line(csv_line: str, headers: list[str]) -> dict[str, str] | None:
    """Parse a single CSV line into a resource dictionary."""
    return parse_csv_line(csv_line, headers)


def validate_and_update_resource(resource: dict[str, str]) -> bool:
    """Validate the resource and update the CSV file."""
    print(f"\nValidating resource: {resource.get('Display Name', 'Unknown')}")
    print(f"ID: {resource.get(ID_HEADER_NAME, 'Unknown')}")
    print(f"Primary URL: {resource.get(PRIMARY_LINK_HEADER_NAME, 'None')}")

    # Load overrides
    overrides = load_overrides()

    # Apply overrides
    resource, locked_fields, skip_validation = apply_overrides(resource, overrides)

    if locked_fields:
        print(f"Fields locked by override: {', '.join(locked_fields)}")

    # Skip validation if active and last_checked are locked
    if "active" in locked_fields and "last_checked" in locked_fields:
        print("Skipping validation - fields locked by override")
        return True

    # Skip validation if marked
    if skip_validation:
        print("Skipping validation - resource marked as skip_validation")
        return True

    # Validate primary URL
    primary_url = resource.get(PRIMARY_LINK_HEADER_NAME, "").strip()
    primary_valid, primary_status, license_info, last_modified = validate_url(primary_url)

    # Update fields based on validation
    if "license" not in locked_fields and license_info and license_info != "NOT_FOUND":
        resource[LICENSE_HEADER_NAME] = license_info
        print(f"✓ Found license: {license_info}")

    if "last_modified" not in locked_fields and last_modified:
        resource[LAST_MODIFIED_HEADER_NAME] = last_modified
        print(f"✓ Found last modified: {last_modified}")

    # Validate secondary URL if present
    secondary_url = resource.get(SECONDARY_LINK_HEADER_NAME, "").strip()
    secondary_valid = True
    if secondary_url:
        secondary_valid, secondary_status, _, _ = validate_url(secondary_url)
        if not secondary_valid:
            print(f"✗ Secondary URL validation failed: {secondary_status}")

    # Update active status
    if "active" not in locked_fields:
        is_active = primary_valid and secondary_valid
        resource[ACTIVE_HEADER_NAME] = "TRUE" if is_active else "FALSE"

        if is_active:
            print("✓ Resource is valid and active")
        else:
            print(f"✗ Resource validation failed: {primary_status}")

    # Update last checked timestamp
    if "last_checked" not in locked_fields:
        resource[LAST_CHECKED_HEADER_NAME] = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")

    # Update the CSV file
    return update_csv_file(resource)


def update_csv_file(updated_resource: dict[str, str]) -> bool:
    """Update the CSV file with the validated resource data."""
    try:
        # Read all rows
        with open(CSV_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        if not fieldnames:
            print("Error: Could not read CSV fieldnames")
            return False

        # Find and update the matching row
        resource_id = updated_resource.get(ID_HEADER_NAME)
        updated = False

        for i, row in enumerate(rows):
            if row.get(ID_HEADER_NAME) == resource_id:
                # Update the row with validated data
                rows[i].update(updated_resource)
                updated = True
                break

        if not updated:
            print(f"Warning: Could not find resource with ID {resource_id} in CSV")
            return False

        # Write back to CSV
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✓ Updated {CSV_FILE} successfully")
        return True

    except Exception as e:
        print(f"Error updating CSV file: {e}")
        return False


def main():
    """Main entry point for pre-push validation."""
    # Check if we're in a git repository
    success, _ = run_git_command(["git", "rev-parse", "--git-dir"])
    if not success:
        print("Error: Not in a git repository")
        sys.exit(1)

    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found")
        sys.exit(1)

    # Check upstream remote exists
    if not check_upstream_remote():
        sys.exit(1)

    # Get CSV headers
    headers = get_csv_headers()
    if not headers:
        print("Error: Could not read CSV headers")
        sys.exit(1)

    # Get diff stats
    num_added, added_lines = get_csv_diff_stats()

    if num_added == -1:
        # Error already printed in get_csv_diff_stats
        sys.exit(1)

    # NOTE: This causes problems if the user pushes more than once.
    # if num_added == 0:
    #     print("\n❌ No new resources found in THE_RESOURCES_TABLE.csv")
    #     print("\n📖 Please review CONTRIBUTING.md for guidance on adding resources.")
    #     print("   The recommended approach is to use: make submit")
    #     sys.exit(1)

    if num_added > 1:
        print(f"\n❌ Found {num_added} lines added to THE_RESOURCES_TABLE.csv")
        print("\n⚠️  Only one resource is permitted per pull request.")
        print("\nPlease ensure:")
        print(f"1. You are up to date with {UPSTREAM_REMOTE}/main:")
        print(f"   git fetch {UPSTREAM_REMOTE}")
        print(f"   git rebase {UPSTREAM_REMOTE}/main")
        print("\n2. If you still have multiple additions after rebasing,")
        print("   please create separate PRs for each resource.")
        sys.exit(1)

    # Exactly one line added - parse and validate it
    print("✓ Found 1 new resource to validate")

    resource = parse_resource_from_line(added_lines[0], headers)
    if not resource:
        print("Error: Could not parse the added resource line")
        sys.exit(1)

    # Validate and update the resource
    success = validate_and_update_resource(resource)

    if success:
        print("\n✅ Resource validation successful!")
        print("   You can now push your changes.")
    else:
        print("\n❌ Resource validation failed.")
        print("   Please fix the issues before pushing.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
