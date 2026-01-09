"""SVG renderers for section dividers and boxes."""


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
