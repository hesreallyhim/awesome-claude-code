#!/usr/bin/env python3
"""Validate TOC anchors against GitHub-rendered HTML.

This utility compares the anchor links in our generated README's table of contents
against the actual anchor IDs that GitHub generates when rendering the markdown.

Usage:
    # Validate against saved HTML fixture
    python -m scripts.testing.validate_toc_anchors

    # Validate with custom paths
    python -m scripts.testing.validate_toc_anchors --html path/to/github.html --readme README.md

    # Generate new fixture (requires manual step to download HTML from GitHub)
    python -m scripts.testing.validate_toc_anchors --generate-expected

To obtain the GitHub HTML:
    1. Push your README to GitHub
    2. View the rendered README page
    3. Open browser dev tools (F12)
    4. Find the <article> element containing the README content
    5. Copy the inner HTML and save to .claude/root-readme-html-article-body.html
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
DEFAULT_HTML_PATH = REPO_ROOT / ".claude" / "root-readme-html-article-body.html"
DEFAULT_README_PATH = REPO_ROOT / "README.md"
EXPECTED_ANCHORS_PATH = REPO_ROOT / "tests" / "fixtures" / "expected_toc_anchors.txt"


def extract_github_anchor_ids(html_content: str) -> set[str]:
    """Extract heading anchor IDs from GitHub-rendered HTML.

    GitHub prefixes heading IDs with 'user-content-' in the rendered HTML.
    """
    pattern = r'id="user-content-([^"]*)"'
    matches = re.findall(pattern, html_content)
    return set(matches)


def extract_toc_anchors_from_readme(readme_content: str) -> set[str]:
    """Extract TOC anchor links from README markdown.

    Handles both markdown links [text](#anchor) and HTML href="#anchor".
    """
    # Markdown style: [text](#anchor)
    md_pattern = r"\]\(#([^)]+)\)"
    md_matches = re.findall(md_pattern, readme_content)

    # HTML style: href="#anchor"
    html_pattern = r'href="#([^"]+)"'
    html_matches = re.findall(html_pattern, readme_content)

    all_anchors = set(md_matches + html_matches)

    # Filter out back-to-top links (these aren't TOC entries)
    all_anchors.discard("awesome-claude-code")

    return all_anchors


def normalize_anchor(anchor: str) -> str:
    """Normalize anchor for comparison (URL decode)."""
    return urllib.parse.unquote(anchor)


def compare_anchors(
    github_anchors: set[str],
    toc_anchors: set[str],
) -> tuple[set[str], set[str], set[str]]:
    """Compare GitHub anchors with TOC anchors.

    Returns:
        Tuple of (matched, missing_in_github, extra_in_github)
    """
    # Normalize TOC anchors (URL decode)
    toc_normalized = {normalize_anchor(a) for a in toc_anchors}

    # Filter GitHub anchors to only include those that could be TOC entries
    # (headings in the body sections, not meta sections like "contents", "license")
    toc_relevant_github = github_anchors.copy()

    matched = toc_normalized & toc_relevant_github
    missing_in_github = toc_normalized - toc_relevant_github
    extra_in_github = toc_relevant_github - toc_normalized

    return matched, missing_in_github, extra_in_github


def validate(
    html_path: Path = DEFAULT_HTML_PATH,
    readme_path: Path = DEFAULT_README_PATH,
    verbose: bool = True,
) -> bool:
    """Validate TOC anchors against GitHub HTML.

    Returns True if validation passes, False otherwise.
    """
    if not html_path.exists():
        print(f"❌ GitHub HTML file not found: {html_path}")
        print("   Download the rendered HTML from GitHub and save it to this path.")
        print("   See module docstring for instructions.")
        return False

    if not readme_path.exists():
        print(f"❌ README file not found: {readme_path}")
        return False

    html_content = html_path.read_text(encoding="utf-8")
    readme_content = readme_path.read_text(encoding="utf-8")

    github_anchors = extract_github_anchor_ids(html_content)
    toc_anchors = extract_toc_anchors_from_readme(readme_content)

    if verbose:
        print(f"📄 GitHub HTML: {html_path}")
        print(f"📄 README: {readme_path}")
        print(f"   Found {len(github_anchors)} GitHub anchor IDs")
        print(f"   Found {len(toc_anchors)} TOC anchors")
        print()

    matched, missing_in_github, extra_in_github = compare_anchors(github_anchors, toc_anchors)

    # Filter extra_in_github to only show content section anchors
    # (exclude meta sections that aren't in TOC)
    meta_sections = {
        "contents",
        "latest-additions",
        "contributing-",
        "license",
        "growing-thanks-to-you",
        "recommend-a-new-resource-here",
        "pick-your-style",
        "awesome-claude-code",
    }
    extra_in_github = extra_in_github - meta_sections

    success = True

    if missing_in_github:
        print("❌ TOC anchors NOT FOUND in GitHub HTML (BROKEN LINKS):")
        for anchor in sorted(missing_in_github):
            print(f"   #{anchor}")
        success = False
    else:
        print("✅ All TOC anchors found in GitHub HTML")

    if extra_in_github and verbose:
        print("\n⚠️  GitHub headings not in TOC (informational only):")
        for anchor in sorted(extra_in_github):
            print(f"   #{anchor}")

    if success:
        print(f"\n🎉 Validation passed! {len(matched)} TOC anchors verified.")

    return success


def generate_expected_anchors(
    html_path: Path = DEFAULT_HTML_PATH,
    output_path: Path = EXPECTED_ANCHORS_PATH,
) -> None:
    """Generate expected anchors file from current GitHub HTML."""
    if not html_path.exists():
        print(f"❌ GitHub HTML file not found: {html_path}")
        return

    html_content = html_path.read_text(encoding="utf-8")
    anchors = extract_github_anchor_ids(html_content)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sorted(anchors)) + "\n", encoding="utf-8")
    print(f"✅ Generated expected anchors file: {output_path}")
    print(f"   Contains {len(anchors)} anchor IDs")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate TOC anchors against GitHub-rendered HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--html",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help="Path to GitHub-rendered HTML file",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=DEFAULT_README_PATH,
        help="Path to README.md file",
    )
    parser.add_argument(
        "--generate-expected",
        action="store_true",
        help="Generate expected anchors fixture file",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only show errors",
    )

    args = parser.parse_args()

    if args.generate_expected:
        generate_expected_anchors(args.html)
        return 0

    success = validate(args.html, args.readme, verbose=not args.quiet)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
