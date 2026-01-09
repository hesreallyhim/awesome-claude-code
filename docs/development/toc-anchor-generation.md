# TOC Anchor Generation

## GitHub Anchor Generation Rules

GitHub generates heading anchors by:
1. Lowercasing the heading text
2. Replacing spaces with `-`
3. Removing special characters
4. Stripping emojis (each emoji leaves a `-` in its place)
5. Appending `-N` suffix for duplicate anchors (where N = 1, 2, 3...)

## Style-Specific Heading Formats

### AWESOME Style
```markdown
## Agent Skills 🤖
### General
```
- Category anchor: `#agent-skills-` (one dash from emoji)
- Subcategory anchor: `#general` (no trailing dash)

### CLASSIC Style
```markdown
## Agent Skills 🤖 [🔝](#awesome-claude-code)
<h3>General <a href="#awesome-claude-code">🔝</a></h3>
```
- Category anchor: `#agent-skills--` (two dashes: one from 🤖, one from 🔝)
- Subcategory anchor: `#general-` (one dash from 🔝)

### EXTRA/VISUAL Style
Uses explicit `id` attributes on headings, controlling anchors directly.

## Duplicate "General" Subcategory Handling

Multiple "General" subcategories across categories generate:
- First: `#general` (AWESOME) or `#general-` (CLASSIC)
- Second: `#general-1` (AWESOME) or `#general--1` (CLASSIC)
- Third: `#general-2` (AWESOME) or `#general--2` (CLASSIC)

Note: GitHub uses double-dash before the counter in CLASSIC due to the 🔝 emoji.

## Relevant Source Files

| File | Purpose |
|------|---------|
| `scripts/readme/markup/awesome.py` | AWESOME style TOC generation |
| `scripts/readme/markup/minimal.py` | CLASSIC style TOC generation |
| `scripts/readme/markup/visual.py` | EXTRA style TOC generation |
| `scripts/readme/helpers/readme_utils.py` | `get_anchor_suffix_for_icon()` helper |
| `scripts/testing/validate_toc_anchors.py` | Validation utility |

## Validation

### Manual Validation
```bash
# Validate root README (AWESOME style)
make validate-toc

# Validate CLASSIC style
python3 -m scripts.testing.validate_toc_anchors \
  --html .claude/readme-body-html-non-root-readme.html \
  --readme README_ALTERNATIVES/README_CLASSIC.md
```

### Obtaining GitHub HTML
1. Push README to GitHub
2. View rendered README page
3. Open browser dev tools (F12)
4. Find `<article>` element containing README content
5. Copy inner HTML to `.claude/root-readme-html-article-body.html`

### Automated Tests
```bash
make test  # Includes TOC anchor validation tests
```

## Common Pitfalls

1. **Extra dash before suffix**: `#{anchor}-{suffix}` when `suffix` already contains `-`
2. **Missing back-to-top dash**: CLASSIC style headings include 🔝 which adds a dash
3. **Wrong General counter format**: CLASSIC uses `general--N`, AWESOME uses `general-N`

## HTML Fixture Storage

Store GitHub-rendered HTML in `.claude/` (gitignored):

| Style | README Path | HTML Fixture Path |
|-------|-------------|-------------------|
| AWESOME | `README.md` | `.claude/github-html-awesome.html` |
| CLASSIC | `README_ALTERNATIVES/README_CLASSIC.md` | `.claude/github-html-classic.html` |
| EXTRA | `README_ALTERNATIVES/README_EXTRA.md` | `.claude/github-html-extra.html` |
| FLAT | `README_ALTERNATIVES/README_FLAT_ALL_AZ.md` | `.claude/github-html-flat.html` |

Validation commands:
```bash
# AWESOME
python3 -m scripts.testing.validate_toc_anchors \
  --html .claude/github-html-awesome.html --readme README.md

# CLASSIC
python3 -m scripts.testing.validate_toc_anchors \
  --html .claude/github-html-classic.html --readme README_ALTERNATIVES/README_CLASSIC.md

# EXTRA
python3 -m scripts.testing.validate_toc_anchors \
  --html .claude/github-html-extra.html --readme README_ALTERNATIVES/README_EXTRA.md

# FLAT
python3 -m scripts.testing.validate_toc_anchors \
  --html .claude/github-html-flat.html --readme README_ALTERNATIVES/README_FLAT_ALL_AZ.md
```

## Remaining Work

| Style | Validated | Notes |
|-------|-----------|-------|
| AWESOME | ✅ | Root README, tested and fixed |
| CLASSIC | ✅ | Tested and fixed (different anchor format due to 🔝 in headings) |
| EXTRA | ❌ | Uses explicit `id` attributes; needs validation |
| FLAT | ❌ | Simpler format (no subcategories); needs validation |

### TODO
- [ ] Download GitHub HTML for EXTRA style and validate
- [ ] Download GitHub HTML for FLAT style and validate
- [ ] Fix any anchor mismatches found in EXTRA/FLAT
- [ ] Consider unifying anchor generation logic into shared helpers
