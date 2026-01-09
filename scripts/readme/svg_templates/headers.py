"""SVG renderers for section headers."""


def render_h2_svg(text: str, icon: str = "") -> str:
    """Create an animated hero-centered H2 header SVG string.

    Args:
        text: The header text (e.g., "Agent Skills")
        icon: Optional icon to append (e.g., an emoji)
    """
    # Build display text with optional icon
    display_text = f"{text} {icon}" if icon else text

    # Escape XML special characters
    text_escaped = display_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Calculate viewBox bounds based on text length
    # Text is centered at x=400, font-size 38px ~ 22px per char, emoji ~ 50px
    text_width = len(text) * 22 + (50 if icon else 0)
    half_text = text_width / 2
    # Ensure we include decorations (x=187 to x=613) plus text bounds with generous padding
    left_bound = int(min(180, 400 - half_text - 30))
    right_bound = int(max(620, 400 + half_text + 30))
    viewbox_width = right_bound - left_bound

    return f"""<svg width="100%" height="100" viewBox="{left_bound} 0 {viewbox_width} 100" xmlns="http://www.w3.org/2000/svg">
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


def render_h3_svg(text: str) -> str:
    """Create an animated minimal-inline H3 header SVG string."""
    # Escape XML special characters
    text_escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Calculate approximate text width (rough estimate: 10px per character for 18px font)
    text_width = len(text) * 10
    total_width = text_width + 50  # Add padding for decorative elements

    return f"""<svg width="100%" height="36" viewBox="0 0 {total_width} 36" xmlns="http://www.w3.org/2000/svg">
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
