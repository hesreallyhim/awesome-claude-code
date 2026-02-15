# README Generation & Asset Management

This document explains how the README and its visual assets are generated and maintained. It's mostly a reference document for development purposes, written and maintained by the coding agents who write most of the code, with some commentary sprinkled in.

## Overview

The repository implements a "multi-list" pattern, with one centralized "list" (which is effectively a kind of backend) and numerous "views" that are strictly generated from the central data source. In that sense, it's maybe the only "full-stack" Awesome list on GitHub - maybe that's a sign that it's a silly thing to do, but I figured if I was going to spend so much time maintaining a list, I had better do something interesting with it. To my knowledge, it's one of the few "full-stack applications" that's entirely hosted on GitHub.com (i.e. not a GitHub Pages site). (Yes, there are others. And yes, calling this an "application" is obviously a little bit of a stretch.)

- **`THE_RESOURCES_TABLE.csv`** - The master data file containing all resources (repo root)
- **`acc-config.yaml`** - Global configuration (root style, style selector settings)
- **`templates/categories.yaml`** - Category and subcategory definitions
- **`scripts/readme/generate_readme.py`** - The generator script (class-based architecture)
- **`scripts/readme/helpers/readme_config.py`** - Config loader and style path helpers
- **`scripts/readme/helpers/readme_utils.py`** - Shared parsing/anchor utilities
- **`scripts/readme/helpers/readme_assets.py`** - SVG asset writers (badges, TOC rows, headers)
- **`scripts/readme/markup/`** - Markdown/HTML renderers by style
- **`scripts/readme/svg_templates/`** - SVG renderers used by the generator
- **`assets/`** - SVG visual assets (badges, headers, dividers, etc.)

The multi-list is maintained via a single source of truth, combined with generators that take templates (which implement the various styles), and generate all the READMEs. The complexity is mostly self-inflicted, and is an artefact of platform-specific features of GitHub.

### Generated README Styles

| Style | Primary Output | Template | Description |
|-------|-------------|----------|-------------|
| Extra (Visual) | `README_ALTERNATIVES/README_EXTRA.md` | `README_EXTRA.template.md` | Full visual theme with SVG badges, CRT-style TOC |
| Classic | `README_ALTERNATIVES/README_CLASSIC.md` | `README_CLASSIC.template.md` | Plain markdown with collapsible sections |
| Awesome | `README_ALTERNATIVES/README_AWESOME.md` | `README_AWESOME.template.md` | Clean awesome-list style |
| Flat | `README_ALTERNATIVES/README_FLAT_*.md` | Built-in template (optional `templates/README_FLAT.template.md`) | 44 table views (category × sort combinations) |

All styles are always generated under `README_ALTERNATIVES/`. The `root_style` is additionally written to `README.md`.

#### Etymology

- **Classic:** The style of the list as it was initially maintained and iterated upon, before the "multi-list" pattern was adopted.
- ***Extra:*** Heightened visual style, consisting almost entirely of SVG assets - "extra" does not mean "additional", it means _extra_.
- **Flat:** Lacks internal structure or visual hierarchy; the "flat" views are basically just a dump of the CSV data with shields.io badges - information-dense and straightforward. This was implemented due to a single user's request, but it became a more interesting problem when the user asked for dynamic table features like sorting and filtering. This is "not possible" with Markdown, which is why I decided to do it - since you can't have any JavaScript on a README, the sorting and filtering functionality is simulated by generating every permutation of Sort x Filter as a separate file, and so the table operations become navigation.
- **Awesome:** The style that is more or less compliant with the Awesome List style guide.

Generation runs in two phases:
1. Generate all styles under `README_ALTERNATIVES/`.
2. Generate `README.md` using the configured `root_style`.

If everything lived at the repo root, this would be a very easy thing to build, but then the user would have to scroll a lot before they even hit the first `h1`. So the whole complexity is due to the necessity of supporting multiple generated README files at two different paths. I'm not even sure if many people enjoy the "Flat" view, and without the 44 permutations, it probably wouldn't be a big deal at all to just put everything at the root... Hm. Nevertheless, I'm grateful to that user for giving me the opportunity to learn some new things, and to build this ridiculous Titanic just to host a list, and I hope the "curiosity" of it compensates for any aesthetic crimes that I've committed in building it.

