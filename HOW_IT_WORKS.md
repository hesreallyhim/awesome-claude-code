# How Awesome Claude Code Works

This document provides technical details about the repository structure, automated systems, and processes that power Awesome Claude Code.

## Repository Architecture

### Core Files

- **`THE_RESOURCES_TABLE.csv`** - The single source of truth for all resources
- **`README.md`** - Generated automatically from the CSV and templates
- **`templates/`** - Contains templates for README generation
  - `README.template.md` - Main template structure
  - `categories.yaml` - Single source of truth for all categories
  - `resource-overrides.yaml` - Manual overrides for specific resources

### Scripts Directory

The `scripts/` directory contains all automation:

- **`parse_issue_form.py`** - Parses GitHub issue form submissions
- **`create_resource_pr.py`** - Creates PRs from approved submissions
- **`generate_readme.py`** - Generates README from CSV data
- **`validate_single_resource.py`** - Validates individual resources
- **`validate_links.py`** - Bulk validation of all resources
- **`badge_issue_notification.py`** - Creates notification issues on featured repos
- **`quick_id.py`** - Generates unique resource IDs

### GitHub Actions Workflows

Located in `.github/workflows/`:

- **`validate-resource-submission.yml`** - Runs on issue creation/edit
- **`approve-resource-submission.yml`** - Runs on maintainer commands
- **`protect-labels.yml`** - Prevents unauthorized label changes
- **`validate-links.yml`** - Scheduled validation of all resource links
- **Additional workflows for CI/CD and maintenance**

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

#### Label Protection

All submission-related labels are protected from unauthorized changes. The `protect-labels.yml` workflow automatically reverts any label changes made by non-maintainers (users without OWNER, MEMBER, or COLLABORATOR permissions).

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

## CSV Structure

| Field | Description | Required | Auto-populated |
|-------|-------------|----------|----------------|
| ID | Unique identifier | Yes | Yes |
| Display Name | Resource name | Yes | No |
| Category | Main category | Yes | No |
| Sub-Category | Optional subcategory | No | No |
| Primary Link | Main URL | Yes | No |
| Secondary Link | Additional URL | No | No |
| Author Name | Creator name | Yes | No |
| Author Link | Creator profile | Yes | No |
| Active | TRUE/FALSE status | Yes | Yes (via validation) |
| Date Added | Addition date | No | Yes |
| Last Modified | GitHub last commit | No | Yes (from API) |
| Last Checked | Validation timestamp | Yes | Yes |
| License | SPDX identifier | Recommended | Yes (from GitHub) |
| Description | Brief description | Yes | No |

## README Generation

The README is generated from templates using:

```yaml
# templates/categories.yaml
categories:
  - id: workflows
    name: "Workflows & Knowledge Guides"
    prefix: wf
    icon: "🧠"
    order: 1
    
  - id: statusline
    name: "Status Lines"
    prefix: status
    icon: "📊"
    order: 3
```

Generation process:
1. Load CSV data
2. Apply any overrides from `resource-overrides.yaml`
3. Group by category/subcategory
4. Format using templates
5. Write final README

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
- **API Endpoint**: `https://github-readme-stats-plus-theta.vercel.app/api/pin/?repo=REPO&username=USER&all_stats=true&stats_only=true`

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

Users can switch between three presentation styles via navigation badges at the top of each page:

| Style | Description | Location |
|-------|-------------|----------|
| **Extra** | Visual/themed with SVG assets, collapsible sections, GitHub stats | `README.md` (root) |
| **Classic** | Clean markdown, minimal styling, traditional awesome-list format | `README_ALTERNATIVES/README_CLASSIC.md` |
| **Flat** | Sortable/filterable table view with category filters | `README_ALTERNATIVES/README_FLAT_*.md` |

### File Structure

Alternative views are in the `README_ALTERNATIVES/` folder to keep the root clean:

