#!/usr/bin/env bash
# agent-deck - tmux session manager for Claude Code projects
#
# Discovers all Claude Code projects (directories containing CLAUDE.md or .claude/)
# and provides a navigable dashboard to launch, attach, and manage sessions.
#
# Compatible with macOS (bash 3.2+) and Linux.
# On macOS: brew install bash tmux (recommended for bash 4+ features, but not required)
#
# Usage:
#   agent-deck                  # Interactive project picker
#   agent-deck list             # List all discovered projects
#   agent-deck launch <path>    # Launch a Claude session for a project
#   agent-deck attach <name>    # Attach to a running session
#   agent-deck kill <name>      # Kill a session
#   agent-deck status           # Show all active agent sessions

set -euo pipefail

SEARCH_DIRS=("$HOME/projects" "$HOME/repos" "$HOME/code" "$HOME/work" "$HOME")
MAX_DEPTH=3
SESSION_PREFIX="agent"

# Detect OS
IS_MACOS=false
[[ "$(uname -s)" == "Darwin" ]] && IS_MACOS=true

# ── Colors ──────────────────────────────────────────────────────────
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Discover Claude Code projects ──────────────────────────────────
discover_projects() {
    local found=()
    for dir in "${SEARCH_DIRS[@]}"; do
        [ -d "$dir" ] || continue
        while IFS= read -r -d '' claude_file; do
            project_dir="$(dirname "$claude_file")"
            # If we found .claude/commands, go up two levels
            if [[ "$claude_file" == *"/.claude" ]]; then
                project_dir="$(dirname "$claude_file")"
            fi
            # Deduplicate
            local already=false
            for p in "${found[@]+"${found[@]}"}"; do
                [ "$p" = "$project_dir" ] && already=true && break
            done
            $already || found+=("$project_dir")
        done < <(find "$dir" -maxdepth "$MAX_DEPTH" -name "CLAUDE.md" -print0 2>/dev/null)

        while IFS= read -r -d '' claude_dir; do
            project_dir="$(dirname "$claude_dir")"
            local already=false
            for p in "${found[@]+"${found[@]}"}"; do
                [ "$p" = "$project_dir" ] && already=true && break
            done
            $already || found+=("$project_dir")
        done < <(find "$dir" -maxdepth "$MAX_DEPTH" -type d -name ".claude" -print0 2>/dev/null)
    done
    printf '%s\n' "${found[@]+"${found[@]}"}" | sort -u
}

