#!/bin/bash
# PostToolUse hook: Runs after file edits
# Logs file changes for tracking and optional linting

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty' 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Log the edit
LOGDIR="claude-agent/output/logs"
mkdir -p "$LOGDIR"
echo "$(date -Iseconds) EDIT: $FILE_PATH" >> "$LOGDIR/edit-log.txt"

# Run linter for specific file types
case "$FILE_PATH" in
  *.js|*.ts|*.tsx|*.jsx)
    # If eslint is available, run it (non-blocking)
    if command -v npx &> /dev/null && [ -f "node_modules/.bin/eslint" ]; then
      npx eslint --fix "$FILE_PATH" 2>/dev/null || true
    fi
    ;;
  *.py)
    # If ruff is available, run it (non-blocking)
    if command -v ruff &> /dev/null; then
      ruff check --fix "$FILE_PATH" 2>/dev/null || true
    fi
    ;;
  *.md)
    # Skill files get special logging
    if echo "$FILE_PATH" | grep -q "skill"; then
      echo "$(date -Iseconds) SKILL_UPDATE: $FILE_PATH" >> "$LOGDIR/skill-updates.txt"
    fi
    ;;
esac

exit 0
