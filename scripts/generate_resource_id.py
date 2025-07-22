#!/usr/bin/env python3
"""
Simple script to generate a resource ID for manual CSV additions.
"""

import hashlib

# Category prefix mapping
CATEGORY_PREFIXES = {
    "Slash-Commands": "cmd",
    "Workflows & Knowledge Guides": "wf",
    "Tooling": "tool",
    "CLAUDE.md Files": "claude",
    "Hooks": "hook",
    "Official Documentation": "doc",
}


def generate_resource_id(display_name, primary_link, category):
    """Generate a stable ID for a resource."""
    # Get category prefix, default to 'res' if not found
    prefix = CATEGORY_PREFIXES.get(category, "res")

    # Generate hash from display name + primary link
    content = f"{display_name}{primary_link}"
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:8]

    return f"{prefix}-{hash_value}"


def main():
    print("Resource ID Generator")
    print("=" * 40)

    # Get input
    display_name = input("Display Name: ").strip()
    primary_link = input("Primary Link: ").strip()

    print("\nAvailable categories:")
    for i, cat in enumerate(CATEGORY_PREFIXES.keys(), 1):
        print(f"{i}. {cat}")

    cat_choice = input("\nSelect category number: ").strip()
    try:
        category = list(CATEGORY_PREFIXES.keys())[int(cat_choice) - 1]
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
