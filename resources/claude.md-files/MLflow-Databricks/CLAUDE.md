# MLflow & Databricks Development Guide

## Overview
This guide covers MLflow model development with emphasis on the "Models from Code" pattern, Databricks Apps development, Unity Catalog integration, and production ML workflows.

## Build & Test Commands
- Install dependencies: `pip install mlflow databricks-sdk`
- Run MLflow UI: `mlflow ui --port 5000`
- Run tests: `pytest tests/ -v`
- Databricks CLI: `databricks workspace list /`
- Validate model: `mlflow models validate --model-uri runs:/<run_id>/model`

## MLflow Models from Code Pattern

### When to Use Models from Code
- GenAI agents and LLM-based applications
- Custom inference logic without trained weights
- Applications requiring human-readable, auditable code
- Models with complex dependencies that don't serialize well

### When NOT to Use (Use Traditional log_model Instead)
- Traditional ML/DL models with trained weights (sklearn, pytorch, tensorflow)
- Models that benefit from optimized serialization
- Simple models without custom logic

### Models from Code Structure
```
my_model/
├── model_code.py      # Model class definition
├── driver.py          # Logging script (or notebook)
└── requirements.txt   # Dependencies
```

### Model Code Pattern (model_code.py)
```python
import mlflow
from mlflow.pyfunc import PythonModel

class MyModel(PythonModel):
    def __init__(self):
        # Initialize any state here
        pass

    def load_context(self, context):
        # Load artifacts, initialize clients, etc.
        # context.artifacts contains paths to logged artifacts
        pass

    def predict(self, context, model_input, params=None):
        # Your inference logic here
        # model_input is a pandas DataFrame by default
        return model_input

# CRITICAL: This line is required for Models from Code
mlflow.models.set_model(MyModel())
```

### Driver Script Pattern (driver.py)
```python
import mlflow

mlflow.set_experiment("/my-experiment")

with mlflow.start_run():
    # Log the model using code path
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model="model_code.py",  # Path to model code
        code_paths=["utils/"],          # Additional code dependencies
        pip_requirements=["pandas>=2.0", "requests"],
    )
```

## Databricks Apps Development

### Project Structure
```
databricks_app/
├── app.py                 # Main Gradio/Streamlit app
├── databricks.yml         # Databricks asset bundle config
├── requirements.txt
└── src/
    └── model_serving.py   # Model serving utilities
```

### databricks.yml Configuration
```yaml
bundle:
  name: my-ml-app

resources:
  apps:
    my_app:
      name: "my-ml-app"
      description: "ML Application"
      source_code_path: .

  model_serving_endpoints:
    my_model_endpoint:
      name: "my-model-serving"
      config:
        served_entities:
          - entity_name: "my_catalog.my_schema.my_model"
            entity_version: "1"
            workload_size: "Small"
            scale_to_zero_enabled: true
```

### Gradio App Pattern
```python
import gradio as gr
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage

w = WorkspaceClient()

def predict(text: str) -> str:
    response = w.serving_endpoints.query(
        name="my-model-serving",
        messages=[ChatMessage(role="user", content=text)]
    )
    return response.choices[0].message.content

demo = gr.Interface(fn=predict, inputs="text", outputs="text")
demo.launch()
```

## Unity Catalog Integration

### Registering Models to Unity Catalog
```python
import mlflow
mlflow.set_registry_uri("databricks-uc")

# Log and register in one step
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model="model_code.py",
        registered_model_name="my_catalog.my_schema.my_model"
    )
```

### Loading from Unity Catalog
```python
model_uri = "models:/my_catalog.my_schema.my_model/1"
model = mlflow.pyfunc.load_model(model_uri)
predictions = model.predict(input_data)
```

## Code Style Guidelines
- **Python**: Follow PEP 8, use type hints for function signatures
- **Imports**: Keep minimal - MLflow infers requirements from top-level imports
- **Naming**: snake_case for functions/variables, CamelCase for classes
- **Model Classes**: Always inherit from `mlflow.pyfunc.PythonModel`
- **Error Handling**: Use custom exceptions, log errors with `mlflow.log_param("error", str(e))`

## Best Practices

### Models from Code
- Only import packages you actually use (MLflow infers deps from imports)
- Use `code_paths` for non-pip-installable local modules
- Always call `mlflow.models.set_model()` at module level
- Keep model code in a single file when possible

### Databricks Apps
- Use environment variables for secrets: `os.environ.get("DB_TOKEN")`
- Enable scale-to-zero for cost optimization
- Use Unity Catalog for model governance
- Test locally with `databricks apps run-local`

### Experiment Tracking
- Use descriptive experiment names: `/Users/you@company.com/project-name`
- Log hyperparameters at the start of runs
- Log metrics iteratively for training curves
- Use `mlflow.log_artifact()` for plots and reports

## Common Patterns

### LangChain + MLflow
```python
import mlflow
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

chain = ChatPromptTemplate.from_template("Answer: {question}") | ChatOpenAI()

with mlflow.start_run():
    mlflow.langchain.log_model(chain, "chain")
```

### Feature Engineering with Feature Store
```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

training_set = fe.create_training_set(
    df=labels_df,
    feature_lookups=[
        FeatureLookup(table_name="my_catalog.my_schema.features", lookup_key="id")
    ],
    label="target"
)
```

## Debugging Tips
- Check MLflow UI artifacts tab for logged code
- Use `mlflow.pyfunc.load_model()` locally to test before deployment
- Enable MLflow autologging: `mlflow.autolog()`
- For Databricks: check driver logs in cluster UI

## Key Links
- MLflow Models from Code: https://mlflow.org/docs/latest/ml/model/models-from-code/
- Databricks Apps: https://docs.databricks.com/en/dev-tools/databricks-apps/
- Unity Catalog Models: https://docs.databricks.com/en/mlflow/models-in-uc.html
