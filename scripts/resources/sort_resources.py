#!/usr/bin/env python3
"""
Sort THE_RESOURCES_TABLE.csv by category, sub-category, and display name.

This utility ensures resources are properly ordered for consistent presentation
in the generated README and other outputs.
"""

import csv
import sys
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
sys.path.insert(0, str(REPO_ROOT))


def sort_resources(csv_path: Path) -> None:
    """Sort resources in the CSV file by category, sub-category,
    and display name."""
    # Load category order from category_utils
    from scripts.categories.category_utils import category_manager

    category_order = []
    categories = []
    try:
        categories = category_manager.get_categories_for_readme()
        category_order = [cat["name"] for cat in categories]
    except Exception as e:
        print(f"Warning: Could not load category order from category_utils: {e}")
        print("Using alphabetical sorting instead.")

    # Create a mapping for sort order
    category_sort_map = {cat: idx for idx, cat in enumerate(category_order)}

    # Create subcategory order mappings for each category
    subcategory_sort_maps = {}
    for category in categories:
        if "subcategories" in category:
            subcat_order = [sub["name"] for sub in category["subcategories"]]
            subcategory_sort_maps[category["name"]] = {
                name: idx for idx, name in enumerate(subcat_order)
            }

    # Read the CSV data
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    # Sort the rows
    # First by Category (using custom order), then by Sub-Category
    # (using defined order from YAML), then by Display Name
    def subcategory_sort_key(category, subcat):
        """Sort subcategories by their defined order in categories.yaml"""
        if not subcat:
            return 999  # Empty sorts last

        # Get the sort map for this category
        if category in subcategory_sort_maps:
            subcat_map = subcategory_sort_maps[category]
            return subcat_map.get(subcat, 998)  # Unknown subcategories sort second-to-last

        # If no sort map, fall back to alphabetical
        return 997  # Categories without defined subcategory order

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            category_sort_map.get(row.get("Category", ""), 999),  # Unknown categories sort last
            subcategory_sort_key(row.get("Category", ""), row.get("Sub-Category", "")),
            row.get("Display Name", "").lower(),
        ),
    )

    # Write the sorted data back
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        if headers:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(sorted_rows)

    print(f"✓ Sorted {len(sorted_rows)} resources in {csv_path}")

    # Print summary of categories
    category_counts: dict[str, dict[str, int]] = {}
    for row in sorted_rows:
        category_name = row.get("Category", "Unknown")
        subcat = row.get("Sub-Category", "") or "None"
        if category_name not in category_counts:
            category_counts[category_name] = {}
        if subcat not in category_counts[category_name]:
            category_counts[category_name][subcat] = 0
        category_counts[category_name][subcat] += 1

    print("\nCategory Summary:")
    # Sort categories using the same custom order
    sorted_categories = sorted(
        category_counts.keys(), key=lambda cat: category_sort_map.get(cat, 999)
    )
    for category_name in sorted_categories:
        print(f"  {category_name}:")
        # Sort subcategories using the same order as in the CSV sorting
        sorted_subcats = sorted(
            category_counts[category_name].keys(),
            key=lambda s: subcategory_sort_key(category_name, s if s != "None" else ""),
        )
        for subcat in sorted_subcats:
            count = category_counts[category_name][subcat]
            if subcat == "None":
                print(f"    (no sub-category): {count} items")
            else:
                print(f"    {subcat}: {count} items")


def main():
    """Main entry point."""
    # Default to THE_RESOURCES_TABLE.csv in parent directory
    csv_path = REPO_ROOT / "THE_RESOURCES_TABLE.csv"

    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    sort_resources(csv_path)


if __name__ == "__main__":
    main()
