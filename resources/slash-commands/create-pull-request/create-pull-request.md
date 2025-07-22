# How to Create a Pull Request Using GitHub CLI

This guide explains how to create pull requests using GitHub CLI in our project.

## Prerequisites

1. Install GitHub CLI if you haven't already:

   ```bash
   # macOS
   brew install gh

   # Windows
   winget install --id GitHub.cli

   # Linux
   # Follow instructions at https://github.com/cli/cli/blob/trunk/docs/install_linux.md
   ```

2. Authenticate with GitHub:
   ```bash
   gh auth login
   ```

## Creating a New Pull Request

1. First, prepare your PR description following the template in `.github/pull_request_template.md`

2. Use the `gh pr create` command to create a new pull request:

   ```bash
   # Basic command structure
   gh pr create --title "✨(scope): Your descriptive title" --body "Your PR description" --base main --draft
   ```

   For more complex PR descriptions with proper formatting, use the `--body-file` option with the exact PR template structure:

   ```bash
   # Create PR with proper template structure
   gh pr create --title "✨(scope): Your descriptive title" --body-file <(echo -e "## Issue\n\n- resolve:\n\n## Why is this change needed?\nYour description here.\n\n## What would you like reviewers to focus on?\n- Point 1\n- Point 2\n\n## Testing Verification\nHow you tested these changes.\n\n## What was done\npr_agent:summary\n\n## Detailed Changes\npr_agent:walkthrough\n\n## Additional Notes\nAny additional notes.") --base main --draft
   ```

## Best Practices

1. **PR Title Format**: Use conventional commit format with emojis

   - Always include an appropriate emoji at the beginning of the title
   - Use the actual emoji character (not the code representation like `:sparkles:`)
   - Examples:
     - `✨(supabase): Add staging remote configuration`
     - `🐛(auth): Fix login redirect issue`
     - `📝(readme): Update installation instructions`

2. **Description Template**: Always use our PR template structure from `.github/pull_request_template.md`:

   - Issue reference
   - Why the change is needed
   - Review focus points
   - Testing verification
   - PR-Agent sections (keep `pr_agent:summary` and `pr_agent:walkthrough` tags intact)
   - Additional notes

3. **Template Accuracy**: Ensure your PR description precisely follows the template structure:

   - Don't modify or rename the PR-Agent sections (`pr_agent:summary` and `pr_agent:walkthrough`)
   - Keep all section headers exactly as they appear in the template
   - Don't add custom sections that aren't in the template

4. **Draft PRs**: Start as draft when the work is in progress
   - Use `--draft` flag in the command
   - Convert to ready for review when complete using `gh pr ready`

### Common Mistakes to Avoid

1. **Incorrect Section Headers**: Always use the exact section headers from the template
2. **Modifying PR-Agent Sections**: Don't remove or modify the `pr_agent:summary` and `pr_agent:walkthrough` placeholders
3. **Adding Custom Sections**: Stick to the sections defined in the template
4. **Using Outdated Templates**: Always refer to the current `.github/pull_request_template.md` file

### Missing Sections

Always include all template sections, even if some are marked as "N/A" or "None"

## Additional GitHub CLI PR Commands

Here are some additional useful GitHub CLI commands for managing PRs:

```bash
# List your open pull requests
gh pr list --author "@me"

# Check PR status
gh pr status

# View a specific PR
gh pr view <PR-NUMBER>

# Check out a PR branch locally
gh pr checkout <PR-NUMBER>

# Convert a draft PR to ready for review
gh pr ready <PR-NUMBER>

# Add reviewers to a PR
gh pr edit <PR-NUMBER> --add-reviewer username1,username2

# Merge a PR
gh pr merge <PR-NUMBER> --squash
```

## Using Templates for PR Creation

To simplify PR creation with consistent descriptions, you can create a template file:

1. Create a file named `pr-template.md` with your PR template
2. Use it when creating PRs:

```bash
gh pr create --title "feat(scope): Your title" --body-file pr-template.md --base main --draft
```

## Related Documentation

- [PR Template](.github/pull_request_template.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub CLI documentation](https://cli.github.com/manual/)
