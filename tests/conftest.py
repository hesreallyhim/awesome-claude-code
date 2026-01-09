"""Shared pytest fixtures."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


class DummyReset:
    """Minimal reset object with a timestamp."""

    @staticmethod
    def timestamp() -> int:
        return 0


class DummyCore:
    """Minimal core rate limit object."""

    def __init__(self) -> None:
        self.remaining = 5000
        self.limit = 5000
        self.reset = DummyReset()


class DummyRateLimit:
    """Minimal rate limit response wrapper."""

    def __init__(self) -> None:
        self.core = DummyCore()


class DummyIssue:
    """Minimal issue object with an html_url."""

    html_url = "https://example.com/issue"


class DummyRepo:
    """Minimal GitHub repo stub for notifications."""

    def __init__(self, full_name: str) -> None:
        self.full_name = full_name

    def get_label(self, name: str):
        return object()

    def create_label(self, name: str, color: str, description: str):
        return object()

    def get_issues(self, **kwargs):
        return []

    def create_issue(self, title: str, body: str, labels: list[str]):
        return DummyIssue()


class DummyUser:
    """Minimal GitHub user object."""

    login = "dummy-user"


class DummyGithub:
    """Minimal GitHub client stub."""

    def __init__(self, *args, **kwargs) -> None:
        pass

    def get_rate_limit(self):
        return DummyRateLimit()

    def get_repo(self, full_name: str):
        return DummyRepo(full_name)

    def get_user(self):
        return DummyUser()


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    while not (p / "pyproject.toml").exists():
        if p.parent == p:
            raise RuntimeError("Repo root not found")
        p = p.parent
    return p


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Resolve the repository root for tests."""
    return find_repo_root(Path(__file__))


@pytest.fixture
def github_stub(monkeypatch: pytest.MonkeyPatch):
    """Replace the GitHub client to avoid network calls."""
    try:
        import scripts.utils.github_utils as github_utils

        monkeypatch.setattr(github_utils, "Github", DummyGithub)
        monkeypatch.setattr(github_utils, "_GITHUB_CLIENTS", {})
    except ImportError:
        pass

    modules = []
    for name in (
        "badge_notification_core",
        "scripts.badge_notification_core",
        "scripts.badges.badge_notification_core",
    ):
        if name in sys.modules:
            modules.append(sys.modules[name])

    if not modules:
        for name in (
            "badge_notification_core",
            "scripts.badge_notification_core",
            "scripts.badges.badge_notification_core",
        ):
            try:
                modules.append(importlib.import_module(name))
            except ImportError:
                continue

    if not modules:
        raise RuntimeError("Could not locate badge_notification_core module for stubbing")

    for module in modules:
        monkeypatch.setattr(module, "Github", DummyGithub)
    return DummyGithub
