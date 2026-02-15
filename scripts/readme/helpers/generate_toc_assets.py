"""Regenerate subcategory TOC SVGs from categories.yaml.

Run after adding or modifying subcategories in templates/categories.yaml
to create/update the corresponding TOC row SVG assets used by the
Visual (Extra) README style.

Usage:
    python -m scripts.readme.generate_toc_assets
"""

from pathlib import Path

from scripts.categories.category_utils import category_manager
from scripts.readme.helpers.readme_assets import regenerate_sub_toc_svgs
from scripts.utils.repo_root import find_repo_root


def main() -> None:
    repo_root = find_repo_root(Path(__file__))
    assets_dir = str(repo_root / "assets")
    categories = category_manager.get_categories_for_readme()
    regenerate_sub_toc_svgs(categories, assets_dir)
    print("✅ Subcategory TOC SVGs regenerated")


if __name__ == "__main__":
    main()
