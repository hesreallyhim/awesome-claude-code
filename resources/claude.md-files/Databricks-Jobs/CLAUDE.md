# Databricks Jobs & Workflow Automation Guide

## Overview
Databricks Jobs (Workflows) enable you to orchestrate data pipelines, ML training, and inference workflows with scheduling, dependencies, and monitoring. This guide covers job creation, asset bundles, and production deployment patterns.

## Build & Test Commands
- Databricks CLI: `databricks jobs`
- List jobs: `databricks jobs list`
- Run job: `databricks jobs run-now --job-id <id>`
- Asset bundles: `databricks bundle deploy`
- Validate bundle: `databricks bundle validate`

## Job Types

| Type | Use Case | Example |
|------|----------|---------|
| Notebook | Interactive development, ad-hoc analysis | Feature engineering |
| Python Script | Production Python code | Model training |
| Python Wheel | Packaged applications | ML pipelines |
| JAR | Scala/Java applications | Spark ETL |
| SQL | Data transformations | Aggregations |
| dbt | dbt transformations | Analytics |
| Pipeline (DLT) | Delta Live Tables | Streaming ETL |

## Creating Jobs with Asset Bundles

### Project Structure
```
my_ml_pipeline/
├── databricks.yml           # Bundle configuration
├── resources/
│   ├── jobs.yml             # Job definitions
│   └── pipelines.yml        # DLT pipeline definitions
├── src/
│   ├── train_model.py       # Training script
│   ├── score_batch.py       # Batch scoring
│   └── feature_eng.py       # Feature engineering
├── notebooks/
│   └── exploration.py       # Databricks notebook
├── tests/
│   └── test_pipeline.py
└── requirements.txt
```

### databricks.yml
```yaml
bundle:
  name: ml-pipeline

variables:
  catalog:
    default: ml_dev
  warehouse_id:
    description: SQL Warehouse ID for queries

workspace:
  host: https://your-workspace.cloud.databricks.com

include:
  - resources/*.yml

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: ml_dev
  staging:
    variables:
      catalog: ml_staging
  prod:
    mode: production
    variables:
      catalog: ml_prod
    run_as:
      service_principal_name: ml-pipeline-sp
```

### resources/jobs.yml
```yaml
resources:
  jobs:
    ml_training_pipeline:
      name: "[${bundle.target}] ML Training Pipeline"
      description: "Daily model training job"

      # Job clusters for cost optimization
      job_clusters:
        - job_cluster_key: training_cluster
          new_cluster:
            spark_version: "14.3.x-cpu-ml-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 4
            spark_conf:
              spark.databricks.delta.preview.enabled: "true"
            custom_tags:
              team: ml-platform
              project: fraud-detection

      # Task definitions
      tasks:
        - task_key: feature_engineering
          job_cluster_key: training_cluster
          python_wheel_task:
            package_name: ml_pipeline
            entry_point: feature_eng
            parameters:
              - --catalog=${var.catalog}
              - --date={{ ds }}
          libraries:
            - whl: ../dist/*.whl

        - task_key: train_model
          depends_on:
            - task_key: feature_engineering
          job_cluster_key: training_cluster
          python_wheel_task:
            package_name: ml_pipeline
            entry_point: train_model
            parameters:
              - --catalog=${var.catalog}
              - --experiment=/Users/${workspace.current_user.userName}/fraud-detection

        - task_key: validate_model
          depends_on:
            - task_key: train_model
          job_cluster_key: training_cluster
          notebook_task:
            notebook_path: ../notebooks/validate_model.py
            base_parameters:
              catalog: ${var.catalog}

        - task_key: deploy_model
          depends_on:
            - task_key: validate_model
          condition_task:
            op: EQUAL_TO
            left: "{{tasks.validate_model.values.validation_passed}}"
            right: "true"

        - task_key: promote_to_champion
          depends_on:
            - task_key: deploy_model
          python_wheel_task:
            package_name: ml_pipeline
            entry_point: promote_model
            parameters:
              - --model-name=${var.catalog}.ml_models.fraud_detector
              - --alias=champion

      # Schedule
      schedule:
        quartz_cron_expression: "0 0 6 * * ?"  # Daily at 6 AM
        timezone_id: America/New_York
        pause_status: UNPAUSED

      # Notifications
      email_notifications:
        on_failure:
          - ml-team@company.com
        on_success:
          - ml-team@company.com

      # Timeout and retries
      timeout_seconds: 7200  # 2 hours
      max_retries: 2
      retry_on_timeout: true

      # Tags
      tags:
        team: ml-platform
        cost_center: "12345"
```

