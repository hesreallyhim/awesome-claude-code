#!/bin/bash
# Setup script for the AI Agent System
# Run this once to install all dependencies

set -e
echo "=== AI Agent System Setup ==="

# Check Node.js
if ! command -v node &> /dev/null; then
  echo "[ERROR] Node.js is not installed. Install it first:"
  echo "  brew install node     # macOS"
  echo "  apt install nodejs    # Ubuntu/Debian"
  exit 1
fi
echo "[OK] Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
  echo "[ERROR] npm is not installed."
  exit 1
fi
echo "[OK] npm $(npm --version)"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
  echo "[WARN] FFmpeg is not installed. Video features will be limited."
  echo "  Install: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)"
else
  echo "[OK] FFmpeg $(ffmpeg -version 2>&1 | head -1)"
fi

# Check git
if ! command -v git &> /dev/null; then
  echo "[ERROR] git is not installed."
  exit 1
fi
echo "[OK] git $(git --version)"

# Check gh (GitHub CLI)
if ! command -v gh &> /dev/null; then
  echo "[WARN] GitHub CLI (gh) is not installed. GitHub publishing will be limited."
  echo "  Install: brew install gh (macOS) or see https://cli.github.com/"
else
  echo "[OK] gh $(gh --version | head -1)"
fi

# Install main project dependencies
echo ""
echo "=== Installing browser automation dependencies ==="
cd "$(dirname "$0")/.."
if [ -f package.json ]; then
  npm install
  echo "[OK] Browser dependencies installed"
else
  echo "[SKIP] No package.json in claude-agent root"
fi

# Install Remotion dependencies
echo ""
echo "=== Installing Remotion video dependencies ==="
if [ -f src/package.json ]; then
  cd src
  npm install
  cd ..
  echo "[OK] Remotion dependencies installed"
else
  echo "[SKIP] No Remotion package.json found"
fi

# Make scripts executable
echo ""
echo "=== Setting script permissions ==="
chmod +x scripts/*.sh
echo "[OK] Scripts are executable"

# Create output directories
echo ""
echo "=== Creating output directories ==="
mkdir -p output/screenshots output/videos output/logs
echo "[OK] Output directories created"

# Verify setup
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Available skills:"
ls -1 skills/*.md 2>/dev/null | sed 's/skills\//  - /' | sed 's/-skill\.md//' || echo "  (none found)"
echo ""
echo "Next steps:"
echo "  1. Copy config/.env.example to config/.env and fill in your keys"
echo "  2. Open Claude Code in this directory"
echo "  3. Try: /train-skill [skill-name]  to learn a new skill"
echo "  4. Try: /run-skill [skill-name]    to execute a skill"
echo "  5. Try: /full-pipeline             to run the full creation pipeline"
