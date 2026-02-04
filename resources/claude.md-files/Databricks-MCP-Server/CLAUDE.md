# Databricks MCP Server Setup Guide

## Overview
The Databricks MCP Server enables Claude Code to execute Databricks operations directly through the Model Context Protocol. Once configured, you can ask Claude to run SQL, manage jobs, deploy pipelines, and more.

## Prerequisites
- Python 3.10+
- uv package manager (`pip install uv`)
- Databricks workspace access
- Databricks personal access token

## Quick Setup

### 1. Clone and Install
```bash
# Clone the AI Dev Kit
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit

# Install dependencies
uv pip install -e ./databricks-tools-core
uv pip install -e ./databricks-mcp-server
```

### 2. Configure Databricks Authentication

**Option A: Environment Variables**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

**Option B: Databricks CLI Profile**
```bash
# Create profile
databricks configure --profile my-workspace

# Reference in env
export DATABRICKS_CONFIG_PROFILE="my-workspace"
```

### 3. Configure Claude Code

Add to `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/ai-dev-kit",
        "python", "databricks-mcp-server/run_server.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      },
      "defer_loading": true
    }
  }
}
```

### 4. Verify Installation
Restart Claude Code, then ask:
```
List the catalogs in my Databricks workspace
```

If configured correctly, Claude will use the MCP tools to query your workspace.

## Available Tools (50+)

### SQL & Data Operations
| Tool | Description |
|------|-------------|
| `execute_sql` | Run SQL queries against warehouse |
| `get_table_info` | Get table schema and metadata |
| `list_tables` | List tables in a schema |
| `list_schemas` | List schemas in a catalog |
| `list_catalogs` | List all catalogs |
| `preview_table` | Get sample rows from table |

### Compute Management
| Tool | Description |
|------|-------------|
| `list_clusters` | List all clusters |
| `get_cluster` | Get cluster details |
| `start_cluster` | Start a stopped cluster |
| `stop_cluster` | Stop a running cluster |
| `run_python_code` | Execute Python on cluster |
| `run_python_file` | Run a Python file remotely |

### Jobs & Workflows
| Tool | Description |
|------|-------------|
| `list_jobs` | List all jobs |
| `get_job` | Get job configuration |
| `create_job` | Create a new job |
| `update_job` | Modify job settings |
| `run_job` | Trigger a job run |
| `get_job_run` | Get run status/results |
| `cancel_job_run` | Cancel a running job |
| `list_job_runs` | List recent runs |

### Spark Declarative Pipelines (DLT)
| Tool | Description |
|------|-------------|
| `list_pipelines` | List all DLT pipelines |
| `get_pipeline` | Get pipeline configuration |
| `create_pipeline` | Create new pipeline |
| `update_pipeline` | Modify pipeline |
| `start_pipeline` | Trigger pipeline run |
| `stop_pipeline` | Stop running pipeline |
| `get_pipeline_update` | Get update status |

### Workspace & Files
| Tool | Description |
|------|-------------|
| `list_workspace` | List workspace directory |
| `read_workspace_file` | Read file/notebook content |
| `write_workspace_file` | Create/update file |
| `upload_file` | Upload local file |
| `upload_folder` | Upload directory |
| `delete_workspace_item` | Remove file/folder |

### Model Serving
| Tool | Description |
|------|-------------|
| `list_serving_endpoints` | List all endpoints |
| `get_serving_endpoint` | Get endpoint details |
| `query_serving_endpoint` | Send inference request |
| `create_serving_endpoint` | Deploy new endpoint |

### AI/BI & Dashboards
| Tool | Description |
|------|-------------|
| `list_dashboards` | List AI/BI dashboards |
| `create_dashboard` | Create new dashboard |
| `get_dashboard` | Get dashboard details |

### Genie & Agents
| Tool | Description |
|------|-------------|
| `list_genie_spaces` | List Genie spaces |
| `create_genie_space` | Create new Genie space |
| `query_genie` | Ask Genie a question |

## Example Interactions

