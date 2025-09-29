#!/usr/bin/env python3
"""
submit_resource.py - One-command submission workflow for awesome-claude-code

This script automates the entire process of submitting a new resource,
from entry to pull request creation.
"""

import argparse
import csv
import logging
import os
import re
import subprocess
import sys
from enum import Enum
from pathlib import Path

from scripts.git_utils import GitUtils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class WorkflowStage(Enum):
    """Defines the stages of the submission workflow."""

    PREFLIGHT = "preflight"
    COLLECT_RESOURCE = "collect_resource"
    UPDATE_CSV = "update_csv"
    GENERATE_README = "generate_readme"
    CREATE_BRANCH = "create_branch"
    COMMIT_CHANGES = "commit_changes"
    PUSH_BRANCH = "push_branch"
    CREATE_PR = "create_pr"
    COMPLETE = "complete"


class ResourceSubmitter:
    """Orchestrates the resource submission workflow."""

    # Repository configuration
    UPSTREAM_REPO = "hesreallyhim/awesome-claude-code"
    UPSTREAM_URL = f"https://github.com/{UPSTREAM_REPO}.git"

    def __init__(self, debug: bool = False, dry_run: bool = False, admin: bool = False):
        """
        Initialize the ResourceSubmitter.

        Args:
            debug: Enable debug logging
            dry_run: Run without making actual changes
            admin: Admin mode - submit directly to upstream repository
        """
        self.debug = debug
        self.dry_run = dry_run
        self.admin = admin
        self.repo_root = Path(__file__).parent.parent

        # Configuration from environment
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.git_user_name = os.environ.get("GIT_USER_NAME", "")
        self.git_user_email = os.environ.get("GIT_USER_EMAIL", "")

        # Set up logging
        self._setup_logging()

        # Initialize git utilities
        self.git = GitUtils(logger=self.logger)

    def _setup_logging(self):
        """Configure logging based on debug setting."""
        log_level = logging.DEBUG if self.debug else logging.INFO
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=log_level, format=log_format, handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger(__name__)

    # Domain-specific utility methods

    def get_last_resource_name(self) -> str | None:
        """
        Get the display name of the most recently added resource by comparing
        the current CSV state with the HEAD version.

        This method finds the newly added resource by:
        1. Getting the current (working) version of the CSV
        2. Getting the HEAD (committed) version of the CSV
        3. Comparing to find rows that exist in current but not in HEAD

        Returns:
            Display name of the newly added resource or None if no new resource found
        """
        csv_path = self.repo_root / "THE_RESOURCES_TABLE.csv"
        csv_relative = csv_path.relative_to(self.repo_root)

        if not csv_path.exists():
            self.logger.error(f"CSV file not found: {csv_path}")
            return None

        try:
            # Get the HEAD version of the CSV
            head_csv_result = subprocess.run(
                ["git", "show", f"HEAD:{csv_relative}"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if head_csv_result.returncode != 0:
                # File might be new or not in HEAD
                self.logger.debug("CSV file not found in HEAD, treating all rows as new")
                head_rows = []
            else:
                # Parse HEAD version
                import io

                head_reader = csv.DictReader(io.StringIO(head_csv_result.stdout))
                head_rows = list(head_reader)

            # Get current version
            with open(csv_path, encoding="utf-8") as f:
                current_reader = csv.DictReader(f)
                current_rows = list(current_reader)

            if not current_rows:
                return None

            # Find rows that are in current but not in HEAD
            # Use ID field for comparison as it should be unique
            head_ids = {row.get("ID") for row in head_rows if row.get("ID")}
            new_rows = [row for row in current_rows if row.get("ID") not in head_ids]

            if new_rows:
                # Return the Display Name of the first new row
                # (typically there should only be one new row)
                return new_rows[0].get("Display Name")
            else:
                # No new rows found, fall back to last row
                # This handles edge cases where git history might be different
                self.logger.debug("No new rows found via diff, using last row")
                return current_rows[-1].get("Display Name")

        except Exception as e:
            self.logger.error(f"Error getting last resource name: {e}")
            return None

    def slugify(self, text: str) -> str:
        """
        Convert text to a URL-safe slug.

        Args:
            text: Text to convert

        Returns:
            URL-safe slug
        """
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        # Collapse multiple hyphens
        slug = re.sub(r"-+", "-", slug)
        return slug

    def get_remote_type(self, remote_name: str = "origin") -> str | None:
        """
        Detect whether a git remote uses SSH or HTTPS.

        Args:
            remote_name: Name of the remote to check

        Returns:
            "ssh" or "https" or None if remote doesn't exist
        """
        return self.git.get_remote_type(remote_name)

    def prompt_with_default(self, prompt: str, default: str = "") -> str:
        """
        Prompt user for input with an optional default value.

        Args:
            prompt: The prompt to display
            default: Default value if user presses enter

        Returns:
            User input or default value
        """
        prompt_text = f"{prompt} [{default}]: " if default else f"{prompt}: "

        user_input = input(prompt_text).strip()
        return user_input if user_input else default

    def install_git_hooks(self) -> bool:
        """
        Install git hooks for the repository.

        Returns:
            True if hooks were installed successfully, False otherwise
        """
        try:
            hooks_dir = self.repo_root / "hooks"
            git_hooks_dir = self.repo_root / ".git" / "hooks"

            # Check if pre-push hook exists in the hooks directory
            pre_push_source = hooks_dir / "pre-push"
            if pre_push_source.exists():
                pre_push_dest = git_hooks_dir / "pre-push"

                # Copy the hook
                import shutil

                shutil.copy2(pre_push_source, pre_push_dest)

                # Make it executable
                os.chmod(pre_push_dest, 0o755)

                self.logger.info("✓ Pre-push hook installed successfully")
                return True
            else:
                self.logger.debug("Pre-push hook not found in hooks directory")
                return True  # Not a failure, just nothing to install

        except Exception as e:
            self.logger.error(f"Failed to install git hooks: {e}")
            return False

    def check_prerequisites(self) -> bool:
        """
        Check all prerequisites before starting the workflow.

        Returns:
            True if all checks pass, False otherwise
        """
        self.logger.info("Checking prerequisites...")
        all_passed = True

        # Check git installation
        if not self.git.is_git_installed():
            self.logger.error("Git is not installed")
            self.logger.info("Setup hint: Install git from https://git-scm.com/downloads")
            all_passed = False
        else:
            self.logger.debug("✓ Git is installed")

        # Check gh CLI installation
        if not self.git.is_gh_installed():
            self.logger.error("GitHub CLI (gh) is not installed")
            self.logger.info("Setup hint: Install gh from https://cli.github.com/")
            all_passed = False
        else:
            self.logger.debug("✓ GitHub CLI is installed")

        # Check gh authentication status
        if not self.git.is_gh_authenticated():
            self.logger.error("GitHub CLI is not authenticated")
            self.logger.info("Setup hint: Run 'gh auth login' to authenticate")
            all_passed = False
        else:
            self.logger.debug("✓ GitHub CLI is authenticated")

        # Check git user configuration
        git_name = self.git.get_git_config("user.name")
        git_email = self.git.get_git_config("user.email")

        if not git_name:
            self.logger.error("Git user.name is not configured")
            self.logger.info("Setup hint: Run 'git config --global user.name \"Your Name\"'")
            all_passed = False
        else:
            self.logger.debug(f"✓ Git user.name is configured: {git_name}")

        if not git_email:
            self.logger.error("Git user.email is not configured")
            self.logger.info("Setup hint: Run 'git config --global user.email \"your@email.com\"'")
            all_passed = False
        else:
            self.logger.debug(f"✓ Git user.email is configured: {git_email}")

        # Check origin remote exists
        if not self.git.check_remote_exists("origin"):
            self.logger.error("Git remote 'origin' does not exist")
            self.logger.info(f"Setup hint: You need to fork {self.UPSTREAM_REPO} on GitHub first")
            self.logger.info("           Then clone your fork or add it as a remote")
            all_passed = False
        else:
            self.logger.debug("✓ Git remote 'origin' exists")

        # Check upstream remote exists and points to the correct repository (skip in admin mode)
        if not self.admin:
            if not self.git.check_remote_exists("upstream"):
                self.logger.error("Git remote 'upstream' does not exist")
                self.logger.info(f"Setup hint: Run 'git remote add upstream {self.UPSTREAM_URL}'")
                all_passed = False
            else:
                # Verify upstream points to the correct repository
                upstream_url = self.git.get_remote_url("upstream")
                if upstream_url and self.UPSTREAM_REPO not in upstream_url:
                    self.logger.warning(f"Upstream remote exists but points to: {upstream_url}")
                    self.logger.info(f"Expected: {self.UPSTREAM_URL}")
                else:
                    self.logger.debug("✓ Git remote 'upstream' points to correct repository")

                    # Check that origin and upstream don't point to the same repository
                    origin_url = self.git.get_remote_url("origin")
                    if origin_url and upstream_url:
                        # Normalize URLs for comparison
                        # (remove protocol differences and .git suffix)
                        origin_normalized = (
                            origin_url.replace("git@github.com:", "github.com/")
                            .replace("https://", "")
                            .replace("http://", "")
                            .rstrip(".git")
                        )
                        upstream_normalized = (
                            upstream_url.replace("git@github.com:", "github.com/")
                            .replace("https://", "")
                            .replace("http://", "")
                            .rstrip(".git")
                        )

                        if origin_normalized == upstream_normalized:
                            self.logger.error(
                                "Origin and upstream remotes point to the same repository"
                            )
                            self.logger.info("This workflow requires a fork-based setup:")
                            self.logger.info("  1. Fork the repository on GitHub")
                            self.logger.info("  2. Clone your fork (this becomes 'origin')")
                            self.logger.info("  3. Add the original repository as 'upstream'")
                            self.logger.info(
                                "\nIf you're the repository owner and want to use this workflow:"
                            )
                            self.logger.info(
                                "  Use the --admin flag to submit directly to upstream"
                            )
                            all_passed = False
        else:
            self.logger.info("Admin mode: Skipping upstream remote check")
            self.logger.debug("✓ Admin mode works directly with origin repository")

            # Verify origin points to the expected repository in admin mode
            origin_url = self.git.get_remote_url("origin")
            if origin_url and self.UPSTREAM_REPO not in origin_url:
                self.logger.error(f"In admin mode, origin must point to {self.UPSTREAM_REPO}")
                self.logger.info(f"Current origin: {origin_url}")
                all_passed = False
            else:
                self.logger.debug(f"✓ Origin points to correct repository: {self.UPSTREAM_REPO}")

        # Check working directory is clean
        if not self.git.is_working_directory_clean():
            self.logger.error("Working directory has uncommitted changes")
            self.logger.info("Setup hint: Commit or stash your changes before proceeding")
            self.logger.info(
                "           Run 'git status' to see what needs to be committed or stashed"
            )
            uncommitted = self.git.get_uncommitted_files()
            if uncommitted:
                self.logger.debug(f"Changed files:\n{uncommitted}")
            all_passed = False
        else:
            self.logger.debug("✓ Working directory is clean")

        if all_passed:
            self.logger.info("✅ All prerequisites checks passed")
        else:
            self.logger.error(
                "❌ Some prerequisite checks failed. Please fix the issues above and try again."
            )

        return all_passed

    def run_add_resource(self) -> bool:
        """
        Run the add_resource.py script to collect resource information.

        Returns:
            True if resource was successfully added, False if cancelled or failed
        """
        self.logger.info("Starting resource collection...")

        # Path to add_resource.py
        add_resource_script = self.repo_root / "scripts" / "add_resource.py"

        if not add_resource_script.exists():
            self.logger.error(f"add_resource.py not found at {add_resource_script}")
            return False

        # Check if CSV was modified before running add_resource
        csv_file = self.repo_root / "THE_RESOURCES_TABLE.csv"
        was_modified_before = self.git.check_file_modified(csv_file, cwd=self.repo_root)

        try:
            # Run add_resource.py interactively
            # Using sys.executable ensures we use the same Python interpreter
            result = subprocess.run(
                [sys.executable, str(add_resource_script)],
                cwd=self.repo_root,
                check=False,  # Don't raise exception on non-zero exit
            )

            # Check return status
            if result.returncode != 0:
                # User cancelled or error occurred
                self.logger.info("Resource addition was cancelled or failed")
                return False

            # Check if .pr_template_content.md was created
            pr_template_file = self.repo_root / ".pr_template_content.md"
            if not pr_template_file.exists():
                self.logger.error("PR template content file was not created")
                return False

            # Verify CSV was actually modified
            was_modified_after = self.git.check_file_modified(csv_file, cwd=self.repo_root)
            if not was_modified_before and not was_modified_after:
                self.logger.warning("CSV file was not modified - resource may be duplicate")
                # This is just a warning, not a failure

            # Stage the CSV file
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would stage {csv_file}")
            else:
                if not self.git.stage_file(csv_file, cwd=self.repo_root):
                    self.logger.error("Failed to stage CSV file")
                    return False
                self.logger.debug(f"Staged {csv_file}")

            self.logger.info("✅ Resource successfully added and CSV staged")
            return True

        except Exception as e:
            self.logger.error(f"Error running add_resource.py: {e}")
            return False

    def generate_readme(self) -> bool:
        """
        Generate README.md from THE_RESOURCES_TABLE.csv using make generate.

        Returns:
            True if README was successfully generated, False otherwise
        """
        self.logger.info("Generating README from CSV...")

        try:
            # Run make generate
            if self.dry_run:
                self.logger.info("[DRY RUN] Would run 'make generate'")
                return True

            # Run the make generate command
            result = subprocess.run(
                ["make", "generate"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            # Check if the command succeeded
            if result.returncode != 0:
                self.logger.error("Failed to generate README")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
                return False

            # Log the output
            if result.stdout:
                self.logger.debug(f"Generation output:\n{result.stdout}")

            # Check if README.md was modified
            readme_file = self.repo_root / "README.md"
            if self.git.check_file_modified(readme_file, cwd=self.repo_root):
                # Stage the README.md file
                if not self.git.stage_file(readme_file, cwd=self.repo_root):
                    self.logger.error("Failed to stage README.md")
                    return False
                self.logger.info("✅ README.md generated and staged")

                # Show what was modified using git diff --stat
                try:
                    stat_result = subprocess.run(
                        ["git", "diff", "--cached", "--stat", str(readme_file.name)],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if stat_result.returncode == 0 and stat_result.stdout:
                        # Extract the statistics from git diff --stat output
                        stat_lines = stat_result.stdout.strip().split("\n")
                        if stat_lines:
                            # The last line contains the summary
                            self.logger.info(f"README.md modified: {stat_lines[-1].strip()}")
                except Exception as e:
                    self.logger.debug(f"Could not get diff statistics: {e}")
            else:
                self.logger.info("README.md was not modified (no changes needed)")

            return True

        except FileNotFoundError:
            self.logger.error("'make' command not found. Please ensure Make is installed.")
            return False
        except Exception as e:
            self.logger.error(f"Error generating README: {e}")
            return False

    def review_changes(self) -> bool:
        """
        Show staged changes and prompt user to review them.

        Provides options to:
        - Continue (Y/Enter)
        - View full diff (v)
        - Cancel submission (n)
        - Unstage and edit files

        Returns:
            True if user approves changes, False if cancelled
        """
        self.logger.info("Reviewing staged changes...")

        # Show summary of staged changes
        try:
            # Get staged files summary using git diff --cached --stat
            stat_result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if stat_result.returncode != 0:
                self.logger.error("Failed to get staged changes summary")
                return False

            if not stat_result.stdout.strip():
                self.logger.warning("No staged changes found")
                return False

            # Display the summary
            print("\n📋 Staged changes summary:")
            print("-" * 50)
            print(stat_result.stdout)

            # Interactive review loop
            while True:
                print("\nOptions:")
                print("  [Y/Enter] - Continue with these changes")
                print("  [v]       - View full diff")
                print("  [n]       - Cancel submission")
                print("  [u]       - Unstage files and edit")

                choice = input("\nYour choice: ").strip().lower()

                if choice in ("", "y"):
                    # User approves, continue
                    self.logger.info("Changes approved by user")
                    return True

                elif choice == "v":
                    # Show full diff
                    print("\n📄 Full diff of staged changes:")
                    print("=" * 70)

                    diff_result = subprocess.run(
                        ["git", "diff", "--cached"],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if diff_result.returncode == 0:
                        # Print the diff with some basic pagination for very long diffs
                        diff_lines = diff_result.stdout.splitlines()
                        if len(diff_lines) > 50:
                            # For long diffs, show in chunks
                            for i in range(0, len(diff_lines), 40):
                                chunk = "\n".join(diff_lines[i : i + 40])
                                print(chunk)
                                if i + 40 < len(diff_lines):
                                    cont = input(
                                        "\n--- Press Enter to continue or 'q' to return to menu ---"
                                    )
                                    if cont.lower() == "q":
                                        break
                        else:
                            print(diff_result.stdout)
                    else:
                        self.logger.error("Failed to get full diff")

                    print("=" * 70)
                    # Loop back to menu

                elif choice == "n":
                    # User cancels
                    self.logger.info("Submission cancelled by user")
                    return False

                elif choice == "u":
                    # Unstage files for editing
                    print("\n🔧 Unstaging files for editing...")

                    # Get list of staged files
                    staged_files_result = subprocess.run(
                        ["git", "diff", "--cached", "--name-only"],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if staged_files_result.returncode == 0 and staged_files_result.stdout:
                        staged_files = staged_files_result.stdout.strip().split("\n")

                        # Unstage all files
                        unstage_result = subprocess.run(
                            ["git", "reset", "HEAD", "--"] + staged_files,
                            cwd=self.repo_root,
                            capture_output=True,
                            text=True,
                            check=False,
                        )

                        if unstage_result.returncode == 0:
                            print(f"\n✅ Unstaged {len(staged_files)} file(s):")
                            for file in staged_files:
                                print(f"   - {file}")
                            print("\nYou can now edit these files manually.")
                            print(
                                "When done, run this script again to continue "
                                "the submission process."
                            )
                            return False
                        else:
                            self.logger.error("Failed to unstage files")
                            if unstage_result.stderr:
                                self.logger.error(f"Error: {unstage_result.stderr}")
                    else:
                        self.logger.error("Failed to get list of staged files")

                else:
                    print(f"Invalid option '{choice}'. Please choose Y, v, n, or u.")

        except Exception as e:
            self.logger.error(f"Error during change review: {e}")
            return False

    def create_branch(self) -> str | None:
        """
        Create a new feature branch for the resource submission.

        Branch naming pattern: add-resource-[slugified-name]-[timestamp]
        Example: add-resource-claude-mcp-server-20250115-1234

        Returns:
            Branch name if successfully created, None if failed
        """
        self.logger.info("Creating feature branch...")

        try:
            # Get the resource name from the most recently added entry
            resource_name = self.get_last_resource_name()
            if not resource_name:
                self.logger.warning("Could not determine resource name, using generic name")
                resource_name = "new-resource"

            # Generate branch name components
            from datetime import datetime

            # Slugify the resource name
            slug = self.slugify(resource_name)
            if len(slug) > 50:  # Limit slug length for reasonable branch names
                slug = slug[:50].rstrip("-")

            # Generate timestamp (YYYYMMDD-HHMM format)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")

            # Construct branch name
            branch_name = f"add-resource-{slug}-{timestamp}"

            # Check if branch already exists
            check_result = subprocess.run(
                ["git", "rev-parse", "--verify", branch_name],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if check_result.returncode == 0:
                # Branch already exists, add a counter
                counter = 2
                while True:
                    alt_branch_name = f"{branch_name}-{counter}"
                    check_alt = subprocess.run(
                        ["git", "rev-parse", "--verify", alt_branch_name],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if check_alt.returncode != 0:
                        branch_name = alt_branch_name
                        break
                    counter += 1
                    if counter > 10:  # Safety limit
                        self.logger.error("Too many similar branch names exist")
                        return None

            # Create and checkout the new branch
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create and checkout branch: {branch_name}")
                return branch_name

            create_result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if create_result.returncode != 0:
                self.logger.error(f"Failed to create branch: {branch_name}")
                if create_result.stderr:
                    self.logger.error(f"Error: {create_result.stderr}")
                return None

            # Show branch name to user
            self.logger.info(f"✅ Created and switched to branch: {branch_name}")

            # Verify we're on the new branch
            current_branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if current_branch_result.returncode == 0:
                current = current_branch_result.stdout.strip()
                if current != branch_name:
                    self.logger.warning(f"Expected to be on {branch_name} but on {current}")

            return branch_name

        except Exception as e:
            self.logger.error(f"Error creating branch: {e}")
            return None

    def commit_changes(self) -> bool:
        """
        Commit the staged changes with an appropriate commit message.

        The method:
        1. Generates a commit message from resource info
        2. Shows the commit message to the user
        3. Allows editing the commit message
        4. Creates the commit with the message
        5. Handles commit failures gracefully

        Returns:
            True if commit was successful, False otherwise
        """
        self.logger.info("Committing changes...")

        try:
            # Generate commit message from resource info
            resource_name = self.get_last_resource_name()
            if not resource_name:
                self.logger.warning("Could not determine resource name for commit message")
                resource_name = "new resource"

            # Use standard format: "Add new resource: {name}"
            default_message = f"Add new resource: {resource_name}"

            # Show commit message to user
            print("\n📝 Proposed commit message:")
            print(f"   {default_message}")

            # Allow editing commit message
            print("\nOptions:")
            print("  [Enter] - Use this message")
            print("  [e]     - Edit the message")
            print("  [c]     - Cancel commit")

            choice = input("\nYour choice: ").strip().lower()

            if choice == "c":
                self.logger.info("Commit cancelled by user")
                return False

            commit_message = default_message

            if choice == "e":
                # Allow user to edit the message
                print("\nEnter your commit message (or press Enter to keep default):")
                edited_message = input("> ").strip()
                if edited_message:
                    commit_message = edited_message
                else:
                    # User pressed enter without typing, keep default
                    pass

            # Create commit with message
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would commit with message: {commit_message}")
                return True

            # Verify we have staged changes
            check_staged = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if check_staged.returncode == 0:
                self.logger.error("No staged changes to commit")
                return False

            # Create the commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            # Handle commit result
            if commit_result.returncode != 0:
                # Handle commit failures
                self.logger.error("Failed to create commit")
                if commit_result.stderr:
                    error_msg = commit_result.stderr.strip()
                    self.logger.error(f"Error: {error_msg}")

                    # Check for common errors
                    if "pre-commit" in error_msg.lower():
                        self.logger.info(
                            "\n💡 Pre-commit hooks failed. Attempting to handle automatically..."
                        )
                        # Try to handle pre-commit changes
                        if self.handle_precommit_changes(commit_message):
                            return True
                        else:
                            self.logger.error("Failed to handle pre-commit hook changes")
                            return False
                    elif "nothing to commit" in error_msg.lower():
                        self.logger.error("No changes to commit. Ensure files are staged.")
                        return False
                    elif "please tell me who you are" in error_msg.lower():
                        self.logger.error("Git user configuration is missing.")
                        self.logger.info('Run: git config --global user.name "Your Name"')
                        self.logger.info('Run: git config --global user.email "your@email.com"')
                        return False

                return False

            # Commit succeeded
            if commit_result.stdout:
                # Extract commit info from output
                output_lines = commit_result.stdout.strip().split("\n")
                if output_lines:
                    # First line typically contains branch and commit summary
                    self.logger.info(f"✅ {output_lines[0]}")

                # Show files committed
                for line in output_lines[1:]:
                    line = line.strip()
                    if line and (
                        line.endswith("changed")
                        or line.endswith("insertion(+)")
                        or line.endswith("deletion(-)")
                    ):
                        self.logger.info(f"   {line}")

            # Get the commit hash for reference
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if hash_result.returncode == 0:
                commit_hash = hash_result.stdout.strip()[:7]  # Short hash
                self.logger.debug(f"Commit hash: {commit_hash}")

            return True

        except Exception as e:
            self.logger.error(f"Error during commit: {e}")
            return False

    def handle_precommit_changes(self, original_commit_message: str) -> bool:
        """
        Handle files modified by pre-commit hooks after a failed commit attempt.

        This method:
        1. Checks if working directory is dirty after commit
        2. Identifies which files were modified by pre-commit
        3. Shows user what pre-commit changed
        4. Stages all pre-commit modifications
        5. Retries commit with the same message
        6. Confirms commit succeeded

        Args:
            original_commit_message: The commit message from the failed attempt

        Returns:
            True if pre-commit changes were handled and commit succeeded, False otherwise
        """
        self.logger.info("Handling pre-commit hook changes...")

        try:
            # Check if working directory is dirty after commit
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if status_result.returncode != 0:
                self.logger.error("Failed to check git status")
                return False

            if not status_result.stdout.strip():
                # No changes, nothing to handle
                self.logger.debug("No pre-commit changes detected")
                return False

            # Identify which files were modified by pre-commit
            modified_files = []
            for line in status_result.stdout.strip().split("\n"):
                if line:
                    # Status format: "XY filename" where X=index, Y=worktree
                    # " M filename" = modified in worktree
                    # "M  filename" = modified in index
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        status_code, filename = parts
                        if "M" in status_code:
                            modified_files.append(filename)

            if not modified_files:
                self.logger.debug("No modified files found")
                return False

            # Show user what pre-commit changed
            print("\n🔧 Pre-commit hooks modified the following files:")
            for file in modified_files:
                print(f"   - {file}")

            print("\n📋 Changes made by pre-commit hooks:")
            # Show diff for each file
            for file in modified_files:
                diff_result = subprocess.run(
                    ["git", "diff", "--", file],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if diff_result.returncode == 0 and diff_result.stdout:
                    print(f"\n{file}:")
                    # Show first few lines of diff
                    diff_lines = diff_result.stdout.strip().split("\n")
                    for line in diff_lines[:10]:  # Show first 10 lines
                        print(f"  {line}")
                    if len(diff_lines) > 10:
                        print(f"  ... ({len(diff_lines) - 10} more lines)")

            print("\n✅ These changes will be automatically included in your commit.")

            if self.dry_run:
                self.logger.info("[DRY RUN] Would stage pre-commit changes and retry commit")
                return True

            # Stage all pre-commit modifications
            self.logger.info("Staging pre-commit hook changes...")
            stage_result = subprocess.run(
                ["git", "add", "-A"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if stage_result.returncode != 0:
                self.logger.error("Failed to stage pre-commit changes")
                if stage_result.stderr:
                    self.logger.error(f"Error: {stage_result.stderr}")
                return False

            # Retry commit with the same message
            self.logger.info("Retrying commit with pre-commit changes...")
            retry_result = subprocess.run(
                ["git", "commit", "-m", original_commit_message],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            # Confirm commit succeeded
            if retry_result.returncode != 0:
                self.logger.error("Failed to commit after staging pre-commit changes")
                if retry_result.stderr:
                    self.logger.error(f"Error: {retry_result.stderr}")
                return False

            # Extract commit info
            if retry_result.stdout:
                output_lines = retry_result.stdout.strip().split("\n")
                if output_lines:
                    self.logger.info(f"✅ {output_lines[0]}")

            # Get the commit hash for reference
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if hash_result.returncode == 0:
                commit_hash = hash_result.stdout.strip()[:7]
                self.logger.info(f"✅ Commit successful with pre-commit changes: {commit_hash}")

            return True

        except Exception as e:
            self.logger.error(f"Error handling pre-commit changes: {e}")
            return False

    def push_to_fork(self) -> bool:
        """
        Push the current branch to origin.

        This method:
        1. Detects remote URL type (SSH vs HTTPS)
        2. Attempts push with -u flag to set upstream tracking
        3. Catches authentication failures
        4. Provides specific help for SSH issues
        5. Provides specific help for HTTPS/credential issues
        6. Shows push progress to user
        7. Confirms successful push

        Returns:
            True if push was successful, False otherwise
        """
        if self.admin:
            self.logger.info("Pushing to origin repository (admin mode)...")
        else:
            self.logger.info("Pushing to fork...")

        try:
            # Get current branch name
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if branch_result.returncode != 0 or not branch_result.stdout.strip():
                self.logger.error("Failed to get current branch name")
                return False

            branch_name = branch_result.stdout.strip()
            self.logger.debug(f"Current branch: {branch_name}")

            # Always push to origin
            remote_name = "origin"

            # Detect remote URL type (SSH vs HTTPS)
            remote_type = self.get_remote_type(remote_name)
            if not remote_type:
                self.logger.error(f"Could not determine remote type for '{remote_name}'")
                return False

            self.logger.debug(f"Remote type: {remote_type}")

            # Show push progress to user
            print(f"\n🚀 Pushing branch '{branch_name}' to {remote_name}...")
            if self.admin:
                print("   Mode: Admin (direct to main repository)")
            print(f"   Remote type: {remote_type.upper()}")

            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would push branch '{branch_name}' to {remote_name}")
                return True

            # Attempt push with -u flag
            push_result = subprocess.run(
                ["git", "push", "-u", remote_name, branch_name],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            # Check result
            if push_result.returncode == 0:
                # Confirm successful push
                self.logger.info("✅ Push successful!")

                # Show output
                if push_result.stderr:  # Git outputs progress to stderr
                    output_lines = push_result.stderr.strip().split("\n")
                    for line in output_lines:
                        if "->>" in line or "Writing objects" in line or "remote:" in line:
                            self.logger.info(f"   {line}")

                # Get remote URL for display
                remote_url = self.git.get_remote_url(remote_name)
                if remote_url:
                    # Convert SSH URL to HTTPS for display
                    if remote_url.startswith("git@github.com:"):
                        https_url = remote_url.replace("git@github.com:", "https://github.com/")
                        https_url = https_url.replace(".git", "")
                        print(f"\n🔗 Branch pushed to: {https_url}/tree/{branch_name}")
                    elif remote_url.startswith("https://"):
                        https_url = remote_url.replace(".git", "")
                        print(f"\n🔗 Branch pushed to: {https_url}/tree/{branch_name}")

                return True

            else:
                # Catch authentication failures
                error_output = push_result.stderr.lower() if push_result.stderr else ""
                self.logger.error("Push failed")

                if (
                    "authentication" in error_output
                    or "permission" in error_output
                    or "could not read" in error_output
                ):
                    # Authentication failure
                    print("\n❌ Push failed due to authentication issues")

                    if remote_type == "ssh":
                        # Provide specific help for SSH issues
                        print("\n🔑 SSH Authentication Help:")
                        print("1. Check if your SSH key is added to ssh-agent:")
                        print("   ssh-add -l")
                        print("\n2. If not listed, add your key:")
                        print("   ssh-add ~/.ssh/id_rsa  # or your key path")
                        print("\n3. Test GitHub SSH connection:")
                        print("   ssh -T git@github.com")
                        print("\n4. Ensure your SSH key is added to your GitHub account:")
                        print("   https://github.com/settings/keys")
                        print("\n5. If using a non-default key, configure SSH:")
                        print("   Edit ~/.ssh/config and add:")
                        print("   Host github.com")
                        print("     IdentityFile ~/.ssh/your_key")

                    else:  # HTTPS
                        # Provide specific help for HTTPS/credential issues
                        print("\n🔐 HTTPS Authentication Help:")
                        print("1. GitHub now requires personal access tokens instead of passwords")
                        print("\n2. Create a personal access token:")
                        print("   https://github.com/settings/tokens/new")
                        print("   - Select 'repo' scope for full repository access")
                        print("\n3. Use the token as your password when prompted")
                        print("\n4. To store credentials (recommended):")
                        print("   git config --global credential.helper cache")
                        print("   # Or use your system's credential manager:")
                        print("   # macOS: git config --global credential.helper osxkeychain")
                        print("   # Windows: git config --global credential.helper wincred")
                        print("\n5. Alternatively, use GitHub CLI for authentication:")
                        print("   gh auth login")

                elif "rejected" in error_output or "failed to push" in error_output:
                    # Other push failures
                    print("\n❌ Push failed")
                    if push_result.stderr:
                        print(f"Error: {push_result.stderr}")
                    print("\nPossible issues:")
                    print("- The branch might already exist on the remote")
                    print("- You might not have write access to the repository")
                    print("- The remote repository might have branch protection rules")

                else:
                    # Unknown error
                    print("\n❌ Push failed with unknown error")
                    if push_result.stderr:
                        print(f"Error output:\n{push_result.stderr}")

                return False

        except Exception as e:
            self.logger.error(f"Error during push: {e}")
            return False

    def create_pull_request(self) -> str | None:
        """
        Create a pull request using GitHub CLI.

        This method:
        1. Gets GitHub username via gh CLI
        2. Reads PR template content from file
        3. Constructs PR title from resource name
        4. Sets correct base branch (main)
        5. Sets correct head (username:branch)
        6. Creates PR with gh CLI
        7. Captures PR URL from output
        8. Handles PR creation failures
        9. Saves PR URL for final display

        Returns:
            PR URL if successful, None if failed
        """
        self.logger.info("Creating pull request...")

        try:
            # Get GitHub username via gh CLI
            self.logger.debug("Getting GitHub username...")
            username_result = subprocess.run(
                ["gh", "api", "user", "-q", ".login"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if username_result.returncode != 0:
                self.logger.error("Failed to get GitHub username")
                if username_result.stderr:
                    self.logger.error(f"Error: {username_result.stderr}")
                print("\n❌ Could not determine GitHub username")
                print("Make sure you're authenticated with GitHub CLI:")
                print("  gh auth login")
                return None

            github_username = username_result.stdout.strip()
            if not github_username:
                self.logger.error("GitHub username is empty")
                return None

            self.logger.info(f"GitHub username: {github_username}")

            # Read PR template content from file
            pr_template_content = ""
            pr_content_file = self.repo_root / ".pr_template_content.md"

            if pr_content_file.exists():
                self.logger.debug("Reading PR template content from .pr_template_content.md")
                with open(pr_content_file, encoding="utf-8") as f:
                    pr_template_content = f.read().strip()
            else:
                self.logger.warning("No .pr_template_content.md found, will use minimal PR body")

            # Construct PR title from resource name
            resource_name = self.get_last_resource_name()
            if not resource_name:
                self.logger.warning("Could not determine resource name for PR title")
                resource_name = "new resource"

            pr_title = f"Add new resource: {resource_name}"

            # Get current branch name
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if branch_result.returncode != 0 or not branch_result.stdout.strip():
                self.logger.error("Failed to get current branch name")
                return None

            current_branch = branch_result.stdout.strip()

            # Set correct base branch (main) and head
            base_branch = "main"
            # In admin mode, head is just the branch name; in fork mode, it's username:branch
            head_branch = current_branch if self.admin else f"{github_username}:{current_branch}"

            # Prepare PR body
            if pr_template_content:
                # Use the pre-filled content from add_resource.py
                pr_body = f"""# Pull Request

<!-- IMPORTANT: Submit only ONE resource per pull request. -->
<!-- If you have multiple resources, please create separate PRs. -->

## Type of Contribution

- [x] **New Resource** - Adding a new resource to the list (ONE per PR)
- [ ] **Update Resource** - Updating existing resource information (e.g., broken link, license info)
- [ ] **Repository Improvement** - Improving the repository itself (not adding resources)

---

## For New Resources

{pr_template_content}"""
            else:
                # Minimal PR body if no template content
                pr_body = f"""# Pull Request

## Type of Contribution

- [x] **New Resource** - Adding a new resource to the list

## Resource Information

- **Display Name**: {resource_name}
- **Description**: New resource added via submit_resource.py

## Checklist

- [x] Used automated submission workflow
- [x] Link verified
- [x] README generated"""

            # Show PR details to user
            print("\n📝 Pull Request Details:")
            print(f"   Title: {pr_title}")
            print(f"   Base: {base_branch}")
            print(f"   Head: {head_branch}")
            if self.admin:
                print("   Mode: Admin (same repository)")
            print(f"   Repository: {self.UPSTREAM_REPO}")

            if self.dry_run:
                self.logger.info("[DRY RUN] Would create PR with gh CLI")
                return "https://github.com/example/pr-url-dry-run"

            # Create PR with gh CLI
            self.logger.info("Creating PR with gh CLI...")

            # Write PR body to temporary file to handle complex content
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
                tmp.write(pr_body)
                tmp_path = tmp.name

            try:
                pr_result = subprocess.run(
                    [
                        "gh",
                        "pr",
                        "create",
                        "--repo",
                        self.UPSTREAM_REPO,
                        "--base",
                        base_branch,
                        "--head",
                        head_branch,
                        "--title",
                        pr_title,
                        "--body-file",
                        tmp_path,
                    ],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

            # Handle PR creation result
            if pr_result.returncode != 0:
                self.logger.error("Failed to create pull request")
                error_output = pr_result.stderr.strip() if pr_result.stderr else ""

                # Handle PR creation failures
                if "already exists" in error_output:
                    print("\n⚠️  A pull request already exists for this branch")
                    # Try to get existing PR URL
                    existing_pr_result = subprocess.run(
                        ["gh", "pr", "view", "--json", "url", "-q", ".url"],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if existing_pr_result.returncode == 0 and existing_pr_result.stdout.strip():
                        pr_url = existing_pr_result.stdout.strip()
                        print(f"   Existing PR: {pr_url}")
                        return pr_url
                elif "no commits between" in error_output:
                    print("\n❌ No commits between base and head branches")
                    print("   Make sure you've committed and pushed your changes")
                elif (
                    "authentication" in error_output.lower() or "permission" in error_output.lower()
                ):
                    print("\n❌ Authentication or permission error")
                    print("   Make sure you're authenticated: gh auth login")
                    print("   And that you have forked the repository")
                else:
                    print(f"\n❌ PR creation failed: {error_output}")

                return None

            # Capture PR URL from output
            pr_url = pr_result.stdout.strip()
            if not pr_url or not pr_url.startswith("http"):
                self.logger.error(f"Invalid PR URL returned: {pr_url}")
                return None

            # Save PR URL for final display
            self.logger.info(f"✅ Pull request created: {pr_url}")
            print("\n✅ Pull request created successfully!")
            print(f"   URL: {pr_url}")

            # Clean up the .pr_template_content.md file after successful PR creation
            if pr_content_file.exists():
                self.logger.debug("Cleaning up .pr_template_content.md")
                pr_content_file.unlink()

            return pr_url

        except Exception as e:
            self.logger.error(f"Error creating pull request: {e}")
            return None

    def show_success(self, pr_url: str) -> None:
        """
        Display success message with final information.

        This method:
        1. Displays success message with emoji
        2. Shows PR URL prominently
        3. Lists next steps for user
        4. Opens PR in browser (if configured)
        5. Thanks user for contribution
        6. Cleans up temporary files

        Args:
            pr_url: The URL of the created pull request
        """
        # Display success message with emoji
        print("\n🎉 Resource submission complete!")
        print("✨ Congratulations! Your contribution is on its way! ✨")

        # Show PR URL prominently
        print("\n" + "=" * 60)
        print("📍 PULL REQUEST CREATED")
        print("=" * 60)
        print(f"🔗 {pr_url}")
        print("=" * 60)

        # List next steps for user
        print("\n📋 Next Steps:")
        print("   1. ⏳ Wait for review from maintainers")
        print("   2. 💬 Address any feedback if requested")
        print("   3. ✅ Your resource will be merged once approved!")
        print("\n💡 Pro Tips:")
        print("   • Watch your PR for notifications")
        print("   • Be responsive to maintainer feedback")
        print("   • Join the discussion if questions arise")

        # Open PR in browser (if configured)
        try:
            # Check if we should open in browser (gh config)
            browser_check = subprocess.run(
                ["gh", "config", "get", "browser"], capture_output=True, text=True, check=False
            )

            # If browser is configured and not empty, try to open
            if browser_check.returncode == 0 and browser_check.stdout.strip():
                print("\n🌐 Opening PR in browser...")
                open_result = subprocess.run(
                    ["gh", "pr", "view", pr_url, "--web"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if open_result.returncode == 0:
                    self.logger.debug("Opened PR in browser")
                else:
                    self.logger.debug("Could not open PR in browser")
            else:
                # Offer to open manually
                print("\n💡 To view your PR in the browser, run:")
                print(f"   gh pr view {pr_url} --web")
        except Exception as e:
            self.logger.debug(f"Could not check browser config: {e}")

        # Thank user for contribution
        print("\n🙏 Thank you for contributing to awesome-claude-code!")
        print("   Your contribution helps the entire Claude Code community.")
        print("   Together we're building an amazing resource collection! 🚀")

        # Clean up temporary files
        self.logger.info("Cleaning up temporary files...")

        # Clean up .pr_template_content.md if it still exists
        pr_content_file = self.repo_root / ".pr_template_content.md"
        if pr_content_file.exists():
            try:
                pr_content_file.unlink()
                self.logger.debug("Cleaned up .pr_template_content.md")
            except Exception as e:
                self.logger.debug(f"Could not clean up PR template file: {e}")

        # Check for any other temporary files that might need cleanup
        temp_files = [".pr_template_content.md.tmp", ".submission_temp.md"]

        for temp_file in temp_files:
            temp_path = self.repo_root / temp_file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                    self.logger.debug(f"Cleaned up {temp_file}")
                except Exception as e:
                    self.logger.debug(f"Could not clean up {temp_file}: {e}")

        # Final spacing for clean output
        print()

    def run(self) -> int:
        """
        Execute the submission workflow.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            self.logger.info("Starting resource submission workflow")

            if self.dry_run:
                self.logger.info("DRY RUN MODE - No changes will be made")

            # Check prerequisites
            if not self.check_prerequisites():
                return 1

            # Install git hooks
            self.logger.info("Installing git hooks...")
            self.install_git_hooks()

            # Run add_resource to collect resource information
            if not self.run_add_resource():
                self.logger.info("Resource submission cancelled or failed")
                return 1

            # Generate README from CSV
            if not self.generate_readme():
                self.logger.error("Failed to generate README")
                return 1

            # Review staged changes
            if not self.review_changes():
                self.logger.info("Changes review cancelled by user")
                return 1

            # Create feature branch
            branch_name = self.create_branch()
            if not branch_name:
                self.logger.error("Failed to create feature branch")
                return 1

            # Commit changes
            if not self.commit_changes():
                self.logger.error("Failed to commit changes")
                return 1

            # Push branch to fork
            if not self.push_to_fork():
                self.logger.error("Failed to push branch to fork")
                return 1

            # Create pull request
            pr_url = self.create_pull_request()
            if not pr_url:
                self.logger.error("Failed to create pull request")
                print("\n💡 You can still create a PR manually:")
                print(f"   Visit: https://github.com/{self.UPSTREAM_REPO}")
                print("   Click 'Compare & pull request' for your pushed branch")
                return 1

            # Show success message
            self.show_success(pr_url)

            self.logger.info("Resource submission workflow completed successfully")
            return 0

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}", exc_info=self.debug)
            return 1


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Submit a new resource to awesome-claude-code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --debug           # Run with debug logging
  %(prog)s --dry-run         # Preview changes without applying
  %(prog)s --admin           # Admin mode: submit directly to upstream
        """,
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument("--dry-run", action="store_true", help="Run without making actual changes")

    parser.add_argument(
        "--admin", action="store_true", help="Admin mode: submit directly to upstream repository"
    )

    args = parser.parse_args()

    # Create and run submitter
    submitter = ResourceSubmitter(debug=args.debug, dry_run=args.dry_run, admin=args.admin)
    sys.exit(submitter.run())


if __name__ == "__main__":
    main()
