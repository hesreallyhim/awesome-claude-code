#!/usr/bin/env python3
"""End-to-end tests for the agent-deck.sh CLI tool.

These tests exercise the shell script functions in isolation using
subprocess calls, verifying that the CLI commands work correctly
without requiring tmux or network access.
"""

from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

from tests.conftest import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
AGENT_DECK = str(REPO_ROOT / "agent-deck.sh")


def run_bash(script: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Run a bash snippet that sources agent-deck.sh functions and executes commands.

    The script sources all function definitions from agent-deck.sh without
    calling ``main``, so tests can invoke individual functions in isolation.
    """
    merged_env = {**os.environ, **(env or {})}
    # Source the script but strip the final `main "$@"` invocation so it
    # doesn't enter the interactive loop.  We also disable set -e and stub
    # tmux so require_tmux doesn't exit.
    full_script = textwrap.dedent(f"""\
        # Stub tmux so require_tmux doesn't exit
        tmux() {{ :; }}
        export -f tmux
        # Source functions only: strip set -euo pipefail and the trailing main call
        eval "$(sed -e '/^set -euo pipefail$/d' -e '/^main "\\$@"$/d' "{AGENT_DECK}")"
        {script}
    """)
    return subprocess.run(
        ["bash", "-c", full_script],
        capture_output=True,
        text=True,
        env=merged_env,
        timeout=30,
    )


# ---------------------------------------------------------------------------
# Script Validity Tests
# ---------------------------------------------------------------------------


class TestScriptValidity:
    """Verify the shell script is syntactically valid."""

    def test_agent_deck_exists(self) -> None:
        assert Path(AGENT_DECK).exists(), "agent-deck.sh not found"

    def test_agent_deck_is_executable(self) -> None:
        assert os.access(AGENT_DECK, os.X_OK), "agent-deck.sh is not executable"

    def test_bash_syntax_check(self) -> None:
        """Verify the script passes bash syntax checking."""
        result = subprocess.run(
            ["bash", "-n", AGENT_DECK],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Syntax error in agent-deck.sh:\n{result.stderr}"

    def test_install_script_syntax_check(self) -> None:
        """Verify install.sh passes bash syntax checking."""
        install_sh = REPO_ROOT / "install.sh"
        if not install_sh.exists():
            pytest.skip("install.sh not found")
        result = subprocess.run(
            ["bash", "-n", str(install_sh)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Syntax error in install.sh:\n{result.stderr}"


# ---------------------------------------------------------------------------
# Project Detection Tests
# ---------------------------------------------------------------------------


class TestProjectDetection:
    """Test the detect_project function for various project types."""

    def test_detect_python_pyproject(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[tool]\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=python" in result.stdout

    def test_detect_python_requirements(self, tmp_path: Path) -> None:
        (tmp_path / "requirements.txt").write_text("flask\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=python" in result.stdout

    def test_detect_python_setup_py(self, tmp_path: Path) -> None:
        (tmp_path / "setup.py").write_text("from setuptools import setup\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=python" in result.stdout

    def test_detect_javascript(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text('{"name": "test"}')
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=javascript" in result.stdout

    def test_detect_rust(self, tmp_path: Path) -> None:
        (tmp_path / "Cargo.toml").write_text("[package]\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=rust" in result.stdout

    def test_detect_go(self, tmp_path: Path) -> None:
        (tmp_path / "go.mod").write_text("module test\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=go" in result.stdout

    def test_detect_java_maven(self, tmp_path: Path) -> None:
        (tmp_path / "pom.xml").write_text("<project></project>\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=java" in result.stdout

    def test_detect_java_gradle(self, tmp_path: Path) -> None:
        (tmp_path / "build.gradle").write_text("apply plugin: 'java'\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=java" in result.stdout

    def test_detect_ruby(self, tmp_path: Path) -> None:
        (tmp_path / "Gemfile").write_text("source 'https://rubygems.org'\n")
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=ruby" in result.stdout

    def test_detect_react_framework(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')
        result = run_bash(
            f'detect_project "{tmp_path}";'
            f' echo "FW=$DETECTED_FRAMEWORK DOMAIN=$DETECTED_DEFAULT_DOMAIN"'
        )
        assert "FW=react" in result.stdout
        assert "DOMAIN=4" in result.stdout

    def test_detect_fastapi_framework(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi"]\n')
        result = run_bash(
            f'detect_project "{tmp_path}";'
            f' echo "FW=$DETECTED_FRAMEWORK DOMAIN=$DETECTED_DEFAULT_DOMAIN"'
        )
        assert "FW=python-api" in result.stdout
        assert "DOMAIN=3" in result.stdout

    def test_detect_empty_directory(self, tmp_path: Path) -> None:
        result = run_bash(f'detect_project "{tmp_path}"; echo "LANG=$DETECTED_LANG"')
        assert "LANG=" in result.stdout  # empty lang


# ---------------------------------------------------------------------------
# Session Name Generation Tests
# ---------------------------------------------------------------------------


class TestSessionNameGeneration:
    """Test session_name_from_path function."""

    def test_simple_directory(self) -> None:
        result = run_bash('echo $(session_name_from_path "/home/user/myproject")')
        assert result.stdout.strip() == "deck-myproject"

    def test_uppercase_converted_to_lower(self) -> None:
        result = run_bash('echo $(session_name_from_path "/home/user/MyProject")')
        assert result.stdout.strip() == "deck-myproject"

    def test_dots_converted_to_dashes(self) -> None:
        result = run_bash('echo $(session_name_from_path "/home/user/my.project")')
        assert result.stdout.strip() == "deck-my-project"

    def test_spaces_converted_to_dashes(self) -> None:
        result = run_bash('echo $(session_name_from_path "/home/user/my project")')
        assert result.stdout.strip() == "deck-my-project"


# ---------------------------------------------------------------------------
# Domain Mapping Tests
# ---------------------------------------------------------------------------


class TestDomainMappings:
    """Test commands_for_domain and templates_for_domain functions."""

    def test_ml_domain_commands(self) -> None:
        result = run_bash('echo $(commands_for_domain "ml")')
        output = result.stdout.strip()
        assert "mlflow-log-model" in output
        assert "uc-register-model" in output

    def test_databricks_domain_commands(self) -> None:
        result = run_bash('echo $(commands_for_domain "databricks")')
        output = result.stdout.strip()
        assert "databricks-job" in output

    def test_devops_domain_commands(self) -> None:
        result = run_bash('echo $(commands_for_domain "devops")')
        output = result.stdout.strip()
        assert "act" in output
        assert "create-hook" in output

    def test_unknown_domain_returns_empty(self) -> None:
        result = run_bash('echo ">>$(commands_for_domain "unknown")<<"')
        assert ">><<" in result.stdout.strip()

    def test_ml_domain_templates(self) -> None:
        result = run_bash('echo $(templates_for_domain "ml")')
        output = result.stdout.strip()
        assert "MLflow-Databricks" in output
        assert "DSPy" in output

    def test_backend_domain_templates(self) -> None:
        result = run_bash('echo $(templates_for_domain "backend")')
        output = result.stdout.strip()
        assert len(output) > 0

    def test_frontend_domain_templates(self) -> None:
        result = run_bash('echo $(templates_for_domain "frontend")')
        output = result.stdout.strip()
        assert len(output) > 0


# ---------------------------------------------------------------------------
# Needs Mapping Tests
# ---------------------------------------------------------------------------


class TestNeedsMappings:
    """Test commands_for_needs function."""

    def test_git_needs(self) -> None:
        result = run_bash('echo $(commands_for_needs "git")')
        output = result.stdout.strip()
        assert "create-pr" in output
        assert "fix-github-issue" in output

    def test_quality_needs(self) -> None:
        result = run_bash('echo $(commands_for_needs "quality")')
        output = result.stdout.strip()
        assert "testing_plan_integration" in output

    def test_context_needs(self) -> None:
        result = run_bash('echo $(commands_for_needs "context")')
        output = result.stdout.strip()
        assert "context-prime" in output

    def test_multiple_needs(self) -> None:
        result = run_bash('echo $(commands_for_needs "git docs")')
        output = result.stdout.strip()
        assert "create-pr" in output
        assert "update-docs" in output


# ---------------------------------------------------------------------------
# Session Save/Load Tests
# ---------------------------------------------------------------------------


class TestSessionManagement:
    """Test session save and load operations."""

    def test_save_and_load_session(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        result = run_bash(
            f"""
            SESSIONS_DIR="{sessions_dir}"
            save_session "deck-test" "/home/user/test" "ml" \
                "git quality" "commit pr-review" "MLflow DSPy"
            load_session "deck-test"
            echo "DIR=$PROJECT_DIR"
            echo "DOMAIN=$DOMAIN"
            echo "TEAM=$TEAM_NAME"
            """
        )
        assert "DIR=/home/user/test" in result.stdout
        assert "DOMAIN=ml" in result.stdout
        assert "TEAM=test" in result.stdout

    def test_load_nonexistent_session_fails(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        result = run_bash(
            f"""
            SESSIONS_DIR="{sessions_dir}"
            load_session "deck-nonexistent" 2>&1
            echo "EXIT=$?"
            """
        )
        assert "not found" in result.stdout.lower() or "EXIT=1" in result.stdout

    def test_session_config_file_created(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        run_bash(
            f"""
            SESSIONS_DIR="{sessions_dir}"
            save_session "deck-proj" "/tmp/proj" "backend" "git" "commit" "FastAPI"
            """
        )

        config_file = sessions_dir / "deck-proj.conf"
        assert config_file.exists(), "Session config file not created"

        content = config_file.read_text()
        assert "PROJECT_DIR=/tmp/proj" in content
        assert "DOMAIN=backend" in content


# ---------------------------------------------------------------------------
# List Command Tests
# ---------------------------------------------------------------------------


class TestListCommand:
    """Test the list/ls command."""

    def test_list_with_no_sessions(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        result = run_bash(
            f"""
            SESSIONS_DIR="{sessions_dir}"
            cmd_list
            """
        )
        assert "no sessions" in result.stdout.lower() or "No sessions" in result.stdout

    def test_list_with_sessions(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        run_bash(
            f"""
            SESSIONS_DIR="{sessions_dir}"
            save_session "deck-alpha" "/tmp/alpha" "ml" "git" "commit" "MLflow"
            save_session "deck-beta" "/tmp/beta" "backend" "git" "commit" "FastAPI"
            """
        )

        result = run_bash(
            f"""
            SESSIONS_DIR="{sessions_dir}"
            cmd_list
            """
        )
        assert "deck-alpha" in result.stdout
        assert "deck-beta" in result.stdout


# ---------------------------------------------------------------------------
# Help & Usage Tests
# ---------------------------------------------------------------------------


class TestHelpCommand:
    """Test the help/usage command."""

    def test_help_flag(self) -> None:
        result = subprocess.run(
            ["bash", AGENT_DECK, "help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "agent-deck" in result.stdout.lower()
        assert "setup" in result.stdout
        assert "open" in result.stdout
        assert "list" in result.stdout

    def test_help_long_flag(self) -> None:
        result = subprocess.run(
            ["bash", AGENT_DECK, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "agent-deck" in result.stdout.lower()

    def test_dash_h_flag(self) -> None:
        result = subprocess.run(
            ["bash", AGENT_DECK, "-h"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "agent-deck" in result.stdout.lower()


# ---------------------------------------------------------------------------
# Init Tests
# ---------------------------------------------------------------------------


class TestInit:
    """Test the init_deck function."""

    def test_init_creates_directories(self, tmp_path: Path) -> None:
        deck_home = tmp_path / "agent-deck"
        result = run_bash(
            f"""
            DECK_HOME="{deck_home}"
            SESSIONS_DIR="{deck_home}/sessions"
            init_deck
            echo "SESSIONS_EXISTS=$( [ -d "{deck_home}/sessions" ] && echo yes || echo no )"
            echo "CACHE_EXISTS=$( [ -d "{deck_home}/cache" ] && echo yes || echo no )"
            """
        )
        assert "SESSIONS_EXISTS=yes" in result.stdout
        assert "CACHE_EXISTS=yes" in result.stdout


# ---------------------------------------------------------------------------
# Install Resources Tests (with mock cache)
# ---------------------------------------------------------------------------


class TestInstallResources:
    """Test install_resources with a mock cache directory."""

    def test_install_slash_command(self, tmp_path: Path) -> None:
        # Set up a mock cache with a slash command
        cache_dir = tmp_path / "cache"
        cmd_dir = cache_dir / "resources" / "slash-commands" / "commit"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "commit.md").write_text("# Commit command\nDo a commit.\n")

        target = tmp_path / "project"
        target.mkdir()

        run_bash(
            f"""
            ACC_CACHE="{cache_dir}"
            install_resources "{target}" "commit" ""
            """,
            env={"HOME": str(tmp_path)},
        )

        installed = target / ".claude" / "commands" / "commit.md"
        assert installed.exists(), "Slash command was not installed"
        assert "Commit command" in installed.read_text()

    def test_install_claude_md_template(self, tmp_path: Path) -> None:
        # Set up a mock cache with a CLAUDE.md template
        cache_dir = tmp_path / "cache"
        tpl_dir = cache_dir / "resources" / "claude.md-files" / "TestTemplate"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "CLAUDE.md").write_text("# Test Template\nDo test things.\n")

        target = tmp_path / "project"
        target.mkdir()

        run_bash(
            f"""
            ACC_CACHE="{cache_dir}"
            install_resources "{target}" "" "TestTemplate"
            """,
            env={"HOME": str(tmp_path)},
        )

        claude_md = target / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md was not created"
        content = claude_md.read_text()
        assert "awesome-claude-code: TestTemplate" in content
        assert "Test Template" in content

    def test_install_does_not_duplicate_template(self, tmp_path: Path) -> None:
        """Installing the same template twice should not duplicate it."""
        cache_dir = tmp_path / "cache"
        tpl_dir = cache_dir / "resources" / "claude.md-files" / "DupeTest"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "CLAUDE.md").write_text("# Dupe Test\n")

        target = tmp_path / "project"
        target.mkdir()

        script = f"""
            ACC_CACHE="{cache_dir}"
            install_resources "{target}" "" "DupeTest"
            install_resources "{target}" "" "DupeTest"
        """
        run_bash(script, env={"HOME": str(tmp_path)})

        content = (target / "CLAUDE.md").read_text()
        assert content.count("awesome-claude-code: DupeTest") == 1
