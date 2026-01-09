#!/usr/bin/env python3
"""
Script to automate adding a new category to awesome-claude-code.
This handles all the necessary file updates and regenerates the README.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.utils.repo_root import find_repo_root

# Add repo root to path for imports

REPO_ROOT = find_repo_root(Path(__file__))
sys.path.insert(0, str(REPO_ROOT))

from scripts.categories.category_utils import category_manager  # noqa: E402


class CategoryAdder:
    """Handles the process of adding a new category to the repository."""

    def __init__(self, repo_root: Path):
        """Initialize the CategoryAdder with the repository root path."""
        self.repo_root = repo_root
        self.templates_dir = repo_root / "templates"
        self.github_dir = repo_root / ".github" / "ISSUE_TEMPLATE"

    def get_max_order(self) -> int:
        """Get the maximum order value from existing categories."""
        categories = category_manager.get_categories_for_readme()
        if not categories:
            return 0
        return max(cat.get("order", 0) for cat in categories)

    def add_category_to_yaml(
        self,
        category_id: str,
        name: str,
        prefix: str,
        icon: str,
        description: str,
        order: int | None = None,
        subcategories: list[str] | None = None,
    ) -> bool:
        """
        Add a new category to categories.yaml.

        Args:
            category_id: The ID for the category (e.g., "alternative-clients")
            name: Display name (e.g., "Alternative Clients")
            prefix: ID prefix for resources (e.g., "client")
            icon: Emoji icon for the category
            description: Markdown description of the category
            order: Order in the list (if None, will be added at the end)
            subcategories: List of subcategory names (defaults to ["General"])

        Returns:
            True if successful, False otherwise
        """
        categories_file = self.templates_dir / "categories.yaml"

        # Load existing categories
        with open(categories_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "categories" not in data:
            print("Error: Invalid categories.yaml structure")
            return False

        # Check if category already exists
        for cat in data["categories"]:
            if cat["id"] == category_id:
                print(f"Category '{category_id}' already exists")
                return False

        # Determine order
        if order is None:
            order = self.get_max_order() + 1

        # Prepare subcategories
        if subcategories is None:
            subcategories = ["General"]

        subcats_data = [{"id": sub.lower().replace(" ", "-"), "name": sub} for sub in subcategories]

        # Create new category entry
        new_category = {
            "id": category_id,
            "name": name,
            "prefix": prefix,
            "icon": icon,
            "description": description,
            "order": order,
            "subcategories": subcats_data,
        }

        # If inserting with specific order, update other categories' orders
        if order <= self.get_max_order():
            for cat in data["categories"]:
                if cat.get("order", 0) >= order:
                    cat["order"] = cat.get("order", 0) + 1

        # Add the new category
        data["categories"].append(new_category)

        # Sort categories by order
        data["categories"] = sorted(data["categories"], key=lambda x: x.get("order", 999))

        # Write back to file
        with open(categories_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"✅ Added '{name}' to categories.yaml with order {order}")
        return True

    def update_issue_template(self, name: str) -> bool:
        """
        Update the GitHub issue template to include the new category.

        Args:
            name: Display name of the category

        Returns:
            True if successful, False otherwise
        """
        template_file = self.github_dir / "recommend-resource.yml"

        with open(template_file, encoding="utf-8") as f:
            content = f.read()

        # Find the category dropdown section
        lines = content.split("\n")
        in_category_section = False
        category_start_idx = -1
        category_end_idx = -1

        for i, line in enumerate(lines):
            if "id: category" in line:
                in_category_section = True
                continue

            if in_category_section:
                if "options:" in line:
                    category_start_idx = i + 1
                elif category_start_idx > 0 and line.strip() and not line.strip().startswith("-"):
                    category_end_idx = i
                    break

        if category_start_idx < 0:
            print("Error: Could not find category options in issue template")
            return False

        # Extract existing categories
        existing_categories = []
        for i in range(category_start_idx, category_end_idx):
            line = lines[i].strip()
            if line.startswith("- "):
                existing_categories.append(line[2:])

        # Check if category already exists
        if name in existing_categories:
            print(f"Category '{name}' already exists in issue template")
            return True

        # Find where to insert (before Official Documentation)
        insert_idx = category_start_idx
        for i in range(category_start_idx, category_end_idx):
            if "Official Documentation" in lines[i]:
                insert_idx = i
                break

        # Insert the new category
        lines.insert(insert_idx, f"        - {name}")

        # Write back to file
        with open(template_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ Added '{name}' to GitHub issue template")
        return True

    def generate_readme(self) -> bool:
        """Generate the README using make generate."""
        print("\n📝 Generating README...")
        try:
            result = subprocess.run(
                ["make", "generate"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                print("Error generating README:")
                if result.stderr:
                    print(result.stderr)
                return False

            print("✅ README generated successfully")
            return True

        except FileNotFoundError:
            print("Error: 'make' command not found")
            return False

    def create_commit(self, name: str) -> bool:
        """Create a commit with the changes."""
        print("\n📦 Creating commit...")

        try:
            # Stage the changes
            files_to_stage = [
                "templates/categories.yaml",
                ".github/ISSUE_TEMPLATE/recommend-resource.yml",
                "README.md",
            ]

            for file in files_to_stage:
                subprocess.run(
                    ["git", "add", file],
                    cwd=self.repo_root,
                    check=True,
                    capture_output=True,
                )

            # Create commit
            commit_message = f"""Add new category: {name}

