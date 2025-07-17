# Scripts Directory

This directory contains all automation scripts for managing the Awesome Claude Code repository. The scripts work together to provide a complete workflow for resource management, from addition to pull request submission.

## Overview

The scripts implement a CSV-first workflow where `THE_RESOURCES_TABLE.csv` serves as the single source of truth for all resources. The README.md is generated from this CSV data using templates.

## Core Workflow Scripts

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

### 2. `generate_readme.py`
**Purpose**: Generates README.md from CSV data using templates  
**Usage**: `make generate`  
**Features**:
- Template-based generation from `.templates/README.template.md`
- Respects manual overrides from `.templates/resource-overrides.yaml`
- Hierarchical table of contents generation
- Preserves custom sections from template
- Automatic backup before generation

### 3. `submit_resource.py`
**Purpose**: One-command workflow from resource entry to pull request  
**Usage**: `make submit`  
**Features**:
- Complete automation from add to PR
- Pre-flight checks (git, gh CLI, authentication)
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
- `validate_resource()`: Validates URL and fetches metadata
- Used by `add_resource.py` for real-time validation
- Supports both regular URLs and GitHub repositories

### 8. `sort_resources.py`
**Purpose**: Sorts CSV entries by category hierarchy  
**Usage**: `make sort` (called automatically by `make generate`)  
**Features**:
- Maintains consistent ordering
- Sorts by: Category → Sub-Category → Display Name
- Preserves CSV structure and formatting

## Utility Scripts

### 9. `generate_resource_id.py`
**Purpose**: Interactive resource ID generator  
**Usage**: `python scripts/generate_resource_id.py`  
**Features**:
- Standalone utility for manual ID generation
- Interactive prompts for resource type and name
- Follows project ID conventions

### 10. `quick_id.py`
**Purpose**: Command-line ID generation  
**Usage**: `python scripts/quick_id.py <resource_type> <name>`  
**Features**:
- Quick one-liner for ID generation
- No interactive prompts
- Useful for scripting

### 11. `badge_issue_notification.py`
**Purpose**: Creates GitHub issues to notify repositories when featured  
**Usage**: `python scripts/badge_issue_notification.py`  
**Features**:
- Tracks processed repos in `.processed_repos.json`
- Creates friendly notification issues
- Includes badge markdown for repositories
- Supports dry-run mode
- See `BADGE_AUTOMATION_SETUP.md` for configuration

## Legacy/Archived Scripts

### 12. `process_resources_to_csv.py`
**Status**: LEGACY - From previous workflow where README was source of truth  
**Purpose**: Extracts resources from README.md to create CSV  
**Note**: Current workflow is CSV → README, not README → CSV

## Workflow Integration

The scripts are integrated through the Makefile with these primary workflows:

### Adding a Resource
```bash
make add_resource      # Interactive addition
make generate         # Regenerate README
make validate         # Validate all links
```

### One-Command Submission
```bash
make submit           # Complete flow from add to PR
```

### Maintenance Tasks
```bash
make sort            # Sort CSV entries
make validate        # Check all links
make download-resources  # Archive resources
```

## Configuration

Scripts respect these configuration files:
- `.templates/resource-overrides.yaml`: Manual overrides for resources
- `.processed_repos.json`: Tracks notified repositories
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

## Future Considerations

- `process_resources_to_csv.py` could be removed if no longer needed
- `badge_issue_notification.py` could be integrated into the main workflow
- Additional validation rules could be added
- More sophisticated duplicate detection
