"""Awesome README generator implementation."""

from scripts.readme.generators.base import ReadmeGenerator
from scripts.readme.markup.awesome import (
    format_resource_entry as format_awesome_resource_entry,
)
from scripts.readme.markup.awesome import (
    generate_repo_ticker as generate_awesome_repo_ticker,
)
from scripts.readme.markup.awesome import (
    generate_section_content as generate_awesome_section_content,
)
from scripts.readme.markup.awesome import (
    generate_toc as generate_awesome_toc,
)
from scripts.readme.markup.awesome import (
    generate_weekly_section as generate_awesome_weekly_section,
)


class AwesomeReadmeGenerator(ReadmeGenerator):
    """Generator for awesome-list-style README variant with clean markdown formatting."""

    @property
    def template_filename(self) -> str:
        return "README_AWESOME.template.md"

    @property
    def output_filename(self) -> str:
        return "README_ALTERNATIVES/README_AWESOME.md"

    @property
    def style_id(self) -> str:
        return "awesome"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format resource in awesome list style: - [Name](url) by [Author](link) - Description."""
        return format_awesome_resource_entry(row, include_separator=include_separator)

    def generate_toc(self) -> str:
        """Generate plain markdown TOC for awesome list style."""
        return generate_awesome_toc(self.categories, self.csv_data)

    def generate_weekly_section(self) -> str:
        """Generate weekly section with plain markdown for awesome list."""
        return generate_awesome_weekly_section(self.csv_data)

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate section with plain markdown headers in awesome list format."""
        _ = section_index
        return generate_awesome_section_content(category, self.csv_data)

    def generate_repo_ticker(self) -> str:
        """Generate the awesome-style animated SVG repo ticker."""
        return generate_awesome_repo_ticker()
