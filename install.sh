#!/usr/bin/env bash
# install.sh - Install awesome-claude-code resources into an existing project
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash
#   bash install.sh
#   bash install.sh --list
#   bash install.sh --pick slash-commands/commit
#   bash install.sh --pick claude.md-files/DSPy
#   bash install.sh --all-commands
#
# This script is non-destructive: it will not overwrite existing files
# without asking, and it cleans up after itself.

set -euo pipefail

REPO_URL="https://github.com/hesreallyhim/awesome-claude-code.git"
REPO_BRANCH="main"
CLEANUP_ON_EXIT=true

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
    BOLD='\033[1m'
    DIM='\033[2m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    RED='\033[0;31m'
    RESET='\033[0m'
else
    BOLD='' DIM='' GREEN='' YELLOW='' CYAN='' RED='' RESET=''
fi

info()  { echo -e "${CYAN}${BOLD}>>>${RESET} $*"; }
ok()    { echo -e "${GREEN}${BOLD} +${RESET} $*"; }
warn()  { echo -e "${YELLOW}${BOLD} !${RESET} $*"; }
err()   { echo -e "${RED}${BOLD} x${RESET} $*" >&2; }

# ─── Temp directory management ───────────────────────────────────────────────

TMPDIR_ACC=""

cleanup() {
    if [ "$CLEANUP_ON_EXIT" = true ] && [ -n "$TMPDIR_ACC" ] && [ -d "$TMPDIR_ACC" ]; then
        rm -rf "$TMPDIR_ACC"
    fi
}

trap cleanup EXIT

ensure_repo() {
    if [ -n "$TMPDIR_ACC" ] && [ -d "$TMPDIR_ACC/resources" ]; then
        return 0
    fi

    TMPDIR_ACC=$(mktemp -d 2>/dev/null || mktemp -d -t acc-install)
    info "Fetching awesome-claude-code resources..."

    if ! git clone --depth 1 --branch "$REPO_BRANCH" --single-branch \
         "$REPO_URL" "$TMPDIR_ACC" 2>/dev/null; then
        err "Failed to clone repository. Check your network connection."
        exit 1
    fi

    ok "Resources fetched."
}

# ─── Target project detection ────────────────────────────────────────────────

TARGET_DIR="$(pwd)"

detect_project_type() {
    # Returns detected info about the project
    DETECTED_LANG=""
    DETECTED_FRAMEWORK=""
    DETECTED_HAS_CLAUDE=""
    DETECTED_HAS_TESTS=""
    DETECTED_HAS_CI=""

    # Language detection
    if [ -f "$TARGET_DIR/pyproject.toml" ] || [ -f "$TARGET_DIR/setup.py" ] || [ -f "$TARGET_DIR/requirements.txt" ]; then
        DETECTED_LANG="python"
    elif [ -f "$TARGET_DIR/package.json" ]; then
        DETECTED_LANG="javascript"
    elif [ -f "$TARGET_DIR/Cargo.toml" ]; then
        DETECTED_LANG="rust"
    elif [ -f "$TARGET_DIR/go.mod" ]; then
        DETECTED_LANG="go"
    elif [ -f "$TARGET_DIR/pom.xml" ] || [ -f "$TARGET_DIR/build.gradle" ]; then
        DETECTED_LANG="java"
    elif [ -f "$TARGET_DIR/Gemfile" ]; then
        DETECTED_LANG="ruby"
    fi

    # Framework hints
    if [ -f "$TARGET_DIR/package.json" ]; then
        if grep -q '"react"' "$TARGET_DIR/package.json" 2>/dev/null; then
            DETECTED_FRAMEWORK="react"
        elif grep -q '"next"' "$TARGET_DIR/package.json" 2>/dev/null; then
            DETECTED_FRAMEWORK="nextjs"
        elif grep -q '"fastify"' "$TARGET_DIR/package.json" 2>/dev/null; then
            DETECTED_FRAMEWORK="fastify"
        elif grep -q '"express"' "$TARGET_DIR/package.json" 2>/dev/null; then
            DETECTED_FRAMEWORK="express"
        fi
    fi
    if [ -f "$TARGET_DIR/pyproject.toml" ]; then
        if grep -q 'fastapi' "$TARGET_DIR/pyproject.toml" 2>/dev/null; then
            DETECTED_FRAMEWORK="fastapi"
        elif grep -q 'django' "$TARGET_DIR/pyproject.toml" 2>/dev/null; then
            DETECTED_FRAMEWORK="django"
        elif grep -q 'flask' "$TARGET_DIR/pyproject.toml" 2>/dev/null; then
            DETECTED_FRAMEWORK="flask"
        elif grep -q 'mlflow\|databricks\|pyspark' "$TARGET_DIR/pyproject.toml" 2>/dev/null; then
            DETECTED_FRAMEWORK="databricks"
        fi
    fi

    # Existing Claude Code setup
    if [ -d "$TARGET_DIR/.claude" ] || [ -f "$TARGET_DIR/CLAUDE.md" ]; then
        DETECTED_HAS_CLAUDE="yes"
    fi

    # Tests
    if [ -d "$TARGET_DIR/tests" ] || [ -d "$TARGET_DIR/test" ] || [ -d "$TARGET_DIR/__tests__" ]; then
        DETECTED_HAS_TESTS="yes"
    fi

    # CI
    if [ -d "$TARGET_DIR/.github/workflows" ] || [ -f "$TARGET_DIR/.gitlab-ci.yml" ] || [ -f "$TARGET_DIR/Jenkinsfile" ]; then
        DETECTED_HAS_CI="yes"
    fi
}

detect_project() {
    if [ ! -d "$TARGET_DIR/.git" ] && [ ! -f "$TARGET_DIR/package.json" ] && \
       [ ! -f "$TARGET_DIR/pyproject.toml" ] && [ ! -f "$TARGET_DIR/Cargo.toml" ] && \
       [ ! -f "$TARGET_DIR/go.mod" ] && [ ! -f "$TARGET_DIR/Makefile" ] && \
       [ ! -f "$TARGET_DIR/Gemfile" ] && [ ! -f "$TARGET_DIR/pom.xml" ]; then
        warn "This doesn't look like a project directory."
        echo -n "Continue installing to $(pwd)? [y/N] "
        read -r confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "Aborted."
            exit 0
        fi
    fi
}

# ─── Resource listing ────────────────────────────────────────────────────────

list_resources() {
    ensure_repo

    echo ""
    echo -e "${BOLD}Available Resources${RESET}"
    echo -e "${DIM}────────────────────────────────────────${RESET}"
    echo ""

    echo -e "${BOLD}Slash Commands${RESET} ${DIM}(install to .claude/commands/)${RESET}"
    for dir in "$TMPDIR_ACC"/resources/slash-commands/*/; do
        name=$(basename "$dir")
        echo -e "  ${GREEN}slash-commands/$name${RESET}"
    done

    echo ""
    echo -e "${BOLD}CLAUDE.md Templates${RESET} ${DIM}(append to CLAUDE.md)${RESET}"
    for dir in "$TMPDIR_ACC"/resources/claude.md-files/*/; do
        name=$(basename "$dir")
        echo -e "  ${CYAN}claude.md-files/$name${RESET}"
    done

    echo ""
    echo -e "${BOLD}Workflow Guides${RESET} ${DIM}(reference material)${RESET}"
    for dir in "$TMPDIR_ACC"/resources/workflows-knowledge-guides/*/; do
        name=$(basename "$dir")
        echo -e "  ${YELLOW}workflows-knowledge-guides/$name${RESET}"
    done

    echo ""
    echo -e "${DIM}Usage:${RESET}"
    echo -e "  bash install.sh --pick slash-commands/commit"
    echo -e "  bash install.sh --pick claude.md-files/DSPy"
    echo -e "  bash install.sh --all-commands"
    echo ""
}

# ─── Install helpers ─────────────────────────────────────────────────────────

install_slash_command() {
    local name="$1"
    local src="$TMPDIR_ACC/resources/slash-commands/$name"

    if [ ! -d "$src" ]; then
        err "Slash command not found: $name"
        return 1
    fi

    local md_file
    md_file=$(find "$src" -maxdepth 1 -name "*.md" | head -1)
    if [ -z "$md_file" ]; then
        err "No .md file found in slash-commands/$name"
        return 1
    fi

    mkdir -p "$TARGET_DIR/.claude/commands"
    local dest="$TARGET_DIR/.claude/commands/$(basename "$md_file")"

    if [ -f "$dest" ]; then
        if [ "${FORCE_OVERWRITE:-}" = "true" ]; then
            cp "$md_file" "$dest"
            ok "Updated: .claude/commands/$(basename "$md_file")"
            return 0
        fi
        warn "Already exists: .claude/commands/$(basename "$md_file")"
        echo -n "  Overwrite? [y/N] "
        read -r confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "  Skipped."
            return 0
        fi
    fi

    cp "$md_file" "$dest"
    ok "Installed: .claude/commands/$(basename "$md_file")"
}

install_claude_md() {
    local name="$1"
    local src="$TMPDIR_ACC/resources/claude.md-files/$name/CLAUDE.md"

    if [ ! -f "$src" ]; then
        err "CLAUDE.md template not found: $name"
        return 1
    fi

    local dest="$TARGET_DIR/CLAUDE.md"

    if [ -f "$dest" ]; then
        local marker="# --- awesome-claude-code: $name ---"
        if grep -qF "$marker" "$dest" 2>/dev/null; then
            warn "Template '$name' already present in CLAUDE.md. Skipped."
            return 0
        fi

        info "Appending $name template to existing CLAUDE.md..."
        {
            echo ""
            echo "$marker"
            echo ""
            cat "$src"
        } >> "$dest"
        ok "Appended $name to CLAUDE.md"
    else
        info "Creating CLAUDE.md with $name template..."
        {
            echo "# --- awesome-claude-code: $name ---"
            echo ""
            cat "$src"
        } > "$dest"
        ok "Created CLAUDE.md with $name template"
    fi
}

install_workflow() {
    local name="$1"
    local src="$TMPDIR_ACC/resources/workflows-knowledge-guides/$name"

    if [ ! -d "$src" ]; then
        err "Workflow guide not found: $name"
        return 1
    fi

    local dest="$TARGET_DIR/.claude/workflows/$name"
    mkdir -p "$dest"

    cp -r "$src"/* "$dest"/
    ok "Installed workflow: .claude/workflows/$name/"
}

install_commands_by_name() {
    # Install a list of command names (space-separated)
    local commands="$1"
    for cmd in $commands; do
        if [ -d "$TMPDIR_ACC/resources/slash-commands/$cmd" ]; then
            install_slash_command "$cmd"
        fi
    done
}

install_templates_by_name() {
    # Install a list of template names (space-separated)
    local templates="$1"
    for tpl in $templates; do
        if [ -d "$TMPDIR_ACC/resources/claude.md-files/$tpl" ]; then
            install_claude_md "$tpl"
        fi
    done
}

install_agent_deck() {
    ensure_repo

    local deck_home="$HOME/.agent-deck"
    mkdir -p "$deck_home/collections" "$deck_home/cache"

    # Copy agent-deck.sh
    if [ -f "$TMPDIR_ACC/agent-deck.sh" ]; then
        cp "$TMPDIR_ACC/agent-deck.sh" "$deck_home/agent-deck.sh"
        chmod +x "$deck_home/agent-deck.sh"
        ok "Installed: ~/.agent-deck/agent-deck.sh"
    fi

    # Install /deck command to current project
    if [ -d "$TMPDIR_ACC/resources/slash-commands/deck" ]; then
        mkdir -p "$TARGET_DIR/.claude/commands"
        local md_file
        md_file=$(find "$TMPDIR_ACC/resources/slash-commands/deck" -maxdepth 1 -name "*.md" | head -1)
        if [ -n "$md_file" ]; then
            cp "$md_file" "$TARGET_DIR/.claude/commands/deck.md"
            ok "Installed: .claude/commands/deck.md"
        fi
    fi

    # Suggest shell alias
    echo ""
    echo -e "${DIM}Add to your shell profile for quick access:${RESET}"
    echo -e "  ${CYAN}alias agent-deck='bash ~/.agent-deck/agent-deck.sh'${RESET}"
    echo ""
}

pick_resource() {
    local resource="$1"
    ensure_repo

    local category name
    category=$(echo "$resource" | cut -d/ -f1)
    name=$(echo "$resource" | cut -d/ -f2-)

    if [ -z "$name" ]; then
        err "Specify a resource: --pick <category>/<name>"
        echo "Run: bash install.sh --list"
        return 1
    fi

    case "$category" in
        slash-commands)
            install_slash_command "$name"
            ;;
        claude.md-files)
            install_claude_md "$name"
            ;;
        workflows-knowledge-guides)
            install_workflow "$name"
            ;;
        *)
            err "Unknown category: $category"
            echo "Valid categories: slash-commands, claude.md-files, workflows-knowledge-guides"
            return 1
            ;;
    esac
}

# ─── Bulk install ────────────────────────────────────────────────────────────

install_all_commands() {
    ensure_repo

    info "Installing all slash commands..."
    mkdir -p "$TARGET_DIR/.claude/commands"

    local count=0
    for dir in "$TMPDIR_ACC"/resources/slash-commands/*/; do
        local name
        name=$(basename "$dir")
        local md_file
        md_file=$(find "$dir" -maxdepth 1 -name "*.md" | head -1)
        if [ -n "$md_file" ]; then
            local dest="$TARGET_DIR/.claude/commands/$(basename "$md_file")"
            if [ -f "$dest" ]; then
                warn "Skipped (exists): .claude/commands/$(basename "$md_file")"
            else
                cp "$md_file" "$dest"
                ok "Installed: .claude/commands/$(basename "$md_file")"
                count=$((count + 1))
            fi
        fi
    done

    echo ""
    ok "Installed $count slash commands to .claude/commands/"
}

# ─── Guided interactive mode ────────────────────────────────────────────────

guided() {
    ensure_repo
    detect_project_type

    echo ""
    echo -e "${BOLD}Awesome Claude Code${RESET}"
    echo -e "${DIM}Guided setup for your project${RESET}"
    echo ""

    # Show what we detected
    if [ -n "$DETECTED_LANG" ]; then
        echo -e "  Detected: ${CYAN}$DETECTED_LANG${RESET} project"
    fi
    if [ -n "$DETECTED_FRAMEWORK" ]; then
        echo -e "  Framework: ${CYAN}$DETECTED_FRAMEWORK${RESET}"
    fi
    if [ "$DETECTED_HAS_CLAUDE" = "yes" ]; then
        echo -e "  Claude Code: ${GREEN}already configured${RESET}"
    fi
    if [ "$DETECTED_HAS_TESTS" = "yes" ]; then
        echo -e "  Tests: ${GREEN}found${RESET}"
    fi
    if [ "$DETECTED_HAS_CI" = "yes" ]; then
        echo -e "  CI: ${GREEN}found${RESET}"
    fi
    echo ""

    # ── Question 1: What are you building? ──

    echo -e "${BOLD}What best describes your project?${RESET}"
    echo ""
    echo "  1) ML / Data Science"
    echo "  2) Data Engineering / Databricks"
    echo "  3) Backend / API"
    echo "  4) Frontend / Web App"
    echo "  5) DevOps / Infrastructure"
    echo "  6) CLI / Tooling"
    echo "  7) General software project"
    echo ""

    # Pre-suggest based on detection
    local default_domain="7"
    case "$DETECTED_FRAMEWORK" in
        databricks) default_domain="2" ;;
        fastapi|django|flask|express|fastify) default_domain="3" ;;
        react|nextjs) default_domain="4" ;;
    esac

    echo -ne "Choice [1-7] (${default_domain}): "
    read -r domain_choice
    domain_choice="${domain_choice:-$default_domain}"

    # ── Question 2: What do you need? ──

    echo ""
    echo -e "${BOLD}What would help you most?${RESET} ${DIM}(pick multiple: e.g. 1 3 5)${RESET}"
    echo ""
    echo "  1) Git workflow      — Better commits, PRs, branches"
    echo "  2) Code quality      — Reviews, optimization, testing"
    echo "  3) Project context   — Help Claude understand your codebase"
    echo "  4) Documentation     — Docs, changelogs, release notes"
    echo "  5) Deployment        — CI/CD, releases"
    echo "  6) Everything useful — All of the above"
    echo ""
    echo -n "Choice: "
    read -r needs_choice

    # Parse needs into flags
    local need_git=false need_quality=false need_context=false need_docs=false need_deploy=false
    for n in $needs_choice; do
        case "$n" in
            1) need_git=true ;;
            2) need_quality=true ;;
            3) need_context=true ;;
            4) need_docs=true ;;
            5) need_deploy=true ;;
            6) need_git=true; need_quality=true; need_context=true; need_docs=true; need_deploy=true ;;
        esac
    done

    # ── Build recommendation list ──

    local rec_commands=""
    local rec_templates=""

    # Universal (always include)
    rec_commands="commit pr-review optimize"

    # Needs-based commands
    if [ "$need_git" = true ]; then
        rec_commands="$rec_commands create-pr fix-github-issue create-worktrees update-branch-name husky"
    fi
    if [ "$need_quality" = true ]; then
        rec_commands="$rec_commands testing_plan_integration create-hook"
    fi
    if [ "$need_context" = true ]; then
        rec_commands="$rec_commands context-prime initref load-llms-txt"
    fi
    if [ "$need_docs" = true ]; then
        rec_commands="$rec_commands update-docs add-to-changelog"
    fi
    if [ "$need_deploy" = true ]; then
        rec_commands="$rec_commands release act"
    fi

    # Domain-specific additions
    case "$domain_choice" in
        1) # ML / Data Science
            rec_commands="$rec_commands mlflow-log-model uc-register-model feature-table"
            rec_templates="DSPy MLflow-Databricks Feature-Engineering Vector-Search Mosaic-AI-Agents Databricks-AI-Dev-Kit"
            ;;
        2) # Data Engineering / Databricks
            rec_commands="$rec_commands databricks-job databricks-deploy feature-table mlflow-log-model uc-register-model"
            rec_templates="Databricks-Full-Stack Delta-Live-Tables Databricks-Jobs Unity-Catalog"
            ;;
        3) # Backend / API
            rec_templates="SG-Cars-Trends-Backend LangGraphJS AWS-MCP-Server Giselle"
            ;;
        4) # Frontend / Web App
            rec_templates="APX-Databricks-Apps Course-Builder JSBeeb"
            ;;
        5) # DevOps / Infrastructure
            rec_commands="$rec_commands act create-hook husky"
            rec_templates="Databricks-MCP-Server claude-code-mcp-enhanced"
            ;;
        6) # CLI / Tooling
            rec_templates="TPL Cursor-Tools"
            ;;
        7) # General
            rec_templates="Basic-Memory"
            ;;
    esac

    # Also install the /setup command itself for future use
    rec_commands="$rec_commands setup"

    # Deduplicate commands
    rec_commands=$(echo "$rec_commands" | tr ' ' '\n' | sort -u | tr '\n' ' ')

    # ── Show recommendations ──

    echo ""
    echo -e "${DIM}────────────────────────────────────────${RESET}"
    echo -e "${BOLD}Recommended for your project:${RESET}"
    echo ""

    local i=1
    echo -e "${BOLD}Slash Commands${RESET} ${DIM}(install to .claude/commands/)${RESET}"
    for cmd in $rec_commands; do
        if [ -d "$TMPDIR_ACC/resources/slash-commands/$cmd" ]; then
            local existing=""
            if [ -f "$TARGET_DIR/.claude/commands/$cmd.md" ]; then
                existing=" ${DIM}(already installed)${RESET}"
            fi
            echo -e "  ${GREEN}$i)${RESET} /$cmd$existing"
            i=$((i + 1))
        fi
    done

    if [ -n "$rec_templates" ]; then
        echo ""
        echo -e "${BOLD}CLAUDE.md Templates${RESET} ${DIM}(append to CLAUDE.md)${RESET}"
        for tpl in $rec_templates; do
            if [ -d "$TMPDIR_ACC/resources/claude.md-files/$tpl" ]; then
                local existing=""
                if [ -f "$TARGET_DIR/CLAUDE.md" ] && grep -qF "awesome-claude-code: $tpl" "$TARGET_DIR/CLAUDE.md" 2>/dev/null; then
                    existing=" ${DIM}(already installed)${RESET}"
                fi
                echo -e "  ${CYAN}$i)${RESET} $tpl$existing"
                i=$((i + 1))
            fi
        done
    fi

    # ── Confirm ──

    echo ""
    echo -ne "Install all recommended resources? ${DIM}[Y/n]${RESET} "
    read -r confirm
    confirm="${confirm:-y}"

    if [ "$confirm" = "n" ] || [ "$confirm" = "N" ]; then
        echo ""
        echo "You can install resources individually:"
        echo "  bash install.sh --pick slash-commands/<name>"
        echo "  bash install.sh --pick claude.md-files/<name>"
        echo "  bash install.sh --list"
        echo ""
        exit 0
    fi

    # ── Install ──

    echo ""
    info "Installing resources..."
    echo ""

    install_commands_by_name "$rec_commands"

    if [ -n "$rec_templates" ]; then
        install_templates_by_name "$rec_templates"
    fi

    # ── Summary ──

    echo ""
    echo -e "${DIM}────────────────────────────────────────${RESET}"
    echo -e "${BOLD}${GREEN}Setup complete!${RESET}"
    echo ""
    echo "Your new commands (use in Claude Code):"
    for cmd in $rec_commands; do
        if [ -f "$TARGET_DIR/.claude/commands/$cmd.md" ]; then
            echo -e "  ${GREEN}/$cmd${RESET}"
        fi
    done

    if [ -n "$rec_templates" ] && [ -f "$TARGET_DIR/CLAUDE.md" ]; then
        echo ""
        echo "CLAUDE.md updated with project-specific patterns."
    fi

    # ── Offer agent deck ──

    echo ""
    echo -ne "Install the Agent Deck for managing collections + tmux sessions? ${DIM}[y/N]${RESET} "
    read -r deck_confirm

    if [ "$deck_confirm" = "y" ] || [ "$deck_confirm" = "Y" ]; then
        install_agent_deck
    fi

    echo ""
    echo "Next steps:"
    echo "  1. Open Claude Code in your project"
    echo "  2. Try /commit for your next git commit"
    echo "  3. Run /setup again anytime to add more resources"
    if [ -f "$HOME/.agent-deck/agent-deck.sh" ]; then
        echo "  4. Run agent-deck to manage collections and sessions"
    fi
    echo ""
}

