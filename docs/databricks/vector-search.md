# Databricks Vector Search Guide

## Overview
Databricks Vector Search enables similarity search over embeddings for RAG applications, semantic search, and recommendation systems. It integrates with Unity Catalog and supports automatic sync from Delta tables.

## Build & Test Commands
- Install: `pip install databricks-vectorsearch`
- Create endpoint: `databricks vector-search endpoints create`
- Create index: `databricks vector-search indexes create`
- Query index: Via Python SDK

## Vector Search Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vector Search Endpoint                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Index 1   │  │   Index 2   │  │      Index N        │  │
│  │  (Docs)     │  │ (Products)  │  │   (Embeddings)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Unity Catalog                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │    Delta Table (Source)                              │    │
│  │    - id (primary key)                               │    │
│  │    - text_content                                   │    │
│  │    - embedding_vector (auto-computed or provided)   │    │
│  │    - metadata_columns                               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Setting Up Vector Search

### Create Endpoint
```python
from databricks.vector_search.client import VectorSearchClient

vs_client = VectorSearchClient()

# Create a vector search endpoint
endpoint = vs_client.create_endpoint(
    name="my-vector-endpoint",
    endpoint_type="STANDARD"  # or "STORAGE_OPTIMIZED" for large indexes
)
```

### Index Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Delta Sync** | Auto-syncs with Delta table | Production RAG, real-time updates |
| **Direct Vector Access** | Manual embedding management | Custom embeddings, batch updates |

## Delta Sync Index (Recommended)

### With Auto-Computed Embeddings
```python
# Source table must exist in Unity Catalog
# CREATE TABLE catalog.schema.documents (
#     id STRING PRIMARY KEY,
#     content STRING,
#     metadata STRING
# )

index = vs_client.create_delta_sync_index(
    endpoint_name="my-vector-endpoint",
    index_name="catalog.schema.doc_index",
    source_table_name="catalog.schema.documents",
    primary_key="id",
    embedding_source_column="content",  # Text to embed
    embedding_model_endpoint_name="databricks-bge-large-en",  # Auto-embed
    pipeline_type="TRIGGERED"  # or "CONTINUOUS"
)
```

### With Pre-Computed Embeddings
```python
# Source table has embedding column
# CREATE TABLE catalog.schema.documents (
#     id STRING PRIMARY KEY,
#     content STRING,
#     embedding ARRAY<FLOAT>  -- Pre-computed embeddings
# )

index = vs_client.create_delta_sync_index(
    endpoint_name="my-vector-endpoint",
    index_name="catalog.schema.doc_index",
    source_table_name="catalog.schema.documents",
    primary_key="id",
    embedding_vector_column="embedding",  # Pre-computed
    embedding_dimension=1024,
    pipeline_type="TRIGGERED"
)
```

## Direct Vector Access Index

```python
# Create index for manual management
index = vs_client.create_direct_access_index(
    endpoint_name="my-vector-endpoint",
    index_name="catalog.schema.manual_index",
    primary_key="id",
    embedding_dimension=1536,
    embedding_vector_column="embedding",
    schema={
        "id": "string",
        "content": "string",
        "embedding": "array<float>",
        "category": "string"
    }
)

# Manually upsert vectors
index.upsert([
    {
        "id": "doc1",
        "content": "Machine learning is...",
        "embedding": [0.1, 0.2, ...],  # 1536 dimensions
        "category": "ML"
    },
    {
        "id": "doc2",
        "content": "Deep learning uses...",
        "embedding": [0.3, 0.4, ...],
        "category": "DL"
    }
])
```

## Querying Vector Search

### Basic Similarity Search
```python
# Get index reference
index = vs_client.get_index(
    endpoint_name="my-vector-endpoint",
    index_name="catalog.schema.doc_index"
)

# Search by text (auto-embedded)
results = index.similarity_search(
    query_text="How do I train a neural network?",
    columns=["id", "content", "metadata"],
    num_results=5
)

# Results structure
for doc in results["result"]["data_array"]:
    print(f"ID: {doc[0]}, Score: {doc[-1]}")  # Last column is similarity score
    print(f"Content: {doc[1]}")
```

### Search by Vector
```python
# If you have your own embedding
query_embedding = embed_model.encode("search query")

results = index.similarity_search(
    query_vector=query_embedding.tolist(),
    columns=["id", "content"],
    num_results=10
)
```

### Filtered Search
```python
# Search with metadata filters
results = index.similarity_search(
    query_text="machine learning",
    columns=["id", "content", "category"],
    filters={"category": "ML"},  # Filter by category
    num_results=5
)

# Complex filters
results = index.similarity_search(
    query_text="neural networks",
    columns=["id", "content", "date", "author"],
    filters={
        "category IN": ["ML", "DL"],
        "date >=": "2024-01-01",
        "author": "John Doe"
    },
    num_results=10
)
```

### Hybrid Search (Vector + Keyword)
```python
# Combine semantic and keyword search
results = index.similarity_search(
    query_text="transformer architecture attention",
    columns=["id", "content", "title"],
    num_results=10,
    query_type="HYBRID"  # Uses both vector similarity and BM25
)
```

