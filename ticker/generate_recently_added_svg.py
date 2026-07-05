#!/usr/bin/env python3
"""Render the "Recently Added" carousel SVGs from our own resource table.

Unlike the scrolling tickers, this is a stop-slide-stop CAROUSEL of GitHub-pinned-
card-style repo cards: each card holds still to be read, then eases to the next.
Motion technique adapted from the prior-art pause-slide carousel (a single slider
group translated by `values` with `keyTimes`/`keySplines`).

Data source: THE_RESOURCES_TABLE_NEW.csv (our curated list) — the most recently
added active entries (by "Date Added"; blanks sort last). Deterministic selection,
so output is stable until the list changes.

Filter-free (GitHub renders SVG blur/glow poorly, esp. on mobile). Theme-adaptive:
emits dark + light variants for a <picture> embed.

Run:  python ticker/generate_recently_added_svg.py   (or `make recently-added`)
"""

from __future__ import annotations

import csv
import os
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "data" / "THE_RESOURCES_TABLE_NEW.csv"
# Source of truth lives at repo root in this dev repo; fall back to it.
if not CSV_PATH.exists():
    CSV_PATH = REPO_ROOT / "THE_RESOURCES_TABLE_NEW.csv"
ASSETS_DIR = Path(os.environ.get("RECENT_ASSETS_DIR") or (REPO_ROOT / "assets"))

RECENT_COUNT = 6  # cards in the carousel
SECONDS_PER_CARD = 6.5  # calmer dwell — each card sits still longer before sliding
VIEW_W = 800
VIEW_H = 240
STEP = VIEW_W  # one viewport per slide
HOLD_RATIO = 0.90  # fraction of each slide's time spent holding still (the "stop")
SLIDE_EASE = "0.45 0 0.55 1"  # cubic-bezier for the eased slide
HOLD_EASE = "0 0 1 1"  # linear (no movement during a hold)

NAME_MAX_CHARS = 26  # kept short so the title clears the top-right category pill
CAT_MAX_CHARS = 30
DESC_WRAP_CHARS = 74
DESC_MAX_LINES = 3

# GitHub "repo" octicon (16x16), placed per card.
REPO_ICON = (
    "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 "
    "0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm"
    "10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a"
    ".25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 "
    "0 0 1-.4-.2Z"
)

THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "card_bg": "#0d1117",
        "border": "#30363d",
        "name": "#58a6ff",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "pill_bg": "#21262d",
        "accent": "#3fb950",
    },
    "light": {
        "card_bg": "#ffffff",
        "border": "#d0d7de",
        "name": "#0969da",
        "text": "#1f2328",
        "muted": "#656d76",
        "pill_bg": "#f6f8fa",
        "accent": "#1a7f37",
    },
}


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def select_recent(rows: list[dict[str, str]], count: int) -> list[dict[str, str]]:
    """Most recently added active entries (Date Added desc, blanks last)."""
    active = [r for r in rows if (r.get("Active") or "").strip().upper() == "TRUE"]
    active.sort(key=lambda r: ((r.get("Date Added") or ""), r["Display Name"].casefold()), reverse=True)
    return active[:count]


