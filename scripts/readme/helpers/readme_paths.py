"""Path resolution helpers for README generation."""

from __future__ import annotations

import os
import re
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

GENERATED_HEADER = "<!-- GENERATED FILE: do not edit directly -->"

ASSET_PATH_PATTERN = re.compile(
    r"\{\{ASSET_PATH\(\s*(?P<quote>['\"])(?P<path>[^'\"]+)(?P=quote)\s*\)\}\}"
)
ASSET_URL_PATTERN = re.compile(r"asset:([A-Za-z0-9_.\-/]+)")


def asset_path_token(filename: str) -> str:
    """Return a tokenized asset reference for templates/markup."""
    filename = filename.lstrip("/")
    return f"{{{{ASSET_PATH('{filename}')}}}}"


def ensure_generated_header(content: str) -> str:
    """Prepend the generated-file header if missing."""
    if content.startswith(GENERATED_HEADER):
        return content
    return f"{GENERATED_HEADER}\n{content.lstrip(chr(10))}"


def resolve_asset_tokens(content: str, output_path: Path, repo_root: Path | None = None) -> str:
    """Resolve asset tokens into relative paths for the output location."""
    repo_root = repo_root or find_repo_root(output_path)
    base_dir = output_path.parent
    assets_dir = repo_root / "assets"

    rel_assets = Path(os.path.relpath(assets_dir, start=base_dir)).as_posix()
    if rel_assets == ".":
        rel_assets = "assets"
    rel_assets = rel_assets.rstrip("/")

    def join_asset(path: str) -> str:
        path = path.lstrip("/")
        if not rel_assets:
            return path
        return f"{rel_assets}/{path}"

    content = content.replace("{{ASSET_PREFIX}}", f"{rel_assets}/")

    content = ASSET_PATH_PATTERN.sub(lambda match: join_asset(match.group("path")), content)
    content = ASSET_URL_PATTERN.sub(lambda match: join_asset(match.group(1)), content)

    return content


def resolve_relative_link(from_path: Path, to_path: Path, repo_root: Path | None = None) -> str:
    """Return a relative link between two files, normalized for README links."""
    repo_root = repo_root or find_repo_root(from_path)
    from_path = from_path.resolve()
    to_path = (repo_root / to_path).resolve() if not to_path.is_absolute() else to_path.resolve()

    rel_path = Path(os.path.relpath(to_path, start=from_path.parent)).as_posix()

    if to_path == repo_root / "README.md":
        if rel_path in (".", "README.md"):
            return "./"
        if rel_path.endswith("/README.md"):
            return rel_path[: -len("README.md")]

    return rel_path
