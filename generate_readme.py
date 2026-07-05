"""Generate README.md from the CSV source of truth.

Reads THE_RESOURCES_TABLE_NEW.csv (single source of truth) and config.yaml
(category / sub-category ordering + optional blurbs), renders the categorized
Awesome list plus its Table of Contents, and substitutes them into the
{{TABLE_OF_CONTENTS}} / {{THE_LIST}} tokens in templates/README.template.md to
produce README.md.

Properties:
  * Idempotent: output is a pure function of (template, CSV, config). Re-running
    produces a byte-identical README.md.
  * Fail-closed: if any Active CSV entry has a Category not declared in
    config.yaml, generation aborts with a non-zero exit and writes nothing.

Run:  venv/bin/python generate_readme.py   (or `make generate`)
"""

from __future__ import annotations

import csv
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "THE_RESOURCES_TABLE_NEW.csv"
CONFIG_PATH = BASE / "config.yaml"
TEMPLATE_PATH = BASE / "templates" / "README.template.md"
OUTPUT_PATH = BASE / "README.md"

TOC_TOKEN = "{{TABLE_OF_CONTENTS}}"
LIST_TOKEN = "{{THE_LIST}}"
TICKER_TOKEN = "{{CLAUDE_CODE_TICKER}}"
RECENTLY_ADDED_TOKEN = "{{RECENTLY_ADDED}}"

# Ticker SVG asset, relative to README.md at the repo root. The "awesome" (clean,
# minimal) style is the canonical plain look for this list; produced out-of-band
# by the ticker workflow (ticker/generate_ticker_svg.py).
TICKER_SVG = "assets/repo-ticker.svg"

# "Recently Added" carousel SVGs (theme-adaptive dark/light), produced out-of-band
# from the CSV by ticker/generate_recently_added_svg.py (`make recently-added`).
RECENTLY_ADDED_SVG = "assets/recently-added.svg"
RECENTLY_ADDED_SVG_LIGHT = "assets/recently-added-light.svg"


