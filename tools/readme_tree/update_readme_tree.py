#!/usr/bin/env python3
"""Update the README generation tree block from a YAML spec."""

from __future__ import annotations

import argparse
import difflib
import fnmatch
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Node:
    """Tree node representing a file or directory."""

    name: str
    is_dir: bool
    children: dict[str, Node] = field(default_factory=dict)


@dataclass(frozen=True)
class IgnoreRule:
    """Parsed ignore rule from config patterns."""

    pattern: str
    negated: bool
    dir_only: bool
    anchored: bool


@dataclass
class GitIgnoreChecker:
    """Check paths against gitignore using `git check-ignore`."""

    repo_root: Path
    enabled: bool = True
    _cache: dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Disable checking when git is unavailable."""
        if not self._git_available():
            self.enabled = False

    def _git_available(self) -> bool:
        """Return True if git is available and repo_root is a git work tree."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_root),
                    "rev-parse",
                    "--is-inside-work-tree",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            return False
        return result.returncode == 0

    @staticmethod
    def _canon_rel(rel_path: str) -> str:
        """Canonicalize a repo-relative POSIX path for comparing with git output."""
        p = rel_path.replace("\\", "/").strip()
        if p.startswith("./"):
            p = p[2:]
        # git check-ignore may echo trailing slashes for dir queries; normalize them away
        if p.endswith("/"):
            p = p[:-1]
        return p

    def _check(self, paths: list[str]) -> set[str]:
        """Return the subset of paths ignored by git, using a single subprocess."""
        if not paths:
            return set()

        # Normalize queries up-front to avoid mismatches with git echo format.
        canon_queries = [self._canon_rel(p) for p in paths if p]
        payload = "\0".join(canon_queries) + "\0"

        result = subprocess.run(
            ["git", "-C", str(self.repo_root), "check-ignore", "-z", "--stdin"],
            input=payload.encode("utf-8"),
            check=False,
            capture_output=True,
        )
        if result.returncode not in (0, 1):
            # Something unexpected (e.g. not a repo, weird git error). Disable to be safe.
            self.enabled = False
            return set()

        output = result.stdout.decode("utf-8", errors="replace")
        ignored_raw = [entry for entry in output.split("\0") if entry]
        ignored = {self._canon_rel(p) for p in ignored_raw}
        return ignored

    def is_ignored(self, rel_path: str, is_dir: bool) -> bool:
        """Return True if a path is ignored by gitignore rules."""
        if not self.enabled:
            return False

        canon = self._canon_rel(rel_path)
        cached = self._cache.get(canon)
        if cached is not None:
            return cached

        queries = [canon]
        # For directories, query both forms; git's echo varies depending on input.
        if is_dir:
            queries.append(f"{canon}/")

        ignored = self._check(queries)
        match = any(self._canon_rel(q) in ignored for q in queries)

        # Cache canonical key.
        self._cache[canon] = match
        return match


def find_repo_root(start: Path) -> Path:
    """Locate the repo root.

    Prefer git to identify the VCS root; fall back to walking upward for pyproject.toml.

    Args:
        start: Path inside the repo.

    Returns:
        The repo root path.
    """
    p = start.resolve()
    # Prefer git root if available.
    try:
        result = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            git_root = result.stdout.strip()
            if git_root:
                return Path(git_root)
    except FileNotFoundError:
        pass

    # Fallback: walk upward until pyproject.toml exists.
    while not (p / "pyproject.toml").exists():
        if p.parent == p:
            raise RuntimeError("Repo root not found (no git root and no pyproject.toml)")
        p = p.parent
    return p


def normalize_key(path: str | Path | None) -> str:
    """Normalize a path-like key into a repo-relative POSIX string."""
    if path is None:
        return ""
    s = str(path).strip()
    if s in {".", "./", ""}:
        return ""
    s = s.replace("\\", "/").strip("/")
    return s


def load_config(config_path: Path) -> dict:
    """Load the YAML configuration for tree generation."""
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Invalid config format")
    return data


