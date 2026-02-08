#!/usr/bin/env bash
# agent-deck - Collection manager + tmux session launcher for Claude Code
#
# Creates and manages "collections" — named sets of resources tailored to a
# project type. Each collection is saved as a config file so it can be
# re-applied to new projects. The deck is your home base; sub-sessions are
# spawned for each project.
#
# Usage:
#   agent-deck                          # Home base (interactive)
#   agent-deck new                      # Create a new collection (guided)
#   agent-deck install <collection> [dir]  # Install collection into a project
#   agent-deck launch <path>            # Spawn a Claude Code sub-session
#   agent-deck list                     # List collections + active sessions
#   agent-deck status                   # Show running sessions
#   agent-deck attach <name>            # Attach to a running session
#   agent-deck kill <name>              # Kill a session

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────
DECK_HOME="${AGENT_DECK_HOME:-$HOME/.agent-deck}"
COLLECTIONS_DIR="$DECK_HOME/collections"
ACC_REPO_URL="https://github.com/hesreallyhim/awesome-claude-code.git"
ACC_CACHE="$DECK_HOME/cache/awesome-claude-code"
SESSION_PREFIX="deck"

SEARCH_DIRS=("$HOME/projects" "$HOME/repos" "$HOME/code" "$HOME/work" "$HOME")
MAX_DEPTH=3

# ── Colors ────────────────────────────────────────────────────────────
if [ -t 1 ]; then
    BOLD='\033[1m' DIM='\033[2m'
    GREEN='\033[0;32m' YELLOW='\033[0;33m' CYAN='\033[0;36m'
    RED='\033[0;31m' BLUE='\033[0;34m' RESET='\033[0m'
else
    BOLD='' DIM='' GREEN='' YELLOW='' CYAN='' RED='' BLUE='' RESET=''
fi

info()  { echo -e "${CYAN}${BOLD}>>>${RESET} $*"; }
ok()    { echo -e "${GREEN}${BOLD} +${RESET} $*"; }
warn()  { echo -e "${YELLOW}${BOLD} !${RESET} $*"; }
err()   { echo -e "${RED}${BOLD} x${RESET} $*" >&2; }

# ── Init ──────────────────────────────────────────────────────────────
init_deck() {
    mkdir -p "$COLLECTIONS_DIR"
    mkdir -p "$DECK_HOME/cache"
}

# ── ACC repo cache ────────────────────────────────────────────────────
ensure_acc() {
    if [ -d "$ACC_CACHE/resources" ]; then
        # Refresh if older than 1 day
        local age=0
        if [ -f "$ACC_CACHE/.fetch_time" ]; then
            local fetch_time
            fetch_time=$(cat "$ACC_CACHE/.fetch_time")
            age=$(( $(date +%s) - fetch_time ))
        fi
        if [ "$age" -gt 86400 ]; then
            info "Updating resource cache..."
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
    ok "Resources cached at $ACC_CACHE"
}

# ── Domain/needs mapping ──────────────────────────────────────────────
# Returns space-separated list of command names
commands_for_domain() {
    local domain="$1"
    case "$domain" in
        ml)          echo "mlflow-log-model uc-register-model feature-table databricks-deploy" ;;
        databricks)  echo "databricks-job databricks-deploy feature-table mlflow-log-model uc-register-model" ;;
        backend)     echo "" ;;
        frontend)    echo "" ;;
        devops)      echo "act create-hook husky" ;;
        cli)         echo "" ;;
        general)     echo "" ;;
    esac
}

templates_for_domain() {
    local domain="$1"
    case "$domain" in
        ml)          echo "DSPy MLflow-Databricks Feature-Engineering Vector-Search Mosaic-AI-Agents Databricks-AI-Dev-Kit" ;;
        databricks)  echo "Databricks-Full-Stack Delta-Live-Tables Databricks-Jobs Unity-Catalog" ;;
        backend)     echo "SG-Cars-Trends-Backend LangGraphJS AWS-MCP-Server Giselle" ;;
        frontend)    echo "APX-Databricks-Apps Course-Builder JSBeeb" ;;
        devops)      echo "Databricks-MCP-Server claude-code-mcp-enhanced" ;;
        cli)         echo "TPL Cursor-Tools" ;;
        general)     echo "Basic-Memory" ;;
    esac
}

