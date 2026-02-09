# Agent Deck Flow Review

## Mental Model Validation

**Your model:** tmux sessions are at the project level (like customer accounts), each containing Claude + orchestrated teams. Mirion is one tmux session, Guidepoint is another.

**Verdict: The implementation matches this model.** The code confirms a 1:1 mapping between projects and tmux sessions. Here's how it breaks down:

```
tmux session: deck-mirion          ← project-level container
├── window 0 (default)             ← Team Lead (Claude Code)
│   ├── spawnTeam("mirion", ...)
│   ├── spawnTeammate("worker-1")  ← tmux pane or window
│   └── spawnTeammate("worker-2")  ← tmux pane or window
├── window: agent-2                ← manually spawned via `agent-deck spawn`
└── window: agent-3                ← manually spawned via `agent-deck spawn`

tmux session: deck-guidepoint      ← separate project-level container
├── window 0 (default)             ← Team Lead (Claude Code)
└── ...
```

The "customer account" analogy is accurate. Each tmux session is an isolated boundary for one project. Everything inside — team lead, teammates, tasks, mailbox — belongs to that project.

---

## Architecture Layers (as implemented)

### Layer 1: Agent Deck (`agent-deck.sh`)
**Role:** Session switcher. Launches/kills/lists tmux sessions. Does NOT orchestrate work.

| Operation | What happens | Code reference |
|-----------|-------------|----------------|
| `setup ~/mirion` | Detects stack, asks domain/needs, installs resources, saves `.conf` | `agent-deck.sh:237-371` |
| `open deck-mirion` | Creates tmux session, sets `AGENT_TEAMS=1`, runs `claude` | `agent-deck.sh:374-411` |
| `spawn deck-mirion` | Adds a new tmux window with another `claude` instance | `agent-deck.sh:413-444` |
| `list` | Reads `.conf` files + task JSON, shows status | `agent-deck.sh:477-520` |
| `kill deck-mirion` | `tmux kill-session` | `agent-deck.sh:523-535` |

### Layer 2: Team Lead (Claude Code instance in window 0)
**Role:** Project brain. Plans work, spawns teammates, coordinates via mailbox, tracks tasks.

- Uses native Agent Teams (`spawnTeam`, `TaskCreate`, mailbox `write`/`broadcast`)
- Has project context: `CLAUDE.md`, `.claude/commands/`, conversation history
- Can use delegate mode (`Shift+Tab`) for pure coordination

### Layer 3: Teammates (spawned by Team Lead)
**Role:** Workers. Each is a separate `claude` process with own context and tmux pane.

- Get task assignments via mailbox
- Claim/complete tasks from shared task list at `~/.claude/tasks/<team>/`
- Communicate with lead and each other via `~/.claude/teams/<team>/inboxes/`

---

## Flow Accuracy Assessment

### What's correct and working

1. **tmux = project boundary** — `agent-deck.sh:407` creates one session per project (`tmux new-session -d -s "$name" -c "$project_dir"`). The session name is derived from the project directory (`agent-deck.sh:139-143`).

2. **Agent Teams env var propagation** — Set at both tmux session level and process level (`agent-deck.sh:408-409`):
   ```bash
   tmux set-environment -t "$name" CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1
   tmux send-keys -t "$name" "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude" Enter
   ```

3. **Session ↔ Team name mapping** — Derived by stripping the `deck-` prefix (`agent-deck.sh:148`). Stored in `.conf` as `TEAM_NAME`. Used to locate `~/.claude/tasks/<team>/` and `~/.claude/teams/<team>/`.

4. **Resource installation** — Commands go to `.claude/commands/`, templates append to `CLAUDE.md` with dedup markers (`agent-deck.sh:183-230`).

5. **Task status in `list`** — `get_team_task_summary()` reads task JSON files and counts status (`agent-deck.sh:447-474`).

6. **Filesystem coordination** — No daemon, no database. Tasks and messages are JSON files with fcntl locks.

### Inconsistencies found

