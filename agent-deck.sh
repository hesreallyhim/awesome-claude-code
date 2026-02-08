#!/usr/bin/env bash
# agent-deck - Home base for Claude Code sessions
#
# A session is scoped to a project folder. It's configured with resources
# and can run multiple agent windows (each a Claude Code instance or
# supporting tool). The deck is where you manage all your sessions.
#
# Usage:
#   agent-deck                        Home base (interactive)
#   agent-deck setup [dir]            Create + configure a session for a project
#   agent-deck open <session>         Open a session (attach or create)
#   agent-deck spawn <session>        Add another agent window to a session
#   agent-deck list                   List all sessions
#   agent-deck kill <session>         Kill a session
#   agent-deck help                   Show help

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────
DECK_HOME="${AGENT_DECK_HOME:-$HOME/.agent-deck}"
SESSIONS_DIR="$DECK_HOME/sessions"
ACC_REPO_URL="https://github.com/hesreallyhim/awesome-claude-code.git"
ACC_CACHE="$DECK_HOME/cache/awesome-claude-code"
SESSION_PREFIX="deck"

# ── Colors ────────────────────────────────────────────────────────────
if [ -t 1 ]; then
    BOLD='\033[1m' DIM='\033[2m'
    GREEN='\033[0;32m' YELLOW='\033[0;33m' CYAN='\033[0;36m'
    RED='\033[0;31m' BLUE='\033[0;34m' MAGENTA='\033[0;35m' RESET='\033[0m'
else
    BOLD='' DIM='' GREEN='' YELLOW='' CYAN='' RED='' BLUE='' MAGENTA='' RESET=''
fi

info()  { echo -e "${CYAN}${BOLD}>>>${RESET} $*"; }
ok()    { echo -e "${GREEN}${BOLD} +${RESET} $*"; }
warn()  { echo -e "${YELLOW}${BOLD} !${RESET} $*"; }
err()   { echo -e "${RED}${BOLD} x${RESET} $*" >&2; }

# ── Init ──────────────────────────────────────────────────────────────
init_deck() {
    mkdir -p "$SESSIONS_DIR" "$DECK_HOME/cache"
}

# ── Resource cache ────────────────────────────────────────────────────
ensure_cache() {
    if [ -d "$ACC_CACHE/resources" ]; then
        local age=0
        if [ -f "$ACC_CACHE/.fetch_time" ]; then
            local fetch_time
            fetch_time=$(cat "$ACC_CACHE/.fetch_time")
            age=$(( $(date +%s) - fetch_time ))
        fi
        if [ "$age" -gt 86400 ]; then
            info "Updating resources..."
            git -C "$ACC_CACHE" pull --quiet 2>/dev/null || true
            date +%s > "$ACC_CACHE/.fetch_time"
        fi
        return 0
    fi

    info "Fetching awesome-claude-code resources (one-time)..."
    if ! git clone --depth 1 "$ACC_REPO_URL" "$ACC_CACHE" 2>/dev/null; then
        err "Failed to clone. Check network."
        return 1
    fi
    date +%s > "$ACC_CACHE/.fetch_time"
    ok "Resources cached."
}

# ── Resource mappings ─────────────────────────────────────────────────
commands_for_domain() {
    case "$1" in
        ml)          echo "mlflow-log-model uc-register-model feature-table databricks-deploy" ;;
        databricks)  echo "databricks-job databricks-deploy feature-table mlflow-log-model uc-register-model" ;;
        devops)      echo "act create-hook husky" ;;
        *)           echo "" ;;
    esac
}

templates_for_domain() {
    case "$1" in
        ml)          echo "DSPy MLflow-Databricks Feature-Engineering Vector-Search Mosaic-AI-Agents Databricks-AI-Dev-Kit" ;;
        databricks)  echo "Databricks-Full-Stack Delta-Live-Tables Databricks-Jobs Unity-Catalog" ;;
        backend)     echo "SG-Cars-Trends-Backend LangGraphJS AWS-MCP-Server Giselle" ;;
        frontend)    echo "APX-Databricks-Apps Course-Builder JSBeeb" ;;
        devops)      echo "Databricks-MCP-Server claude-code-mcp-enhanced" ;;
        cli)         echo "TPL Cursor-Tools" ;;
        general)     echo "Basic-Memory" ;;
        *)           echo "" ;;
    esac
}

