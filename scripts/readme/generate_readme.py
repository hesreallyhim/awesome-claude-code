#!/usr/bin/env python3
"""
Template-based README generator for the Awesome Claude Code repository.
Reads resource metadata from CSV and generates README using templates.
"""

import sys
from pathlib import Path

from scripts.readme.generators.awesome import AwesomeReadmeGenerator
from scripts.readme.generators.base import ReadmeGenerator
from scripts.readme.generators.flat import (
    FLAT_CATEGORIES,
    FLAT_SORT_TYPES,
    ParameterizedFlatListGenerator,
)
from scripts.readme.generators.minimal import MinimalReadmeGenerator
from scripts.readme.generators.visual import VisualReadmeGenerator
from scripts.readme.helpers.readme_assets import generate_flat_badges
from scripts.readme.helpers.readme_config import get_root_style
from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))

STYLE_GENERATORS: dict[str, type[ReadmeGenerator]] = {
    "extra": VisualReadmeGenerator,
    "classic": MinimalReadmeGenerator,
    "awesome": AwesomeReadmeGenerator,
    "flat": ParameterizedFlatListGenerator,
}

PRIMARY_STYLE_IDS = tuple(
    style_id
    for style_id, generator_cls in STYLE_GENERATORS.items()
    if generator_cls is not ParameterizedFlatListGenerator
)


def build_root_generator(
    style_id: str,
    csv_path: str,
    template_dir: str,
    assets_dir: str,
    repo_root: str,
) -> ReadmeGenerator:
    """Return the generator instance for a root style."""
    style_id = style_id.lower()
    generator_cls = STYLE_GENERATORS.get(style_id)
    if generator_cls is None:
        raise ValueError(f"Unknown root style: {style_id}")
    if generator_cls is ParameterizedFlatListGenerator:
        return ParameterizedFlatListGenerator(
            csv_path,
            template_dir,
            assets_dir,
            repo_root,
            category_slug="all",
            sort_type="az",
        )
    return generator_cls(csv_path, template_dir, assets_dir, repo_root)


def main():
    """Main entry point - generates all README versions."""
    repo_root = REPO_ROOT

    csv_path = str(repo_root / "THE_RESOURCES_TABLE.csv")
    template_dir = str(repo_root / "templates")
    assets_dir = str(repo_root / "assets")

    print("=== README Generation ===")

    # Generate flat list badges first
    print("\n--- Generating flat list badges ---")
    generate_flat_badges(assets_dir, FLAT_SORT_TYPES, FLAT_CATEGORIES)
    print("✅ Flat list badges generated")

    # Generate primary styles under README_ALTERNATIVES/
    main_generators = [
        STYLE_GENERATORS[style_id](csv_path, template_dir, assets_dir, str(repo_root))
        for style_id in PRIMARY_STYLE_IDS
    ]

    for generator in main_generators:
        resolved_path = generator.resolved_output_path
        print(f"\n--- Generating {resolved_path} ---")
        try:
            resource_count, backup_path = generator.generate()
            print(f"✅ {resolved_path} generated successfully")
            print(f"📊 Generated with {resource_count} active resources")
            if backup_path:
                print(f"📁 Backup saved at: {backup_path}")
        except Exception as e:
            print(f"❌ Error generating {resolved_path}: {e}")
            sys.exit(1)

    # Generate all flat list combinations (categories × sort types = 44 files)
    print("\n--- Generating flat list views ---")
    flat_count = 0
    for category_slug in FLAT_CATEGORIES:
        for sort_type in FLAT_SORT_TYPES:
            generator = ParameterizedFlatListGenerator(
                csv_path,
                template_dir,
                assets_dir,
                str(repo_root),
                category_slug=category_slug,
                sort_type=sort_type,
            )
            try:
                resource_count, _ = generator.generate()
                flat_count += 1
                # Only print summary for first of each category
                if sort_type == "az":
                    print(f"  📂 {category_slug}: {resource_count} resources")
            except Exception as e:
                print(f"❌ Error generating {generator.output_filename}: {e}")
                sys.exit(1)

    print(f"✅ Generated {flat_count} flat list views")

    # Generate root README after all alternatives exist
    root_style = get_root_style()
    root_generator = build_root_generator(
        root_style,
        csv_path,
        template_dir,
        assets_dir,
        str(repo_root),
    )
    print(f"\n--- Generating README.md (root style: {root_style}) ---")
    try:
        resource_count, backup_path = root_generator.generate(output_path="README.md")
        print("✅ README.md generated successfully")
        print(f"📊 Generated with {resource_count} active resources")
        if backup_path:
            print(f"📁 Backup saved at: {backup_path}")
    except Exception as e:
        print(f"❌ Error generating README.md: {e}")
        sys.exit(1)

    print("\n=== Generation Complete ===")


if __name__ == "__main__":
    main()
