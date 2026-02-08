# Installing Resources into an Existing Project

This guide covers how to add awesome-claude-code resources to a project you're already working on (a "brownfield" project).

## Quick Start

From your project directory, run:

```bash
curl -fsSL https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/install.sh | bash
```

The installer will:
1. Detect your project type (language, framework, existing setup)
2. Ask what you're building (ML, backend, frontend, etc.)
3. Ask what you need help with (git workflow, code quality, deployment, etc.)
4. Recommend and install the right resources for your situation

It clones the repo to a temp directory, copies what you select, and cleans up after itself.

## Two Ways to Set Up

### 1. Guided Setup via Bash (the bootstrapper)

Run the install script from your project directory. It walks you through two questions, recommends resources, and installs them:

```bash
bash install.sh
```

The guided flow also installs a `/setup` slash command so you can re-run the setup later from within Claude Code.

### 2. Guided Setup via Claude Code (the agent experience)

Once `/setup` is installed (either by the bash script or manually), you get a richer agent-driven experience inside Claude Code:

```
/setup
```

The `/setup` command goes deeper than the bash script. It:
- Reads your actual project files to understand your stack
- Has a conversational Q&A (not just numbered menus)
- Makes smarter recommendations based on what it finds in your codebase
- Can explain each resource and why it's relevant

This is the recommended path if you already have Claude Code running in your project.

## What Gets Installed Where

| Resource Type | Source | Destination in Your Project |
|---|---|---|
| Slash commands | `resources/slash-commands/` | `.claude/commands/<name>.md` |
| CLAUDE.md templates | `resources/claude.md-files/` | Appended to `CLAUDE.md` |
| Workflow guides | `resources/workflows-knowledge-guides/` | `.claude/workflows/<name>/` |

Slash commands become immediately usable as `/<command-name>` in your Claude Code session. CLAUDE.md templates provide project-specific guidance that Claude reads automatically.

## Install Options

### Guided setup (recommended)

```bash
bash install.sh
```

Asks about your project and needs, then recommends and installs resources.

### Simple menu

```bash
bash install.sh --menu
```

Browse and pick resources from a numbered list without the questionnaire.

### List available resources

```bash
bash install.sh --list
```

### Install a specific resource

```bash
# A slash command
bash install.sh --pick slash-commands/commit

# A CLAUDE.md template
bash install.sh --pick claude.md-files/DSPy

# A workflow guide
bash install.sh --pick workflows-knowledge-guides/Design-Review-Workflow
```

### Install all slash commands at once

```bash
bash install.sh --all-commands
```

### Target a different directory

```bash
bash install.sh --target /path/to/my/project --pick slash-commands/optimize
```

## What the Script Does

1. Detects your project type (language, framework, CI, tests, existing Claude Code config)
2. Asks two guided questions about your domain and needs
3. Recommends resources tailored to your answers
4. Clones the awesome-claude-code repo to a temporary directory (shallow clone)
5. Copies selected resources to the correct locations in your project
6. Removes the temporary clone on exit

It does **not**:
- Modify existing files without asking
- Install any dependencies or packages
- Touch anything outside your project directory
- Leave the cloned repo behind

## Manual Installation

If you prefer not to run the script, you can manually copy resources:

```bash
# Clone the repo somewhere
git clone --depth 1 https://github.com/hesreallyhim/awesome-claude-code.git /tmp/acc

# Copy a slash command
mkdir -p .claude/commands
cp /tmp/acc/resources/slash-commands/commit/commit.md .claude/commands/

# Copy the /setup command for future use
cp /tmp/acc/resources/slash-commands/setup/setup.md .claude/commands/

# Append a CLAUDE.md template
cat /tmp/acc/resources/claude.md-files/DSPy/CLAUDE.md >> CLAUDE.md

# Clean up
rm -rf /tmp/acc
```

## Available Resources

### Slash Commands (29)

Commands you can invoke with `/<name>` in Claude Code:

| Command | Purpose |
|---|---|
| `/setup` | **Guided project setup** (install this first) |
| `/act` | Act on a task |
| `/add-to-changelog` | Add changelog entries |
| `/clean` | Clean up project artifacts |
| `/commit` | Conventional commit workflow |
| `/context-prime` | Prime Claude with project context |
| `/create-hook` | Create Claude Code hooks |
| `/create-jtbd` | Create Jobs-to-be-Done specs |
| `/create-pr` | Create pull requests |
| `/create-prd` | Create product requirement docs |
| `/create-prp` | Create product requirement plans |
| `/create-pull-request` | Pull request with template |
| `/create-worktrees` | Create git worktrees |
| `/databricks-deploy` | Deploy to Databricks |
| `/databricks-job` | Manage Databricks jobs |
| `/feature-table` | Feature table operations |
| `/fix-github-issue` | Fix GitHub issues |
| `/husky` | Set up git hooks |
| `/initref` | Initialize reference docs |
| `/load-llms-txt` | Load LLM config files |
| `/mlflow-log-model` | Log MLflow models |
| `/optimize` | Performance optimization |
| `/pr-review` | Review pull requests |
| `/release` | Manage releases |
| `/testing_plan_integration` | Integration test planning |
| `/todo` | Manage project todos |
| `/uc-register-model` | Register Unity Catalog models |
| `/update-branch-name` | Update branch names |
| `/update-docs` | Update documentation |

### CLAUDE.md Templates (34)

Project-specific guidance templates. Each adds domain knowledge and coding standards to your `CLAUDE.md`:

- AI-IntelliJ-Plugin, APX-Databricks-Apps, AVS-Vibe-Developer-Guide, AWS-MCP-Server
- Basic-Memory, Comm, Course-Builder, Cursor-Tools
- DSPy, Databricks-AI-Dev-Kit, Databricks-Full-Stack, Databricks-Jobs
- Databricks-MCP-Server, Delta-Live-Tables, DroidconKotlin, EDSL
- Feature-Engineering, Giselle, Guitar, JSBeeb
- Lamoom-Python, LangGraphJS, MLflow-Databricks, Mosaic-AI-Agents
- Network-Chronicles, Note-Companion, Pareto-Mac, Perplexity-MCP
- SG-Cars-Trends-Backend, SPy, TPL, Unity-Catalog
- Vector-Search, claude-code-mcp-enhanced

### Workflow Guides (3)

Multi-file reference implementations for specific workflows:

- **Autonomous-Claude-Tmux** — Autonomous agent orchestration
- **Blogging-Platform-Instructions** — Blogging platform workflow
- **Design-Review-Workflow** — UI/UX design review agents

## Removing Resources

Resources are plain files in your project. To remove:

```bash
# Remove a slash command
rm .claude/commands/commit.md

# Remove a workflow guide
rm -rf .claude/workflows/Design-Review-Workflow/
```

For CLAUDE.md templates, find and remove the section between `# --- awesome-claude-code: <name> ---` markers.

## Updating Resources

Re-run the install script or `/setup` to get the latest versions. Both will ask before overwriting existing files.
