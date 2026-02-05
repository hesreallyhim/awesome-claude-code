# Create Pull Request

Create a new branch, commit changes, and submit a pull request.

## Behavior

1. **Detect the project's formatter** and run it on modified files before committing
2. **Analyze changes** and split into logical commits when appropriate:
   - Split by feature, component, or concern
   - Keep related file changes together
   - Separate refactoring from feature additions
   - Each commit should be understandable independently
3. **Create descriptive commit messages** using conventional commit format
4. **Push branch** to remote
5. **Create pull request** using `gh pr create` with:
   - A clear title in conventional commit format
   - A summary of what changed and why
   - A test plan describing how to verify the changes

## Usage

```bash
# Basic -- creates PR from current branch
/create-pr

# With context
/create-pr "Add user authentication to API routes"
```

## Notes

- If a PR template exists at `.github/pull_request_template.md`, use it
- Start as draft (`--draft`) if work is still in progress
- All PR titles and descriptions should be in English
- See `/create-pull-request` for a detailed guide on GitHub CLI PR commands
