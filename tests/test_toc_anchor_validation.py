"""Integration tests for TOC anchor validation against GitHub HTML.

These tests validate that our generated TOC anchors match what GitHub
actually produces when rendering the markdown. This catches anchor
generation bugs that would result in broken TOC links.

HTML fixtures are stored in tests/fixtures/github-html/ and version controlled.
To update fixtures:
    1. Push changes to GitHub
    2. Navigate to the README on GitHub
    3. Open browser dev tools (F12)
    4. Find the <article> element containing the README
    5. Copy inner HTML to the appropriate fixture file
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
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "github-html"
EXPECTED_ANCHORS_PATH = REPO_ROOT / "tests" / "fixtures" / "expected_toc_anchors.txt"

# Style configurations: (html_fixture, readme_path)
# HTML fixture names indicate root vs non-root placement on GitHub
STYLE_CONFIGS = {
    "awesome": (FIXTURES_DIR / "awesome-root.html", REPO_ROOT / "README.md"),
    "classic": (
        FIXTURES_DIR / "classic-non-root.html",
        REPO_ROOT / "README_ALTERNATIVES" / "README_CLASSIC.md",
    ),
    "extra": (
        FIXTURES_DIR / "extra-non-root.html",
        REPO_ROOT / "README_ALTERNATIVES" / "README_EXTRA.md",
    ),
    "flat": (
        FIXTURES_DIR / "flat-non-root.html",
        REPO_ROOT / "README_ALTERNATIVES" / "README_FLAT_ALL_AZ.md",
    ),
}


def is_placeholder(path: Path) -> bool:
    """Check if an HTML fixture is a placeholder (not yet populated)."""
    if not path.exists():
        return True
    content = path.read_text(encoding="utf-8")
    return content.strip().startswith("<!-- PLACEHOLDER:")


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


def _validate_style(style_name: str) -> None:
    """Common validation logic for a README style."""
    html_path, readme_path = STYLE_CONFIGS[style_name]

    html_content = html_path.read_text(encoding="utf-8")
    readme_content = readme_path.read_text(encoding="utf-8")

    github_anchors = extract_github_anchor_ids(html_content)
    toc_anchors = extract_toc_anchors_from_readme(readme_content)

    _, missing_in_github, _ = compare_anchors(github_anchors, toc_anchors)

    assert not missing_in_github, (
        f"[{style_name.upper()}] TOC contains anchors not found in GitHub HTML (broken links): "
        f"{sorted(missing_in_github)}"
    )


class TestAwesomeStyle:
    """Integration tests for AWESOME style (root README.md)."""

    @pytest.mark.skipif(
        is_placeholder(STYLE_CONFIGS["awesome"][0]),
        reason="AWESOME HTML fixture not populated",
    )
    def test_toc_anchors_match_github(self) -> None:
        """Verify all AWESOME style TOC anchors exist in GitHub HTML."""
        _validate_style("awesome")

    @pytest.mark.skipif(
        is_placeholder(STYLE_CONFIGS["awesome"][0]),
        reason="AWESOME HTML fixture not populated",
    )
    def test_expected_anchor_count(self) -> None:
        """Verify AWESOME anchor count is reasonable."""
        html_path = STYLE_CONFIGS["awesome"][0]
        html_content = html_path.read_text(encoding="utf-8")
        github_anchors = extract_github_anchor_ids(html_content)
        assert len(github_anchors) >= 30, (
            f"Expected at least 30 anchors, found {len(github_anchors)}"
        )


class TestClassicStyle:
    """Integration tests for CLASSIC style (README_CLASSIC.md)."""

    @pytest.mark.skipif(
        is_placeholder(STYLE_CONFIGS["classic"][0]),
        reason="CLASSIC HTML fixture not populated",
    )
    def test_toc_anchors_match_github(self) -> None:
        """Verify all CLASSIC style TOC anchors exist in GitHub HTML."""
        _validate_style("classic")


class TestExtraStyle:
    """Integration tests for EXTRA style (README_EXTRA.md)."""

    @pytest.mark.skipif(
        is_placeholder(STYLE_CONFIGS["extra"][0]),
        reason="EXTRA HTML fixture not populated - see tests/fixtures/github-html/extra.html",
    )
    def test_toc_anchors_match_github(self) -> None:
        """Verify all EXTRA style TOC anchors exist in GitHub HTML."""
        _validate_style("extra")


class TestFlatStyle:
    """Integration tests for FLAT style (README_FLAT_ALL_AZ.md)."""

    @pytest.mark.skipif(
        is_placeholder(STYLE_CONFIGS["flat"][0]),
        reason="FLAT HTML fixture not populated - see tests/fixtures/github-html/flat.html",
    )
    def test_toc_anchors_match_github(self) -> None:
        """Verify all FLAT style TOC anchors exist in GitHub HTML."""
        _validate_style("flat")


@pytest.mark.skipif(
    not EXPECTED_ANCHORS_PATH.exists(),
    reason="Expected anchors fixture not generated",
)
class TestExpectedAnchorsFixture:
    """Tests against the expected anchors fixture file (AWESOME style baseline)."""

    def test_github_structure_unchanged(self) -> None:
        """Detect if GitHub's anchor generation changed.

        If this fails, GitHub may have changed how they generate anchor IDs.
        Update the fixture with: python -m scripts.testing.validate_toc_anchors --generate-expected
        """
        html_path = STYLE_CONFIGS["awesome"][0]
        if is_placeholder(html_path):
            pytest.skip("AWESOME HTML fixture not populated")

        expected = set(EXPECTED_ANCHORS_PATH.read_text().strip().split("\n"))
        html_content = html_path.read_text(encoding="utf-8")
        actual = extract_github_anchor_ids(html_content)

        assert actual == expected, (
            f"GitHub anchor structure changed. "
            f"New: {actual - expected}, Removed: {expected - actual}. "
            f"If intentional, regenerate fixture with: "
            f"python -m scripts.testing.validate_toc_anchors --generate-expected"
        )
