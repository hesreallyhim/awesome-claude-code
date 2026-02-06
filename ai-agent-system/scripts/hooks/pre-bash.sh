#!/bin/bash
# PreToolUse Hook — Runs BEFORE every Bash command
# Purpose: Block dangerous commands, warn about potential issues
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# === BLOCK: Destructive system commands ===
if echo "$COMMAND" | grep -qiE '\b(rm\s+-rf\s+/|mkfs|dd\s+if=|shutdown|reboot|init\s+[06]|halt|:(){ :|&)' ; then
  echo '{"error": "BLOCKED: Destructive system command detected. This could damage the system."}' >&2
  exit 2
fi

# === BLOCK: Secret exfiltration ===
if echo "$COMMAND" | grep -qiE '(curl|wget|nc)\s+.*\b(API_KEY|SECRET|TOKEN|PASSWORD)\b' ; then
  echo '{"error": "BLOCKED: Potential secret exfiltration detected."}' >&2
  exit 2
fi

# === WARN: Reading .env (not .env.example) ===
if echo "$COMMAND" | grep -qE 'cat\s+.*\.env\b' && ! echo "$COMMAND" | grep -qi 'example' ; then
  echo '{"warning": "Reading .env file — ensure secrets are not exposed in output."}' >&2
fi

# All checks passed
exit 0
