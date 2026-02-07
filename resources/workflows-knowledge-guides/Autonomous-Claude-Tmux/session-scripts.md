# Session Scripts for Autonomous Claude Code

Automation scripts for creating pre-configured tmux development dashboards and managing multiple Claude Code sessions.

## Development Dashboard

A single script that sets up a full development environment with Claude Code, test watchers, logs, and git in separate windows:

```bash
#!/bin/bash
# claude-dev-session.sh
# Creates a multi-window tmux session for autonomous Claude Code work

SESSION="claude-dev"

tmux new-session -d -s "$SESSION"
tmux rename-window -t "$SESSION:0" 'Claude Code'
tmux new-window -t "$SESSION:1" -n 'Tests'
tmux new-window -t "$SESSION:2" -n 'Logs'
tmux new-window -t "$SESSION:3" -n 'Git'

# Start Claude Code in the first window
tmux send-keys -t "$SESSION:0" 'claude' Enter

# Set up test watcher in second window
tmux send-keys -t "$SESSION:1" 'npm run test:watch' Enter

# Tail logs in third window
tmux send-keys -t "$SESSION:2" 'tail -f logs/app.log' Enter

tmux attach-session -t "$SESSION"
```

Make it executable:
```bash
chmod +x claude-dev-session.sh
```

## Multi-Project Session Management

Keep separate tmux sessions for different projects, each with its own Claude Code instance and context:

```bash
# Start a session for Project A
tmux new -s project-a -c ~/projects/project-a
# Inside: run `claude` to start Claude Code with project-a context

# Start a session for Project B
tmux new -s project-b -c ~/projects/project-b
# Inside: run `claude` to start Claude Code with project-b context

# Switch between projects instantly
tmux switch -t project-a
tmux switch -t project-b

# List all active sessions
tmux ls
```

## Monitoring Pane Layout

When Claude Code is performing extensive autonomous operations, set up a monitoring layout:

```bash
# From inside tmux:

# Split pane to monitor system resources
# Ctrl+a |
htop

# Split another pane for real-time log monitoring
# Ctrl+a -
tail -f ~/.claude/logs/claude.log

# Claude continues working uninterrupted in the main pane
# You can detach (Ctrl+a d) and come back later to check progress
```

## Collaborative Sessions

tmux session sharing enables pair programming with Claude Code acting as a shared AI assistant:

```bash
# Developer 1 creates a shared session
tmux new -s collab

# Developer 2 attaches to the same session from another terminal
tmux attach -t collab

# Both developers see the same Claude Code instance in real time
```

## Quick Reference

| Action | Command |
|--------|---------|
| Detach (Claude keeps running) | `Ctrl+a d` |
| List sessions | `tmux ls` |
| Reattach | `tmux attach -t <session>` |
| Split horizontal | `Ctrl+a \|` |
| Split vertical | `Ctrl+a -` |
| Navigate panes | `Ctrl+a h/j/k/l` |
| Enter copy mode (scroll) | `Ctrl+a [` |
| Switch session | `tmux switch -t <name>` |
