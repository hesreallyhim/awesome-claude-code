# Autonomous Claude Code + tmux Workflow

This directory contains a comprehensive guide for running Claude Code autonomously in tmux sessions. The core idea: start a complex task, detach from the terminal, and come back hours later to find the work done.

## Concept

tmux provides persistent terminal sessions that survive disconnections, SSH drops, and laptop closures. Combined with Claude Code, this creates a truly autonomous AI development workflow where:

- **Sessions persist indefinitely** - Start a refactoring task, close your laptop, come back hours or days later
- **Background execution** - Claude Code runs long tasks (test suites, migrations, builds) without blocking you
- **Multi-pane dashboards** - Monitor Claude, tests, logs, and git all in one view
- **Network resilience** - SSH drops and connection failures don't kill your Claude session
- **Zero context loss** - Never re-explain context or lose conversation history

## Resources

### Templates & Guides
- [tmux Configuration](./tmux-config.md) - Complete tmux.conf optimized for Claude Code with Catppuccin Mocha theme
- [Session Scripts](./session-scripts.md) - Automation scripts for creating development dashboards and managing sessions
- [Autonomous Workflows](./autonomous-workflows.md) - Patterns for leave-your-computer autonomous Claude Code execution

## Source

Based on [Claude Code + tmux: The Ultimate Terminal Workflow for AI Development](https://www.blle.co/blog/claude-code-tmux-beautiful-terminal) by Blue Leaf LLC.
