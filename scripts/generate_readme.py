#!/usr/bin/env python3
"""
Template-based README generator for the Awesome Claude Code repository.
Reads resource metadata from CSV and generates README using templates.
"""

import csv
import glob
import os
import re
import shutil
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from validate_links import parse_github_url  # type: ignore[import-not-found]


# =============================================================================
# FLAT LIST CONFIGURATION
# =============================================================================

# Category definitions: slug -> (csv_value, display_name, badge_color)
FLAT_CATEGORIES = {
    "all": (None, "All", "#71717a"),
    "tooling": ("Tooling", "Tooling", "#3b82f6"),
    "commands": ("Slash-Commands", "Commands", "#8b5cf6"),
    "claude-md": ("CLAUDE.md Files", "CLAUDE.md", "#ec4899"),
    "workflows": ("Workflows & Knowledge Guides", "Workflows", "#14b8a6"),
    "hooks": ("Hooks", "Hooks", "#f97316"),
    "skills": ("Agent Skills", "Skills", "#eab308"),
    "styles": ("Output Styles", "Styles", "#06b6d4"),
    "statusline": ("Status Lines", "Status", "#84cc16"),
    "docs": ("Official Documentation", "Docs", "#6366f1"),
    "clients": ("Alternative Clients", "Clients", "#f43f5e"),
}

# Sort type definitions: slug -> (display_name, badge_color, description)
FLAT_SORT_TYPES = {
    "az": ("A - Z", "#6366f1", "alphabetically by name"),
    "updated": ("UPDATED", "#f472b6", "by last updated date"),
    "created": ("CREATED", "#34d399", "by date created"),
    "releases": ("RELEASES", "#f59e0b", "by latest release (30 days)"),
}


def load_template(template_path):
    """Load a template file."""
    with open(template_path, encoding="utf-8") as f:
        return f.read()


def create_h2_svg_file(text: str, filename: str, assets_dir: str, icon: str = "") -> str:
    """Create an animated hero-centered H2 header SVG file.

    Args:
        text: The header text (e.g., "Agent Skills")
        filename: The output filename
        assets_dir: Directory to save the SVG
        icon: Optional emoji icon to append (e.g., "🤖")

    Returns:
        The filename of the created SVG
    """
    # Build display text with optional icon
    display_text = f"{text} {icon}" if icon else text

    # Escape XML special characters
    text_escaped = display_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Calculate viewBox bounds based on text length
    # Text is centered at x=400, font-size 38px ≈ 22px per char, emoji ≈ 50px
    text_width = len(text) * 22 + (50 if icon else 0)
    half_text = text_width / 2
    # Ensure we include decorations (x=187 to x=613) plus text bounds with generous padding
    left_bound = int(min(180, 400 - half_text - 30))
    right_bound = int(max(620, 400 + half_text + 30))
    viewbox_width = right_bound - left_bound

    svg_content = f"""<svg width="100%" height="100" viewBox="{left_bound} 0 {viewbox_width} 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Subtle glow for hero text - reduced blur for better readability -->
    <filter id="heroGlow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Hero gradient - brighter, more saturated colors for contrast -->
    <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF8855" stop-opacity="1">
        <animate attributeName="stop-color" values="#FF8855;#FFAA77;#FF8855" dur="5s" repeatCount="indefinite"/>
      </stop>
      <stop offset="50%" stop-color="#FFAA77" stop-opacity="1"/>
      <stop offset="100%" stop-color="#FF8855" stop-opacity="1">
        <animate attributeName="stop-color" values="#FF8855;#FFCC99;#FF8855" dur="5s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>

    <!-- Accent line gradient -->
    <linearGradient id="accentLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FFB088" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FF8855" stop-opacity="1">
        <animate attributeName="stop-opacity" values="0.8;1;0.8" dur="3s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="#FFB088" stop-opacity="0"/>
    </linearGradient>

    <!-- Radial glow background - more subtle -->
    <radialGradient id="bgGlow">
      <stop offset="0%" stop-color="#FF8C5A" stop-opacity="0.08">
        <animate attributeName="stop-opacity" values="0.05;0.12;0.05" dur="4s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="#FF8C5A" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Background glow - more subtle -->
  <ellipse cx="400" cy="50" rx="300" ry="40" fill="url(#bgGlow)"/>

  <!-- Top accent line -->
  <line x1="200" y1="20" x2="600" y2="20" stroke="url(#accentLine)" stroke-width="2" stroke-linecap="round">
    <animate attributeName="stroke-width" values="2;2.5;2" dur="3s" repeatCount="indefinite"/>
  </line>

  <!-- Main hero text - larger, bolder, with subtle dark outline for contrast -->
  <text x="400" y="58" font-family="system-ui, -apple-system, sans-serif" font-size="38" font-weight="900" fill="url(#heroGrad)" text-anchor="middle" filter="url(#heroGlow)" letter-spacing="0.5" stroke="#221111" stroke-width="0.5" paint-order="stroke fill">
    {text_escaped}
  </text>

  <!-- Bottom accent line -->
  <line x1="200" y1="80" x2="600" y2="80" stroke="url(#accentLine)" stroke-width="2" stroke-linecap="round">
    <animate attributeName="stroke-width" values="2;2.5;2" dur="3s" begin="1.5s" repeatCount="indefinite"/>
  </line>

  <!-- Decorative corner elements -->
  <g opacity="0.6">
    <!-- Top left -->
    <path d="M 195,16 L 195,24 M 195,20 L 187,20" stroke="#FF8855" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" repeatCount="indefinite"/>
    </path>
    <!-- Top right -->
    <path d="M 605,16 L 605,24 M 605,20 L 613,20" stroke="#FF8855" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="0.5s" repeatCount="indefinite"/>
    </path>
    <!-- Bottom left -->
    <path d="M 195,76 L 195,84 M 195,80 L 187,80" stroke="#FFAA77" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="1s" repeatCount="indefinite"/>
    </path>
    <!-- Bottom right -->
    <path d="M 605,76 L 605,84 M 605,80 L 613,80" stroke="#FFAA77" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="1.5s" repeatCount="indefinite"/>
    </path>
  </g>

  <!-- Floating accent particles - reduced opacity -->
  <g opacity="0.35">
    <circle cx="250" cy="35" r="2" fill="#FFCBA4">
      <animate attributeName="cy" values="35;30;35" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.5;0" dur="4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="550" cy="45" r="2.5" fill="#FFB088">
      <animate attributeName="cy" values="45;40;45" dur="4.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.6;0" dur="4.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="320" cy="68" r="1.5" fill="#FF9B70">
      <animate attributeName="cy" values="68;63;68" dur="3.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.4;0" dur="3.5s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>"""

    # Write SVG file
    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def create_h3_svg_file(text, filename, assets_dir):
    """Create an animated minimal-inline H3 header SVG file."""
    # Escape XML special characters
    text_escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Calculate approximate text width (rough estimate: 10px per character for 18px font)
    text_width = len(text) * 10
    total_width = text_width + 50  # Add padding for decorative elements

    svg_content = f"""<svg width="100%" height="36" viewBox="0 0 {total_width} 36" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Very subtle glow -->
    <filter id="minimalGlow">
      <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Simple gradient -->
    <linearGradient id="minimalGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF6B35" stop-opacity="1"/>
      <stop offset="100%" stop-color="#8B5A3C" stop-opacity="1"/>
    </linearGradient>
  </defs>

  <!-- Left decorative element -->
  <g>
    <line x1="0" y1="18" x2="12" y2="18" stroke="#FF6B35" stroke-width="3" stroke-linecap="round" opacity="0.8">
      <animate attributeName="x2" values="12;16;12" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;1;0.7" dur="3s" repeatCount="indefinite"/>
    </line>
    <circle cx="18" cy="18" r="2" fill="#FF8C5A" opacity="0.7">
      <animate attributeName="r" values="2;2.5;2" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.6;0.9;0.6" dur="3s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- Header text -->
  <text x="30" y="24" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="600" fill="url(#minimalGrad)" filter="url(#minimalGlow)">
    {text_escaped}
    <animate attributeName="opacity" values="0.93;1;0.93" dur="4s" repeatCount="indefinite"/>
  </text>
</svg>"""

    # Write SVG file
    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def load_announcements(template_dir):
    """Load announcements from the announcements.yaml file and format as markdown."""
    announcements_path = os.path.join(template_dir, "announcements.yaml")
    if os.path.exists(announcements_path):
        with open(announcements_path, encoding="utf-8") as f:
            announcements_data = yaml.safe_load(f)

        if not announcements_data:
            return ""

        # Format the YAML data into markdown with nested collapsible sections using lists
        markdown_lines = []

        # Add the announcements header
        markdown_lines.append("### Announcements [🔝](#awesome-claude-code)")
        markdown_lines.append("")

        # Make the entire announcements section collapsible (open by default)
        markdown_lines.append("<details open>")
        markdown_lines.append("<summary>View Announcements</summary>")
        markdown_lines.append("")

        # Use unordered list for first level indentation
        for entry in announcements_data:
            date = entry.get("date", "")
            title = entry.get("title", "")
            items = entry.get("items", [])

            # Make each date group a collapsible list item (open by default)
            markdown_lines.append("- <details open>")

            # Create summary for date group
            if title:
                markdown_lines.append(f"  <summary>{date} - {title}</summary>")
            else:
                markdown_lines.append(f"  <summary>{date}</summary>")

            markdown_lines.append("")

            # Use nested list for second level indentation
            # Process items - can be strings or objects with summary/text
            for item in items:
                if isinstance(item, str):
                    # Simple string item - render as nested bullet point
                    markdown_lines.append(f"  - {item}")
                elif isinstance(item, dict):
                    # Object with summary and text - render as collapsible details
                    summary = item.get("summary", "")
                    text = item.get("text", "")

                    if summary and text:
                        markdown_lines.append("  - <details open>")
                        markdown_lines.append(f"    <summary>{summary}</summary>")
                        markdown_lines.append("")

                        # Handle multi-line text properly with triple nesting
                        text_lines = text.strip().split("\n")
                        for i, line in enumerate(text_lines):
                            if i == 0:
                                markdown_lines.append(f"    - {line}")
                            else:
                                # Continue paragraphs without bullet points
                                markdown_lines.append(f"      {line}")

                        markdown_lines.append("")
                        markdown_lines.append("    </details>")
                    elif summary:
                        # If only summary, just render as nested bullet point
                        markdown_lines.append(f"  - {summary}")
                    elif text:
                        # If only text, render as nested bullet point
                        markdown_lines.append(f"  - {text}")

                markdown_lines.append("")

            # Close date group details
            markdown_lines.append("  </details>")
            markdown_lines.append("")

        # Close main announcements details
        markdown_lines.append("</details>")

        return "\n".join(markdown_lines).strip()

    return ""


def get_anchor_suffix_for_icon(icon):
    """
    Generate the appropriate anchor suffix for a section with an emoji icon.

    GitHub's markdown anchor generation for trailing emojis:
    1. Simple emojis (single Unicode codepoint): Stripped and replaced with a
       single dash "-"
    2. Emojis with variation selectors (U+FE00-FE0F): Base emoji is stripped
       and replaced with dash, variation selector becomes URL-encoded

    For example:
    - "## Tooling 🧰" → #tooling- (simple emoji becomes dash)
    - "## Official Documentation 🏛️" → #official-documentation-%EF%B8%8F
      (emoji becomes dash, VS-16 is URL-encoded)

    The 🏛️ emoji is actually two characters:
    - U+1F3DB (🏛) - Classical Building base character
    - U+FE0F - Variation Selector-16 (forces emoji presentation)

    Unicode has 16 variation selectors (U+FE00 to U+FE0F):
    - VS-1 to VS-15 (U+FE00-FE0E): Rarely used with emojis
    - VS-16 (U+FE0F): Common, forces colorful emoji presentation

    Args:
        icon: The emoji icon string from the category definition

    Returns:
        The appropriate suffix for the anchor link
        Examples: "-", "-%EF%B8%8F", "-%EF%B8%80", etc.
    """
    if not icon:
        # No icon means no suffix needed
        return ""

    # Check for any variation selector (U+FE00 to U+FE0F)
    # Note: We return after finding the first VS, as emojis typically have
    # only one variation selector. Multiple VSs in a single icon would be
    # extremely rare and likely invalid Unicode.
    vs_char = next((char for char in icon if 0xFE00 <= ord(char) <= 0xFE0F), None)
    if vs_char:
        # Found a variation selector - URL-encode it
        vs_bytes = vs_char.encode("utf-8")
        url_encoded = "".join(f"%{byte:02X}" for byte in vs_bytes)
        return f"-{url_encoded}"

    # No variation selector found - simple emoji gets replaced with dash
    return "-"