commands_for_needs() {
    local cmds=""
    for need in $1; do
        case "$need" in
            git)     cmds="$cmds create-pr fix-github-issue create-worktrees update-branch-name husky" ;;
            quality) cmds="$cmds testing_plan_integration create-hook" ;;
            context) cmds="$cmds context-prime initref load-llms-txt" ;;
            docs)    cmds="$cmds update-docs add-to-changelog" ;;
            deploy)  cmds="$cmds release act" ;;
        esac
    done
    echo "$cmds"
}

# ── Project detection ─────────────────────────────────────────────────
detect_project() {
    local dir="$1"
    DETECTED_LANG="" DETECTED_FRAMEWORK="" DETECTED_DEFAULT_DOMAIN="7"

    if [ -f "$dir/pyproject.toml" ] || [ -f "$dir/setup.py" ] || [ -f "$dir/requirements.txt" ]; then
        DETECTED_LANG="python"
    elif [ -f "$dir/package.json" ]; then
        DETECTED_LANG="javascript"
    elif [ -f "$dir/Cargo.toml" ]; then
        DETECTED_LANG="rust"
    elif [ -f "$dir/go.mod" ]; then
        DETECTED_LANG="go"
    elif [ -f "$dir/pom.xml" ] || [ -f "$dir/build.gradle" ]; then
        DETECTED_LANG="java"
    elif [ -f "$dir/Gemfile" ]; then
        DETECTED_LANG="ruby"
    fi

    if [ -f "$dir/package.json" ]; then
        grep -q '"react"\|"next"' "$dir/package.json" 2>/dev/null && DETECTED_FRAMEWORK="react" && DETECTED_DEFAULT_DOMAIN="4"
        grep -q '"express"\|"fastify"' "$dir/package.json" 2>/dev/null && DETECTED_FRAMEWORK="node-api" && DETECTED_DEFAULT_DOMAIN="3"
    fi
    if [ -f "$dir/pyproject.toml" ]; then
        grep -q 'fastapi\|django\|flask' "$dir/pyproject.toml" 2>/dev/null && DETECTED_FRAMEWORK="python-api" && DETECTED_DEFAULT_DOMAIN="3"
        grep -q 'mlflow\|databricks\|pyspark' "$dir/pyproject.toml" 2>/dev/null && DETECTED_FRAMEWORK="databricks" && DETECTED_DEFAULT_DOMAIN="2"
        grep -q 'torch\|tensorflow\|scikit' "$dir/pyproject.toml" 2>/dev/null && DETECTED_FRAMEWORK="ml" && DETECTED_DEFAULT_DOMAIN="1"
    fi
}

