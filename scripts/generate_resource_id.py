#!/usr/bin/env python3
"""
Simple script to generate a resource ID for manual CSV additions.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.category_utils import category_manager
from scripts.resource_id import generate_resource_id


def main():
    print("Resource ID Generator")
    print("=" * 40)

    # Get input
    display_name = input("Display Name: ").strip()
    primary_link = input("Primary Link: ").strip()

    categories = category_manager.get_all_categories()
    print("\nAvailable categories:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")

    cat_choice = input("\nSelect category number: ").strip()
    try:
        category = categories[int(cat_choice) - 1]
    except (ValueError, IndexError):
        print("Invalid category selection. Using custom category.")
        category = input("Enter custom category: ").strip()

    # Generate ID
    resource_id = generate_resource_id(display_name, primary_link, category)

    print(f"\nGenerated ID: {resource_id}")
    print("\nCSV Row Preview:")
    print(f"ID: {resource_id}")
    print(f"Display Name: {display_name}")
    print(f"Category: {category}")
    print(f"Primary Link: {primary_link}")


if __name__ == "__main__":
    main()
