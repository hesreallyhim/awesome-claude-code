# Awesome Claude Code - Agent Deck

## How It Works

Each project gets a **persistent team lead** — a Claude Code session with Agent Teams enabled that manages work, spawns teammates, and tracks progress. You switch between projects with `agent-deck`.

```
You
├── agent-deck open deck-mirion      → Team Lead for Mirion
│   ├── teammate → "fix auth bug"        (own tmux pane)
│   ├── teammate → "run tests"           (own tmux pane)
│   └── tracks tasks, reports on check-in
│
├── agent-deck open deck-guidepoint  → Team Lead for Guidepoint
│   ├── teammate → "build API endpoint"  (own tmux pane)
│   └── teammate → "review PR"           (own tmux pane)
│
└── agent-deck list                  → status + task progress
```

See [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) for the full architecture.

## Quick Start

```bash
# Install (one-time)
curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash

# Set up projects
deck setup ~/mirion           # guided: detects stack, installs resources
deck setup ~/guidepoint       # same for another project

# Work
deck                          # dashboard (home base)
deck open mirion              # enter a project session
deck                          # (from inside a project) back to dashboard
deck open guidepoint          # enter another project
```

## Available Domains

| Domain | Resources Available |
|--------|---------------------|
| **Databricks/ML** | MLflow, Unity Catalog, DLT, Feature Engineering, Mosaic AI |
| **Data Engineering** | Pipelines, ETL, data quality |
| **APIs/Backend** | FastAPI, authentication, database patterns |
| **Frontend/Apps** | React, APX apps |
| **DevOps/Infra** | CI/CD, deployment, Docker |

## Core Principles (Always Apply)

### Development Workflow
1. **Understand first** - Read existing code before modifying
2. **Plan if complex** - Outline approach for multi-step tasks
3. **Implement incrementally** - One logical change at a time
4. **Test what you build** - Run tests before considering done
5. **Validate before commit** - Lint, type-check, build should pass

### Keep It Simple
- Don't add features beyond what's asked
- Don't create abstractions for one-time operations
- Don't over-engineer for hypothetical futures
- Three similar lines > premature abstraction

### Code Style
- Type hints for function signatures
- Format with project's formatter (ruff, black, prettier)
- Comments only where logic isn't self-evident
- Delete unused code completely

### Git Practices
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Never force push to main/master
- Stage specific files (avoid `git add -A`)
- One logical change per commit

## The Orchestrator (Team Lead)

When you `agent-deck open` a session, Claude Code starts as the **team lead** for that project. Agent Teams is enabled automatically.

### How to Orchestrate

When given a complex task, the team lead should:

1. **Plan the work** — Break it into a task DAG with dependencies
2. **Spawn a team** — Use `spawnTeam` to create the team
3. **Create tasks** — Use `TaskCreate` for each work item, with `blockedBy` for dependencies
4. **Spawn teammates** — Each teammate is a separate Claude Code process in its own tmux pane
5. **Coordinate** — Use direct messages (`write`) or `broadcast` to communicate
6. **Track progress** — Monitor the shared task list, unblock downstream work
7. **Report** — When the user checks in, summarize status

### When to Use Teammates vs. Subagents

| Use | For |
|-----|-----|
| **Agent Teams teammates** | Real implementation work — features, bug fixes, tests, deployments. Each gets its own context, tmux pane, and codebase access. |
| **Subagents (Task tool)** | Quick lookups — search for a file, read docs, analyze a diff. Results come back inline, no tmux pane needed. |

### Delegate Mode

Press `Shift+Tab` to enter delegate mode — the team lead coordinates only, no direct code changes. Use this for pure project management: spawn teammates, message them, manage tasks, approve plans.

### Check-In Protocol

When the user returns to a session after being away, immediately:

1. Read the task list (`~/.claude/tasks/<team>/`) for current status
2. Check the mailbox for any messages from teammates
3. Present a status summary:
   ```
   Status for <team>:
     ✓ Task 1 (description) — completed by worker-1
     ✓ Task 2 (description) — completed by worker-2
     → Task 3 (description) — in progress (worker-1)
     ○ Task 4 (description) — pending (blocked by 3)
     ✗ Task 5 (description) — needs attention: [reason]
   ```
4. Flag anything that needs user input or decision
5. Suggest next steps

### Quality Gates

Use hooks to enforce standards:
- **`TaskCompleted`** — exit code 2 blocks completion (e.g., "run tests before marking done")
- **`TeammateIdle`** — exit code 2 sends feedback to keep teammate working

## Commands

| Command | Purpose |
|---------|---------|
| `/start` | Interactive project setup - "What are we building?" |
| `/pick <resource>` | Pull specific resource into project |
| `/list-resources` | Browse all available resources |
| `/commit` | Structured commit workflow |
| `/review <file>` | Code review checklist |

## Resources

69 resources across three types, installed per-project during setup:

| Type | Location | Count | Purpose |
|------|----------|-------|---------|
| Slash commands | `.claude/commands/` | 31 | Workflow templates (commit, deploy, review, etc.) |
| CLAUDE.md templates | Appended to `CLAUDE.md` | 35 | Domain-specific instructions (MLflow, Databricks, FastAPI, etc.) |
| Workflow guides | Reference docs | 3 | Multi-step patterns (autonomous work, design review) |

Browse all: `/list-resources` or see `resources/` directory.

See [docs/INSTALL.md](docs/INSTALL.md) for installation details.
