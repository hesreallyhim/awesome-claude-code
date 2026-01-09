"""Integration tests for TOC anchor validation against GitHub HTML.

These tests validate that our generated TOC anchors match what GitHub
actually produces when rendering the markdown. This catches anchor
generation bugs that would result in broken TOC links.

To update the fixtures after intentional changes:
    python -m scripts.testing.validate_toc_anchors --generate-expected
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.testing.validate_toc_anchors import (
    compare_anchors,
    extract_github_anchor_ids,
    extract_toc_anchors_from_readme,
    normalize_anchor,
)
from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
HTML_FIXTURE_PATH = REPO_ROOT / ".claude" / "root-readme-html-article-body.html"
EXPECTED_ANCHORS_PATH = REPO_ROOT / "tests" / "fixtures" / "expected_toc_anchors.txt"


class TestAnchorExtraction:
    """Unit tests for anchor extraction functions."""

    def test_extract_github_anchors_finds_user_content_ids(self) -> None:
        html = """
        <h2 id="user-content-agent-skills-">Agent Skills</h2>
        <h3 id="user-content-general">General</h3>
        <div id="other-id">Not a heading</div>
        """
        anchors = extract_github_anchor_ids(html)
        assert anchors == {"agent-skills-", "general"}

    def test_extract_toc_anchors_markdown_style(self) -> None:
        readme = """
        - [Agent Skills](#agent-skills-)
        - [General](#general)
        """
        anchors = extract_toc_anchors_from_readme(readme)
        assert "agent-skills-" in anchors
        assert "general" in anchors

    def test_extract_toc_anchors_html_style(self) -> None:
        readme = """
        <a href="#agent-skills-">Agent Skills</a>
        <a href="#general">General</a>
        """
        anchors = extract_toc_anchors_from_readme(readme)
        assert "agent-skills-" in anchors
        assert "general" in anchors

    def test_extract_toc_anchors_excludes_back_to_top(self) -> None:
        readme = """
        - [Agent Skills](#agent-skills-)
        [🔝](#awesome-claude-code)
        """
        anchors = extract_toc_anchors_from_readme(readme)
        assert "agent-skills-" in anchors
        assert "awesome-claude-code" not in anchors

    def test_normalize_anchor_url_decodes(self) -> None:
        assert normalize_anchor("official-documentation-%EF%B8%8F") == "official-documentation-️"
        assert normalize_anchor("simple-anchor") == "simple-anchor"


class TestAnchorComparison:
    """Unit tests for anchor comparison logic."""

    def test_compare_anchors_perfect_match(self) -> None:
        github = {"a", "b", "c"}
        toc = {"a", "b", "c"}
        matched, missing, extra = compare_anchors(github, toc)
        assert matched == {"a", "b", "c"}
        assert missing == set()
        assert extra == set()

    def test_compare_anchors_with_url_encoded(self) -> None:
        github = {"test-️"}  # Actual emoji
        toc = {"test-%EF%B8%8F"}  # URL encoded
        matched, missing, _ = compare_anchors(github, toc)
        assert "test-️" in matched
        assert missing == set()

    def test_compare_anchors_missing_in_github(self) -> None:
        github = {"a", "b"}
        toc = {"a", "b", "c"}
        _, missing, _ = compare_anchors(github, toc)
        assert "c" in missing

    def test_compare_anchors_extra_in_github(self) -> None:
        github = {"a", "b", "c"}
        toc = {"a", "b"}
        _, _, extra = compare_anchors(github, toc)
        assert "c" in extra


@pytest.mark.skipif(
    not HTML_FIXTURE_PATH.exists(),
    reason="GitHub HTML fixture not available (download from GitHub to enable)",
)
class TestTOCAnchorIntegration:
    """Integration tests validating TOC anchors against GitHub HTML."""

    def test_all_toc_anchors_exist_in_github_html(self) -> None:
        """Verify all TOC anchors match GitHub's actual anchor IDs.

        This is the primary regression test for TOC anchor generation.
        If this fails, TOC links are broken on GitHub.
        """
        html_content = HTML_FIXTURE_PATH.read_text(encoding="utf-8")
        readme_path = REPO_ROOT / "README.md"
        readme_content = readme_path.read_text(encoding="utf-8")

        github_anchors = extract_github_anchor_ids(html_content)
        toc_anchors = extract_toc_anchors_from_readme(readme_content)

        _, missing_in_github, _ = compare_anchors(github_anchors, toc_anchors)

        assert not missing_in_github, (
            f"TOC contains anchors not found in GitHub HTML (broken links): "
            f"{sorted(missing_in_github)}"
        )

    def test_expected_anchor_count(self) -> None:
        """Verify anchor counts haven't changed unexpectedly."""
        html_content = HTML_FIXTURE_PATH.read_text(encoding="utf-8")
        github_anchors = extract_github_anchor_ids(html_content)

        # Allow some flexibility for added/removed sections
        assert (
            len(github_anchors) >= 30
        ), f"Expected at least 30 GitHub anchors, found {len(github_anchors)}"


@pytest.mark.skipif(
    not EXPECTED_ANCHORS_PATH.exists(),
    reason="Expected anchors fixture not generated",
)
class TestExpectedAnchorsFixture:
    """Tests against the expected anchors fixture file."""

    def test_github_structure_unchanged(self) -> None:
        """Detect if GitHub's anchor generation changed.

        If this fails, GitHub may have changed how they generate anchor IDs.
        Update the fixture with: python -m scripts.testing.validate_toc_anchors --generate-expected
        """
        if not HTML_FIXTURE_PATH.exists():
            pytest.skip("GitHub HTML fixture not available")

        expected = set(EXPECTED_ANCHORS_PATH.read_text().strip().split("\n"))
        html_content = HTML_FIXTURE_PATH.read_text(encoding="utf-8")
        actual = extract_github_anchor_ids(html_content)

        assert actual == expected, (
            f"GitHub anchor structure changed. "
            f"New: {actual - expected}, Removed: {expected - actual}. "
            f"If intentional, regenerate fixture with: "
            f"python -m scripts.testing.validate_toc_anchors --generate-expected"
        )