# =============================================================================
# SVG GENERATORS - Auto-generate assets for new categories/subcategories
# =============================================================================


def generate_category_header_light_svg(title, section_number="01"):
    """Generate a light-mode category header SVG in vintage technical manual style.

    Args:
        title: The category title (e.g., "Agent Skills", "Tooling")
        section_number: Two-digit section number (e.g., "01", "02")
    """
    # Escape XML special characters
    title_escaped = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Calculate text width for positioning
    title_width = len(title) * 14  # Approximate width per character
    line_end_x = max(640, 220 + title_width + 50)

    return f"""<svg width="100%" height="80" viewBox="150 0 500 80" xmlns="http://www.w3.org/2000/svg">
  <!--
    Vintage Technical Manual Style - Header (Auto-generated)
    Clean, authoritative, reference manual aesthetic
  -->

  <!-- Section number box -->
  <g>
    <rect x="160" y="22" width="36" height="36" fill="none" stroke="#5c5247" stroke-width="2" opacity="0.6"/>
    <text x="178" y="48"
          font-family="'Courier New', Courier, monospace"
          font-size="20"
          font-weight="700"
          fill="#c96442"
          text-anchor="middle">
      {section_number}
    </text>
  </g>

  <!-- Main title -->
  <text x="220" y="47"
        font-family="system-ui, -apple-system, 'Helvetica Neue', sans-serif"
        font-size="28"
        font-weight="600"
        fill="#3d3530"
        letter-spacing="0.5">
    {title_escaped}
  </text>

  <!-- Horizontal rule extending from title -->
  <line x1="220" y1="58" x2="{line_end_x}" y2="58" stroke="#5c5247" stroke-width="1.75" opacity="0.45"/>

  <!-- Reference dots pattern (like page markers) -->
  <g fill="#5c5247" opacity="0.3">
    <circle cx="{line_end_x - 60}" cy="35" r="1"/>
    <circle cx="{line_end_x - 45}" cy="35" r="1"/>
    <circle cx="{line_end_x - 30}" cy="35" r="1"/>
    <circle cx="{line_end_x - 15}" cy="35" r="1"/>
    <circle cx="{line_end_x}" cy="35" r="1"/>
  </g>

  <!-- Thin top line -->
  <line x1="160" y1="15" x2="{line_end_x}" y2="15" stroke="#5c5247" stroke-width="1.75" opacity="0.45"/>
</svg>"""


def generate_section_divider_light_svg(variant=1):
    """Generate a light-mode section divider SVG.

    Args:
        variant: 1, 2, or 3 for different styles
    """
    if variant == 1:
        # Diagram/schematic style with nodes
        return """<svg width="900" height="40" xmlns="http://www.w3.org/2000/svg">
  <!-- Vintage Technical Manual Style - Diagram Variant (BOLD) -->

  <!-- Ghost line for layered effect -->
  <line x1="82" y1="18" x2="818" y2="18" stroke="#5c5247" stroke-width="1.5" opacity="0.2"/>

  <!-- Main horizontal rule -->
  <line x1="80" y1="20" x2="820" y2="20" stroke="#5c5247" stroke-width="1.75" opacity="0.65"/>

  <!-- Technical node markers along the line -->
  <g fill="none" stroke="#5c5247">
    <!-- Left terminal node -->
    <circle cx="80" cy="20" r="5" stroke-width="1.5" opacity="0.7"/>
    <circle cx="80" cy="20" r="2.5" fill="#5c5247" opacity="0.55"/>
    <circle cx="82" cy="22" r="1.5" fill="#5c5247" opacity="0.25"/>

    <!-- Intermediate nodes -->
    <circle cx="200" cy="20" r="3.5" stroke-width="1.25" opacity="0.55"/>
    <circle cx="350" cy="20" r="3.5" stroke-width="1.25" opacity="0.55"/>

    <!-- Center node - emphasized -->
    <circle cx="450" cy="20" r="6" stroke-width="1.5" opacity="0.65"/>
    <circle cx="450" cy="20" r="3.5" fill="#c96442" opacity="0.75"/>
    <circle cx="452" cy="22" r="2" fill="#c96442" opacity="0.35"/>

    <!-- Intermediate nodes -->
    <circle cx="550" cy="20" r="3.5" stroke-width="1.25" opacity="0.55"/>
    <circle cx="700" cy="20" r="3.5" stroke-width="1.25" opacity="0.55"/>

    <!-- Right terminal node -->
    <circle cx="820" cy="20" r="5" stroke-width="1.5" opacity="0.7"/>
    <circle cx="820" cy="20" r="2.5" fill="#5c5247" opacity="0.55"/>
    <circle cx="818" cy="22" r="1.5" fill="#5c5247" opacity="0.25"/>
  </g>

  <!-- Measurement ticks -->
  <g stroke="#5c5247" opacity="0.4">
    <line x1="140" y1="15" x2="140" y2="25" stroke-width="1"/>
    <line x1="142" y1="16" x2="142" y2="24" stroke-width="0.75" opacity="0.5"/>
    <line x1="260" y1="15" x2="260" y2="25" stroke-width="1"/>
    <line x1="380" y1="15" x2="380" y2="25" stroke-width="1"/>
    <line x1="382" y1="16" x2="382" y2="24" stroke-width="0.75" opacity="0.5"/>
    <line x1="520" y1="15" x2="520" y2="25" stroke-width="1"/>
    <line x1="640" y1="15" x2="640" y2="25" stroke-width="1"/>
    <line x1="642" y1="16" x2="642" y2="24" stroke-width="0.75" opacity="0.5"/>
    <line x1="760" y1="15" x2="760" y2="25" stroke-width="1"/>
  </g>

  <!-- Directional arrows at ends -->
  <g stroke="#5c5247" stroke-width="1.5" fill="none" opacity="0.5">
    <path d="M 52 20 L 65 20 M 58 15 L 65 20 L 58 25"/>
    <path d="M 848 20 L 835 20 M 842 15 L 835 20 L 842 25"/>
  </g>
</svg>"""

    elif variant == 2:
        # Wave/organic style
        return """<svg width="900" height="40" xmlns="http://www.w3.org/2000/svg">
  <!-- Vintage Technical Manual Style - Wave Variant -->

  <!-- Ghost wave -->
  <path d="M 50 22 Q 150 12, 250 20 T 450 18 T 650 22 T 850 18"
        fill="none" stroke="#5c5247" stroke-width="1" opacity="0.2"/>

  <!-- Main wave line -->
  <path d="M 50 20 Q 150 10, 250 18 T 450 16 T 650 20 T 850 16"
        fill="none" stroke="#5c5247" stroke-width="1.75" opacity="0.5"/>

  <!-- Circle accents -->
  <g fill="#5c5247">
    <circle cx="50" cy="20" r="4" opacity="0.5"/>
    <circle cx="52" cy="22" r="2" opacity="0.25"/>
    <circle cx="250" cy="18" r="3" opacity="0.35"/>
    <circle cx="450" cy="16" r="4" opacity="0.45"/>
    <circle cx="452" cy="18" r="2.5" fill="#c96442" opacity="0.6"/>
    <circle cx="650" cy="20" r="3" opacity="0.35"/>
    <circle cx="850" cy="16" r="4" opacity="0.5"/>
    <circle cx="848" cy="18" r="2" opacity="0.25"/>
  </g>

  <!-- Tick marks -->
  <g stroke="#5c5247" opacity="0.35">
    <line x1="150" y1="12" x2="150" y2="24" stroke-width="1.25"/>
    <line x1="350" y1="14" x2="350" y2="22" stroke-width="1.25"/>
    <line x1="550" y1="14" x2="550" y2="24" stroke-width="1.25"/>
    <line x1="750" y1="12" x2="750" y2="22" stroke-width="1.25"/>
  </g>
</svg>"""

    else:  # variant == 3
        # Bracket style with layered drafts
        return """<svg width="900" height="40" xmlns="http://www.w3.org/2000/svg">
  <!-- Vintage Technical Manual Style - Bracket Variant -->

  <!-- Ghost lines -->
  <line x1="82" y1="18" x2="818" y2="18" stroke="#5c5247" stroke-width="1" opacity="0.15"/>

  <!-- Main horizontal line -->
  <line x1="80" y1="20" x2="820" y2="20" stroke="#5c5247" stroke-width="1.75" opacity="0.5"/>

  <!-- Corner brackets - left -->
  <g fill="none" stroke="#5c5247">
    <path d="M 50,20 L 50,35 M 50,20 L 80,20" stroke-width="2" opacity="0.5"/>
    <path d="M 53,18 L 53,33 M 53,18 L 78,18" stroke-width="1" opacity="0.2"/>
  </g>

  <!-- Corner brackets - right -->
  <g fill="none" stroke="#5c5247">
    <path d="M 850,20 L 850,35 M 850,20 L 820,20" stroke-width="2" opacity="0.5"/>
    <path d="M 847,18 L 847,33 M 847,18 L 822,18" stroke-width="1" opacity="0.2"/>
  </g>

  <!-- Corner dots -->
  <g fill="#5c5247">
    <circle cx="50" cy="20" r="4" opacity="0.45"/>
    <circle cx="52" cy="22" r="2" opacity="0.2"/>
    <circle cx="850" cy="20" r="4" opacity="0.45"/>
    <circle cx="848" cy="22" r="2" opacity="0.2"/>
  </g>

  <!-- Center accent -->
  <circle cx="450" cy="20" r="5" fill="none" stroke="#5c5247" stroke-width="1.5" opacity="0.5"/>
  <circle cx="450" cy="20" r="2.5" fill="#c96442" opacity="0.6"/>

  <!-- Tick marks with doubles -->
  <g stroke="#5c5247" opacity="0.35">
    <line x1="180" y1="14" x2="180" y2="26" stroke-width="1.25"/>
    <line x1="182" y1="15" x2="182" y2="25" stroke-width="0.75" opacity="0.5"/>
    <line x1="320" y1="15" x2="320" y2="25" stroke-width="1.25"/>
    <line x1="580" y1="15" x2="580" y2="25" stroke-width="1.25"/>
    <line x1="720" y1="14" x2="720" y2="26" stroke-width="1.25"/>
    <line x1="722" y1="15" x2="722" y2="25" stroke-width="0.75" opacity="0.5"/>
  </g>
</svg>"""


