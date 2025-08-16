# 🚀 Codegen + Claude Code: Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Set up Secrets

```bash
# Set Claude Code OAuth token (Required)
gh secret set CLAUDE_CODE_OAUTH_TOKEN

# GitHub token is automatically provided by GitHub Actions
# No need to set GITHUB_TOKEN manually
```

### Step 2: Install GitHub Apps

1. **Claude Code**: Install via `/install-github-app` in Claude Code terminal
2. **Codegen**: [Install from GitHub Marketplace](https://github.com/marketplace/codegen-sh)

### Step 3: Connect Integrations

Go to [codegen.com/integrations](https://codegen.com/integrations) and connect:

- ✅ GitHub (Required)
- 📊 Linear (Recommended)
- 💬 Slack (Optional)

## 🎯 How to Use

### Automatic Implementation

Create an issue with one of these labels:

- `codegen:auto-implement` - Full auto mode
- `enhancement` - New features
- `bug` - Bug fixes

Example:

```markdown
Title: Add user authentication
Labels: enhancement, codegen:auto-implement

Description:
Implement JWT-based authentication with:
- Login endpoint
- Token refresh
- Protected routes
```

**Result**: Codegen will automatically create a branch, implement the feature, and open a PR.

### Quick Commands

In any issue or PR, use these commands:

| Command | What it does | Example |
|---------|--------------|---------|
| `/implement` | Create implementation | `/implement Add dark mode` |
| `/fix` | Fix a bug | `/fix Login timeout issue` |
| `/test` | Add tests | `/test Auth module` |
| `/docs` | Update docs | `/docs API endpoints` |
| `@claude` | Ask Claude | `@claude Review this code` |

### PR Reviews

Every PR automatically gets:

1. **Claude Code Review** - AI-powered code review
2. **Codegen Analysis** - Pattern compliance check
3. **Security Scan** - Vulnerability detection

## 📊 Status Labels

Codegen automatically manages these labels:

- 🚀 `codegen:auto-implement` - Ready for automation
- ⚡ `codegen:in-progress` - Being worked on
- ✅ `codegen:ready` - Ready for review
- ✨ `codegen:done` - Completed

## 🔥 Real Examples

### Example 1: Quick Bug Fix

```markdown
# In issue comment:
/fix The login button doesn't work on mobile

# Codegen will:
1. Create branch: codegen/123-fix-mobile-login
2. Implement the fix
3. Add tests
4. Create PR
```

### Example 2: Feature Request

```markdown
# Create issue:
Title: Add CSV export
Labels: enhancement, codegen:auto-implement

# Codegen will:
1. Analyze requirements
2. Implement CSV export
3. Add documentation
4. Create PR with tests
```

### Example 3: Claude Assistance

```markdown
# In PR comment:
@claude Can you improve the error handling in this function?

# Claude will:
1. Review the code
2. Suggest improvements
3. Can even implement changes
```

## ⚙️ Configuration

### Basic Settings (.codegen.yml)

```yaml
automation:
  auto_pr:
    enabled: true
    triggers:
      - label: "codegen:auto-implement"
      
ai_agent:
  model: claude-3-opus
  temperature: 0.7
```

### Workflow Customization

Edit `.github/workflows/codegen-automation.yml` to customize triggers and behaviors.

## 🛠️ Troubleshooting

### Issue: Bot permission denied

**Solution**: Workflows already configured to allow bots

### Issue: PR not created

**Check**:

- Issue has correct labels
- Codegen app is installed
- Secrets are configured

### Issue: Claude not responding

**Check**:

- Used `@claude` mention
- CLAUDE_CODE_OAUTH_TOKEN is set
- PR/Issue is public or Claude has access

## 📈 Monitoring

### Check Automation Status

```bash
# View recent automation runs
gh run list --workflow=codegen-automation.yml

# Check specific run
gh run view <run-id>

# View Claude reviews
gh pr view <pr-number> --comments
```

### Daily Reports

Automated daily standup at 9 AM shows:

- Active issues
- Open PRs
- Completed tasks
- Blocked items

## 🎉 Tips & Tricks

1. **Batch Operations**: Label multiple issues at once for bulk automation
2. **Custom Workflows**: Define your own in `.codegen.yml`
3. **Linear Sync**: Issues ↔️ Linear tasks automatically sync
4. **Slack Updates**: Get real-time notifications in Slack
5. **Draft PRs**: Add `[WIP]` to title to create as draft

## 🔗 Useful Links

- [Full Documentation](./docs/AUTOMATED_DEVELOPMENT.md)
- [Codegen Dashboard](https://codegen.com/dashboard)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)
- [GitHub Actions Status](../../actions)

## 💡 Pro Tips

### Speed up development

```bash
# Create and auto-implement in one command
gh issue create --title "Add feature X" --label "codegen:auto-implement"
```

### Bulk updates

```bash
# Apply label to multiple issues
gh issue list --limit 10 | xargs -I {} gh issue edit {} --add-label "codegen:auto-implement"
```

### Monitor progress

```bash
# Watch automation in real-time
gh run watch
```

---

**Need help?**

- Create issue with `question` label
- Ask `@claude` in any PR/issue
- Check [troubleshooting guide](./docs/AUTOMATED_DEVELOPMENT.md#troubleshooting)

---

*Powered by [Codegen](https://codegen.com) + [Claude Code](https://claude.ai)*
