"""Repo root discovery helpers."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path) -> Path:
    """Locate the repo root by walking upward until pyproject.toml exists."""
    p = start.resolve()
    while not (p / "pyproject.toml").exists():
        if p.parent == p:
            raise RuntimeError("Repo root not found")
        p = p.parent
    return p