# ── Session config ────────────────────────────────────────────────────
session_name_from_path() {
    local name
    name=$(basename "$1" | tr '.' '-' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    echo "${SESSION_PREFIX}-${name}"
}

save_session() {
    local name="$1" dir="$2" domain="$3" needs="$4" commands="$5" templates="$6"
    cat > "$SESSIONS_DIR/$name.conf" << EOF
# Agent Deck Session: $name
# Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
PROJECT_DIR=$dir
DOMAIN=$domain
NEEDS=$needs
COMMANDS=$commands
TEMPLATES=$templates
EOF
}

load_session() {
    local name="$1"
    # Try with and without prefix
    local file="$SESSIONS_DIR/$name.conf"
    [ ! -f "$file" ] && file="$SESSIONS_DIR/${SESSION_PREFIX}-${name}.conf"
    if [ ! -f "$file" ]; then
        err "Session not found: $name"
        return 1
    fi
    # shellcheck disable=SC1090
    source "$file"
}

tmux_session_exists() {
    tmux has-session -t "$1" 2>/dev/null
}

tmux_window_count() {
    tmux list-windows -t "$1" 2>/dev/null | wc -l | tr -d ' '
}

# ── Install resources into a directory ────────────────────────────────
install_resources() {
    local target_dir="$1" commands="$2" templates="$3"

    ensure_cache || return 1

    # Install commands
    mkdir -p "$target_dir/.claude/commands"
    local cmd_count=0
    for cmd in $commands; do
        local src="$ACC_CACHE/resources/slash-commands/$cmd"
        if [ -d "$src" ]; then
            local md_file
            md_file=$(find "$src" -maxdepth 1 -name "*.md" | head -1)
            if [ -n "$md_file" ]; then
                local dest="$target_dir/.claude/commands/$(basename "$md_file")"
                if [ ! -f "$dest" ]; then
                    cp "$md_file" "$dest"
                    ok "/$cmd"
                    cmd_count=$((cmd_count + 1))
                fi
            fi
        fi
    done

    # Install templates
    local tpl_count=0
    for tpl in $templates; do
        local src="$ACC_CACHE/resources/claude.md-files/$tpl/CLAUDE.md"
        if [ -f "$src" ]; then
            local dest="$target_dir/CLAUDE.md"
            local marker="# --- awesome-claude-code: $tpl ---"
            if [ -f "$dest" ] && grep -qF "$marker" "$dest" 2>/dev/null; then
                continue
            fi
            {
                [ -f "$dest" ] && echo ""
                echo "$marker"
                echo ""
                cat "$src"
            } >> "$dest"
            ok "$tpl"
            tpl_count=$((tpl_count + 1))
        fi
    done

    echo ""
    ok "Installed $cmd_count commands + $tpl_count templates"
}

# ══════════════════════════════════════════════════════════════════════
# COMMANDS
# ══════════════════════════════════════════════════════════════════════

# ── setup: create + configure a session for a project ─────────────────
cmd_setup() {
    local target_dir="${1:-$(pwd)}"
    target_dir="$(cd "$target_dir" && pwd)"

    local name
    name=$(session_name_from_path "$target_dir")

    echo ""
    echo -e "${BOLD}${BLUE}  Agent Deck — Session Setup${RESET}"
    echo -e "${DIM}  $target_dir${RESET}"
    echo ""

    # Detect project
    detect_project "$target_dir"
    if [ -n "$DETECTED_LANG" ]; then
        echo -e "  Detected: ${CYAN}$DETECTED_LANG${RESET}"
    fi
    if [ -n "$DETECTED_FRAMEWORK" ]; then
        echo -e "  Framework: ${CYAN}$DETECTED_FRAMEWORK${RESET}"
    fi
    [ -d "$target_dir/.claude" ] && echo -e "  Claude Code: ${GREEN}configured${RESET}"
    echo ""

    # ── Domain ──
    echo -e "  ${BOLD}What are you building?${RESET}"
    echo ""
    echo "    1) ML / Data Science"
    echo "    2) Data Engineering / Databricks"
    echo "    3) Backend / API"
    echo "    4) Frontend / Web App"
    echo "    5) DevOps / Infrastructure"
    echo "    6) CLI / Tooling"
    echo "    7) General software project"
    echo ""

    local default_domain="${DETECTED_DEFAULT_DOMAIN:-7}"
    echo -ne "  Choice [1-7] (${default_domain}): "
    read -r domain_choice
    domain_choice="${domain_choice:-$default_domain}"

    local domain
    case "$domain_choice" in
        1) domain="ml" ;; 2) domain="databricks" ;; 3) domain="backend" ;;
        4) domain="frontend" ;; 5) domain="devops" ;; 6) domain="cli" ;;
        *) domain="general" ;;
    esac

    # ── Needs ──
    echo ""
    echo -e "  ${BOLD}What do you need?${RESET} ${DIM}(multiple: 1 3 5)${RESET}"
    echo ""
    echo "    1) Git workflow      — Commits, PRs, branches"
    echo "    2) Code quality      — Reviews, optimization, testing"
    echo "    3) Project context   — Help Claude understand your code"
    echo "    4) Documentation     — Docs, changelogs, release notes"
    echo "    5) Deployment        — CI/CD, releases"
    echo "    6) Everything"
    echo ""
    echo -n "  Choice: "
    read -r needs_choice

    local needs=""
    for n in $needs_choice; do
        case "$n" in
            1) needs="$needs git" ;; 2) needs="$needs quality" ;;
            3) needs="$needs context" ;; 4) needs="$needs docs" ;;
            5) needs="$needs deploy" ;; 6) needs="git quality context docs deploy" ;;
        esac
    done

    # ── Build resource list ──
    local base_cmds="commit pr-review optimize"
    local domain_cmds
    domain_cmds=$(commands_for_domain "$domain")
    local needs_cmds
    needs_cmds=$(commands_for_needs "$needs")
    local all_cmds
    all_cmds=$(echo "$base_cmds $domain_cmds $needs_cmds" | tr ' ' '\n' | sort -u | tr '\n' ' ')
    local templates
    templates=$(templates_for_domain "$domain")

    # ── Preview ──
    echo ""
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo -e "  ${BOLD}Session: ${GREEN}$name${RESET}"
    echo ""
    echo -e "  ${BOLD}Commands:${RESET}"
    for cmd in $all_cmds; do
        echo -e "    ${GREEN}/$cmd${RESET}"
    done
    if [ -n "$templates" ]; then
        echo ""
        echo -e "  ${BOLD}Templates:${RESET}"
        for tpl in $templates; do
            echo -e "    ${CYAN}$tpl${RESET}"
        done
    fi

    # ── Confirm + install ──
    echo ""
    echo -ne "  Set up this session? ${DIM}[Y/n]${RESET} "
    read -r confirm
    confirm="${confirm:-y}"
    [ "$confirm" = "n" ] || [ "$confirm" = "N" ] && return 0

    echo ""
    info "Installing resources..."
    echo ""
    install_resources "$target_dir" "$all_cmds" "$templates"

    # Save session config
    save_session "$name" "$target_dir" "$domain" "$needs" "$all_cmds" "$templates"

    # ── Launch? ──
    echo ""
    if command -v tmux &>/dev/null; then
        echo -ne "  Launch session now? ${DIM}[Y/n]${RESET} "
        read -r launch_confirm
        launch_confirm="${launch_confirm:-y}"
        if [ "$launch_confirm" != "n" ] && [ "$launch_confirm" != "N" ]; then
            cmd_open "$name"
            return
        fi
    fi

    echo ""
    echo -e "${BOLD}${GREEN}  Session ready.${RESET}"
    echo ""
    echo "  Open it:"
    echo -e "    ${CYAN}agent-deck open $name${RESET}"
    echo ""
    echo "  Add more agents:"
    echo -e "    ${CYAN}agent-deck spawn $name${RESET}"
    echo ""
}

