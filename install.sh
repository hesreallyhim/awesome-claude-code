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

REPO_URL="https://github.com/stuagano/awesome-claude-code.git"
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

    # ── Install `deck` command ──

    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"

    # Create `deck` wrapper that detaches if inside tmux, launches dashboard otherwise
    cat > "$bin_dir/deck" << 'DECK_EOF'
#!/usr/bin/env bash
if [ -n "${TMUX:-}" ]; then
    tmux detach
else
    exec bash ~/.agent-deck/agent-deck.sh "$@"
fi
DECK_EOF
    chmod +x "$bin_dir/deck"
    ok "Installed: ~/.local/bin/deck"

    # Also install as agent-deck for backwards compat
    cat > "$bin_dir/agent-deck" << 'AD_EOF'
#!/usr/bin/env bash
exec bash ~/.agent-deck/agent-deck.sh "$@"
AD_EOF
    chmod +x "$bin_dir/agent-deck"
    ok "Installed: ~/.local/bin/agent-deck"

    # Check if ~/.local/bin is in PATH
    if ! echo "$PATH" | tr ':' '\n' | grep -q "$bin_dir"; then
        warn "$bin_dir is not in your PATH. Add to your shell profile:"
        echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
        echo ""
    fi

    echo ""
    echo -e "${BOLD}${GREEN}Agent Deck installed.${RESET}"
    echo ""
    echo -e "${DIM}────────────────────────────────────────${RESET}"
    echo ""
    echo "Usage:"
    echo -e "  ${BOLD}deck${RESET}                          Dashboard (home base)"
    echo -e "  ${BOLD}deck setup ~/myproject${RESET}        Set up a project"
    echo -e "  ${BOLD}deck open mirion${RESET}              Enter a project session"
    echo -e "  ${BOLD}deck${RESET}                          ${DIM}(from inside a project) back to dashboard${RESET}"
    echo ""
}

main "$@"
