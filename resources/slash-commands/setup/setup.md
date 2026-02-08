# Project Setup

Guided setup for adding awesome-claude-code resources to this project.

This command is an alias for `/deck setup`. It inspects your project, asks what you're building and what you need, then creates a collection and installs the right resources.

## Flow

1. **Inspect** the current project (language, framework, existing config)
2. **Ask** what you're building (ML, backend, frontend, etc.)
3. **Ask** what you need (git workflow, code quality, docs, etc.)
4. **Preview** the recommended resources
5. **Save** the collection to `~/.agent-deck/collections/`
6. **Install** commands to `.claude/commands/` and templates to `CLAUDE.md`

## Implementation

Run this as if the user typed `/deck setup`. Follow the `/deck` command's `setup` section exactly.

If the `/deck` command is not available in this project, perform the same guided flow inline:

1. Read the project's top-level files to detect language/framework
2. Ask: **"What best describes your project?"** (ML, Data Eng, Backend, Frontend, DevOps, CLI, General)
3. Ask: **"What would help you most?"** (Git workflow, Code quality, Project context, Documentation, Deployment, Everything)
4. Build a resource list using the same domain/needs mappings as `/deck`
5. Clone `https://github.com/hesreallyhim/awesome-claude-code.git` to a temp location if `~/.agent-deck/cache/` doesn't exist
6. Copy resources to this project
7. Summarize what was installed

Begin now. Inspect the project first, then greet the user.