## Computing Embeddings

### Using Foundation Model API
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_embeddings(texts: list[str]) -> list[list[float]]:
    response = w.serving_endpoints.query(
        name="databricks-bge-large-en",
        input=texts
    )
    return [item.embedding for item in response.data]

# Embed documents
texts = ["Document 1 content", "Document 2 content"]
embeddings = get_embeddings(texts)
```

### Using sentence-transformers
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
```

## RAG Pipeline Integration

### Complete RAG Example
```python
from databricks.vector_search.client import VectorSearchClient
from databricks.sdk import WorkspaceClient

class RAGPipeline:
    def __init__(self, index_name: str, endpoint_name: str):
        self.vs_client = VectorSearchClient()
        self.index = self.vs_client.get_index(
            endpoint_name=endpoint_name,
            index_name=index_name
        )
        self.w = WorkspaceClient()
    
    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve relevant documents."""
        results = self.index.similarity_search(
            query_text=query,
            columns=["id", "content", "source", "title"],
            num_results=top_k
        )
        
        documents = []
        for row in results["result"]["data_array"]:
            documents.append({
                "id": row[0],
                "content": row[1],
                "source": row[2],
                "title": row[3],
                "score": row[-1]
            })
        return documents
    
    def generate(self, query: str, context: list[dict]) -> str:
        """Generate response using retrieved context."""
        context_text = "\n\n".join([
            f"[{doc['title']}]\n{doc['content']}" 
            for doc in context
        ])
        
        prompt = f"""Answer the question based on the provided context.

Context:
{context_text}

Question: {query}

Answer:"""
        
        response = self.w.serving_endpoints.query(
            name="databricks-meta-llama-3-1-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        
        return response.choices[0].message.content
    
    def query(self, question: str) -> dict:
        """Full RAG pipeline."""
        # Retrieve
        documents = self.retrieve(question)
        
        # Generate
        answer = self.generate(question, documents)
        
        return {
            "question": question,
            "answer": answer,
            "sources": [doc["source"] for doc in documents]
        }

# Usage
rag = RAGPipeline(
    index_name="catalog.schema.knowledge_base_index",
    endpoint_name="my-vector-endpoint"
)

result = rag.query("What is Delta Lake?")
print(result["answer"])
```

## Document Ingestion Pipeline

### Chunking and Embedding
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

def process_documents(documents: list[dict]) -> pd.DataFrame:
    """Chunk documents and prepare for indexing."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for doc in documents:
        doc_chunks = splitter.split_text(doc["content"])
        for i, chunk in enumerate(doc_chunks):
            chunks.append({
                "id": f"{doc['id']}_chunk_{i}",
                "content": chunk,
                "source": doc["source"],
                "title": doc["title"],
                "chunk_index": i
            })
    
    return pd.DataFrame(chunks)

# Write to Delta table (will auto-sync to vector index)
chunks_df = process_documents(raw_documents)
spark.createDataFrame(chunks_df).write.mode("append").saveAsTable(
    "catalog.schema.documents"
)
```

### Scheduled Sync
```python
# Trigger sync manually
index = vs_client.get_index("my-vector-endpoint", "catalog.schema.doc_index")
index.sync()

# For CONTINUOUS pipeline_type, sync happens automatically
```

## Index Management

### List Indexes
```python
indexes = vs_client.list_indexes(endpoint_name="my-vector-endpoint")
for idx in indexes:
    print(f"{idx.name}: {idx.status}")
```

### Delete Index
```python
vs_client.delete_index(
    endpoint_name="my-vector-endpoint",
    index_name="catalog.schema.old_index"
)
```

### Check Sync Status
```python
index = vs_client.get_index("my-vector-endpoint", "catalog.schema.doc_index")
status = index.describe()
print(f"Status: {status['status']}")
print(f"Rows: {status['num_rows']}")
```

## Best Practices

1. **Chunking**: Use 500-1000 token chunks with 10-20% overlap
2. **Embedding Model**: Match embedding model between indexing and query
3. **Primary Keys**: Use stable, unique IDs for documents
4. **Filters**: Add metadata columns for filtering to improve relevance
5. **Sync Mode**: Use TRIGGERED for batch, CONTINUOUS for real-time
6. **Hybrid Search**: Enable for better keyword matching
7. **Monitoring**: Track query latency and result quality

## Performance Tips

- Use `STORAGE_OPTIMIZED` endpoint for indexes > 1M vectors
- Add appropriate filters to reduce search space
- Cache frequent queries at application level
- Batch upserts for direct access indexes
- Monitor index sync lag for Delta Sync indexes

## Key Links
- Vector Search: https://docs.databricks.com/en/generative-ai/vector-search.html
- Python SDK: https://docs.databricks.com/en/generative-ai/create-query-vector-search.html
- Embedding Models: https://docs.databricks.com/en/generative-ai/tutorials/ai-cookbook/fundamentals-embedding-models.html