def generate_desc_box_light_svg(position="top"):
    """Generate a light-mode description box SVG (top or bottom).

    Args:
        position: "top" or "bottom"
    """
    if position == "top":
        return """<svg width="900" height="40" xmlns="http://www.w3.org/2000/svg">
  <!-- Vintage Technical Manual - BOLD layered drafts (top) -->

  <!-- Ghost/draft lines -->
  <line x1="30" y1="13" x2="870" y2="13" stroke="#5c5247" stroke-width="1.5" opacity="0.15"/>
  <line x1="26" y1="17" x2="875" y2="17" stroke="#5c5247" stroke-width="1" opacity="0.12"/>

  <!-- Main horizontal line -->
  <line x1="28" y1="15" x2="872" y2="15" stroke="#5c5247" stroke-width="2" opacity="0.5"/>

  <!-- Secondary lines - partial, offset -->
  <line x1="45" y1="21" x2="620" y2="21" stroke="#5c5247" stroke-width="1" opacity="0.25"/>
  <line x1="48" y1="23" x2="580" y2="23" stroke="#5c5247" stroke-width="0.75" opacity="0.15"/>

  <!-- Short accent lines on right -->
  <line x1="720" y1="10" x2="850" y2="10" stroke="#5c5247" stroke-width="1" opacity="0.22"/>
  <line x1="740" y1="8" x2="830" y2="8" stroke="#5c5247" stroke-width="0.75" opacity="0.12"/>

  <!-- Bold tick marks -->
  <g stroke="#5c5247" opacity="0.4">
    <line x1="95" y1="8" x2="95" y2="26" stroke-width="1.5"/>
    <line x1="97" y1="9" x2="97" y2="24" stroke-width="1" opacity="0.5"/>
    <line x1="175" y1="10" x2="175" y2="22" stroke-width="1.5"/>
    <line x1="270" y1="7" x2="270" y2="27" stroke-width="1.5"/>
    <line x1="272" y1="9" x2="272" y2="25" stroke-width="1" opacity="0.5"/>
    <line x1="390" y1="9" x2="390" y2="24" stroke-width="1.5"/>
    <line x1="530" y1="10" x2="530" y2="23" stroke-width="1.5"/>
    <line x1="600" y1="7" x2="600" y2="27" stroke-width="1.5"/>
    <line x1="720" y1="9" x2="720" y2="24" stroke-width="1.5"/>
    <line x1="820" y1="7" x2="820" y2="27" stroke-width="1.5"/>
  </g>

  <!-- Bold circles -->
  <g fill="#5c5247">
    <circle cx="130" cy="15" r="3" opacity="0.35"/>
    <circle cx="133" cy="17" r="2" opacity="0.2"/>
    <circle cx="330" cy="16" r="2.5" opacity="0.3"/>
    <circle cx="480" cy="15" r="3.5" opacity="0.35"/>
    <circle cx="560" cy="17" r="2" opacity="0.28"/>
    <circle cx="660" cy="15" r="3" opacity="0.32"/>
    <circle cx="790" cy="14" r="2.5" opacity="0.3"/>
  </g>

  <!-- Corner dots -->
  <g fill="#5c5247">
    <circle cx="20" cy="15" r="5" opacity="0.5"/>
    <circle cx="22" cy="17" r="3" opacity="0.25"/>
    <circle cx="880" cy="15" r="5" opacity="0.5"/>
    <circle cx="878" cy="17" r="3" opacity="0.25"/>
  </g>

  <!-- Corner brackets -->
  <g fill="none" stroke="#5c5247">
    <path d="M 6,15 L 6,38 M 6,15 L 28,15" stroke-width="2.5" opacity="0.55"/>
    <path d="M 9,13 L 9,36 M 9,13 L 30,13" stroke-width="1.5" opacity="0.2"/>
    <path d="M 894,15 L 894,38 M 894,15 L 872,15" stroke-width="2.5" opacity="0.55"/>
    <path d="M 891,13 L 891,36 M 891,13 L 870,13" stroke-width="1.5" opacity="0.2"/>
  </g>
</svg>"""
    else:  # bottom
        return """<svg width="900" height="40" xmlns="http://www.w3.org/2000/svg">
  <!-- Vintage Technical Manual - BOLD layered drafts (bottom) -->

  <!-- Ghost/draft lines -->
  <line x1="30" y1="27" x2="870" y2="27" stroke="#5c5247" stroke-width="1.5" opacity="0.15"/>
  <line x1="26" y1="23" x2="875" y2="23" stroke="#5c5247" stroke-width="1" opacity="0.12"/>

  <!-- Main horizontal line -->
  <line x1="28" y1="25" x2="872" y2="25" stroke="#5c5247" stroke-width="2" opacity="0.5"/>

  <!-- Secondary lines -->
  <line x1="280" y1="19" x2="855" y2="19" stroke="#5c5247" stroke-width="1" opacity="0.25"/>
  <line x1="320" y1="17" x2="852" y2="17" stroke="#5c5247" stroke-width="0.75" opacity="0.15"/>

  <!-- Short accent lines on left -->
  <line x1="50" y1="30" x2="180" y2="30" stroke="#5c5247" stroke-width="1" opacity="0.22"/>
  <line x1="70" y1="32" x2="160" y2="32" stroke="#5c5247" stroke-width="0.75" opacity="0.12"/>

  <!-- Bold tick marks -->
  <g stroke="#5c5247" opacity="0.4">
    <line x1="80" y1="14" x2="80" y2="32" stroke-width="1.5"/>
    <line x1="82" y1="16" x2="82" y2="30" stroke-width="1" opacity="0.5"/>
    <line x1="210" y1="17" x2="210" y2="30" stroke-width="1.5"/>
    <line x1="370" y1="14" x2="370" y2="32" stroke-width="1.5"/>
    <line x1="500" y1="16" x2="500" y2="31" stroke-width="1.5"/>
    <line x1="630" y1="14" x2="630" y2="32" stroke-width="1.5"/>
    <line x1="632" y1="16" x2="632" y2="30" stroke-width="1" opacity="0.5"/>
    <line x1="760" y1="16" x2="760" y2="30" stroke-width="1.5"/>
    <line x1="820" y1="14" x2="820" y2="32" stroke-width="1.5"/>
  </g>

  <!-- Bold circles -->
  <g fill="#5c5247">
    <circle cx="140" cy="25" r="3" opacity="0.35"/>
    <circle cx="143" cy="23" r="2" opacity="0.2"/>
    <circle cx="290" cy="24" r="2.5" opacity="0.3"/>
    <circle cx="440" cy="25" r="3.5" opacity="0.35"/>
    <circle cx="570" cy="23" r="2" opacity="0.28"/>
    <circle cx="700" cy="25" r="3" opacity="0.32"/>
    <circle cx="850" cy="24" r="2.5" opacity="0.3"/>
  </g>

  <!-- Corner dots -->
  <g fill="#5c5247">
    <circle cx="20" cy="25" r="5" opacity="0.5"/>
    <circle cx="22" cy="23" r="3" opacity="0.25"/>
    <circle cx="880" cy="25" r="5" opacity="0.5"/>
    <circle cx="878" cy="23" r="3" opacity="0.25"/>
  </g>

  <!-- Corner brackets (inverted for bottom) -->
  <g fill="none" stroke="#5c5247">
    <path d="M 6,25 L 6,2 M 6,25 L 28,25" stroke-width="2.5" opacity="0.55"/>
    <path d="M 9,27 L 9,4 M 9,27 L 30,27" stroke-width="1.5" opacity="0.2"/>
    <path d="M 894,25 L 894,2 M 894,25 L 872,25" stroke-width="2.5" opacity="0.55"/>
    <path d="M 891,27 L 891,4 M 891,27 L 870,27" stroke-width="1.5" opacity="0.2"/>
  </g>
</svg>"""


def generate_toc_row_svg(directory_name, description):
    """Generate a dark-mode TOC row SVG in CRT terminal style.

    Args:
        directory_name: The directory name (e.g., "agent-skills/")
        description: Short description for the comment
    """
    # Escape XML entities
    desc_escaped = description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    dir_escaped = directory_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<svg width="400" height="40" viewBox="0 0 400 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMid meet">
  <defs>
    <filter id="crtGlow">
      <feGaussianBlur stdDeviation="0.2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <pattern id="scanlines" x="0" y="0" width="100%" height="4" patternUnits="userSpaceOnUse">
      <rect x="0" y="0" width="100%" height="2" fill="#000000" opacity="0.25"/>
    </pattern>

    <linearGradient id="phosphor" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0f380f;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#0a2f0a;stop-opacity:1"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="400" height="40" fill="#1a1a1a"/>
  <rect x="7" y="0" width="393" height="40" fill="url(#phosphor)"/>
  <rect x="7" y="0" width="393" height="40" fill="url(#scanlines)"/>

  <!-- Hover highlight -->
  <rect x="7" y="0" width="393" height="40" fill="#33ff33" opacity="0">
    <animate attributeName="opacity" values="0;0.05;0" dur="2s" repeatCount="indefinite"/>
  </rect>

  <!-- Content -->
  <g filter="url(#crtGlow)">
    <text x="20" y="25" font-family="monospace" font-size="16" fill="#66ff66">
      drwxr-xr-x
    </text>
    <text x="140" y="25" font-family="monospace" font-size="16" fill="#33ff33" font-weight="bold">
      {dir_escaped}
      <animate attributeName="opacity" values="1;0.95;1" dur="0.1s" repeatCount="indefinite"/>
    </text>
    <!--
    <text x="400" y="25" font-family="monospace" font-size="14" fill="#449944" opacity="1">
      # {desc_escaped}
    </text>
    -->
  </g>
</svg>"""


def generate_toc_row_light_svg(directory_name, description):
    """Generate a light-mode TOC row SVG in vintage manual style."""
    _ = description  # Reserved for future use
    dir_escaped = directory_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<svg width="400" height="40" viewBox="0 0 400 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMid meet">
  <defs>
    <linearGradient id="paperBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#faf8f3"/>
      <stop offset="100%" style="stop-color:#f5f0e6"/>
    </linearGradient>
    <pattern id="leaderDots" x="0" y="0" width="10" height="4" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.8" fill="#8a7b6f" opacity="0.5"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="400" height="36" fill="url(#paperBg)"/>
  <line x1="2" y1="0" x2="2" y2="36" stroke="#c4baa8" stroke-width="1"/>
  <line x1="398" y1="0" x2="398" y2="36" stroke="#c4baa8" stroke-width="1"/>

  <!-- Section number -->
  <text x="32" y="24"
        font-family="'Courier New', Courier, monospace"
        font-size="14"
        font-weight="700"
        fill="#c96442"
        text-anchor="middle">
    01
  </text>

  <!-- Section title -->
  <text x="120" y="24"
        font-family="Georgia, 'Times New Roman', serif"
        font-size="14"
        fill="#3d3530">
    {dir_escaped}
  </text>

  <!-- Leader dots -->
  <rect x="210" y="20" width="140" height="4" fill="url(#leaderDots)"/>

  <!-- Page/section reference -->
  <text x="370" y="24"
        font-family="'Courier New', Courier, monospace"
        font-size="12"
        fill="#5c5247"
        text-anchor="end"
        opacity="0.7">
    §1
  </text>

  <!-- Bottom rule -->
  <line x1="20" y1="34" x2="380" y2="34" stroke="#c4baa8" stroke-width="0.5" opacity="0.3"/>
</svg>"""


def generate_toc_header_light_svg():
    """Generate a compact light-mode TOC header with fixed width and centered title."""
    return """<svg width="400" height="48" viewBox="0 0 400 48" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMid meet">
  <defs>
    <linearGradient id="tocHeaderBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#faf8f3"/>
      <stop offset="100%" style="stop-color:#f3eee4"/>
    </linearGradient>
  </defs>

  <rect x="0.5" y="0.5" width="399" height="47" rx="3" ry="3" fill="url(#tocHeaderBg)" stroke="#c4baa8" stroke-width="1"/>

  <!-- Center title -->
  <text x="200" y="28"
        font-family="Georgia, 'Times New Roman', serif"
        font-size="17"
        font-weight="600"
        fill="#3d3530"
        text-anchor="middle"
        letter-spacing="2">
    CONTENTS
  </text>

  <!-- Decorative diamonds -->
  <g fill="#5c5247" opacity="0.65">
    <path d="M 118 24 L 124 18 L 130 24 L 124 30 Z"/>
    <path d="M 282 24 L 288 18 L 294 24 L 288 30 Z"/>
  </g>

  <!-- Light scan indicator -->
  <rect x="-40" y="2" width="3" height="44" fill="#d2c5b4" opacity="0.16">
    <animate attributeName="x" values="-40;420;420;-40" keyTimes="0;0.28;0.98;1" dur="7s" repeatCount="indefinite" />
  </rect>
</svg>"""


def generate_toc_sub_svg(directory_name, description):
    """Generate a dark-mode TOC subcategory row SVG.

    Args:
        directory_name: The subdirectory name (e.g., "general/")
        description: Short description for the comment
    """
    _ = description  # Reserved for future use
    dir_escaped = directory_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<svg height="40" width="400" viewBox="0 0 400 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMid meet">
  <defs>
    <filter id="crtGlow">
      <feGaussianBlur stdDeviation="0.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <pattern id="scanlines" x="0" y="0" width="100%" height="4" patternUnits="userSpaceOnUse">
      <rect x="0" y="0" width="100%" height="2" fill="#000000" opacity="0.25"/>
    </pattern>

    <linearGradient id="phosphor" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0f380f;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#0a2f0a;stop-opacity:1"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="400" height="40" fill="#1a1a1a"/>
  <rect x="7" y="0" width="393" height="40" fill="url(#phosphor)"/>
  <rect x="7" y="0" width="393" height="40" fill="url(#scanlines)"/>

  <!-- Content -->
  <g filter="url(#crtGlow)">
    <text x="18" y="25" font-family="monospace" font-size="12" fill="#66ff66" opacity="0.8">
      |-
    </text>
    <text x="56" y="25" font-family="monospace" font-size="13" fill="#33ff33">
      {dir_escaped}
    </text>
  </g>
