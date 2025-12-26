#!/usr/bin/env python3
"""
Backfill script to populate Latest Release, Release Version, and Release Source
columns for existing resources in THE_RESOURCES_TABLE.csv.

This script fetches release information from:
- GitHub Releases API (with fallback to Tags)
- npm registry
- PyPI

Usage:
    python scripts/backfill_releases.py [--max N] [--dry-run]

Options:
    --max N      Process at most N resources (for testing)
    --dry-run    Don't write changes, just show what would be updated
"""

import argparse
import csv
import os
import sys
import time

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_links import get_latest_release_info


def backfill_releases(csv_path: str, max_resources: int | None = None, dry_run: bool = False):
    """Backfill release information for resources in the CSV."""

    # Read the CSV file
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not fieldnames:
        print("Error: Could not read CSV headers")
        return

    # Ensure new columns exist in fieldnames
    new_columns = ["Latest Release", "Release Version", "Release Source"]
    for col in new_columns:
        if col not in fieldnames:
            fieldnames.append(col)

    total = len(rows)
    processed = 0
    updated = 0
    skipped = 0
    errors = 0

    print(f"Processing {total} resources...")
    print()

    for i, row in enumerate(rows):
        if max_resources and processed >= max_resources:
            print(f"\nReached max limit ({max_resources}). Stopping.")
            break

        display_name = row.get("Display Name", "Unknown")
        primary_link = row.get("Primary Link", "") or ""
        active_val = row.get("Active", "") or ""
        active = active_val.upper() == "TRUE"

        # Skip inactive resources
        if not active:
            skipped += 1
            continue

        # Skip if already has release data
        if row.get("Latest Release"):
            print(f"[{i+1}/{total}] {display_name}: Already has release data, skipping")
            skipped += 1
            continue

        # Skip non-URL entries
        if not primary_link.startswith("http"):
            skipped += 1
            continue

        print(f"[{i+1}/{total}] {display_name}: Fetching release info...", end=" ")

        try:
            release_date, version, source = get_latest_release_info(primary_link, display_name)

            if release_date:
                row["Latest Release"] = release_date
                row["Release Version"] = version or ""
                row["Release Source"] = source or ""
                print(f"✓ {version} ({source}) - {release_date[:10]}")
                updated += 1
            else:
                print("No releases found")
                row["Latest Release"] = ""
                row["Release Version"] = ""
                row["Release Source"] = ""

        except Exception as e:
            print(f"Error: {e}")
            errors += 1

        processed += 1

        # Rate limiting - be nice to APIs
        time.sleep(0.5)

    # Write updated CSV
    if not dry_run:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n✓ CSV updated: {csv_path}")
    else:
        print("\n[DRY RUN] No changes written to CSV")

    # Summary
    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total resources: {total}")
    print(f"Processed: {processed}")
    print(f"Updated with release info: {updated}")
    print(f"Skipped (inactive/existing/non-URL): {skipped}")
    print(f"Errors: {errors}")


def main():
    parser = argparse.ArgumentParser(description="Backfill release information for resources")
    parser.add_argument("--max", type=int, help="Maximum number of resources to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()

    # Find CSV file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(script_dir), "THE_RESOURCES_TABLE.csv")

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    backfill_releases(csv_path, max_resources=args.max, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
