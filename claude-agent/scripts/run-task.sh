#!/bin/bash
# Run a specific task using the AI agent system
# Usage: ./run-task.sh <task-name> [arguments...]

set -e

TASK=$1
shift 2>/dev/null || true
ARGS="$*"

SKILLS_DIR="$(dirname "$0")/../skills"
OUTPUT_DIR="$(dirname "$0")/../output"

case "$TASK" in
  "research")
    echo "=== Running Research Task ==="
    echo "Reading research skill..."
    cat "$SKILLS_DIR/research-skill.md"
    echo ""
    echo "Execute with Claude Code: Use the researcher subagent"
    ;;
  "code")
    echo "=== Running Coding Task ==="
    echo "Project idea: $ARGS"
    echo "Reading coding skill..."
    cat "$SKILLS_DIR/coding-skill.md"
    ;;
  "publish")
    echo "=== Running Publish Task ==="
    echo "Reading GitHub skill..."
    cat "$SKILLS_DIR/github-skill.md"
    ;;
  "video")
    echo "=== Running Video Creation Task ==="
    echo "Reading video editing skill..."
    cat "$SKILLS_DIR/video-editing-skill.md"
    ;;
  "promote")
    echo "=== Running Promotion Task ==="
    echo "Reading promotion skill..."
    cat "$SKILLS_DIR/promo-skill.md"
    ;;
  "pipeline")
    echo "=== Running Full Pipeline ==="
    echo "This will execute: Research -> Code -> Publish -> Video -> Promote"
    echo ""
    echo "Topic: ${ARGS:-auto-detect from trends}"
    ;;
  *)
    echo "Usage: ./run-task.sh <task> [arguments]"
    echo ""
    echo "Available tasks:"
    echo "  research   - Research trending topics"
    echo "  code       - Create a coding project"
    echo "  publish    - Publish to GitHub"
    echo "  video      - Create an explainer video"
    echo "  promote    - Promote across platforms"
    echo "  pipeline   - Run the full pipeline"
    ;;
esac
