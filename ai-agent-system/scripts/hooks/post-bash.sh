#!/bin/bash
# PostToolUse Hook — Runs AFTER every Bash command
# Purpose: Log command history for debugging and pipeline tracking

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

LOGDIR="output/logs"
mkdir -p "$LOGDIR"

TIMESTAMP=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')
echo "$TIMESTAMP CMD $COMMAND" >> "$LOGDIR/command-log.txt"

exit 0
