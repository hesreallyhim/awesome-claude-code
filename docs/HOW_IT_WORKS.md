# How Awesome Claude Code Works

This document provides assorted technical details about the repository structure, automated systems, and processes that power Awesome Claude Code. It's mostly superceded by [README-GENERATION](./README-GENERATION.md), but, for one reason or another, it's still here, for now.

### GitHub Labels

The submission system uses several labels to track issue state:

#### Resource Submission Labels

- **`resource-submission`** - Applied automatically to issues created via the submission form
- **`validation-passed`** - Applied when submission passes all validation checks
- **`validation-failed`** - Applied when submission fails validation
- **`approved`** - Applied when maintainer approves submission with `/approve`
- **`pr-created`** - Applied after PR is successfully created
- **`error-creating-pr`** - Applied if PR creation fails
- **`rejected`** - Applied when maintainer rejects with `/reject`
- **`changes-requested`** - Applied when maintainer requests changes with `/request-changes`

#### Other Labels

- **`broken-links`** - Applied by scheduled link validation when resources become unavailable
- **`automated`** - Applied alongside `broken-links` to indicate automated detection
- **`do-not-disturb`** - Apply to a resource PR before merging to skip the badge notification to the resource author's repository

#### Label State Transitions

1. New submission → `resource-submission`
2. After validation → adds `validation-passed` OR `validation-failed`
3. If changes requested → adds `changes-requested`
4. When user edits and validation passes → removes `changes-requested`
5. On approval → adds `approved` + `pr-created` (or `error-creating-pr`)
6. On rejection → adds `rejected`

## The Submission Flow

### 1. User Submits Issue

When a user submits a resource via the issue form:

```yaml
# .github/ISSUE_TEMPLATE/submit-resource.yml
- Structured form with all required fields
- Auto-labels with "resource-submission"
- Validates input formats
```

### 2. Automated Validation

The validation workflow triggers immediately:

```python
# Simplified validation flow
1. Parse issue body → extract form data
2. Validate required fields
3. Check URL accessibility
4. Verify no duplicates exist
5. Post results as comment
6. Update issue labels
```

**Validation includes:**
- URL validation (200 OK response)
- License detection from GitHub API
- Duplicate checking against existing CSV
- Field format validation

### 3. Maintainer Review

Once validation passes, maintainers can:

- `/approve` - Triggers PR creation
- `/request-changes [reason]` - Asks for modifications
- `/reject [reason]` - Closes the submission

**Notification System:**
- When changes are requested, the maintainer is @-mentioned in the comment
- When the user edits their issue, the maintainer receives a notification if:
  - It's the first edit after requesting changes
  - The validation status changes (pass→fail or fail→pass)
- Multiple rapid edits won't spam the maintainer with notifications

### 4. Automated PR Creation

Upon approval:

```bash
1. Checkout fresh main branch
2. Create unique branch: add-resource/category/name-timestamp
3. Add resource to CSV with generated ID
4. Run generate_readme.py
5. Commit changes
6. Push branch
7. Create PR via GitHub CLI
8. Link back to original issue
9. Close submission issue
```

### 5. Final Steps

- Maintainer merges PR
- Badge notification system runs (if enabled)
- Submitter receives GitHub notifications

## Resource ID Generation

IDs follow the format: `{prefix}-{hash}`

```python
prefixes = {
    "Agent Skills": "skill",
    "Slash-Commands": "cmd",
    "Workflows & Knowledge Guides": "wf",
    "Tooling": "tool",
    "CLAUDE.md Files": "claude",
    "Hooks": "hook",
    "Official Documentation": "doc",
}

# Hash is first 8 chars of SHA256(display_name + primary_link)
```

### Collapsible Sections

The generated README uses HTML `<details>` elements for improved navigation:
- **Categories without subcategories**: Wrapped in `<details open>` (fully collapsible)
- **Categories with subcategories**: Regular headers (subcategories are collapsible)
- **All subcategories**: Wrapped in `<details open>` elements
- **Table of Contents**: Collapsible with nested sections for categories with subcategories
- All collapsible sections are open by default for easy browsing

**Design Note**: Initially attempted to make all categories collapsible with nested subcategories, but this caused anchor link navigation issues - links from the Table of Contents couldn't reach subcategories when their parent category was collapsed. The current design balances navigation functionality with collapsibility.

