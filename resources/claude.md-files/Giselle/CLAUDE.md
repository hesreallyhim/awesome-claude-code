# Development Philosophy

## Core Principle: **Less is more**
Keep every implementation as small and obvious as possible.

## Guidelines
- **Simplicity first** – Prefer the simplest data structures and APIs that work
- **Avoid needless abstractions** – Refactor only when duplication hurts
- **Remove dead code early** – `pnpm tidy` scans for unused files/deps and lets you delete them in one command
- **Minimize dependencies** – Before adding a dependency, ask "Can we do this with what we already have?"
- **Consistency wins** – Follow existing naming and file-layout patterns; if you must diverge, document why
- **Explicit over implicit** – Favor clear, descriptive names and type annotations over clever tricks
- **Fail fast** – Validate inputs, throw early, and surface actionable errors
- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious

# REQUIRED COMMANDS AFTER CODE CHANGES
**IMMEDIATE ACTION REQUIRED: After using `edit_file` tool:**

1. Run `pnpm format`
2. Run `pnpm build-sdk`
3. Run `pnpm check-types`
4. Run `pnpm tidy`
5. Run `pnpm test`

**These commands are part of the `edit_file` operation itself.**

(CI also runs these steps; your PR will fail if any step fails.)


# Pull Request Guidelines

## When to Create a Pull Request
- **Create PRs in meaningful minimum units** - even 1 commit or ~20 lines of diff is fine
- Feature Flags protect unreleased features, so submit PRs for any meaningful unit of work
- After PR submission, create a new branch from the current branch and continue development

## What Constitutes a "Meaningful Unit"
- Any UI change (border color, text color, size, etc.)
- Function renames or folder structure changes
- Any self-contained improvement or fix

## Size Guidelines
- **~500 lines**: Consider wrapping up current work for a PR
- **1000 lines**: Maximum threshold - avoid exceeding this
- Large diffs are acceptable when API + UI changes are coupled, but still aim to break down when possible


# Bash commands
- pnpm build-sdk: build the SDK packages
- pnpm -F playground build: build the playground app
- pnpm -F studio.giselles.ai build: build Giselle Cloud
- pnpm check-types: type‑check the project
- pnpm format: format code
- pnpm tidy --fix: delete unused files/dependencies
- pnpm tidy: diagnose unused files/dependencies
- pnpm test: run tests


# Language Support
- Some core members are non‑native English speakers.
- Please correct grammar in commit messages, code comments, and PR discussions.
- Rewrite unclear user input when necessary to ensure smooth communication.
