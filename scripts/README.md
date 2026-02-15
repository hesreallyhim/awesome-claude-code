# Scripts Directory

This directory contains all automation scripts for managing the Awesome Claude Code repository. The scripts work together to provide a complete workflow for resource management, from addition to pull request submission.

**Important Note**: While the primary submission workflow has moved to GitHub Issues for better user experience, we maintain these manual scripts for several critical purposes:
- **Backup submission method** when the automated Issues workflow is unavailable
- **Administrative tasks** requiring direct CSV manipulation
- **Testing and debugging** the automation pipeline
- **Emergency recovery** when automated systems fail


## Overview

The scripts implement a CSV-first workflow where `THE_RESOURCES_TABLE.csv` serves as the single source of truth for all resources. The README.md is generated from this CSV data using templates.

## Repo Root Resolution

Scripts should never assume the current working directory or rely on fragile parent traversal. Use repo-root discovery (walk up to `pyproject.toml`) and resolve paths from there. File paths should be built from `REPO_ROOT` (e.g., `REPO_ROOT / "THE_RESOURCES_TABLE.csv"`).

```python
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
```

### Imports and working directory

Most scripts import modules as `scripts.*`. Those imports resolve reliably when:
- you run from the repo root (default for local usage and GitHub Actions), or
- you set `PYTHONPATH` to the repo root, or
- you use `python -m` with the package path.

If a script fails with `ModuleNotFoundError: scripts`, run it from the repo root or set `PYTHONPATH`.

### Running scripts with `python -m`

When invoking scripts, prefer module paths (dot notation) and omit the `.py` suffix:

```bash
python -m scripts.readme.generate_readme
python -m scripts.validation.validate_links
```

This only works for modules with a CLI entrypoint (`if __name__ == "__main__":`).

## Directory Structure

- `badges/` - Badge notification automation (core + manual)
- `categories/` - Category tooling and config helpers
- `graphics/` - Logo and branding SVG generation
- `ids/` - Resource ID generation utilities
- `maintenance/` - Repo chores and maintenance scripts
- `testing/` - Test and integration utilities (including `test_regenerate_cycle.py`)
- `archive/` - Temporary holding area for deprecated scripts
- `readme/` - README generation pipeline, generators, helpers, markup, SVG templates
- `resources/` - Resource submission, sorting, and CSV utilities
- `ticker/` - Repo ticker data fetch + SVG generation
- `utils/` - Shared git helpers
- `validation/` - URL and submission validation scripts

## Category System

### `categories/category_utils.py`
**Purpose**: Unified category management system  
**Usage**: `from scripts.categories.category_utils import category_manager`  
**Features**:
- Singleton pattern for efficient data loading
- Reads categories from `templates/categories.yaml`
- Provides methods for category lookup, validation, and ordering
- Used by all scripts that need category information

### Adding New Categories
To add a new category:
1. Edit `templates/categories.yaml` and add your category with:
   - `id`: Unique identifier
   - `name`: Display name
   - `prefix`: ID prefix (e.g., "cmd" for Slash-Commands)
   - `icon`: Emoji icon
   - `order`: Sort order
   - `description`: Markdown description
   - `subcategories`: Optional list of subcategories
2. Update `.github/ISSUE_TEMPLATE/recommend-resource.yml` to add the category to the dropdown
3. If subcategories were added, run `make generate-toc-assets` to create subcategory TOC SVGs
4. Run `make generate` to update the README

All scripts automatically use the new category without any code changes.

## Automated Backend Scripts

These scripts power the GitHub Issues-based submission workflow and are executed automatically by GitHub Actions:

### `resources/parse_issue_form.py`
**Purpose**: Parses GitHub issue form submissions and extracts resource data
**Usage**: Called by `validate-resource-submission.yml` workflow
**Features**:
- Extracts structured data from issue body
- Validates form field completeness
- Converts form data to resource format
- Provides validation feedback as issue comments

### `resources/create_resource_pr.py`
**Purpose**: Creates pull requests from approved resource submissions
**Usage**: Called by `approve-resource-submission.yml` workflow
**Features**:
- Generates unique resource IDs
- Adds resources to CSV database
- Creates feature branches automatically
- Opens PR with proper linking to original issue
- Handles pre-commit hooks gracefully

## Core Workflow Scripts (Manual/Admin Use)

### 1. `resources/resource_utils.py`
**Purpose**: CSV append helpers and PR content generation  
**Usage**: Imported by `resources/create_resource_pr.py`  
**Notes**:
- Keeps CSV writes aligned to header order
- Generates standardized PR content for automated submissions

