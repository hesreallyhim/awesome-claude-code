# Databricks AI Dev Kit Guide

## Overview
Databricks AI Dev Kit is a comprehensive toolkit for coding agents (Claude Code, Cursor, Windsurf) that provides trusted patterns, tools, and skills for building applications on Databricks. It includes an MCP server, Python library, and extensive skill guides.

## Build & Test Commands
- Install core: `pip install databricks-tools-core`
- Setup project: `cd ai-dev-project && ./setup.sh`
- Run MCP server: `npx databricks-mcp-server`
- Run builder app: `cd databricks-builder-app && ./start.sh`

## Toolkit Components

| Component | Description |
|-----------|-------------|
| **databricks-tools-core** | Python library with high-level Databricks functions |
| **databricks-mcp-server** | 50+ tools via Model Context Protocol |
| **databricks-skills** | 15 markdown guides for Databricks patterns |
| **databricks-builder-app** | Web UI for Databricks development |
| **ai-dev-project** | Starter template for new projects |

## What You Can Build

- Spark Declarative Pipelines (streaming, CDC, Auto Loader)
- Databricks Jobs and scheduled workflows
- AI/BI dashboards and analytics
- Unity Catalog governance structures
- Genie Spaces for natural language exploration
- RAG-based knowledge assistants
- MLflow experiments and evaluations
- Model serving endpoints
- Full-stack Databricks Apps

## Installation Options

### 1. Full Starter Kit
```bash
git clone https://github.com/databricks-solutions/ai-dev-kit
cd ai-dev-kit/ai-dev-project
./setup.sh
```

### 2. MCP Server Only
```bash
# Add to Claude Code or Cursor MCP config
npx databricks-mcp-server
```

### 3. Python Core Library
```bash
pip install databricks-tools-core
```

### 4. Skills Only (No Code)
Copy skills from `databricks-skills/` to your project's `.claude/` or context.

## Environment Setup

```bash
# Required environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."

# Or use CLI profile
databricks configure --profile my-workspace
```

## MCP Server Configuration

### For Claude Code (~/.claude/mcp.json)
```json
{
  "mcpServers": {
    "databricks": {
      "command": "npx",
      "args": ["databricks-mcp-server"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-token"
      }
    }
  }
}
```

### For Cursor (.cursor/mcp.json)
```json
{
  "mcpServers": {
    "databricks": {
      "command": "npx",
      "args": ["databricks-mcp-server"]
    }
  }
}
```

## Available MCP Tools

The MCP server exposes 50+ tools including:

### Workspace & Files
- `list_workspace_files` - Browse workspace directories
- `read_workspace_file` - Read notebook/file content
- `write_workspace_file` - Create/update files

### Unity Catalog
- `list_catalogs` - List available catalogs
- `list_schemas` - List schemas in catalog
- `list_tables` - List tables in schema
- `get_table_info` - Get table metadata
- `execute_sql` - Run SQL queries

### Jobs & Pipelines
- `list_jobs` - List all jobs
- `create_job` - Create new job
- `run_job` - Trigger job run
- `get_job_run` - Get run status
- `list_pipelines` - List DLT pipelines

### ML & AI
- `list_experiments` - List MLflow experiments
- `list_models` - List registered models
- `list_serving_endpoints` - List model endpoints
- `query_serving_endpoint` - Query a model

### Clusters & Compute
- `list_clusters` - List compute resources
- `get_cluster` - Get cluster details
- `create_cluster` - Create new cluster

## Using databricks-tools-core

### Basic Usage
```python
from databricks_tools_core import DatabricksTools

tools = DatabricksTools()

# Execute SQL
results = tools.execute_sql("SELECT * FROM catalog.schema.table LIMIT 10")

# List tables
tables = tools.list_tables("my_catalog", "my_schema")

# Get table info
info = tools.get_table_info("my_catalog.my_schema.my_table")
```

### Unity Catalog Operations
```python
from databricks_tools_core import UnityCatalogTools

uc = UnityCatalogTools()

# Create schema
uc.create_schema("catalog", "new_schema", comment="My new schema")

# Grant permissions
uc.grant_permissions(
    securable_type="SCHEMA",
    full_name="catalog.new_schema",
    principal="data-scientists",
    privileges=["USE_SCHEMA", "SELECT"]
)
```

### Job Management
```python
from databricks_tools_core import JobTools

jobs = JobTools()

# Create a job
job_id = jobs.create_job(
    name="My ETL Job",
    tasks=[{
        "task_key": "etl_task",
        "notebook_task": {
            "notebook_path": "/Repos/user/project/etl_notebook"
        }
    }]
)

# Run the job
run_id = jobs.run_job(job_id)

# Wait for completion
status = jobs.wait_for_run(run_id)
```

## Databricks Skills Reference

The `databricks-skills/` directory contains guides for:

1. **spark-declarative-pipelines** - DLT patterns
2. **jobs-workflows** - Job orchestration
3. **unity-catalog** - Governance patterns
4. **vector-search** - RAG and embeddings
5. **model-serving** - Deployment patterns
6. **feature-engineering** - Feature Store
7. **mlflow-tracking** - Experiment tracking
8. **delta-tables** - Delta Lake patterns
9. **auto-loader** - Streaming ingestion
10. **sql-warehouses** - SQL analytics
11. **dashboards** - AI/BI visualization
12. **genie-spaces** - Natural language data
13. **databricks-apps** - Full-stack apps
14. **secrets-management** - Credential handling
15. **cluster-management** - Compute optimization

## Project Structure (ai-dev-project)

```
ai-dev-project/
├── .claude/
│   ├── commands/           # Slash commands
│   ├── skills/            # Databricks skills (copied)
│   └── mcp.json           # MCP configuration
├── src/
│   ├── pipelines/         # DLT pipelines
│   ├── jobs/              # Job definitions
│   ├── notebooks/         # Databricks notebooks
│   └── apps/              # Databricks Apps
├── tests/
├── databricks.yml         # Asset bundle config
├── pyproject.toml
└── setup.sh               # Initial setup script
```

## Integration with Claude Code

### Using Skills as Context
```bash
# Copy skills to your project
cp -r ai-dev-kit/databricks-skills/ .claude/skills/

# Reference in CLAUDE.md
# See .claude/skills/ for Databricks patterns
```

### Custom Slash Commands
```markdown
# .claude/commands/create-pipeline.md
Create a new DLT pipeline with the following:
1. Bronze layer for raw ingestion
2. Silver layer with data quality expectations
3. Gold layer for aggregations

Use patterns from .claude/skills/spark-declarative-pipelines.md
```

## Best Practices

1. **Environment**: Always set DATABRICKS_HOST and TOKEN before using tools
2. **Skills First**: Read relevant skills before implementing patterns
3. **MCP for Exploration**: Use MCP tools for interactive development
4. **Core for Automation**: Use Python library for scripts and pipelines
5. **Asset Bundles**: Use databricks.yml for deployable configurations
6. **Unity Catalog**: Always target UC for production workloads

## Key Links
- AI Dev Kit: https://github.com/databricks-solutions/ai-dev-kit
- MCP Protocol: https://modelcontextprotocol.io/
- Databricks SDK: https://docs.databricks.com/en/dev-tools/sdk-python.html
