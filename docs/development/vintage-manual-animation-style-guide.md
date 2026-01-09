# Vintage Manual Animation Style Guide

A comprehensive guide to the animation effects developed for the light mode "vintage technical manual" theme. These animations are designed to evoke 70s-80s computer documentation, printing, and paper-based media while remaining subtle and professional.

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Animation Patterns](#animation-patterns)
   - [Typewriter Reveal](#1-typewriter-reveal)
   - [Print Scan](#2-print-scan)
   - [Stamp Press](#3-stamp-press)
   - [Registration Shift](#4-registration-shift)
   - [Line Printer](#5-line-printer)
5. [Parameterization Guide](#parameterization-guide)
6. [Implementation Examples](#implementation-examples)

---

## Design Principles

1. **Paper-like Motion**: Animations should feel physical - like ink, paper, and mechanical processes
2. **Warm Aesthetics**: Use sepia tones that suggest aged paper and vintage printing
3. **Purposeful Timing**: Each animation should have clear phases (anticipation, action, settle)
4. **Loopable**: Animations should loop seamlessly without jarring resets

---

## Color Palette

```css
/* Primary Colors */
--ink-dark: #2d251f;        /* Main text, darkest ink */
--ink-medium: #3d3530;      /* Secondary text */
--ink-light: #5c5247;       /* Tertiary, rules, borders */
--ink-faded: #6b5b4f;       /* Subtle text, descriptions */
--ink-ghost: #7a6b5f;       /* Very light text */
--ink-muted: #8a7b6f;       /* Metadata, timestamps */

/* Accent Colors */
--accent-terracotta: #c96442;  /* Section numbers, highlights */
--accent-warm: #9a8b7f;        /* Warm gray accent */

/* Paper Colors */
--paper-light: #faf8f3;     /* Lightest paper */
--paper-cream: #f5f0e6;     /* Standard paper */
--paper-aged: #f2ede4;      /* Slightly aged */
--paper-shadow: #e8e3d9;    /* Paper shadow/fold */

/* Border Colors */
--border-light: #c4baa8;    /* Light borders */
--border-medium: #b0a696;   /* Medium borders */

/* Print Effects */
--greenbar: #4a7c4a;        /* Green bar paper stripe */
--perf-hole: #d4cfc5;       /* Perforation holes */
--cyan-offset: #6b8a8a;     /* Registration cyan layer */
--magenta-offset: #8a6b6b;  /* Registration magenta layer */
```

---

## Typography

```css
/* Primary Heading - Serif */
font-family: Georgia, 'Times New Roman', serif;
font-size: 38px;
font-weight: 400;
letter-spacing: 8px;

/* Secondary Heading - Monospace */
font-family: 'Courier New', Courier, monospace;
font-size: 12px;
letter-spacing: 3px;

/* Body/Tagline - Serif Italic */
font-family: Georgia, 'Times New Roman', serif;
font-size: 13px;
font-style: italic;

/* Technical/Metadata - Monospace */
font-family: 'Courier New', Courier, monospace;
font-size: 9px;
```

---

## Animation Patterns

### 1. Typewriter Reveal

**Concept**: Characters appear sequentially, mimicking a typewriter or teletype machine.

**Timing**: 6 second cycle
- Characters appear every 0.3s
- Cursor follows and blinks
- Subtitle/tagline fade in after title completes

**Core Technique**:
```xml
<!-- Each character has staggered opacity animation -->
<text x="100" y="50" opacity="0">A
  <animate
    attributeName="opacity"
    values="0;0;1;1;1;1;1;1;1;1"
    dur="6s"
    repeatCount="indefinite"/>
</text>

<text x="120" y="50" opacity="0">W
  <animate
    attributeName="opacity"
    values="0;0;0;1;1;1;1;1;1;1"
    dur="6s"
    repeatCount="indefinite"/>
</text>

<!-- Cursor follows typing position -->
<rect width="4" height="28" fill="#2d251f">
  <animate
    attributeName="x"
    values="100;120;140;160;180"
    dur="6s"
    repeatCount="indefinite"
    calcMode="discrete"/>
  <animate
    attributeName="opacity"
    values="1;0"
    dur="0.5s"
    repeatCount="indefinite"/>
</rect>
```

**Parameters**:
- `charDelay`: Time between each character (default: 0.3s)
- `cursorBlinkRate`: Cursor blink speed (default: 0.5s)
- `holdTime`: Time to display complete text before reset

**Generator Function** (JavaScript):
```javascript
function generateTypewriterText(text, x, y, options = {}) {
  const {
    charWidth = 24,
    charDelay = 0.3,
    cycleDuration = 6,
    fontSize = 36
  } = options;

  const chars = text.split('');
  const totalChars = chars.length;

  return chars.map((char, i) => {
    const charX = x + (i * charWidth);
    const appearTime = (i * charDelay) / cycleDuration;
    const values = Array(20).fill('1');
    const appearIndex = Math.floor(appearTime * 20);
    for (let j = 0; j < appearIndex; j++) values[j] = '0';

    return `
      <text x="${charX}" y="${y}" opacity="0">${char}
        <animate attributeName="opacity"
                 values="${values.join(';')}"
                 dur="${cycleDuration}s"
                 repeatCount="indefinite"/>
      </text>`;
  }).join('\n');
}
```

---

### 2. Print Scan

**Concept**: A glowing scan bar sweeps across, simulating a print head or scanner.

**Timing**: 4 second cycle (continuous)

**Core Technique**:
```xml
<defs>
  <!-- Gradient for scan bar glow -->
  <linearGradient id="scanGlow" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" style="stop-color:#c96442;stop-opacity:0"/>
    <stop offset="50%" style="stop-color:#c96442;stop-opacity:0.6"/>
    <stop offset="100%" style="stop-color:#c96442;stop-opacity:0"/>
  </linearGradient>
</defs>

<!-- Scan bar that moves across -->
<rect x="-100" y="0" width="100" height="180" fill="url(#scanGlow)">
  <animate
    attributeName="x"
    values="-100;950"
    dur="4s"
    repeatCount="indefinite"/>
</rect>

<!-- Optional: Print head indicator dot -->
<circle r="3" fill="#c96442" opacity="0.8">
  <animate attributeName="cx" values="-50;900" dur="4s" repeatCount="indefinite"/>
  <animate attributeName="cy" values="10;10;170;170;10" dur="4s" repeatCount="indefinite"/>
</circle>
```

**Parameters**:
- `scanDuration`: Time for full sweep (default: 4s)
- `barWidth`: Width of scan bar (default: 100px)
- `glowColor`: Scan bar color (default: #c96442)
- `direction`: 'ltr' | 'rtl' | 'ttb' | 'btt'

---

### 3. Stamp Press

**Concept**: Elements drop from above and "press" into the paper with a bounce and ink spread.

**Timing**: 5 second cycle
- Elements start offset above
- Drop with slight overshoot
- Bounce back to final position
- Ink spread effect at moment of impact

**Core Technique**:
```xml
<defs>
  <!-- Shadow that animates with press -->
  <filter id="stampShadow">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#3d3530" flood-opacity="0.2">
      <animate attributeName="dy" values="4;0;0;0;0;0" dur="5s" repeatCount="indefinite"/>
      <animate attributeName="stdDeviation" values="4;1;1;1;1;1" dur="5s" repeatCount="indefinite"/>
    </feDropShadow>
  </filter>

  <!-- Ink spread filter -->
  <filter id="inkSpread">
    <feMorphology operator="dilate" radius="0">
      <animate attributeName="radius" values="0;0.5;0" dur="3s" repeatCount="indefinite"/>
    </feMorphology>
  </filter>
</defs>

<!-- Element with stamp animation -->
<text filter="url(#stampShadow)" opacity="0">
  TITLE TEXT
  <animate attributeName="opacity" values="0;0;0;1;1;1" dur="5s" repeatCount="indefinite"/>
  <animateTransform
    attributeName="transform"
    type="translate"
    values="0,-15;0,-15;0,-15;0,3;0,0;0,0"
    dur="5s"
    repeatCount="indefinite"/>
</text>
```

**Parameters**:
- `dropDistance`: How far above element starts (default: 15px)
- `bounceAmount`: Overshoot distance (default: 3px)
- `stampDelay`: Stagger between elements (default: 0.5s)
- `inkSpreadRadius`: Maximum ink spread (default: 0.5)

---

### 4. Registration Shift

**Concept**: Color layers start misaligned and shift into registration, like offset printing.

**Timing**: 4 second cycle
- Cyan and magenta layers offset by ~3px
- Shift to aligned position
- Hold aligned
- Quick reset

**Core Technique**:
```xml
<!-- Cyan offset layer (behind) -->
<text x="450" y="85" fill="#6b8a8a" opacity="0.15">
  TITLE TEXT
  <animate attributeName="x" values="447;450;450;450" dur="4s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0.25;0.1;0.1;0.1" dur="4s" repeatCount="indefinite"/>
</text>

<!-- Magenta offset layer (behind) -->
<text x="450" y="85" fill="#8a6b6b" opacity="0.15">
  TITLE TEXT
  <animate attributeName="x" values="453;450;450;450" dur="4s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0.25;0.1;0.1;0.1" dur="4s" repeatCount="indefinite"/>
</text>

<!-- Main layer (on top) -->
<text x="450" y="85" fill="#2d251f">
  TITLE TEXT
  <animate attributeName="y" values="83;85;85;85" dur="4s" repeatCount="indefinite"/>
</text>
```

**Parameters**:
- `offsetDistance`: How far layers are misaligned (default: 3px)
- `cyanOffset`: Direction of cyan layer (default: -3, 0)
- `magentaOffset`: Direction of magenta layer (default: +3, 0)
- `settleTime`: Time to reach alignment (default: 25% of cycle)

---

### 5. Line Printer

**Concept**: Content reveals top-to-bottom like continuous form paper feeding through a printer.

**Timing**: 8 second cycle (with pause)
- Paper feeds down revealing content (2s)
- Hold/pause (4s)
- Rapid wipe up to reset (1s)
- Brief blank (1s)

**Core Technique**:
```xml
<defs>
  <!-- Clip path for line reveal -->
  <clipPath id="lineReveal">
    <rect x="0" y="0" width="900" height="0">
      <!-- Down (reveal) - pause - up (hide) - pause -->
      <animate
        attributeName="height"
        values="0;180;180;180;180;180;0;0"
        keyTimes="0;0.25;0.3;0.7;0.75;0.8;0.9;1"
        dur="8s"
        repeatCount="indefinite"/>
    </rect>
  </clipPath>

  <!-- Green bar paper pattern -->
  <pattern id="greenBar" width="60" height="60" patternUnits="userSpaceOnUse">
    <rect width="60" height="30" fill="#4a7c4a" opacity="0.08"/>
  </pattern>

  <!-- Perforation pattern -->
  <pattern id="perfEdge" width="10" height="20" patternUnits="userSpaceOnUse">
    <circle cx="5" cy="10" r="2" fill="#d4cfc5"/>
  </pattern>
</defs>

<!-- Perforated edges -->
<rect x="0" y="0" width="12" height="180" fill="url(#perfEdge)" opacity="0.5"/>
<rect x="888" y="0" width="12" height="180" fill="url(#perfEdge)" opacity="0.5"/>

<!-- Green bar stripes -->
<rect x="20" y="0" width="860" height="180" fill="url(#greenBar)"/>

<!-- Content with clip -->
<g clip-path="url(#lineReveal)">
  <!-- All content here -->
</g>

<!-- Print head line -->
<line x1="20" y1="0" x2="880" y2="0" stroke="#c96442" stroke-width="2">
  <animate
    attributeName="y1"
    values="0;180;180;180;180;180;0;0"
    keyTimes="0;0.25;0.3;0.7;0.75;0.8;0.9;1"
    dur="8s"
    repeatCount="indefinite"/>
</line>
```

**Parameters**:
- `revealSpeed`: Time to reveal content (default: 2s)
- `holdTime`: Pause duration (default: 4s)
- `wipeSpeed`: Time to wipe up (default: 1s)
- `showGreenBar`: Boolean for green bar paper effect
- `showPerforations`: Boolean for feed holes

---

## Parameterization Guide

### Creating a Generator Function

```javascript
function generateVintageManualSVG(options) {
  const {
    width = 900,
    height = 180,
    title = 'TITLE',
    subtitle = 'Subtitle',
    tagline = 'Tagline text here',
    animation = 'lineprint', // typewriter|printscan|stamp|registration|lineprint
    colors = {
      ink: '#2d251f',
      accent: '#c96442',
      paper: '#faf8f3'
    },
    timing = {
      cycleDuration: 8,
      revealDuration: 2,
      holdDuration: 4
    }
  } = options;

  // Generate SVG based on animation type
  switch(animation) {
    case 'typewriter':
      return generateTypewriterSVG(options);
    case 'printscan':
      return generatePrintScanSVG(options);
    case 'stamp':
      return generateStampSVG(options);
    case 'registration':
      return generateRegistrationSVG(options);
    case 'lineprint':
      return generateLinePrintSVG(options);
  }
}
```

### CSS Custom Properties Approach

```css
:root {
  --manual-cycle-duration: 8s;
  --manual-reveal-duration: 2s;
  --manual-hold-duration: 4s;
  --manual-ink-color: #2d251f;
  --manual-accent-color: #c96442;
  --manual-paper-color: #faf8f3;
}
```

---

## Implementation Examples

### React Component

```jsx
const VintageHeader = ({
  title,
  subtitle,
  animation = 'lineprint',
  cycleDuration = 8
}) => {
  return (
    <svg viewBox="0 0 900 180" className="vintage-header">
      {/* SVG content with dynamic values */}
    </svg>
  );
};
```

### Web Component

```javascript
class VintageManualHeader extends HTMLElement {
  static get observedAttributes() {
    return ['title', 'subtitle', 'animation', 'duration'];
  }

  connectedCallback() {
    this.render();
  }

  render() {
    const animation = this.getAttribute('animation') || 'lineprint';
    // Generate appropriate SVG
  }
}

customElements.define('vintage-header', VintageManualHeader);
```

---

## File Reference

| Animation | File | Cycle | Best For |
|-----------|------|-------|----------|
| Typewriter | `terminal-header-light-anim-typewriter.svg` | 6s | One-time reveals, loading states |
| Print Scan | `terminal-header-light-anim-printscan.svg` | 4s | Continuous ambient animation |
| Stamp Press | `terminal-header-light-anim-stamp.svg` | 5s | Dramatic entrances, hero sections |
| Registration | `terminal-header-light-anim-registration.svg` | 4s | Subtle ambient animation |
| Line Printer | `terminal-header-light-anim-lineprint.svg` | 8s | Headers, document-style layouts |

---

*Style Guide Version 1.0 - Created for Awesome Claude Code*
