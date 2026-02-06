#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Full Pipeline Runner — Orchestrates: Research → Code → Publish → Video → Promote
# Usage: bash scripts/run-pipeline.sh [topic]
# ═══════════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")/.."

TOPIC="${1:-auto}"
LOGFILE="output/logs/pipeline-$(date +%Y%m%d-%H%M%S).log"
mkdir -p output/logs

log() {
  local msg="[$(date '+%H:%M:%S')] $1"
  echo "$msg" | tee -a "$LOGFILE"
}

log "═══ PIPELINE START ═══"
log "Topic: $TOPIC"
log "Log: $LOGFILE"

# ── Stage 1: Research ──────────────────────────────────────────
log ""
log "── Stage 1: RESEARCH ──"
log "Instruction: Use the researcher subagent."
log "Read skills/research-skill.md and find trending topics."
if [ "$TOPIC" = "auto" ]; then
  log "Auto-mode: Agent will discover the best topic."
else
  log "Topic provided: $TOPIC"
fi

# ── Stage 2: Code ─────────────────────────────────────────────
log ""
log "── Stage 2: CODE ──"
log "Instruction: Use the coder subagent."
log "Read skills/coding-skill.md and build the project."

# ── Stage 3: Publish ──────────────────────────────────────────
log ""
log "── Stage 3: PUBLISH ──"
log "Instruction: Use the publisher subagent."
log "Read skills/github-skill.md and push to GitHub."

# ── Stage 4: Video ────────────────────────────────────────────
log ""
log "── Stage 4: VIDEO ──"
log "Instruction: Use the video-creator subagent."
log "Read skills/video-editing-skill.md and create an explainer video."

# ── Stage 5: Promote ──────────────────────────────────────────
log ""
log "── Stage 5: PROMOTE ──"
log "Instruction: Use the promoter subagent."
log "Read skills/promo-skill.md and post on X + LinkedIn."

log ""
log "═══ PIPELINE INSTRUCTIONS READY ═══"
log "Open Claude Code and run: /full-pipeline $TOPIC"
log "The agent will execute each stage using the appropriate subagents."
