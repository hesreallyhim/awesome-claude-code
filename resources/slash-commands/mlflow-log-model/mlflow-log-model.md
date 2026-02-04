# Claude Command: MLflow Log Model

This command helps you create and log MLflow models using the "Models from Code" pattern.

## Usage

```
/mlflow-log-model
```

Or with options:
```
/mlflow-log-model --type pyfunc
/mlflow-log-model --type langchain
/mlflow-log-model --unity-catalog my_catalog.my_schema.my_model
```

## What This Command Does

1. Analyzes your current project to understand the model type and dependencies
2. Creates the model code file (`model_code.py`) with proper structure
3. Creates the driver script for logging the model
4. Sets up proper `mlflow.models.set_model()` call
5. Identifies and specifies pip requirements from imports
6. Optionally registers to Unity Catalog

## Models from Code Structure

The command generates:

```
your_project/
├── model_code.py      # Model class with PythonModel inheritance
└── log_model.py       # Driver script to log the model
```

## Model Code Template

```python
import mlflow
from mlflow.pyfunc import PythonModel

class YourModel(PythonModel):
    def __init__(self):
        pass

    def load_context(self, context):
        # Load artifacts, initialize clients
        pass

    def predict(self, context, model_input, params=None):
        # Your inference logic
        return model_input

# Required for Models from Code
mlflow.models.set_model(YourModel())
```

## Best Practices

- **Minimal imports**: Only import what you use - MLflow infers requirements from imports
- **Single file**: Keep model code in one file when possible
- **Use code_paths**: For local modules that aren't pip-installable
- **Test locally**: Run `mlflow.pyfunc.load_model()` before deploying

## When to Use Models from Code

Use this pattern for:
- GenAI agents and LLM applications
- Custom inference logic without trained weights
- Applications requiring auditable, readable code
- Complex dependency scenarios

Do NOT use for:
- Traditional ML with trained weights (use `sklearn.log_model()`, etc.)
- Simple models that serialize well with pickle

## Command Options

- `--type <pyfunc|langchain|custom>`: Specify model flavor
- `--unity-catalog <catalog.schema.model>`: Register to Unity Catalog
- `--experiment <name>`: Set MLflow experiment name
- `--artifacts <path>`: Additional artifacts to log

## Example Output

After running `/mlflow-log-model`, you'll have:

1. A `model_code.py` with your model class
2. A `log_model.py` driver script
3. Instructions for testing and deployment

## Integration with Databricks

When using `--unity-catalog`:
- Sets registry URI to `databricks-uc`
- Uses three-level namespace (catalog.schema.model)
- Enables model governance and lineage tracking

## Related Commands

- `/databricks-deploy`: Deploy model to serving endpoint
- `/mlflow-experiment`: Set up experiment tracking
