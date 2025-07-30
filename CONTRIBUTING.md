# Contributing to Awesome Claude Code

Welcome! We're excited that you want to contribute to Awesome Claude Code. This guide will walk you through our contribution process, which has been designed to be as simple as possible, despite the admittedly absurd length of this document. That being said, if you find the automated process is not working for you, we definitely do not wish to dissuade anyone from contributing, so just make your best effort. Regarding reviews, I take reviews seriously, not only from a quality control point of view, but more importantly for security - this technology can expose users to serious data risks if not handled with care, and I do not wish to promote any resource that undermines security, or perhaps even is malicious. The consequence is that approval of especially more advanced tools may take a little time.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms. Follow the conventions of the repo and don't engage in self-promotion. Use descriptive language, not "marketing" style.

## Contribution Process

There are a few ways to contribute to this repository. Generally the goal is to isolate all new submissions to adding a single row to the main CSV file, [`THE_RESOURCES_TABLE.csv`](./THE_RESOURCES_TABLE.csv). The rest of the process is meant to be automated. If you can't get it to work for some reason, you may submit a PR manually with just the data in the CSV file. If you're interested in how this works, visit the [`scripts`](./scripts) directory.

#### Setup Instructions

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

### How to Contribute

#### Method 1: One-Command Workflow

Our `make submit` command provides a completely streamlined submission process - due to its relative complexity, there are also more failure points; if you encounter any road bumps or jank, feel free to open an Issue. You may also find the other method simpler.

```bash
make submit
```

**What happens:**

1. ✅ Checks all prerequisites (git, gh auth, fork setup - fork this repo, clone it, set it as "upstream" remote)
2. 🔒 Installs pre-push validation hook automatically (checks that your entry is well-formed and link is working on push)
3. 📝 Guides you through resource information entry
4. 🔍 Validates your inputs
5. 📄 Updates THE_RESOURCES_TABLE.csv
6. 🔄 Regenerates README.md
7. 👀 Shows you the changes for review
8. 🌿 Creates a feature branch
9. 💾 Commits your changes
10. 🚀 Pushes to your fork (with validation)
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

- Install pre-push validation hook automatically
- Guide you through resource entry
- Update the CSV file
- Generate README.md
- Create `.pr_template_content.md` with PR description

You'll need to manually:

- Create a branch
- Commit changes
- Push to your fork
- Create a PR (copying content from `.pr_template_content.md`)

For complete control over the process:

1. Edit `THE_RESOURCES_TABLE.csv` directly (you can generate an ID using the [`quick_id.py`](./scripts/quick_id.py) script)
2. Run `make validate` to check your changes
3. Run `make generate` to update `README.md`
4. Create a branch, commit, push, and open PR manually

## Understanding the Repository

### CSV-Based Architecture

All resources are stored in `THE_RESOURCES_TABLE.csv` with these fields:

| Field          | Description                       | Required        |
| -------------- | --------------------------------- | --------------- |
| ID             | Auto-generated unique identifier  | Yes (automatic) |
| Display Name   | Resource name shown in README     | Yes             |
| Primary Link   | Main URL for the resource         | Yes             |
| Secondary Link | Optional secondary URL            | No              |
| Author Name    | Creator's name/username/alias     | Yes             |
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
- 🔄 Work with the latest version of Claude Code
- 📝 Include clear documentation (demo videos are a huge bonus!)
- ❄️ Be unique and different from other existing awesome resources
- ⚖️ Respect the Terms of Service that govern the usage of Claude Code

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

### Testing Your Changes

Before submitting, you can test your changes:

```bash
# Make sure you are up to date with upstream/main
git fetch upstream
git merge upstream/main

# Validate your CSV entry
make validate_new_resource

# Check if README generates correctly
make generate
```

## Badges

If your submission is approved, you can add a badge to your README:

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

If your resource is on GitHub, tthen if it gets included, our automated system will create a friendly notification issue on your repository informing you of the inclusion and providing badge options.

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

# Manually run pre-push validation
make validate_new_resource
```

---

For transparency - @hesreallyhim has no affiliation with Anthropic or with Claude (great guy, though).

Thank you for helping make Awesome Claude Code even more awesome! 🚀