# ── open: attach to or create a tmux session ──────────────────────────
cmd_open() {
    require_tmux
    local name="$1"

    # Add prefix if needed
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    # If tmux session exists, attach
    if tmux_session_exists "$name"; then
        echo -e "${GREEN}Attaching to: ${name}${RESET}"
        tmux attach -t "$name"
        return
    fi

    # Try to load session config for the project dir
    local project_dir=""
    if [ -f "$SESSIONS_DIR/$name.conf" ]; then
        # shellcheck disable=SC1090
        source "$SESSIONS_DIR/$name.conf"
        project_dir="$PROJECT_DIR"
    fi

    if [ -z "$project_dir" ] || [ ! -d "$project_dir" ]; then
        err "No session config for '$name'. Run: agent-deck setup <project-dir>"
        return 1
    fi

    echo -e "${GREEN}Launching: ${name}${RESET}"
    echo -e "${DIM}Project: ${project_dir}${RESET}"

    tmux new-session -d -s "$name" -c "$project_dir"
    tmux send-keys -t "$name" 'claude' Enter
    tmux attach -t "$name"
}

# ── spawn: add another agent window to a running session ──────────────
cmd_spawn() {
    require_tmux
    local name="$1"
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    if ! tmux_session_exists "$name"; then
        # If session config exists, open it first
        if [ -f "$SESSIONS_DIR/$name.conf" ]; then
            cmd_open "$name"
            return
        fi
        err "No running session: $name"
        return 1
    fi

    local window_count
    window_count=$(tmux_window_count "$name")
    local new_window="agent-$((window_count + 1))"

    echo -e "${GREEN}Spawning agent window: ${new_window}${RESET}"

    tmux new-window -t "$name" -n "$new_window"
    tmux send-keys -t "$name:$new_window" 'claude' Enter

    # If we're not attached, attach
    if [ -z "${TMUX:-}" ]; then
        tmux attach -t "$name"
    else
        tmux select-window -t "$name:$new_window"
    fi
}

