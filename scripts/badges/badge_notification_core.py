#!/usr/bin/env python3
"""
Core module for badge notification system
Shared functionality for both automated and manual badge notifications
Includes security hardening, rate limiting, and error handling
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path

from github import Github
from github.GithubException import (
    BadCredentialsException,
    GithubException,
    RateLimitExceededException,
    UnknownObjectException,
)

from scripts.utils.github_utils import get_github_client, parse_github_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Handle GitHub API rate limiting with exponential backoff"""

    def __init__(self):
        self.last_request_time = 0
        self.request_count = 0
        self.backoff_seconds = 1
        self.max_backoff = 60

    def check_rate_limit(self, github_client: Github) -> dict:
        """Check current rate limit status"""
        try:
            rate_limit = github_client.get_rate_limit()
            core = rate_limit.resources.core
            return {
                "remaining": core.remaining,
                "limit": core.limit,
                "reset_time": core.reset.timestamp(),
                "should_pause": core.remaining < 100,
                "should_stop": core.remaining < 10,
            }
        except Exception as e:
            logger.warning(f"Could not check rate limit: {e}")
            return {
                "remaining": -1,
                "limit": -1,
                "reset_time": 0,
                "should_pause": False,
                "should_stop": False,
            }

    def wait_if_needed(self, github_client: Github):
        """Wait if rate limiting requires it"""
        status = self.check_rate_limit(github_client)

        if status["should_stop"]:
            wait_time = max(0, status["reset_time"] - time.time())
            logger.warning(
                f"Rate limit nearly exhausted. Waiting {wait_time:.0f} seconds until reset"
            )
            time.sleep(wait_time + 1)
        elif status["should_pause"]:
            logger.info(
                f"Rate limit low ({status['remaining']} remaining). "
                f"Pausing {self.backoff_seconds} seconds"
            )
            time.sleep(self.backoff_seconds)
            self.backoff_seconds = min(self.backoff_seconds * 2, self.max_backoff)
        else:
            # Reset backoff if we're doing well
            if status["remaining"] > 1000:
                self.backoff_seconds = 1

    def handle_rate_limit_error(self, error: RateLimitExceededException):
        """Handle rate limit exception"""
        reset_time = error.headers.get("X-RateLimit-Reset", "0") if error.headers else "0"
        wait_time = max(0, int(reset_time) - time.time())
        logger.error(f"Rate limit exceeded. Waiting {wait_time} seconds until reset")
        time.sleep(wait_time + 1)


