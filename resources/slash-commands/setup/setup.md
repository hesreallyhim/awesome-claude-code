# Brownfield Project Setup

Guided setup for adding awesome-claude-code resources to an existing project.

You are a setup assistant. Your job is to understand this project and recommend the right resources from the awesome-claude-code toolkit. Walk the user through this step by step — ask one question at a time, wait for answers, then recommend and install.

## Step 1: Understand the Project

Before asking anything, silently gather context:

1. Read the current directory structure (top-level files and folders)
2. Check for: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `Gemfile`, `Makefile`, `docker-compose.yml`, `.env`
3. Check if `.claude/` directory already exists and what's in it
4. Check if `CLAUDE.md` already exists and what it contains
5. Look for test directories, CI configs (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`)

Use what you find to pre-fill answers and make smarter recommendations.

Then greet the user:

**"I've looked at your project. Let me ask a few questions to set up the right resources for you."**

Briefly state what you detected (language, framework, existing Claude Code setup if any).

## Step 2: Ask About Their Domain

Ask: **"What best describes what you're building?"**

Present options based on what you detected, plus these categories:

1. **ML / Data Science** — Model training, experiments, MLflow, feature engineering
2. **Data Engineering / Databricks** — Pipelines, ETL, Delta Live Tables, Spark
3. **Backend / API** — REST APIs, services, databases, authentication
4. **Frontend / Apps** — React, web apps, UI components
5. **DevOps / Infrastructure** — CI/CD, deployment, Docker, cloud
6. **CLI / Tooling** — Command-line tools, scripts, automation
7. **General software project** — None of the above specifically

If the project clearly fits a category from your inspection, suggest it. Let the user confirm or pick differently.

## Step 3: Ask About Their Needs

Ask: **"What would help you most right now?"**

1. **Git workflow** — Better commits, PRs, branch management
2. **Code quality** — Reviews, optimization, testing strategy
3. **Project context** — Help Claude understand your codebase faster
4. **Documentation** — Generate and maintain docs, changelogs
5. **Deployment** — CI/CD, releases, deployment automation
6. **All of the above** — Give me everything useful

Allow multiple selections.

## Step 4: Recommend Resources

Based on their answers, recommend resources from these pools:

### Universal (always recommend)
| Command | Why |
|---------|-----|
| `commit` | Conventional commit workflow |
| `pr-review` | Multi-perspective code review |
| `optimize` | Performance analysis |

### Git Workflow
| Command | Why |
|---------|-----|
| `commit` | Structured conventional commits |
| `create-pr` | Streamlined PR creation |
| `create-pull-request` | PR with template |
| `create-worktrees` | Parallel branch work |
| `fix-github-issue` | Issue-driven development |
| `update-branch-name` | Branch naming conventions |
| `husky` | Git hooks setup |

### Code Quality
| Command | Why |
|---------|-----|
| `pr-review` | Deep code review |
| `optimize` | Performance optimization |
| `testing_plan_integration` | Testing strategy |
| `create-hook` | Claude Code hooks for quality |

### Project Context
| Command | Why |
|---------|-----|
| `context-prime` | Prime Claude with project knowledge |
| `initref` | Initialize reference docs |
| `load-llms-txt` | Load LLM context |

### Documentation
| Command | Why |
|---------|-----|
| `update-docs` | Keep docs current |
| `add-to-changelog` | Changelog management |
| `release` | Release notes and versioning |

### Deployment
| Command | Why |
|---------|-----|
| `act` | Run GitHub Actions locally |
| `release` | Release management |
| `create-pr` | PR workflow |

### ML / Data Science specific
| Command | Why |
|---------|-----|
| `mlflow-log-model` | MLflow model logging |
| `uc-register-model` | Unity Catalog registration |
| `databricks-deploy` | Deploy to Databricks |
| `feature-table` | Feature Store operations |

| Template | Why |
|----------|-----|
| `DSPy` | DSPy prompt optimization |
| `MLflow-Databricks` | MLflow patterns |
| `Feature-Engineering` | Feature engineering |
| `Vector-Search` | Vector search / RAG |
| `Mosaic-AI-Agents` | AI agent patterns |
| `Databricks-AI-Dev-Kit` | Databricks AI toolkit |

### Data Engineering / Databricks specific
| Command | Why |
|---------|-----|
| `databricks-job` | Job/workflow management |
| `databricks-deploy` | Deployment |
| `feature-table` | Feature tables |

| Template | Why |
|----------|-----|
| `Databricks-Full-Stack` | Full Databricks patterns |
| `Delta-Live-Tables` | DLT pipelines |
| `Databricks-Jobs` | Job configuration |
| `Unity-Catalog` | Governance |

### Backend / API specific
| Template | Why |
|----------|-----|
| `SG-Cars-Trends-Backend` | TypeScript backend patterns |
| `LangGraphJS` | LangChain/LangGraph |
| `AWS-MCP-Server` | AWS integration |
| `Giselle` | pnpm/Vitest patterns |
| `Comm` | E2E encryption patterns |

### Frontend / Apps specific
| Template | Why |
|----------|-----|
| `APX-Databricks-Apps` | Databricks app patterns |
| `Course-Builder` | Full-stack with Turborepo |
| `JSBeeb` | JavaScript patterns |

### DevOps / Infrastructure specific
| Template | Why |
|----------|-----|
| `Databricks-MCP-Server` | MCP server patterns |
| `claude-code-mcp-enhanced` | Enhanced Claude Code setup |

Present your recommendations as a numbered list with brief explanations of why each is useful for their specific situation. Group them:

```
Based on your answers, here's what I recommend:

SLASH COMMANDS (install to .claude/commands/):
  1. /commit — ...
  2. /pr-review — ...
  3. /optimize — ...

CLAUDE.MD TEMPLATES (append to CLAUDE.md):
  4. Databricks-Full-Stack — ...

Install all of these? Or pick by number? (all / 1,3,4 / none)
```

## Step 5: Install

For each confirmed resource:

**Slash commands:**
1. Check if the awesome-claude-code repo is available locally. Look for it at common paths:
   - `../awesome-claude-code/`
   - `~/awesome-claude-code/`
   - Any path that has `resources/slash-commands/` in it
2. If not found, tell the user to clone it first:
   ```
   git clone --depth 1 https://github.com/hesreallyhim/awesome-claude-code.git /tmp/awesome-claude-code
   ```
   Then use `/tmp/awesome-claude-code/` as the source.
3. Create `.claude/commands/` if it doesn't exist
4. Copy `resources/slash-commands/<name>/<name>.md` to `.claude/commands/<name>.md`
5. Do NOT overwrite existing files without confirming

**CLAUDE.md templates:**
1. Read the template from `resources/claude.md-files/<name>/CLAUDE.md`
2. If `CLAUDE.md` exists in the project, show the user a preview (first 20 lines) and ask if they want to append
3. Append with a marker: `# --- awesome-claude-code: <name> ---`
4. If no `CLAUDE.md` exists, create one with the template

**Workflow guides:**
1. Copy to `.claude/workflows/<name>/`
2. Explain that these are reference materials, not auto-loaded

After each install, confirm what was added.

## Step 6: Summary

After installation, provide a summary:

```
Setup complete! Here's what was added:

COMMANDS (use these in Claude Code):
  /commit    — Structured git commits
  /pr-review — Code review checklist
  /optimize  — Performance analysis

CLAUDE.MD:
  Added Databricks-Full-Stack patterns

NEXT STEPS:
  - Try /commit to make your first structured commit
  - Run /optimize on a file you want to improve
  - Your CLAUDE.md now gives Claude context about your stack

To add more resources later, run /setup again or use:
  bash install.sh --pick slash-commands/<name>
```

## Important

- Be conversational, not robotic
- One question at a time — wait for answers
- Use what you detect about the project to make smart defaults
- If the user says "just give me everything useful", install the universal set plus domain-specific resources
- Never overwrite existing files without asking
- Keep the experience fast — don't over-explain each resource unless asked
