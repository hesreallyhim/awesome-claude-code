#!/usr/bin/env python3
"""Git and GitHub utility functions for command-line operations."""

import logging
import subprocess
from pathlib import Path


class GitUtils:
    """Handle git and GitHub operations."""

    def __init__(self, logger: logging.Logger | None = None):
        """
        Initialize GitUtils.

        Args:
            logger: Optional logger instance. If not provided, creates a
                default logger.
        """
        self.logger = logger or logging.getLogger(__name__)

    def check_command_exists(self, command: str) -> bool:
        """
        Check if a command is available in the system PATH.

        Args:
            command: Command name to check (e.g., 'git', 'gh')

        Returns:
            True if command exists, False otherwise
        """
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def run_command(self, cmd: list[str], error_msg: str = "") -> bool:
        """
        Run a command and check if it succeeds.

        Args:
            cmd: Command to run as list of strings
            error_msg: Optional error message to log on failure

        Returns:
            True if command succeeds, False otherwise
        """
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                if error_msg:
                    self.logger.error(f"{error_msg}: {result.stderr}")
                return False
            return True
        except Exception as e:
            if error_msg:
                self.logger.error(f"{error_msg}: {e}")
            return False

    def is_git_installed(self) -> bool:
        """Check if git is installed."""
        return self.check_command_exists("git")

    def is_gh_installed(self) -> bool:
        """Check if GitHub CLI (gh) is installed."""
        return self.check_command_exists("gh")

    def is_gh_authenticated(self) -> bool:
        """Check if GitHub CLI is authenticated."""
        try:
            # Try to get the current user - this will fail if not authenticated
            result = subprocess.run(
                ["gh", "api", "user", "-q", ".login"],
                capture_output=True,
                text=True,
                check=False,
            )
            # If we get a username back, we're authenticated
            return result.returncode == 0 and result.stdout.strip() != ""
        except Exception:
            return False

    def get_github_username(self) -> str | None:
        """
        Get GitHub username from gh CLI.

        Returns:
            GitHub username or None if not available
        """
        try:
            result = subprocess.run(
                ["gh", "api", "user", "--jq", ".login"],
                capture_output=True,
                text=True,
                check=True,
            )
            username = result.stdout.strip()
            return username if username else None
        except subprocess.CalledProcessError:
            self.logger.warning("Could not get GitHub username from gh CLI")
            return None

    def get_git_config(self, key: str) -> str | None:
        """
        Get a git configuration value.

        Args:
            key: Git config key (e.g., 'user.name', 'user.email')

        Returns:
            Config value or None if not set
        """
        try:
            result = subprocess.run(
                ["git", "config", key], capture_output=True, text=True, check=False
            )
            value = result.stdout.strip()
            return value if value else None
        except subprocess.SubprocessError:
            return None

    def check_remote_exists(self, remote_name: str = "origin") -> bool:
        """
        Check if a git remote exists.

        Args:
            remote_name: Name of the remote to check

        Returns:
            True if remote exists, False otherwise
        """
        return self.run_command(
            ["git", "remote", "get-url", remote_name],
            f"Remote '{remote_name}' not found",
        )

    def get_remote_url(self, remote_name: str = "origin") -> str | None:
        """
        Get URL for a git remote.

        Args:
            remote_name: Name of the remote

        Returns:
            Remote URL or None if remote doesn't exist
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", remote_name],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_remote_type(self, remote_name: str = "origin") -> str | None:
        """
        Detect whether a git remote uses SSH or HTTPS.

        Args:
            remote_name: Name of the remote to check

        Returns:
            "ssh" or "https" or None if remote doesn't exist
        """
        url = self.get_remote_url(remote_name)
        if not url:
            return None

        if url.startswith("git@") or url.startswith("ssh://"):
            return "ssh"
        elif url.startswith("https://"):
            return "https"
        else:
            self.logger.warning(f"Unknown remote URL format: {url}")
            return None

    def is_working_directory_clean(self) -> bool:
        """
        Check if working directory has no uncommitted changes.

        Returns:
            True if clean, False if there are uncommitted changes
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            return not result.stdout.strip()
        except subprocess.SubprocessError:
            return False

    def get_uncommitted_files(self) -> str | None:
        """
        Get list of uncommitted files.

        Returns:
            Output of git status --porcelain or None on error
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return None

    def stage_file(self, filepath: Path, cwd: Path | None = None) -> bool:
        """
        Stage a file for commit.

        Args:
            filepath: Path to file to stage
            cwd: Working directory for the command

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "add", str(filepath)],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.logger.error(f"Failed to stage file: {result.stderr}")
                return False
            return True
        except subprocess.SubprocessError as e:
            self.logger.error(f"Error staging file: {e}")
            return False

    def check_file_modified(self, filepath: Path, cwd: Path | None = None) -> bool:
        """
        Check if a file has been modified (staged or unstaged).

        Args:
            filepath: Path to check
            cwd: Working directory for the command

        Returns:
            True if file is modified, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", str(filepath)],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            unstaged = bool(result.stdout.strip())

            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", str(filepath)],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            staged = bool(result.stdout.strip())

            return unstaged or staged
        except subprocess.SubprocessError:
            return False