# ── list: show all sessions ───────────────────────────────────────────
cmd_list() {
    echo ""
    echo -e "${BOLD}${BLUE}  Sessions${RESET}"
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"

    local has_any=false

    for file in "$SESSIONS_DIR"/*.conf 2>/dev/null; do
        [ -f "$file" ] || continue
        has_any=true

        local name project_dir domain
        name=$(basename "$file" .conf)
        project_dir=$(grep '^PROJECT_DIR=' "$file" | cut -d= -f2)
        domain=$(grep '^DOMAIN=' "$file" | cut -d= -f2)

        local status_icon windows_info
        if command -v tmux &>/dev/null && tmux_session_exists "$name"; then
            local wc
            wc=$(tmux_window_count "$name")
            status_icon="${GREEN}●${RESET}"
            windows_info=" ${DIM}(${wc} agent$([ "$wc" != "1" ] && echo "s"))${RESET}"
        else
            status_icon="${DIM}○${RESET}"
            windows_info=""
        fi

        echo -e "  $status_icon ${BOLD}$name${RESET}$windows_info  ${DIM}$domain${RESET}"
        echo -e "    ${DIM}$project_dir${RESET}"
    done

    if [ "$has_any" = false ]; then
        echo -e "  ${DIM}No sessions. Run: agent-deck setup <project-dir>${RESET}"
    fi
    echo ""
}

# ── kill: terminate a session ─────────────────────────────────────────
cmd_kill() {
    require_tmux
    local name="$1"
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    if ! tmux_session_exists "$name"; then
        err "No running session: $name"
        return 1
    fi

    tmux kill-session -t "$name"
    ok "Killed: $name"
}

# ── home: interactive dashboard ───────────────────────────────────────
cmd_home() {
    echo ""
    echo -e "${BOLD}${BLUE}  Agent Deck${RESET}"

    cmd_list

    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo -e "  ${CYAN}s${RESET}etup <dir>   ${CYAN}o${RESET}pen <name>   s${CYAN}p${RESET}awn <name>   ${CYAN}k${RESET}ill <name>   ${CYAN}q${RESET}uit"
    echo ""

    while true; do
        echo -ne "  ${BOLD}>${RESET} "
        read -r input

        case "$input" in
            q|quit|exit) break ;;
            s\ *|setup\ *)
                local dir="${input#* }"
                cmd_setup "$dir"
                cmd_list
                ;;
            o\ *|open\ *)
                local target="${input#* }"
                cmd_open "$target"
                break
                ;;
            p\ *|spawn\ *)
                local target="${input#* }"
                cmd_spawn "$target"
                break
                ;;
            k\ *|kill\ *)
                local target="${input#* }"
                cmd_kill "$target"
                echo ""
                ;;
            l|list|ls)
                cmd_list
                ;;
            *)
                echo -e "  ${DIM}setup <dir>  open <name>  spawn <name>  kill <name>  list  quit${RESET}"
                ;;
        esac
    done
}

# ── help ──────────────────────────────────────────────────────────────
usage() {
    echo "agent-deck - Home base for Claude Code sessions"
    echo ""
    echo "A session is scoped to a project folder. It can run multiple"
    echo "agent windows — each a Claude Code instance or supporting tool."
    echo ""
    echo "Usage:"
    echo "  agent-deck                        Home base (interactive)"
    echo "  agent-deck setup [dir]            Create + configure a session"
    echo "  agent-deck open <session>         Open a session"
    echo "  agent-deck spawn <session>        Add another agent window"
    echo "  agent-deck list                   List all sessions"
    echo "  agent-deck kill <session>         Kill a session"
    echo ""
    echo "Sessions: $SESSIONS_DIR"
    echo "Cache:    $ACC_CACHE"
}

# ── Helpers ───────────────────────────────────────────────────────────
require_tmux() {
    if ! command -v tmux &>/dev/null; then
        err "tmux is required for session management."
        echo -e "Install: ${CYAN}sudo apt install tmux${RESET} or ${CYAN}brew install tmux${RESET}"
        exit 1
    fi
}

# ── Main ──────────────────────────────────────────────────────────────
main() {
    init_deck

    local cmd="${1:-}"

    case "$cmd" in
        # Works without tmux
        setup)          shift; cmd_setup "$@" ;;
        list|ls)        cmd_list ;;
        help|-h|--help) usage ;;

        # Requires tmux
        open|o)
            [ -z "${2:-}" ] && err "Usage: agent-deck open <session>" && exit 1
            cmd_open "$2"
            ;;
        spawn|p)
            [ -z "${2:-}" ] && err "Usage: agent-deck spawn <session>" && exit 1
            cmd_spawn "$2"
            ;;
        kill|rm)
            [ -z "${2:-}" ] && err "Usage: agent-deck kill <session>" && exit 1
            cmd_kill "$2"
            ;;
        *)
            require_tmux; cmd_home
            ;;
    esac
}

main "$@"