## Configuration (`acc-config.yaml`)

The `acc-config.yaml` file at the repository root controls global README generation settings.

### Root Style

The `readme.root_style` setting determines which README style is additionally written to the repo root (`README.md`). All styles are always generated in `README_ALTERNATIVES/`.

```yaml
readme:
  root_style: extra  # Options: extra, classic, awesome, flat
```

Changing this value and regenerating will:
- Write the new root style to `README.md`
- Keep all styles (including the root) in `README_ALTERNATIVES/`
- Update the style selector links to reflect which style is root

### Style Selector Configuration

The `styles` section defines each README style's metadata for the style selector:

```yaml
styles:
  extra:
    name: Extra                    # Display name for badge alt text
    badge: badge-style-extra.svg   # Badge filename in assets/
    highlight_color: "#6a6a8a"     # Border color when selected
    filename: README_EXTRA.md

  classic:
    name: Classic
    badge: badge-style-classic.svg
    highlight_color: "#c9a227"
    filename: README_CLASSIC.md
  # ... other styles
```

`filename` is the README variant filename under `README_ALTERNATIVES/` used for selector links and references.

The `style_order` list controls the left-to-right order of badges in the selector:

```yaml
style_order:
  - extra
  - classic
  - flat
  - awesome
```

## Quick Reference

| Task | Automated? | What to do |
|------|------------|------------|
| Add a new resource | Yes | Add row to CSV, run `make generate` |
| Add a new category | Yes | Use `make add-category` or edit `categories.yaml` |
| Add a new subcategory | Yes | Edit `categories.yaml`, run `make generate-toc-assets`, run generator |
| Update resource info | Yes | Edit CSV, run `make generate` |
| Customize asset style | Manual | Edit generator templates or asset files |

## Backups (README Outputs)

The README generators create a backup of the existing output file before overwriting it.

- Location: `.myob/backups/` at repo root
- Naming: `{basename}.{YYYYMMDD_HHMMSS}.bak` (e.g., `README.md.20250105_154233.bak`)
- Behavior: only created when the target file already exists
- Coverage: applies to README outputs written by `scripts/readme/generate_readme.py`
- Retention: keeps the most recent backup per output file; older backups are pruned

## Adding a New Resource

This process is now handled entirely by GitHub workflows. Due to the intricate, not-at-all-over-engineered design ~~mistakes~~ choices, having people submit PRs became unmanageable. Instead, all of the data that goes into a resource entry is processed as a "form" using GitHub's Issue form templates. That makes the shape of an Issue predictable, and the different fields are machine-readable. Since the resources table is the single source of truth for the list entries, the goal is just to get the necessary data points into the CSV, and everything else is controlled by the template/generator system. This eliminated any problems around merge conflicts, stale resource PRs, etc. (Trying to fix merge conflicts in a CSV file is not a good way to spend an afternoon.) The _state_ of resource recommendation Issues is managed by (i) labels (`pending-validation`, `validation-passed`, `approved`, etc.), which indicate the current state; (ii) "slash commands" (`/approve`, `/request-changes`, etc.), which trigger a workflow that transitions the state (if they're written by the maintainer). This is a simplified piecture of what the GitHub bot does once a resource is approved:

1. **Edit `THE_RESOURCES_TABLE.csv`** - Add a new row with these columns:
   - `Display Name` - The resource name shown in the README
   - `Primary Link` - URL to the resource (usually GitHub)
   - `Author Name` - Creator's name (optional but recommended)
   - `Author Link` - URL to author's profile
   - `Description` - Brief description of the resource
   - `Category` - Must match a category name in `categories.yaml`
   - `Sub-Category` - Must match a subcategory in `categories.yaml`
   - `Active` - Set to `TRUE` to include in README
   - `Removed From Origin` - Set to `TRUE` if the original repo/resource was deleted