```
README.md                                      # Main "Extra" view (root)
README_ALTERNATIVES/
├── README_CLASSIC.md                          # Classic markdown view
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

The "Releases" sort option shows resources with published releases in the past 30 days. Release information is fetched from multiple sources in priority order:

1. **GitHub Releases** - Official release tags
2. **GitHub Tags** - Fallback if no releases
3. **npm Registry** - For JavaScript packages
4. **PyPI** - For Python packages
5. **crates.io** - For Rust packages
6. **Homebrew** - For Homebrew formulas
7. **README parsing** - Last resort version extraction

Release data is stored in the CSV with columns:
- `Latest Release` - Timestamp of the release
- `Release Version` - Version string
- `Release Source` - Which registry/method detected it

A disclaimer appears on all release views noting the best-effort nature of detection.

### Generator Architecture

The `generate_readme.py` script uses a class hierarchy for different README styles:

```python
ReadmeGenerator (ABC)
├── VisualReadmeGenerator        # README.md (Extra)
├── MinimalReadmeGenerator       # README_CLASSIC
└── ParameterizedFlatListGenerator  # All flat views (parameterized by category + sort)
```

The `ParameterizedFlatListGenerator` takes `category_slug` and `sort_type` parameters, enabling generation of all 44 combinations from a single class.

### Navigation Badges

SVG badges are generated dynamically in `assets/`:
- `badge-style-*.svg` - Style selector (Extra, Classic, Flat)
- `badge-sort-*.svg` - Sort options (A-Z, Updated, Created, Releases)
- `badge-cat-*.svg` - Category filters (All, Tooling, Hooks, etc.)

Current selections are highlighted with colored borders matching each badge's theme color.

### Adding/Removing Flat List Categories

To add a new category filter to flat list views:

1. **Update `FLAT_CATEGORIES`** in `scripts/generate_readme.py`:
   ```python
   FLAT_CATEGORIES = {
       # ... existing categories ...
       "new-category": ("CSV Category Value", "Display Name", "#hexcolor"),
   }
   ```
   - First value: Exact match for the `Category` column in CSV (or `None` for "all")
   - Second value: Display name shown on badge
   - Third value: Hex color for badge accent and selection border

2. **Regenerate READMEs**: Run `python scripts/generate_readme.py`
   - Creates new files: `README_ALTERNATIVES/README_FLAT_NEWCATEGORY_*.md`
   - Generates badge: `assets/badge-cat-new-category.svg`
   - Updates navigation in all 44+ flat views

To remove a category: Delete its entry from `FLAT_CATEGORIES` and run the generator. Manually delete the orphaned `.md` files from `README_ALTERNATIVES/`.

### Adding/Removing Sort Types

To add a new sort option:

1. **Update `FLAT_SORT_TYPES`** in `scripts/generate_readme.py`:
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
| Extra | `VisualReadmeGenerator` | `README.template.md` | `README.md` |
| Classic | `MinimalReadmeGenerator` | `README_CLASSIC.template.md` | `README_ALTERNATIVES/README_CLASSIC.md` |
| Flat | `ParameterizedFlatListGenerator` | (built-in) | `README_ALTERNATIVES/README_FLAT_*.md` |

**To add a new README style:**

1. **Create a generator class** extending `ReadmeGenerator`:
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

2. **Create template** in `templates/README_NEWSTYLE.template.md`

3. **Add to `main()`** in `generate_readme.py`:
   ```python
   # Generate new style
   generator = NewStyleReadmeGenerator(csv_path, template_dir, assets_dir, repo_root)
   resource_count, backup = generator.generate()
   ```

4. **Create style badge** `assets/badge-style-newstyle.svg`

5. **Update navigation** in all templates to include the new style option

**To remove a style:** Delete the generator class, template, and `main()` call. Update navigation in remaining templates.

### Announcements System

Announcements are stored in `templates/announcements.yaml`:
- YAML format for structured data
- Renders as nested collapsible sections
- Each date group is collapsible
- Individual items can be simple text or collapsible with summary/text
- Falls back to `.md` file if YAML doesn't exist

## Validation System

### Link Validation

- Checks HTTP status (200-299 = valid)
- Handles redirects
- Respects rate limits
- Caches results for efficiency

### GitHub-Specific Features

For GitHub links:
- Fetches repository metadata
- Extracts license information
- Gets last commit date
- Checks if repository exists/is public

### Override System

The `templates/resource-overrides.yaml` allows:
- Locking specific fields from updates
- Skipping validation for special cases
- Manual corrections to auto-detected data

## Security Considerations

1. **Input Validation** - All user input is sanitized
2. **URL Validation** - Only HTTPS URLs accepted
3. **GitHub Token Scoping** - Minimal permissions required
4. **Review Process** - Human review before code changes
5. **Automated Checks** - No direct CSV manipulation by users

## Environment Variables

- `GITHUB_TOKEN` - For API access (provided by Actions)
- `AWESOME_CC_PAT_PUBLIC_REPO` - For creating notification issues
- `CREATE_ISSUES` - Enable/disable notification system

## Local Development

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Test validation
python scripts/validate_single_resource.py "https://example.com"

# Generate README
python scripts/generate_readme.py

# Parse a test issue
ISSUE_BODY="..." python scripts/parse_issue_form.py --validate
```

## Adding New Categories

Repository maintainers can add new categories using the automated tool:

### Interactive Mode
```bash
make add-category
```

This will prompt you for:
- Category name
- ID and prefix
- Icon emoji
- Description
- Order position
- Subcategories

### Command Line Mode
```bash
make add-category ARGS='--name "My Category" --prefix "mycat" --icon "🎯"'
```

### What It Does
The `add-category` command automatically:
1. Updates `templates/categories.yaml` with the new category
2. Updates the GitHub issue template dropdown
3. Regenerates the README with the new section
4. Optionally creates a commit with all changes

### Examples
```bash
# Add a simple category with defaults
make add-category ARGS='--name "Extensions" --prefix "ext" --icon "🧩"'

# Add a category with multiple subcategories
make add-category ARGS='--name "Integrations" --prefix "int" --icon "🔗" --subcategories "API,Webhooks,Plugins"'

# Add a category at a specific position
make add-category ARGS='--name "Templates" --prefix "tmpl" --icon "📋" --order 5'
```

## Maintenance Tasks

### Regular Tasks

- Monitor validation failures
- Update templates as needed
- Review and merge PRs
- Handle edge cases with overrides

### Bulk Operations

```bash
# Validate all links
make validate

# Sort resources
make sort

# Regenerate README
make generate
```

## Contributing to the System

To improve the automation:

1. Test changes locally first
2. Update relevant documentation
3. Consider backward compatibility
4. Add tests if applicable
5. Submit PR with clear description

---

For questions about the technical implementation, please open an issue with the "enhancement" label.
