#!/usr/bin/env bash
set -euo pipefail

# Install Coding-With-Claude toolkit into a target project
#
# Works two ways:
#   1. From within the awesome-claude-code repo (uses local files)
#   2. Piped from curl (fetches from GitHub)
#
# Usage:
#   ./install.sh /path/to/your-project
#   ./install.sh /path/to/your-project --commands
#   ./install.sh /path/to/your-project --append
#   curl -fsSL <url>/install.sh | bash -s -- /path/to/your-project

GITHUB_RAW="https://raw.githubusercontent.com/stuagano/awesome-claude-code/main/resources"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null || echo ".")" && pwd)"

# Detect if running from within the repo or standalone
if [ -f "$SCRIPT_DIR/CLAUDE.md" ]; then
    MODE="local"
    TOOLKIT_CLAUDE_MD="$SCRIPT_DIR/CLAUDE.md"
    COMMANDS_DIR="$SCRIPT_DIR/../../slash-commands"
else
    MODE="remote"
fi

usage() {
    echo "Usage: $(basename "$0") <project-path> [--commands] [--append]"
    echo ""
    echo "  <project-path>   Path to the project to install the toolkit into (use . for current dir)"
    echo "  --commands        Also install slash commands into .claude/commands/"
    echo "  --append          Append to existing CLAUDE.md instead of overwriting"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") ."
    echo "  $(basename "$0") ~/my-project"
    echo "  $(basename "$0") ~/my-project --commands --append"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

TARGET_DIR="$1"
shift

INSTALL_COMMANDS=false
APPEND_MODE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --commands) INSTALL_COMMANDS=true ;;
        --append)   APPEND_MODE=true ;;
        *)          echo "Unknown option: $1"; usage ;;
    esac
    shift
done

# Resolve . to actual path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR is not a directory"
    exit 1
fi

# Helper: get toolkit CLAUDE.md content (local or remote), stripping the Setup section
get_toolkit_content() {
    if [ "$MODE" = "local" ]; then
        sed '/^## Setup$/,$ d' "$TOOLKIT_CLAUDE_MD"
    else
        curl -fsSL "$GITHUB_RAW/claude.md-files/Coding-With-Claude-Toolkit/CLAUDE.md" | sed '/^## Setup$/,$ d'
    fi
}

# Helper: get a slash command file (local or remote)
get_command() {
    local cmd_name="$1"
    if [ "$MODE" = "local" ]; then
        cat "$COMMANDS_DIR/$cmd_name/$cmd_name.md"
    else
        curl -fsSL "$GITHUB_RAW/slash-commands/$cmd_name/$cmd_name.md"
    fi
}

# Install CLAUDE.md
if [ -f "$TARGET_DIR/CLAUDE.md" ] && [ "$APPEND_MODE" = false ]; then
    echo "CLAUDE.md already exists in $TARGET_DIR"
    echo "Use --append to add toolkit to existing CLAUDE.md, or remove it first."
    exit 1
fi

if [ "$APPEND_MODE" = true ] && [ -f "$TARGET_DIR/CLAUDE.md" ]; then
    echo "" >> "$TARGET_DIR/CLAUDE.md"
    echo "---" >> "$TARGET_DIR/CLAUDE.md"
    echo "<!-- Coding-With-Claude Toolkit (auto-behaviors below) -->" >> "$TARGET_DIR/CLAUDE.md"
    echo "" >> "$TARGET_DIR/CLAUDE.md"
    get_toolkit_content >> "$TARGET_DIR/CLAUDE.md"
    echo "Appended toolkit to $TARGET_DIR/CLAUDE.md"
else
    get_toolkit_content > "$TARGET_DIR/CLAUDE.md"
    echo "Installed $TARGET_DIR/CLAUDE.md"
fi

# Install slash commands
if [ "$INSTALL_COMMANDS" = true ]; then
    COMMANDS_TARGET="$TARGET_DIR/.claude/commands"
    mkdir -p "$COMMANDS_TARGET"

    for cmd_name in structure-request plan-feature debug-error act; do
        if get_command "$cmd_name" > "$COMMANDS_TARGET/$cmd_name.md" 2>/dev/null; then
            echo "Installed $COMMANDS_TARGET/$cmd_name.md"
        else
            echo "Warning: could not fetch $cmd_name, skipping"
            rm -f "$COMMANDS_TARGET/$cmd_name.md"
        fi
    done
fi

echo ""
echo "Done. Start Claude Code in $TARGET_DIR and the toolkit is active."
echo ""
echo "What's installed:"
echo "  $TARGET_DIR/CLAUDE.md (9 auto-behaviors, always on)"
if [ "$INSTALL_COMMANDS" = true ]; then
    echo "  $TARGET_DIR/.claude/commands/ (optional slash commands)"
fi
echo ""
echo "No connection back to the awesome-claude-code repo needed."