def parse_ignore_rule(pattern: str | Path | None) -> IgnoreRule | None:
    """Parse a raw ignore pattern into a structured rule."""
    if pattern is None:
        return None
    line = str(pattern).strip()
    if not line or line.startswith("#"):
        return None

    negated = line.startswith("!")
    if negated:
        line = line[1:]

    anchored = line.startswith("/")
    if anchored:
        line = line[1:]

    dir_only = line.endswith("/")
    if dir_only:
        line = line[:-1]

    line = line.replace("\\", "/").strip()
    if not line:
        return None

    return IgnoreRule(pattern=line, negated=negated, dir_only=dir_only, anchored=anchored)


def parse_ignore_rules(patterns: list[str | Path]) -> list[IgnoreRule]:
    """Parse a list of ignore patterns into IgnoreRule entries."""
    rules: list[IgnoreRule] = []
    for pattern in patterns:
        rule = parse_ignore_rule(pattern)
        if rule:
            rules.append(rule)
    return rules


def matches_ignore_rule(rule: IgnoreRule, rel_path: str, is_dir: bool) -> bool:
    """Check whether a path matches a given ignore rule."""
    path = rel_path

    if rule.dir_only and not is_dir:
        return False

    # For dir-only rules, allow matching the dir itself or any descendant.
    if rule.dir_only:
        if rule.anchored:
            return path == rule.pattern or path.startswith(f"{rule.pattern}/")
        return (
            path == rule.pattern
            or path.endswith(f"/{rule.pattern}")
            or path.startswith(f"{rule.pattern}/")
            or f"/{rule.pattern}/" in f"/{path}/"
        )

    if rule.anchored:
        return fnmatch.fnmatch(path, rule.pattern)

    if "/" in rule.pattern:
        return fnmatch.fnmatch(path, rule.pattern) or fnmatch.fnmatch(path, f"*/{rule.pattern}")

    # Basename match
    if fnmatch.fnmatch(Path(path).name, rule.pattern):
        return True
    return fnmatch.fnmatch(path, rule.pattern) or fnmatch.fnmatch(path, f"*/{rule.pattern}")


def is_ignored(rel_path: str, is_dir: bool, rules: list[IgnoreRule]) -> bool:
    """Determine if a path should be ignored based on ordered rules."""
    ignored = False
    for rule in rules:
        if matches_ignore_rule(rule, rel_path, is_dir):
            ignored = not rule.negated
    return ignored


def is_pruned(rel_path: str, patterns: list[str]) -> bool:
    """Check whether a path should be pruned (no descent)."""
    for pattern in patterns:
        pat = pattern.strip()
        if not pat:
            continue
        pat = pat.replace("\\", "/").strip("/")
        if rel_path == pat or rel_path.startswith(f"{pat}/"):
            return True
    return False


def add_path(root: Node, parts: list[str], is_dir: bool) -> Node:
    """Add a path to the tree, creating nodes as needed."""
    node = root
    for i, part in enumerate(parts):
        if not part:
            continue
        if part not in node.children:
            node.children[part] = Node(
                name=part,
                is_dir=is_dir if i == len(parts) - 1 else True,
            )
        node = node.children[part]
    node.is_dir = is_dir
    return node


def walk_include(
    root: Node,
    repo_root: Path,
    include_path: Path,
    max_depth: int,
    ignore: list[IgnoreRule],
    gitignore: GitIgnoreChecker | None,
    prune: list[str],
    *,
    base_rel: str,
    base_depth: int,
) -> None:
    """Walk an include path and add matching entries to the tree.

    Depth limiting is relative to the include root (not repo root).
    """
    rel = include_path.relative_to(repo_root).as_posix()

    if gitignore and gitignore.is_ignored(rel, include_path.is_dir()):
        return
    if is_ignored(rel, include_path.is_dir(), ignore):
        return

    if include_path.is_file():
        add_path(root, rel.split("/"), is_dir=False)
        return

    add_path(root, rel.split("/"), is_dir=True)
    if is_pruned(rel, prune):
        return

    for child in sorted(include_path.iterdir(), key=lambda p: p.name.lower()):
        child_rel = child.relative_to(repo_root).as_posix()
        if gitignore and gitignore.is_ignored(child_rel, child.is_dir()):
            continue
        if is_ignored(child_rel, child.is_dir(), ignore):
            continue

        # Depth relative to include root
        rel_to_include = child_rel[len(base_rel) :].lstrip("/") if base_rel else child_rel
        depth_rel = base_depth + (len(rel_to_include.split("/")) if rel_to_include else 0)
        if max_depth and depth_rel > max_depth:
            continue

        if child.is_dir():
            walk_include(
                root,
                repo_root,
                child,
                max_depth,
                ignore,
                gitignore,
                prune,
                base_rel=base_rel,
                base_depth=base_depth,
            )
        else:
            add_path(root, child_rel.split("/"), is_dir=False)


