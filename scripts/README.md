# Scripts Directory

This directory contains all automation scripts for managing the Awesome Claude Code repository. The scripts work together to provide a complete workflow for resource management, from addition to pull request submission.

**Important Note**: While the primary submission workflow has moved to GitHub Issues for better user experience, we maintain these manual scripts for several critical purposes:
- **Backup submission method** when the automated Issues workflow is unavailable
- **Administrative tasks** requiring direct CSV manipulation
- **Testing and debugging** the automation pipeline
- **Emergency recovery** when automated systems fail

The scripts below fall into two categories:
- **Automated Backend Scripts**: Used by GitHub Actions to process issue submissions (`parse_issue_form.py`, `create_resource_pr.py`)
- **Manual Admin Scripts**: Available for maintainer use and backup purposes (`add_resource.py`, `submit_resource.py`)

## Overview

The scripts implement a CSV-first workflow where `THE_RESOURCES_TABLE.csv` serves as the single source of truth for all resources. The README.md is generated from this CSV data using templates.

## Category System

### `category_utils.py`
**Purpose**: Unified category management system  
**Usage**: `from category_utils import category_manager`  
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
2. Update `.github/ISSUE_TEMPLATE/submit-resource.yml` to add the category to the dropdown
3. Run `make generate` to update the README

All scripts automatically use the new category without any code changes.

## Automated Backend Scripts

These scripts power the GitHub Issues-based submission workflow and are executed automatically by GitHub Actions:

### `parse_issue_form.py`
**Purpose**: Parses GitHub issue form submissions and extracts resource data
**Usage**: Called by `validate-resource-submission.yml` workflow
**Features**:
- Extracts structured data from issue body
- Validates form field completeness
- Converts form data to resource format
- Provides validation feedback as issue comments

### `create_resource_pr.py`
**Purpose**: Creates pull requests from approved resource submissions
**Usage**: Called by `approve-resource-submission.yml` workflow
**Features**:
- Generates unique resource IDs
- Adds resources to CSV database
- Creates feature branches automatically
- Opens PR with proper linking to original issue
- Handles pre-commit hooks gracefully

## Core Workflow Scripts (Manual/Admin Use)

### 1. `add_resource.py`
**Purpose**: Interactive CLI tool for adding new resources to the CSV database  
**Usage**: `make add_resource`  
**Features**:
- Interactive prompts for all resource fields
- Automatic ID generation
- URL validation with retry support
- GitHub repository metadata fetching
- Duplicate detection
- CSV backup before modification
- Automatic pre-push hook installation

### 2. `generate_readme.py`
**Purpose**: Generates README.md from CSV data using templates
**Usage**: `make generate`
**Features**:
- Template-based generation from `.templates/README.template.md`
- Respects manual overrides from `.templates/resource-overrides.yaml`
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

### 3. `submit_resource.py`
**Purpose**: One-command workflow from resource entry to pull request  
**Usage**: `make submit`  
**Features**:
- Complete automation from add to PR
- Pre-flight checks (git, gh CLI, authentication)
- Automatic pre-push hook installation
- Interactive review points
- Smart branch naming
- Pre-commit hook handling
- Automatic PR creation with template

### 4. `validate_links.py`
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

### 5. `download_resources.py`
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

### 6. `git_utils.py`
**Purpose**: Git and GitHub utility functions  
**Interface**:
- `get_github_username()`: Retrieves GitHub username
- `get_current_branch()`: Gets active git branch
- `create_branch()`: Creates new git branch
- `commit_changes()`: Commits with message
- `push_to_remote()`: Pushes branch to remote
- GitHub CLI integration utilities

### 7. `validate_single_resource.py`
**Purpose**: Validates individual resources  
**Usage**: `make validate-single URL=...`  
**Interface**:
- `validate_single_resource()`: Validates URL and fetches metadata using kwargs
- Used by `add_resource.py` for real-time validation
- Supports both regular URLs and GitHub repositories

### 8. `validate_new_resource.py`
**Purpose**: Pre-push hook validation for new resources  
**Usage**: `make validate_new_resource` (or automatically via git pre-push hook)  
**Features**:
- Compares current branch against upstream/main
- Ensures exactly one resource added per PR
- Validates the new resource entry
- Updates CSV with validation results
- Provides clear error messages for common issues
- Installed automatically by submission workflows

