# DSPy - Programming Language Models Guide

## Overview
DSPy (Declarative Self-improving Python) is a framework for programming—not prompting—language models. Instead of crafting brittle prompts, you write compositional Python code and use DSPy's optimizers to automatically improve prompts and weights.

## Build & Test Commands
- Install: `pip install dspy`
- Run tests: `pytest tests/ -v`
- With MLflow: `pip install dspy mlflow`

## Core Philosophy

**Traditional Approach:**
```python
# Brittle, manual prompt engineering
prompt = """You are a helpful assistant. Given a question, provide a concise answer.
Question: {question}
Answer:"""
```

**DSPy Approach:**
```python
# Declarative, optimizable
class QA(dspy.Signature):
    """Answer the question concisely."""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

qa = dspy.ChainOfThought(QA)
```

## Setup and Configuration

### Basic Setup
```python
import dspy

# Configure the language model
lm = dspy.LM("openai/gpt-4o-mini", api_key="...")
dspy.configure(lm=lm)

# Or use Databricks Foundation Models
lm = dspy.LM(
    "databricks/databricks-meta-llama-3-1-70b-instruct",
    api_base="https://your-workspace.cloud.databricks.com/serving-endpoints",
    api_key="dapi..."
)
dspy.configure(lm=lm)
```

### With Multiple Models
```python
# Different models for different tasks
fast_lm = dspy.LM("openai/gpt-4o-mini")
strong_lm = dspy.LM("openai/gpt-4o")
reasoning_lm = dspy.LM("anthropic/claude-3-5-sonnet-20241022")

# Use in specific modules
with dspy.context(lm=strong_lm):
    result = complex_module(input)
```

## Signatures

Signatures define the semantic interface (inputs → outputs) for your LM calls.

### Inline Signatures
```python
# Simple string format
qa = dspy.Predict("question -> answer")
classify = dspy.Predict("text -> label")
summarize = dspy.Predict("document -> summary")

# With types
qa = dspy.Predict("question: str -> answer: str")
```

### Class-Based Signatures
```python
class QuestionAnswer(dspy.Signature):
    """Answer questions with detailed explanations."""
    
    question: str = dspy.InputField(desc="The question to answer")
    context: str = dspy.InputField(desc="Relevant context", default="")
    answer: str = dspy.OutputField(desc="The detailed answer")
    confidence: float = dspy.OutputField(desc="Confidence score 0-1")

qa = dspy.ChainOfThought(QuestionAnswer)
result = qa(question="What is MLflow?", context="MLflow is an ML platform...")
print(result.answer, result.confidence)
```

### Multiple Outputs
```python
class EntityExtraction(dspy.Signature):
    """Extract entities from text."""
    
    text: str = dspy.InputField()
    people: list[str] = dspy.OutputField(desc="Names of people mentioned")
    organizations: list[str] = dspy.OutputField(desc="Organization names")
    locations: list[str] = dspy.OutputField(desc="Location names")
```

## Modules

DSPy modules are like PyTorch nn.Module but for LM programs.

### dspy.Predict
Basic predictor, no reasoning chain.
```python
predict = dspy.Predict("question -> answer")
result = predict(question="What is 2+2?")
print(result.answer)  # "4"
```

### dspy.ChainOfThought
Adds step-by-step reasoning before the answer.
```python
cot = dspy.ChainOfThought("question -> answer")
result = cot(question="If a train leaves at 3pm going 60mph...")
print(result.reasoning)  # Shows thought process
print(result.answer)     # Final answer
```

### dspy.ProgramOfThought
Generates and executes code to solve problems.
```python
pot = dspy.ProgramOfThought("question -> answer")
result = pot(question="What is the 50th Fibonacci number?")
# Generates Python code, executes it, returns result
```

### dspy.ReAct
Agent with tool use capabilities.
```python
def search(query: str) -> str:
    """Search the web for information."""
    # Implementation
    return results

def calculate(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)

react = dspy.ReAct(
    "question -> answer",
    tools=[search, calculate]
)
result = react(question="What's the population of France times 2?")
```

### dspy.MultiChainComparison
Compare multiple reasoning chains.
```python
multi = dspy.MultiChainComparison("question -> answer", M=5)
# Generates 5 chains, compares them, returns best answer
```

## Building Complex Programs

### Composing Modules
```python
class RAGPipeline(dspy.Module):
    def __init__(self, num_passages=3):
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, question):
        # Retrieve relevant passages
        passages = self.retrieve(question).passages
        context = "\n".join(passages)
        
        # Generate answer with context
        return self.generate(context=context, question=question)

rag = RAGPipeline()
result = rag(question="What are the benefits of MLflow?")
```

### Multi-Hop Reasoning
```python
class MultiHopQA(dspy.Module):
    def __init__(self):
        self.generate_query = dspy.ChainOfThought("question -> search_query")
        self.retrieve = dspy.Retrieve(k=3)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, question):
        # First hop: generate search query
        query = self.generate_query(question=question).search_query
        
        # Retrieve
        passages = self.retrieve(query).passages
        
        # Second hop: may need more info
        context = "\n".join(passages)
        return self.generate_answer(context=context, question=question)
```

## Optimizers