def _load_formatter() -> Any:
    """Import the hyphen-named formatter module by path."""
    path = BASE / "resources" / "awesome-list-entry-formatter.py"
    spec = importlib.util.spec_from_file_location("awesome_formatter", path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load formatter module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


formatter = _load_formatter()


# --------------------------------------------------------------------------- #
# Config / CSV loading
# --------------------------------------------------------------------------- #
def load_config() -> list[dict[str, Any]]:
    """Return the ordered list of category mappings from config.yaml.

    Each item is normalized to {name, description, subcategories} where
    subcategories is a list of {name, description}.
    """
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    raw_categories = data.get("categories", []) or []
    categories: list[dict[str, Any]] = []
    for raw in raw_categories:
        if isinstance(raw, str):
            raw = {"name": raw}
        subs_out: list[dict[str, str]] = []
        for sub in raw.get("subcategories", []) or []:
            if isinstance(sub, str):
                sub = {"name": sub}
            subs_out.append(
                {"name": sub["name"], "description": (sub.get("description") or "").strip()}
            )
        categories.append(
            {
                "name": raw["name"],
                "description": (raw.get("description") or "").strip(),
                "subcategories": subs_out,
            }
        )
    return categories


def load_active_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [r for r in rows if (r.get("Active") or "").strip().upper() == "TRUE"]


def validate_categories(rows: list[dict[str, str]], categories: list[dict[str, Any]]) -> None:
    """Fail closed: every Active row's Category must be declared in config.yaml."""
    known = {c["name"] for c in categories}
    offenders: dict[str, list[str]] = {}
    for row in rows:
        category = (row.get("Category") or "").strip()
        if category not in known:
            offenders.setdefault(category, []).append(row.get("ID", "?"))
    if offenders:
        print(
            "ERROR: Active CSV entries reference categories not present in config.yaml.\n"
            "Add them to config.yaml (to set their order) or mark the entries inactive.\n",
            file=sys.stderr,
        )
        for category, ids in sorted(offenders.items()):
            shown = ", ".join(ids[:10]) + (" ..." if len(ids) > 10 else "")
            print(f"  - {category!r}: {len(ids)} entr(y/ies) [{shown}]", file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def github_slug(text: str) -> str:
    """Replicate GitHub's heading-anchor algorithm.

    Lowercase; drop characters that are not word chars, spaces, or hyphens (so
    `&`, `,`, `/`, `()` vanish); convert spaces to hyphens. GitHub does
    NOT collapse the resulting runs of hyphens, e.g. "Design & UI/UX" ->
    "design--uiux". (Duplicate heading names would need a -1/-2 suffix; the
    current data has none.)
    """
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def _sort_key(row: dict[str, str]) -> str:
    return row["Display Name"].casefold()


def _render_entries(rows: list[dict[str, str]]) -> str:
    """Alphabetical (case-insensitive) entries, blank line between each."""
    ordered = sorted(rows, key=_sort_key)
    return "\n\n".join(formatter.format_entry(r) for r in ordered)


def build_list(rows: list[dict[str, str]], categories: list[dict[str, Any]]) -> str:
    """Render the full categorized list for {{THE_LIST}}."""
    blocks: list[str] = []
    for cat in categories:
        cat_rows = [r for r in rows if (r.get("Category") or "").strip() == cat["name"]]
        if not cat_rows:
            # Skip categories with no active entries (mirrors build_toc) so a
            # category declared ahead of its first resource doesn't render as a
            # bare heading. It stays in config.yaml for ordering + validation.
            continue
        section: list[str] = [f"## {cat['name']}"]
        if cat["description"]:
            section.append(cat["description"])

        configured_subs = cat["subcategories"]
        configured_names = [s["name"] for s in configured_subs]
        # Sub-categories actually present on entries, in config order first, then
        # any leftover (lenient) sub-categories alphabetically; finally "" (none).
        present = {(r.get("Sub-Category") or "").strip() for r in cat_rows}
        leftover = sorted(n for n in present if n and n not in configured_names)

        if not present - {""} and not configured_subs:
            # Flat category: render entries directly under the heading.
            body = _render_entries(cat_rows)
            if body:
                section.append(body)
        else:
            # Entries with no sub-category come first, then ordered sub-sections.
            no_sub = [r for r in cat_rows if not (r.get("Sub-Category") or "").strip()]
            if no_sub:
                section.append(_render_entries(no_sub))
            for sub in configured_subs + [{"name": n, "description": ""} for n in leftover]:
                sub_rows = [
                    r for r in cat_rows if (r.get("Sub-Category") or "").strip() == sub["name"]
                ]
                if not sub_rows:
                    continue
                sub_block = [f"### {sub['name']}"]
                if sub.get("description"):
                    sub_block.append(sub["description"])
                sub_block.append(_render_entries(sub_rows))
                section.append("\n\n".join(sub_block))

        blocks.append("\n\n".join(section))
    return "\n\n".join(blocks)


def build_toc(rows: list[dict[str, str]], categories: list[dict[str, Any]]) -> str:
    """Render the nested Table of Contents for {{TABLE_OF_CONTENTS}}."""
    lines: list[str] = []
    for cat in categories:
        cat_rows = [r for r in rows if (r.get("Category") or "").strip() == cat["name"]]
        if not cat_rows:
            continue
        lines.append(f"- [{cat['name']}](#{github_slug(cat['name'])})")
        configured_names = [s["name"] for s in cat["subcategories"]]
        present = {(r.get("Sub-Category") or "").strip() for r in cat_rows}
        leftover = sorted(n for n in present if n and n not in configured_names)
        for name in configured_names + leftover:
            if any((r.get("Sub-Category") or "").strip() == name for r in cat_rows):
                lines.append(f"  - [{name}](#{github_slug(name)})")
    return "\n".join(lines)


def ticker_markup() -> str:
    """Centered <picture> embedding the animated repo-ticker SVG (awesome style).

    Static and deterministic, so it does not affect README idempotency. The SVG
    file itself is regenerated separately (semi-randomly, several times a day) by
    the ticker workflow.
    """
    return (
        '<div align="center">\n\n'
        "<picture>\n"
        f'  <img src="{TICKER_SVG}" alt="Featured Claude Code Projects" width="100%">\n'
        "</picture>\n\n"
        "</div>"
    )


def recently_added_markup() -> str:
    """Centered theme-adaptive <picture> for the "Recently Added" carousel.

    Serves the light SVG under a light color scheme, dark otherwise. Static and
    deterministic (does not affect README idempotency); the SVGs are regenerated
    out-of-band from the CSV by ticker/generate_recently_added_svg.py.
    """
    return (
        '<div align="center">\n\n'
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: light)" srcset="{RECENTLY_ADDED_SVG_LIGHT}">\n'
        f'  <img src="{RECENTLY_ADDED_SVG}" alt="Recently Added Resources" width="100%">\n'
        "</picture>\n\n"
        "</div>"
    )


def render_readme(
    template: str, rows: list[dict[str, str]], categories: list[dict[str, Any]]
) -> str:
    """Pure render: substitute the TOC, list, ticker, and carousel tokens.

    Deterministic in (template, rows, categories) — the basis of idempotency.
    """
    return (
        template.replace(TOC_TOKEN, build_toc(rows, categories))
        .replace(LIST_TOKEN, build_list(rows, categories))
        .replace(TICKER_TOKEN, ticker_markup())
        .replace(RECENTLY_ADDED_TOKEN, recently_added_markup())
    )


def main() -> None:
    categories = load_config()
    rows = load_active_rows()
    validate_categories(rows, categories)

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered = render_readme(template, rows, categories)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.name} ({len(rows)} active entries, {len(categories)} categories)")


if __name__ == "__main__":
    main()