def build_tree(config: dict, repo_root: Path) -> Node:
    """Build a tree based on config includes and virtual entries."""
    root_label = config.get("root", repo_root.name)
    root = Node(name=str(root_label), is_dir=True)
    include = [normalize_key(p) for p in config.get("include", [])]
    ignore_patterns = config.get("ignore", [])
    prune = [normalize_key(p) for p in config.get("prune", [])]
    max_depth = int(config.get("max_depth", 0))
    respect_gitignore = bool(config.get("respect_gitignore", True))

    ignore_rules = parse_ignore_rules(ignore_patterns)
    git_checker = GitIgnoreChecker(repo_root) if respect_gitignore else None

    for item in include:
        if not item:
            continue
        path = repo_root / item
        if not path.exists():
            raise RuntimeError(f"Included path does not exist: {item}")

        base_rel = path.relative_to(repo_root).as_posix()
        base_depth = 0  # include root itself counts as depth 0
        walk_include(
            root,
            repo_root,
            path,
            max_depth,
            ignore_rules,
            git_checker,
            prune,
            base_rel=base_rel,
            base_depth=base_depth,
        )

    virtual_entries = config.get("virtual_entries", {})
    if isinstance(virtual_entries, list):
        tmp: dict[str, str] = {}
        for item in virtual_entries:
            if not isinstance(item, dict):
                raise RuntimeError(
                    "virtual_entries list items must be mappings with 'path' and optional 'comment'"
                )
            p = item.get("path")
            c = item.get("comment", "")
            if p:
                tmp[str(p)] = str(c) if c is not None else ""
        items = tmp
    elif isinstance(virtual_entries, dict):
        items = {str(k): ("" if v is None else str(v)) for k, v in virtual_entries.items()}
    else:
        raise RuntimeError("virtual_entries must be a mapping or a list")

    for path_str in items:
        if not path_str:
            continue
        is_dir = str(path_str).endswith("/")
        norm = normalize_key(str(path_str))
        if norm:
            add_path(root, norm.split("/"), is_dir=is_dir)

    return root


def sort_children(node: Node, path: str, order_map: dict[str, list[str]]) -> list[Node]:
    """Sort child nodes with optional ordered patterns."""
    order_list = order_map.get(path, [])

    def order_index(name: str) -> int | None:
        for idx, pattern in enumerate(order_list):
            if pattern.startswith("glob:"):
                if fnmatch.fnmatch(name, pattern[5:]):
                    return idx
            elif name == pattern:
                return idx
        return None

    def sort_key(child: Node) -> tuple[int, int, str]:
        idx = order_index(child.name)
        if idx is not None:
            return (0, idx, child.name.lower())
        # dirs first, then files
        return (1, 0 if child.is_dir else 1, child.name.lower())

    return sorted(node.children.values(), key=sort_key)


