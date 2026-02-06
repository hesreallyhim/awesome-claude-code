---
name: publish-github
description: Initialize a git repository and push to GitHub using gh CLI. Creates public repos with proper commits and README.
disable-model-invocation: true
---

# Publish to GitHub

Push a project to GitHub using git and `gh` CLI.

## Arguments
`$ARGUMENTS` = optional repo name (defaults to current directory name)

## Prerequisites
- `git` installed and configured
- `gh` CLI authenticated (`gh auth login`)

## Process

1. **Read the GitHub skill**: `cat skills/github-skill.md`

2. **Initialize git** (if not already):
   ```bash
   git init
   git add -A
   git commit -m "feat: initial project — $ARGUMENTS"
   ```

3. **Create GitHub repo**:
   ```bash
   REPO_NAME="${ARGUMENTS:-$(basename $(pwd))}"
   gh repo create "$REPO_NAME" --public --source=. --push \
     --description "Built with Claude Code AI Agent System"
   ```

4. **Verify**:
   ```bash
   gh repo view --web
   ```

5. **Report the URL**:
   ```bash
   echo "Published: https://github.com/$(gh api user -q .login)/$REPO_NAME"
   ```

## Commit Convention
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `chore:` — Maintenance

## Creating a Release (optional)
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release"
```
