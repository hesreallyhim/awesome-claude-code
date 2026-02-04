# Claude Command: Databricks Job

Create and configure Databricks Jobs (Workflows) with asset bundles for ML pipelines.

## Usage

```
/databricks-job
/databricks-job --name ml-training-pipeline
/databricks-job --schedule daily
```

## What This Command Does

1. Generates `databricks.yml` asset bundle configuration
2. Creates job definitions with tasks and dependencies
3. Sets up cluster configurations
4. Configures scheduling and notifications

## Job Configuration Template

```yaml
resources:
  jobs:
    ml_pipeline:
      name: "ML Training Pipeline"
      
      job_clusters:
        - job_cluster_key: training
          new_cluster:
            spark_version: "14.3.x-cpu-ml-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 4

      tasks:
        - task_key: feature_engineering
          job_cluster_key: training
          python_wheel_task:
            package_name: ml_pipeline
            entry_point: features

        - task_key: train_model
          depends_on:
            - task_key: feature_engineering
          notebook_task:
            notebook_path: ./train.py

      schedule:
        quartz_cron_expression: "0 0 6 * * ?"
        timezone_id: America/New_York
```

## Task Types

- `notebook_task`: Run a notebook
- `python_wheel_task`: Run packaged Python code
- `spark_python_task`: Run a Python script
- `sql_task`: Run SQL queries
- `dbt_task`: Run dbt transformations

## Multi-Task Dependencies

```yaml
tasks:
  - task_key: extract
  - task_key: transform
    depends_on: [{task_key: extract}]
  - task_key: train_a
    depends_on: [{task_key: transform}]
  - task_key: train_b
    depends_on: [{task_key: transform}]
  - task_key: evaluate
    depends_on:
      - {task_key: train_a}
      - {task_key: train_b}
```

## Best Practices

- Use job clusters for production (not all-purpose)
- Enable autoscaling for variable workloads
- Set up email notifications for failures
- Use targets for dev/staging/prod environments