The reason for the last field is due to the fact that (i) well, it's good to know if you're sharing a link that's dead; (ii) for a while, I was maintaing copies of the third-party authors' resources on the list (when it was licensed in a way that allowed me to do that), but that was when the resource were usually a bit of plaintext. Most entries are full repositories, and re-hosting entire repositories is out of scope. That directory is still present, but it's not currently maintained, and may become deprecated.

2. **Run the generator:**
   ```bash
   make generate
   # or directly:
   python3 scripts/readme/generate_readme.py
   ```

3. **What gets auto-generated:**
   - `assets/badge-{resource-name}.svg` - Theme-adaptive badge with initials box
   - Entry in all README styles

## Adding a New Category

1. **Use the interactive tool:**
   ```bash
   make add-category
   # or with arguments:
   make add-category ARGS='--name "My Category" --prefix mycat --icon "🎯"'
   ```

   Note: `make add-category` uses `scripts/categories/add_category.py` (experimental). It rewrites
   `templates/categories.yaml` via PyYAML and updates `.github/ISSUE_TEMPLATE/recommend-resource.yml`,
   so review the diff after running it.

2. **Or manually edit `templates/categories.yaml`:**
   ```yaml
   categories:
     - id: my-category
       name: My Category
       icon: "🎯"
       description: Description of this category
       order: 10
       subcategories:
         - id: general
           name: General
   ```

3. **Run the generator:**
   ```bash
   make generate
   ```

4. **What gets auto-generated:**
   - `assets/header_{category}.svg` - Dark mode category header (CRT style)
   - `assets/header_{category}-light-v3.svg` - Light mode category header
   - `assets/subheader_{subcat}.svg` - Subcategory header (when resources exist)
   - Section in all README styles

5. **Regenerate subcategory TOC SVGs** (if subcategories were added):
   ```bash
   make generate-toc-assets
   ```
   This creates/updates `assets/toc-sub-{subcat}.svg` and `assets/toc-sub-{subcat}-light-anim-scanline.svg` files for all subcategories.

6. **What needs manual creation:**
   - `assets/toc-row-{category}.svg` and `assets/toc-row-{category}-light-anim-scanline.svg` - TOC row assets (category-level)
   - Card assets if using the EXTRA style navigation grid

## Adding a New Subcategory

Subcategories can be added to any category.

1. **Edit `templates/categories.yaml`:**
   ```yaml
   categories:
     - id: tooling
       name: Tooling
       subcategories:
         - id: general
           name: General
         - id: my-new-subcat    # Add new subcategory
           name: My New Subcat
   ```

2. **Regenerate subcategory TOC SVGs:**
   ```bash
   make generate-toc-assets
   ```
   This creates/updates the `toc-sub-*.svg` and `toc-sub-*-light-anim-scanline.svg` files in `assets/` for all subcategories.

3. **Run the generator** - Subcategory headers are auto-generated alongside the README content

## If You Change Category IDs or Names

Update these locations:
1. `templates/categories.yaml` - Category definitions
2. Card-grid anchors in `templates/README_EXTRA.template.md` (they use trailing `-` anchors)
3. Any static assets that embed text (for example, card SVGs)

## Adding a New README Style

1. Create a template file in `templates/` (for example, `README_NEWSTYLE.template.md`)
2. Add a generator class extending `ReadmeGenerator` under `scripts/readme/generators/`
3. Register the class in `STYLE_GENERATORS` in `scripts/readme/generate_readme.py`
4. Create a style selector badge in `assets/badge-style-newstyle.svg`
5. Add the style to `acc-config.yaml`:
   - Add an entry under `styles:` with name, badge, highlight_color, filename
   - Add the style ID to `style_order:`
6. Ensure your template includes `{{STYLE_SELECTOR}}`

## Generator Architecture

The generator uses a class-based architecture with the Template Method pattern.
Generator classes live under `scripts/readme/generators/` and are wired in
`scripts/readme/generate_readme.py`:

