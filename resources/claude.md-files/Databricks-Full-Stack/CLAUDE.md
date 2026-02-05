# Databricks & MLflow Development Guide

## Table of Contents

### Core ML Platform
| Guide | Description |
|-------|-------------|
| [MLflow](docs/databricks/mlflow.md) | Models from Code, experiment tracking, model registry |
| [Unity Catalog](docs/databricks/unity-catalog.md) | Governance, aliases, access control, lineage |
| [Feature Engineering](docs/databricks/feature-engineering.md) | Feature Store, point-in-time lookups, online serving |

### Data Pipelines
| Guide | Description |
|-------|-------------|
| [Delta Live Tables](docs/databricks/delta-live-tables.md) | Medallion architecture, streaming, CDC, expectations |
| [Jobs & Workflows](docs/databricks/jobs.md) | Asset bundles, scheduling, multi-task pipelines |

### AI & GenAI
| Guide | Description |
|-------|-------------|
| [Mosaic AI Agents](docs/databricks/mosaic-agents.md) | ChatAgent, tool calling, RAG agents, evaluation |
| [Vector Search](docs/databricks/vector-search.md) | Embeddings, similarity search, RAG pipelines |
| [DSPy](docs/databricks/dspy.md) | Programming LMs with signatures, modules, optimizers |

### Apps & Tooling
| Guide | Description |
|-------|-------------|
| [APX Apps](docs/databricks/apx-apps.md) | FastAPI + React apps with Databricks integration |
| [AI Dev Kit](docs/databricks/ai-dev-kit.md) | MCP server, tools-core library, skills |
| [MCP Server Setup](docs/databricks/mcp-server.md) | Configure Claude Code with Databricks tools |

---

## Development Methodology

### 1. Project Setup

```bash
# Initialize with APX for apps
uvx --index https://databricks-solutions.github.io/apx/simple apx init my-project

# Or standard Python project
mkdir my-project && cd my-project
uv init
uv add mlflow databricks-sdk pyspark
```

### 2. Local Development Loop

```
┌─────────────────────────────────────────────────────┐
│  1. WRITE CODE                                      │
│     - Use patterns from docs/databricks/*.md        │
│     - Follow code style guidelines below            │
└───────────────────────┬─────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│  2. TEST LOCALLY                                    │
│     - pytest for unit tests                         │
│     - mlflow run for ML code                        │
│     - apx run for apps                              │
└───────────────────────┬─────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│  3. VALIDATE                                        │
│     - databricks bundle validate                    │
│     - ruff check . && ruff format .                 │
└───────────────────────┬─────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│  4. DEPLOY TO DEV                                   │
│     - databricks bundle deploy -t dev               │
│     - Test in Databricks workspace                  │
└───────────────────────┬─────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│  5. PROMOTE                                         │
│     - databricks bundle deploy -t prod              │
│     - Tag model alias: champion                     │
└─────────────────────────────────────────────────────┘
```

### 3. Git Workflow

```bash
# Feature branch
git checkout -b feature/my-feature

# Develop, test, commit
git add .
git commit -m "feat: add feature X"

# Push and create PR
git push -u origin feature/my-feature
gh pr create --fill
```

**Commit Prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance

### 4. Code Style

**Python:**
- Use type hints for all function signatures
- Format with `ruff format`
- Lint with `ruff check`
- Docstrings for public functions

**SQL:**
- UPPERCASE keywords
- snake_case for identifiers
- CTEs over subqueries

**Naming Conventions:**
- Tables: `catalog.schema.noun_noun` (e.g., `ml_prod.fraud.transactions`)
- Models: `catalog.schema.model_name` (e.g., `ml_prod.models.fraud_detector`)
- Features: `noun_metric_window` (e.g., `customer_spend_30d`)
- Jobs: `domain-action-frequency` (e.g., `fraud-training-daily`)

### 5. MLflow Experiment Tracking

```python
import mlflow

mlflow.set_experiment("/Users/you@company.com/project-name")

with mlflow.start_run(run_name="descriptive-name"):
    # Log parameters at start
    mlflow.log_params({"model": "xgboost", "n_estimators": 100})

    # Train model
    model = train(...)

    # Log metrics
    mlflow.log_metrics({"accuracy": 0.95, "f1": 0.92})

    # Log model to Unity Catalog
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="catalog.schema.model_name"
    )
```

### 6. Testing Strategy

| Level | Tool | What to Test |
|-------|------|--------------|
| Unit | pytest | Pure functions, transformations |
| Integration | pytest + spark | DataFrame operations, UDFs |
| Model | mlflow.evaluate | Model quality metrics |
| Pipeline | DLT expectations | Data quality rules |
| E2E | Databricks Jobs | Full workflow in dev |

```python
# Example test structure
tests/
├── unit/
│   └── test_transformations.py
├── integration/
│   └── test_feature_pipeline.py
└── model/
    └── test_model_quality.py
```

### 7. Deployment Checklist

- [ ] All tests passing
- [ ] Bundle validates: `databricks bundle validate`
- [ ] Code reviewed and approved
- [ ] Model registered in Unity Catalog
- [ ] Model alias set (challenger → champion)
- [ ] Monitoring configured (inference tables)
- [ ] Alerts set up for failures
- [ ] Documentation updated

---

## Quick Commands

```bash
# MLflow
mlflow ui --port 5000                    # Local UI
mlflow run . -P param=value              # Run project

# Databricks CLI
databricks workspace list /              # List workspace
databricks jobs list                     # List jobs
databricks bundle deploy -t dev          # Deploy bundle
databricks bundle run job_name -t dev    # Run job

# APX Apps
apx init my-app                          # Create app
apx run                                  # Dev server
apx deploy                               # Deploy to Databricks

# Testing
pytest tests/ -v                         # Run tests
ruff check . --fix                       # Lint and fix
ruff format .                            # Format code
```

---

## Environment Setup

```bash
# Required environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."

# Optional
export MLFLOW_TRACKING_URI="databricks"
export DATABRICKS_WAREHOUSE_ID="abc123"
```

## Project Structure Template

```
my-ml-project/
├── CLAUDE.md                 # This file (or copy relevant sections)
├── databricks.yml            # Asset bundle configuration
├── pyproject.toml            # Python dependencies
├── src/
│   ├── pipelines/            # DLT pipeline definitions
│   ├── features/             # Feature engineering code
│   ├── models/               # Model training code
│   └── serving/              # Inference/serving code
├── notebooks/                # Exploration notebooks
├── tests/
│   ├── unit/
│   ├── integration/
│   └── model/
└── docs/                     # Additional documentation
```
