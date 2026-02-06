#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# AI Agent System — One-Time Setup
# ═══════════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")/.."

echo "╔══════════════════════════════════════════════╗"
echo "║   AI Agent System — Setup                    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Check prerequisites ────────────────────────────────────────

check() {
  if command -v "$1" &>/dev/null; then
    echo "  ✓ $1 $($1 --version 2>&1 | head -1)"
  else
    echo "  ✗ $1 — NOT FOUND ($2)"
    return 1
  fi
}

echo "Checking prerequisites..."
MISSING=0
check node    "Install: https://nodejs.org/"       || MISSING=1
check npm     "Comes with Node.js"                 || MISSING=1
check git     "Install: apt install git"           || MISSING=1
check ffmpeg  "Install: apt install ffmpeg"        || true  # optional
check gh      "Install: https://cli.github.com/"   || true  # optional

if [ "$MISSING" -eq 1 ]; then
  echo ""
  echo "ERROR: Required tools missing. Install them and re-run."
  exit 1
fi

# ── Install dependencies ──────────────────────────────────────

echo ""
echo "Installing dependencies..."
npm install --silent
echo "  ✓ Main dependencies installed"

if [ -f src/package.json ]; then
  cd src && npm install --silent && cd ..
  echo "  ✓ Remotion dependencies installed"
fi

# ── Make scripts executable ───────────────────────────────────

echo ""
echo "Setting permissions..."
chmod +x scripts/*.js scripts/*.sh scripts/hooks/*.sh 2>/dev/null || true
echo "  ✓ Scripts are executable"

# ── Create config from example ────────────────────────────────

if [ ! -f config/.env ] && [ -f config/.env.example ]; then
  cp config/.env.example config/.env
  echo "  ✓ Created config/.env from template (edit with your keys)"
fi

# ── Create .gitkeep files ────────────────────────────────────

touch output/screenshots/.gitkeep output/videos/.gitkeep output/logs/.gitkeep
echo "  ✓ Output directories ready"

# ── Summary ───────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Setup Complete!                            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Available skills:"
for f in skills/*-skill.md; do
  [ -f "$f" ] && echo "  • $(basename "$f" -skill.md)"
done
echo ""
echo "Slash commands:"
for d in .claude/skills/*/; do
  [ -d "$d" ] && echo "  • /$(basename "$d")"
done
echo ""
echo "Subagents:"
for f in .claude/agents/*.md; do
  [ -f "$f" ] && echo "  • $(basename "$f" .md)"
done
echo ""
echo "Next steps:"
echo "  1. Edit config/.env with your API keys (if needed)"
echo "  2. Open Claude Code: claude"
echo "  3. Try: /train-skill <name>     — Learn a new skill"
echo "  4. Try: /run-skill <name>       — Execute a skill"
echo "  5. Try: /full-pipeline          — Run the full pipeline"
echo ""