```
ReadmeGenerator (ABC)
├── VisualReadmeGenerator      → README_ALTERNATIVES/README_EXTRA.md
├── MinimalReadmeGenerator     → README_ALTERNATIVES/README_CLASSIC.md
├── AwesomeReadmeGenerator     → README_ALTERNATIVES/README_AWESOME.md
└── ParameterizedFlatListGenerator → README_ALTERNATIVES/README_FLAT_*.md (44 files)

The `root_style` also gets an additional copy written to `README.md`.
```

### Category Management

Categories can be managed via `scripts/categories/category_utils.py` (experimental):

```python
from scripts.categories.category_utils import category_manager

# Get all categories
categories = category_manager.get_categories_for_readme()

# Get category by name
cat = category_manager.get_category_by_name("Tooling")
```

### Template Placeholders

Templates use `{{PLACEHOLDER}}` syntax for dynamic content. Key placeholders:

| Placeholder | Description | Generator Method |
|-------------|-------------|------------------|
| `{{ASSET_PATH('file.svg')}}` | Tokenized asset path resolved per output location | `resolve_asset_tokens()` |
| `{{STYLE_SELECTOR}}` | "Pick Your Style" badge row linking to all README variants | `get_style_selector()` |
| `{{REPO_TICKER}}` | Animated SVG ticker showing featured projects | `generate_repo_ticker()` |
| `{{ANNOUNCEMENTS}}` | Latest announcements from `templates/announcements.yaml` | `load_announcements()` |
| `{{WEEKLY_SECTION}}` | Latest additions section | `generate_weekly_section()` |
| `{{TABLE_OF_CONTENTS}}` | Table of contents | `generate_toc()` |
| `{{BODY_SECTIONS}}` | Main resource listings | `generate_section_content()` |
| `{{FOOTER}}` | Footer template content | `load_footer()` |

Template content outside these placeholders is treated as manual copy and is not regenerated.

Asset references use token placeholders (e.g. `{{ASSET_PATH('logo.svg')}}`) that are resolved after templating based on the destination README path. Resolution walks upward to the repo root (`pyproject.toml`) and computes a relative path to `/assets` for each output file.

Generated outputs are prefixed with `<!-- GENERATED FILE: do not edit directly -->` as a reminder that edits belong in templates and source data.

## Repo Ticker System

The repo ticker displays an animated scrolling banner of featured Claude Code projects with live GitHub stats.

### Components

| File | Purpose |
|------|---------|
| `scripts/ticker/fetch_repo_ticker_data.py` | Fetches GitHub stats for tracked repos |
| `scripts/ticker/generate_ticker_svg.py` | Generates animated SVG tickers |
| `data/repo-ticker.csv` | Current repo stats (stars, forks, deltas) |
| `data/repo-ticker-previous.csv` | Previous stats for delta calculation |

### Generated Tickers

| Theme | Output File | Used By |
|-------|-------------|---------|
| Dark (CRT) | `assets/repo-ticker.svg` | Extra style (dark mode) |
| Light (Vintage) | `assets/repo-ticker-light.svg` | Extra style (light mode) |
| Awesome | `assets/repo-ticker-awesome.svg` | Awesome style |

### Ticker Generation

```bash
# Fetch latest repo stats (requires GITHUB_TOKEN)
python scripts/ticker/fetch_repo_ticker_data.py

# Generate ticker SVGs from current data
python scripts/ticker/generate_ticker_svg.py
```

The tickers:
- Sample 10 random repos from the CSV
- Display repo name, owner, stars, and daily delta
- Animate with seamless horizontal scrolling
- Use theme-appropriate styling (CRT glow for dark, muted colors for awesome)

## Asset Types

### Auto-Generated Assets

