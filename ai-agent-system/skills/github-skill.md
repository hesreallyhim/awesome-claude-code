# GitHub Skill

## Purpose
Create, manage, and publish code repositories on GitHub using `git` and `gh` CLI.

## Prerequisites
- `git` installed and configured (user.name, user.email)
- `gh` CLI authenticated: `gh auth login`
- SSH key or token for push access

## Workflows

### Create and Push New Repository
```
1. mkdir my-project && cd my-project
2. git init
3. Create README.md, .gitignore, code files
4. git add -A
5. git commit -m "feat: initial project — [description]"
6. gh repo create my-project --public --source=. --push --description "[desc]"
7. Verify: gh repo view --web
```

### Push Updates
```
1. git add -A
2. git commit -m "feat: [description]"
3. git push origin main
```

### Create a Release
```
1. git tag -a v1.0.0 -m "Release v1.0.0: [description]"
2. git push origin v1.0.0
3. gh release create v1.0.0 --title "v1.0.0" --notes "[notes]"
```

### Fork and Contribute
```
1. gh repo fork owner/repo --clone
2. git checkout -b feature/my-feature
3. Make changes, commit
4. git push origin feature/my-feature
5. gh pr create --title "Feature: [desc]" --body "[details]"
```

### Manage Issues
```
1. gh issue list
2. gh issue create --title "[title]" --body "[body]"
3. gh issue close NUMBER
```

## Commit Convention

| Prefix | Meaning |
|--------|---------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `style:` | Formatting |
| `refactor:` | Restructuring |
| `test:` | Tests |
| `chore:` | Maintenance |

## Code Snippets

### Quick Publish Script
```bash
#!/bin/bash
PROJECT="$1"
DESCRIPTION="$2"
git init
git add -A
git commit -m "feat: $DESCRIPTION"
gh repo create "$PROJECT" --public --source=. --push --description "$DESCRIPTION"
echo "Published: https://github.com/$(gh api user -q .login)/$PROJECT"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth error | Run `gh auth status`, re-login if needed |
| Push denied | Check SSH key or token permissions |
| Repo exists | Use `gh repo clone` instead |
| Rate limited | Check: `gh api rate_limit` |