| # | Issue | Where | Impact |
|---|-------|-------|--------|
| 1 | **SYSTEM_OVERVIEW.md says Agent Teams is NOT enabled by default** (line 298), but the code DOES enable it | `agent-deck.sh:408-409` vs `docs/SYSTEM_OVERVIEW.md:298` | Doc is stale — the code already does what the doc says is missing |
| 2 | **SYSTEM_OVERVIEW.md says session config doesn't store TEAM_NAME** (line 302), but the code DOES store it | `agent-deck.sh:157` vs `docs/SYSTEM_OVERVIEW.md:302` | Same — doc gap lists a problem that's already solved |
| 3 | **SYSTEM_OVERVIEW.md says `list` doesn't show task progress** (line 300), but the code DOES show it | `agent-deck.sh:506-510` vs `docs/SYSTEM_OVERVIEW.md:300` | Same pattern — doc is behind code |
| 4 | **Two spawn mechanisms exist but their relationship is unclear** | `agent-deck spawn` (manual, `agent-deck.sh:413-444`) vs Agent Teams `spawnTeammate` (automatic, native) | These create different kinds of windows — `agent-deck spawn` creates an independent Claude instance, while `spawnTeammate` creates a coordinated teammate with mailbox/task access. The docs don't clarify when to use which. |
| 5 | **`cmd_spawn` agents are not wired into Agent Teams** | `agent-deck.sh:435-436` | A manually spawned agent via `agent-deck spawn` gets a fresh `claude` process but doesn't join the team. It has no `--agent-id`, no `--team-name`, no mailbox. It's a lone wolf in the same tmux session. |

### Gaps in the flow

| # | Gap | Description |
|---|-----|-------------|
| 1 | **No orchestrator bootstrap prompt** | When `agent-deck open` launches Claude, it just runs `claude`. There's no initial prompt telling the team lead "you are an orchestrator for team X, check tasks, report status." The team lead behavior described in `CLAUDE.md` depends on the user's first message to activate it. |
| 2 | **Check-in protocol is aspirational** | `CLAUDE.md:104-120` describes a check-in protocol (read tasks, check mailbox, present status). But nothing triggers this on re-attach. When you `agent-deck open deck-mirion` and the session exists, it just does `tmux attach` — the Claude instance inside doesn't know you returned. |
| 3 | **No team name passed to Claude** | The team name is derived and stored in the `.conf`, but it's never communicated to the Claude instance. The team lead has to figure out its own team name, or the user has to tell it. |
| 4 | **Hooks referenced but not installed** | `CLAUDE.md` and `SYSTEM_OVERVIEW.md` mention `TaskCompleted` and `TeammateIdle` hooks, but `agent-deck setup` doesn't create any hook configurations. |
| 5 | **No recovery from tmux kill** | Session config persists, but conversation history doesn't survive `tmux kill`. Task/team state in `~/.claude/` does survive, so a re-opened session could theoretically resume from the task list — but the team lead starts fresh with no context about prior work. |

---

## Architecture Diagram (Actual)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER                                     │
│                                                                 │
│   agent-deck setup ~/mirion     →  Configure + install resources│
│   agent-deck open deck-mirion   →  Create/attach tmux session   │
│   agent-deck spawn deck-mirion  →  Add standalone agent window  │
│   agent-deck list               →  Show all sessions + tasks    │
│   agent-deck kill deck-mirion   →  Terminate session            │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│  tmux session: deck-mirion                                       │
│  Working dir: ~/mirion                                           │
│  Env: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1                     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  Window 0: Team Lead (claude)                           │     │
│  │                                                         │     │
│  │  Context:                                               │     │
│  │  ├── ~/mirion/CLAUDE.md (domain templates appended)     │     │
│  │  ├── ~/mirion/.claude/commands/ (slash commands)        │     │
│  │  └── Conversation history (volatile, lost on kill)      │     │
│  │                                                         │     │
│  │  Can do:                                                │     │
│  │  ├── spawnTeam("mirion", "...")                         │     │
│  │  ├── TaskCreate({ subject, blockedBy, ... })            │     │
│  │  ├── spawnTeammate("worker-1", { model, task })        │     │
│  │  ├── write("worker-1", "message")                      │     │
│  │  ├── broadcast("status update")                        │     │
│  │  └── Use subagents (Task tool) for quick lookups       │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌───────────────────────┐  ┌───────────────────────┐           │
│  │  Pane: worker-1       │  │  Pane: worker-2       │           │
│  │  (spawned by lead)    │  │  (spawned by lead)    │           │
│  │  --agent-id w1@mirion │  │  --agent-id w2@mirion │           │
│  │  --team-name mirion   │  │  --team-name mirion   │           │
│  │  Has mailbox access   │  │  Has mailbox access   │           │
│  │  Has task list access │  │  Has task list access │           │
│  └───────────────────────┘  └───────────────────────┘           │
│                                                                  │
│  ┌───────────────────────┐                                      │
│  │  Window: agent-2      │  ← from `agent-deck spawn`          │
│  │  (standalone claude)  │     NOT part of Agent Teams          │
│  │  No --agent-id        │     No mailbox, no task access       │
│  │  No --team-name       │     Independent context              │
│  └───────────────────────┘                                      │
└──────────────────────────────────────────────────────────────────┘

