#!/usr/bin/env python3
"""
Create a pull request with a new resource addition.
This script is called by the GitHub Action after approval.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# Import existing functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_resource import append_to_csv, generate_pr_content
from generate_readme import generate_readme_from_templates
from resource_id import generate_resource_id


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def create_unique_branch_name(base_name: str) -> str:
    """Create a unique branch name with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{base_name}-{timestamp}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create PR from approved resource submission")
    parser.add_argument("--issue-number", required=True, help="Issue number")
    parser.add_argument("--resource-data", required=True, help="Path to resource data JSON file")
    args = parser.parse_args()

    # Load resource data
    with open(args.resource_data) as f:
        resource_data = json.load(f)

    # If the validation returned a structure with 'data' field, extract it
    if isinstance(resource_data, dict) and "data" in resource_data:
        resource_data = resource_data["data"]

    # Generate resource ID
    resource_id = generate_resource_id(
        resource_data["display_name"], resource_data["primary_link"], resource_data["category"]
    )

    # Prepare the complete resource data
    resource = {
        "id": resource_id,
        "display_name": resource_data["display_name"],
        "category": resource_data["category"],
        "subcategory": resource_data.get("subcategory", ""),
        "primary_link": resource_data["primary_link"],
        "secondary_link": resource_data.get("secondary_link", ""),
        "author_name": resource_data["author_name"],
        "author_link": resource_data["author_link"],
        "license": resource_data.get("license", "NOT_FOUND"),
        "description": resource_data["description"],
    }

    # Create branch name based on category and display name
    safe_name = resource_data["display_name"].lower()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in safe_name)
    safe_name = safe_name.strip("-")[:50]  # Limit length

    branch_base = f"add-resource/{resource_data['category'].lower().replace(' ', '-')}/{safe_name}"
    branch_name = create_unique_branch_name(branch_base)

    try:
        # Ensure we're on main and up to date
        run_command(["git", "checkout", "main"])
        run_command(["git", "pull", "origin", "main"])

        # Create new branch
        try:
            run_command(["git", "checkout", "-b", branch_name])
        except subprocess.CalledProcessError as e:
            # Branch might already exist, try checking it out
            print(f"Failed to create branch, trying to checkout: {e}", file=sys.stderr)
            run_command(["git", "checkout", branch_name])

        # Add resource to CSV
        if not append_to_csv(resource):
            raise Exception("Failed to add resource to CSV")

        # Sort the CSV
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print("Sorting CSV after adding resource", file=sys.stderr)
        sort_result = run_command(
            ["python3", os.path.join(script_dir, "sort_resources.py")], check=False
        )
        if sort_result.returncode != 0:
            print(f"Warning: CSV sorting failed: {sort_result.stderr}", file=sys.stderr)
        else:
            print("CSV sorted successfully", file=sys.stderr)

        # Generate README
        csv_path = os.path.join(script_dir, "..", "THE_RESOURCES_TABLE.csv")
        template_dir = os.path.join(script_dir, "..", "templates")
        output_path = os.path.join(script_dir, "..", "README.md")

        print(f"Generating README from {csv_path} to {output_path}", file=sys.stderr)
        try:
            generate_readme_from_templates(csv_path, template_dir, output_path)
            print("README generation completed successfully", file=sys.stderr)
        except Exception as e:
            print(f"ERROR generating README: {e}", file=sys.stderr)
            raise

        # Check if README was modified
        status_result = run_command(["git", "status", "--porcelain"])
        print(f"Git status after README generation:\n{status_result.stdout}", file=sys.stderr)

        # Stage changes
        run_command(["git", "add", "THE_RESOURCES_TABLE.csv", "README.md"])

        # Commit
        commit_message = f"Add resource: {resource_data['display_name']}\n\n"
        commit_message += f"Category: {resource_data['category']}\n"
        if resource_data.get("subcategory"):
            commit_message += f"Sub-category: {resource_data['subcategory']}\n"
        commit_message += f"Author: {resource_data['author_name']}\n"
        commit_message += f"From issue: #{args.issue_number}"

        run_command(["git", "commit", "-m", commit_message])

        # Push branch
        run_command(["git", "push", "origin", branch_name])

        # Create PR
        pr_title = f"Add resource: {resource_data['display_name']}"
        pr_body = generate_pr_content(resource)
        pr_body += f"\n\n---\n\nResolves #{args.issue_number}"

        # Use gh CLI to create PR
        result = run_command(
            [
                "gh",
                "pr",
                "create",
                "--title",
                pr_title,
                "--body",
                pr_body,
                "--base",
                "main",
                "--head",
                branch_name,
            ]
        )

        # Extract PR URL from output
        pr_url = result.stdout.strip()

        # Output result
        result = {
            "success": True,
            "pr_url": pr_url,
            "branch_name": branch_name,
            "resource_id": resource_id,
        }

    except Exception as e:
        print(f"Error in create_resource_pr: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        result = {
            "success": False,
            "error": str(e),
            "branch_name": branch_name if "branch_name" in locals() else None,
        }

    print(json.dumps(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
