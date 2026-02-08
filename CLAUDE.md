# Awesome Claude Code - Agent Deck

## How It Works

Each project gets a **persistent orchestrator** — a Claude Code session that manages work, spawns subagents, and tracks progress. You switch between projects with `agent-deck`.

```
You
├── agent-deck open deck-mirion      → Orchestrator for Mirion
│   ├── subagent → "fix auth bug"
│   ├── subagent → "run tests"
│   └── tracks progress, reports on check-in
│
├── agent-deck open deck-guidepoint  → Orchestrator for Guidepoint
│   ├── subagent → "build API endpoint"
│   └── subagent → "review PR"
│
└── agent-deck list                  → status of everything
```

See [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) for the full architecture.

## Quick Start

```bash
# Install (one-time)
curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash
alias agent-deck='bash ~/.agent-deck/agent-deck.sh'

# Set up a project
agent-deck setup ~/mirion           # guided: detects stack, installs resources
agent-deck setup ~/guidepoint       # same for another project

# Work
agent-deck open deck-mirion         # orchestrator session
agent-deck open deck-guidepoint     # switch projects
agent-deck list                     # see all sessions
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

## The Orchestrator

When you `agent-deck open` a session, Claude Code starts as the **orchestrator** for that project. The orchestrator:

- Knows the project context (codebase, domain, what's been done)
- Plans work and breaks it into tasks
- Spawns subagents via the Task tool for parallel execution
- Tracks progress and reports status when you check back in
- Uses installed slash commands (`/commit`, `/pr-review`, `/optimize`, etc.)

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