| Asset | Filename Pattern | Generator Function |
|-------|------------------|-------------------|
| Resource badges | `badge-{name}.svg` | `scripts/readme/svg_templates/badges.py:generate_resource_badge_svg()` |
| Entry separators | `entry-separator-light-animated.svg` | `scripts/readme/svg_templates/dividers.py:generate_entry_separator_svg()` |
| Category headers (dark/light) | `header_{cat}.svg`, `header_{cat}-light-v3.svg` | `scripts/readme/helpers/readme_assets.py:ensure_category_header_exists()` |
| Subcategory headers | `subheader_{subcat}.svg` | `scripts/readme/helpers/readme_assets.py:create_h3_svg_file()` |
| Section dividers (light) | `section-divider-light-manual-v{1,2,3}.svg` | `scripts/readme/svg_templates/dividers.py:generate_section_divider_light_svg()` |
| Desc boxes (light) | `desc-box-{top,bottom}-light.svg` | `scripts/readme/svg_templates/dividers.py:generate_desc_box_light_svg()` |
| Sort badges | `badge-sort-{type}.svg` | `scripts/readme/helpers/readme_assets.py:generate_flat_badges()` |
| Category filter badges | `badge-cat-{slug}.svg` | `scripts/readme/helpers/readme_assets.py:generate_flat_badges()` |
| Repo tickers | `repo-ticker*.svg` | `generate_ticker_svg()` / `generate_awesome_ticker_svg()` |
| Subcategory TOC rows | `toc-sub-{subcat}.svg`, `toc-sub-{subcat}-light-anim-scanline.svg` | `scripts/readme/helpers/readme_assets.py:regenerate_sub_toc_svgs()` via `make generate-toc-assets` |
| Style selector badges | `badge-style-{style}.svg` | Manual |

### Pre-Made Assets (Manual)

| Asset | Purpose |
|-------|---------|
| `section-divider-alt2.svg` | Dark mode section divider |
| `desc-box-{top,bottom}.svg` | Dark mode description boxes |
| `toc-row-*.svg` | Category-level TOC row assets (light variants use `-light-anim-scanline`) |
| `toc-header*.svg` | TOC header assets (light variants use `-light-anim-scanline`) |
| `card-*.svg` | Terminal Navigation grid cards |
| `badge-style-*.svg` | Style selector badges |
| Hero banners, logos | Top-of-README branding |

## Visual Styles

### Light Mode: "Vintage Technical Manual"
- Muted brown/sepia tones (`#5c5247`, `#3d3530`)
- Coral accent (`#c96442`)
- "Layered drafts" effect - doubled lines, ghost shadows
- L-shaped corner brackets
- Tick marks and circle clusters

### Dark Mode: "CRT Terminal"
- Green phosphor colors (`#33ff33`, `#66ff66`)
- Scanline overlay effect
- Subtle glow filter
- Monospace fonts
- Animated flicker effects

## Generator Functions

Key SVG renderers in `scripts/readme/svg_templates/`:

```python
# Badge for each resource entry
generate_resource_badge_svg(display_name, author_name)

# Category section header
generate_category_header_light_svg(title, section_number)

# Horizontal dividers between sections
generate_section_divider_light_svg(variant)  # 1, 2, or 3

# Description box frames
generate_desc_box_light_svg(position)  # "top" or "bottom"

# TOC directory listing rows
generate_toc_row_svg(directory_name, description)
generate_toc_row_light_svg(directory_name, description)
generate_toc_sub_svg(directory_name, description)
```

Key markup helpers in `scripts/readme/markup/`:

```python
# Style selector (dynamically generated)
generate_style_selector(current_style, output_path, repo_root=None)
```

Key asset writers in `scripts/readme/helpers/readme_assets.py`:

```python
# Flat list badges (writes SVGs using scripts/readme/svg_templates/badges.py)
generate_flat_badges(assets_dir, sort_types, categories)

# Regenerate subcategory TOC SVGs for the Visual (Extra) style
regenerate_sub_toc_svgs(categories, assets_dir)
```

Standalone TOC asset script (`scripts/readme/helpers/generate_toc_assets.py`):

```bash
# Regenerate subcategory TOC SVGs from categories.yaml
make generate-toc-assets
# or directly:
python -m scripts.readme.helpers.generate_toc_assets
```

