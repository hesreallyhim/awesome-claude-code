#!/usr/bin/env python3
"""
Manual Badge Issue Notification
Creates a single notification issue in a specified GitHub repository
for manual/ad-hoc notifications about being featured in Awesome Claude Code

This script uses the shared badge_notification_core module for all
core functionality, ensuring consistency and security across the system.
"""

import os
import sys

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Import the shared core module
try:
    from scripts.badge_notification_core import BadgeNotificationCore, ManualNotificationTracker
except (ImportError, ModuleNotFoundError):
    # If running from a different directory, try to add scripts to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from badge_notification_core import BadgeNotificationCore, ManualNotificationTracker


def main():
    """Main execution for manual notification using shared core module"""

    # Get inputs from environment variables (set by GitHub Actions)
    repo_url = os.environ.get("REPOSITORY_URL", "").strip()
    resource_name = os.environ.get("RESOURCE_NAME", "").strip() or None
    description = os.environ.get("DESCRIPTION", "").strip() or None
    skip_duplicate_check = os.environ.get("SKIP_DUPLICATE_CHECK", "false").lower() == "true"
    enable_tracking = os.environ.get("ENABLE_TRACKING", "false").lower() == "true"

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
    if skip_duplicate_check:
        print("Skipping duplicate check")

    try:
        # Initialize the core notification system
        notifier = BadgeNotificationCore(github_token)

        # Optional: Check if recently notified (using optional tracker)
        if enable_tracking and not skip_duplicate_check:
            tracker = ManualNotificationTracker()
            if tracker.has_recent_notification(repo_url, time_window_hours=24):
                print("⚠️  Warning: This repository was already notified in the last 24 hours")
                print("Use SKIP_DUPLICATE_CHECK=true to force notification")
                # Continue anyway if user wants to

        # Send the notification using the core module
        result = notifier.create_notification_issue(
            repo_url=repo_url,
            resource_name=resource_name,
            description=description,
            skip_duplicate_check=skip_duplicate_check,
        )

        # Handle the result
        if result["success"]:
            print(f"✅ Success! Issue created: {result['issue_url']}")

            # Optional: Track the notification
            if enable_tracking:
                tracker = ManualNotificationTracker()
                tracker.record_notification(
                    repo_url=repo_url,
                    issue_url=result["issue_url"],
                    resource_name=resource_name or "",
                )
                print("Notification recorded in tracking file")

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