# ─── Simple interactive mode (menu-based) ───────────────────────────────────

menu() {
    ensure_repo

    echo ""
    echo -e "${BOLD}Awesome Claude Code - Resource Installer${RESET}"
    echo -e "${DIM}Install resources into: $TARGET_DIR${RESET}"
    echo ""

    echo "  1) Slash commands (pick individually)"
    echo "  2) All slash commands"
    echo "  3) CLAUDE.md template"
    echo "  4) Workflow guide"
    echo "  5) Browse all resources"
    echo "  q) Quit"
    echo ""
    echo -n "Choice [1-5/q]: "
    read -r choice

    case "$choice" in
        1)
            echo ""
            echo -e "${BOLD}Available Slash Commands:${RESET}"
            echo ""
            local commands=()
            local i=1
            for dir in "$TMPDIR_ACC"/resources/slash-commands/*/; do
                local name
                name=$(basename "$dir")
                commands+=("$name")
                echo "  $i) $name"
                i=$((i + 1))
            done
            echo ""
            echo -n "Enter number(s) separated by spaces, or 'all': "
            read -r selection

            if [ "$selection" = "all" ]; then
                install_all_commands
            else
                for num in $selection; do
                    local idx=$((num - 1))
                    if [ "$idx" -ge 0 ] && [ "$idx" -lt "${#commands[@]}" ]; then
                        install_slash_command "${commands[$idx]}"
                    else
                        warn "Invalid selection: $num"
                    fi
                done
            fi
            ;;
        2)
            install_all_commands
            ;;
        3)
            echo ""
            echo -e "${BOLD}Available CLAUDE.md Templates:${RESET}"
            echo ""
            local templates=()
            local i=1
            for dir in "$TMPDIR_ACC"/resources/claude.md-files/*/; do
                local name
                name=$(basename "$dir")
                templates+=("$name")
                echo "  $i) $name"
                i=$((i + 1))
            done
            echo ""
            echo -n "Enter number(s) separated by spaces: "
            read -r selection

            for num in $selection; do
                local idx=$((num - 1))
                if [ "$idx" -ge 0 ] && [ "$idx" -lt "${#templates[@]}" ]; then
                    install_claude_md "${templates[$idx]}"
                else
                    warn "Invalid selection: $num"
                fi
            done
            ;;
        4)
            echo ""
            echo -e "${BOLD}Available Workflow Guides:${RESET}"
            echo ""
            local workflows=()
            local i=1
            for dir in "$TMPDIR_ACC"/resources/workflows-knowledge-guides/*/; do
                local name
                name=$(basename "$dir")
                workflows+=("$name")
                echo "  $i) $name"
                i=$((i + 1))
            done
            echo ""
            echo -n "Enter number(s) separated by spaces: "
            read -r selection

            for num in $selection; do
                local idx=$((num - 1))
                if [ "$idx" -ge 0 ] && [ "$idx" -lt "${#workflows[@]}" ]; then
                    install_workflow "${workflows[$idx]}"
                else
                    warn "Invalid selection: $num"
                fi
            done
            ;;
        5)
            list_resources
            ;;
        q|Q)
            echo "Bye."
            exit 0
            ;;
        *)
            err "Invalid choice."
            exit 1
            ;;
    esac

    echo ""
    ok "Done! Your resources are ready to use."
}

# ─── Usage ───────────────────────────────────────────────────────────────────

usage() {
    echo "Usage: bash install.sh [OPTIONS]"
    echo ""
    echo "Install awesome-claude-code resources into your existing project."
    echo ""
    echo "Options:"
    echo "  (no args)              Guided setup (recommended)"
    echo "  --menu                 Simple menu to pick resources"
    echo "  --list                 List all available resources"
    echo "  --pick <cat/name>      Install a specific resource"
    echo "  --all-commands         Install all slash commands"
    echo "  --deck                 Install Agent Deck (collection manager + tmux launcher)"
    echo "  --target <dir>         Target project directory (default: current)"
    echo "  --help                 Show this help"
    echo ""
    echo "Examples:"
    echo "  bash install.sh                                  # Guided setup"
    echo "  bash install.sh --pick slash-commands/commit      # Install one command"
    echo "  bash install.sh --pick claude.md-files/DSPy       # Add a template"
    echo "  bash install.sh --all-commands                    # Install all commands"
    echo "  bash install.sh --list                            # Browse resources"
    echo ""
    echo "One-liner from any project:"
    echo "  curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash"
    echo ""
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
    local action="guided"
    local pick_target=""

    while [ $# -gt 0 ]; do
        case "$1" in
            --list|-l)
                action="list"
                shift
                ;;
            --pick|-p)
                action="pick"
                pick_target="${2:-}"
                if [ -z "$pick_target" ]; then
                    err "--pick requires a resource path (e.g., slash-commands/commit)"
                    exit 1
                fi
                shift 2
                ;;
            --all-commands)
                action="all-commands"
                shift
                ;;
            --deck)
                action="deck"
                shift
                ;;
            --menu|-m)
                action="menu"
                shift
                ;;
            --target|-t)
                TARGET_DIR="${2:-}"
                if [ -z "$TARGET_DIR" ] || [ ! -d "$TARGET_DIR" ]; then
                    err "--target requires a valid directory"
                    exit 1
                fi
                shift 2
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                err "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Prevent running from inside the awesome-claude-code repo itself
    if [ -f "$TARGET_DIR/acc-config.yaml" ] && [ -d "$TARGET_DIR/resources/slash-commands" ]; then
        warn "You appear to be inside the awesome-claude-code repository."
        echo "This script is meant to be run from your own project directory."
        echo ""
        echo "Usage: cd /path/to/your/project && bash /path/to/install.sh"
        exit 1
    fi

    detect_project

    case "$action" in
        guided)
            guided
            ;;
        menu)
            menu
            ;;
        list)
            list_resources
            ;;
        pick)
            pick_resource "$pick_target"
            ;;
        all-commands)
            install_all_commands
            ;;
        deck)
            install_agent_deck
            ;;
    esac
}

main "$@"
