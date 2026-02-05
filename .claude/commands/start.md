# Project Setup

Interactive setup to configure this project based on what you're building.

## Flow

### Step 1: What Are We Building?

Ask: **"What are we building today?"**

Listen for project type:
- ML / model / training / pipeline → Machine Learning
- Data / ETL / pipeline → Data Engineering
- API / backend / server → Backend Services
- App / frontend / UI → Applications
- Databricks / Spark → Databricks Platform
- CLI / tool / script → Command-line Tools

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

### Step 4: Pull Resources

Based on answers, suggest 3-5 relevant resources from:
- `resources/claude.md-files/` - Project templates
- `resources/slash-commands/` - Workflow commands
- `resources/workflows-knowledge-guides/` - Patterns

Example output:
```
Based on your project, I'd recommend:

1. **Databricks-Full-Stack** - MLflow + Unity Catalog patterns
2. **/databricks-deploy** - Deployment workflow command
3. **/optimize** - Performance optimization

Add these to your project? (yes / pick numbers / skip)
```

### Step 5: Configure & Start

If confirmed:
1. Copy selected resources to `.claude/commands/`
2. Append relevant CLAUDE.md sections
3. Summarize what was added

End with: **"What would you like to work on first?"**

---

Begin now. Ask: "What are we building today?"
