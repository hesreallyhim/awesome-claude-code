# Project Setup

Guided setup for adding awesome-claude-code resources to this project.

This command runs the Agent Deck's setup flow. It inspects your project, asks what you're building and what you need, then installs the right resources and saves a session config.

## Flow

1. **Inspect** the current project (language, framework, existing config)
2. **Ask** what you're building (ML, backend, frontend, etc.)
3. **Ask** what you need (git workflow, code quality, docs, etc.)
4. **Preview** the recommended resources
5. **Install** commands to `.claude/commands/` and templates to `CLAUDE.md`
6. **Save** the session config to `~/.agent-deck/sessions/`

## Implementation

Perform the guided setup flow inline:

1. Read the project's top-level files to detect language/framework
2. Ask: **"What best describes your project?"** (ML, Data Eng, Backend, Frontend, DevOps, CLI, General)
3. Ask: **"What would help you most?"** (Git workflow, Code quality, Project context, Documentation, Deployment, Everything)
4. Build a resource list using these mappings:

### Domain → Commands
| Domain | Commands |
|--------|----------|
| ml | mlflow-log-model, uc-register-model, feature-table, databricks-deploy |
| databricks | databricks-job, databricks-deploy, feature-table, mlflow-log-model, uc-register-model |
| devops | act, create-hook, husky |

### Needs → Commands
| Need | Commands |
|------|----------|
| git | create-pr, fix-github-issue, create-worktrees, update-branch-name, husky |
| quality | testing_plan_integration, create-hook |
| context | context-prime, initref, load-llms-txt |
| docs | update-docs, add-to-changelog |
| deploy | release, act |

### Base Commands (always included)
commit, pr-review, optimize

5. Clone `https://github.com/hesreallyhim/awesome-claude-code.git` to a temp location if `~/.agent-deck/cache/` doesn't exist
6. Copy resources to this project
7. Summarize what was installed

Begin now. Inspect the project first, then greet the user.