### 2. `readme/generate_readme.py`
**Purpose**: Generates multiple README styles from CSV data using templates
**Usage**: `make generate`
**Features**:
- Template-based generation from `templates/README_EXTRA.template.md` (and other templates)
- Configurable root style via `acc-config.yaml`
- Dynamic style selector and repo ticker via placeholders
- Hierarchical table of contents generation
- Preserves custom sections from template
- Automatic backup before generation
- **GitHub Stats Integration**: Automatically adds collapsible repository statistics for GitHub resources
  - Displays stars, forks, issues, and other metrics via GitHub Stats API
  - Uses disclosure elements (`<details>`) to keep the main list clean
  - Works with all GitHub URL formats (repository root, blob URLs, etc.)

#### Collapsible Sections
The generated README uses collapsible `<details>` elements for better navigation:
- **Categories WITHOUT subcategories**: Wrapped in `<details open>` (fully collapsible)
- **Categories WITH subcategories**: Use regular headers (subcategories are collapsible)
- **All subcategories**: Wrapped in `<details open>` elements
- **Table of Contents**: Main wrapper and nested categories use `<details open>`

**Note on anchor links**: Initially, all categories were made collapsible, but this caused issues with anchor links from the Table of Contents - links couldn't navigate to subcategories when their parent category was collapsed. The current design balances navigation and collapsibility.

### 2a. `readme/helpers/generate_toc_assets.py`
**Purpose**: Regenerates subcategory TOC SVG assets from `templates/categories.yaml`
**Usage**: `make generate-toc-assets`
**Features**:
- Creates/updates `toc-sub-*.svg` and `toc-sub-*-light-anim-scanline.svg` files in `assets/`
- Uses `regenerate_sub_toc_svgs()` from `readme_assets.py` with categories from `category_manager`
- Should be run after adding or modifying subcategories in `templates/categories.yaml`
- SVGs are used by the Visual (Extra) README style for subcategory TOC rows

### 2b. `ticker/generate_ticker_svg.py`
**Purpose**: Generates animated SVG tickers showing featured projects
**Usage**: `python scripts/ticker/generate_ticker_svg.py`
**Features**:
- Reads repo stats from `data/repo-ticker.csv`
- Generates three ticker themes: dark (CRT), light (vintage), awesome (minimal)
- Displays repo name, owner, stars, and daily delta
- Seamless horizontal scrolling animation

### 2c. `ticker/fetch_repo_ticker_data.py`
**Purpose**: Fetches GitHub statistics for repos tracked in the ticker
**Usage**: `python scripts/ticker/fetch_repo_ticker_data.py`
**Features**:
- Queries GitHub API for stars, forks, watchers
- Calculates deltas from previous run
- Outputs to `data/repo-ticker.csv`
- Requires `GITHUB_TOKEN` environment variable

### 4. `validation/validate_links.py`
**Purpose**: Validates all URLs in the CSV database  
**Usage**: `make validate`  
**Features**:
- Batch URL validation with progress bar
- GitHub API integration for repository checks
- License detection from GitHub repos
- Last modified date fetching
- Exponential backoff for rate limiting
- Override support from `.templates/resource-overrides.yaml`
- JSON output for CI/CD integration

### 5. `resources/download_resources.py`
**Purpose**: Downloads resources from GitHub repositories  
**Usage**: `make download-resources`  
**Features**:
- Downloads files from GitHub repositories
- Respects license restrictions
- Category and license filtering
- Rate limiting support
- Progress tracking
- Creates organized directory structure

## Helper Modules

### 6. `utils/git_utils.py`
**Purpose**: Git and GitHub utility functions  
**Interface**:
- `get_github_username()`: Retrieves GitHub username
- `get_current_branch()`: Gets active git branch
- `create_branch()`: Creates new git branch
- `commit_changes()`: Commits with message
- `push_to_remote()`: Pushes branch to remote
- GitHub CLI integration utilities

### 7. `utils/github_utils.py`
**Purpose**: Shared GitHub API helpers  
**Interface**:
- `parse_github_url()`: Parse GitHub URLs into API endpoints
- `get_github_client()`: Pygithub client with request pacing
- `github_request_json()`: JSON requests via PyGithub requester

### 8. `validation/validate_single_resource.py`
**Purpose**: Validates individual resources  
**Usage**: `make validate-single URL=...`  
**Interface**:
- `validate_single_resource()`: Validates URL and fetches metadata using kwargs
- Used by issue submission validation and manual validation workflows
- Supports both regular URLs and GitHub repositories

### 9. `resources/sort_resources.py`
**Purpose**: Sorts CSV entries by category hierarchy  
**Usage**: `make sort` (called automatically by `make generate`)  
**Features**:
- Maintains consistent ordering
- Sorts by: Category → Sub-Category → Display Name
- Uses category order from `categories.yaml`
- Preserves CSV structure and formatting