### GitHub Stats Integration

Each GitHub resource in the README automatically includes a collapsible statistics section:
- **Automatic Detection**: The `parse_github_url` function from `validate_links.py` identifies GitHub repositories
- **Stats Display**: Uses the GitHub Stats API to generate an SVG badge with repository metrics
- **Collapsible Design**: Stats are hidden by default in a `<details>` element to keep the main list clean
- **Universal Support**: Works with all GitHub URL formats (repository root, blob URLs, tree URLs, etc.)

Example output for a GitHub resource:
```markdown
[`resource-name`](https://github.com/owner/repo)
Description of the resource

<details>
<summary>📊 GitHub Stats</summary>
<br>

![GitHub Stats for repo](https://github-readme-stats-plus-theta.vercel.app/api/pin/?repo=repo&username=owner&all_stats=true&stats_only=true)

</details>
```

## Alternative README Views

The repository offers multiple README styles to suit different preferences, all generated from the same CSV source of truth.

### Style Options

Users can switch between four presentation styles via navigation badges at the top of each page:

| Style | Description | Location |
|-------|-------------|----------|
| **Extra** | Visual/themed with SVG assets, collapsible sections, GitHub stats | `README_ALTERNATIVES/README_EXTRA.md` (and `README.md` when `root_style: extra`) |
| **Classic** | Clean markdown, minimal styling, traditional awesome-list format | `README_ALTERNATIVES/README_CLASSIC.md` (and `README.md` when `root_style: classic`) |
| **Awesome** | Clean awesome-list style with minimal embellishment | `README_ALTERNATIVES/README_AWESOME.md` (and `README.md` when `root_style: awesome`) |
| **Flat** | Sortable/filterable table view with category filters | `README_ALTERNATIVES/README_FLAT_*.md` (and `README.md` when `root_style: flat`) |

### File Structure

Alternative views are in the `README_ALTERNATIVES/` folder to keep the root clean:

```
README.md                                      # Root README (root_style)
README_ALTERNATIVES/
├── README_EXTRA.md                            # Extra visual view
├── README_CLASSIC.md                          # Classic markdown view
├── README_AWESOME.md                          # Awesome list view
├── README_FLAT_ALL_AZ.md                      # Flat: All resources, A-Z
├── README_FLAT_ALL_UPDATED.md                 # Flat: All resources, by updated
├── README_FLAT_ALL_CREATED.md                 # Flat: All resources, by created
├── README_FLAT_ALL_RELEASES.md                # Flat: All resources, recent releases
├── README_FLAT_TOOLING_AZ.md                  # Flat: Tooling only, A-Z
├── README_FLAT_HOOKS_UPDATED.md               # Flat: Hooks only, by updated
└── ... (44 flat views total: 11 categories × 4 sort types)
```

### Flat List System

The flat view provides a searchable table with dual navigation:

#### Sort Options
- **A-Z** - Alphabetical by resource name
- **Updated** - By last modified date (most recent first)
- **Created** - By repository creation date (newest first)
- **Releases** - Resources with releases in past 30 days

#### Category Filters
- **All** - All 164+ resources
- **Tooling**, **Commands**, **CLAUDE.md**, **Workflows**, **Hooks**, **Skills**, **Styles**, **Status**, **Docs**, **Clients**

#### Table Format
Resources are displayed with stacked name/author format to maximize description space:

```markdown
| Resource | Category | Sub-Category | Description |
|----------|----------|--------------|-------------|
| [**Resource Name**](link)<br>by [Author](link) | Category | Sub-Cat | Full description... |
```

### Release Detection

The "Releases" sort option shows resources with published releases in the past 30 days. Release information is fetched from GitHub Releases only.

### Generator Architecture

The `generate_readme.py` script uses generator classes under `scripts/readme/generators/`:

```python
ReadmeGenerator (ABC)
├── VisualReadmeGenerator            # README_ALTERNATIVES/README_EXTRA.md
├── MinimalReadmeGenerator           # README_ALTERNATIVES/README_CLASSIC.md
├── AwesomeReadmeGenerator           # README_ALTERNATIVES/README_AWESOME.md
└── ParameterizedFlatListGenerator   # README_ALTERNATIVES/README_FLAT_*.md
```

