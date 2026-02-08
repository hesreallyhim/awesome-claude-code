# System Overview

How the Agent Deck works.

## The Core Idea

You're working on multiple projects at once — Mirion and Guidepoint. Each project gets a persistent orchestrator (a Claude Code team lead) that manages work, spawns Agent Teams teammates as workers, and keeps running while you focus elsewhere. You switch between projects to check in.

```
You
│
├── agent-deck open deck-mirion
│   └── Team Lead (persistent Claude Code session)
│       ├── teammate → "refactor ingestion pipeline"   ← own tmux pane
│       ├── teammate → "fix failing tests"             ← own tmux pane
│       └── teammate → "draft PR for feature Y"        ← own tmux pane
│       Tasks: ~/.claude/tasks/mirion/
│       Mailbox: ~/.claude/teams/mirion/inboxes/
│
├── agent-deck open deck-guidepoint
│   └── Team Lead (persistent Claude Code session)
│       ├── teammate → "build the API endpoint"
│       ├── teammate → "review the auth changes"
│       └── teammate → "run integration tests"
│       Tasks: ~/.claude/tasks/guidepoint/
│       Mailbox: ~/.claude/teams/guidepoint/inboxes/
│
└── agent-deck list → status across everything
```

## Architecture: Three Layers

### Layer 1: Agent Deck (the session switcher)

`agent-deck.sh` is a bash script. It manages sessions — nothing more. It launches orchestrators, lets you switch between projects, and shows you status.

**What it does:**
- Creates and stores session configs (project dir, domain, installed resources)
- Launches tmux sessions with Claude Code as team lead
- Switches between projects
- Shows status of all running sessions
- Enables Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)

**What it is NOT:**
- Not the orchestrator. It just launches them.
- Doesn't coordinate work. Doesn't touch tasks or messages.

```bash
agent-deck setup ~/mirion        # configure + launch
agent-deck setup ~/guidepoint    # same for another project
agent-deck list                  # see both running
agent-deck open deck-mirion      # switch to Mirion
agent-deck open deck-guidepoint  # switch to Guidepoint
```

### Layer 2: Orchestrator / Team Lead (one per session)

Each session has a **Claude Code instance acting as the team lead**. This is the brain of the project. It uses the native Agent Teams feature (`spawnTeam`) to create a team and coordinate work.