class BadgeNotificationCore:
    """Core functionality for badge notifications with security hardening"""

    # Configuration
    ISSUE_TITLE = "🎉 Your project has been featured in Awesome Claude Code!"
    NOTIFICATION_LABEL = "awesome-claude-code"
    GITHUB_URL_BASE = "https://github.com/hesreallyhim/awesome-claude-code"

    def __init__(self, github_token: str):
        """Initialize with GitHub token"""
        if not github_token:
            raise ValueError("GitHub token is required")

        self.github = get_github_client(token=github_token)
        self.rate_limiter = RateLimiter()

    @staticmethod
    def validate_input_safety(text: str, field_name: str = "input") -> tuple[bool, str]:
        """
        Validate that input text is safe for use in GitHub issues.
        Returns (is_safe, reason_if_unsafe)

        This does NOT modify the input - it only checks for dangerous content.
        If dangerous content is found, the operation should be aborted.
        """
        if not text:
            return True, ""

        # Check for dangerous protocol handlers
        dangerous_protocols = [
            "javascript:",
            "data:",
            "vbscript:",
            "file:",
            "about:",
            "chrome:",
            "ms-",
        ]
        for protocol in dangerous_protocols:
            if protocol.lower() in text.lower():
                reason = f"Dangerous protocol '{protocol}' detected in {field_name}"
                logger.warning(f"SECURITY: {reason} - Content: {text[:100]}")
                return False, reason

        # Check for HTML/script injection attempts
        dangerous_patterns = [
            "<script",
            "</script",
            "<iframe",
            "<embed",
            "<object",
            "<applet",
            "<meta",
            "<link",
            "onclick=",
            "onload=",
            "onerror=",
            "onmouseover=",
            "onfocus=",
        ]
        for pattern in dangerous_patterns:
            if pattern.lower() in text.lower():
                reason = f"HTML injection attempt detected in {field_name}: {pattern}"
                logger.warning(f"SECURITY: {reason} - Content: {text[:100]}")
                return False, reason

        # Check for excessive length (DoS prevention)
        max_length = 5000  # Reasonable limit for resource descriptions
        if len(text) > max_length:
            reason = f"{field_name} exceeds maximum length ({len(text)} > {max_length})"
            logger.warning(f"SECURITY: {reason}")
            return False, reason

        # Check for null bytes (can cause issues in various systems)
        if "\x00" in text:
            reason = f"Null byte detected in {field_name}"
            logger.warning(f"SECURITY: {reason}")
            return False, reason

        # Check for control characters (except newline and tab)
        control_chars = [chr(i) for i in range(0, 32) if i not in [9, 10, 13]]
        for char in control_chars:
            if char in text:
                reason = f"Control character (ASCII {ord(char)}) detected in {field_name}"
                logger.warning(f"SECURITY: {reason}")
                return False, reason

        return True, ""

    @staticmethod
    def validate_github_url(url: str) -> bool:
        """
        Strictly validate GitHub URL format
        Prevents command injection and other URL-based attacks
        """
        if not url:
            return False

        # Only allow HTTPS GitHub URLs
        if not url.startswith("https://github.com/"):
            return False

        # Check for dangerous characters that could be used for injection
        dangerous_chars = [
            ";",
            "|",
            "&",
            "`",
            "$",
            "(",
            ")",
            "{",
            "}",
            "<",
            ">",
            "\n",
            "\r",
            "\\",
            "'",
            '"',
        ]
        if any(char in url for char in dangerous_chars):
            return False

        # Strict regex for GitHub URLs
        # Only allow alphanumeric, dash, dot, underscore in owner/repo names
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$"
        if not re.match(pattern, url):
            return False

        # Check for path traversal attempts
        return ".." not in url

    def create_issue_body(self, resource_name: str, description: str = "") -> str:
        """Create issue body with badge options after validating inputs"""
        # Validate inputs - DO NOT modify them
        is_safe, reason = self.validate_input_safety(resource_name, "resource_name")
        if not is_safe:
            raise ValueError(f"Security validation failed: {reason}")

        if description:
            is_safe, reason = self.validate_input_safety(description, "description")
            if not is_safe:
                raise ValueError(f"Security validation failed: {reason}")

        # Use the ORIGINAL, unmodified values in the template
        # If they were unsafe, we would have thrown an exception above
        final_description = (
            description
            if description
            else f"Your project {resource_name} provides valuable resources "
            f"for the Claude Code community."
        )

        # Use the original values directly
        return f"""Hello! 👋

I'm excited to let you know that **{resource_name}** has been featured in the
[Awesome Claude Code]({self.GITHUB_URL_BASE}) list!

## About Awesome Claude Code
Awesome Claude Code is a curated collection of the best slash-commands, CLAUDE.md files,
CLI tools, and other resources for enhancing Claude Code workflows. Your project has been
recognized for its valuable contribution to the Claude Code community.

## Your Listing
{final_description}

You can find your entry here: [View in Awesome Claude Code]({self.GITHUB_URL_BASE})

## Show Your Recognition! 🏆
If you'd like to display a badge in your README to show that your project is featured,
you can use one of these:

### Option 1: Standard Badge
```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)]({self.GITHUB_URL_BASE})
```
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)]({self.GITHUB_URL_BASE})

### Option 2: Flat Badge
```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge-flat.svg)]({self.GITHUB_URL_BASE})
```
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge-flat.svg)]({self.GITHUB_URL_BASE})

## No Action Required
This is just a friendly notification - no action is required on your part.
Feel free to close this issue at any time.

Thank you for contributing to the Claude Code ecosystem! 🙏

---
*This notification was sent because your project was added to the Awesome Claude Code list. This is a one-time notification.*"""  # noqa: E501

    def can_create_label(self, repo) -> bool:
        """Check if we can create labels (requires write access)"""
        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed(self.github)

            # Try to create or get the label
            try:
                repo.get_label(self.NOTIFICATION_LABEL)
                return True  # Label already exists
            except UnknownObjectException:
                # Label doesn't exist, try to create it
                repo.create_label(
                    self.NOTIFICATION_LABEL, "f39c12", "Featured in Awesome Claude Code"
                )
                return True
        except GithubException as e:
            if e.status == 403:
                logger.info(f"No permission to create labels in {repo.full_name}")
            else:
                logger.warning(f"Could not create label for {repo.full_name}: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error creating label for {repo.full_name}: {e}")
            return False

    def create_notification_issue(
        self,
        repo_url: str,
        resource_name: str | None = None,
        description: str | None = None,
    ) -> dict:
        """
        Create a notification issue in the specified repository

        Returns dict with: success, message, issue_url, repo_url
        """
        result = {
            "repo_url": repo_url,
            "success": False,
            "message": "",
            "issue_url": None,
        }

        # Validate and parse URL
        if not self.validate_github_url(repo_url):
            result["message"] = "Invalid or dangerous GitHub URL format"
            return result

        _, is_github, owner, repo_name = parse_github_url(repo_url)
        if not is_github or not owner or not repo_name:
            result["message"] = "Invalid or dangerous GitHub URL format"
            return result

        repo_full_name = f"{owner}/{repo_name}"

        # Use resource name from input or default to repo name
        if not resource_name:
            resource_name = repo_name

        # Skip Anthropic repositories
        if "anthropic" in owner.lower() or "anthropic" in repo_name.lower():
            result["message"] = "Skipping Anthropic repository"
            return result

        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed(self.github)

            # Get the repository
            repo = self.github.get_repo(repo_full_name)

            # Try to create or use label
            labels = []
            if self.can_create_label(repo):
                labels = [self.NOTIFICATION_LABEL]

            # Create the issue body (this will validate inputs and throw if unsafe)
            try:
                issue_body = self.create_issue_body(resource_name, description or "")
            except ValueError as e:
                # Security validation failed - abort the operation
                result["message"] = str(e)
                logger.error(f"Security validation failed for {repo_full_name}: {e}")
                return result

            # Apply rate limiting before creating issue
            self.rate_limiter.wait_if_needed(self.github)

            # Create the issue
            issue = repo.create_issue(title=self.ISSUE_TITLE, body=issue_body, labels=labels)

            result["success"] = True
            result["message"] = "Issue created successfully"
            result["issue_url"] = issue.html_url

        except UnknownObjectException:
            result["message"] = "Repository not found or private"
        except BadCredentialsException:
            result["message"] = "Invalid GitHub token"
        except RateLimitExceededException as e:
            self.rate_limiter.handle_rate_limit_error(e)
            result["message"] = "Rate limit exceeded - please try again later"
        except GithubException as e:
            if e.status == 410:
                result["message"] = "Repository has issues disabled"
            elif e.status == 403:
                if "Resource not accessible" in str(e):
                    result["message"] = "Insufficient permissions - requires public_repo scope"
                else:
                    result["message"] = "Permission denied - check PAT permissions"
            else:
                logger.error(f"GitHub API error for {repo_full_name}: {e}")
                result["message"] = f"GitHub API error (status {e.status})"
        except Exception as e:
            logger.error(f"Unexpected error for {repo_full_name}: {e}")
            result["message"] = f"Unexpected error: {str(e)[:100]}"

        return result