Key functions in `scripts/ticker/generate_ticker_svg.py`:

```python
# Standard ticker (dark/light themes)
generate_ticker_svg(repos, theme="dark")  # or "light"

# Awesome-style ticker (clean, minimal)
generate_awesome_ticker_svg(repos)
```

## Animated Elements

### Entry Separator (`entry-separator-light-animated.svg`)
- Pulsating dots that ripple outward then contract back in
- 3 core dots always visible
- 9 rings of dots animate with staggered timing
- 2.5 second cycle

### TOC Rows
- Subtle opacity flicker on directory names
- Hover highlight pulse animation

## File Structure

This tree is auto-generated from `tools/readme_tree/config.yaml` (update with `make docs-tree`).

<!-- TREE:START -->
```
awesome-claude-code//
├── THE_RESOURCES_TABLE.csv  # Master data file
├── acc-config.yaml  # Root style + selector config
├── README.md  # Generated root README (root_style)
├── README_ALTERNATIVES/  # All generated README variants
│   ├── README_EXTRA.md  # Generated (Extra style, always)
│   ├── README_CLASSIC.md  # Generated (Classic style)
│   ├── README_AWESOME.md  # Generated (Awesome list style)
│   └── README_FLAT_*.md  # Generated (44 flat list views)
├── templates/  # README templates and supporting YAML
│   ├── categories.yaml  # Category definitions
│   ├── announcements.yaml  # Announcements content
│   ├── README_EXTRA.template.md  # Extra style template
│   ├── README_CLASSIC.template.md  # Classic style template
│   ├── README_AWESOME.template.md  # Awesome style template
│   ├── footer.template.md  # Shared footer
│   └── resource-overrides.yaml  # Manual resource overrides
├── scripts/
│   ├── readme/  # README generation pipeline
│   │   ├── generate_readme.py  # Generator entrypoint
│   │   ├── generators/  # README generator classes by style
│   │   │   ├── base.py  # ReadmeGenerator base + shared helpers
│   │   │   ├── visual.py  # Extra (visual) README generator
│   │   │   ├── minimal.py  # Classic README generator
│   │   │   ├── awesome.py  # Awesome list README generator
│   │   │   └── flat.py  # Flat list README generator
│   │   ├── helpers/  # Config/utils/assets helpers for README generation
│   │   │   ├── readme_assets.py
│   │   │   ├── readme_config.py
│   │   │   ├── readme_utils.py
│   │   │   ├── generate_toc_assets.py
│   │   │   └── readme_paths.py
│   │   ├── markup/  # Markdown/HTML renderers by style
│   │   │   ├── awesome.py
│   │   │   ├── flat.py
│   │   │   ├── minimal.py
│   │   │   ├── shared.py
│   │   │   └── visual.py
│   │   └── svg_templates/  # SVG renderers used by the generator
│   │       ├── badges.py
│   │       ├── dividers.py
│   │       ├── headers.py
│   │       └── toc.py
│   ├── ticker/  # Repo ticker generation scripts
│   │   ├── generate_ticker_svg.py  # Repo ticker SVG generator
│   │   └── fetch_repo_ticker_data.py  # GitHub stats fetcher
│   ├── categories/  # Category management scripts
│   │   ├── category_utils.py  # Category management
│   │   └── add_category.py  # Category addition tool
│   └── resources/  # Resource maintenance scripts
│       ├── sort_resources.py  # CSV sorting (used by generator)
│       ├── resource_utils.py  # CSV append + PR content helpers
│       ├── create_resource_pr.py
│       ├── detect_informal_submission.py
│       ├── download_resources.py
│       └── parse_issue_form.py
├── assets/  # SVG badges, headers, dividers
│   ├── badge-*.svg  # Resource badges (auto-generated)
│   ├── header_*.svg  # Category headers
│   ├── section-divider-*.svg  # Section dividers
│   ├── desc-box-*.svg  # Description boxes
│   ├── toc-*.svg  # TOC elements
│   ├── subheader_*.svg  # Subcategory headers
│   ├── badge-sort-*.svg  # Flat list sort badges
│   ├── badge-cat-*.svg  # Flat list category badges
│   ├── badge-style-*.svg  # Style selector badges
│   ├── repo-ticker*.svg  # Animated repo tickers
│   └── entry-separator-*.svg  # Entry separators
├── data/  # Generated ticker data
│   ├── repo-ticker.csv  # Current repository stats
│   └── repo-ticker-previous.csv  # Previous stats (for deltas)
└── docs/
    └── README-GENERATION.md  # This file
```
<!-- TREE:END -->

