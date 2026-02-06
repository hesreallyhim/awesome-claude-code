#!/bin/bash
# PostToolUse Hook — Runs AFTER every Write/Edit operation
# Purpose: Log file changes, auto-lint where possible

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty' 2>/dev/null)

[ -z "$FILE_PATH" ] && exit 0

LOGDIR="output/logs"
mkdir -p "$LOGDIR"

# Log the edit
TIMESTAMP=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')
echo "$TIMESTAMP EDIT $FILE_PATH" >> "$LOGDIR/edit-log.txt"

# Auto-lint based on file type (non-blocking, best-effort)
case "$FILE_PATH" in
  *.js|*.ts|*.tsx|*.jsx)
    if [ -f "node_modules/.bin/eslint" ]; then
      npx eslint --fix "$FILE_PATH" 2>/dev/null || true
    fi
    ;;
  *.py)
    if command -v ruff &>/dev/null; then
      ruff check --fix "$FILE_PATH" 2>/dev/null || true
    fi
    ;;
  *skill*.md)
    echo "$TIMESTAMP SKILL_UPDATE $FILE_PATH" >> "$LOGDIR/skill-updates.txt"
    ;;
esac

exit 0
