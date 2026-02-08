# Installing Resources into an Existing Project

This guide covers how to add awesome-claude-code resources to a project you're already working on.

## How It Works

There are two pieces:

1. **`install.sh`** — A one-liner that bootstraps the Agent Deck onto your machine
2. **Agent Deck** — The actual tool. Creates collections, installs resources, manages tmux sessions. Has the guided setup built in.

```
install.sh (run once)
    └── installs → Agent Deck (~/.agent-deck/)
                        ├── agent-deck setup    ← guided setup (this is what you use)
                        ├── agent-deck new      ← create a collection
                        ├── agent-deck install  ← install to a project
                        └── agent-deck launch   ← spawn tmux sub-session
```

## Quick Start

```bash
# 1. Install the Agent Deck (one-time)
curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash

# 2. Add the alias it suggests
alias agent-deck='bash ~/.agent-deck/agent-deck.sh'

# 3. Set up your project (guided)
cd ~/my-project
agent-deck setup
```

The `setup` command will:
1. Detect your project type (language, framework, existing config)
2. Ask what you're building (ML, backend, frontend, etc.)
3. Ask what you need (git workflow, code quality, docs, etc.)
4. Create a named collection with the right resources
5. Install everything into your project

Or from Claude Code:
```
/deck setup
```

## What Gets Installed Where

| Resource Type | Destination |
|---|---|
| Slash commands | `.claude/commands/<name>.md` |
| CLAUDE.md templates | Appended to `CLAUDE.md` |
| Agent Deck | `~/.agent-deck/` (shared across projects) |
| Collections | `~/.agent-deck/collections/` (reusable) |

## Agent Deck Commands

### `agent-deck setup [dir]` — Guided Setup

The primary command for setting up a project. Detects your stack, asks two questions, creates a collection, and installs resources. If no directory given, uses the current directory.

### `agent-deck new [dir]` — Create a Collection

Same guided Q&A as `setup`, but just saves the collection without installing. Useful if you want to create a collection first and install it to multiple projects later.

If a directory is provided, the project is inspected to pre-suggest the domain.

### `agent-deck install <collection> [dir]` — Install a Collection

Apply a saved collection to a project directory. If no directory given, uses the current directory.

```bash
agent-deck install ml-pipeline ~/projects/my-model
agent-deck install api-service .
```

### `agent-deck launch <path>` — Spawn a Sub-Session

Create a tmux session for a project directory and start Claude Code in it.

```bash
agent-deck launch ~/projects/my-model
# → tmux session "deck-my-model" running claude
```

### `agent-deck` — Home Base

Interactive dashboard showing collections, active sessions, and discovered projects. Navigate between them.

### `agent-deck list` / `agent-deck status`

List saved collections or show active tmux sessions.

## Collections

A collection is a named set of resources tailored to a project type. It's stored as a plain `.conf` file:

```ini
# Agent Deck Collection: ml-pipeline
# Created: 2026-02-08T12:00:00Z
DOMAIN=ml
NEEDS=git quality context
COMMANDS=commit context-prime create-pr deck feature-table mlflow-log-model optimize pr-review testing_plan_integration uc-register-model
TEMPLATES=DSPy MLflow-Databricks Feature-Engineering Vector-Search Mosaic-AI-Agents Databricks-AI-Dev-Kit
```

Collections are:
- **Reusable** — install the same collection to multiple projects
- **Portable** — share `.conf` files with your team
- **Saved** — in `~/.agent-deck/collections/`, persist across sessions

## Claude Code Integration

The installer also copies `/deck` into your project's `.claude/commands/`, giving you the full Agent Deck experience within Claude Code:

```
/deck                    Home dashboard
/deck setup              Guided project setup
/deck new                Create a collection
/deck install <name>     Install a collection
/deck launch <path>      Spawn a tmux session
/deck status             Show active sessions
```

`/setup` is also available as a shortcut for `/deck setup`.

## What Gets Installed (Resource Catalog)

### Slash Commands

| Command | Purpose |
|---|---|
| `/deck` | Agent Deck — collection manager + session launcher |
| `/setup` | Guided project setup (alias for `/deck setup`) |
| `/commit` | Conventional commit workflow |
| `/pr-review` | Multi-perspective code review |
| `/optimize` | Performance analysis |
| `/context-prime` | Prime Claude with project context |
| `/create-pr` | Create pull requests |
| `/fix-github-issue` | Issue-driven development |
| `/testing_plan_integration` | Testing strategy |
| `/release` | Release management |
| `/update-docs` | Documentation updates |
| `/add-to-changelog` | Changelog management |
| `/mlflow-log-model` | MLflow model logging |
| `/databricks-deploy` | Deploy to Databricks |
| `/databricks-job` | Manage Databricks jobs |
| ... | And more — run `agent-deck new` to see domain-specific options |

### CLAUDE.md Templates

34 project-specific templates covering ML, Databricks, backend, frontend, DevOps, and more. The guided setup recommends the right ones for your stack.

## Removing Resources

```bash
# Remove a slash command
rm .claude/commands/commit.md

# Remove a template section from CLAUDE.md
# Find and delete between "# --- awesome-claude-code: <name> ---" markers

# Uninstall the Agent Deck entirely
rm -rf ~/.agent-deck
```

## Updating

Re-run `agent-deck setup` to get the latest resources. The deck auto-updates its cache when it's more than a day old.
