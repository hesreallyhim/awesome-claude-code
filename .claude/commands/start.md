# Project Setup

Interactive setup to configure this project based on what you're building.

## Flow

### Step 0: Discover the Project (Brownfield Check)

**Always do this first, regardless of what the user is building.**

Before installing anything, learn what already exists:

1. **Check for existing CLAUDE.md.** If the project has one, read it carefully. Note:
   - Existing rules, conventions, and principles (these take priority over the toolkit)
   - Existing commands or workflows already defined
   - Any sections that would overlap with the toolkit

2. **Check for existing conventions.** Scan for:
   - `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` → language and toolchain
   - `.eslintrc`, `biome.json`, `ruff.toml`, `.editorconfig` → formatting/linting rules
   - `Makefile`, `justfile`, CI config → build/test/deploy commands
   - Existing test files → test framework, patterns, locations
   - `git log --oneline -10` → commit message style

3. **Summarize what you found** to the user:
   ```
   I see this is an existing [Python/FastAPI] project with:
   - ruff + mypy for linting/types (from pyproject.toml)
   - pytest with tests in tests/ (saw 42 test files)
   - Conventional commits with scope (from git log)
   - Existing CLAUDE.md with API development guidelines
   - GitHub Actions CI pipeline

   I'll respect all of these. The toolkit will fill in gaps
   without overriding what's already here.
   ```

4. **Install the base toolkit.** Check if CLAUDE.md already contains "Auto-Detect Behaviors (Always On)". If not:
   - Read the toolkit from `resources/claude.md-files/Coding-With-Claude-Toolkit/CLAUDE.md`
   - **New project (no CLAUDE.md):** Create one with the toolkit contents (excluding the Setup section)
   - **Existing CLAUDE.md:** Append the toolkit AFTER the existing content, with a clear separator:
     ```markdown
     ---
     <!-- Coding-With-Claude Toolkit (auto-behaviors below) -->
     ```
   - **If overlap detected:** Skip sections the project already covers. For example:
     - Project already has commit conventions → don't add conflicting commit rules
     - Project already has a test strategy → don't add generic test suggestions
     - Project already has pre-commit hooks → note them in Pre-Commit Cleanup

5. Tell the user what was installed and what was skipped:
   ```
   Installed the base toolkit with 9 automatic behaviors.
   Skipped: commit conventions (your CLAUDE.md already covers this)
   Skipped: test patterns (following your existing pytest setup)
   ```

Then proceed to Step 1.

### Step 1: What Are We Building?

Ask: **"What are we building today?"**

Listen for project type:
- ML / model / training / pipeline → Machine Learning
- Data / ETL / pipeline → Data Engineering
- API / backend / server → Backend Services
- App / frontend / UI → Applications
- Databricks / Spark → Databricks Platform
- CLI / tool / script → Command-line Tools

If the user says something like "just the toolkit" or "nothing specific" or "general coding", skip to Step 5 -- they already have what they need from Step 0.

### Step 2: Which Specific Area?

Based on domain, ask about specifics:

**Databricks/ML:**
- MLflow experiment tracking?
- Unity Catalog for governance?
- Feature Store?
- Delta Live Tables?
- Mosaic AI Agents?

**Data Engineering:**
- Batch or streaming?
- Data quality requirements?
- Orchestration needs?

**Backend:**
- Framework? (FastAPI, Flask, etc.)
- Database? (SQL, NoSQL)
- Authentication needs?

### Step 3: What Style of Help?

Ask: **"What style of help do you need?"**

- **Hands-on coding** - Write code together, implement features
- **Architecture review** - Design discussions, trade-offs
- **Debugging** - Fix issues, understand problems
- **Learning** - Explain concepts, teach patterns

### Step 4: Pull Domain Resources

Based on answers, suggest 3-5 relevant resources from:
- `resources/claude.md-files/` - Project templates (appended to CLAUDE.md)
- `resources/slash-commands/` - Workflow commands (copied to .claude/commands/)
- `resources/workflows-knowledge-guides/` - Patterns

Example output:
```
Based on your project, I'd recommend adding:

1. **Databricks-Full-Stack** - MLflow + Unity Catalog patterns
2. **/databricks-deploy** - Deployment workflow command
3. **/optimize** - Performance optimization

These layer on top of the base toolkit. Add them? (yes / pick numbers / skip)
```

### Step 5: Configure & Start

If confirmed:
1. Copy selected slash-command `.md` files to `.claude/commands/`
2. Append selected CLAUDE.md template sections to the project's `CLAUDE.md`
3. Summarize what was added:
   ```
   Your project now has:
   - Base toolkit (9 auto-behaviors) ← always included
   - Databricks-Full-Stack patterns ← from your selections
   - /databricks-deploy command ← from your selections
   ```

End with: **"What would you like to work on first?"**

---

Begin now. Start with Step 0 (check for base toolkit), then ask: "What are we building today?"
