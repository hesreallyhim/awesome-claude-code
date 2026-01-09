#!/usr/bin/env python3
"""Tests for GitUtils helper methods."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.git_utils import GitUtils  # noqa: E402


def test_check_command_exists_true(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().check_command_exists("git") is True


def test_check_command_exists_false_on_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().check_command_exists("nope") is False


def test_run_command_failure_logs_error(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=1, stderr="bad", stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    utils = GitUtils(logger=logging.getLogger("git-utils-test"))
    with caplog.at_level(logging.ERROR):
        assert utils.run_command(["git", "status"], error_msg="oops") is False
        assert any("oops: bad" in message for message in caplog.messages)


def test_is_gh_authenticated(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="user\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().is_gh_authenticated() is True


def test_is_gh_authenticated_false_on_empty_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().is_gh_authenticated() is False


def test_get_github_username_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="octocat\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().get_github_username() == "octocat"


def test_get_github_username_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, "gh api")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().get_github_username() is None


def test_get_git_config_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="value\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().get_git_config("user.name") == "value"


def test_get_remote_type_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    utils = GitUtils()
    monkeypatch.setattr(utils, "get_remote_url", lambda *_: "git@github.com:owner/repo.git")
    assert utils.get_remote_type() == "ssh"

    monkeypatch.setattr(utils, "get_remote_url", lambda *_: "https://github.com/owner/repo")
    assert utils.get_remote_type() == "https"

    monkeypatch.setattr(utils, "get_remote_url", lambda *_: "file:///tmp/repo")
    assert utils.get_remote_type() is None


def test_is_working_directory_clean(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().is_working_directory_clean() is True


def test_is_working_directory_dirty(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout=" M file.txt\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().is_working_directory_clean() is False


def test_get_uncommitted_files(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout=" M file.txt\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().get_uncommitted_files() == "M file.txt"


def test_stage_file_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().stage_file(tmp_path / "file.txt") is True


def test_stage_file_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=1, stderr="bad")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().stage_file(tmp_path / "file.txt") is False


def test_check_file_modified(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(cmd, *args, **kwargs):
        if cmd[:3] == ["git", "diff", "--name-only"]:
            return SimpleNamespace(stdout="file.txt\n")
        if cmd[:4] == ["git", "diff", "--cached", "--name-only"]:
            return SimpleNamespace(stdout="")
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().check_file_modified(tmp_path / "file.txt") is True


def test_check_file_modified_staged(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(cmd, *args, **kwargs):
        if cmd[:3] == ["git", "diff", "--name-only"]:
            return SimpleNamespace(stdout="")
        if cmd[:4] == ["git", "diff", "--cached", "--name-only"]:
            return SimpleNamespace(stdout="file.txt\n")
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().check_file_modified(tmp_path / "file.txt") is True


def test_check_file_modified_clean(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(cmd, *args, **kwargs):
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert GitUtils().check_file_modified(tmp_path / "file.txt") is False