</svg>"""


def generate_toc_sub_light_svg(directory_name, description):
    """Generate a light-mode TOC subcategory row SVG."""
    _ = description  # Reserved for future use
    dir_escaped = directory_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<svg width="400" height="40" viewBox="0 0 400 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMid meet">
  <defs>
    <linearGradient id="paperBgSub" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#fbfaf6"/>
      <stop offset="100%" style="stop-color:#f4efe5"/>
    </linearGradient>
  </defs>

  <rect width="400" height="36" fill="url(#paperBgSub)"/>
  <line x1="2" y1="0" x2="2" y2="36" stroke="#c4baa8" stroke-width="1"/>
  <line x1="398" y1="0" x2="398" y2="36" stroke="#c4baa8" stroke-width="1"/>

  <text x="22" y="24"
        font-family="'Courier New', Courier, monospace"
        font-size="12"
        fill="#c96442"
        opacity="0.8">
    |-
  </text>
  <text x="60" y="24"
        font-family="Georgia, 'Times New Roman', serif"
        font-size="13"
        fill="#3d3530">
    {dir_escaped}
  </text>

  <line x1="20" y1="33" x2="380" y2="33" stroke="#c4baa8" stroke-width="0.5" opacity="0.3"/>
</svg>"""


# =============================================================================
# ASSET SAVING HELPERS - Save generated assets to disk
# =============================================================================


def ensure_category_header_exists(
    category_id: str,
    title: str,
    section_number: str,
    assets_dir: str,
    icon: str = "",
    always_regenerate: bool = True,
) -> tuple[str, str]:
    """Ensure category header SVGs exist, generating them if needed.

    Args:
        category_id: The category identifier (e.g., "skills", "tooling")
        title: The display title (e.g., "Agent Skills")
        section_number: Two-digit section number (e.g., "01")
        assets_dir: Directory to save SVGs
        icon: Optional emoji icon for dark mode header
        always_regenerate: If True, regenerate even if file exists (default True)

    Returns:
        Tuple of (dark_filename, light_filename)
    """
    # Define filenames
    safe_name = category_id.replace("-", "_")
    dark_filename = f"header_{safe_name}.svg"
    light_filename = f"header_{safe_name}-light-v3.svg"

    # Generate dark version
    dark_path = os.path.join(assets_dir, dark_filename)
    if always_regenerate or not os.path.exists(dark_path):
        create_h2_svg_file(title, dark_filename, assets_dir, icon=icon)

    # Generate light version
    light_path = os.path.join(assets_dir, light_filename)
    if always_regenerate or not os.path.exists(light_path):
        svg_content = generate_category_header_light_svg(title, section_number)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return (dark_filename, light_filename)


def ensure_section_divider_exists(variant, assets_dir):
    """Ensure section divider SVG exists, generating if needed.

    Returns tuple of (dark_filename, light_filename).
    """
    dark_filename = "section-divider-alt2.svg"
    light_filename = f"section-divider-light-manual-v{variant}.svg"

    light_path = os.path.join(assets_dir, light_filename)
    if not os.path.exists(light_path):
        svg_content = generate_section_divider_light_svg(variant)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return (dark_filename, light_filename)


def ensure_desc_box_exists(position, assets_dir):
    """Ensure desc box SVG exists, generating if needed.

    Args:
        position: "top" or "bottom"
    """
    filename = f"desc-box-{position}-light.svg"
    filepath = os.path.join(assets_dir, filename)

    if not os.path.exists(filepath):
        svg_content = generate_desc_box_light_svg(position)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return filename


def ensure_toc_row_exists(
    category_id, directory_name, description, assets_dir, always_regenerate=True
):
    """Ensure TOC row SVG exists, generating if needed."""
    filename = f"toc-row-{category_id}.svg"
    filepath = os.path.join(assets_dir, filename)

    if always_regenerate or not os.path.exists(filepath):
        svg_content = generate_toc_row_svg(directory_name, description)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return filename


def ensure_toc_sub_exists(
    subcat_id, directory_name, description, assets_dir, always_regenerate=True
):
    """Ensure TOC subcategory SVG exists, generating if needed."""
    filename = f"toc-sub-{subcat_id}.svg"
    filepath = os.path.join(assets_dir, filename)

    if always_regenerate or not os.path.exists(filepath):
        svg_content = generate_toc_sub_svg(directory_name, description)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return filename


# =============================================================================
# MAPPING FUNCTIONS - Map IDs to filenames
# =============================================================================


def get_category_svg_filename(category_id):
    """Map category ID to SVG filename."""
    svg_map = {
        "skills": "toc-row-skills.svg",
        "workflows": "toc-row-workflows.svg",
        "tooling": "toc-row-tooling.svg",
        "statusline": "toc-row-statusline.svg",
        "hooks": "toc-row-custom.svg",
        "slash-commands": "toc-row-commands.svg",
        "claude-md-files": "toc-row-config.svg",
        "alternative-clients": "toc-row-clients.svg",
        "official-documentation": "toc-row-docs.svg",
    }
    return svg_map.get(category_id, f"toc-row-{category_id}.svg")


def get_subcategory_svg_filename(subcat_id):
    """Map subcategory ID to SVG filename."""
    svg_map = {
        "general": "toc-sub-general.svg",
        "ide-integrations": "toc-sub-ide.svg",
        "usage-monitors": "toc-sub-monitors.svg",
        "orchestrators": "toc-sub-orchestrators.svg",
        "version-control-git": "toc-sub-git.svg",
        "code-analysis-testing": "toc-sub-code-analysis.svg",
        "context-loading-priming": "toc-sub-context.svg",
        "documentation-changelogs": "toc-sub-documentation.svg",
        "ci-deployment": "toc-sub-ci.svg",
        "project-task-management": "toc-sub-project-mgmt.svg",
        "miscellaneous": "toc-sub-misc.svg",
        "language-specific": "toc-sub-language.svg",
        "domain-specific": "toc-sub-domain.svg",
        "project-scaffolding-mcp": "toc-sub-scaffolding.svg",
    }
    return svg_map.get(subcat_id, f"toc-sub-{subcat_id}.svg")


def get_category_header_svg(category_id):
    """Map category ID to pre-made header SVG filenames (dark and light variants)."""
    header_map = {
        "skills": ("header_agent_skills.svg", "header_agent_skills-light-v3.svg"),
        "workflows": (
            "header_workflows_knowledge_guides.svg",
            "header_workflows_knowledge_guides-light-v3.svg",
        ),
        "tooling": ("header_tooling.svg", "header_tooling-light-v3.svg"),
        "statusline": ("header_status_lines.svg", "header_status_lines-light-v3.svg"),
        "hooks": ("header_hooks.svg", "header_hooks-light-v3.svg"),
        "slash-commands": ("header_slash_commands.svg", "header_slash_commands-light-v3.svg"),
        "claude-md-files": ("header_claudemd_files.svg", "header_claudemd_files-light-v3.svg"),
        "alternative-clients": (
            "header_alternative_clients.svg",
            "header_alternative_clients-light-v3.svg",
        ),
        "official-documentation": (
            "header_official_documentation.svg",
            "header_official_documentation-light-v3.svg",
        ),
    }
    return header_map.get(
        category_id, (f"header_{category_id}.svg", f"header_{category_id}-light-v3.svg")
    )


# Global counter for cycling section dividers (light mode only)
_section_divider_counter = 0


def get_section_divider_svg():
    """Get the next section divider SVG filenames.

    Dark mode: always uses section-divider.svg (electric wire style)
    Light mode: cycles through section-divider-light-manual-v1.svg, v2.svg, v3.svg
    """
    global _section_divider_counter
    variant = (_section_divider_counter % 3) + 1  # 1, 2, 3
    _section_divider_counter += 1
    return ("section-divider-alt2.svg", f"section-divider-light-manual-v{variant}.svg")


def sanitize_filename_from_anchor(anchor: str) -> str:
    """Convert an anchor string to a tidy filename fragment."""
    name = anchor.rstrip("-")
    name = name.replace("-", "_")
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def build_general_anchor_map(categories, csv_data=None):
    """Build a map of (category, 'General') -> anchor string shared by TOC and body."""
    general_map = {}

    for category in categories:
        category_name = category.get("name", "")
        category_id = category.get("id", "")
        subcategories = category.get("subcategories", [])

        for subcat in subcategories:
            sub_title = subcat["name"]
            if sub_title != "General":
                continue

            include_subcategory = True
            if csv_data is not None:
                resources = [
                    r
                    for r in csv_data
                    if r["Category"] == category_name
                    and r.get("Sub-Category", "").strip() == sub_title
                ]
                include_subcategory = bool(resources)

            if not include_subcategory:
                continue

            anchor = f"{category_id}-general"
            general_map[(category_id, sub_title)] = anchor

    return general_map


def generate_toc_from_categories(csv_data=None, general_map=None):
    """Generate simple table of contents as vertical list of SVG rows.

    Args:
        csv_data: List of resource dictionaries from CSV.
                 If None, TOC will include all subcategories.
    """
    from category_utils import category_manager  # type: ignore[import-not-found]

    categories = category_manager.get_categories_for_readme()

    toc_header = """<!-- Directory Tree Terminal - Theme Adaptive -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/toc-header.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/toc-header-light-anim-scanline.svg">
  <img src="assets/toc-header-light-anim-scanline.svg" alt="Directory Listing" height="48" style="height:48px;max-width:none;">
</picture>"""

    toc_lines = [
        '<div style="overflow-x:auto;white-space:nowrap;text-align:left;">',
        f'<div style="height:48px;width:400px;overflow:hidden;display:block;">{toc_header}</div>',
    ]

    for category in categories:
        # Main section link
        section_title = category["name"]
        category_name = category.get("name", "")
        category_id = category.get("id", "")
        anchor = (
            section_title.lower()
            .replace(" ", "-")
            .replace("&", "")
            .replace("/", "")
            .replace(".", "")
        )

        # All category headers have back-to-top links (🔝 emoji), so they need "-" suffix
        anchor_suffix = "-"

        # Get SVG filename for this category
        svg_filename = get_category_svg_filename(category_id)

        # Add main category row with theme-adaptive picture element
        dark_svg = svg_filename
        light_svg = svg_filename.replace(".svg", "-light-anim-scanline.svg")
        toc_lines.append('<div style="height:40px;width:400px;overflow:hidden;display:block;">')
        toc_lines.append(f'<a href="#{anchor}{anchor_suffix}">')
        toc_lines.append("  <picture>")
        toc_lines.append(
            f'    <source media="(prefers-color-scheme: dark)" srcset="assets/{dark_svg}">'
        )
        toc_lines.append(
            f'    <source media="(prefers-color-scheme: light)" srcset="assets/{light_svg}">'
        )
        toc_lines.append(
            f'    <img src="assets/{light_svg}" alt="{section_title}" height="40" style="height:40px;max-width:none;">'
        )
        toc_lines.append("  </picture>")
        toc_lines.append("</a>")
        toc_lines.append("</div>")

        # Check if this category has subcategories
        subcategories = category.get("subcategories", [])

        if subcategories:
            # Add subcategory rows
            for subcat in subcategories:
                sub_title = subcat["name"]
                subcat_id = subcat.get("id", "")

                # Check if this subcategory has any resources (if csv_data is provided)
                include_subcategory = True
                if csv_data is not None:
                    category_name = category.get("name", "")
                    resources = [
                        r
                        for r in csv_data
                        if r["Category"] == category_name
                        and r.get("Sub-Category", "").strip() == sub_title
                    ]
                    include_subcategory = bool(resources)

                # Only include subcategory if it has resources
                if include_subcategory:
                    sub_anchor = (
                        sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")
                    )

                    # Special handling for "General" subcategories
                    if sub_title == "General":
                        if general_map is not None:
                            sub_anchor = general_map.get((category_id, sub_title), "general-")
                        else:
                            sub_anchor = f"{category_id}-general"
                    else:
                        # Non-General subcategories need "-" suffix due to back-to-top links (🔝 emoji)
                        sub_anchor = sub_anchor + "-"

                    # Get SVG filename for this subcategory
                    svg_filename = get_subcategory_svg_filename(subcat_id)

                    # Add subcategory row with theme-adaptive picture element
                    dark_svg = svg_filename
                    light_svg = svg_filename.replace(".svg", "-light-anim-scanline.svg")
                    toc_lines.append(
                        '<div style="height:40px;width:400px;overflow:hidden;display:block;">'
                    )
                    toc_lines.append(f'<a href="#{sub_anchor}">')
                    toc_lines.append("  <picture>")
                    toc_lines.append(
                        f'    <source media="(prefers-color-scheme: dark)" srcset="assets/{dark_svg}">'
                    )
                    toc_lines.append(
                        f'    <source media="(prefers-color-scheme: light)" srcset="assets/{light_svg}">'
                    )
                    toc_lines.append(
                        f'    <img src="assets/{light_svg}" alt="{sub_title}" height="40" style="height:40px;max-width:none;">'
                    )
                    toc_lines.append("  </picture>")
                    toc_lines.append("</a>")
                    toc_lines.append("</div>")

    toc_lines.append("</div>")

    return "\n".join(toc_lines).strip()


