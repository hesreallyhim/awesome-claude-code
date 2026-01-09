"""SVG renderers for table-of-contents elements."""

import re


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
