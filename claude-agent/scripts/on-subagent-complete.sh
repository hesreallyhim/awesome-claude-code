#!/bin/bash
# SubagentStop hook: Runs when any subagent finishes
# Logs completion for tracking pipeline progress

LOGDIR="claude-agent/output/logs"
mkdir -p "$LOGDIR"

echo "$(date -Iseconds) SUBAGENT_COMPLETE" >> "$LOGDIR/pipeline-log.txt"

exit 0