def _normalize_svg_root(tag: str, target_width: int, target_height: int) -> str:
    """Ensure root SVG tag enforces target width/height, viewBox, and left anchoring."""

    def ensure_attr(svg_tag: str, name: str, value: str) -> str:
        if re.search(rf'{name}="[^"]*"', svg_tag):
            return re.sub(rf'{name}="[^"]*"', f'{name}="{value}"', svg_tag)
        # Insert before closing ">"
        return svg_tag.rstrip(">") + f' {name}="{value}">'

    # Force consistent width/height
    svg_tag = ensure_attr(tag, "width", str(target_width))
    svg_tag = ensure_attr(svg_tag, "height", str(target_height))

    # Ensure preserveAspectRatio anchors left and keeps aspect
    svg_tag = ensure_attr(svg_tag, "preserveAspectRatio", "xMinYMid meet")

    # Enforce viewBox to match target dimensions
    svg_tag = ensure_attr(svg_tag, "viewBox", f"0 0 {target_width} {target_height}")

    return svg_tag


def normalize_toc_svgs(assets_dir: str) -> None:
    """Normalize TOC row/sub SVGs to enforce consistent display height/anchoring."""
    patterns = ["toc-row-*.svg", "toc-sub-*.svg", "toc-header*.svg"]
    for pattern in patterns:
        for path in glob.glob(os.path.join(assets_dir, pattern)):
            with open(path, encoding="utf-8") as f:
                content = f.read()

            # Grab the root tag
            match = re.search(r"<svg[^>]*>", content)
            if not match:
                continue

            root_tag = match.group(0)
            is_header = "toc-header" in os.path.basename(path)
            target_width = 400
            target_height = 48 if is_header else 40

            normalized_tag = _normalize_svg_root(root_tag, target_width, target_height)
            if normalized_tag != root_tag:
                content = content.replace(root_tag, normalized_tag, 1)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)


def format_category_dir_name(name: str, category_id: str | None = None) -> str:
    """Convert category name to display text for TOC rows."""
    overrides = {
        "workflows": "WORKFLOWS_&_GUIDES/",
    }
    if category_id and category_id in overrides:
        return overrides[category_id]

    # Default: UPPER_SNAKE_CASE with trailing slash
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()
    return slug + "/"


