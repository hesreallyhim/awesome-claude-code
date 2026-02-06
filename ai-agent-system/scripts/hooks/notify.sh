#!/bin/bash
# Notification Hook — Runs on agent notifications
# Purpose: Optional desktop/terminal notifications for pipeline progress

INPUT=$(cat)
MESSAGE=$(echo "$INPUT" | jq -r '.message // empty' 2>/dev/null)

[ -z "$MESSAGE" ] && exit 0

LOGDIR="output/logs"
mkdir -p "$LOGDIR"

TIMESTAMP=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')
echo "$TIMESTAMP NOTIFY $MESSAGE" >> "$LOGDIR/notifications.txt"

# Desktop notification (if available)
if command -v notify-send &>/dev/null; then
  notify-send "AI Agent" "$MESSAGE" 2>/dev/null || true
elif command -v osascript &>/dev/null; then
  osascript -e "display notification \"$MESSAGE\" with title \"AI Agent\"" 2>/dev/null || true
fi

# Terminal bell
printf '\a' 2>/dev/null || true

exit 0
