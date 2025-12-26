#!/usr/bin/env python3
"""
Create a pull request with a new resource addition.
This script is called by the GitHub Action after approval.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

# Import existing functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_resource import append_to_csv, generate_pr_content
from generate_readme import main as generate_readmes
from resource_id import generate_resource_id
from validate_links import get_github_commit_dates_from_url, get_latest_release_info


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def create_unique_branch_name(base_name: str) -> str:
    """Create a unique branch name with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{base_name}-{timestamp}"


def get_badge_filename(display_name: str) -> str:
    """Compute the badge filename for a resource.

    Uses the same logic as save_resource_badge_svg in generate_readme.py.
    """
    safe_name = re.sub(r"[^a-zA-Z0-9]", "-", display_name.lower())
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    return f"badge-{safe_name}.svg"


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

    # Fetch commit dates from GitHub if applicable
    primary_link = resource_data["primary_link"]
    first_commit_date, last_commit_date = get_github_commit_dates_from_url(primary_link)

    if last_commit_date:
        print(f"Fetched Last Modified date from GitHub: {last_commit_date}", file=sys.stderr)
    else:
        print("Could not fetch Last Modified date from GitHub (non-GitHub URL or API error)", file=sys.stderr)

    if first_commit_date:
        print(f"Fetched First Commit date from GitHub: {first_commit_date}", file=sys.stderr)

    # Fetch latest release info
    release_date, release_version, release_source = get_latest_release_info(
        primary_link, resource_data["display_name"]
    )
    if release_date:
        print(f"Fetched release info: {release_version} from {release_source} ({release_date})", file=sys.stderr)
    else:
        print("No release info found (no releases/tags or non-GitHub URL)", file=sys.stderr)

    # Prepare the complete resource data
    resource = {
        "id": resource_id,
        "display_name": resource_data["display_name"],
        "category": resource_data["category"],
        "subcategory": resource_data.get("subcategory", ""),
        "primary_link": primary_link,
        "secondary_link": resource_data.get("secondary_link", ""),
        "author_name": resource_data["author_name"],
        "author_link": resource_data["author_link"],
        "license": resource_data.get("license", "NOT_FOUND"),
        "description": resource_data["description"],
        "last_modified": last_commit_date or "",  # Set from GitHub API
        "repo_created": first_commit_date or "",  # First commit date from GitHub API
        "latest_release": release_date or "",  # Latest release date
        "release_version": release_version or "",  # Release version (e.g., v1.2.3)
        "release_source": release_source or "",  # Release source (npm, pypi, github-releases)
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

        # Generate all README variants
        print("Generating README files...", file=sys.stderr)
        try:
            generate_readmes()
            print("README generation completed successfully", file=sys.stderr)
        except Exception as e:
            print(f"ERROR generating README: {e}", file=sys.stderr)
            raise

        # Check if README was modified
        status_result = run_command(["git", "status", "--porcelain"])
        print(f"Git status after README generation:\n{status_result.stdout}", file=sys.stderr)

        # Compute badge path and check if it was generated
        script_dir_abs = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(script_dir_abs)
        badge_filename = get_badge_filename(resource_data["display_name"])
        badge_path = os.path.join(repo_root, "assets", badge_filename)
        badge_warning = ""

        # Stage changes (all README variants)
        files_to_stage = ["THE_RESOURCES_TABLE.csv", "README.md", "README_CLASSIC.md", "README_FLAT_LAST_MODIFIED.md", "README_FLAT_LAST_CREATED.md", "README_FLAT_ALPHABETICAL.md", "README_FLAT_LATEST_RELEASES.md"]

        if os.path.exists(badge_path):
            # Stage the badge file relative to repo root
            files_to_stage.append(f"assets/{badge_filename}")
            print(f"Badge file found and will be staged: {badge_filename}", file=sys.stderr)
        else:
            print(f"Warning: Badge file not generated: {badge_path}", file=sys.stderr)
            badge_warning = (
                f"\n\n> **Warning**: Badge SVG (`assets/{badge_filename}`) was not generated. "
                "Manual attention may be required."
            )

        run_command(["git", "add", *files_to_stage])

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
        pr_body += badge_warning  # Empty string if badge was generated successfully
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
