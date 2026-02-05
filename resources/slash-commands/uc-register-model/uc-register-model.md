# Claude Command: Unity Catalog Register Model

Register and manage MLflow models in Unity Catalog with proper governance.

## Usage

```
/uc-register-model
/uc-register-model --model-name catalog.schema.model_name
/uc-register-model --alias champion
```

## What This Command Does

1. Configures MLflow to use Unity Catalog registry
2. Registers trained models with proper naming
3. Sets up model aliases (champion/challenger)
4. Configures permissions and tags

## Model Registration Pattern

```python
import mlflow

mlflow.set_registry_uri("databricks-uc")

with mlflow.start_run():
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="catalog.schema.model_name"
    )
```

## Alias Management

```python
from mlflow import MlflowClient

client = MlflowClient(registry_uri="databricks-uc")

# Set champion alias
client.set_registered_model_alias(
    name="catalog.schema.model_name",
    alias="champion",
    version=5
)
```

## Loading Models

```python
# By alias (recommended)
model = mlflow.pyfunc.load_model("models:/catalog.schema.model@champion")

# By version
model = mlflow.pyfunc.load_model("models:/catalog.schema.model/5")
```

## Best Practices

- Use three-level namespace: `catalog.schema.model_name`
- Always deploy via aliases, not version numbers
- Tag models with team ownership and data classification
- Use separate catalogs for dev/staging/prod