## Utility Scripts

### 10. `ids/generate_resource_id.py`
**Purpose**: Interactive resource ID generator  
**Usage**: `python scripts/ids/generate_resource_id.py`  
**Features**:
- Interactive prompts for display name, link, and category
- Shows all available categories from `categories.yaml`
- Displays generated ID and CSV row preview

### 11. `ids/resource_id.py`
**Purpose**: Shared resource ID generation module  
**Usage**: `from resource_id import generate_resource_id`  
**Features**:
- Central function used by all ID generation scripts
- Uses category prefixes from `categories.yaml`
- Ensures consistent ID generation across the project

### 12. `badges/badge_notification_core.py`
**Purpose**: Core functionality for badge notification system
**Usage**: `from scripts.badges.badge_notification_core import BadgeNotificationCore`
**Features**:
- Shared notification logic used by other badge scripts
- Input validation and sanitization
- GitHub API interaction utilities
- Template rendering for notification messages

### 13. `badges/badge_notification.py`
**Purpose**: Action-only notifier for merged resource PRs  
**Usage**: Used by `notify-on-merge.yml` (not intended for manual execution)  
**Features**:
- Sends a single notification issue to the resource repository
- Uses `badge_notification_core.py` for shared logic

### 14. `graphics/generate_logo_svgs.py`
**Purpose**: Generates SVG logos for the repository
**Usage**: `python -m scripts.graphics.generate_logo_svgs`
**Features**:
- Creates consistent branding assets
- Generates light/dark logo variants
- Supports dark/light mode variants
- Used for README badges and documentation

## Workflow Integration

### Primary Workflow (GitHub Issues)

**For Users**: Recommend resources through the GitHub Issue form at `.github/ISSUE_TEMPLATE/recommend-resource.yml`
1. User fills out the issue form
2. `validate-resource-submission.yml` workflow validates the submission automatically
3. Maintainer reviews and uses `/approve` command
4. `approve-resource-submission.yml` workflow creates the PR automatically

### Manual Backup Workflows (Make Commands)

These commands remain available for maintainers and emergency situations:

#### Adding a Resource Manually
```bash
make generate         # Regenerate README
make validate         # Validate all links
```

### Maintenance Tasks
```bash
make sort                # Sort CSV entries
make validate            # Check all links
make download-resources  # Archive resources
make generate-toc-assets # Regenerate subcategory TOC SVGs (after adding subcategories)
```

## Configuration

Scripts respect these configuration files:
- `.templates/resource-overrides.yaml`: Manual overrides for resources
- `.env`: Environment variables (not tracked in git)

## Environment Variables

- `GITHUB_TOKEN`: For API rate limiting (optional but recommended)
- `AWESOME_CC_PAT_PUBLIC_REPO`: For badge notifications
- `AWESOME_CC_FORK_REMOTE`: Git remote name for fork (default: origin)
- `AWESOME_CC_UPSTREAM_REMOTE`: Git remote name for upstream (default: upstream)

## Development Notes

1. All scripts include comprehensive error handling
2. Progress bars and user feedback for long operations
3. Backup creation before destructive operations
4. Consistent use of pathlib for cross-platform compatibility
5. Type hints and docstrings throughout
6. Scripts can be run standalone or through Make targets

### Naming Conventions

**Status Lines category** (2025-09-16): The "Statusline" category was renamed to "Status Lines" (title case, plural) for consistency with other categories like "Hooks". This change was made throughout:
- Category name: "Status Lines" (was "Statusline" or "Status line")
- The `id` remains `statusline` to preserve backward compatibility
- CSV entries updated to use "Status Lines" as the category value
- All display text uses the title case plural form "Status Lines"

This ensures consistent title case and pluralization across categories. If issues arise with status line resources, verify that the category name matches "Status Lines" in CSV entries.

### Announcements System

**YAML Format** (2025-09-17): Announcements migrated from Markdown to YAML format for better structure and rendering:

**File**: `templates/announcements.yaml`

**Structure**:
```yaml
- date: "YYYY-MM-DD"
  title: "Announcement Title"  # Optional
  items:
    - "Simple text item"
    - summary: "Collapsible item"
      text: "Detailed description that can be expanded"
```

**Features**:
- Automatically renders as nested collapsible sections in README
- Each date group is collapsible
- Individual items can be simple text or collapsible with summary/text
- Supports multi-line text in detailed descriptions
- Falls back to `.md` file if YAML doesn't exist for backward compatibility

## Future Considerations

- Additional validation rules could be added
- More sophisticated duplicate detection
