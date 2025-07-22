# Badge Issue Notification Setup Guide

## Overview
This system creates friendly notification issues on GitHub repositories when they are **newly** featured in the Awesome Claude Code list. It only notifies for new additions, not existing entries.

## Prerequisites
1. Python 3.11+
2. PyGithub library (installed automatically via pyproject.toml)

## Setup Steps

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Configure GitHub Token
Create a Personal Access Token on GitHub with appropriate permissions for creating issues in external repositories.

For local testing:

Option 1: Use environment variable
```bash
export AWESOME_CC_PAT_PUBLIC_REPO=your_github_personal_access_token
```

Option 2: Use .env file (recommended)
```bash
echo "AWESOME_CC_PAT_PUBLIC_REPO=your_github_personal_access_token" > .env
```

The script will automatically load the token from .env if present. The .env file is gitignored for security.

Note: The default `GITHUB_TOKEN` from GitHub Actions is not sufficient for creating issues in external repositories. You must use a Personal Access Token.

### 3. Manual Testing
Process all entries in the CSV:
```bash
python badge_issue_notification.py
```

## GitHub Action Setup

### 1. Required Setup
Add your Personal Access Token as a repository secret named `AWESOME_CC_PAT_PUBLIC_REPO`:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `AWESOME_CC_PAT_PUBLIC_REPO`
4. Value: Your Personal Access Token with `public_repo` scope

### 2. Automatic Triggers
The action automatically runs when:
- THE_RESOURCES_TABLE.csv is updated on main branch
- Manual workflow dispatch

### 3. Manual Trigger
1. Go to Actions tab
2. Select "Badge Issue Notifications"
3. Click "Run workflow"

## How It Works

### Issue Creation Process
1. Loads all GitHub repositories from THE_RESOURCES_TABLE.csv
2. Compares against `.processed_repos.json` to find new entries
3. Creates friendly notification issues for new repositories
4. Updates `.processed_repos.json` with newly processed repos
5. GitHub Action commits the updated file

### New Entry Detection
- Maintains a `.processed_repos.json` file with all previously processed repositories
- Compares current CSV entries against this list to find new repositories
- Resilient to CSV reordering, formatting changes, and description edits
- Only creates issues for repositories not in the processed list

### Initial Setup
Before first use, run with `--init` flag to populate the processed list with all existing entries:
```bash
python scripts/badge_issue_notification.py --init
```
This ensures no existing entries get notified - only future additions.

### Issue Content
- Friendly greeting and announcement
- Description of Awesome Claude Code
- Two badge style options (standard and flat)
- Clear markdown snippets for easy copying
- No action required message

### Duplicate Prevention
- Maintains `.processed_repos.json` file
- Checks for existing issues by the bot
- Skips repositories already processed

## Features

### Advantages Over PR Approach
- ✅ Non-intrusive - just information
- ✅ No code changes required
- ✅ Maintainers can close anytime
- ✅ Much simpler implementation
- ✅ No fork/branch management
- ✅ Faster processing

### Error Handling
- Gracefully handles:
  - Private repositories
  - Disabled issues
  - Rate limiting
  - Invalid URLs

## Manual Testing

You can test the script locally:

```bash
# First time: Initialize with existing repos
export AWESOME_CC_PAT_PUBLIC_REPO=your_token_here
python scripts/badge_issue_notification.py --init

# Test processing (dry run - won't actually create issues)
python scripts/badge_issue_notification.py

# Skip issue creation (just mark repos as processed)
export CREATE_ISSUES=false
python scripts/badge_issue_notification.py
```

## Controlling Issue Creation

The workflow supports disabling issue creation while still tracking processed repositories:

1. **Via GitHub Actions UI**: When manually triggering the workflow, select "false" for "Create notification issues"
2. **Via Environment Variable**: Set `CREATE_ISSUES=false` when running locally
3. **Default Behavior**: Issues are created by default unless explicitly disabled

## Monitoring
Check GitHub Actions logs for:
- Number of repositories processed
- Successfully created issues
- Any errors or skipped repos
