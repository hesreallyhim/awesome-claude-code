# Contributing to Awesome Claude Code

Welcome! We're excited that you want to contribute to Awesome Claude Code. This guide will walk you through our contribution process, which has been designed to be as simple as possible.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms.

## Quick Start: One-Command Submission

The fastest way to contribute a new resource is:

```bash
make submit
```

This single command handles everything from resource entry to pull request creation. Skip to [Prerequisites](#prerequisites) to get started!

## Prerequisites

### Required Tools

1. **Git** - Version control
2. **Python 3.6+** - For running scripts
3. **Make** - Build automation
4. **GitHub CLI (`gh`)** - For PR creation

### Setup Instructions

1. **Install GitHub CLI**

   ```bash
   # macOS
   brew install gh

   # Ubuntu/Debian
   sudo apt install gh

   # Windows
   scoop install gh
   # or
   choco install gh
   ```

2. **Authenticate with GitHub**

   ```bash
   gh auth login
   ```

   Follow the prompts to authenticate via browser or token.

3. **Fork and Clone**

   - Fork this repository on GitHub (click the Fork button)
   - Clone your fork:
     ```bash
     git clone https://github.com/YOUR_USERNAME/awesome-claude-code.git
     cd awesome-claude-code
     ```
   - Add upstream remote:
     ```bash
     git remote add upstream https://github.com/hesreallyhim/awesome-claude-code.git
     ```

4. **Configure Git** (if needed)
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## How to Contribute

### Method 1: One-Command Workflow (Recommended)

Our `make submit` command provides a complete submission workflow:

```bash
make submit
```

**What happens:**

1. ✅ Checks all prerequisites (git, gh auth, fork setup)
2. 📝 Guides you through resource information entry
3. 🔍 Validates your inputs
4. 📄 Updates THE_RESOURCES_TABLE.csv
5. 🔄 Regenerates README.md
6. 👀 Shows you the changes for review
7. 🌿 Creates a feature branch
8. 💾 Commits your changes
9. 🔧 Handles pre-commit hooks automatically
10. 🚀 Pushes to your fork
11. 🎯 Creates a pull request
12. 🌐 Opens the PR in your browser

**Important:** Submit one resource per PR. Multiple resources require separate pull requests.

### Method 2: Interactive Script Only

If you prefer to handle git operations manually:

```bash
make add-resource
# or
python scripts/add_resource.py
```

This will:

- Guide you through resource entry
- Update the CSV file
- Generate README.md
- Create `.pr_template_content.md` with PR description

You'll need to manually:

- Create a branch
- Commit changes
- Push to your fork
- Create a PR (copying content from `.pr_template_content.md`)

### Method 3: Claude Code Command

If you're using Claude Code:

```bash
/add-new-resource
```

This provides a guided wizard experience within Claude Code.

### Method 4: Manual Contribution

For complete control over the process:

1. Edit `THE_RESOURCES_TABLE.csv` directly
2. Run `make validate` to check your changes
3. Run `make generate` to update README.md
4. Create a branch, commit, push, and PR manually

## Understanding the Repository

### CSV-Based Architecture

All resources are stored in `THE_RESOURCES_TABLE.csv` with these fields:

| Field          | Description                       | Required        |
| -------------- | --------------------------------- | --------------- |
| ID             | Auto-generated unique identifier  | Yes (automatic) |
| Display Name   | Resource name shown in README     | Yes             |
| Primary Link   | Main URL for the resource         | Yes             |
| Secondary Link | Optional secondary URL            | No              |
| Author Name    | Creator's name/username           | Yes             |
| Author Link    | Link to author's profile          | Yes             |
| Category       | Main category (see below)         | Yes             |
| Sub-Category   | Optional sub-category             | No              |
| Active         | TRUE for active resources         | Yes             |
| Last Modified  | Auto-updated by validation        | No              |
| Last Checked   | Auto-updated by validation        | No              |
| License        | License type (MIT, etc.)          | Recommended     |
| Description    | Brief description (1-2 sentences) | Yes             |

### Categories

- **Workflows & Knowledge Guides** - Comprehensive workflow systems
- **Tooling** - CLI applications and executables
  - IDE Integrations
- **Hooks** - Claude Code hook configurations
- **Slash-Commands** - Individual command files
  - Version Control & Git
  - Code Analysis & Testing
  - Context Loading & Priming
  - Documentation & Changelogs
  - CI / Deployment
  - Project & Task Management
  - Miscellaneous
- **CLAUDE.md Files** - Project configuration files
  - Language-Specific
  - Domain-Specific
  - Project Scaffolding & MCP
- **Official Documentation** - Anthropic resources

## What Makes a Resource "Awesome"?

Your submission should:

- ✨ Provide genuine value to Claude Code users
- 🚀 Demonstrate innovative or exemplary usage patterns
- 📚 Follow best practices for the resource type
- ⭐ Come from a reputable source (high star count helps!)
- 🔄 Work with the latest version of Claude Code
- 📝 Include clear documentation
- ⚖️ Have an appropriate license (for code resources)

We especially welcome:

- Proven workflows used in production
- Creative experiments pushing Claude Code's boundaries
- Tools that enhance Claude Code functionality
- Non-traditional applications (CI/CD, testing, documentation)

## Troubleshooting

### Common Issues and Solutions

**"GitHub CLI is not authenticated"**

```bash
gh auth login
```

**"No fork found"**

- Ensure you've forked the repository on GitHub
- Check your remotes: `git remote -v`

**"Branch already exists"**

```bash
git branch -D old-branch-name
# or let the script create a unique branch name
```

**Pre-commit hook failures**

- The `make submit` workflow handles these automatically
- For manual commits, stage the auto-fixed files and retry

**"Rate limit exceeded"**

- Wait 1 hour for reset
- Or authenticate with `gh auth login` for higher limits

### Debug Mode

For verbose output:

```bash
make submit ARGS="--debug"
```

## Advanced Usage

### Environment Variables

Optional configuration:

```bash
# Change remote names (defaults shown)
export AWESOME_CC_FORK_REMOTE=origin
export AWESOME_CC_UPSTREAM_REMOTE=upstream

# Disable automatic PR browser opening
export AWESOME_CC_AUTO_OPEN_PR=false
```

### Submitting Multiple Resources

While we require one resource per PR, you can streamline multiple submissions:

```bash
# Submit first resource
make submit

# After PR is created, start fresh for next resource
git checkout main
git pull upstream main
make submit
```

### Testing Your Changes

Before submitting:

```bash
# Validate your CSV entry (requires "GITHUB_TOKEN env variable - can skip)
make validate

# Test with limited link checking
make validate MAX_LINKS=10

# Check if README generates correctly
make generate
```

## Badges

Once your resource is added, you can add a badge to your README:

[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)](https://github.com/hesreallyhim/awesome-claude-code)

```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)](https://github.com/hesreallyhim/awesome-claude-code)
```

Or the flat version:

[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge-flat.svg)](https://github.com/hesreallyhim/awesome-claude-code)

```markdown
[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge-flat.svg)](https://github.com/hesreallyhim/awesome-claude-code)
```

## GitHub Repository Notifications

When your GitHub-hosted resource is added, our automated system will create a friendly notification issue on your repository informing you of the inclusion and providing badge options.

## Getting Help

- 📖 Check existing issues for similar questions
- 💬 Open a new issue for persistent problems
- 🐛 Include error messages and debug output
- 🔒 Report security issues immediately

## Quick Reference

```bash
# Complete workflow (recommended)
make submit

# Just add resource (no git operations)
make add-resource

# Validate CSV integrity
make validate

# Generate README from CSV
make generate
```

---

Thank you for helping make Awesome Claude Code even more awesome! 🚀