### Query Data
```
You: Run this query: SELECT count(*) FROM ml_prod.fraud.transactions WHERE date > '2024-01-01'

Claude: [Uses execute_sql tool]
The query returned 1,234,567 rows matching your criteria.
```

### Create a Job
```
You: Create a daily job that runs the notebook /Repos/user/project/etl at 6am

Claude: [Uses create_job tool]
Created job "ETL Daily" (job_id: 123456) scheduled for 6:00 AM UTC daily.
```

### Deploy a Pipeline
```
You: Create a DLT pipeline called "sales-pipeline" using notebooks in /Repos/user/pipelines/

Claude: [Uses create_pipeline tool]
Created pipeline "sales-pipeline" (pipeline_id: abc123). 
Ready to start with: start_pipeline
```

### Check Model Endpoint
```
You: What's the status of my fraud-detector endpoint?

Claude: [Uses get_serving_endpoint tool]
Endpoint "fraud-detector" is READY
- Model: ml_prod.models.fraud_detector v3
- Scale: 1-4 instances (currently 2)
- Latency p50: 45ms
```

## Troubleshooting

### MCP Server Not Starting
```bash
# Test manually
cd /path/to/ai-dev-kit
uv run python databricks-mcp-server/run_server.py

# Check for errors in output
```

### Authentication Errors
```bash
# Verify token works
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  "$DATABRICKS_HOST/api/2.0/clusters/list"
```

### Tool Not Found
- Restart Claude Code after changing mcp.json
- Check `defer_loading` is set to `true`
- Verify paths in mcp.json are absolute

### Permission Denied
- Ensure token has required permissions
- Check Unity Catalog grants for data access
- Verify cluster/warehouse access policies

## Configuration Options

### Full mcp.json with All Options
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/ai-dev-kit",
        "python", "databricks-mcp-server/run_server.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi...",
        "DATABRICKS_WAREHOUSE_ID": "abc123def456",
        "LOG_LEVEL": "INFO"
      },
      "defer_loading": true
    }
  }
}
```

### Multiple Workspaces
```json
{
  "mcpServers": {
    "databricks-dev": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ai-dev-kit",
               "python", "databricks-mcp-server/run_server.py"],
      "env": {
        "DATABRICKS_HOST": "https://dev-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi-dev-token..."
      }
    },
    "databricks-prod": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ai-dev-kit",
               "python", "databricks-mcp-server/run_server.py"],
      "env": {
        "DATABRICKS_HOST": "https://prod-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi-prod-token..."
      }
    }
  }
}
```

## Security Best Practices

1. **Token Scope**: Use tokens with minimum required permissions
2. **No Hardcoding**: Use environment variables or secret managers
3. **Rotate Tokens**: Regularly rotate personal access tokens
4. **Audit Logs**: Monitor Databricks audit logs for MCP activity
5. **Network**: Consider IP allowlisting for production workspaces

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code                             │
│  "Create a job that runs notebook X daily at 6am"           │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol (stdio)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              databricks-mcp-server                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  FastMCP Server                                      │    │
│  │  - Tool definitions (@mcp.tool decorators)          │    │
│  │  - Request routing                                   │    │
│  │  - Response formatting                               │    │
│  └─────────────────────┬───────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │ Python function calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              databricks-tools-core                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  High-level Databricks operations                    │    │
│  │  - SQL execution                                     │    │
│  │  - Job management                                    │    │
│  │  - Pipeline operations                               │    │
│  │  - Workspace file handling                           │    │
│  └─────────────────────┬───────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │ REST API calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Databricks Workspace                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   SQL    │ │   Jobs   │ │   DLT    │ │  Unity   │       │
│  │Warehouse │ │ Service  │ │ Pipelines│ │ Catalog  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Key Links
- AI Dev Kit: https://github.com/databricks-solutions/ai-dev-kit
- MCP Protocol: https://modelcontextprotocol.io/
- Databricks REST API: https://docs.databricks.com/api/
- Personal Access Tokens: https://docs.databricks.com/en/dev-tools/auth/pat.html
