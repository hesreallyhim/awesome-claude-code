# UI Generation vs. Hard-Coding

This repository mixes generated UI assets with a few hand-authored bits. This note documents what is still hard-coded so you know where to edit when changing layout or text.

## Generated
- README body, TOC, and anchors via `scripts/generate_readme.py` using `templates/README.template.md`.
- TOC rows/subrows (dark/light) and light TOC header when `REGEN_TOC_ASSETS=1 make generate` is used.
- Category headers (dark/light) and subheaders (`subheader_*.svg`) via the generators.
- Resource badges (light) during README generation.

## Hard-Coded / Manual
- The “Terminal Navigation” card grid in `templates/README.template.md`:
  - Card assets (`assets/card-*.svg`) are static files.
  - Anchor hrefs are manually set; they must match the category IDs and their trailing dash convention (e.g., `#tooling-`, `#workflows-knowledge-guides-`, `#official-documentation-`).
- Most assets under `assets/` (cards, subheaders, banners, section dividers, etc.) remain hand-authored; only the TOC rows/subrows/light header, category headers, and badges are generated.
- Dark TOC header (`assets/toc-header.svg`) is static (light version is generated).
- Any custom copy in `templates/README.template.md` that is outside the placeholder slots stays manual.

## Regeneration Tips
- Run `REGEN_TOC_ASSETS=1 make generate` to regenerate the TOC assets (rows/subrows/light header) along with README.
- If you change category IDs/names, update:
  - `templates/categories.yaml`
  - The card-grid anchor hrefs in `templates/README.template.md`
  - Any static assets that embed text (e.g., card SVGs), since those are not regenerated automatically.