class ManualNotificationTracker:
    """Optional state tracking for manual notifications"""

    def __init__(self, tracking_file: str = ".manual_notifications.json"):
        self.tracking_file = Path(tracking_file)
        self.history = self._load_history()

    def _load_history(self) -> list:
        """Load notification history from file"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load history: {e}")
        return []

    def _save_history(self):
        """Save notification history to file"""
        try:
            with open(self.tracking_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save history: {e}")

    def record_notification(self, repo_url: str, issue_url: str, resource_name: str = ""):
        """Record a manual notification"""
        entry = {
            "repo_url": repo_url,
            "issue_url": issue_url,
            "resource_name": resource_name,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(entry)
        self._save_history()

    def get_notification_count(self, repo_url: str, time_window_hours: int = 24) -> int:
        """Get count of recent notifications for a repository"""
        cutoff = datetime.now().timestamp() - (time_window_hours * 3600)
        count = 0

        for entry in self.history:
            if entry["repo_url"] == repo_url:
                try:
                    timestamp = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    if timestamp > cutoff:
                        count += 1
                except Exception:
                    pass

        return count

    def has_recent_notification(self, repo_url: str, time_window_hours: int = 24) -> bool:
        """Check if repository was notified recently"""
        return self.get_notification_count(repo_url, time_window_hours) > 0