The `ParameterizedFlatListGenerator` takes `category_slug` and `sort_type` parameters, enabling generation of all 44 combinations from a single class. The configured `root_style` is additionally generated as `README.md`.

### Navigation Badges

SVG badges are generated dynamically in `assets/`:
- `badge-style-*.svg` - Style selector (Extra, Classic, Awesome, Flat)
- `badge-sort-*.svg` - Sort options (A-Z, Updated, Created, Releases)
- `badge-cat-*.svg` - Category filters (All, Tooling, Hooks, etc.)

Current selections are highlighted with colored borders matching each badge's theme color.

### Adding/Removing Flat List Categories

To add a new category filter to flat list views:

1. **Update `FLAT_CATEGORIES`** in `scripts/readme/generators/flat.py`:
   ```python
   FLAT_CATEGORIES = {
       # ... existing categories ...
       "new-category": ("CSV Category Value", "Display Name", "#hexcolor"),
   }
   ```
   - First value: Exact match for the `Category` column in CSV (or `None` for "all")
   - Second value: Display name shown on badge
   - Third value: Hex color for badge accent and selection border

2. **Regenerate READMEs**: Run `python scripts/readme/generate_readme.py`
   - Creates new files: `README_ALTERNATIVES/README_FLAT_NEWCATEGORY_*.md`
   - Generates badge: `assets/badge-cat-new-category.svg`
   - Updates navigation in all 44+ flat views

To remove a category: Delete its entry from `FLAT_CATEGORIES` and run the generator. Manually delete the orphaned `.md` files from `README_ALTERNATIVES/`.

### Adding/Removing Sort Types

To add a new sort option:

1. **Update `FLAT_SORT_TYPES`** in `scripts/readme/generators/flat.py`:
   ```python
   FLAT_SORT_TYPES = {
       # ... existing sorts ...
       "newsort": ("DISPLAY", "#hexcolor", "description for status text"),
   }
   ```

2. **Implement sorting logic** in `ParameterizedFlatListGenerator.sort_resources()`:
   ```python
   elif self.sort_type == "newsort":
       # Custom sorting logic
       return sorted(resources, key=lambda x: ...)
   ```

3. **Regenerate READMEs**: Creates new views for all categories × new sort type.

### Adding/Removing README Styles

The main README styles are defined as generator classes:

| Style | Generator Class | Template | Output |
|-------|----------------|----------|--------|
| Extra | `VisualReadmeGenerator` | `README_EXTRA.template.md` | `README_ALTERNATIVES/README_EXTRA.md` |
| Classic | `MinimalReadmeGenerator` | `README_CLASSIC.template.md` | `README_ALTERNATIVES/README_CLASSIC.md` |
| Awesome | `AwesomeReadmeGenerator` | `README_AWESOME.template.md` | `README_ALTERNATIVES/README_AWESOME.md` |
| Flat | `ParameterizedFlatListGenerator` | (built-in) | `README_ALTERNATIVES/README_FLAT_*.md` |

The configured `root_style` is additionally written to `README.md`.

**To add a new README style:**

1. **Create a generator class** extending `ReadmeGenerator` under `scripts/readme/generators/`:
   ```python
   class NewStyleReadmeGenerator(ReadmeGenerator):
       @property
       def template_filename(self) -> str:
           return "README_NEWSTYLE.template.md"

       @property
       def output_filename(self) -> str:
           return "README_ALTERNATIVES/README_NEWSTYLE.md"

       # Implement abstract methods...
   ```

2. **Create template** in `templates/README_NEWSTYLE.template.md` (include `{{STYLE_SELECTOR}}`).

3. **Register the generator** in `STYLE_GENERATORS` inside `scripts/readme/generate_readme.py`.

4. **Create style badge** `assets/badge-style-newstyle.svg`.

5. **Update config** in `acc-config.yaml`:
   - add a new entry under `styles:`
   - append the style ID to `style_order:`

**To remove a style:** Delete the generator class, template, badge asset, and config entry, then remove the style from `STYLE_GENERATORS` and `style_order`.

### Announcements System

Announcements are stored in `templates/announcements.yaml`:
- YAML format for structured data
- Renders as nested collapsible sections
- Each date group is collapsible
- Individual items can be simple text or collapsible with summary/text
- Falls back to `.md` file if YAML doesn't exist
