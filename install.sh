#!/usr/bin/env bash
# install.sh - Bootstrap the Agent Deck onto your machine
#
# This is the one-liner entry point. It installs the Agent Deck, which
# is the actual tool for managing Claude Code resources across projects.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash
#   bash install.sh
#
# After install, use:
#   agent-deck new           Create a collection (guided setup)
#   agent-deck install       Install a collection into a project
#   agent-deck launch        Spawn a Claude Code tmux session

set -euo pipefail

REPO_URL="https://github.com/hesreallyhim/awesome-claude-code.git"
REPO_BRANCH="main"
DECK_HOME="${AGENT_DECK_HOME:-$HOME/.agent-deck}"

# Colors
if [ -t 1 ]; then
    BOLD='\033[1m' DIM='\033[2m'
    GREEN='\033[0;32m' YELLOW='\033[0;33m' CYAN='\033[0;36m'
    RED='\033[0;31m' RESET='\033[0m'
else
    BOLD='' DIM='' GREEN='' YELLOW='' CYAN='' RED='' RESET=''
fi

info()  { echo -e "${CYAN}${BOLD}>>>${RESET} $*"; }
ok()    { echo -e "${GREEN}${BOLD} +${RESET} $*"; }
warn()  { echo -e "${YELLOW}${BOLD} !${RESET} $*"; }
err()   { echo -e "${RED}${BOLD} x${RESET} $*" >&2; }

main() {
    echo ""
    echo -e "${BOLD}Awesome Claude Code — Agent Deck Installer${RESET}"
    echo ""

    # ── Clone or update the resource cache ──

    local cache_dir="$DECK_HOME/cache/awesome-claude-code"
    mkdir -p "$DECK_HOME/collections" "$DECK_HOME/cache"

    if [ -d "$cache_dir/resources" ]; then
        info "Updating resource cache..."
        git -C "$cache_dir" pull --quiet 2>/dev/null || true
    else
        info "Fetching awesome-claude-code resources..."
        if ! git clone --depth 1 --branch "$REPO_BRANCH" --single-branch \
             "$REPO_URL" "$cache_dir" 2>/dev/null; then
            err "Failed to clone. Check your network connection."
            exit 1
        fi
    fi
    date +%s > "$cache_dir/.fetch_time"
    ok "Resources cached."

    # ── Install agent-deck.sh ──

    if [ -f "$cache_dir/agent-deck.sh" ]; then
        cp "$cache_dir/agent-deck.sh" "$DECK_HOME/agent-deck.sh"
        chmod +x "$DECK_HOME/agent-deck.sh"
        ok "Installed: ~/.agent-deck/agent-deck.sh"
    else
        err "agent-deck.sh not found in repo."
        exit 1
    fi

    # ── Install /deck command to current project (if it looks like a project) ──

    local target="$(pwd)"
    if [ -d "$target/.git" ] || [ -f "$target/package.json" ] || \
       [ -f "$target/pyproject.toml" ] || [ -f "$target/Cargo.toml" ] || \
       [ -f "$target/go.mod" ] || [ -f "$target/Makefile" ]; then

        local deck_cmd="$cache_dir/resources/slash-commands/deck"
        if [ -d "$deck_cmd" ]; then
            mkdir -p "$target/.claude/commands"
            local md_file
            md_file=$(find "$deck_cmd" -maxdepth 1 -name "*.md" | head -1)
            if [ -n "$md_file" ] && [ ! -f "$target/.claude/commands/deck.md" ]; then
                cp "$md_file" "$target/.claude/commands/deck.md"
                ok "Installed /deck command to this project"
            fi
        fi
    fi

    # ── Set up shell alias ──

    echo ""
    echo -e "${BOLD}${GREEN}Agent Deck installed.${RESET}"
    echo ""
    echo "Add this alias to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
    echo ""
    echo -e "  ${CYAN}alias agent-deck='bash ~/.agent-deck/agent-deck.sh'${RESET}"
    echo ""
    echo -e "${DIM}────────────────────────────────────────${RESET}"
    echo ""
    echo "Get started:"
    echo -e "  ${BOLD}agent-deck new${RESET}           Create a collection (guided setup)"
    echo -e "  ${BOLD}agent-deck install${RESET}       Install a collection into a project"
    echo -e "  ${BOLD}agent-deck launch <dir>${RESET}  Spawn a Claude Code tmux session"
    echo -e "  ${BOLD}agent-deck${RESET}               Home base (interactive)"
    echo ""
    echo "Or from Claude Code:"
    echo -e "  ${BOLD}/deck${RESET}                    Full agent deck experience"
    echo ""
}

main "$@"
