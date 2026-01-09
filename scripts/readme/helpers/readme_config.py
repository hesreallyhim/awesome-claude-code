"""Configuration loader for README generation."""

import os
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))


def load_config() -> dict:
    """Load configuration from acc-config.yaml."""
    config_path = REPO_ROOT / "acc-config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: acc-config.yaml not found at {config_path}, using defaults")
        return {
            "readme": {"root_style": "extra"},
            "styles": {
                "extra": {
                    "name": "Extra",
                    "badge": "badge-style-extra.svg",
                    "highlight_color": "#6a6a8a",
                    "filename": "README_EXTRA.md",
                },
                "classic": {
                    "name": "Classic",
                    "badge": "badge-style-classic.svg",
                    "highlight_color": "#c9a227",
                    "filename": "README_CLASSIC.md",
                },
                "awesome": {
                    "name": "Awesome",
                    "badge": "badge-style-awesome.svg",
                    "highlight_color": "#cc3366",
                    "filename": "README_AWESOME.md",
                },
                "flat": {
                    "name": "Flat",
                    "badge": "badge-style-flat.svg",
                    "highlight_color": "#71717a",
                    "filename": "README_FLAT_ALL_AZ.md",
                },
            },
            "style_order": ["extra", "classic", "flat", "awesome"],
        }


# Global config instance
CONFIG = load_config()


def get_root_style() -> str:
    """Get the root README style from config."""
    readme_config = CONFIG.get("readme", {})
    return readme_config.get("root_style") or readme_config.get("default_style", "extra")


def get_style_selector_target(style_id: str) -> str:
    """Get the selector link target for a style, accounting for root style config."""
    root_style = get_root_style()
    styles = CONFIG.get("styles", {})
    style_config = styles.get(style_id, {})
    filename = style_config.get("filename")
    if not filename:
        if style_id == "flat":
            filename = "README_FLAT_ALL_AZ.md"
        else:
            filename = f"README_{style_id.upper()}.md"
    filename = os.path.basename(filename)

    if style_id == root_style:
        return "README.md"
    return f"README_ALTERNATIVES/{filename}"
