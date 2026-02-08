# Installing Resources into an Existing Project

This guide covers how to add awesome-claude-code resources to a project you're already working on.

## How It Works

There are two pieces:

1. **`install.sh`** — A one-liner that bootstraps the Agent Deck onto your machine
2. **Agent Deck** — The actual tool. Sets up sessions, installs resources, manages tmux agent windows. Has the guided setup built in.

```
install.sh (run once)
    └── installs → Agent Deck (~/.agent-deck/)
                        ├── agent-deck setup    ← guided setup (this is what you use)
                        ├── agent-deck open     ← open a session
                        ├── agent-deck spawn    ← add another agent window
                        └── agent-deck list     ← see all sessions
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
4. Preview recommended resources and confirm
5. Install everything into your project
6. Save a session config so you can reopen later

## What Gets Installed Where

| Resource Type | Destination |
|---|---|
| Slash commands | `.claude/commands/<name>.md` |
| CLAUDE.md templates | Appended to `CLAUDE.md` |
| Agent Deck | `~/.agent-deck/` (shared across projects) |
| Session configs | `~/.agent-deck/sessions/` (persist across restarts) |

## Sessions

A **session** is the core concept. It's scoped to a project folder, configured with the right resources, and can run multiple agent windows (each a Claude Code instance in tmux).

Session configs are stored as plain `.conf` files:

```ini
# Agent Deck Session: deck-my-model
# Created: 2026-02-08T12:00:00Z
PROJECT_DIR=/home/user/projects/my-model
DOMAIN=ml
NEEDS=git quality context
COMMANDS=commit context-prime create-pr feature-table mlflow-log-model optimize pr-review testing_plan_integration uc-register-model
TEMPLATES=DSPy MLflow-Databricks Feature-Engineering Vector-Search Mosaic-AI-Agents Databricks-AI-Dev-Kit
```

Sessions are:
- **Persistent** — configs survive tmux being killed; `open` re-creates from config
- **Multi-agent** — `spawn` adds agent windows to a running session
- **Self-contained** — resources are installed in the project dir, so any new agent window picks them up automatically via `.claude/commands/` and `CLAUDE.md`

## Agent Deck Commands

### `agent-deck setup [dir]` — Guided Setup

The primary command for setting up a project. Detects your stack, asks two questions, builds a resource list, installs everything, and saves a session config. If no directory given, uses the current directory.

### `agent-deck open <session>` — Open a Session

Attach to a running tmux session, or create one from the saved config. Starts Claude Code in the project directory.

```bash
agent-deck open deck-my-model
# → tmux session "deck-my-model" running claude in ~/projects/my-model
```

### `agent-deck spawn <session>` — Add an Agent Window

Add another Claude Code instance to a running session. Use this for parallel work — one agent on tests, another on implementation, a third on docs.

```bash
agent-deck spawn deck-my-model
# → new tmux window "agent-2" running claude
```

### `agent-deck list` — List Sessions

Show all saved sessions with their status (running/stopped), agent count, domain, and project path.

```
Sessions
  ● deck-my-model   (3 agents)  ml       ~/projects/my-model
  ● deck-api-v2     (1 agent)   backend  ~/projects/api-v2
  ○ deck-infra                   devops   ~/infra
```

### `agent-deck kill <session>` — Kill a Session

Terminate a running tmux session. The config persists — you can `open` it again later.

### `agent-deck` — Home Base

Interactive dashboard showing all sessions. Navigate between them, set up new projects, spawn agents.

## Session Lifecycle

Sessions are persistent configs — they survive tmux being killed. The `.conf` file remembers the project dir, domain, and resources. When you `open` a session, it re-creates the tmux session from the config.

Agents within a session spin up and down naturally:
- `spawn` adds agents when there's parallel work to do
- Individual windows close when their work is done
- The session config persists so you can always `open` it again
- Resources are already installed in the project — new agents pick them up automatically via `.claude/commands/` and `CLAUDE.md`

## What Gets Installed (Resource Catalog)

### Slash Commands

| Command | Purpose |
|---|---|
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
| ... | And more — domain-specific commands are recommended during setup |

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