- Add {name} category to templates/categories.yaml
- Update GitHub issue template to include {name}
- Regenerate README with new category section

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("No changes to commit")
                else:
                    print("Error creating commit:")
                    if result.stderr:
                        print(result.stderr)
                    return False
            else:
                print(f"✅ Created commit for '{name}' category")

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error with git operations: {e}")
            return False


def interactive_mode(adder: CategoryAdder) -> None:
    """Run the script in interactive mode, prompting for all inputs."""
    print("=" * 60)
    print("ADD NEW CATEGORY TO AWESOME CLAUDE CODE")
    print("=" * 60)
    print()

    # Get category details
    name = input("Enter category display name (e.g., 'Alternative Clients'): ").strip()
    if not name:
        print("Error: Name is required")
        sys.exit(1)

    # Generate ID from name
    category_id = name.lower().replace(" ", "-").replace("&", "and")
    suggested_id = category_id
    category_id = input(f"Enter category ID (default: '{suggested_id}'): ").strip() or suggested_id

    # Generate prefix from name
    suggested_prefix = name.lower().split()[0][:6]
    prefix = input(f"Enter ID prefix (default: '{suggested_prefix}'): ").strip() or suggested_prefix

    # Get icon
    icon = input("Enter emoji icon (e.g., 🔌): ").strip() or "📦"

    # Get description
    print("\nEnter description (can be multiline, enter '---' on a new line to finish):")
    description_lines = []
    while True:
        line = input()
        if line == "---":
            break
        description_lines.append(line)

    description = "\n".join(description_lines)
    if description and not description.startswith(">"):
        description = "> " + description.replace("\n", "\n> ")

    # Get order
    max_order = adder.get_max_order()
    order_input = input(
        f"Enter order position (1-{max_order + 1}, default: {max_order + 1}): "
    ).strip()
    order = int(order_input) if order_input else max_order + 1

    # Get subcategories
    print("\nSubcategories Configuration:")
    print("Most categories only need 'General'. Add more only if you need specific groupings.")
    print("Examples:")
    print("  - For simple categories: Just press Enter (uses 'General')")
    print("  - For complex categories: General, Advanced, Experimental")
    print("\nEnter subcategories (comma-separated, default: 'General'):")
    subcats_input = input("> ").strip()
    subcategories = (
        [s.strip() for s in subcats_input.split(",") if s.strip()] if subcats_input else ["General"]
    )

    # Ensure General is always included if not explicitly added
    if subcategories and "General" not in subcategories:
        print("\nNote: Consider including 'General' as a catch-all subcategory.")

    # Confirm
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Name: {name}")
    print(f"ID: {category_id}")
    print(f"Prefix: {prefix}")
    print(f"Icon: {icon}")
    print(f"Order: {order}")
    print(f"Subcategories: {', '.join(subcategories)}")
    print(f"Description:\n{description}")
    print("=" * 60)

    confirm = input("\nProceed with adding this category? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled")
        sys.exit(0)

    # Add the category
    if not adder.add_category_to_yaml(
        category_id, name, prefix, icon, description, order, subcategories
    ):
        sys.exit(1)

    if not adder.update_issue_template(name):
        sys.exit(1)

    if not adder.generate_readme():
        sys.exit(1)

    # Ask about commit
    commit_confirm = input("\nCreate a commit with these changes? (y/n): ").strip().lower()
    if commit_confirm == "y":
        adder.create_commit(name)

    print("\n✨ Category added successfully!")
    print("\n📝 Note: The category will appear in the Table of Contents only after")
    print("   resources are added to it. This is by design to keep the ToC clean.")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Add a new category to awesome-claude-code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s --name "My Category" --prefix "mycat" --icon "🎯"
  %(prog)s --name "Tools" --order 5 --subcategories "CLI,GUI,Web"
        """,
    )

    parser.add_argument("--name", help="Display name for the category")
    parser.add_argument("--id", help="Category ID (defaults to slugified name)")
    parser.add_argument("--prefix", help="ID prefix for resources")
    parser.add_argument("--icon", default="📦", help="Emoji icon for the category")
    parser.add_argument(
        "--description", help="Description of the category (will be prefixed with '>')"
    )
    parser.add_argument("--order", type=int, help="Order position in the list")
    parser.add_argument(
        "--subcategories",
        help="Comma-separated list of subcategories (default: General)",
    )
    parser.add_argument(
        "--no-commit", action="store_true", help="Don't create a commit after adding"
    )

    args = parser.parse_args()

    # Get repository root
    adder = CategoryAdder(REPO_ROOT)

    # If name is provided, run in non-interactive mode
    if args.name:
        # Generate defaults for missing arguments
        category_id = args.id or args.name.lower().replace(" ", "-").replace("&", "and")
        prefix = args.prefix or args.name.lower().split()[0][:6]
        description = args.description or f"> **{args.name}** category for awesome-claude-code"
        if not description.startswith(">"):
            description = "> " + description

        subcategories = (
            [s.strip() for s in args.subcategories.split(",")]
            if args.subcategories
            else ["General"]
        )

        # Add the category
        if not adder.add_category_to_yaml(
            category_id,
            args.name,
            prefix,
            args.icon,
            description,
            args.order,
            subcategories,
        ):
            sys.exit(1)

        if not adder.update_issue_template(args.name):
            sys.exit(1)

        if not adder.generate_readme():
            sys.exit(1)

        if not args.no_commit:
            adder.create_commit(args.name)

        print("\n✨ Category added successfully!")
        print("\n📝 Note: The category will appear in the Table of Contents only after")
        print("   resources are added to it. This is by design to keep the ToC clean.")
    else:
        # Run in interactive mode
        interactive_mode(adder)


if __name__ == "__main__":
    main()
