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

### Step 1: Install the Agent Deck

From your project directory:
```bash
curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash
```

This installs the Agent Deck (`~/.agent-deck/agent-deck.sh`) and the `/deck` slash command.

### Step 2: Set Up Your Project

**From the terminal:**
```bash
agent-deck setup              # Guided setup for current directory
agent-deck setup ~/my-project # ...or specify a path
```

**From Claude Code:**
```
/deck setup
```

Both paths do the same thing: detect your project, ask what you're building and what you need, create a collection, and install the right resources.

### Ongoing: Manage Collections + Sessions

```bash
agent-deck                    # Home base — collections, sessions, projects
agent-deck new                # Create a reusable collection
agent-deck install <name> .   # Apply a collection to a directory
agent-deck launch <path>      # Spawn a Claude Code tmux sub-session
```

See [docs/INSTALL.md](docs/INSTALL.md) for the full guide.

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