**The team lead:**
- Holds project context (what we're building, what's been done, what's blocked)
- Plans work and breaks it into tasks (DAG with dependencies)
- Spawns teammates to do the actual work
- Coordinates via the mailbox (direct messages and broadcasts)
- Approves or rejects teammate plans (when `planModeRequired` is set)
- Tracks progress via the shared task list
- Reports status when you check back in
- Can operate in **delegate mode** (`Shift+Tab`) — pure coordination, no direct code changes

**The team lead's context includes:**
- The project's `CLAUDE.md` (domain-specific instructions, coding standards)
- Installed slash commands in `.claude/commands/`
- The full conversation history
- The shared task list (`~/.claude/tasks/<team>/`)
- The mailbox (`~/.claude/teams/<team>/inboxes/`)

### Layer 3: Teammates / Workers (spawned by team lead)

Teammates are the workers. Each is a **separate Claude Code process** with its own context window, running in its own tmux pane. They are spawned by the team lead using Agent Teams.

**Each teammate:**
- Gets a specific task assignment via the mailbox
- Has full access to the project codebase
- Works independently in its own context
- Communicates with the team lead (and other teammates) via messages
- Claims and completes tasks from the shared task list
- Can be shut down by the team lead when done

**How teammates are spawned:**

The team lead uses the TeammateTool to spawn workers. Under the hood, each teammate is a `claude` CLI process launched with internal flags:

```bash
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude \
  --agent-id worker-1@mirion \
  --agent-name worker-1 \
  --team-name mirion \
  --agent-color blue \
  --parent-session-id <lead-uuid> \
  --agent-type general-purpose \
  --model sonnet
```

Each teammate appears as a tmux split pane (or a separate window). You can see all their output at once.

## The Agent Teams Protocol

Agent Teams is a native Claude Code feature. The coordination is filesystem-based — no database, no daemon, no network layer. Just JSON files.

### Tasks

Stored in `~/.claude/tasks/<team-name>/`:

```
~/.claude/tasks/mirion/
├── .lock          # fcntl lock for atomic operations
├── 1.json         # "Set up database schema"     → completed
├── 2.json         # "Build ingestion pipeline"   → in_progress (worker-1)
├── 3.json         # "Write integration tests"    → pending (blocked by 2)
└── 4.json         # "Deploy to staging"          → pending (blocked by 2, 3)
```

Each task file:
```json
{
  "id": "2",
  "subject": "Build ingestion pipeline",
  "description": "Implement the data ingestion from S3...",
  "activeForm": "Building ingestion pipeline",
  "status": "in_progress",
  "owner": "worker-1",
  "blocks": ["3", "4"],
  "blockedBy": ["1"]
}
```

Tasks form a DAG. When task 1 completes, tasks that depend on it automatically unblock. Status can only move forward: `pending → in_progress → completed`. Cycle detection prevents impossible dependency chains.

### Mailbox

Stored in `~/.claude/teams/<team-name>/inboxes/`:

```
~/.claude/teams/mirion/inboxes/
├── .lock              # Shared lock
├── team-lead.json     # Lead's inbox
├── worker-1.json      # Worker 1's inbox
└── worker-2.json      # Worker 2's inbox
```

Message types:
- **Direct messages** — team lead → teammate, or teammate → team lead
- **Broadcasts** — team lead → all teammates
- **Task assignments** — auto-sent when a task's `owner` is set
- **Shutdown requests/approvals** — graceful shutdown handshake
- **Plan approvals/rejections** — team lead reviews teammate plans

### Team Config

Stored in `~/.claude/teams/<team-name>/config.json`:
```json
{
  "name": "mirion",
  "description": "Mirion data platform",
  "leadAgentId": "team-lead@mirion",
  "leadSessionId": "a1b2c3d4-...",
  "members": [
    { "name": "team-lead", "agentType": "team-lead", "model": "claude-opus-4-6" },
    { "name": "worker-1", "agentType": "general-purpose", "model": "sonnet", "color": "blue", "tmuxPaneId": "%42" },
    { "name": "worker-2", "agentType": "general-purpose", "model": "sonnet", "color": "green", "tmuxPaneId": "%43" }
  ]
}
```

## How Sessions Work

### Session Lifecycle

```
1. SETUP
   agent-deck setup ~/mirion
   ├── detect project type (python, node, etc.)
   ├── ask: "what are you building?" → ML pipeline
   ├── ask: "what do you need?" → git workflow, testing, MLflow
   ├── install resources → .claude/commands/, CLAUDE.md
   ├── enable Agent Teams (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)
   └── save session config → ~/.agent-deck/sessions/deck-mirion.conf

2. LAUNCH
   agent-deck open deck-mirion
   ├── create tmux session
   ├── start Claude Code in project dir (this becomes team lead)
   └── team lead boots with project context + Agent Teams enabled

3. WORK
   You → team lead: "Build the data ingestion pipeline"
   Team lead:
   ├── spawnTeam("mirion", "Mirion data platform")
   ├── creates task DAG:
   │   task 1: "Set up database schema"
   │   task 2: "Build ingestion logic" (blocked by 1)
   │   task 3: "Write tests" (blocked by 2)
   │   task 4: "Deploy to staging" (blocked by 2, 3)
   ├── spawns teammate worker-1 → assigns task 1
   ├── spawns teammate worker-2 → assigns task 2 (waits for 1)
   └── coordinates via mailbox, tracks progress via task list

4. SWITCH AWAY
   agent-deck open deck-guidepoint
   (Mirion keeps running in background — tmux + Agent Teams persist)

5. CHECK BACK IN
   agent-deck open deck-mirion
   Team lead: "Here's what happened:
     ✓ Task 1 (schema) — completed by worker-1
     ✓ Task 2 (ingestion) — completed by worker-2
     → Task 3 (tests) — in progress, worker-1 picked it up
     ○ Task 4 (deploy) — pending, waiting on task 3"

6. PERSIST
   Session config survives tmux restarts.
   Task and team state survive in ~/.claude/tasks/ and ~/.claude/teams/.
   Conversation history is lost on tmux kill (known limitation).
```

### Agent Teams vs. Subagents (Task tool)

Both are available. They serve different purposes:

| | Subagents (Task tool) | Agent Teams (teammates) |
|---|---|---|
| **Context** | Shares parent's context, returns results back | Own context window, fully independent |
| **Communication** | One-way: result goes back to caller | Two-way: mailbox messaging between all agents |
| **Coordination** | Parent manages everything | Shared task list, teammates self-coordinate |
| **Visibility** | Hidden — runs inside parent's process | Visible — each gets a tmux pane |
| **Best for** | Quick, focused lookups (search, read, analyze) | Real work (implement features, fix bugs, write tests) |
| **Cost** | Lower (results summarized back) | Higher (each is a full Claude instance) |

The team lead can use **both**: subagents for quick research/analysis, Agent Teams teammates for actual implementation work.

### Session Config

Stored in `~/.agent-deck/sessions/<name>.conf`:

```ini
PROJECT_DIR=/home/user/mirion
DOMAIN=ml
NEEDS=git quality context
COMMANDS=commit context-prime mlflow-log-model optimize pr-review
TEMPLATES=MLflow-Databricks Feature-Engineering
```

This tells agent-deck how to reconstruct the session environment. Resources are installed in the project directory, so any new Claude Code instance picks them up automatically via `.claude/commands/` and `CLAUDE.md`.

## Resources

Resources are the building blocks the team lead and teammates use. Three types:

### Slash Commands (`.claude/commands/*.md`)

Prompt templates that define workflows. When anyone in the team runs `/commit`, Claude reads `.claude/commands/commit.md` and follows the instructions.

31 available commands across categories:
- **Git:** commit, create-pr, pr-review, fix-github-issue
- **Databricks/ML:** databricks-deploy, mlflow-log-model, feature-table, uc-register-model
- **Planning:** create-prd, plan-feature, structure-request
- **Quality:** optimize, debug-error, testing_plan_integration, review

### CLAUDE.md Templates

Domain-specific instructions appended to the project's `CLAUDE.md`. They give the team lead and teammates deep context about the domain. 35 templates available (MLflow, Databricks, DSPy, FastAPI, etc.).

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
| Agent Teams (native) | Works | Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| Multi-session switching | Works | tmux handles this |

## What Needs Integration

The pieces exist separately — they need to be wired together:

| Gap | Description | Fix |
|-----|-------------|-----|
| **Agent Teams not enabled by default** | `agent-deck open` doesn't set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | Set the env var when launching Claude Code in tmux |
| **Team lead doesn't know it's an orchestrator** | No instructions in CLAUDE.md telling the team lead to use Agent Teams for coordination | Add orchestrator behavior to CLAUDE.md or a bootstrap command |
| **agent-deck doesn't read team state** | `agent-deck list` shows session names but not task progress | Read `~/.claude/tasks/<team>/` to show task counts and status |
| **No check-in protocol** | Team lead doesn't proactively summarize progress on re-attach | Add instructions for check-in behavior to the orchestrator prompt |
| **Session ↔ Team mapping** | Session config doesn't store the Agent Teams team name | Add `TEAM_NAME` to `.conf` so agent-deck can find the right `~/.claude/teams/` directory |

## Enabling Agent Teams

To enable the Agent Teams feature:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or per-session via the environment variable:
```bash
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude
```

### Display Modes

- **In-process** (default): Teammates run inside your terminal. `Shift+Up/Down` to select, `Enter` to view, `Escape` to interrupt.
- **Split-pane** (tmux/iTerm2): Each teammate gets its own pane. See everyone's output at once.

### Delegate Mode

Press `Shift+Tab` to put the team lead in delegate mode — coordination only, no direct code changes. The lead can only spawn teammates, message them, manage tasks, and approve/reject plans. This is the pure project-manager mode.

### Hooks

Two hooks are available for quality control:
- **`TeammateIdle`** — runs when a teammate is about to go idle. Exit code 2 keeps them working.
- **`TaskCompleted`** — runs when a task is marked complete. Exit code 2 blocks completion (e.g., "run tests first").

### Known Limitations

- No session resumption with in-process teammates (`/resume` doesn't restore teammates)
- One team per session
- No nested teams (teammates can't spawn their own teams)
- Lead is fixed (can't promote a teammate)
- Split panes require tmux or iTerm2 (not VS Code terminal, Windows Terminal, or Ghostty)
