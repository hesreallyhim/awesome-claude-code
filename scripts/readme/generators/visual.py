"""Visual README generator implementation."""

from scripts.readme.generators.base import ReadmeGenerator
from scripts.readme.markup.visual import (
    format_resource_entry as format_visual_resource_entry,
)
from scripts.readme.markup.visual import (
    generate_repo_ticker as generate_visual_repo_ticker,
)
from scripts.readme.markup.visual import (
    generate_section_content as generate_visual_section_content,
)
from scripts.readme.markup.visual import (
    generate_toc_from_categories as generate_visual_toc,
)
from scripts.readme.markup.visual import (
    generate_weekly_section as generate_visual_weekly_section,
)


class VisualReadmeGenerator(ReadmeGenerator):
    """Generator for visual/themed README variant with SVG assets."""

    @property
    def template_filename(self) -> str:
        return "README_EXTRA.template.md"

    @property
    def output_filename(self) -> str:
        return "README_ALTERNATIVES/README_EXTRA.md"

    @property
    def style_id(self) -> str:
        return "extra"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format resource with SVG badges and visible GitHub stats."""
        return format_visual_resource_entry(
            row,
            assets_dir=self.assets_dir,
            include_separator=include_separator,
        )

    def generate_toc(self) -> str:
        """Generate terminal-style SVG TOC."""
        return generate_visual_toc(
            self.categories,
            self.csv_data,
            self.general_anchor_map,
        )

    def generate_weekly_section(self) -> str:
        """Generate latest additions section with header SVG."""
        return generate_visual_weekly_section(self.csv_data, assets_dir=self.assets_dir)

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate section with SVG headers and desc boxes."""
        return generate_visual_section_content(
            category,
            self.csv_data,
            self.general_anchor_map,
            assets_dir=self.assets_dir,
            section_index=section_index,
        )

    def generate_repo_ticker(self) -> str:
        """Generate the animated SVG repo ticker for visual theme."""
        return generate_visual_repo_ticker()
