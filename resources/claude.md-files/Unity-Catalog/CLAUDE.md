# Unity Catalog Development Guide

## Overview
Unity Catalog provides centralized governance for data and AI assets across Databricks workspaces. This guide covers model management, data governance, lineage tracking, and access control patterns.

## Three-Level Namespace
```
catalog.schema.asset
├── catalog    → Top-level container (e.g., prod, dev, ml)
├── schema     → Logical grouping (e.g., fraud_detection, recommendations)
└── asset      → Tables, models, volumes, functions
```

## Build & Test Commands
- Databricks CLI: `databricks unity-catalog`
- List catalogs: `databricks catalogs list`
- List schemas: `databricks schemas list --catalog-name <catalog>`
- List models: `databricks registered-models list --catalog-name <catalog> --schema-name <schema>`

## Model Registry with Unity Catalog

### Setting Up MLflow for Unity Catalog
```python
import mlflow

# CRITICAL: Set registry URI before any model operations
mlflow.set_registry_uri("databricks-uc")

# Set experiment in Unity Catalog
mlflow.set_experiment("/Users/you@company.com/my-experiment")
```

### Registering Models
```python
# Method 1: Log and register in one step
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model="model_code.py",
        registered_model_name="prod.ml_models.fraud_detector"
    )

# Method 2: Register existing run
mlflow.register_model(
    model_uri="runs:/abc123/model",
    name="prod.ml_models.fraud_detector"
)
```

### Model Versioning and Aliases
```python
from mlflow import MlflowClient

client = MlflowClient()

# Set alias for production deployment
client.set_registered_model_alias(
    name="prod.ml_models.fraud_detector",
    alias="champion",
    version=3
)

# Set alias for staging/challenger
client.set_registered_model_alias(
    name="prod.ml_models.fraud_detector",
    alias="challenger",
    version=4
)

# Load model by alias
model = mlflow.pyfunc.load_model("models:/prod.ml_models.fraud_detector@champion")
```

### Model Tags and Descriptions
```python
# Add model-level tags
client.set_registered_model_tag(
    name="prod.ml_models.fraud_detector",
    key="team",
    value="fraud-ml"
)

# Add version-level tags
client.set_model_version_tag(
    name="prod.ml_models.fraud_detector",
    version=3,
    key="validation_status",
    value="approved"
)

# Update description
client.update_registered_model(
    name="prod.ml_models.fraud_detector",
    description="Fraud detection model using XGBoost. Trained on 2024 data."
)
```

## Data Governance

### Creating Catalogs and Schemas
```sql
-- Create catalog with managed location
CREATE CATALOG IF NOT EXISTS ml_prod
MANAGED LOCATION 's3://my-bucket/unity-catalog/ml_prod';

-- Create schema
CREATE SCHEMA IF NOT EXISTS ml_prod.fraud_detection
COMMENT 'Fraud detection models and feature tables';

-- Grant permissions
GRANT USE CATALOG ON CATALOG ml_prod TO `data-scientists`;
GRANT USE SCHEMA ON SCHEMA ml_prod.fraud_detection TO `data-scientists`;
GRANT SELECT ON SCHEMA ml_prod.fraud_detection TO `data-scientists`;
```

### Table Access Control
```sql
-- Grant table-level permissions
GRANT SELECT ON TABLE ml_prod.fraud_detection.features TO `ml-engineers`;
GRANT MODIFY ON TABLE ml_prod.fraud_detection.features TO `feature-engineers`;

-- Row-level security with row filters
ALTER TABLE ml_prod.fraud_detection.transactions
SET ROW FILTER security.region_filter ON (region);

-- Column masking
ALTER TABLE ml_prod.fraud_detection.customers
ALTER COLUMN ssn SET MASK security.mask_ssn;
```

## Lineage Tracking

### Viewing Lineage in Python
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Get table lineage
lineage = w.lineage.get_table_lineage(
    table_name="ml_prod.fraud_detection.features"
)

# Get model lineage (what tables were used to train)
model_lineage = w.lineage.get_model_lineage(
    model_name="ml_prod.ml_models.fraud_detector"
)
```

### Automatic Lineage Capture
```python
# MLflow automatically captures lineage when you log datasets
with mlflow.start_run():
    # Log training data - creates lineage link
    mlflow.log_input(
        mlflow.data.from_spark(training_df, table_name="ml_prod.fraud_detection.features"),
        context="training"
    )

    # Train and log model
    mlflow.sklearn.log_model(model, "model")
