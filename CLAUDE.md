# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a curated list repository for Claude Code resources. It uses a CSV-driven architecture with automated validation and template-based README generation. The entire system is automated through GitHub Actions, Python scripts, and Make commands.

## Core Architecture

### Data Flow
```
THE_RESOURCES_TABLE.csv (single source of truth)
    ↓ (processed by)
templates/categories.yaml + templates/README.template.md
    ↓ (generates)
README.md (auto-generated, never edit manually)
```

### Key Files
- `THE_RESOURCES_TABLE.csv` - The single source of truth for all resources
- `templates/categories.yaml` - Single source of truth for categories, icons, order
- `templates/resource-overrides.yaml` - Manual overrides for specific resources
- `templates/README.template.md` - Main template structure
- `templates/announcements.yaml` - Announcements content (renders as nested collapsible sections)

### Scripts Organization
All automation lives in `scripts/`:
- `generate_readme.py` - Generates README from CSV and templates
- `validate_links.py` - Validates all resource URLs
- `validate_single_resource.py` - Single resource validation
- `parse_issue_form.py` - Parses GitHub issue form submissions
- `create_resource_pr.py` - Creates PRs from approved submissions
- `add_category.py` - Interactive category addition tool
- `sort_resources.py` - Sorts CSV by category/subcategory/name

## Common Commands

### Essential Development Commands
```bash
# Generate README from CSV (most common operation)
make generate

# Validate all resource links
make validate

# Validate single URL
make validate-single URL=https://example.com

# Run tests
make test

# Format code with ruff
make format

# Check formatting without fixing
make format-check
```

### Resource Management
```bash
# Add new resource interactively
make add_resource

# Add new category (updates categories.yaml + issue template)
make add-category

# Sort resources
make sort

# Process README to extract resources to CSV
make process
```

### Local Development Setup
```bash
# Install dependencies (uses venv/bin/python3 locally, python3 in CI)
make install

# Clean generated files
make clean
```

## Important Architectural Patterns

### CSV-Driven System
- **Never edit README.md manually** - it's auto-generated from CSV
- CSV structure includes: ID, Display Name, Category, Sub-Category, Primary Link, Secondary Link, Author Name, Author Link, Active, Date Added, Last Modified, Last Checked, License, Description
- IDs follow format: `{prefix}-{hash}` (e.g., `skill-a1b2c3d4`, `cmd-e5f6g7h8`)
- Resource IDs are generated from category prefix + SHA256 hash of (display_name + primary_link)

### Category System
- All categories defined in `templates/categories.yaml`
- Each category has: id, name, prefix, icon, description, order, subcategories
- Adding a new category requires updating categories.yaml (use `make add-category`)
- The system automatically updates issue templates and README when categories change

### Template-Based Generation
- README uses collapsible `<details>` sections for navigation
- Categories without subcategories are fully collapsible
- Categories with subcategories have collapsible subcategory sections
- GitHub resources automatically include collapsible stats using GitHub Stats API
- Template renders announcements from YAML as nested collapsible sections

### Validation System
- Validates HTTP status codes (200-299 = valid)
- For GitHub links: fetches metadata, license info, last commit date
- Override system in `resource-overrides.yaml` for special cases
- Scheduled GitHub Action runs validation periodically

### GitHub Actions Workflow
1. User submits via issue form → auto-labeled `resource-submission`
2. Validation workflow runs → adds `validation-passed` or `validation-failed`
3. Maintainer reviews and comments `/approve`, `/request-changes`, or `/reject`
4. Approval triggers PR creation workflow:
   - Creates branch: `add-resource/{category}/{name}-{timestamp}`
   - Adds to CSV with generated ID
   - Runs `generate_readme.py`
   - Creates PR and closes issue

## Python Environment

- Requires Python 3.11+
- Uses `pyproject.toml` for dependency management
- Ruff for linting/formatting (line-length: 100)
- PyGithub for GitHub API interactions
- Pytest for testing

## Testing Changes

Before submitting changes:
```bash
# 1. Make your changes to scripts or templates

# 2. If modifying generation logic, test it
make generate

# 3. If modifying validation, test it
make validate-single URL=https://github.com/example/repo

# 4. Run tests
make test

# 5. Format code
make format
```

## Key Conventions

### CSV Operations
- Always use the scripts to modify CSV (never edit manually)
- After CSV changes, run `make generate` to update README
- Resource sorting is by: category order → subcategory → name

### Adding New Categories
- Use `make add-category` for interactive mode
- Updates both `categories.yaml` and `.github/ISSUE_TEMPLATE/submit-resource.yml`
- Automatically regenerates README with new section

### GitHub Stats Integration
- GitHub URLs are auto-detected by `parse_github_url()` in `validate_links.py`
- Stats rendered using: `https://github-readme-stats-plus-theta.vercel.app/api/pin/`
- Works with all GitHub URL formats (root, blob, tree, etc.)

### Collapsible Sections Design
- Table of Contents has nested sections for categories with subcategories
- Categories without subcategories are wrapped in `<details open>`
- Subcategories always wrapped in `<details open>`
- All sections open by default for easy browsing
- **Note**: Making parent categories collapsible breaks anchor link navigation to subcategories

## Git Workflow

When working on this repository:
- Branch naming: `claude/init-project-011CUogDpCPjZMetguHA1pQ1` (current session)
- Always develop on designated branch
- For git push: use `git push -u origin <branch-name>`
- Branch must start with `claude/` and match session ID
- On 403 errors during push: retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

## Security Considerations

- All submissions reviewed before merging
- Input validation and sanitization on all user data
- Only HTTPS URLs accepted
- No direct CSV manipulation by users (all changes via scripts/automation)