## Multi-Task Workflows

### Task Dependencies
```yaml
tasks:
  - task_key: extract_data
    # No dependencies - runs first

  - task_key: transform_features
    depends_on:
      - task_key: extract_data
    # Runs after extract_data

  - task_key: train_model_a
    depends_on:
      - task_key: transform_features
    # Runs after transform_features

  - task_key: train_model_b
    depends_on:
      - task_key: transform_features
    # Runs in PARALLEL with train_model_a

  - task_key: evaluate_models
    depends_on:
      - task_key: train_model_a
      - task_key: train_model_b
    # Waits for BOTH models to complete
```

### Conditional Tasks
```yaml
tasks:
  - task_key: check_data_quality
    notebook_task:
      notebook_path: ./check_quality.py
    # Must set task value: dbutils.jobs.taskValues.set("quality_score", 0.95)

  - task_key: proceed_if_quality_good
    depends_on:
      - task_key: check_data_quality
    condition_task:
      op: GREATER_THAN
      left: "{{tasks.check_data_quality.values.quality_score}}"
      right: "0.9"

  - task_key: train_model
    depends_on:
      - task_key: proceed_if_quality_good
        outcome: "true"  # Only run if condition passed
```

### For-Each Tasks (Parallel Loops)
```yaml
tasks:
  - task_key: train_models_parallel
    for_each_task:
      inputs: "[\"xgboost\", \"lightgbm\", \"catboost\"]"
      concurrency: 3
      task:
        task_key: train_single_model
        python_wheel_task:
          package_name: ml_pipeline
          entry_point: train_model
          parameters:
            - --algorithm={{input}}
```

## Passing Data Between Tasks

### Using Task Values
```python
# In first task (Python notebook or script)
from pyspark.dbutils import DBUtils
dbutils = DBUtils(spark)

# Set a value for downstream tasks
model_version = "3"
dbutils.jobs.taskValues.set(key="model_version", value=model_version)

# Set multiple values
dbutils.jobs.taskValues.set(key="metrics", value={
    "accuracy": 0.95,
    "f1_score": 0.92
})
```

```python
# In downstream task
dbutils = DBUtils(spark)

# Get value from upstream task
model_version = dbutils.jobs.taskValues.get(
    taskKey="train_model",
    key="model_version"
)

# Use in job YAML with template syntax
# parameters: ["--model-version={{tasks.train_model.values.model_version}}"]
```

### Using Temporary Tables
```python
# Task 1: Write results to temp table
results_df.write.mode("overwrite").saveAsTable("tmp.pipeline_results")

# Task 2: Read from temp table
results = spark.table("tmp.pipeline_results")
```

## Cluster Configuration

### Job Clusters vs All-Purpose Clusters
```yaml
# Job cluster (recommended for production)
job_clusters:
  - job_cluster_key: training_cluster
    new_cluster:
      spark_version: "14.3.x-cpu-ml-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 4
      autoscale:
        min_workers: 2
        max_workers: 8

# Existing cluster (for development)
tasks:
  - task_key: dev_task
    existing_cluster_id: "1234-567890-abcdef"
```

### Instance Pools for Faster Startup
```yaml
job_clusters:
  - job_cluster_key: fast_cluster
    new_cluster:
      spark_version: "14.3.x-cpu-ml-scala2.12"
      instance_pool_id: "0123-456789-pool"
      driver_instance_pool_id: "0123-456789-pool"
      num_workers: 4
```

