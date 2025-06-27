# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the Awesome Claude Code repository - a curated list of slash-commands, CLAUDE.md files, CLI tools, and other resources for enhancing Claude Code workflows. The repository serves as a community resource hub for sharing knowledge and best practices.

## Common Development Tasks

### Adding New Resources

1. **Use the slash-command**: Run `/project:add-new-resource` to be guided through adding a new resource
2. **Manual addition**: Edit README.md following the existing format and alphabetical ordering

### Checking Links

Run `/check-links` to verify all links in the README are working properly.

### Creating Pull Requests

1. Follow the PR template in `.github/PULL_REQUEST_TEMPLATE.md`
2. Ensure entries are properly categorized and alphabetically ordered
3. Use permalinks when linking to GitHub files

## Repository Structure

- **README.md**: Main list of resources, organized by category
- **CONTRIBUTING.md**: Contribution guidelines
- **code-of-conduct.md**: Community standards
- **.claude/commands/**: Custom slash-commands for this project
  - `add-new-resource.md`: Wizard for adding new resources
  - `add-new-claude-md.md`: Helper for adding CLAUDE.md files
  - `check-links.md`: Link validation tool
  - `commit-all.md`: Commit helper
  - `create-badge-pr.md`: Badge creation helper

## Key Guidelines

1. **Resource Quality**: Only include resources that provide genuine value to Claude Code users
2. **Formatting**: Follow existing formatting exactly - entries are categorized and alphabetically ordered
3. **Attribution**: Always include proper attribution and prefer permalinks for GitHub resources
4. **Categories**:
   - Workflows & Knowledge Guides
   - Tooling
   - Slash-Commands (organized by command name)
   - CLAUDE.md Files (organized by repository name)
   - Official Documentation

## Working with This Repository

- The repository excludes `.myob` and `.claude` directories from analysis unless specifically requested
- This is a documentation/curation project focused on maintaining high-quality, well-organized content
- While no source code testing is needed, consider implementing:
  - Link validation tests to ensure all curated resources remain accessible
  - Markdown linting to maintain consistent formatting
  - CI/CD checks for PR validation (formatting, alphabetical ordering, category placement)