DSPy optimizers automatically improve your prompts and few-shot examples.

### LabeledFewShot
Use labeled examples directly.
```python
from dspy.teleprompt import LabeledFewShot

# Training data
trainset = [
    dspy.Example(question="What is Python?", answer="A programming language").with_inputs("question"),
    dspy.Example(question="What is Java?", answer="A programming language").with_inputs("question"),
    # ... more examples
]

optimizer = LabeledFewShot(k=3)  # Use 3 examples in prompt
optimized_program = optimizer.compile(my_program, trainset=trainset)
```

### BootstrapFewShot
Bootstrap examples by running program and filtering by metric.
```python
from dspy.teleprompt import BootstrapFewShot

def metric(example, prediction, trace=None):
    """Return True if prediction is good."""
    return prediction.answer.lower() == example.answer.lower()

optimizer = BootstrapFewShot(
    metric=metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=4
)

optimized = optimizer.compile(my_program, trainset=trainset)
```

### MIPROv2
State-of-the-art optimizer for prompt and demo selection.
```python
from dspy.teleprompt import MIPROv2

optimizer = MIPROv2(
    metric=metric,
    num_candidates=10,
    init_temperature=1.0
)

optimized = optimizer.compile(
    my_program,
    trainset=trainset,
    valset=valset,  # Validation set
    num_batches=20
)
```

### BootstrapFinetune
Fine-tune the underlying model.
```python
from dspy.teleprompt import BootstrapFinetune

optimizer = BootstrapFinetune(metric=metric)
optimized = optimizer.compile(my_program, trainset=trainset)
```

## Evaluation

### Basic Evaluation
```python
from dspy.evaluate import Evaluate

evaluator = Evaluate(
    devset=testset,
    metric=metric,
    num_threads=4,
    display_progress=True
)

score = evaluator(my_program)
print(f"Accuracy: {score}%")
```

### Custom Metrics
```python
def semantic_similarity_metric(example, prediction, trace=None):
    """Check if answer is semantically similar."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    emb1 = model.encode(example.answer)
    emb2 = model.encode(prediction.answer)
    
    similarity = cosine_similarity([emb1], [emb2])[0][0]
    return similarity > 0.8

def factual_accuracy_metric(example, prediction, trace=None):
    """Use an LM to judge factual accuracy."""
    judge = dspy.ChainOfThought("claim, reference -> is_accurate: bool")
    result = judge(claim=prediction.answer, reference=example.answer)
    return result.is_accurate
```

## Integration with MLflow

### Logging DSPy Programs
```python
import mlflow
import dspy

mlflow.set_experiment("/dspy-experiments")

with mlflow.start_run():
    # Log configuration
    mlflow.log_params({
        "model": "gpt-4o-mini",
        "optimizer": "MIPROv2",
        "num_demos": 4
    })
    
    # Train/optimize
    optimized = optimizer.compile(program, trainset=trainset)
    
    # Evaluate
    score = evaluator(optimized)
    mlflow.log_metric("accuracy", score)
    
    # Save the optimized program
    optimized.save("optimized_program.json")
    mlflow.log_artifact("optimized_program.json")
```

### Loading Saved Programs
```python
# Save
my_program.save("my_program.json")

# Load
loaded_program = MyProgramClass()
loaded_program.load("my_program.json")
```

## Common Patterns

### Retrieval-Augmented Generation
```python
class RAG(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)
```

### Classification with Confidence
```python
class Classifier(dspy.Signature):
    """Classify text into categories."""
    text: str = dspy.InputField()
    category: str = dspy.OutputField(desc="One of: positive, negative, neutral")
    confidence: float = dspy.OutputField(desc="Confidence 0.0 to 1.0")
    reasoning: str = dspy.OutputField(desc="Explanation for classification")

classifier = dspy.ChainOfThought(Classifier)
```

### Multi-Agent System
```python
class ResearchTeam(dspy.Module):
    def __init__(self):
        self.researcher = dspy.ReAct("topic -> findings", tools=[search])
        self.analyst = dspy.ChainOfThought("findings -> analysis")
        self.writer = dspy.ChainOfThought("analysis, topic -> report")
    
    def forward(self, topic):
        findings = self.researcher(topic=topic).findings
        analysis = self.analyst(findings=findings).analysis
        return self.writer(analysis=analysis, topic=topic)
```

## Best Practices

1. **Start Simple**: Begin with dspy.Predict, add ChainOfThought if needed
2. **Clear Signatures**: Write descriptive docstrings and field descriptions
3. **Good Examples**: Quality training data matters more than quantity
4. **Iterative Optimization**: Start with BootstrapFewShot, graduate to MIPROv2
5. **Evaluation First**: Define metrics before optimizing
6. **Version Control**: Save optimized programs as artifacts
7. **Test Systematically**: Use held-out test sets for final evaluation

## Debugging

```python
# Enable verbose mode
dspy.configure(lm=lm, trace=[])

# Inspect last LM call
print(lm.history[-1])

# Inspect module internals
print(my_module.generate.demos)  # See few-shot examples
```

## Key Links
- DSPy Documentation: https://dspy.ai
- GitHub: https://github.com/stanfordnlp/dspy
- Paper: https://arxiv.org/abs/2310.03714
