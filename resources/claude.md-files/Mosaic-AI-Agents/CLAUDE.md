# Mosaic AI Agent Framework Guide

## Overview
Mosaic AI Agent Framework enables building, deploying, and monitoring production-grade AI agents on Databricks. It provides tools for creating compound AI systems with tool calling, retrieval, and multi-step reasoning capabilities.

## Build & Test Commands
- Install: `pip install databricks-agents mlflow`
- Run agent locally: `python agent.py`
- Deploy agent: `databricks agents deploy`
- Evaluate agent: `mlflow.evaluate()`

## Agent Framework Architecture

```
┌─────────────────────────────────────────────┐
│              Mosaic AI Agent                │
├─────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │   LLM   │  │  Tools  │  │  Retriever  │ │
│  └─────────┘  └─────────┘  └─────────────┘ │
├─────────────────────────────────────────────┤
│         MLflow Tracking & Serving           │
├─────────────────────────────────────────────┤
│         Unity Catalog Governance            │
└─────────────────────────────────────────────┘
```

## Creating an Agent with ChatAgent

### Basic Agent Pattern
```python
from databricks.agents import ChatAgent, ChatAgentMessage, ChatAgentResponse
from databricks.sdk import WorkspaceClient
import mlflow

class MyAgent(ChatAgent):
    def __init__(self):
        self.client = WorkspaceClient()
        # Initialize any resources
    
    def chat(self, messages: list[ChatAgentMessage]) -> ChatAgentResponse:
        # Get the latest user message
        user_message = messages[-1].content
        
        # Call foundation model
        response = self.client.serving_endpoints.query(
            name="databricks-meta-llama-3-1-70b-instruct",
            messages=[{"role": "user", "content": user_message}]
        )
        
        return ChatAgentResponse(
            content=response.choices[0].message.content
        )

# Set the agent for MLflow logging
mlflow.models.set_model(MyAgent())
```

### Agent with Tools
```python
from databricks.agents import ChatAgent, ChatAgentMessage, ChatAgentResponse
from databricks.agents.tools import tool
import json

class ToolAgent(ChatAgent):
    def __init__(self):
        self.tools = [self.search_catalog, self.execute_query]
    
    @tool
    def search_catalog(self, query: str) -> str:
        """Search Unity Catalog for tables matching the query.
        
        Args:
            query: Search term for finding tables
        """
        # Implementation
        return json.dumps({"tables": ["catalog.schema.table1"]})
    
    @tool
    def execute_query(self, sql: str) -> str:
        """Execute a SQL query and return results.
        
        Args:
            sql: The SQL query to execute
        """
        # Implementation
        return json.dumps({"rows": 100, "preview": [...]})
    
    def chat(self, messages: list[ChatAgentMessage]) -> ChatAgentResponse:
        # LLM decides which tools to call
        # Process tool calls and return response
        pass
```

## Using Foundation Model APIs

### Direct Model Calling
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Chat completion
response = w.serving_endpoints.query(
    name="databricks-meta-llama-3-1-70b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain MLflow in one sentence."}
    ],
    max_tokens=256,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### With Tool Calling
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

response = w.serving_endpoints.query(
    name="databricks-meta-llama-3-1-70b-instruct",
    messages=[{"role": "user", "content": "What's the weather in Seattle?"}],
    tools=tools,
    tool_choice="auto"
)

# Check if model wants to call a tool
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Call function: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")
```

## RAG Agent Pattern

### With Vector Search Retrieval
```python
from databricks.agents import ChatAgent, ChatAgentMessage, ChatAgentResponse
from databricks.vector_search.client import VectorSearchClient

class RAGAgent(ChatAgent):
    def __init__(self):
        self.vs_client = VectorSearchClient()
        self.index = self.vs_client.get_index(
            endpoint_name="vector-search-endpoint",
            index_name="catalog.schema.doc_index"
        )
        self.w = WorkspaceClient()
    
    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """Retrieve relevant documents."""
        results = self.index.similarity_search(
            query_text=query,
            columns=["content", "source"],
            num_results=top_k
        )
        return [row["content"] for row in results["result"]["data_array"]]
    
    def chat(self, messages: list[ChatAgentMessage]) -> ChatAgentResponse:
        user_query = messages[-1].content
        
        # Retrieve relevant context
        context_docs = self.retrieve(user_query)
        context = "\n\n".join(context_docs)
        
        # Augmented prompt
        augmented_prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {user_query}

