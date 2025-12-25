#!/usr/bin/env python3
"""
Backfill script to populate the 'Repo Created' column with first commit dates from GitHub.
Run this once to populate existing resources.
"""

import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_links import get_github_commit_dates_from_url


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(script_dir), "THE_RESOURCES_TABLE.csv")

    # Read all rows
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"Found {len(rows)} resources to process")

    # Ensure 'Repo Created' column exists
    if "Repo Created" not in fieldnames:
        fieldnames = list(fieldnames) + ["Repo Created"]

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for i, row in enumerate(rows):
        display_name = row.get("Display Name", "") or ""
        primary_link = row.get("Primary Link", "") or ""
        current_repo_created = (row.get("Repo Created") or "").strip()

        # Skip if already has a value
        if current_repo_created:
            skipped_count += 1
            continue

        # Skip non-GitHub URLs
        if not primary_link or "github.com" not in primary_link:
            print(f"[{i+1}/{len(rows)}] Skipping non-GitHub: {display_name}")
            skipped_count += 1
            continue

        print(f"[{i+1}/{len(rows)}] Fetching dates for: {display_name}...", end=" ")

        try:
            first_commit_date, _ = get_github_commit_dates_from_url(primary_link)
            if first_commit_date:
                row["Repo Created"] = first_commit_date
                print(f"OK ({first_commit_date})")
                updated_count += 1
            else:
                print("No date found")
                row["Repo Created"] = ""
        except Exception as e:
            print(f"Error: {e}")
            row["Repo Created"] = ""
            error_count += 1

        # Rate limiting - be nice to GitHub API
        time.sleep(0.5)

    # Write back to CSV
    print(f"\nWriting updated CSV...")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nBackfill complete!")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors:  {error_count}")


if __name__ == "__main__":
    main()