Shared State (filesystem):
  ~/.claude/tasks/mirion/        ← task DAG (JSON files + lock)
  ~/.claude/teams/mirion/        ← team config + mailbox inboxes
  ~/.agent-deck/sessions/        ← session configs (.conf files)
```

---

## Recommendations

### 1. Resolve the dual-spawn confusion (High priority)

`agent-deck spawn` and Agent Teams `spawnTeammate` create fundamentally different things:
- `spawnTeammate` → coordinated worker with mailbox, task access, team membership
- `agent-deck spawn` → independent Claude instance, no team integration

**Options:**
- (a) Remove `agent-deck spawn` entirely — let the team lead handle all spawning via Agent Teams
- (b) Wire `agent-deck spawn` into Agent Teams by passing `--agent-id`, `--team-name` flags
- (c) Rename to `agent-deck solo` to make the distinction clear, and document when each is useful

Recommendation: **(a)**. The team lead already handles spawning. Manual spawn adds confusion without clear benefit.

### 2. Update SYSTEM_OVERVIEW.md "What Needs Integration" table

Three of the five listed gaps are already resolved in code:
- Agent Teams IS enabled by default in `cmd_open` (lines 408-409)
- `TEAM_NAME` IS stored in session config (line 157)
- `list` DOES show task progress (lines 506-510)

The remaining two gaps are real:
- Team lead doesn't know it's an orchestrator (no bootstrap prompt)
- No check-in protocol on re-attach

### 3. Add orchestrator bootstrap prompt

When `cmd_open` launches Claude, pass an initial prompt:
```bash
tmux send-keys -t "$name" "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude --initial-prompt 'You are the team lead for $team_name. Check ~/.claude/tasks/$team_name/ for existing tasks and report status.'" Enter
```
Or inject orchestrator instructions into the project's `CLAUDE.md` during setup.

### 4. Wire check-in on re-attach

When `agent-deck open` finds an existing tmux session and attaches, it could send a message to the team lead's mailbox or use `tmux send-keys` to trigger a status check. Currently it just does `tmux attach` silently.

### 5. Install hooks during setup

`agent-deck setup` should create `TaskCompleted` and `TeammateIdle` hook stubs in the project's `.claude/settings.local.json` to enable the quality gates described in the docs.

---

## Summary

Your mental model is correct. The architecture cleanly maps:

| Your term | Implementation |
|-----------|---------------|
| Customer account / project | tmux session (`deck-mirion`) |
| Claude | Team Lead (first Claude Code instance in the session) |
| Orchestrated teams | Agent Teams teammates (spawned by team lead) |
| Another project (mirion) | Another tmux session (`deck-guidepoint`) |

The main structural risk is the `agent-deck spawn` command creating agents that look like teammates but aren't part of the Agent Teams coordination layer. The docs are also behind the code in several places. The flow itself — setup → open → work → switch → check-in — is sound and matches the implementation.
