"""Minimal README generator implementation."""

from scripts.readme.generators.base import ReadmeGenerator
from scripts.readme.markup.minimal import (
    format_resource_entry as format_minimal_resource_entry,
)
from scripts.readme.markup.minimal import (
    generate_section_content as generate_minimal_section_content,
)
from scripts.readme.markup.minimal import (
    generate_toc as generate_minimal_toc,
)
from scripts.readme.markup.minimal import (
    generate_weekly_section as generate_minimal_weekly_section,
)


class MinimalReadmeGenerator(ReadmeGenerator):
    """Generator for plain markdown README classic variant."""

    @property
    def template_filename(self) -> str:
        return "README_CLASSIC.template.md"

    @property
    def output_filename(self) -> str:
        return "README_ALTERNATIVES/README_CLASSIC.md"

    @property
    def style_id(self) -> str:
        return "classic"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format resource as plain markdown with collapsible GitHub stats."""
        return format_minimal_resource_entry(row, include_separator=include_separator)

    def generate_toc(self) -> str:
        """Generate plain markdown nested details TOC."""
        return generate_minimal_toc(self.categories, self.csv_data)

    def generate_weekly_section(self) -> str:
        """Generate weekly section with plain markdown."""
        return generate_minimal_weekly_section(self.csv_data)

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate section with plain markdown headers."""
        _ = section_index
        return generate_minimal_section_content(category, self.csv_data)
