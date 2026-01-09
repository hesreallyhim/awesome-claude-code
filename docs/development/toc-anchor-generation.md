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

GitHub-rendered HTML fixtures are stored in `tests/fixtures/github-html/` (version controlled).
Fixture filenames indicate root vs non-root placement to detect potential rendering differences:

| Style | README Path | HTML Fixture | Placement |
|-------|-------------|--------------|-----------|
| AWESOME | `README.md` | `awesome-root.html` | Root |
| CLASSIC | `README_ALTERNATIVES/README_CLASSIC.md` | `classic-non-root.html` | Non-root |
| EXTRA | `README_ALTERNATIVES/README_EXTRA.md` | `extra-non-root.html` | Non-root |
| FLAT | `README_ALTERNATIVES/README_FLAT_ALL_AZ.md` | `flat-non-root.html` | Non-root |

Validation commands:
```bash
# AWESOME (default)
python3 -m scripts.testing.validate_toc_anchors

# Other styles
python3 -m scripts.testing.validate_toc_anchors --style classic
python3 -m scripts.testing.validate_toc_anchors --style extra
python3 -m scripts.testing.validate_toc_anchors --style flat
```

## Validation Status

| Style | Status | Notes |
|-------|--------|-------|
| AWESOME | ✅ | Root README, 30 TOC anchors verified |
| CLASSIC | ✅ | Different anchor format due to 🔝 in headings |
| EXTRA | ✅ | Uses explicit `id` attributes; template anchor fixed |
| FLAT | ✅ | No TOC anchors (flat list format) |

## Future Work

- [ ] Unify anchor generation logic into shared helper with parameterized flags
- [ ] Add CI job to validate TOC anchors on README changes

---

## Architectural Decision: Anchor Generation Unification

**Date**: 2026-01-09

**Context**: TOC anchor generation logic is duplicated across three files (`awesome.py`, `minimal.py`, `visual.py`) with subtle differences due to each style's heading format.

**Options Considered**:

1. **Parameterized flags** - Create shared helper with semantic flags like `has_back_to_top_in_heading`
2. **Unify to ID-based** - Migrate all styles to use explicit `<h2 id="...">` like EXTRA

**Decision**: Option 1 (parameterized flags)

**Rationale**:
- Lower risk: heading markup remains unchanged
- AWESOME style intentionally uses clean markdown (`## Title`) for aesthetic reasons
- ID-based approach would require CLASSIC to restructure its `[🔝](#...)` links
- Parameterized flags are self-documenting and decouple anchor logic from style names

**Proposed API**:
```python
def generate_toc_anchor(
    title: str,
    icon: str | None = None,
    has_back_to_top_in_heading: bool = False,
) -> str:
    """Generate TOC anchor for a heading.

    Args:
        title: The heading text (e.g., "Agent Skills")
        icon: Optional trailing emoji icon (e.g., "🤖")
        has_back_to_top_in_heading: True if heading contains 🔝 back-to-top link
    """
```

**Trade-off**: If a style changes its heading format (e.g., CLASSIC removes 🔝), only the flag value changes—not the shared logic.
