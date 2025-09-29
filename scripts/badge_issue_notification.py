#!/usr/bin/env python3
"""
Badge Issue Notification System
Creates friendly notification issues when NEW repositories are featured in
Awesome Claude Code
"""

import csv
import json
import os
import re
import sys
from datetime import datetime
from typing import Any

from github import Github, GithubException

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not installed, that's okay
    pass


# Configuration
ISSUE_TITLE = "🎉 Your project has been featured in Awesome Claude Code!"
NOTIFICATION_LABEL = "awesome-claude-code"


class BadgeNotification:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.processed_repos = self._load_processed_repos()

    def _load_processed_repos(self) -> set:
        """Load list of already processed repositories"""
        try:
            with open(".processed_repos.json") as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()

    def _save_processed_repos(self):
        """Save list of processed repositories"""
        with open(".processed_repos.json", "w") as f:
            json.dump(sorted(self.processed_repos), f, indent=2)

    def get_all_github_repos_from_csv(self, csv_path: str) -> dict:
        """Get all active GitHub repositories from the CSV"""
        github_repos = {}

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                # Check if it's an active GitHub entry
                if row.get("Active", "").upper() == "TRUE" and "github.com" in row.get(
                    "Primary Link", ""
                ):
                    # Parse repository information
                    primary_link = row.get("Primary Link", "")
                    owner, repo_name = self._parse_github_url(primary_link)
                    if owner and repo_name:
                        repo_full_name = f"{owner}/{repo_name}"
                        github_repos[repo_full_name] = {
                            "url": row.get("Primary Link", ""),
                            "name": row.get("Display Name", ""),
                            "description": row.get("Description", ""),
                            # Store the row index for updating Date Added
                            "row_index": idx,
                        }

        return github_repos

    def update_date_added_for_new_repos(self, csv_path: str, new_repos: dict):
        """Update the Date Added field for new repositories in the CSV"""
        # Read all rows from CSV
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            rows = list(reader)

        if headers is None:
            raise ValueError("CSV file has no headers. Please check the file format.")

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Track updates
        updates_made = 0

        # Update Date Added for new repos
        for repo_full_name, info in new_repos.items():
            row_idx = info.get("row_index")
            if (
                row_idx is not None
                and row_idx < len(rows)
                and not rows[row_idx].get("Date Added", "").strip()
            ):
                rows[row_idx]["Date Added"] = today
                updates_made += 1
                name = info.get("name", repo_full_name)
                print(f"  - Added date {today} for: {name}")

        # Write back to CSV if updates were made
        if updates_made > 0:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            print(f"  - Updated {updates_made} resources with Date Added = {today}")

        return updates_made

    def process_new_entries_only(self, csv_path: str, create_issues: bool = True):
        """Process only NEW GitHub entries from CSV"""
        results: list[dict[str, Any]] = []

        # Get all current GitHub repos from CSV
        current_repos = self.get_all_github_repos_from_csv(csv_path)

        # Find new repos (in CSV but not in processed list)
        new_repos = {
            repo: info for repo, info in current_repos.items() if repo not in self.processed_repos
        }

        if not new_repos:
            print("No new GitHub entries found to process.")
            return results

        print(f"Found {len(new_repos)} new GitHub entries to process.")

        # Update Date Added for new repos
        print("\nUpdating Date Added for new resources...")
        self.update_date_added_for_new_repos(csv_path, new_repos)

        if not create_issues:
            print(
                "CREATE_ISSUES is set to false. Marking repos as processed without creating issues."
            )
            # Just mark them as processed without creating issues
            for repo_full_name in new_repos:
                self.processed_repos.add(repo_full_name)
                results.append(
                    {
                        "repo_url": new_repos[repo_full_name]["url"],
                        "success": True,
                        "message": "Marked as processed (issue creation disabled)",
                        "issue_url": None,
                    }
                )
        else:
            # Create issues as normal
            for repo_full_name, info in new_repos.items():
                result = self.notify_repository(
                    repo_url=info["url"],
                    resource_name=info["name"],
                    description=info["description"],
                    repo_full_name=repo_full_name,
                )
                results.append(result)

        self._save_processed_repos()
        return results

    def notify_repository(
        self, repo_url: str, resource_name: str, description: str, repo_full_name: str
    ) -> dict:
        """Create notification issue for a single repository"""
        result = {"repo_url": repo_url, "success": False, "message": "", "issue_url": None}

        # exclude anthropics repo and anthropic.com
        if "anthropic.com" in repo_url or "anthropics" in repo_full_name:
            result["message"] = "Skipping Anthropics repository"
            self.processed_repos.add(repo_full_name)
            return result

        try:
            # Get the repository
            repo = self.github.get_repo(repo_full_name)

            # Check if issue already exists
            if self._notification_exists(repo):
                result["message"] = "Notification issue already exists"
                self.processed_repos.add(repo_full_name)
                return result

            # Create the issue
            issue_body = self._create_issue_body(resource_name, description)
            issue = repo.create_issue(
                title=ISSUE_TITLE,
                body=issue_body,
                labels=[NOTIFICATION_LABEL] if self._can_create_label(repo) else [],
            )

            self.processed_repos.add(repo_full_name)
            result["success"] = True
            result["message"] = "Issue created successfully"
            result["issue_url"] = issue.html_url

        except GithubException as e:
            if e.status == 410:
                result["message"] = "Repository has issues disabled"
            elif e.status == 404:
                result["message"] = "Repository not found or private"
            elif e.status == 403:
                result["message"] = (
                    "Permission denied - requires a Personal Access Token "
                    "(default GITHUB_TOKEN insufficient)"
                )
            else:
                result["message"] = f"GitHub API error: {str(e)}"
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"

        return result

    def _parse_github_url(self, url: str) -> tuple[str | None, str | None]:
        """Extract owner and repo name from GitHub URL"""
        patterns = [
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
            r"github\.com/([^/]+)/([^/]+)/tree",
            r"github\.com/([^/]+)/([^/]+)/blob",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)

        return None, None

    def _notification_exists(self, repo) -> bool:
        """Check if notification issue already exists"""
        try:
            issues = repo.get_issues(state="all", creator=self.github.get_user().login)
            for issue in issues:
                if "awesome claude code" in issue.title.lower():
                    return True
        except Exception as e:
            print(f"Warning: Could not check existing issues for {repo.full_name}: {e}")
        return False

    def _can_create_label(self, repo) -> bool:
        """Check if we can create labels (requires write access)"""
        try:
            repo.create_label(NOTIFICATION_LABEL, "f39c12", "Featured in Awesome Claude Code")
            return True
        except Exception as _e:
            print(f"Warning: Could not create label for {repo.full_name}: {_e}")
            return False

    def _create_issue_body(self, resource_name: str, description: str) -> str:
        """Create friendly issue body with badge options"""
        github_url = "https://github.com/hesreallyhim/awesome-claude-code"
        return f"""Hello! 👋

I'm excited to let you know that **{resource_name}** has been featured in the
[Awesome Claude Code]({github_url}) list!

## About Awesome Claude Code
Awesome Claude Code is a curated collection of the best slash-commands, CLAUDE.md files,
CLI tools, and other resources for enhancing Claude Code workflows. Your project has been
recognized for its valuable contribution to the Claude Code community.

## Your Listing
{description}

You can find your entry here: [View in Awesome Claude Code]({github_url})

## Show Your Recognition! 🏆
If you'd like to display a badge in your README to show that your project is featured,
you can use one of these:

### Option 1: Standard Badge
```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)](https://github.com/hesreallyhim/awesome-claude-code)
```
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)]({github_url})

### Option 2: Flat Badge
```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge-flat.svg)]({github_url})
```
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge-flat.svg)]({github_url})

## No Action Required
This is just a friendly notification - no action is required on your part.
Feel free to close this issue at any time.

Thank you for contributing to the Claude Code ecosystem! 🙏

---
*This notification was sent because your project was added to the Awesome Claude Code list. \
This is a one-time notification.*"""