```

## Volumes for Unstructured Data

### Creating and Using Volumes
```sql
-- Create managed volume
CREATE VOLUME ml_prod.fraud_detection.model_artifacts
COMMENT 'Model artifacts and checkpoints';

-- Create external volume
CREATE EXTERNAL VOLUME ml_prod.fraud_detection.raw_data
LOCATION 's3://my-bucket/raw-data';
```

```python
# Access volume in Python
volume_path = "/Volumes/ml_prod/fraud_detection/model_artifacts"

# Write files
with open(f"{volume_path}/config.json", "w") as f:
    json.dump(config, f)

# Read files
import pandas as pd
df = pd.read_parquet(f"{volume_path}/data.parquet")
```

## Functions (UDFs) in Unity Catalog

### Registering Python UDFs
```sql
CREATE OR REPLACE FUNCTION ml_prod.fraud_detection.score_transaction(
    amount DOUBLE,
    merchant_category STRING,
    time_since_last_txn DOUBLE
)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
import pickle
import numpy as np

# Load model from volume
with open("/Volumes/ml_prod/fraud_detection/models/scorer.pkl", "rb") as f:
    model = pickle.load(f)

features = np.array([[amount, hash(merchant_category) % 100, time_since_last_txn]])
return float(model.predict_proba(features)[0, 1])
$$;
```

### Using UDFs
```sql
SELECT
    transaction_id,
    ml_prod.fraud_detection.score_transaction(amount, merchant, time_diff) as fraud_score
FROM ml_prod.fraud_detection.transactions
WHERE fraud_score > 0.8;
```

## Cross-Workspace Sharing

### Sharing Models Across Workspaces
```python
# In source workspace: Create share
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create a share
w.shares.create(
    name="fraud_models_share",
    comment="Fraud detection models for partner teams"
)

# Add model to share
w.shares.update(
    name="fraud_models_share",
    updates=[{
        "action": "ADD",
        "data_object": {
            "name": "ml_prod.ml_models.fraud_detector",
            "data_object_type": "MODEL"
        }
    }]
)

# Grant access to recipient
w.shares.share_permissions.update(
    name="fraud_models_share",
    changes=[{
        "principal": "partner_workspace",
        "add": ["SELECT"]
    }]
)
```

## Best Practices

### Naming Conventions
```
Catalogs:  {env}_{domain}        → prod_ml, dev_analytics
Schemas:   {project}_{version}   → fraud_detection_v2
Models:    {task}_{algorithm}    → fraud_classifier_xgb
Tables:    {entity}_{suffix}     → transactions_features, customers_labels
```

### Environment Strategy
```
dev.ml_models.fraud_detector      → Development/experimentation
staging.ml_models.fraud_detector  → Pre-production validation
prod.ml_models.fraud_detector     → Production deployment
```

### Model Promotion Pattern
```python
def promote_model(model_name: str, source_env: str, target_env: str, version: int):
    """Promote model from one environment to another."""
    source_model = f"{source_env}.ml_models.{model_name}"
    target_model = f"{target_env}.ml_models.{model_name}"

    # Copy model version
    client = MlflowClient()
    client.copy_model_version(
        src_model_uri=f"models:/{source_model}/{version}",
        dst_name=target_model
    )

    # Set alias on target
    new_version = client.get_latest_versions(target_model)[0].version
    client.set_registered_model_alias(target_model, "champion", new_version)
```

## Debugging & Troubleshooting

### Common Issues
```python
# Check if catalog exists
spark.sql("SHOW CATALOGS").show()

# Check permissions
spark.sql("SHOW GRANTS ON CATALOG ml_prod").show()
spark.sql("SHOW GRANTS ON MODEL ml_prod.ml_models.fraud_detector").show()

# Verify MLflow registry URI
print(mlflow.get_registry_uri())  # Should be "databricks-uc"
```

### Permission Errors
```sql
-- Grant minimum required permissions for model registration
GRANT USE CATALOG ON CATALOG ml_prod TO `user@company.com`;
GRANT USE SCHEMA ON SCHEMA ml_prod.ml_models TO `user@company.com`;
GRANT CREATE MODEL ON SCHEMA ml_prod.ml_models TO `user@company.com`;
```

## Key Links
- Unity Catalog Overview: https://docs.databricks.com/en/data-governance/unity-catalog/
- Models in Unity Catalog: https://docs.databricks.com/en/mlflow/models-in-uc.html
- Unity Catalog Best Practices: https://docs.databricks.com/en/data-governance/unity-catalog/best-practices.html