### Spot Instances for Cost Savings
```yaml
new_cluster:
  spark_version: "14.3.x-cpu-ml-scala2.12"
  node_type_id: "i3.xlarge"
  num_workers: 4
  aws_attributes:
    first_on_demand: 1  # Driver is on-demand
    availability: SPOT_WITH_FALLBACK
    spot_bid_price_percent: 100
```

## Serverless Jobs

```yaml
tasks:
  - task_key: serverless_task
    # No cluster config needed
    notebook_task:
      notebook_path: ./my_notebook.py
      warehouse_id: ${var.warehouse_id}  # For SQL operations

    # Enable serverless compute
    environment_key: default  # Uses serverless
```

## Monitoring & Alerting

### Job Run Notifications
```yaml
email_notifications:
  on_start:
    - ml-team@company.com
  on_success:
    - ml-team@company.com
  on_failure:
    - oncall@company.com
    - ml-team@company.com
  on_duration_warning_threshold_exceeded:
    - ml-team@company.com

webhook_notifications:
  on_failure:
    - id: slack_webhook
      # Configure webhook in workspace settings

notification_settings:
  no_alert_for_skipped_runs: true
  no_alert_for_canceled_runs: false
```

### Health Rules
```yaml
health:
  rules:
    - metric: RUN_DURATION_SECONDS
      op: GREATER_THAN
      value: 3600  # Alert if > 1 hour
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy ML Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Configure Databricks
        run: |
          databricks configure --token <<EOF
          ${{ secrets.DATABRICKS_HOST }}
          ${{ secrets.DATABRICKS_TOKEN }}
          EOF

      - name: Validate Bundle
        run: databricks bundle validate -t prod

      - name: Deploy Bundle
        run: databricks bundle deploy -t prod

      - name: Run Tests
        run: databricks bundle run ml_pipeline_tests -t prod
```

### Triggering Jobs Programmatically
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Trigger job run
run = w.jobs.run_now(
    job_id=123456,
    notebook_params={"date": "2024-01-15"},
    python_params=["--mode", "full"]
)

# Wait for completion
result = w.jobs.wait_get_run_job_terminated_or_skipped(run_id=run.run_id)
print(f"Run completed with state: {result.state.result_state}")
```

## Common Patterns

### Incremental Processing
```python
# Get last successful run date
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
runs = w.jobs.list_runs(job_id=job_id, completed_only=True, limit=1)
last_run = next(runs)
last_date = last_run.start_time

# Process only new data
df = spark.table("source_table").filter(f"date > '{last_date}'")
```

### Retry with Backoff
```yaml
max_retries: 3
min_retry_interval_millis: 60000  # 1 minute
retry_on_timeout: true
```

### Parameterized Runs
```yaml
parameters:
  - name: start_date
    default: "2024-01-01"
  - name: end_date
    default: "2024-01-31"
  - name: model_version
    default: "latest"

tasks:
  - task_key: process_data
    python_wheel_task:
      parameters:
        - --start-date={{job.parameters.start_date}}
        - --end-date={{job.parameters.end_date}}
```

## Best Practices

1. **Use Asset Bundles**: Version control your job definitions
2. **Job Clusters**: Use job clusters for production, not all-purpose
3. **Idempotency**: Design tasks to be safely re-runnable
4. **Monitoring**: Set up alerts for failures and duration anomalies
5. **Cost Tags**: Tag clusters for cost attribution
6. **Secrets**: Use secret scopes, never hardcode credentials
7. **Testing**: Run jobs in dev/staging before production

## Key Links
- Databricks Jobs: https://docs.databricks.com/en/workflows/jobs/jobs.html
- Asset Bundles: https://docs.databricks.com/en/dev-tools/bundles/
- Job API: https://docs.databricks.com/api/workspace/jobs
