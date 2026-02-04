# Claude Command: Databricks Deploy

This command helps you deploy MLflow models and Databricks Apps to production.

## Usage

```
/databricks-deploy
```

Or with options:
```
/databricks-deploy --type app
/databricks-deploy --type model-serving
/databricks-deploy --endpoint my-endpoint
```

## What This Command Does

1. Analyzes your project structure (MLflow model, Gradio/Streamlit app, etc.)
2. Creates or updates `databricks.yml` asset bundle configuration
3. Generates appropriate deployment resources
4. Validates configuration before deployment
5. Provides deployment commands

## Deployment Types

### Model Serving Endpoint
Deploys an MLflow model from Unity Catalog to a real-time serving endpoint.

```yaml
resources:
  model_serving_endpoints:
    my_endpoint:
      name: "my-model-serving"
      config:
        served_entities:
          - entity_name: "catalog.schema.model"
            entity_version: "1"
            workload_size: "Small"
            scale_to_zero_enabled: true
```

### Databricks App
Deploys a Gradio or Streamlit application.

```yaml
resources:
  apps:
    my_app:
      name: "my-ml-app"
      description: "ML Application"
      source_code_path: .
```

## Project Structure

For Apps:
```
my_app/
├── app.py              # Gradio/Streamlit app
├── databricks.yml      # Asset bundle config
├── requirements.txt
└── src/
    └── utils.py
```

For Model Serving:
```
my_model/
├── model_code.py       # MLflow model
├── databricks.yml      # Asset bundle config
└── log_model.py        # Logging script
```

## databricks.yml Template

```yaml
bundle:
  name: my-project

workspace:
  host: https://your-workspace.cloud.databricks.com

resources:
  apps:
    my_app:
      name: "${bundle.name}-app"
      description: "Description"
      source_code_path: .

  model_serving_endpoints:
    my_endpoint:
      name: "${bundle.name}-serving"
      config:
        served_entities:
          - entity_name: "catalog.schema.model"
            entity_version: "1"
            workload_size: "Small"
            scale_to_zero_enabled: true

targets:
  dev:
    workspace:
      host: https://dev-workspace.cloud.databricks.com
  prod:
    workspace:
      host: https://prod-workspace.cloud.databricks.com
```

## Best Practices

### Model Serving
- Enable `scale_to_zero_enabled: true` for cost optimization
- Start with "Small" workload size, scale as needed
- Use traffic splitting for A/B testing new model versions
- Set up alerts for latency and error rate

### Databricks Apps
- Use environment variables for secrets
- Test locally with `databricks apps run-local`
- Keep apps stateless when possible
- Use Unity Catalog for data access

### General
- Use targets for dev/staging/prod environments
- Version your `databricks.yml` in git
- Use variable substitution: `${bundle.name}`
- Validate before deploy: `databricks bundle validate`

## Command Options

- `--type <app|model-serving>`: Deployment type
- `--endpoint <name>`: Serving endpoint name
- `--target <dev|staging|prod>`: Deployment target
- `--validate-only`: Only validate, don't deploy
- `--workload-size <Small|Medium|Large>`: Serving capacity

## Deployment Commands

After generating configuration:

```bash
# Validate bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy --target dev

# Deploy to production
databricks bundle deploy --target prod

# Run app locally for testing
databricks apps run-local --app-dir .
```

## Environment Variables

Set these for authentication:
```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
```

Or use Databricks CLI profiles:
```bash
databricks configure --profile my-workspace
```

## Monitoring Deployed Resources

```bash
# Check endpoint status
databricks serving-endpoints get my-endpoint

# View app logs
databricks apps get-logs my-app

# List deployments
databricks bundle summary
```

## Related Commands

- `/mlflow-log-model`: Create and log MLflow models
- `/mlflow-experiment`: Set up experiment tracking
