"""
Tests for style selector and path handling logic.

These tests verify the brittle assumptions around:
- output_path-based selector behavior
- resolved_output_path computation
- generate_style_selector() path generation
- Config-driven root style switching
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.readme.helpers import readme_config  # noqa: E402
from scripts.readme.helpers.readme_config import (  # noqa: E402
    CONFIG,
    get_root_style,
    get_style_selector_target,
)
from scripts.readme.helpers.readme_paths import (  # noqa: E402
    resolve_asset_tokens,
    resolve_relative_link,
)
from scripts.readme.markup.shared import generate_style_selector  # noqa: E402


def _resolve_selector(html: str, output_path: Path, repo_root: Path) -> str:
    return resolve_asset_tokens(html, output_path, repo_root)


class TestResolveRelativeLink:
    """Tests for resolve_relative_link() helper."""

    def test_root_self_link_is_dot_slash(self, tmp_path: Path) -> None:
        href = resolve_relative_link(tmp_path / "README.md", Path("README.md"), tmp_path)
        assert href == "./"

    def test_root_to_alternative_link(self, tmp_path: Path) -> None:
        href = resolve_relative_link(
            tmp_path / "README.md",
            Path("README_ALTERNATIVES/README_CLASSIC.md"),
            tmp_path,
        )
        assert href == "README_ALTERNATIVES/README_CLASSIC.md"

    def test_alternative_to_root_link(self, tmp_path: Path) -> None:
        href = resolve_relative_link(
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            Path("README.md"),
            tmp_path,
        )
        assert href == "../"

    def test_alternative_to_sibling_link(self, tmp_path: Path) -> None:
        href = resolve_relative_link(
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            Path("README_ALTERNATIVES/README_AWESOME.md"),
            tmp_path,
        )
        assert href == "README_AWESOME.md"


class TestGetRootStyle:
    """Tests for get_root_style() function."""

    def test_root_style_from_config(self) -> None:
        """Root style should come from config."""
        root_style = get_root_style()
        assert root_style in ["extra", "classic", "awesome", "flat"]

    def test_root_style_can_be_changed(self, monkeypatch) -> None:
        """Root style should reflect config changes."""
        monkeypatch.setitem(readme_config.CONFIG, "readme", {"root_style": "awesome"})
        assert get_root_style() == "awesome"

    def test_root_style_fallback(self, monkeypatch) -> None:
        """Should fall back to 'extra' if not configured."""
        monkeypatch.setitem(readme_config.CONFIG, "readme", {})
        assert get_root_style() == "extra"

    def test_root_style_missing_readme_section(self, monkeypatch) -> None:
        """Should fall back to 'extra' if readme section missing."""
        monkeypatch.delitem(readme_config.CONFIG, "readme", raising=False)
        assert get_root_style() == "extra"


class TestGetStyleSelectorTarget:
    """Tests for get_style_selector_target() function."""

    def test_root_style_goes_to_root(self) -> None:
        """The root style should always output to README.md."""
        root_style = get_root_style()
        path = get_style_selector_target(root_style)
        assert path == "README.md"

    def test_non_root_style_goes_to_alternatives(self) -> None:
        """Non-root styles should go to README_ALTERNATIVES/."""
        root_style = get_root_style()
        non_root_styles = [s for s in ["extra", "classic", "awesome", "flat"] if s != root_style]

        for style in non_root_styles:
            path = get_style_selector_target(style)
            assert path.startswith("README_ALTERNATIVES/"), (
                f"Style '{style}' should be in README_ALTERNATIVES/, got: {path}"
            )

    def test_style_swap_extra_to_alternatives(self, monkeypatch) -> None:
        """When awesome is root, extra should move to alternatives."""
        monkeypatch.setitem(readme_config.CONFIG, "readme", {"root_style": "awesome"})
        monkeypatch.setitem(
            readme_config.CONFIG,
            "styles",
            {
                "extra": {"filename": "README_EXTRA.md"},
                "awesome": {"filename": "README_AWESOME.md"},
            },
        )
        assert get_style_selector_target("awesome") == "README.md"
        assert get_style_selector_target("extra") == "README_ALTERNATIVES/README_EXTRA.md"

    def test_style_originally_in_alternatives_becomes_root(self, monkeypatch) -> None:
        """A style configured for alternatives can become root."""
        monkeypatch.setitem(readme_config.CONFIG, "readme", {"root_style": "classic"})
        monkeypatch.setitem(
            readme_config.CONFIG,
            "styles",
            {
                "classic": {"filename": "README_CLASSIC.md"},
                "extra": {"filename": "README_EXTRA.md"},
            },
        )
        assert get_style_selector_target("classic") == "README.md"


class TestGenerateStyleSelector:
    """Tests for generate_style_selector() function."""

    def test_root_readme_uses_assets_prefix(self, tmp_path: Path) -> None:
        """Root README should use 'assets/' prefix."""
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        resolved = _resolve_selector(html, tmp_path / "README.md", tmp_path)
        assert 'src="assets/' in resolved
        assert 'src="../assets/' not in resolved

    def test_alternatives_readme_uses_parent_assets_prefix(self, tmp_path: Path) -> None:
        """README in alternatives should use '../assets/' prefix."""
        html = generate_style_selector(
            "classic",
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )
        resolved = _resolve_selector(
            html,
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )
        assert 'src="../assets/' in resolved

    def test_root_readme_links_to_alternatives_with_full_path(self, tmp_path: Path) -> None:
        """Root README should link to alternatives with full path."""
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        assert "README_ALTERNATIVES/" in html

    def test_selector_uses_asset_tokens(self, tmp_path: Path) -> None:
        """Style selector should emit asset tokens, not concrete prefixes."""
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        assert "ASSET_PATH" in html
        assert "assets/" not in html

    def test_alternatives_readme_links_to_root_with_parent(self, tmp_path: Path) -> None:
        """Alternatives README should link to root with '../'."""
        html = generate_style_selector(
            "classic",
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )
        assert 'href="../"' in html

    def test_alternatives_readme_links_to_siblings_with_filename(self, tmp_path: Path) -> None:
        """Alternatives README should link to siblings with just filename."""
        html = generate_style_selector(
            "classic",
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )
        assert '.md"' in html

    def test_current_style_gets_highlight_border(self, tmp_path: Path) -> None:
        """Current style should have a highlight border."""
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        assert "border:" in html

    def test_selector_includes_all_styles_in_order(self, tmp_path: Path) -> None:
        """Selector should include all styles in configured order."""
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        assert "badge-style-extra.svg" in html
        assert "badge-style-classic.svg" in html
        assert "badge-style-flat.svg" in html
        assert "badge-style-awesome.svg" in html


class TestPathConsistency:
    """Tests for path consistency across different scenarios."""

    def test_asset_prefix_consistency(self, tmp_path: Path) -> None:
        """Asset prefix should be consistent based on output path."""
        root_html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        alt_html = generate_style_selector(
            "extra",
            tmp_path / "README_ALTERNATIVES" / "README_EXTRA.md",
            tmp_path,
        )
        root_resolved = _resolve_selector(root_html, tmp_path / "README.md", tmp_path)
        alt_resolved = _resolve_selector(
            alt_html,
            tmp_path / "README_ALTERNATIVES" / "README_EXTRA.md",
            tmp_path,
        )

        # Root uses assets/
        assert "assets/" in root_resolved
        # Alternatives uses ../assets/
        assert "../assets/" in alt_resolved

        # Root should NOT use ../assets/
        assert "../assets/" not in root_resolved

    def test_cross_linking_symmetry(self, tmp_path: Path) -> None:
        """Links should be symmetric - root to alt and alt to root."""
        root_html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        alt_html = generate_style_selector(
            "classic",
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )

        # Root links to alternatives with full path
        assert "README_ALTERNATIVES/" in root_html

        # Alternatives links back to root with ../
        assert 'href="../"' in alt_html


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_missing_style_config_handled(self, monkeypatch, tmp_path: Path) -> None:
        """Should handle missing style configuration gracefully."""
        monkeypatch.setitem(readme_config.CONFIG, "readme", {"root_style": "nonexistent"})
        monkeypatch.setitem(readme_config.CONFIG, "styles", {})
        monkeypatch.setitem(readme_config.CONFIG, "style_order", [])
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        assert isinstance(html, str)

    def test_unknown_style_id(self, tmp_path: Path) -> None:
        """Should handle unknown style ID gracefully."""
        html = generate_style_selector("unknown_style", tmp_path / "README.md", tmp_path)
        assert isinstance(html, str)


class TestAssumptionsDocumented:
    """
    Meta-tests that document the key assumptions.

    These tests serve as executable documentation of the assumptions
    the path-handling system relies on.
    """

    def test_assumption_readme_at_root_uses_assets_directly(self, tmp_path: Path) -> None:
        """
        ASSUMPTION: A README at repo root resolves assets via 'assets/'.

        This assumes the assets folder is a direct child of the repo root.
        """
        html = generate_style_selector("extra", tmp_path / "README.md", tmp_path)
        resolved = _resolve_selector(html, tmp_path / "README.md", tmp_path)
        assert "../assets/" not in resolved
        assert "assets/" in resolved

    def test_assumption_alternatives_one_level_deep(self, tmp_path: Path) -> None:
        """
        ASSUMPTION: README_ALTERNATIVES/ is exactly one level below root.

        This is why we resolve to '../assets/' for files in that folder.
        If README_ALTERNATIVES were nested deeper, paths would change.
        """
        html = generate_style_selector(
            "classic",
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )
        resolved = _resolve_selector(
            html,
            tmp_path / "README_ALTERNATIVES" / "README_CLASSIC.md",
            tmp_path,
        )
        assert "../assets/" in resolved
        assert "../../" not in resolved

    def test_assumption_root_style_is_root_readme(self) -> None:
        """
        ASSUMPTION: The root_style in config determines which README is at root.

        Changing root_style should move a different README to root.
        """
        root_style = get_root_style()
        path = get_style_selector_target(root_style)
        assert path == "README.md"

    def test_assumption_only_one_readme_at_root(self) -> None:
        """
        ASSUMPTION: Exactly one style lives at README.md (the root style).

        All other styles go to README_ALTERNATIVES/.
        """
        styles = ["extra", "classic", "awesome", "flat"]
        root_count = sum(1 for s in styles if get_style_selector_target(s) == "README.md")
        assert root_count == 1, "Exactly one style should be at root"

    def test_assumption_flat_is_special_case(self) -> None:
        """
        ASSUMPTION: Flat style has many files, linked via README_FLAT_ALL_AZ.md.

        The style selector links to this specific file as the entry point.
        """
        styles = CONFIG.get("styles", {})
        flat_config = styles.get("flat", {})
        filename = flat_config.get("filename", "")
        assert "FLAT" in filename.upper()
