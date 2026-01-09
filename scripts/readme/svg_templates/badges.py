"""SVG renderers for badges."""


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


def render_flat_sort_badge_svg(display: str, color: str) -> str:
    """Render a flat-list sort badge SVG."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="180" height="48" viewBox="0 0 180 48">
  <rect x="0" y="0" width="180" height="48" fill="#1a1a2e"/>
  <rect x="0" y="0" width="6" height="48" fill="{color}"/>
  <text x="93" y="32" font-family="'SF Mono', 'Consolas', monospace" font-size="18" font-weight="700" fill="#e2e8f0" text-anchor="middle" letter-spacing="1">{display}</text>
</svg>"""


def render_flat_category_badge_svg(display: str, color: str, width: int) -> str:
    """Render a flat-list category badge SVG."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28">
  <rect x="0" y="0" width="{width}" height="28" fill="#27272a"/>
  <rect x="0" y="0" width="4" height="28" fill="{color}"/>
  <text x="{width // 2 + 2}" y="19" font-family="'SF Mono', 'Consolas', monospace" font-size="12" font-weight="600" fill="#d4d4d8" text-anchor="middle">{display}</text>
</svg>"""
