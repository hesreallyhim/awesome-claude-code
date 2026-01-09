"""Tests for readme config file resolution."""

import contextlib
import sys
from pathlib import Path

import yaml

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))


from scripts.readme.helpers import readme_config  # noqa: E402


def _load_root_style(repo_root: Path) -> str:
    config_path = repo_root / "acc-config.yaml"
    with config_path.open(encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    return config.get("readme", {}).get("root_style", "extra")


def test_load_config_uses_repo_root() -> None:
    """load_config should read acc-config.yaml from repo root, not scripts/."""
    root_style = _load_root_style(repo_root)
    conflicting_root = "classic" if root_style != "classic" else "extra"

    scripts_config_path = repo_root / "scripts" / "acc-config.yaml"
    existing_contents = None
    if scripts_config_path.exists():
        existing_contents = scripts_config_path.read_text(encoding="utf-8")

    try:
        scripts_config = {"readme": {"root_style": conflicting_root}}
        scripts_config_path.write_text(
            yaml.safe_dump(scripts_config, sort_keys=True),
            encoding="utf-8",
        )
        config = readme_config.load_config()
        assert config.get("readme", {}).get("root_style", "extra") == root_style
    finally:
        if existing_contents is None:
            with contextlib.suppress(FileNotFoundError):
                scripts_config_path.unlink()
        else:
            scripts_config_path.write_text(existing_contents, encoding="utf-8")
