# System Overview

How the Agent Deck actually works — and how it's supposed to work.

## The Core Idea

You're working on multiple projects at once. Maybe Mirion and Guidepoint. You want each project to have a **persistent AI orchestrator** that knows the project, manages work, spawns subagents for tasks, and keeps running while you focus elsewhere. You switch between them when you want to check in.

```
You
│
├── agent-deck switch mirion
│   └── Orchestrator (persistent Claude Code session)
│       ├── context: Mirion codebase, goals, what's in flight
│       ├── subagent → "refactor the ingestion pipeline"
│       ├── subagent → "fix failing tests in module X"
│       └── subagent → "draft PR for feature Y"
│
├── agent-deck switch guidepoint
│   └── Orchestrator (persistent Claude Code session)
│       ├── context: Guidepoint codebase, goals, what's in flight
│       ├── subagent → "build the API endpoint"
│       ├── subagent → "review the auth changes"
│       └── subagent → "run integration tests"
│
└── agent-deck → home base, status of everything
```

## Architecture: Three Layers

### Layer 1: Agent Deck (the session switcher)

`agent-deck.sh` is a bash script that manages sessions. It's the thing you interact with from the terminal.

**What it does:**
- Creates and stores session configs (project dir, domain, resources)
- Launches tmux sessions with Claude Code
- Lets you switch between projects
- Shows status of all running sessions

**What it is NOT:**
- It is not the orchestrator. It just launches orchestrators.
- It doesn't coordinate work. It's a launcher.

```bash
agent-deck setup ~/mirion        # configure + launch
agent-deck setup ~/guidepoint    # configure + launch
agent-deck list                  # see both running
agent-deck open deck-mirion      # switch to Mirion
agent-deck open deck-guidepoint  # switch to Guidepoint
```

### Layer 2: Orchestrator (one per session)

Each session has a **single Claude Code instance that acts as the orchestrator**. This is the brain of the session. It:

- Holds the full project context (what we're building, what's been done, what's blocked)
- Plans work and breaks it into tasks
- Spawns subagents for parallel execution
- Tracks progress across all subagents
- Reports status when you check in
- Persists across disconnections (tmux keeps it alive)

The orchestrator is a Claude Code session running in the primary tmux window. Its context includes:
- The project's `CLAUDE.md` (domain-specific instructions, coding standards)
- Installed slash commands in `.claude/commands/`
- The full conversation history (what you've asked, what's been done)

**Key behavior:** When you come back after being away, the orchestrator should be able to tell you:
- What subagents completed
- What's still running
- What's blocked and needs your input
- What it plans to do next

### Layer 3: Subagents (spawned by orchestrator)

Subagents are the workers. The orchestrator spawns them to do specific, scoped tasks. They:

- Receive a clear task from the orchestrator (e.g., "fix the auth bug in `src/auth.py`")
- Have access to the project codebase
- Use the installed slash commands and resources as tools
- Report results back to the orchestrator
- Are ephemeral — they spin up, do work, and finish

**How subagents are spawned today:**
Claude Code has a built-in `Task` tool that spawns subagents within the same session. The orchestrator uses this to delegate work:

```
Orchestrator (Claude Code) uses Task tool:
  → subagent: "Run the test suite and fix any failures"
  → subagent: "Refactor database.py to use connection pooling"
  → subagent: "Review the PR diff and write review comments"
```

These run as child processes of the orchestrator's Claude Code session. They share the filesystem but have isolated conversation contexts.

## How Sessions Work

### Session Lifecycle

```
1. SETUP
   agent-deck setup ~/mirion
   ├── detect project type (python, node, etc.)
   ├── ask: "what are you building?" → ML pipeline
   ├── ask: "what do you need?" → git workflow, testing, MLflow
   ├── install resources → .claude/commands/, CLAUDE.md
   └── save session config → ~/.agent-deck/sessions/deck-mirion.conf

2. LAUNCH
   agent-deck open deck-mirion
   ├── create tmux session
   ├── start Claude Code in project dir
   └── orchestrator boots with project context

3. WORK
   You → orchestrator: "Build the data ingestion pipeline"
   Orchestrator:
   ├── plans the work (breaks into tasks)
   ├── subagent → "create the schema definitions"
   ├── subagent → "write the ingestion logic"
   ├── subagent → "add tests"
   └── tracks progress, coordinates results

4. SWITCH AWAY
   agent-deck open deck-guidepoint
   (Mirion keeps running in background via tmux)

5. CHECK BACK IN
   agent-deck open deck-mirion
   Orchestrator: "Here's what happened while you were away..."

6. PERSIST
   Session config survives tmux restarts.
   agent-deck open deck-mirion recreates from config.
   (Conversation history is lost on tmux kill — this is a known gap.)
```

### Session Config

Stored in `~/.agent-deck/sessions/<name>.conf`:

```ini
PROJECT_DIR=/home/user/mirion
DOMAIN=ml
NEEDS=git quality context
COMMANDS=commit context-prime mlflow-log-model optimize pr-review
TEMPLATES=MLflow-Databricks Feature-Engineering
```

This tells agent-deck how to reconstruct the session environment. The resources are already installed in the project directory, so any new Claude Code instance picks them up automatically.

## Resources

Resources are the building blocks the orchestrator and subagents use. Three types:

### Slash Commands (`.claude/commands/*.md`)

Prompt templates that define specific workflows. When the orchestrator or a subagent runs `/commit`, Claude reads `.claude/commands/commit.md` and follows the instructions.

31 available commands across categories:
- **Git:** commit, create-pr, pr-review, fix-github-issue
- **Databricks/ML:** databricks-deploy, mlflow-log-model, feature-table, uc-register-model
- **Planning:** create-prd, plan-feature, structure-request
- **Quality:** optimize, debug-error, testing_plan_integration, review

### CLAUDE.md Templates

Domain-specific instructions appended to the project's `CLAUDE.md`. They give the orchestrator and subagents deep context about the domain. 35 templates available (MLflow, Databricks, DSPy, FastAPI, etc.).

### Workflow Guides

Longer documents covering multi-step workflows:
- **Autonomous Claude + Tmux:** Patterns for leave-your-computer autonomous work
- **Design Review:** Multi-phase design review agent methodology
- **Blogging Platform:** Content platform instructions

## What Works Today

| Component | Status | Notes |
|-----------|--------|-------|
| `agent-deck.sh` | Works | Session management, tmux launching, resource installation |
| `install.sh` | Works | One-line bootstrap |
| Session configs | Works | Persistent `.conf` files |
| Resources (69 total) | Works | Slash commands, templates, and guides exist |
| `.claude/commands/` | Works | 6 core commands defined |
| Orchestrator (manual) | Partially works | Claude Code in tmux holds context, can spawn subagents via Task tool |
| Multi-session switching | Works | tmux handles this |

## What's Missing

| Gap | Description | Impact |
|-----|-------------|--------|
| **Orchestrator auto-behavior** | No instructions telling the orchestrator to proactively manage work, track subagent status, or report progress on check-in | Orchestrator acts like a regular Claude session, not a project manager |
| **Subagent coordination** | No structured way for the orchestrator to track what subagents are doing, what completed, what failed | Orchestrator loses track of parallel work |
| **Session state persistence** | tmux kill loses conversation history — session config only stores resources, not work state | Coming back after tmux restart means starting fresh |
| **Status dashboard** | `agent-deck list` shows session names but not what work is in progress | No way to see "Mirion: 3 tasks done, 1 blocked" from home base |
| **Orchestrator bootstrap prompt** | No standard prompt that initializes the orchestrator with "you are the project manager for this session" behavior | Each session starts as a blank Claude instance |

## Next Steps

To close the gap between what exists and the vision:

1. **Orchestrator system prompt** — A CLAUDE.md section or bootstrap command that tells Claude "you are the orchestrator for this project, here's how you manage work, track subagents, and report status."

2. **Subagent tracking** — A convention for the orchestrator to maintain a task list (using TodoWrite or a project file) that tracks spawned subagents and their status.

3. **Check-in protocol** — When the user re-attaches to a session, the orchestrator summarizes what happened since they left.

4. **agent-deck status enrichment** — Pull task status from each session's tracking file so `agent-deck list` shows meaningful progress.

5. **Session state file** — A `.agent-deck-state.md` or similar in the project dir that the orchestrator writes to, surviving tmux restarts. New orchestrator instances read this to resume context.
