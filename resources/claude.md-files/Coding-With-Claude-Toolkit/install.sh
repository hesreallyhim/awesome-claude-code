#!/usr/bin/env bash
set -euo pipefail

# Install Coding-With-Claude toolkit into a target project
#
# Usage:
#   ./install.sh /path/to/your-project
#   ./install.sh /path/to/your-project --commands   # also install slash commands
#   ./install.sh /path/to/your-project --append      # append to existing CLAUDE.md

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT_CLAUDE_MD="$SCRIPT_DIR/CLAUDE.md"

# Slash command source files (from the repo)
COMMANDS_DIR="$SCRIPT_DIR/../../slash-commands"

usage() {
    echo "Usage: $(basename "$0") <project-path> [--commands] [--append]"
    echo ""
    echo "  <project-path>   Path to the project to install the toolkit into"
    echo "  --commands        Also install slash commands into .claude/commands/"
    echo "  --append          Append to existing CLAUDE.md instead of overwriting"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") ~/my-project"
    echo "  $(basename "$0") ~/my-project --commands"
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

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR is not a directory"
    exit 1
fi

# Install CLAUDE.md
if [ -f "$TARGET_DIR/CLAUDE.md" ] && [ "$APPEND_MODE" = false ]; then
    echo "CLAUDE.md already exists in $TARGET_DIR"
    echo "Use --append to add toolkit to existing CLAUDE.md, or remove it first."
    exit 1
fi

if [ "$APPEND_MODE" = true ] && [ -f "$TARGET_DIR/CLAUDE.md" ]; then
    echo "" >> "$TARGET_DIR/CLAUDE.md"
    # Strip the Setup section when appending (it's repo-specific instructions)
    sed '/^---$/,/^- The CLAUDE.md is the only file/d' "$TOOLKIT_CLAUDE_MD" >> "$TARGET_DIR/CLAUDE.md"
    echo "Appended toolkit to $TARGET_DIR/CLAUDE.md"
else
    # Strip the Setup section when copying (it's repo-specific instructions)
    sed '/^## Setup$/,/^- The CLAUDE.md is the only file.*conveniences$/d' "$TOOLKIT_CLAUDE_MD" > "$TARGET_DIR/CLAUDE.md"
    echo "Installed $TARGET_DIR/CLAUDE.md"
fi

# Install slash commands
if [ "$INSTALL_COMMANDS" = true ]; then
    COMMANDS_TARGET="$TARGET_DIR/.claude/commands"
    mkdir -p "$COMMANDS_TARGET"

    COMMAND_FILES=(
        "structure-request/structure-request.md"
        "plan-feature/plan-feature.md"
        "debug-error/debug-error.md"
        "act/act.md"
    )

    for cmd_file in "${COMMAND_FILES[@]}"; do
        cmd_name="$(basename "$cmd_file")"
        if [ -f "$COMMANDS_DIR/$cmd_file" ]; then
            cp "$COMMANDS_DIR/$cmd_file" "$COMMANDS_TARGET/$cmd_name"
            echo "Installed $COMMANDS_TARGET/$cmd_name"
        else
            echo "Warning: $COMMANDS_DIR/$cmd_file not found, skipping"
        fi
    done
fi

echo ""
echo "Done. Start Claude Code in $TARGET_DIR and the toolkit is active."
