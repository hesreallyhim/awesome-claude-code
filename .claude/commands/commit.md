# Commit Changes

Create a well-structured commit for current changes.

## Steps

1. Run `git status` to see what's changed
2. Run `git diff --staged` (or `git diff` if nothing staged)
3. Stage appropriate files with `git add <file>` (avoid `git add -A`)
4. Write commit message:
   - Format: `type: short description`
   - Types: feat, fix, docs, refactor, test, chore
   - Under 72 characters
   - Imperative mood ("add" not "added")
5. If changes span unrelated concerns, suggest splitting
6. Run `git commit`
7. Show `git status` to confirm

## Examples

- `feat: add user authentication endpoint`
- `fix: handle null response from API`
- `refactor: extract validation logic`
- `docs: update setup instructions`