### 9. `sort_resources.py`
**Purpose**: Sorts CSV entries by category hierarchy  
**Usage**: `make sort` (called automatically by `make generate`)  
**Features**:
- Maintains consistent ordering
- Sorts by: Category → Sub-Category → Display Name
- Uses category order from `categories.yaml`
- Preserves CSV structure and formatting

## Utility Scripts

### 10. `generate_resource_id.py`
**Purpose**: Interactive resource ID generator  
**Usage**: `python scripts/generate_resource_id.py`  
**Features**:
- Interactive prompts for display name, link, and category
- Shows all available categories from `categories.yaml`
- Displays generated ID and CSV row preview

### 11. `quick_id.py`
**Purpose**: Command-line ID generation  
**Usage**: `python scripts/quick_id.py 'Display Name' 'https://link.com' 'Category'`  
**Features**:
- Quick one-liner for ID generation
- No interactive prompts
- Useful for scripting and automation

### 12. `resource_id.py`
**Purpose**: Shared resource ID generation module  
**Usage**: `from resource_id import generate_resource_id`  
**Features**:
- Central function used by all ID generation scripts
- Uses category prefixes from `categories.yaml`
- Ensures consistent ID generation across the project

### 13. `badge_issue_notification.py`
**Purpose**: Creates GitHub issues to notify repositories when featured and updates Date Added for new resources
**Usage**: `python scripts/badge_issue_notification.py`
**Features**:
- Tracks processed repos in `.processed_repos.json`
- Updates "Date Added" field in CSV for new resources
- Creates friendly notification issues
- Includes badge markdown for repositories
- Supports dry-run mode
- Automatically triggered by GitHub Actions when new resources are merged
- See `BADGE_AUTOMATION_SETUP.md` for configuration

### 14. `badge_notification_core.py`
**Purpose**: Core functionality for badge notification system
**Usage**: `from badge_notification_core import BadgeNotifier`
**Features**:
- Shared notification logic used by other badge scripts
- Input validation and sanitization
- GitHub API interaction utilities
- Template rendering for notification messages

### 15. `manual_badge_notification.py`
**Purpose**: Manual tool for sending badge notifications to specific repositories
**Usage**: `python scripts/manual_badge_notification.py [repo-owner/repo-name]`
**Features**:
- Send notifications outside of the automated workflow
- Useful for re-sending failed notifications
- Supports custom notification messages
- Bypasses the processed repos tracking

### 16. `generate_logo_svgs.py`
**Purpose**: Generates SVG logos for the repository
**Usage**: `python scripts/generate_logo_svgs.py`
**Features**:
- Creates consistent branding assets
- Generates multiple size variants
- Supports dark/light mode variants
- Used for README badges and documentation

## Legacy/Archived Scripts

### `process_resources_to_csv.py`
**Status**: LEGACY - From previous workflow where README was source of truth  
**Purpose**: Extracts resources from README.md to create CSV  
**Note**: Current workflow is CSV → README, not README → CSV

## Workflow Integration

### Primary Workflow (GitHub Issues)

**For Users**: Submit resources through the GitHub Issue form at `.github/ISSUE_TEMPLATE/submit-resource.yml`
1. User fills out the issue form
2. `validate-resource-submission.yml` workflow validates the submission automatically
3. Maintainer reviews and uses `/approve` command
4. `approve-resource-submission.yml` workflow creates the PR automatically

### Manual Backup Workflows (Make Commands)

These commands remain available for maintainers and emergency situations:

#### Adding a Resource Manually
```bash
make add_resource      # Interactive addition (installs pre-push hook)
make generate         # Regenerate README
make validate         # Validate all links
```

#### One-Command Manual Submission
```bash
make submit           # Complete flow from add to PR (installs pre-push hook)
```

### Maintenance Tasks
```bash
make sort            # Sort CSV entries
make validate        # Check all links
make download-resources  # Archive resources
make validate_new_resource  # Manually run pre-push validation
make install-hooks   # Manually install git hooks
```

## Configuration

Scripts respect these configuration files:
- `.templates/resource-overrides.yaml`: Manual overrides for resources
- `.processed_repos.json`: Tracks notified repositories
- `.env`: Environment variables (not tracked in git)
- `hooks/pre-push`: Git pre-push hook for validation

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
7. Pre-push validation enforces one resource per PR policy
8. Automatic hook installation in submission workflows

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

- `process_resources_to_csv.py` could be removed if no longer needed
- `badge_issue_notification.py` could be integrated into the main workflow
- Additional validation rules could be added
- More sophisticated duplicate detection