def wrap_description(text: str, width: int = DESC_WRAP_CHARS, max_lines: int = DESC_MAX_LINES) -> list[str]:
    lines = textwrap.wrap(text.strip(), width=width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    lines[-1] = lines[-1].rstrip(".,;: ") + "…"
    return lines


def _truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip() + "…"


def build_card(repo: dict[str, str], colors: dict[str, str], x_offset: int) -> str:
    name = _esc(_truncate(repo["Display Name"], NAME_MAX_CHARS))
    author = _esc(_truncate(repo.get("Author Name", ""), 38))
    category = _esc(_truncate(repo.get("Category", ""), CAT_MAX_CHARS))
    desc_lines = [_esc(line) for line in wrap_description(repo.get("Description", ""))]

    desc_svg = "\n".join(
        f'    <text x="64" y="{140 + i * 24}" font-family="-apple-system, BlinkMacSystemFont, '
        f"'Segoe UI', Helvetica, Arial, sans-serif\" font-size=\"16\" fill=\"{colors['text']}\">{line}</text>"
        for i, line in enumerate(desc_lines)
    )

    # Category pill: top-right, aligned with the title row. (No per-card "RECENTLY
    # ADDED" kicker — the section heading above the carousel already says it.)
    pill_w = min(18 + len(category) * 7, 220)
    pill_x = 736 - pill_w
    return f"""  <g transform="translate({x_offset}, 0)">
    <rect x="40" y="24" width="720" height="192" rx="12" fill="{colors["card_bg"]}" stroke="{colors["border"]}" stroke-width="1"/>
    <g transform="translate(60, 46) scale(1.4)" fill="{colors["name"]}"><path d="{REPO_ICON}"/></g>
    <text x="98" y="66" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="26" font-weight="700" fill="{colors["name"]}">{name}</text>
    <rect x="{pill_x}" y="46" width="{pill_w}" height="24" rx="12" fill="{colors["pill_bg"]}"/>
    <text x="{pill_x + pill_w / 2}" y="62" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="12" fill="{colors["muted"]}">{category}</text>
    <text x="64" y="106" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="15" fill="{colors["muted"]}">by {author}</text>
{desc_svg}
  </g>"""


def build_animation(n: int, dur: float) -> tuple[str, str, str]:
    """Stop-slide-stop transform: hold each card, then ease to the next.

    Returns (values, keyTimes, keySplines). Slides through n cards plus a
    duplicate of the first for a seamless loop (final position -n*STEP).
    """
    unit = 1.0 / n
    times: list[float] = []
    values: list[str] = []
    splines: list[str] = []
    for i in range(n):
        start = i * unit
        hold_end = start + unit * HOLD_RATIO
        pos = -i * STEP
        times.append(start)
        values.append(f"{pos},0")
        times.append(hold_end)
        values.append(f"{pos},0")
        splines.append(HOLD_EASE)  # hold segment (start -> hold_end)
        splines.append(SLIDE_EASE)  # slide segment (hold_end -> next start)
    times.append(1.0)
    values.append(f"{-n * STEP},0")

    keytimes = "; ".join(f"{t:.4f}" for t in times)
    return "; ".join(values), keytimes, "; ".join(splines)


def build_svg(repos: list[dict[str, str]], theme: str) -> str:
    colors = THEMES[theme]
    n = len(repos)
    dur = n * SECONDS_PER_CARD

    # n real cards + a duplicate of the first at the wrap position.
    cards = [build_card(repo, colors, i * STEP) for i, repo in enumerate(repos)]
    cards.append(build_card(repos[0], colors, n * STEP))
    cards_svg = "\n".join(cards)

    values, keytimes, keysplines = build_animation(n, dur)

    return f"""<svg viewBox="0 0 {VIEW_W} {VIEW_H}" width="100%" xmlns="http://www.w3.org/2000/svg">
  <clipPath id="raClip"><rect x="0" y="0" width="{VIEW_W}" height="{VIEW_H}"/></clipPath>
  <g clip-path="url(#raClip)">
    <g id="raSlider">
      <animateTransform attributeName="transform" type="translate" calcMode="spline"
        values="{values}"
        keyTimes="{keytimes}"
        keySplines="{keysplines}"
        dur="{dur:.0f}s" repeatCount="indefinite"/>
{cards_svg}
    </g>
  </g>
</svg>"""


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = load_rows(CSV_PATH)
    repos = select_recent(rows, RECENT_COUNT)
    if not repos:
        print("⚠ No active entries found; nothing to render.")
        return

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for theme, filename in (("dark", "recently-added.svg"), ("light", "recently-added-light.svg")):
        (ASSETS_DIR / filename).write_text(build_svg(repos, theme), encoding="utf-8")
        print(f"✓ Generated {theme} theme: {ASSETS_DIR / filename}")
    print(f"  Cards: {', '.join(r['Display Name'] for r in repos)}")


if __name__ == "__main__":
    main()