## Makefile Commands

```bash
make generate            # Generate all READMEs (sorts CSV first)
make generate-toc-assets # Regenerate subcategory TOC SVGs (after adding subcategories)
make add-category        # Interactive category addition
make sort                # Sort resources in CSV
make validate            # Validate all resource links
make docs-tree           # Update README-GENERATION tree block
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | Avoid GitHub API rate limiting during validation |

## Troubleshooting

### Badge not appearing
- Check the resource name doesn't have special characters that break filenames
- Verify the CSV row has all required columns
- Ensure `Active` is set to `TRUE`

### New category not showing
- Ensure category is added to `templates/categories.yaml`
- Check for typos between CSV Category column and categories.yaml name
- Run `make generate` after changes

### Assets look wrong after regeneration
- The `ensure_*_exists()` functions only create files if they don't exist
- To regenerate an asset, delete it first then run the generator
- Or edit the generator template and manually update existing files

### Dark mode assets missing
- Dark mode dividers, TOC header, and card assets are manual
- Use existing dark mode assets as templates

### README style not generating
- Check that the template file exists in `templates/`
- Verify the generator class is registered in `STYLE_GENERATORS` in `scripts/readme/generate_readme.py`

## Path Resolution System

The generator uses a dynamic path resolution system to handle relative paths correctly across different README locations. This section documents the key assumptions and behaviors.

### Core Assumptions

These assumptions are tested in `tests/test_style_selector_paths.py`:

| Assumption | Description |
|------------|-------------|
| **Single root README** | Exactly one style is copied to `README.md` (the `root_style`) |
| **Alternatives path is fixed** | `README_ALTERNATIVES/` is a fixed directory under the repo root |
| **Assets at root** | The `assets/` folder is a direct child of the repo root |
| **Repo root discovery** | Paths resolve from the repo root discovered by finding `pyproject.toml` |
| **Flat entry point** | Flat style links to `README_FLAT_ALL_AZ.md` as its entry point |

### Path Prefix Rules

| Location | Asset Prefix | Link to Root | Link to Alternatives |
|----------|--------------|--------------|----------------------|
| Root (`README.md`) | `assets/` | `./` | `README_ALTERNATIVES/file.md` |
| Alternatives | `../assets/` | `../` | `file.md` (same folder) |

### Key Properties

```python
# In ReadmeGenerator base class:

is_root_style    # True if this style matches config's root_style
resolved_output_path  # Default output path (under README_ALTERNATIVES/)
alternative_output_path  # Path under README_ALTERNATIVES/ for this style
# Root generation uses generate(output_path="README.md")
```

### How Root Style Changes Work

When `acc-config.yaml` changes from `root_style: extra` to `root_style: awesome`:

1. **Awesome README** is also written to `README.md`
   - Asset paths use `assets/`
   - Links to other styles use `README_ALTERNATIVES/file.md`

2. **All alternatives remain in `README_ALTERNATIVES/`**
   - Asset paths remain `../assets/`
   - Style selector links update to reflect the new root

### Breaking Changes to Avoid

These changes would break the path resolution system:

- **Changing `README_ALTERNATIVES/` location**: Output paths and selector targets are hardcoded to `README_ALTERNATIVES/`
- **Renaming `assets/` folder**: All asset path prefixes would break
- **Having multiple root READMEs**: Only one style can be `root_style`
- **Nested alternative folders**: All alternatives must be in the same flat folder
