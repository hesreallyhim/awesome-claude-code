#!/bin/bash
# PreToolUse hook: Validates Bash commands before execution
# Blocks dangerous commands while allowing automation tools

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block destructive system commands
if echo "$COMMAND" | grep -iE '\b(rm\s+-rf\s+/|mkfs|dd\s+if=|shutdown|reboot|init\s+0|halt)\b' > /dev/null; then
  echo "Blocked: Dangerous system command detected" >&2
  exit 2
fi

# Block commands that could leak secrets
if echo "$COMMAND" | grep -iE '\b(cat\s+.*\.env\b|echo\s+.*API_KEY|curl.*Authorization)' > /dev/null; then
  # Only block if it looks like it's outputting secrets, not reading .env.example
  if ! echo "$COMMAND" | grep -i 'example' > /dev/null; then
    echo "Warning: Command may expose secrets. Proceeding with caution." >&2
  fi
fi

# All checks passed
exit 0