# ── Session name from path ─────────────────────────────────────────
session_name() {
    local path="$1"
    local name
    name=$(basename "$path" | tr '.' '-' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    echo "${SESSION_PREFIX}-${name}"
}

# ── Check if session exists ────────────────────────────────────────
session_exists() {
    tmux has-session -t "$1" 2>/dev/null
}

# ── Read projects into array (bash 3.2 compatible) ────────────────
# mapfile/readarray is bash 4+ only; this works on macOS default bash
load_projects() {
    PROJECTS=()
    while IFS= read -r line; do
        [ -n "$line" ] && PROJECTS+=("$line")
    done < <(discover_projects)
}

# ── List projects ─────────────────────────────────────────────────
cmd_list() {
    echo -e "${BOLD}${BLUE}  Agent Deck - Claude Code Projects${RESET}"
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo ""

    load_projects

    if [ ${#PROJECTS[@]} -eq 0 ]; then
        echo -e "  ${YELLOW}No Claude Code projects found.${RESET}"
        echo -e "  ${DIM}Searched: ${SEARCH_DIRS[*]}${RESET}"
        echo -e "  ${DIM}Looking for: CLAUDE.md or .claude/ directories${RESET}"
        return
    fi

    local idx=1
    for project in "${PROJECTS[@]}"; do
        local name
        name=$(session_name "$project")
        local status_icon

        if session_exists "$name"; then
            status_icon="${GREEN}● running${RESET}"
        else
            status_icon="${DIM}○ idle${RESET}"
        fi

        local has_claude_md=""
        local has_dot_claude=""
        [ -f "$project/CLAUDE.md" ] && has_claude_md="${CYAN}CLAUDE.md${RESET} "
        [ -d "$project/.claude" ] && has_dot_claude="${CYAN}.claude/${RESET} "

        echo -e "  ${BOLD}${idx})${RESET}  ${status_icon}  ${BOLD}$(basename "$project")${RESET}"
        echo -e "      ${DIM}${project}${RESET}"
        echo -e "      ${has_claude_md}${has_dot_claude}"
        ((idx++))
    done
}

# ── Launch a Claude session ────────────────────────────────────────
cmd_launch() {
    local project_path="$1"

    if [ ! -d "$project_path" ]; then
        echo -e "${RED}Error: Directory not found: ${project_path}${RESET}"
        return 1
    fi

    local name
    name=$(session_name "$project_path")

    if session_exists "$name"; then
        echo -e "${YELLOW}Session '${name}' already running. Attaching...${RESET}"
        tmux attach -t "$name"
        return
    fi

    echo -e "${GREEN}Launching agent session: ${name}${RESET}"
    echo -e "${DIM}Project: ${project_path}${RESET}"

    tmux new-session -d -s "$name" -c "$project_path"
    tmux send-keys -t "$name" 'claude' Enter
    tmux attach -t "$name"
}

# ── Attach to session ─────────────────────────────────────────────
cmd_attach() {
    local name="$1"

    # Add prefix if not present
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    if ! session_exists "$name"; then
        echo -e "${RED}No session named '${name}'. Active sessions:${RESET}"
        cmd_status
        return 1
    fi

    tmux attach -t "$name"
}

# ── Kill a session ─────────────────────────────────────────────────
cmd_kill() {
    local name="$1"
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    if ! session_exists "$name"; then
        echo -e "${RED}No session named '${name}'.${RESET}"
        return 1
    fi

    tmux kill-session -t "$name"
    echo -e "${GREEN}Killed session: ${name}${RESET}"
}

# ── Status of all agent sessions ──────────────────────────────────
cmd_status() {
    echo -e "${BOLD}${BLUE}  Agent Deck - Active Sessions${RESET}"
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo ""

    local sessions
    sessions=$(tmux list-sessions -F '#{session_name} #{session_path} #{session_windows} #{session_created}' 2>/dev/null | grep "^${SESSION_PREFIX}-" || true)

    if [ -z "$sessions" ]; then
        echo -e "  ${DIM}No active agent sessions.${RESET}"
        echo -e "  ${DIM}Use 'agent-deck' to launch one.${RESET}"
        return
    fi

    while IFS=' ' read -r name path windows created; do
        local now age human_age
        now=$(date +%s)
        age=$(( now - created ))
        if [ $age -lt 3600 ]; then
            human_age="$((age / 60))m ago"
        elif [ $age -lt 86400 ]; then
            human_age="$((age / 3600))h ago"
        else
            human_age="$((age / 86400))d ago"
        fi

        echo -e "  ${GREEN}●${RESET} ${BOLD}${name}${RESET}  ${DIM}(${windows} windows, started ${human_age})${RESET}"
        echo -e "    ${DIM}${path}${RESET}"
    done <<< "$sessions"
}

# ── Interactive picker ─────────────────────────────────────────────
cmd_interactive() {
    cmd_list
    echo ""

    load_projects

    [ ${#PROJECTS[@]} -eq 0 ] && return

    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo -e "  ${BOLD}Commands:${RESET}"
    echo -e "  ${CYAN}<number>${RESET}  Launch/attach to project"
    echo -e "  ${CYAN}s${RESET}        Show active sessions"
    echo -e "  ${CYAN}k <name>${RESET} Kill a session"
    echo -e "  ${CYAN}q${RESET}        Quit"
    echo ""

    while true; do
        echo -ne "  ${BOLD}>${RESET} "
        read -r input

        case "$input" in
            q|quit|exit)
                break
                ;;
            s|status)
                echo ""
                cmd_status
                echo ""
                ;;
            k\ *)
                local target="${input#k }"
                cmd_kill "$target"
                echo ""
                ;;
            ''|*[!0-9]*)
                echo -e "  ${DIM}Enter a number, 's', 'k <name>', or 'q'${RESET}"
                ;;
            *)
                local idx=$((input - 1))
                if [ "$idx" -ge 0 ] && [ "$idx" -lt ${#PROJECTS[@]} ]; then
                    cmd_launch "${PROJECTS[$idx]}"
                    break
                else
                    echo -e "  ${RED}Invalid selection.${RESET}"
                fi
                ;;
        esac
    done
}

# ── Main ───────────────────────────────────────────────────────────
main() {
    if ! command -v tmux &>/dev/null; then
        echo -e "${RED}Error: tmux is not installed.${RESET}"
        echo -e "Install with: ${CYAN}sudo apt install tmux${RESET} or ${CYAN}brew install tmux${RESET}"
        exit 1
    fi

    local cmd="${1:-}"

    case "$cmd" in
        list|ls)
            cmd_list
            ;;
        launch|start)
            [ -z "${2:-}" ] && echo -e "${RED}Usage: agent-deck launch <path>${RESET}" && exit 1
            cmd_launch "$2"
            ;;
        attach|a)
            [ -z "${2:-}" ] && echo -e "${RED}Usage: agent-deck attach <name>${RESET}" && exit 1
            cmd_attach "$2"
            ;;
        kill|rm)
            [ -z "${2:-}" ] && echo -e "${RED}Usage: agent-deck kill <name>${RESET}" && exit 1
            cmd_kill "$2"
            ;;
        status|st)
            cmd_status
            ;;
        help|-h|--help)
            echo "agent-deck - tmux session manager for Claude Code projects"
            echo ""
            echo "Usage:"
            echo "  agent-deck                  Interactive project picker"
            echo "  agent-deck list             List all discovered projects"
            echo "  agent-deck launch <path>    Launch a Claude session for a project"
            echo "  agent-deck attach <name>    Attach to a running session"
            echo "  agent-deck kill <name>      Kill a session"
            echo "  agent-deck status           Show all active agent sessions"
            echo ""
            echo "Search directories: ${SEARCH_DIRS[*]}"
            echo "Edit SEARCH_DIRS in this script to customize."
            ;;
        *)
            cmd_interactive
            ;;
    esac
}

main "$@"