def regenerate_main_toc_svgs(categories, assets_dir: str) -> None:
    """Regenerate main category TOC row SVGs with standardized styling."""
    for category in categories:
        display_dir = format_category_dir_name(category.get("name", ""), category.get("id", ""))
        description = category.get("description", "")

        # Regenerate the dark SVG used in README
        dark_filename = get_category_svg_filename(category.get("id", ""))
        dark_path = os.path.join(assets_dir, dark_filename)
        svg_content = generate_toc_row_svg(display_dir, description)
        with open(dark_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        # Regenerate light-mode version
        light_path = dark_path.replace(".svg", "-light-anim-scanline.svg")
        light_svg = generate_toc_row_light_svg(display_dir, description)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(light_svg)


def regenerate_sub_toc_svgs(categories, assets_dir: str) -> None:
    """Regenerate subcategory TOC SVGs to keep sizing consistent."""
    for category in categories:
        subcats = category.get("subcategories", [])
        for subcat in subcats:
            display_dir = subcat.get("name", "")
            description = subcat.get("description", "")
            dark_filename = get_subcategory_svg_filename(subcat.get("id", ""))
            dark_path = os.path.join(assets_dir, dark_filename)
            svg_content = generate_toc_sub_svg(display_dir, description)
            with open(dark_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            light_path = dark_path.replace(".svg", "-light-anim-scanline.svg")
            light_svg = generate_toc_sub_light_svg(display_dir, description)
            with open(light_path, "w", encoding="utf-8") as f:
                f.write(light_svg)


def regenerate_toc_header(assets_dir: str) -> None:
    """Regenerate the light-mode TOC header for consistent sizing."""
    light_header_path = os.path.join(assets_dir, "toc-header-light-anim-scanline.svg")
    light_header_svg = generate_toc_header_light_svg()
    with open(light_header_path, "w", encoding="utf-8") as f:
        f.write(light_header_svg)


def generate_resource_badge_svg(display_name, author_name=""):
    """Generate SVG content for a resource name badge with theme-adaptive colors.

    Uses CSS media queries to switch between light and dark color schemes.
    - Light: dark text on transparent background
    - Dark: light text on transparent background
    """
    # Get first two letters/initials for the box
    words = display_name.split()
    if len(words) >= 2:
        initials = words[0][0].upper() + words[1][0].upper()
    else:
        initials = display_name[:2].upper()

    # Escape XML special characters
    name_escaped = (
        display_name.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    author_escaped = (
        author_name.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        if author_name
        else ""
    )

    # Calculate width based on text length (approximate) - larger fonts need more space
    name_width = len(display_name) * 10
    author_width = (len(author_name) * 7 + 35) if author_name else 0  # 35px for "by "
    text_width = name_width + author_width + 70  # 70px for box + padding
    svg_width = max(220, min(700, text_width))

    # Calculate position for author text
    name_end_x = 48 + name_width

    # Build author text element if author provided
    author_element = ""
    if author_name:
        author_element = f"""
  <text class="author" x="{name_end_x + 10}" y="30" font-family="system-ui, -apple-system, 'Helvetica Neue', sans-serif" font-size="14" font-weight="400">by {author_escaped}</text>"""

    svg = f"""<svg width="{svg_width}" height="44" xmlns="http://www.w3.org/2000/svg">
  <style>
    @media (prefers-color-scheme: light) {{
      .line {{ stroke: #5c5247; }}
      .box {{ stroke: #5c5247; }}
      .initials {{ fill: #c96442; }}
      .name {{ fill: #3d3530; }}
      .author {{ fill: #5c5247; opacity: 0.7; }}
    }}
    @media (prefers-color-scheme: dark) {{
      .line {{ stroke: #888; }}
      .box {{ stroke: #888; }}
      .initials {{ fill: #ff6b4a; }}
      .name {{ fill: #e8e8e8; }}
      .author {{ fill: #aaa; opacity: 0.8; }}
    }}
  </style>

  <!-- Thin top line -->
  <line class="line" x1="4" y1="6" x2="{svg_width - 4}" y2="6" stroke-width="1.25" opacity="0.4"/>

  <!-- Initials box -->
  <rect class="box" x="4" y="12" width="32" height="26" fill="none" stroke-width="2.25" opacity="0.6"/>
  <text class="initials" x="20" y="30" font-family="'Courier New', Courier, monospace" font-size="14" font-weight="700" text-anchor="middle">{initials}</text>

  <!-- Resource name -->
  <text class="name" x="48" y="30" font-family="system-ui, -apple-system, 'Helvetica Neue', sans-serif" font-size="17" font-weight="600">{name_escaped}</text>{author_element}

  <!-- Bottom rule -->
  <line class="line" x1="48" y1="37" x2="{svg_width - 4}" y2="37" stroke-width="1.25" opacity="0.5"/>
</svg>"""
    return svg


def save_resource_badge_svg(display_name, author_name, assets_dir):
    """Save a resource name SVG badge to the assets directory and return the filename."""
    # Create a safe filename from the display name (no -light suffix, badge is theme-adaptive)
    safe_name = re.sub(r"[^a-zA-Z0-9]", "-", display_name.lower())
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    filename = f"badge-{safe_name}.svg"

    # Generate the SVG content (theme-adaptive via CSS media queries)
    svg_content = generate_resource_badge_svg(display_name, author_name)

    # Save to file
    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def generate_entry_separator_svg():
    """Generate a small separator SVG between entries in vintage manual style.

    Uses bolder 'layered drafts' aesthetic with ghost circles for depth.
    """
    return """<svg width="200" height="12" xmlns="http://www.w3.org/2000/svg">
  <g opacity="0.55">
    <circle cx="88" cy="6" r="2.5" fill="#c4baa8"/>
    <circle cx="100" cy="6" r="3.5" fill="#c96442"/>
    <circle cx="112" cy="6" r="2.5" fill="#c4baa8"/>
    <!-- Ghost circles for layered effect -->
    <circle cx="90" cy="7" r="1.5" fill="#c4baa8" opacity="0.4"/>
    <circle cx="102" cy="7" r="2" fill="#c96442" opacity="0.3"/>
    <circle cx="110" cy="7" r="1.5" fill="#c4baa8" opacity="0.4"/>
  </g>
</svg>"""


def ensure_separator_svg_exists(assets_dir):
    """Return the animated entry separator SVG filename.

    The animated separator is a pre-made asset with pulsating/radiating dots
    that ripple outward then contract back in.
    """
    # Use the animated version - it's a pre-made asset, no generation needed
    return "entry-separator-light-animated.svg"


def format_resource_entry(row, assets_dir=None, include_separator=True):
    """Format a single resource entry with vintage manual styling for light mode.

    Uses two spaces + newline for line breaks within entry (no empty lines).
    """
    display_name = row["Display Name"]
    primary_link = row["Primary Link"]
    author_name = row.get("Author Name", "").strip()
    description = row.get("Description", "").strip()
    removed_from_origin = row.get("Removed From Origin", "").strip().upper() == "TRUE"

    parts = []

    # Generate and save the light mode SVG badge if assets_dir provided
    # Badge includes resource name and author
    if assets_dir:
        badge_filename = save_resource_badge_svg(display_name, author_name, assets_dir)
        # Link with SVG badge image
        parts.append(f'<a href="{primary_link}">')
        parts.append(f'<img src="assets/{badge_filename}" alt="{display_name}">')
        parts.append("</a>")
    else:
        # Fallback to text link
        parts.append(f"[`{display_name}`]({primary_link})")
        if author_name:
            parts.append(f" by {author_name}")

    # Add description (with two spaces for line break)
    if description:
        parts.append("  \n")
        parts.append(f"_{description}_" + ("*" if removed_from_origin else ""))

    # Add footnote if removed from origin
    if removed_from_origin:
        parts.append("  \n")
        parts.append("<sub>* Removed from origin</sub>")

    # Add GitHub stats directly under the entry
    if primary_link and not removed_from_origin:
        _, is_github, owner, repo = parse_github_url(primary_link)

        if is_github and owner and repo:
            base_url = "https://github-readme-stats-plus-theta.vercel.app/api/pin/"
            stats_url = f"{base_url}?repo={repo}&username={owner}&all_stats=true&stats_only=true&hide_border=true&bg_color=00000000&icon_color=FF0000&text_color=FF0000"
            parts.append("  \n")
            parts.append(f"![GitHub Stats for {repo}]({stats_url})")

    # Add separator between entries
    if include_separator and assets_dir:
        separator_filename = ensure_separator_svg_exists(assets_dir)
        parts.append("\n\n")
        parts.append('<div align="center">')
        parts.append(f'<img src="assets/{separator_filename}" alt="">')
        parts.append("</div>")
        parts.append("\n")

    return "".join(parts)


def parse_resource_date(date_string):
    """Parse a date string that may include timestamp information.

    Handles formats:
    - YYYY-MM-DD
    - YYYY-MM-DD:HH-MM-SS

    Returns datetime object or None if parsing fails.
    """
    if not date_string:
        return None

    date_string = date_string.strip()

    # Try different date formats
    date_formats = [
        "%Y-%m-%d:%H-%M-%S",  # Full format with timestamp
        "%Y-%m-%d",  # Date only format
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None


def generate_weekly_section(csv_data, assets_dir=None):
    """Generate the latest additions section that appears above Contents."""
    lines = []

    # Latest Additions header with light/dark mode support
    lines.append('<div align="center">')
    lines.append("  <picture>")
    lines.append(
        '    <source media="(prefers-color-scheme: dark)" srcset="assets/latest-additions-header.svg">'
    )
    lines.append(
        '    <source media="(prefers-color-scheme: light)" srcset="assets/latest-additions-header-light.svg">'
    )
    lines.append('    <img src="assets/latest-additions-header-light.svg" alt="LATEST ADDITIONS">')
    lines.append("  </picture>")
    lines.append("</div>")
    lines.append("")

    # Get rows sorted by date added (newest first)
    resources_sorted_by_date = []
    for row in csv_data:
        date_added = row.get("Date Added", "").strip()
        if date_added:
            parsed_date = parse_resource_date(date_added)
            if parsed_date:
                resources_sorted_by_date.append((parsed_date, row))
    resources_sorted_by_date.sort(key=lambda x: x[0], reverse=True)

    # Add all resources added in the past 7 days
    latest_additions = []
    cutoff_date = datetime.now() - timedelta(days=7)
    for dated_resource in resources_sorted_by_date:
        if dated_resource[0] >= cutoff_date or len(latest_additions) < 3:
            latest_additions.append(dated_resource[1])
        else:
            break

    for resource in latest_additions:
        lines.append(
            format_resource_entry(resource, assets_dir=assets_dir, include_separator=False)
        )
        lines.append("")

    # # Get all resources with dates, sorted newest first
    # cutoff_date = datetime.now() - timedelta(days=7)
    # all_dated_resources = []

    # for row in csv_data:
    #     date_added = row.get("Date Added", "").strip()
    #     if date_added:
    #         parsed_date = parse_resource_date(date_added)
    #         if parsed_date:
    #             all_dated_resources.append((parsed_date, row))

    # # Sort by date (newest first)
    # all_dated_resources.sort(key=lambda x: x[0], reverse=True)

    # # Get resources from past 7 days
    # recent_resources = [(d, r) for d, r in all_dated_resources if d >= cutoff_date]

    # # Ensure at least 3 entries (fill with most recent if needed)
    # min_entries = 3
    # if len(recent_resources) < min_entries:
    #     # Add more recent entries to reach minimum
    #     for dated_resource in all_dated_resources:
    #         if dated_resource not in recent_resources:
    #             recent_resources.append(dated_resource)
    #         if len(recent_resources) >= min_entries:
    #             break
    #     # Re-sort after adding extras
    #     recent_resources.sort(key=lambda x: x[0], reverse=True)

    # if recent_resources:
    #     lines.append("<blockquote>")
    #     lines.append("")
    #     lines.append("The latest resources added to the list")
    #     lines.append("")
    #     lines.append("</blockquote>")
    #     lines.append("")
    #     for _, resource in recent_resources:
    #         lines.append(
    #             format_resource_entry(resource, assets_dir=assets_dir, include_separator=False)
    #         )
    #         lines.append("")
    # else:
    #     lines.append("<blockquote>")
    #     lines.append("")
    #     lines.append("*No resources with dates found.*")
    #     lines.append("")
    #     lines.append("</blockquote>")
    #     lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_section_content(
    category: dict,
    csv_data: list,
    general_map: dict | None = None,
    assets_dir: str | None = None,
    section_index: int = 0,
) -> str:
    """Generate content for a category based on CSV data.

    Args:
        category: Category dictionary with name, id, icon, description, subcategories
        csv_data: List of resource dictionaries from CSV
        general_map: Map for handling multiple "General" subcategory anchors
        assets_dir: Directory to save generated SVG assets
        section_index: Zero-based index of this section (for section numbering)
    """
    lines = []

    # Get category details
    category_id = category.get("id", "")
    title = category.get("name", "")
    icon = category.get("icon", "")
    description = category.get("description", "").strip()
    category_name = category.get("name", "")
    subcategories = category.get("subcategories", [])

    # Add decorative section divider before each major category (cycles through v1, v2, v3)
    dark_divider, light_divider = get_section_divider_svg()
    lines.append('<div align="center">')
    lines.append("  <picture>")
    lines.append(
        f'    <source media="(prefers-color-scheme: dark)" srcset="assets/{dark_divider}">'
    )
    lines.append(
        f'    <source media="(prefers-color-scheme: light)" srcset="assets/{light_divider}">'
    )
    lines.append(
        f'    <img src="assets/{light_divider}" alt="" width="100%" style="max-width: 800px;">'
    )
    lines.append("  </picture>")
    lines.append("</div>")
    lines.append("")

    # Has subcategories - use regular header (not collapsible at category level)
    # header_text = f"{title} {icon}" if icon else title

    # Generate anchor ID matching TOC format
    anchor = title.lower().replace(" ", "-").replace("&", "").replace("/", "").replace(".", "")
    anchor_id = f"{anchor}-"  # Category headers have "-" suffix

    # Generate header SVG files for this category (dark and light versions)
    section_number = str(section_index + 1).zfill(2)  # "01", "02", etc.
    display_title = title
    if category_id == "workflows":
        display_title = "Workflows & Guides"
    dark_header, light_header = ensure_category_header_exists(
        category_id, display_title, section_number, assets_dir, icon=icon, always_regenerate=True
    )

    # Add header with proper ID and theme-adaptive picture element
    lines.append(f'<h2 id="{anchor_id}">')
    lines.append('<div align="center">')
    lines.append("  <picture>")
    lines.append(f'    <source media="(prefers-color-scheme: dark)" srcset="assets/{dark_header}">')
    lines.append(
        f'    <source media="(prefers-color-scheme: light)" srcset="assets/{light_header}">'
    )
    lines.append(f'    <img src="assets/{light_header}" alt="{title}" style="max-width: 600px;">')
    lines.append("  </picture>")
    lines.append("</div>")
    lines.append("</h2>")
    lines.append('<div align="right"><a href="#awesome-claude-code">🔝 Back to top</a></div>')
    lines.append("")

    # Add section description if present, wrapped in decorative box
    if description:
        lines.append("")
        lines.append('<div align="center">')
        lines.append("  <picture>")
        lines.append(
            '    <source media="(prefers-color-scheme: dark)" srcset="assets/desc-box-top.svg">'
        )
        lines.append(
            '    <source media="(prefers-color-scheme: light)" srcset="assets/desc-box-top-light.svg">'
        )
        lines.append(
            '    <img src="assets/desc-box-top-light.svg" alt="" width="100%" style="max-width: 900px;">'
        )
        lines.append("  </picture>")
        lines.append("</div>")
        # lines.append('')
        lines.append(f"<h3 id='{anchor_id}' align='center'>{description}</h3>")
        # lines.append('')
        lines.append('<div align="center">')
        lines.append("  <picture>")
        lines.append(
            '    <source media="(prefers-color-scheme: dark)" srcset="assets/desc-box-bottom.svg">'
        )
        lines.append(
            '    <source media="(prefers-color-scheme: light)" srcset="assets/desc-box-bottom-light.svg">'
        )
        lines.append(
            '    <img src="assets/desc-box-bottom-light.svg" alt="" width="100%" style="max-width: 900px;">'
        )
        lines.append("  </picture>")
        lines.append("</div>")

        # First render main category resources without subcategory
        # main_resources = [
        #     r
        #     for r in csv_data
        #     if r["Category"] == category_name and not r.get("Sub-Category", "").strip()
        # ]
        # if main_resources:
        #     lines.append("")
        #     for resource in main_resources:
        #         lines.append(format_resource_entry(resource, assets_dir=assets_dir))
        #         lines.append("")

        # Then render each subsection as a collapsible element
        for subcat in subcategories:
            sub_title = subcat["name"]

            resources = [
                r
                for r in csv_data
                if r["Category"] == category_name and r.get("Sub-Category", "").strip() == sub_title
            ]

            if resources:
                lines.append("")

                # Generate anchor ID for subcategory (matching TOC format)
                sub_anchor = sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")

                # Special handling for "General" to keep anchors in sync with TOC
                if sub_title == "General":
                    if general_map is not None:
                        sub_anchor = general_map.get((category_id, sub_title), "general-")
                    else:
                        sub_anchor = f"{category_id}-general"
                else:
                    sub_anchor = f"{sub_anchor}-"

                # For "General" we keep the anchor as-is (no trailing dash)
                if sub_title == "General":
                    sub_anchor_id = sub_anchor
                else:
                    sub_anchor_id = sub_anchor if sub_anchor.endswith("-") else f"{sub_anchor}-"

                # Create SVG file for this subsection
                safe_filename = sanitize_filename_from_anchor(sub_anchor)
                svg_filename = f"subheader_{safe_filename}.svg"
                assets_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
                )
                create_h3_svg_file(sub_title, svg_filename, assets_dir)

                # Start subcategory disclosure element with the SVG inside the summary
                lines.append(f'<details open id="{sub_anchor_id}">')
                lines.append(
                    f'<summary><span><picture><img src="assets/{svg_filename}" alt="{sub_title}" align="absmiddle"></picture></span></summary>'
                )
                lines.append("")

                for resource in resources:
                    lines.append(format_resource_entry(resource, assets_dir=assets_dir))
                    lines.append("")

                # Close subcategory disclosure element
                lines.append("</details>")

    return "\n".join(lines).rstrip() + "\n"


def load_overrides(template_dir):
    """Load resource overrides."""
    override_path = os.path.join(template_dir, "resource-overrides.yaml")
    if not os.path.exists(override_path):
        return {}

    with open(override_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("overrides", {})


def apply_overrides(row, overrides):
    """Apply overrides to a resource row.

    Override values are applied for README generation. Any field set in
    the override configuration is automatically locked by validation scripts.
    """
    resource_id = row.get("ID", "")
    if not resource_id or resource_id not in overrides:
        return row

    override_config = overrides[resource_id]

    # Apply overrides (excluding control/metadata fields and legacy locked flags)
    for field, value in override_config.items():
        # Skip special control/metadata fields
        if field in ["skip_validation", "notes"]:
            continue

        # Skip any legacy *_locked flags (no longer needed)
        if field.endswith("_locked"):
            continue

        # Apply override values
        if field == "license":
            row["License"] = value
        elif field == "active":
            row["Active"] = value
        elif field == "description":
            row["Description"] = value

    return row


def create_backup(file_path):
    """Create a backup of the file if it exists."""
    if not os.path.exists(file_path):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get the repository root (one level up from scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    backup_dir = os.path.join(repo_root, ".myob", "backups")
    os.makedirs(backup_dir, exist_ok=True)

    backup_filename = f"{os.path.basename(file_path)}.{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)

    shutil.copy2(file_path, backup_path)
    return backup_path


def generate_readme_from_templates(csv_path, template_dir, output_path):
    """Generate README using template system.

    DEPRECATED: This function is deprecated and will be removed in a future version.
    Use the class-based generators (VisualReadmeGenerator, MinimalReadmeGenerator)
    or call main() instead, which generates both README.md and README_CLASSIC.md.
    """
    from category_utils import category_manager  # type: ignore[import-not-found]

    # Create backup of existing README
    backup_path = create_backup(output_path)

    # Compute assets directory (sibling of templates dir)
    repo_root = os.path.dirname(template_dir)
    assets_dir = os.path.join(repo_root, "assets")

    # Load template
    template_path = os.path.join(template_dir, "README.template.md")
    template = load_template(template_path)
    overrides = load_overrides(template_dir)
    announcements = load_announcements(template_dir)
    categories = category_manager.get_categories_for_readme()

    # Optional: regenerate/normalize TOC row assets when explicitly requested
    if os.getenv("REGEN_TOC_ASSETS"):
        regenerate_main_toc_svgs(categories, assets_dir)
        regenerate_sub_toc_svgs(categories, assets_dir)
        regenerate_toc_header(assets_dir)
        normalize_toc_svgs(assets_dir)

    # Load CSV data
    csv_data = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Apply overrides
            row = apply_overrides(row, overrides)
            if row["Active"].upper() == "TRUE":
                csv_data.append(row)

    # Precompute consistent anchors for repeated "General" subcategories
    general_anchor_map = build_general_anchor_map(categories, csv_data)

    # Generate table of contents
    toc_content = generate_toc_from_categories(csv_data, general_anchor_map)

    # Generate weekly section
    weekly_section = generate_weekly_section(csv_data, assets_dir=assets_dir)

    # Generate body sections
    body_sections = []
    for section_index, category in enumerate(categories):
        section_content = generate_section_content(
            category,
            csv_data,
            general_anchor_map,
            assets_dir=assets_dir,
            section_index=section_index,
        )
        body_sections.append(section_content)

    # Replace placeholders in template
    readme_content = template
    readme_content = readme_content.replace("{{ANNOUNCEMENTS}}", announcements)
    readme_content = readme_content.replace("{{WEEKLY_SECTION}}", weekly_section)
    readme_content = readme_content.replace("{{TABLE_OF_CONTENTS}}", toc_content)
    readme_content = readme_content.replace("{{BODY_SECTIONS}}", "\n<br>\n\n".join(body_sections))

    # Write output
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
    except Exception as e:
        if backup_path:
            print(f"❌ Error writing README: {e}")
            print(f"   Backup preserved at: {backup_path}")
        raise

    return len(csv_data), backup_path


# =============================================================================
# CLASS-BASED README GENERATORS
# =============================================================================


class ReadmeGenerator(ABC):
    """Base class for README generation with shared logic."""

    def __init__(self, csv_path: str, template_dir: str, assets_dir: str, repo_root: str) -> None:
        self.csv_path = csv_path
        self.template_dir = template_dir
        self.assets_dir = assets_dir
        self.repo_root = repo_root
        self.csv_data: list[dict] = []
        self.categories: list[dict] = []
        self.overrides: dict = {}
        self.announcements: str = ""
        self.footer: str = ""
        self.general_anchor_map: dict = {}

    @property
    @abstractmethod
    def template_filename(self) -> str:
        """Return the template filename to use."""
        ...

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """Return the output filename to generate."""
        ...

    @abstractmethod
    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format a single resource entry."""
        ...

    @abstractmethod
    def generate_toc(self) -> str:
        """Generate the table of contents."""
        ...

    @abstractmethod
    def generate_weekly_section(self) -> str:
        """Generate the weekly additions section."""
        ...

    @abstractmethod
    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate content for a category section."""
        ...

    def load_csv_data(self) -> list[dict]:
        """Load and filter active resources from CSV."""
        csv_data = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = apply_overrides(row, self.overrides)
                if row["Active"].upper() == "TRUE":
                    csv_data.append(row)
        return csv_data

    def load_categories(self) -> list[dict]:
        """Load categories from the category manager."""
        from category_utils import category_manager  # type: ignore[import-not-found]

        return category_manager.get_categories_for_readme()

    def load_overrides(self) -> dict:
        """Load resource overrides from YAML."""
        return load_overrides(self.template_dir)

    def load_announcements(self) -> str:
        """Load announcements from YAML."""
        return load_announcements(self.template_dir)

    def load_footer(self) -> str:
        """Load footer template from file."""
        footer_path = os.path.join(self.template_dir, "footer.template.md")
        try:
            with open(footer_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Warning: Footer template not found at {footer_path}")
            return ""

    def build_general_anchor_map(self) -> dict:
        """Build anchor map for General subcategories."""
        return build_general_anchor_map(self.categories, self.csv_data)

    def create_backup(self, output_path: str) -> str | None:
        """Create backup of existing file."""
        return create_backup(output_path)

    def generate(self) -> tuple[int, str | None]:
        """Generate the README (template method pattern)."""
        # Load all data
        self.overrides = self.load_overrides()
        self.csv_data = self.load_csv_data()
        self.categories = self.load_categories()
        self.announcements = self.load_announcements()
        self.footer = self.load_footer()
        self.general_anchor_map = self.build_general_anchor_map()

        # Load template
        template_path = os.path.join(self.template_dir, self.template_filename)
        template = load_template(template_path)

        # Generate sections
        toc_content = self.generate_toc()
        weekly_section = self.generate_weekly_section()

        body_sections = []
        for section_index, category in enumerate(self.categories):
            section_content = self.generate_section_content(category, section_index)
            body_sections.append(section_content)

        # Replace placeholders
        readme_content = template
        readme_content = readme_content.replace("{{ANNOUNCEMENTS}}", self.announcements)
        readme_content = readme_content.replace("{{WEEKLY_SECTION}}", weekly_section)
        readme_content = readme_content.replace("{{TABLE_OF_CONTENTS}}", toc_content)
        readme_content = readme_content.replace(
            "{{BODY_SECTIONS}}", "\n<br>\n\n".join(body_sections)
        )
        readme_content = readme_content.replace("{{FOOTER}}", self.footer)

        # Write output
        output_path = os.path.join(self.repo_root, self.output_filename)
        # Ensure directory exists for folder-based output
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        backup_path = self.create_backup(output_path)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
        except Exception as e:
            if backup_path:
                print(f"❌ Error writing {self.output_filename}: {e}")
                print(f"   Backup preserved at: {backup_path}")
            raise

        return len(self.csv_data), backup_path


class VisualReadmeGenerator(ReadmeGenerator):
    """Generator for visual/themed README.md with SVG assets."""

    @property
    def template_filename(self) -> str:
        return "README.template.md"

    @property
    def output_filename(self) -> str:
        return "README.md"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format resource with SVG badges and visible GitHub stats."""
        return format_resource_entry(
            row, assets_dir=self.assets_dir, include_separator=include_separator
        )

    def generate_toc(self) -> str:
        """Generate terminal-style SVG TOC."""
        return generate_toc_from_categories(self.csv_data, self.general_anchor_map)

    def generate_weekly_section(self) -> str:
        """Generate latest additions section with header SVG."""
        return generate_weekly_section(self.csv_data, assets_dir=self.assets_dir)

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate section with SVG headers and desc boxes."""
        return generate_section_content(
            category,
            self.csv_data,
            self.general_anchor_map,
            assets_dir=self.assets_dir,
            section_index=section_index,
        )


class MinimalReadmeGenerator(ReadmeGenerator):
    """Generator for plain markdown README_CLASSIC/README.md."""

    @property
    def template_filename(self) -> str:
        return "README_CLASSIC.template.md"

    @property
    def output_filename(self) -> str:
        return "README_ALTERNATIVES/README_CLASSIC.md"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Format resource as plain markdown with collapsible GitHub stats."""
        _ = include_separator  # Not used in minimal version (no separators)
        display_name = row["Display Name"]
        primary_link = row["Primary Link"]
        author_name = row.get("Author Name", "").strip()
        author_link = row.get("Author Link", "").strip()
        description = row.get("Description", "").strip()
        license_info = row.get("License", "").strip()
        removed_from_origin = row.get("Removed From Origin", "").strip().upper() == "TRUE"

        # Build entry
        entry_parts = [f"[`{display_name}`]({primary_link})"]

        # Add author
        if author_name:
            if author_link:
                entry_parts.append(f" &nbsp; by &nbsp; [{author_name}]({author_link})")
            else:
                entry_parts.append(f" &nbsp; by &nbsp; {author_name}")

        entry_parts.append("  ")

        # Add license
        if license_info and license_info != "NOT_FOUND":
            entry_parts.append(f"&nbsp;&nbsp;⚖️&nbsp;&nbsp;{license_info}")

        result = "".join(entry_parts)

        # Add description
        if description:
            result += f"  \n{description}" + ("*  " if removed_from_origin else "")

        if removed_from_origin:
            result += "\n<sub>* Removed from origin</sub>"

        # Add GitHub stats in collapsible
        if primary_link and not removed_from_origin:
            _, is_github, owner, repo = parse_github_url(primary_link)
            if is_github and owner and repo:
                base_url = "https://github-readme-stats-plus-theta.vercel.app/api/pin/"
                stats_url = (
                    f"{base_url}?repo={repo}&username={owner}&all_stats=true&stats_only=true"
                )
                result += "\n\n<details>"
                result += "\n<summary>📊 GitHub Stats</summary>"
                result += f"\n\n![GitHub Stats for {repo}]({stats_url})"
                result += "\n\n</details>"
                result += "\n<br>"

        return result

    def generate_toc(self) -> str:
        """Generate plain markdown nested details TOC."""
        toc_lines = []
        toc_lines.append("## Contents [🔝](#awesome-claude-code)")
        toc_lines.append("")
        toc_lines.append("<details open>")
        toc_lines.append("<summary>Table of Contents</summary>")
        toc_lines.append("")

        general_counter = 0

        for category in self.categories:
            section_title = category.get("name", "")
            icon = category.get("icon", "")
            subcategories = category.get("subcategories", [])
            anchor_suffix = get_anchor_suffix_for_icon(icon)

            anchor = (
                section_title.lower()
                .replace(" ", "-")
                .replace("&", "")
                .replace("/", "")
                .replace(".", "")
            )

            if subcategories:
                toc_lines.append("- <details open>")
                toc_lines.append(
                    f'  <summary><a href="#{anchor}-{anchor_suffix}">{section_title}</a></summary>'
                )
                toc_lines.append("")

                for subcat in subcategories:
                    sub_title = subcat["name"]

                    # Check if subcategory has resources
                    category_name = category.get("name", "")
                    resources = [
                        r
                        for r in self.csv_data
                        if r["Category"] == category_name
                        and r.get("Sub-Category", "").strip() == sub_title
                    ]

                    if resources:
                        sub_anchor = (
                            sub_title.lower().replace(" ", "-").replace("&", "").replace("/", "")
                        )

                        if sub_title == "General":
                            if general_counter == 0:
                                sub_anchor = "general-"
                            else:
                                sub_anchor = f"general--{general_counter}"
                            general_counter += 1
                        else:
                            sub_anchor = sub_anchor + "-"

                        toc_lines.append(f"  - [{sub_title}](#{sub_anchor})")

                toc_lines.append("")
                toc_lines.append("  </details>")
            else:
                toc_lines.append(f"- [{section_title}](#{anchor}{anchor_suffix})")

            toc_lines.append("")

        toc_lines.append("</details>")
        return "\n".join(toc_lines).strip()

    def generate_weekly_section(self) -> str:
        """Generate weekly section with plain markdown."""
        lines = []
        lines.append("## Latest Additions ✨ [🔝](#awesome-claude-code)")
        lines.append("")

        # Get rows sorted by date added (newest first)
        resources_sorted_by_date = []
        for row in self.csv_data:
            date_added = row.get("Date Added", "").strip()
            if date_added:
                parsed_date = parse_resource_date(date_added)
                if parsed_date:
                    resources_sorted_by_date.append((parsed_date, row))
        resources_sorted_by_date.sort(key=lambda x: x[0], reverse=True)

        # Add all resources added in the past 7 days
        latest_additions: list[dict[str, str]] = []
        cutoff_date = datetime.now() - timedelta(days=7)
        for dated_resource in resources_sorted_by_date:
            if dated_resource[0] >= cutoff_date or len(latest_additions) < 3:
                latest_additions.append(dated_resource[1])
            else:
                break

        lines.append("")
        for resource in latest_additions:
            lines.append(self.format_resource_entry(resource, include_separator=False))
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Generate section with plain markdown headers."""
        _ = section_index  # Not used in minimal version but required by interface
        lines = []

        title = category.get("name", "")
        icon = category.get("icon", "")
        description = category.get("description", "").strip()
        category_name = category.get("name", "")
        subcategories = category.get("subcategories", [])

        # Header
        header_text = f"{title} {icon}" if icon else title
        lines.append(f"## {header_text} [🔝](#awesome-claude-code)")
        lines.append("")

        # Description as blockquote
        if description:
            lines.append(f"> {description}")
            lines.append("")

        # Subcategories
        for subcat in subcategories:
            sub_title = subcat["name"]
            resources = [
                r
                for r in self.csv_data
                if r["Category"] == category_name and r.get("Sub-Category", "").strip() == sub_title
            ]

            if resources:
                lines.append("<details open>")
                lines.append(
                    f'<summary><h3>{sub_title} <a href="#awesome-claude-code">🔝</a></h3></summary>'
                )
                lines.append("")

                for resource in resources:
                    lines.append(self.format_resource_entry(resource, include_separator=False))
                    lines.append("")

                lines.append("</details>")
                lines.append("")

        lines.append("<br>")
        return "\n".join(lines).rstrip() + "\n"


class ParameterizedFlatListGenerator(ReadmeGenerator):
    """Unified generator for flat list READMEs with category filtering and sort options."""

    DAYS_THRESHOLD = 30  # For releases filter

    def __init__(
        self,
        csv_path: str,
        template_dir: str,
        assets_dir: str,
        repo_root: str,
        category_slug: str = "all",
        sort_type: str = "az",
    ):
        super().__init__(csv_path, template_dir, assets_dir, repo_root)
        self.category_slug = category_slug
        self.sort_type = sort_type
        self._category_info = FLAT_CATEGORIES.get(category_slug, FLAT_CATEGORIES["all"])
        self._sort_info = FLAT_SORT_TYPES.get(sort_type, FLAT_SORT_TYPES["az"])

    @property
    def template_filename(self) -> str:
        return "README_FLAT.template.md"

    @property
    def output_filename(self) -> str:
        return f"README_ALTERNATIVES/README_FLAT_{self.category_slug.upper()}_{self.sort_type.upper()}.md"

    def format_resource_entry(self, row: dict, include_separator: bool = True) -> str:
        """Not used for flat list."""
        _ = include_separator
        return ""

    def generate_toc(self) -> str:
        """Not used for flat list."""
        return ""

    def generate_weekly_section(self) -> str:
        """Not used for flat list."""
        return ""

    def generate_section_content(self, category: dict, section_index: int) -> str:
        """Not used for flat list."""
        _ = category, section_index
        return ""

    def get_filtered_resources(self) -> list[dict]:
        """Get resources filtered by category."""
        csv_category_value = self._category_info[0]
        if csv_category_value is None:
            # "all" - return all resources
            return list(self.csv_data)
        return [r for r in self.csv_data if r.get("Category", "").strip() == csv_category_value]

    def sort_resources(self, resources: list[dict]) -> list[dict]:
        """Sort resources according to sort_type."""
        if self.sort_type == "az":
            return sorted(resources, key=lambda x: (x.get("Display Name", "") or "").lower())
        elif self.sort_type == "updated":
            with_dates = []
            for row in resources:
                last_modified = row.get("Last Modified", "").strip()
                parsed = parse_resource_date(last_modified) if last_modified else None
                with_dates.append((parsed, row))
            with_dates.sort(key=lambda x: (x[0] is None, x[0] if x[0] else datetime.min), reverse=True)
            return [r for _, r in with_dates]
        elif self.sort_type == "created":
            with_dates = []
            for row in resources:
                repo_created = row.get("Repo Created", "").strip()
                parsed = parse_resource_date(repo_created) if repo_created else None
                with_dates.append((parsed, row))
            with_dates.sort(key=lambda x: (x[0] is None, x[0] if x[0] else datetime.min), reverse=True)
            return [r for _, r in with_dates]
        elif self.sort_type == "releases":
            cutoff = datetime.now() - timedelta(days=self.DAYS_THRESHOLD)
            recent = []
            for row in resources:
                release_date_str = row.get("Latest Release", "")
                if not release_date_str:
                    continue
                try:
                    release_date = datetime.strptime(release_date_str, "%Y-%m-%d:%H-%M-%S")
                except ValueError:
                    continue
                if release_date >= cutoff:
                    row["_parsed_release_date"] = release_date
                    recent.append(row)
            recent.sort(key=lambda x: x.get("_parsed_release_date", datetime.min), reverse=True)
            return recent
        return resources

    def generate_sort_navigation(self) -> str:
        """Generate sort option badges."""
        lines = ['<p align="center">']
        for slug, (display, color, _) in FLAT_SORT_TYPES.items():
            filename = f"README_FLAT_{self.category_slug.upper()}_{slug.upper()}.md"
            is_selected = slug == self.sort_type
            style = f' style="border: 3px solid {color}; border-radius: 6px;"' if is_selected else ""
            lines.append(
                f'  <a href="{filename}"><img src="../assets/badge-sort-{slug}.svg" alt="{display}" height="48"{style}></a>'
            )
        lines.append("</p>")
        return "\n".join(lines)

    def generate_category_navigation(self) -> str:
        """Generate category filter badges."""
        lines = ['<p align="center">']
        for slug, (_, display, color) in FLAT_CATEGORIES.items():
            filename = f"README_FLAT_{slug.upper()}_{self.sort_type.upper()}.md"
            is_selected = slug == self.category_slug
            style = f' style="border: 2px solid {color}; border-radius: 4px;"' if is_selected else ""
            lines.append(
                f'  <a href="{filename}"><img src="../assets/badge-cat-{slug}.svg" alt="{display}" height="28"{style}></a>'
            )
        lines.append("</p>")
        return "\n".join(lines)

    def generate_navigation(self) -> str:
        """Generate combined navigation (sort + category)."""
        sort_nav = self.generate_sort_navigation()
        cat_nav = self.generate_category_navigation()
        _, _, sort_desc = self._sort_info
        _, cat_display, _ = self._category_info

        current_info = f"**{cat_display}** sorted {sort_desc}"
        if self.sort_type == "releases":
            current_info += " (past 30 days)"

        return f"""{sort_nav}
<p align="center"><strong>Category:</strong></p>
{cat_nav}
<p align="center"><em>Currently viewing: {current_info}</em></p>"""

    def generate_resources_table(self) -> str:
        """Generate the resources table."""
        resources = self.get_filtered_resources()
        sorted_resources = self.sort_resources(resources)

        if not sorted_resources:
            if self.sort_type == "releases":
                return "*No releases in the past 30 days for this category.*"
            return "*No resources found in this category.*"

        # Different columns for releases vs other sorts
        if self.sort_type == "releases":
            lines = ["| Resource | Version | Source | Release Date | Description |"]
            lines.append("|----------|---------|--------|--------------|-------------|")
            for row in sorted_resources:
                display_name = row.get("Display Name", "").strip()
                primary_link = row.get("Primary Link", "").strip()
                author_name = row.get("Author Name", "").strip()
                author_link = row.get("Author Link", "").strip()

                # Stacked format: Resource name + author
                resource_link = f"[**{display_name}**]({primary_link})" if primary_link else f"**{display_name}**"
                author_part = f"[{author_name}]({author_link})" if author_name and author_link else (author_name or "")
                resource_cell = f"{resource_link}<br>by {author_part}" if author_part else resource_link

                version = row.get("Release Version", "").strip() or "-"
                source = row.get("Release Source", "").strip()
                source_display = {
                    "github-releases": "GitHub", "npm": "npm", "pypi": "PyPI",
                    "crates": "crates.io", "homebrew": "Homebrew", "readme": "README",
                }.get(source, source or "-")

                release_date = row.get("Latest Release", "")[:10] if row.get("Latest Release") else "-"

                description = row.get("Description", "").strip().replace("|", "\\|")

                lines.append(f"| {resource_cell} | {version} | {source_display} | {release_date} | {description} |")
        else:
            lines = ["| Resource | Category | Sub-Category | Description |"]
            lines.append("|----------|----------|--------------|-------------|")
            for row in sorted_resources:
                display_name = row.get("Display Name", "").strip()
                primary_link = row.get("Primary Link", "").strip()
                author_name = row.get("Author Name", "").strip()
                author_link = row.get("Author Link", "").strip()

                # Stacked format: Resource name + author
                resource_link = f"[**{display_name}**]({primary_link})" if primary_link else f"**{display_name}**"
                author_part = f"[{author_name}]({author_link})" if author_name and author_link else (author_name or "")
                resource_cell = f"{resource_link}<br>by {author_part}" if author_part else resource_link

                category = row.get("Category", "").strip() or "-"
                sub_category = row.get("Sub-Category", "").strip() or "-"

                description = row.get("Description", "").strip().replace("|", "\\|")

                lines.append(f"| {resource_cell} | {category} | {sub_category} | {description} |")

        return "\n".join(lines)

    def generate(self) -> tuple[int, str | None]:
        """Generate the flat list README."""
        self.overrides = self.load_overrides()
        self.csv_data = self.load_csv_data()

        # Use a generic template
        template_path = os.path.join(self.template_dir, self.template_filename)
        if not os.path.exists(template_path):
            # Create default template content
            template = self._get_default_template()
        else:
            template = load_template(template_path)

        navigation = self.generate_navigation()
        resources_table = self.generate_resources_table()
        resources = self.get_filtered_resources()
        sorted_resources = self.sort_resources(resources)

        generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        _, cat_display, _ = self._category_info
        _, sort_display, sort_desc = self._sort_info

        # Generate releases disclaimer only for releases views
        releases_disclaimer = ""
        if self.sort_type == "releases":
            releases_disclaimer = """
> **Note:** We make a best-effort attempt to determine the latest release from GitHub Releases, npm, PyPI, crates.io, and Homebrew. Please verify with the project directly.
>
> If your project publishes to a package registry and isn't listed here, please [open an Issue](https://github.com/hesreallyhim/awesome-claude-code/issues).
"""

        readme_content = template
        readme_content = readme_content.replace("{{NAVIGATION}}", navigation)
        readme_content = readme_content.replace("{{RELEASES_DISCLAIMER}}", releases_disclaimer)
        readme_content = readme_content.replace("{{RESOURCES_TABLE}}", resources_table)
        readme_content = readme_content.replace("{{RESOURCE_COUNT}}", str(len(sorted_resources)))
        readme_content = readme_content.replace("{{CATEGORY_NAME}}", cat_display)
        readme_content = readme_content.replace("{{SORT_DESC}}", sort_desc)
        readme_content = readme_content.replace("{{GENERATED_DATE}}", generated_date)

        output_path = os.path.join(self.repo_root, self.output_filename)
        # Ensure directory exists for folder-based output
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        backup_path = self.create_backup(output_path)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
        except Exception as e:
            if backup_path:
                print(f"Error writing {self.output_filename}: {e}")
                print(f"   Backup preserved at: {backup_path}")
            raise

        return len(sorted_resources), backup_path

    def _get_default_template(self) -> str:
        """Return default template content."""
        return """<!--lint disable remark-lint:awesome-badge-->

<h3 align="center">Pick Your Style:</h3>
<p align="center">
<a href="../"><img src="../assets/badge-style-extra.svg" alt="Extra" height="28"></a>
<a href="README_CLASSIC.md"><img src="../assets/badge-style-classic.svg" alt="Classic" height="28"></a>
<a href="README_FLAT_ALL_AZ.md"><img src="../assets/badge-style-flat.svg" alt="Flat" height="28" style="border: 2px solid #71717a; border-radius: 4px;"></a>
</p>

# Awesome Claude Code (Flat)

[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)

A flat list view of all resources. Category: **{{CATEGORY_NAME}}** | Sorted: {{SORT_DESC}}

---

## Sort By:

{{NAVIGATION}}

---

## Resources
{{RELEASES_DISCLAIMER}}
{{RESOURCES_TABLE}}

---

**Total Resources:** {{RESOURCE_COUNT}}

**Last Generated:** {{GENERATED_DATE}}
"""


def generate_flat_badges(assets_dir: str):
    """Generate all sort and category badge SVGs."""
    # Sort badges (larger)
    for slug, (display, color, _) in FLAT_SORT_TYPES.items():
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="48" viewBox="0 0 180 48">
  <rect x="0" y="0" width="180" height="48" fill="#1a1a2e"/>
  <rect x="0" y="0" width="6" height="48" fill="{color}"/>
  <text x="93" y="32" font-family="'SF Mono', 'Consolas', monospace" font-size="18" font-weight="700" fill="#e2e8f0" text-anchor="middle" letter-spacing="1">{display}</text>
</svg>'''
        filepath = os.path.join(assets_dir, f"badge-sort-{slug}.svg")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)

    # Category badges (smaller)
    for slug, (_, display, color) in FLAT_CATEGORIES.items():
        # Calculate width based on text length
        width = max(70, len(display) * 10 + 30)
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28">
  <rect x="0" y="0" width="{width}" height="28" fill="#27272a"/>
  <rect x="0" y="0" width="4" height="28" fill="{color}"/>
  <text x="{width // 2 + 2}" y="19" font-family="'SF Mono', 'Consolas', monospace" font-size="12" font-weight="600" fill="#d4d4d8" text-anchor="middle">{display}</text>
</svg>'''
        filepath = os.path.join(assets_dir, f"badge-cat-{slug}.svg")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)


def main():
    """Main entry point - generates all README versions."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    csv_path = str(repo_root / "THE_RESOURCES_TABLE.csv")
    template_dir = str(repo_root / "templates")
    assets_dir = str(repo_root / "assets")

    print("=== README Generation ===")

    # Generate flat list badges first
    print("\n--- Generating flat list badges ---")
    generate_flat_badges(assets_dir)
    print("✅ Flat list badges generated")

    # Main README generators (Extra and Classic views)
    main_generators = [
        VisualReadmeGenerator(csv_path, template_dir, assets_dir, str(repo_root)),
        MinimalReadmeGenerator(csv_path, template_dir, assets_dir, str(repo_root)),
    ]

    for generator in main_generators:
        print(f"\n--- Generating {generator.output_filename} ---")
        try:
            resource_count, backup_path = generator.generate()
            print(f"✅ {generator.output_filename} generated successfully")
            print(f"📊 Generated with {resource_count} active resources")
            if backup_path:
                print(f"📁 Backup saved at: {backup_path}")
        except Exception as e:
            print(f"❌ Error generating {generator.output_filename}: {e}")
            sys.exit(1)

    # Generate all flat list combinations (categories × sort types = 44 files)
    print("\n--- Generating flat list views ---")
    flat_count = 0
    for category_slug in FLAT_CATEGORIES:
        for sort_type in FLAT_SORT_TYPES:
            generator = ParameterizedFlatListGenerator(
                csv_path, template_dir, assets_dir, str(repo_root),
                category_slug=category_slug, sort_type=sort_type
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

    print("\n=== Generation Complete ===")


if __name__ == "__main__":
    main()
