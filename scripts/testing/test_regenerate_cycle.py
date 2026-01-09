#!/usr/bin/env python3
"""Integration regeneration cycle test for README outputs."""

from __future__ import annotations

import contextlib
import re
import subprocess
import sys
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
CONFIG_PATH = REPO_ROOT / "acc-config.yaml"
README_PATH = REPO_ROOT / "README.md"

ROOT_STYLE_RE = re.compile(r"^(?P<indent>\s*)root_style:\s*(?P<value>\S+)\s*$", re.M)
STYLE_ORDER_RE = re.compile(r"^(style_order:\s*\n)(?P<items>(?:\s*-\s*.*\n?)+)", re.M)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def git_status() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def read_config_text() -> str:
    return CONFIG_PATH.read_text(encoding="utf-8")


def write_config_text(text: str) -> None:
    CONFIG_PATH.write_text(text, encoding="utf-8")


def set_root_style(text: str, root_style: str) -> str:
    if not ROOT_STYLE_RE.search(text):
        raise RuntimeError("root_style not found in acc-config.yaml")
    return ROOT_STYLE_RE.sub(rf"\g<indent>root_style: {root_style}", text, count=1)


def get_style_order(text: str) -> list[str]:
    match = STYLE_ORDER_RE.search(text)
    if not match:
        raise RuntimeError("style_order not found in acc-config.yaml")
    items: list[str] = []
    for line in match.group("items").splitlines():
        line = line.strip()
        if line.startswith("-"):
            items.append(line[1:].strip())
    if not items:
        raise RuntimeError("style_order is empty in acc-config.yaml")
    return items


def set_style_order(text: str, style_order: list[str]) -> str:
    if not STYLE_ORDER_RE.search(text):
        raise RuntimeError("style_order not found in acc-config.yaml")
    block = "style_order:\n" + "".join(f"  - {style}\n" for style in style_order)
    return STYLE_ORDER_RE.sub(block, text, count=1)


def read_readme() -> str:
    return README_PATH.read_text(encoding="utf-8")


def selector_order_from_content(content: str) -> list[str]:
    matches = re.findall(r"badge-style-([a-z0-9_-]+)\.svg", content)
    if not matches:
        raise RuntimeError("Could not determine style selector order from README.md")
    ordered: list[str] = []
    for item in matches:
        if item not in ordered:
            ordered.append(item)
    return ordered


def main() -> int:
    if git_status():
        print("Error: working tree must be clean before running test-regenerate-cycle")
        return 1

    original_text = read_config_text()

    try:
        run(["make", "test-regenerate"])

        current_text = read_config_text()
        style_order = get_style_order(current_text)

        if len(style_order) < 2:
            raise RuntimeError("style_order must contain at least two entries")

        first_style = style_order[0]
        second_style = style_order[1]

        updated_text = set_root_style(current_text, first_style)
        write_config_text(updated_text)

        run(["make", "test-regenerate-allow-diff"])
        first_content = read_readme()

        updated_text = set_root_style(updated_text, second_style)
        write_config_text(updated_text)

        run(["make", "test-regenerate-allow-diff"])
        root_content = read_readme()
        if root_content == first_content:
            raise RuntimeError("README.md did not change after root_style update")

        new_order = style_order[1:] + style_order[:1] if len(style_order) > 1 else style_order
        updated_text = set_style_order(updated_text, new_order)
        write_config_text(updated_text)

        previous_content = root_content
        run(["make", "test-regenerate-allow-diff"])
        root_content = read_readme()
        if root_content == previous_content:
            raise RuntimeError("README.md did not change after style_order update")

        selector_order = selector_order_from_content(root_content)
        if selector_order[: len(new_order)] != new_order:
            raise RuntimeError("Style selector order does not match updated style_order")

        write_config_text(original_text)
        run(["make", "test-regenerate", "ALLOW_DIRTY=1"])

        if git_status():
            raise RuntimeError("Working tree is dirty after restoring configuration")
    except subprocess.CalledProcessError as exc:
        print(f"Error: command failed: {exc}", file=sys.stderr)
        write_config_text(original_text)
        with contextlib.suppress(subprocess.CalledProcessError):
            run(["make", "test-regenerate", "ALLOW_DIRTY=1"])
        return exc.returncode
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        write_config_text(original_text)
        with contextlib.suppress(subprocess.CalledProcessError):
            run(["make", "test-regenerate", "ALLOW_DIRTY=1"])
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