Answer:"""
        
        # Generate response
        response = self.w.serving_endpoints.query(
            name="databricks-meta-llama-3-1-70b-instruct",
            messages=[{"role": "user", "content": augmented_prompt}]
        )
        
        return ChatAgentResponse(
            content=response.choices[0].message.content
        )
```

## Logging and Deploying Agents

### Log Agent with MLflow
```python
import mlflow

mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment("/Users/you@company.com/my-agent")

with mlflow.start_run():
    # Log agent using models from code
    mlflow.pyfunc.log_model(
        artifact_path="agent",
        python_model="agent.py",  # Your agent code file
        registered_model_name="catalog.schema.my_agent",
        pip_requirements=[
            "databricks-agents",
            "databricks-vectorsearch",
            "mlflow"
        ]
    )
```

### Deploy Agent to Serving Endpoint
```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput

w = WorkspaceClient()

w.serving_endpoints.create(
    name="my-agent-endpoint",
    config=EndpointCoreConfigInput(
        served_entities=[
            ServedEntityInput(
                entity_name="catalog.schema.my_agent",
                entity_version="1",
                workload_size="Small",
                scale_to_zero_enabled=True
            )
        ]
    )
)
```

## Agent Evaluation

### Using MLflow Evaluate
```python
import mlflow
import pandas as pd

# Evaluation dataset
eval_data = pd.DataFrame({
    "inputs": [
        "What is MLflow?",
        "How do I deploy a model?",
        "Explain Unity Catalog"
    ],
    "ground_truth": [
        "MLflow is an open source platform for ML lifecycle management.",
        "Use mlflow.sklearn.log_model() then deploy to a serving endpoint.",
        "Unity Catalog is Databricks' unified governance solution."
    ]
})

# Load agent
agent = mlflow.pyfunc.load_model("models:/catalog.schema.my_agent@champion")

# Evaluate
results = mlflow.evaluate(
    model=agent,
    data=eval_data,
    targets="ground_truth",
    model_type="question-answering",
    evaluators=["default"],
    extra_metrics=[
        mlflow.metrics.latency(),
        mlflow.metrics.token_count(),
        mlflow.metrics.genai.relevance(),
        mlflow.metrics.genai.faithfulness()
    ]
)

print(results.metrics)
```

### Custom Evaluation Metrics
```python
from mlflow.metrics import make_metric

@make_metric
def response_length(predictions, targets):
    """Custom metric for response length."""
    lengths = [len(p) for p in predictions]
    return sum(lengths) / len(lengths)

results = mlflow.evaluate(
    model=agent,
    data=eval_data,
    extra_metrics=[response_length]
)
```

## Agent Monitoring

### Inference Tables
```python
# Enable inference logging (in endpoint config)
config = EndpointCoreConfigInput(
    served_entities=[...],
    auto_capture_config={
        "catalog_name": "catalog",
        "schema_name": "schema",
        "table_name_prefix": "agent_logs"
    }
)
```

### Query Agent Logs
```sql
SELECT 
    request_time,
    request,
    response,
    latency_ms,
    token_count
FROM catalog.schema.agent_logs_payload
WHERE request_time > current_date() - INTERVAL 1 DAY
ORDER BY request_time DESC
```

## Multi-Agent Patterns

### Supervisor Agent
```python
class SupervisorAgent(ChatAgent):
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.review_agent = ReviewAgent()
    
    def chat(self, messages: list[ChatAgentMessage]) -> ChatAgentResponse:
        user_request = messages[-1].content
        
        # Step 1: Research
        research = self.research_agent.chat([
            ChatAgentMessage(role="user", content=f"Research: {user_request}")
        ])
        
        # Step 2: Write draft
        draft = self.writing_agent.chat([
            ChatAgentMessage(role="user", content=f"Write based on: {research.content}")
        ])
        
        # Step 3: Review and refine
        final = self.review_agent.chat([
            ChatAgentMessage(role="user", content=f"Review and improve: {draft.content}")
        ])
        
        return final
```

## Best Practices

1. **Use Models from Code**: Log agents as Python code for auditability
2. **Structured Tools**: Define tools with clear docstrings and type hints
3. **Error Handling**: Gracefully handle tool failures and LLM errors
4. **Evaluation**: Always evaluate before deploying to production
5. **Monitoring**: Enable inference tables for observability
6. **Governance**: Register agents in Unity Catalog
7. **Cost Management**: Use scale-to-zero for non-critical endpoints

## Key Links
- Mosaic AI Agents: https://docs.databricks.com/en/generative-ai/agent-framework/
- Foundation Models: https://docs.databricks.com/en/machine-learning/foundation-models/
- Agent Evaluation: https://docs.databricks.com/en/generative-ai/agent-evaluation/
