# Agent Deck - Claude Code Session Navigator

Agent Deck is a tmux-based session manager that discovers all your Claude Code projects and lets you launch, navigate between, and monitor autonomous Claude sessions from a single dashboard.

## How It Works

```
$ agent-deck

  Agent Deck - Claude Code Projects
  ─────────────────────────────────────────

  1)  ● running  my-api
      /home/user/projects/my-api
      CLAUDE.md .claude/

  2)  ○ idle     data-pipeline
      /home/user/projects/data-pipeline
      CLAUDE.md

  3)  ● running  frontend-app
      /home/user/projects/frontend-app
      .claude/

  ─────────────────────────────────────────
  Commands:
  <number>  Launch/attach to project
  s         Show active sessions
  k <name>  Kill a session
  q         Quit

  > _
```

Agent Deck scans your common project directories for `CLAUDE.md` files or `.claude/` directories, indicating a Claude Code project. It shows which projects have active tmux sessions and lets you jump into any of them instantly.

## Installation

### macOS
```bash
# Prerequisites
brew install tmux

# Copy the script somewhere on your PATH
cp agent-deck.sh /usr/local/bin/agent-deck
chmod +x /usr/local/bin/agent-deck

# Or if using Homebrew paths (Apple Silicon)
cp agent-deck.sh /opt/homebrew/bin/agent-deck
chmod +x /opt/homebrew/bin/agent-deck
```

### Linux
```bash
# Prerequisites
sudo apt install tmux   # Debian/Ubuntu
sudo dnf install tmux   # Fedora/RHEL

# Copy the script somewhere on your PATH
cp agent-deck.sh ~/.local/bin/agent-deck
chmod +x ~/.local/bin/agent-deck
```

### Either platform (symlink)
```bash
ln -s "$(pwd)/agent-deck.sh" ~/.local/bin/agent-deck
```

## Commands

| Command | Description |
|---------|-------------|
| `agent-deck` | Interactive picker - lists projects, pick a number to launch |
| `agent-deck list` | List all discovered Claude Code projects |
| `agent-deck launch <path>` | Launch a new Claude session for a project |
| `agent-deck attach <name>` | Reattach to a running session |
| `agent-deck kill <name>` | Kill a session |
| `agent-deck status` | Show all active agent sessions with uptime |

## Configuration

Edit the top of `agent-deck.sh` to customize:

```bash
# Directories to scan for Claude Code projects
SEARCH_DIRS=("$HOME/projects" "$HOME/repos" "$HOME/code" "$HOME/work" "$HOME")

# How deep to search for CLAUDE.md / .claude/
MAX_DEPTH=3

# Prefix for tmux session names (e.g., "agent-my-api")
SESSION_PREFIX="agent"
```

## Navigation Workflow

### Launching a project
```bash
# Interactive - pick from a list
agent-deck

# Direct launch
agent-deck launch ~/projects/my-api
```

### Switching between projects

From inside any agent session, you don't need to exit Claude. Use tmux session switching:

```
Ctrl+a s          # tmux session picker (visual list)
Ctrl+a (          # Previous session
Ctrl+a )          # Next session
```

This is the key navigation pattern: you stay in tmux and flip between sessions. Claude keeps running in each one.

### Checking on all sessions
```bash
# From any terminal (even a new SSH connection)
agent-deck status

  Agent Deck - Active Sessions
  ─────────────────────────────────────────

  ● agent-my-api          (1 windows, started 3h ago)
    /home/user/projects/my-api
  ● agent-data-pipeline   (1 windows, started 45m ago)
    /home/user/projects/data-pipeline
  ● agent-frontend-app    (1 windows, started 6h ago)
    /home/user/projects/frontend-app
```

### The daily cycle

```
Morning:
  $ agent-deck              # See all projects
  > 1                       # Jump into first project, Claude is still running from yesterday

Mid-day:
  Ctrl+a )                  # Flip to next project
  Ctrl+a )                  # Flip again
  Ctrl+a d                  # Detach, go to lunch

Evening:
  $ agent-deck status       # Quick check from phone via SSH
                            # Everything still running, go home
```

## tmux Keybindings Quick Reference

These work from inside any agent session:

| Action | Keys |
|--------|------|
| Session picker (navigate visually) | `Ctrl+a s` |
| Next session | `Ctrl+a )` |
| Previous session | `Ctrl+a (` |
| Detach (sessions keep running) | `Ctrl+a d` |
| New window in current session | `Ctrl+a c` |
| Split pane horizontally | `Ctrl+a \|` |
| Split pane vertically | `Ctrl+a -` |
| Navigate panes | `Ctrl+a h/j/k/l` |
| Scroll up (copy mode) | `Ctrl+a [` |

## Example: Parallel Autonomous Agents

Launch three Claude instances working on different parts of your system, then walk away:

```bash
# Launch all three
agent-deck launch ~/projects/api         # Give Claude the backend task
# Ctrl+a d to detach

agent-deck launch ~/projects/frontend    # Give Claude the frontend task
# Ctrl+a d to detach

agent-deck launch ~/projects/infra       # Give Claude the IaC task
# Ctrl+a d to detach

# Check on everything
agent-deck status

# Jump into any one
agent-deck attach api
```

## macOS-Specific Notes

### Keeping sessions alive when you walk away

On a Mac, closing the lid suspends all processes including tmux. For true autonomy:

```bash
# Option 1: Keep Mac awake with caffeinate
caffeinate -t 28800 &    # 8 hours
agent-deck launch ~/projects/big-refactor
# Close the terminal window (not the lid) - Claude keeps working

# Option 2: Run on a remote server
ssh my-server
agent-deck launch ~/projects/big-refactor
# Now you can close your Mac entirely
```

### Checking sessions from your phone

Any iOS SSH client (Blink Shell, Termius, Prompt) works:

```bash
ssh my-mac.local          # or your remote server
agent-deck status         # See what's running
agent-deck attach api     # Jump in to check progress
```
