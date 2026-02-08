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
#   agent-deck setup         Guided setup for your project
#   agent-deck open          Open a session
#   agent-deck spawn         Add another agent window

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
    mkdir -p "$DECK_HOME/sessions" "$DECK_HOME/cache"

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

    # ── Enable Agent Teams ──

    local claude_settings_dir="$HOME/.claude"
    local claude_settings="$claude_settings_dir/settings.json"
    mkdir -p "$claude_settings_dir"

    if [ -f "$claude_settings" ]; then
        # Check if Agent Teams is already enabled
        if ! grep -q 'CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS' "$claude_settings" 2>/dev/null; then
            # Add env block if it exists, or create it
            if grep -q '"env"' "$claude_settings" 2>/dev/null; then
                warn "Agent Teams not enabled in settings. Add manually:"
                echo -e "  ${DIM}\"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS\": \"1\"${RESET}"
                echo -e "  ${DIM}to the \"env\" block in $claude_settings${RESET}"
            else
                warn "Agent Teams not enabled in settings. Add manually:"
                echo -e "  ${DIM}\"env\": { \"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS\": \"1\" }${RESET}"
                echo -e "  ${DIM}to $claude_settings${RESET}"
            fi
        else
            ok "Agent Teams: already enabled"
        fi
    else
        # Create settings with Agent Teams enabled
        cat > "$claude_settings" << 'SETTINGS_EOF'
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
SETTINGS_EOF
        ok "Agent Teams: enabled in $claude_settings"
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
    echo -e "  ${BOLD}agent-deck setup${RESET}             Guided setup for your project"
    echo -e "  ${BOLD}agent-deck open <session>${RESET}    Open a session (launches team lead)"
    echo -e "  ${BOLD}agent-deck list${RESET}              See all sessions + task progress"
    echo -e "  ${BOLD}agent-deck${RESET}                   Home base (interactive)"
    echo ""
}

main "$@"
