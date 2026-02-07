# Autonomous Workflows: Leave Your Computer Running

Patterns for fully autonomous Claude Code execution where you can walk away for hours and return to completed work.

## The Core Pattern

The key insight: tmux sessions persist on the server regardless of your connection. Claude Code continues executing inside the tmux pane even when you detach or lose connectivity.

```
1. Start tmux session
2. Launch Claude Code with a clear task
3. Detach (Ctrl+a d) or close your laptop
4. Come back hours later
5. Reattach (tmux attach -t <session>)
6. Review completed work
```

## Workflow 1: Overnight Refactoring

Start a large refactoring task before leaving for the day:

```bash
# Create a dedicated session
tmux new -s refactor -c ~/projects/my-app

# Start Claude Code and give it the task
claude

# Inside Claude: describe the full refactoring scope
# e.g., "Migrate all class components to functional components with hooks.
#        Run tests after each file. Commit after each successful migration."

# Detach and go home
# Ctrl+a d
```

Come back the next morning:
```bash
tmux attach -t refactor
# Review what Claude accomplished overnight
```

## Workflow 2: Autonomous Test Suite Fixing

Let Claude work through a failing test suite:

```bash
tmux new -s test-fixes -c ~/projects/my-app

# Start Claude with a directive
claude

# Inside Claude: "Run the full test suite. For each failing test,
#                 analyze the failure, fix the underlying code,
#                 and re-run to verify. Commit each fix separately."

# Detach
# Ctrl+a d
```

## Workflow 3: Codebase Migration

Large-scale migrations that take significant time:

```bash
tmux new -s migration -c ~/projects/my-app

claude

# Inside Claude: "Migrate the entire codebase from JavaScript to TypeScript.
#                 Process one file at a time. Add proper type annotations.
#                 Run tsc after each file to verify no type errors.
#                 Commit each completed file."

# Detach and check back periodically
# Ctrl+a d

# Check progress from anywhere (even your phone via SSH)
tmux attach -t migration
```

## Workflow 4: The Daily Dashboard

A persistent development environment you keep running all week:

```bash
#!/bin/bash
# daily-claude.sh

SESSION="daily"

# Only create if session doesn't exist
tmux has-session -t "$SESSION" 2>/dev/null
if [ $? != 0 ]; then
    tmux new-session -d -s "$SESSION"
    tmux rename-window -t "$SESSION:0" 'Claude'
    tmux new-window -t "$SESSION:1" -n 'Monitor'
    tmux new-window -t "$SESSION:2" -n 'Shell'

    tmux send-keys -t "$SESSION:0" 'claude' Enter
fi

tmux attach-session -t "$SESSION"
```

Morning routine:
1. `tmux attach -t daily` - Resume yesterday's session
2. Claude's context is preserved from the previous day
3. Continue exactly where you left off

## Workflow 5: Parallel Claude Instances

Run multiple Claude Code instances on different parts of a project:

```bash
# Frontend work
tmux new -s frontend -c ~/projects/my-app/frontend
# Start claude, give it frontend tasks, detach

# Backend work
tmux new -s backend -c ~/projects/my-app/backend
# Start claude, give it backend tasks, detach

# Infrastructure
tmux new -s infra -c ~/projects/my-app/infra
# Start claude, give it IaC tasks, detach

# Check on all of them
tmux ls
# frontend: 1 windows (created ...)
# backend: 1 windows (created ...)
# infra: 1 windows (created ...)

# Jump into any one
tmux attach -t backend
```

## Tips for Reliable Autonomous Operation

### 1. Give Clear, Scoped Instructions
The more specific the task description, the better Claude performs autonomously:

```
Good:  "Migrate src/components/*.jsx to TypeScript. Add strict types.
        Run `npm run typecheck` after each file. Commit each file separately
        with message format 'feat: migrate <filename> to TypeScript'."

Bad:   "Convert everything to TypeScript."
```

### 2. Set Up Commit Checkpoints
Ask Claude to commit frequently so you can review incremental progress:

```
"After completing each module, run tests and commit with a descriptive message.
 If tests fail, fix them before moving on."
```

### 3. Use Large Scrollback
Ensure you can review everything Claude did while you were away:

```bash
# In tmux.conf
set -g history-limit 50000
```

### 4. Monitor from Anywhere
SSH into your development machine from any device to check on progress:

```bash
ssh dev-server
tmux attach -t migration
# See exactly where Claude is in the task
# Ctrl+a d to detach again
```

### 5. Session Naming Convention
Use descriptive session names so you can quickly identify what each session is doing:

```bash
tmux new -s "migrate-js-to-ts"
tmux new -s "fix-integration-tests"
tmux new -s "refactor-auth-module"
```

## Performance Benefits

| Benefit | Description |
|---------|-------------|
| Zero context loss | Never lose a conversation or re-explain context |
| Parallel operations | Multiple Claude instances for different services |
| Resource efficiency | One terminal, multiple contexts, minimal overhead |
| Network resilience | Survive connection drops without losing work |
| Time savings | Eliminate startup time by keeping sessions alive |
| True autonomy | Walk away for hours, return to completed work |