commands_for_needs() {
    local needs="$1"
    local cmds=""
    if echo "$needs" | grep -q "git"; then
        cmds="$cmds create-pr fix-github-issue create-worktrees update-branch-name husky"
    fi
    if echo "$needs" | grep -q "quality"; then
        cmds="$cmds testing_plan_integration create-hook"
    fi
    if echo "$needs" | grep -q "context"; then
        cmds="$cmds context-prime initref load-llms-txt"
    fi
    if echo "$needs" | grep -q "docs"; then
        cmds="$cmds update-docs add-to-changelog"
    fi
    if echo "$needs" | grep -q "deploy"; then
        cmds="$cmds release act"
    fi
    echo "$cmds"
}

# ── Collection management ─────────────────────────────────────────────

save_collection() {
    local name="$1" domain="$2" needs="$3" commands="$4" templates="$5"
    local file="$COLLECTIONS_DIR/$name.conf"

    cat > "$file" << EOF
# Agent Deck Collection: $name
# Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
DOMAIN=$domain
NEEDS=$needs
COMMANDS=$commands
TEMPLATES=$templates
EOF
    ok "Collection saved: $name"
}

load_collection() {
    local name="$1"
    local file="$COLLECTIONS_DIR/$name.conf"
    if [ ! -f "$file" ]; then
        err "Collection not found: $name"
        return 1
    fi
    # Source the collection config
    # shellcheck disable=SC1090
    source "$file"
}

