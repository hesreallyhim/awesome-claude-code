"""CSV append + PR body helpers for the new 12-column schema.

Schema (THE_RESOURCES_TABLE_NEW.csv):
  ID, Display Name, Category, Sub-Category, Link, Author Name, Author Link,
  Active, Date Added, Last Checked, Description, Stale
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "THE_RESOURCES_TABLE_NEW.csv"


def _value_map(data: dict[str, str], now: str) -> dict[str, str]:
    return {
        "ID": data.get("id", ""),
        "Display Name": data.get("display_name", ""),
        "Category": data.get("category", ""),
        "Sub-Category": data.get("subcategory", ""),
        "Link": data.get("link", ""),
        "Author Name": data.get("author_name", ""),
        "Author Link": data.get("author_link", ""),
        "Active": data.get("active", "TRUE"),
        "Date Added": data.get("date_added", now),
        "Last Checked": data.get("last_checked", now),
        "Description": data.get("description", ""),
        "Stale": data.get("stale", "FALSE"),
    }


def append_to_csv(data: dict[str, str], csv_path: Path | None = None) -> bool:
    """Append one resource row, honoring the existing header order."""
    path = csv_path or CSV_PATH
    try:
        with path.open(encoding="utf-8", newline="") as f:
            headers = next(csv.reader(f), None)
    except OSError as e:
        print(f"Error reading CSV header: {e}")
        return False
    if not headers:
        print("Error reading CSV header: missing header row")
        return False

    now = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")
    value_map = _value_map(data, now)
    missing = [key for key in value_map if key not in headers]
    if missing:
        print(f"Error: CSV header missing columns {', '.join(missing)}")
        return False

    row = {header: value_map.get(header, "") for header in headers}
    try:
        with path.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=headers).writerow(row)
        return True
    except OSError as e:
        print(f"Error writing to CSV: {e}")
        return False


def generate_pr_content(data: dict[str, str]) -> str:
    """Render the PR body for an approved submission."""
    subcategory = data.get("subcategory") or "N/A"
    author = data.get("author_name", "")
    author_link = data.get("author_link", "")
    author_md = f"[{author}]({author_link})" if author_link else author
    return f"""### Resource Information

- **Display Name**: {data.get("display_name", "")}
- **Category**: {data.get("category", "")}
- **Sub-Category**: {subcategory}
- **Link**: {data.get("link", "")}
- **Author**: {author_md}

### Description

{data.get("description", "")}
"""
