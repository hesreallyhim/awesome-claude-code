#!/usr/bin/env python3
"""Helpers for resource CSV updates and PR content generation."""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))

__all__ = ["append_to_csv", "generate_pr_content"]


def append_to_csv(data: dict[str, str]) -> bool:
    """Append the new resource to THE_RESOURCES_TABLE.csv using header order."""
    csv_path = os.path.join(REPO_ROOT, "THE_RESOURCES_TABLE.csv")

    try:
        with open(csv_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
    except Exception as e:
        print(f"Error reading CSV header: {e}")
        return False

    if not headers:
        print("Error reading CSV header: missing header row")
        return False

    now = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")
    value_map = {
        "ID": data.get("id", ""),
        "Display Name": data.get("display_name", ""),
        "Category": data.get("category", ""),
        "Sub-Category": data.get("subcategory", ""),
        "Primary Link": data.get("primary_link", ""),
        "Secondary Link": data.get("secondary_link", ""),
        "Author Name": data.get("author_name", ""),
        "Author Link": data.get("author_link", ""),
        "Active": data.get("active", "TRUE"),
        "Date Added": data.get("date_added", now),
        "Last Modified": data.get("last_modified", ""),
        "Last Checked": data.get("last_checked", now),
        "License": data.get("license", ""),
        "Description": data.get("description", ""),
        "Removed From Origin": data.get("removed_from_origin", "FALSE"),
        "Stale": data.get("stale", "FALSE"),
        "Repo Created": data.get("repo_created", ""),
        "Latest Release": data.get("latest_release", ""),
        "Release Version": data.get("release_version", ""),
        "Release Source": data.get("release_source", ""),
    }

    missing_headers = [key for key in value_map if key not in headers]
    if missing_headers:
        print(f"Error reading CSV header: missing columns {', '.join(missing_headers)}")
        return False

    row = {header: value_map.get(header, "") for header in headers}

    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False


def generate_pr_content(data: dict[str, str]) -> str:
    """Generate PR template content."""
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
  notification issue when merged"""

    return content
