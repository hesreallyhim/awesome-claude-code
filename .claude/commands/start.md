# Project Setup

Interactive setup to configure this project based on what you're building.

## Flow

### Step 0: Install the Base Toolkit

**Always do this first, regardless of what the user is building.**

Check if the project's `CLAUDE.md` already contains "Auto-Detect Behaviors (Always On)". If not:

1. Read the Coding-With-Claude toolkit from `resources/claude.md-files/Coding-With-Claude-Toolkit/CLAUDE.md`
2. If the project has no `CLAUDE.md`, create one with the toolkit contents (excluding the Setup section at the bottom)
3. If the project already has a `CLAUDE.md`, append the toolkit contents after the existing content
4. Tell the user:
   ```
   Installed the base toolkit with 9 automatic behaviors:
   - Vague request clarification
   - Error diagnosis
   - Scope checking
   - Pre-commit cleanup
   - Test awareness
   - Goal drift detection
   - Pushback on bad ideas
   - Documentation sync
   - Gotcha capture

   These are always active. You don't need to invoke anything.
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
