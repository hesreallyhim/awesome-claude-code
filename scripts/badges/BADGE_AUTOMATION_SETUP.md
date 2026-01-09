# Badge Issue Notification Setup Guide

## Overview
This system creates friendly notification issues on GitHub repositories when they are **newly** featured in the Awesome Claude Code list. It only notifies for new additions, not existing entries.

## Prerequisites
1. Python 3.11+
2. PyGithub library (installed automatically via pyproject.toml)

## GitHub Action Setup

### 1. Required Setup
Add your Personal Access Token as a repository secret named `AWESOME_CC_PAT_PUBLIC_REPO`:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `AWESOME_CC_PAT_PUBLIC_REPO`
4. Value: Your Personal Access Token with `public_repo` scope

### 2. Automatic Triggers
The action automatically runs when resource PRs are merged by the automation bot.

## How It Works

### Issue Creation Process
1. Extracts the GitHub URL and resource name from the merged PR
2. Runs `scripts/badges/badge_notification.py` to send a single notification issue

### Issue Content
- Friendly greeting and announcement
- Description of Awesome Claude Code
- Two badge style options (standard and flat)
- Clear markdown snippets for easy copying
- No action required message

### Duplicate Prevention
- Checks for existing issues by the bot

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
