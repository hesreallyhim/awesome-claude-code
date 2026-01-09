#!/usr/bin/env python3
"""
Badge Issue Notification (GitHub Actions only).

Creates a single notification issue in a specified GitHub repository
when a resource PR is merged. This script is designed for automated
use in GitHub Actions and is not intended for manual execution.
"""

import os
import sys
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv  # type: ignore[import]

    load_dotenv()
except ImportError:
    pass


REPO_ROOT = find_repo_root(Path(__file__))
sys.path.insert(0, str(REPO_ROOT))

from scripts.badges.badge_notification_core import BadgeNotificationCore  # noqa: E402


def main():
    """Main execution for automated notification via GitHub Actions."""

    # Get inputs from environment variables (set by GitHub Actions)
    repo_url = os.environ.get("REPOSITORY_URL", "").strip()
    resource_name = os.environ.get("RESOURCE_NAME", "").strip() or None
    description = os.environ.get("DESCRIPTION", "").strip() or None
    # Validate required inputs
    if not repo_url:
        print("Error: REPOSITORY_URL environment variable is required")
        sys.exit(1)

    # Get GitHub token
    github_token = os.environ.get("AWESOME_CC_PAT_PUBLIC_REPO")
    if not github_token:
        print("Error: AWESOME_CC_PAT_PUBLIC_REPO environment variable is required")
        print("This token needs 'public_repo' scope to create issues in external repositories")
        sys.exit(1)

    # Log the operation
    print(f"Sending notification to: {repo_url}")
    if resource_name:
        print(f"Resource name: {resource_name}")
    if description:
        print(f"Description: {description[:100]}...")

    try:
        # Initialize the core notification system
        notifier = BadgeNotificationCore(github_token)

        # Send the notification using the core module
        result = notifier.create_notification_issue(
            repo_url=repo_url,
            resource_name=resource_name,
            description=description,
        )

        # Handle the result
        if result["success"]:
            print(f"✅ Success! Issue created: {result['issue_url']}")
            sys.exit(0)
        else:
            print(f"❌ Failed: {result['message']}")

            # Provide helpful guidance based on error
            if "Security validation failed" in result["message"]:
                print("\n🛡️ SECURITY: Dangerous content detected in input")
                print("   The operation was aborted for security reasons.")
                print("   Check the resource name and description for:")
                print("   - HTML tags or JavaScript")
                print("   - Protocol handlers (javascript:, data:, etc.)")
                print("   - Event handlers (onclick=, onerror=, etc.)")
            elif "Invalid or dangerous" in result["message"]:
                print("\n💡 Tip: Ensure the URL is a valid GitHub repository URL")
                print("   Format: https://github.com/owner/repository")
            elif "Rate limit" in result["message"]:
                print("\n💡 Tip: GitHub API rate limit reached. Please wait and try again.")
            elif "Permission denied" in result["message"]:
                print("\n💡 Tip: Ensure your PAT has 'public_repo' scope")
            elif "not found or private" in result["message"]:
                print("\n💡 Tip: The repository may be private or deleted")
            elif "issues disabled" in result["message"]:
                print("\n💡 Tip: The repository has issues disabled in settings")

            sys.exit(1)

    except ValueError as e:
        # Handle initialization errors (e.g., missing token)
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