list_collections() {
    echo -e "${BOLD}${BLUE}  Collections${RESET}"
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"

    if [ ! -d "$COLLECTIONS_DIR" ] || [ -z "$(ls "$COLLECTIONS_DIR"/*.conf 2>/dev/null)" ]; then
        echo -e "  ${DIM}No collections yet. Run: agent-deck new${RESET}"
        return
    fi

    for file in "$COLLECTIONS_DIR"/*.conf; do
        local name domain commands templates
        name=$(basename "$file" .conf)
        domain=$(grep '^DOMAIN=' "$file" | cut -d= -f2)
        commands=$(grep '^COMMANDS=' "$file" | cut -d= -f2 | wc -w | tr -d ' ')
        templates=$(grep '^TEMPLATES=' "$file" | cut -d= -f2 | wc -w | tr -d ' ')
        echo -e "  ${GREEN}${BOLD}$name${RESET}  ${DIM}($domain — ${commands} commands, ${templates} templates)${RESET}"
    done
}

# ── Create a new collection (guided) ──────────────────────────────────

cmd_new() {
    echo ""
    echo -e "${BOLD}${BLUE}  New Collection${RESET}"
    echo -e "${DIM}  Create a tailored set of resources${RESET}"
    echo ""

    # Name
    echo -ne "  ${BOLD}Collection name:${RESET} "
    read -r coll_name
    coll_name=$(echo "$coll_name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

    if [ -f "$COLLECTIONS_DIR/$coll_name.conf" ]; then
        warn "Collection '$coll_name' already exists."
        echo -n "  Overwrite? [y/N] "
        read -r confirm
        [ "$confirm" != "y" ] && [ "$confirm" != "Y" ] && return 0
    fi

    # Domain
    echo ""
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
    echo -n "  Choice [1-7]: "
    read -r domain_choice

    local domain
    case "$domain_choice" in
        1) domain="ml" ;;
        2) domain="databricks" ;;
        3) domain="backend" ;;
        4) domain="frontend" ;;
        5) domain="devops" ;;
        6) domain="cli" ;;
        *) domain="general" ;;
    esac

    # Needs
    echo ""
    echo -e "  ${BOLD}What do you need?${RESET} ${DIM}(multiple: e.g. 1 3 5)${RESET}"
    echo ""
    echo "    1) Git workflow"
    echo "    2) Code quality"
    echo "    3) Project context"
    echo "    4) Documentation"
    echo "    5) Deployment"
    echo "    6) Everything"
    echo ""
    echo -n "  Choice: "
    read -r needs_choice

    local needs=""
    for n in $needs_choice; do
        case "$n" in
            1) needs="$needs git" ;;
            2) needs="$needs quality" ;;
            3) needs="$needs context" ;;
            4) needs="$needs docs" ;;
            5) needs="$needs deploy" ;;
            6) needs="git quality context docs deploy" ;;
        esac
    done

    # Build resource lists
    local base_cmds="commit pr-review optimize setup"
    local domain_cmds
    domain_cmds=$(commands_for_domain "$domain")
    local needs_cmds
    needs_cmds=$(commands_for_needs "$needs")
    local all_cmds
    all_cmds=$(echo "$base_cmds $domain_cmds $needs_cmds" | tr ' ' '\n' | sort -u | tr '\n' ' ')

    local templates
    templates=$(templates_for_domain "$domain")

    # Preview
    echo ""
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo -e "  ${BOLD}Collection: ${GREEN}$coll_name${RESET}"
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

    echo ""
    echo -n "  Save this collection? [Y/n] "
    read -r confirm
    confirm="${confirm:-y}"
    [ "$confirm" = "n" ] || [ "$confirm" = "N" ] && return 0

    save_collection "$coll_name" "$domain" "$needs" "$all_cmds" "$templates"

    echo ""
    echo -e "  ${BOLD}Next:${RESET}"
    echo -e "    agent-deck install $coll_name /path/to/project"
    echo -e "    agent-deck launch /path/to/project"
    echo ""
}

# ── Install collection into a directory ───────────────────────────────

cmd_install() {
    local coll_name="${1:-}"
    local target_dir="${2:-$(pwd)}"

    if [ -z "$coll_name" ]; then
        echo ""
        list_collections
        echo ""
        echo -ne "  ${BOLD}Collection to install:${RESET} "
        read -r coll_name
    fi

    load_collection "$coll_name" || return 1
    ensure_acc || return 1

    if [ ! -d "$target_dir" ]; then
        info "Creating directory: $target_dir"
        mkdir -p "$target_dir"
    fi

    echo ""
    info "Installing collection '$coll_name' into $target_dir"
    echo ""

    # Install commands
    mkdir -p "$target_dir/.claude/commands"
    local cmd_count=0
    for cmd in $COMMANDS; do
        local src="$ACC_CACHE/resources/slash-commands/$cmd"
        if [ -d "$src" ]; then
            local md_file
            md_file=$(find "$src" -maxdepth 1 -name "*.md" | head -1)
            if [ -n "$md_file" ]; then
                local dest="$target_dir/.claude/commands/$(basename "$md_file")"
                if [ -f "$dest" ]; then
                    warn "Exists: .claude/commands/$(basename "$md_file")"
                else
                    cp "$md_file" "$dest"
                    ok "/$cmd"
                    cmd_count=$((cmd_count + 1))
                fi
            fi
        fi
    done

    # Install templates
    local tpl_count=0
    if [ -n "$TEMPLATES" ]; then
        for tpl in $TEMPLATES; do
            local src="$ACC_CACHE/resources/claude.md-files/$tpl/CLAUDE.md"
            if [ -f "$src" ]; then
                local dest="$target_dir/CLAUDE.md"
                local marker="# --- awesome-claude-code: $tpl ---"

                if [ -f "$dest" ] && grep -qF "$marker" "$dest" 2>/dev/null; then
                    warn "Template '$tpl' already in CLAUDE.md"
                else
                    {
                        [ -f "$dest" ] && echo ""
                        echo "$marker"
                        echo ""
                        cat "$src"
                    } >> "$dest"
                    ok "$tpl template"
                    tpl_count=$((tpl_count + 1))
                fi
            fi
        done
    fi

    echo ""
    ok "Installed $cmd_count commands + $tpl_count templates"
    echo ""
    echo -e "  ${BOLD}Launch a session:${RESET}"
    echo -e "    agent-deck launch $target_dir"
    echo ""
}

# ── Session management ────────────────────────────────────────────────

session_name() {
    local path="$1"
    local name
    name=$(basename "$path" | tr '.' '-' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    echo "${SESSION_PREFIX}-${name}"
}

session_exists() {
    tmux has-session -t "$1" 2>/dev/null
}

cmd_launch() {
    local project_path="$1"

    if [ ! -d "$project_path" ]; then
        err "Directory not found: $project_path"
        return 1
    fi

    # Resolve to absolute path
    project_path="$(cd "$project_path" && pwd)"

    local name
    name=$(session_name "$project_path")

    if session_exists "$name"; then
        echo -e "${YELLOW}Session '${name}' already running. Attaching...${RESET}"
        tmux attach -t "$name"
        return
    fi

    echo -e "${GREEN}Launching: ${name}${RESET}"
    echo -e "${DIM}Project: ${project_path}${RESET}"

    tmux new-session -d -s "$name" -c "$project_path"
    tmux send-keys -t "$name" 'claude' Enter
    tmux attach -t "$name"
}

cmd_attach() {
    local name="$1"
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    if ! session_exists "$name"; then
        err "No session: $name"
        cmd_status
        return 1
    fi

    tmux attach -t "$name"
}

cmd_kill() {
    local name="$1"
    [[ "$name" == ${SESSION_PREFIX}-* ]] || name="${SESSION_PREFIX}-${name}"

    if ! session_exists "$name"; then
        err "No session: $name"
        return 1
    fi

    tmux kill-session -t "$name"
    ok "Killed: $name"
}

cmd_status() {
    echo -e "${BOLD}${BLUE}  Active Sessions${RESET}"
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"

    local sessions
    sessions=$(tmux list-sessions -F '#{session_name} #{session_path} #{session_windows} #{session_created}' 2>/dev/null | grep "^${SESSION_PREFIX}-" || true)

    if [ -z "$sessions" ]; then
        echo -e "  ${DIM}No active sessions.${RESET}"
        return
    fi

    while IFS=' ' read -r name path windows created; do
        local now age human_age
        now=$(date +%s)
        age=$(( now - created ))
        if [ $age -lt 3600 ]; then
            human_age="$((age / 60))m"
        elif [ $age -lt 86400 ]; then
            human_age="$((age / 3600))h"
        else
            human_age="$((age / 86400))d"
        fi
        echo -e "  ${GREEN}●${RESET} ${BOLD}${name}${RESET}  ${DIM}(${windows}w, ${human_age})${RESET}  ${DIM}${path}${RESET}"
    done <<< "$sessions"
}

# ── Discover projects ─────────────────────────────────────────────────
discover_projects() {
    local found=()
    for dir in "${SEARCH_DIRS[@]}"; do
        [ -d "$dir" ] || continue
        while IFS= read -r -d '' claude_file; do
            local project_dir
            project_dir="$(dirname "$claude_file")"
            if [[ "$claude_file" == *"/.claude" ]]; then
                project_dir="$(dirname "$claude_file")"
            fi
            local already=false
            for p in "${found[@]+"${found[@]}"}"; do
                [ "$p" = "$project_dir" ] && already=true && break
            done
            $already || found+=("$project_dir")
        done < <(find "$dir" -maxdepth "$MAX_DEPTH" -name "CLAUDE.md" -print0 2>/dev/null)

        while IFS= read -r -d '' claude_dir; do
            local project_dir
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

# ── Home base (interactive) ───────────────────────────────────────────
cmd_home() {
    echo ""
    echo -e "${BOLD}${BLUE}  Agent Deck${RESET}"
    echo -e "${DIM}  Your Claude Code home base${RESET}"
    echo ""

    # Show collections
    list_collections
    echo ""

    # Show active sessions
    cmd_status
    echo ""

    # Show discovered projects
    echo -e "${BOLD}${BLUE}  Projects${RESET}"
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"

    local projects=()
    while IFS= read -r line; do
        [ -n "$line" ] && projects+=("$line")
    done < <(discover_projects)

    if [ ${#projects[@]} -eq 0 ]; then
        echo -e "  ${DIM}No Claude Code projects found.${RESET}"
    else
        local idx=1
        for project in "${projects[@]}"; do
            local name
            name=$(session_name "$project")
            local status_icon
            if session_exists "$name"; then
                status_icon="${GREEN}●${RESET}"
            else
                status_icon="${DIM}○${RESET}"
            fi
            echo -e "  ${BOLD}${idx})${RESET} $status_icon ${BOLD}$(basename "$project")${RESET}  ${DIM}${project}${RESET}"
            ((idx++))
        done
    fi

    echo ""
    echo -e "${DIM}  ─────────────────────────────────────────${RESET}"
    echo -e "  ${CYAN}n${RESET}ew collection  ${CYAN}i${RESET}nstall  ${CYAN}<num>${RESET} launch  ${CYAN}s${RESET}tatus  ${CYAN}q${RESET}uit"
    echo ""

    while true; do
        echo -ne "  ${BOLD}>${RESET} "
        read -r input

        case "$input" in
            q|quit|exit) break ;;
            n|new) cmd_new ;;
            i|install)
                echo -ne "  Collection name: "
                read -r cname
                echo -ne "  Target directory: "
                read -r tdir
                cmd_install "$cname" "$tdir"
                ;;
            s|status) echo ""; cmd_status; echo "" ;;
            k\ *)
                local target="${input#k }"
                cmd_kill "$target"
                ;;
            ''|*[!0-9]*)
                echo -e "  ${DIM}n=new  i=install  <num>=launch  s=status  k <name>=kill  q=quit${RESET}"
                ;;
            *)
                local idx=$((input - 1))
                if [ "$idx" -ge 0 ] && [ "$idx" -lt ${#projects[@]} ]; then
                    cmd_launch "${projects[$idx]}"
                    break
                else
                    echo -e "  ${RED}Invalid selection.${RESET}"
                fi
                ;;
        esac
    done
}

# ── Usage ─────────────────────────────────────────────────────────────
usage() {
    echo "agent-deck - Collection manager + session launcher for Claude Code"
    echo ""
    echo "Usage:"
    echo "  agent-deck                              Home base (interactive)"
    echo "  agent-deck new                          Create a new collection"
    echo "  agent-deck install <collection> [dir]   Install collection into project"
    echo "  agent-deck launch <path>                Spawn Claude Code sub-session"
    echo "  agent-deck list                         List collections"
    echo "  agent-deck status                       Show active sessions"
    echo "  agent-deck attach <name>                Attach to session"
    echo "  agent-deck kill <name>                  Kill a session"
    echo ""
    echo "Collections are saved to: $COLLECTIONS_DIR"
    echo "Resource cache: $ACC_CACHE"
}

# ── Main ──────────────────────────────────────────────────────────────
main() {
    init_deck

    if ! command -v tmux &>/dev/null; then
        err "tmux is not installed."
        echo -e "Install: ${CYAN}sudo apt install tmux${RESET} or ${CYAN}brew install tmux${RESET}"
        exit 1
    fi

    local cmd="${1:-}"

    case "$cmd" in
        new)                cmd_new ;;
        install|setup)      shift; cmd_install "$@" ;;
        launch|start)
            [ -z "${2:-}" ] && err "Usage: agent-deck launch <path>" && exit 1
            cmd_launch "$2"
            ;;
        attach|a)
            [ -z "${2:-}" ] && err "Usage: agent-deck attach <name>" && exit 1
            cmd_attach "$2"
            ;;
        kill|rm)
            [ -z "${2:-}" ] && err "Usage: agent-deck kill <name>" && exit 1
            cmd_kill "$2"
            ;;
        list|ls)            list_collections ;;
        status|st)          cmd_status ;;
        help|-h|--help)     usage ;;
        *)                  cmd_home ;;
    esac
}

main "$@"
