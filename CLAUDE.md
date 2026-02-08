# Awesome Claude Code - Interactive Toolkit

## What Are We Building?

Use `/start` to begin an interactive session that configures this project based on what you're building.

```
/start

→ "What are we building today?"
→ You: "ML pipeline on Databricks"
→ "Which area?" (MLflow, DLT, Feature Store, etc.)
→ "What style of help?" (hands-on coding, architecture review, debugging)
→ Pulls in relevant resources automatically
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

## Commands

| Command | Purpose |
|---------|---------|
| `/start` | Interactive project setup - "What are we building?" |
| `/pick <resource>` | Pull specific resource into project |
| `/list-resources` | Browse all available resources |
| `/commit` | Structured commit workflow |
| `/review <file>` | Code review checklist |

## Resources

Browse `/resources/` for domain-specific content:

```
resources/
├── claude.md-files/        # Project templates
│   ├── Databricks-Full-Stack/
│   ├── DSPy/
│   ├── MLflow/
│   └── ...
├── slash-commands/         # Reusable commands
│   ├── commit/
│   ├── pr-review/
│   ├── optimize/
│   └── ...
└── workflows-knowledge-guides/
```

## Adding Resources to an Existing Project

Two options for adding resources to a project you're already working on:

### Option 1: Bash installer (bootstrapper)

From your project directory:
```bash
curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash
```

The installer detects your project type, asks what you're building and what you need, then recommends and installs tailored resources. It also installs the `/setup` command for future use.

### Option 2: `/setup` command (agent-driven)

If you already have the `/setup` command in your project (installed by the bash script or copied manually), run it in Claude Code for a richer guided experience:

```
/setup
```

Claude will inspect your project, ask guided questions, and recommend the right mix of slash commands and CLAUDE.md templates.

See [docs/INSTALL.md](docs/INSTALL.md) for the full installation guide.

### Option 3: Agent Deck (collection manager + tmux sessions)

For managing multiple projects with saved resource collections:
```bash
bash install.sh --deck
```

Or from Claude Code: `/deck`

The Agent Deck lets you create named collections (e.g., "ml-pipeline"), install them to any directory, and spawn tmux sub-sessions — each running its own Claude Code instance. See [docs/INSTALL.md](docs/INSTALL.md) for details.

## Quick Start Examples

**Databricks ML Project:**
```
/start
→ "Databricks ML pipeline"
→ Adds: MLflow patterns, Unity Catalog, testing strategy
```

**API Development:**
```
/start
→ "FastAPI backend"
→ Adds: API patterns, authentication, database access
```

**Just exploring:**
```
/list-resources
/pick slash-commands/optimize
```