def initialize_processed_repos_with_existing(csv_path: str):
    """One-time initialization to add all existing GitHub repos to processed list"""
    notifier = BadgeNotification(os.environ.get("GITHUB_TOKEN", ""))
    existing_repos = notifier.get_all_github_repos_from_csv(csv_path)

    print(f"Found {len(existing_repos)} existing GitHub repositories in CSV")

    # Add all existing repos to processed list
    for repo in existing_repos:
        notifier.processed_repos.add(repo)

    notifier._save_processed_repos()
    print(f"Initialized .processed_repos.json with {len(notifier.processed_repos)} repositories")


def main():
    """Main execution"""
    # Process CSV file
    csv_path = os.path.join(os.path.dirname(__file__), "..", "THE_RESOURCES_TABLE.csv")

    # Check for initialization mode
    if "--init" in sys.argv:
        print("Initializing processed repos with all existing entries...")
        initialize_processed_repos_with_existing(csv_path)
        return

    awesome_cc_token = os.environ.get("AWESOME_CC_PAT_PUBLIC_REPO", None)
    if not awesome_cc_token:
        print("Error: AWESOME_CC_PAT_PUBLIC_REPO environment variable not set")
        print("Note: This script requires a Personal Access Token (PAT) with public_repo scope")
        print(
            "The default GITHUB_TOKEN from GitHub Actions is not sufficient for "
            "creating issues in external repositories"
        )
        sys.exit(1)

    notifier = BadgeNotification(awesome_cc_token)

    # Check if we're in CI/CD environment
    is_ci = os.environ.get("CI", "false").lower() == "true"

    # Check if issue creation is enabled
    create_issues = os.environ.get("CREATE_ISSUES", "true").lower() == "true"

    if is_ci:
        print("Running in CI mode - processing only new entries")
    else:
        print("Running in manual mode - processing only new entries")

    if not create_issues:
        print("Issue creation is DISABLED via CREATE_ISSUES environment variable")

    results = notifier.process_new_entries_only(csv_path, create_issues=create_issues)

    # Print summary
    success_count = sum(1 for r in results if r["success"])
    print(f"\nProcessed {len(results)} new GitHub repositories")
    print(f"Successfully created {success_count} issues")

    # Print detailed results
    for result in results:
        if result["success"]:
            print(f"✅ {result['repo_url']} - Issue: {result['issue_url']}")
        else:
            print(f"❌ {result['repo_url']} - {result['message']}")


if __name__ == "__main__":
    main()