def render_tree(root: Node, comments: dict[str, str], order_map: dict[str, list[str]]) -> list[str]:
    """Render the tree into a list of display lines."""
    lines: list[str] = [f"{root.name}/"]

    def render_node(node: Node, prefix: str, path: str, is_last: bool) -> None:
        connector = "└── " if is_last else "├── "
        name = f"{node.name}/" if node.is_dir else node.name
        comment = comments.get(path, "")
        line = f"{prefix}{connector}{name}"
        if comment:
            line += f"  # {comment}"
        lines.append(line)

        if not node.children:
            return

        child_prefix = f"{prefix}{'    ' if is_last else '│   '}"
        children = sort_children(node, path, order_map)
        for idx, child in enumerate(children):
            child_path = f"{path}/{child.name}" if path else child.name
            render_node(child, child_prefix, child_path, idx == len(children) - 1)

    children = sort_children(root, "", order_map)
    for idx, child in enumerate(children):
        render_node(child, "", child.name, idx == len(children) - 1)

    return lines


def update_document(
    doc_path: Path,
    marker_start: str,
    marker_end: str,
    block: str,
    check: bool,
    *,
    debug: bool = False,
    debug_context: dict[str, str] | None = None,
) -> None:
    content = doc_path.read_text(encoding="utf-8")

    start = content.find(marker_start)
    if start == -1:
        raise RuntimeError("Tree start marker not found in document")

    end = content.find(marker_end, start + len(marker_start))
    if end == -1:
        raise RuntimeError("Tree end marker not found in document")

    updated = content[: start + len(marker_start)] + "\n" + block + "\n" + content[end:]

    if check:
        if updated != content:
            if debug:
                if debug_context:
                    print("README TREE CHECK DEBUG CONTEXT:", file=sys.stderr)
                    for k, v in debug_context.items():
                        print(f"- {k}: {v}", file=sys.stderr)

                diff = difflib.unified_diff(
                    content.splitlines(keepends=True),
                    updated.splitlines(keepends=True),
                    fromfile=str(doc_path),
                    tofile=str(doc_path) + " (expected)",
                )
                print("\n".join(diff), file=sys.stderr)

            raise RuntimeError("Tree block is out of date")
        return

    doc_path.write_text(updated, encoding="utf-8")


def main() -> int:
    """CLI entry point for updating the README tree block."""
    parser = argparse.ArgumentParser(description="Update README tree block.")
    parser.add_argument(
        "--config",
        default="tools/readme_tree/config.yaml",
        help="Path to the tree config file.",
    )
    parser.add_argument("--check", action="store_true", help="Fail if updates are needed.")
    parser.add_argument("--debug", action="store_true", help="Print debug info on mismatch.")

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        return 1

    repo_root = find_repo_root(config_path)
    config = load_config(config_path)

    doc_path = repo_root / config.get("doc_path", "docs/README-GENERATION.md")
    if not doc_path.exists():
        print(f"Doc not found: {doc_path}", file=sys.stderr)
        return 1

    tree = build_tree(config, repo_root)

    comments = {normalize_key(k): v for k, v in config.get("entries", {}).items()}
    virtual_comments = config.get("virtual_entries", {})
    if isinstance(virtual_comments, dict):
        for key, value in virtual_comments.items():
            if value is None:
                continue
            comments.setdefault(normalize_key(key), str(value))

    order_map = {normalize_key(k): v for k, v in config.get("order", {}).items()}

    lines = render_tree(tree, comments, order_map)
    block = "```" + "\n" + "\n".join(lines) + "\n```"

    debug_context = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "doc_path": str(doc_path),
        "config_path": str(config_path),
        "LANG": os.environ.get("LANG", ""),
        "LC_ALL": os.environ.get("LC_ALL", ""),
    }

    try:
        debug_context["git_version"] = subprocess.check_output(
            ["git", "--version"], text=True
        ).strip()
        debug_context["git_toplevel"] = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "--show-toplevel"], text=True
        ).strip()
        debug_context["git_core_ignorecase"] = subprocess.check_output(
            ["git", "-C", str(repo_root), "config", "--get", "core.ignorecase"],
            text=True,
        ).strip()
    except Exception:
        pass

    update_document(
        doc_path,
        config.get("marker_start", "<!-- TREE:START -->"),
        config.get("marker_end", "<!-- TREE:END -->"),
        block,
        args.check,
        debug=args.debug,
        debug_context=debug_context,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
