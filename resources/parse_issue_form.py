#!/usr/bin/env python3
"""Parse + validate a resource-recommendation issue form.

Reads the issue body from ISSUE_BODY. With --validate, returns
{valid, errors, warnings, data} as compact JSON; otherwise just the parsed data.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

from resources.categories import category_names

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "THE_RESOURCES_TABLE_NEW.csv"

REQUIRED_FIELDS = ["display_name", "category", "link", "author_name", "author_link", "description"]
NONE_VALUES = ("none", "not applicable", "n/a")


def parse_issue_body(issue_body: str) -> dict[str, str]:
    """Parse a GitHub issue-form body (### Label\\nvalue) into fields."""
    data: dict[str, str] = {}
    for section in re.split(r"###\s+", issue_body):
        if not section.strip():
            continue
        lines = section.strip().split("\n")
        label = lines[0].strip()
        value_lines = [
            ln for ln in lines[1:] if ln.strip() and not ln.strip().startswith("_No response_")
        ]
        value = "\n".join(value_lines).strip()

        # Order matters: more specific labels first.
        if "Display Name" in label:
            data["display_name"] = value
        elif "Sub-Category" in label or "Sub-category" in label:
            data["subcategory"] = "" if (not value or value.lower() in NONE_VALUES) else value
        elif "Category" in label:
            data["category"] = value
        elif "Author Name" in label:
            data["author_name"] = value
        elif "Author Link" in label:
            data["author_link"] = value
        elif "Link" in label:  # plain Link, after Author Link
            data["link"] = value
        elif "Description" in label:
            data["description"] = value
    return data


def check_for_duplicates(data: dict[str, str]) -> list[str]:
    """Warn if the Link or Display Name already exists in the CSV."""
    warnings: list[str] = []
    if not CSV_PATH.exists():
        return warnings
    link = data.get("link", "").strip().lower()
    name = data.get("display_name", "").strip().lower()
    with CSV_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if link and row.get("Link", "").strip().lower() == link:
                warnings.append(f"A resource with this link already exists: {row.get('Display Name')}")
            elif name and row.get("Display Name", "").strip().lower() == name:
                warnings.append(f"A resource with the same name already exists: {row.get('Display Name')}")
    return warnings


def validate_parsed_data(data: dict[str, str]) -> tuple[bool, list[str], list[str]]:
    """Return (is_valid, errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        if not data.get(field, "").strip():
            errors.append(f"Required field '{field}' is missing or empty")

    valid_categories = category_names()
    if data.get("category") and data["category"] not in valid_categories:
        errors.append(
            f"Invalid category: {data.get('category')}. Must be one of: {', '.join(valid_categories)}"
        )

    for field in ("link", "author_link"):
        value = data.get(field, "").strip()
        if value and not value.startswith("https://"):
            errors.append(f"{field} must start with https://")
        # A submitted URL should never contain whitespace or HTML/markdown
        # metacharacters; these are what let a crafted Link break out of the
        # rendered <img src="..."> badge or the [text](link) markdown target.
        if value and re.search(r"""[\s"'<>`\\)]""", value):
            errors.append(f"{field} contains forbidden characters")

    description = data.get("description", "")
    if len(description) > 500:
        errors.append("Description is too long (max 500 characters)")
    elif 0 < len(description) < 10:
        errors.append("Description is too short (min 10 characters)")

    if data.get("display_name", "").strip().lower() in ("test", "testing", "example"):
        warnings.append("Display name appears to be a test entry")

    return len(errors) == 0, errors, warnings


def main() -> int:
    issue_body = os.environ.get("ISSUE_BODY", "")
    if not issue_body:
        print(json.dumps({"valid": False, "errors": ["No issue body provided"], "data": {}}))
        return 1

    data = parse_issue_body(issue_body)

    if "--validate" in sys.argv:
        is_valid, errors, warnings = validate_parsed_data(data)
        warnings.extend(check_for_duplicates(data))
        result = {"valid": is_valid, "errors": errors, "warnings": warnings, "data": data}
    else:
        result = data

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
