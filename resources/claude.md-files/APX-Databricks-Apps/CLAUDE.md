# APX - Databricks Apps Development Guide

## Overview
APX is the official toolkit for building Databricks Apps, providing an integrated development experience with FastAPI backend, React frontend, and seamless Databricks integration. It bundles all necessary tools including the Bun JavaScript runtime.

## Build & Test Commands
- Initialize project: `uvx --index https://databricks-solutions.github.io/apx/simple apx init`
- Start development: `apx run`
- Run backend only: `apx run --backend`
- Run frontend only: `apx run --frontend`
- Deploy to Databricks: `apx deploy`
- Upgrade APX: `uv sync --upgrade-package apx --index https://databricks-solutions.github.io/apx/simple`

## Project Structure

```
my-databricks-app/
├── app.yaml                 # App configuration
├── pyproject.toml           # Python dependencies
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI entry point
│   │   ├── routes/          # API route handlers
│   │   │   └── api.py
│   │   └── services/        # Business logic
│   │       └── databricks.py
│   └── frontend/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       └── src/
│           ├── App.tsx
│           ├── main.tsx
│           └── components/
├── tests/
│   └── test_api.py
└── .gitignore
```

## Technology Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **Pydantic**: Data validation and settings management
- **Databricks SDK**: Native Databricks integration
- **SQLModel**: ORM for database operations

### Frontend
- **React + TypeScript**: UI framework
- **shadcn/ui**: Accessible component library
- **Tailwind CSS**: Utility-first CSS
- **Vite**: Fast build tooling
- **Bun**: Bundled JS runtime (no Node.js needed)

## FastAPI Backend Pattern

### main.py
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from databricks.sdk import WorkspaceClient

app = FastAPI()

# Initialize Databricks client
w = WorkspaceClient()

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/current-user")
async def get_current_user():
    user = w.current_user.me()
    return {"user": user.user_name, "display_name": user.display_name}

# Mount static files for production
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### API Routes Pattern
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from databricks.sdk import WorkspaceClient

router = APIRouter(prefix="/api")
w = WorkspaceClient()

class QueryRequest(BaseModel):
    sql: str
    warehouse_id: str

class QueryResponse(BaseModel):
    columns: list[str]
    data: list[list]

@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    try:
        result = w.statement_execution.execute_statement(
            warehouse_id=request.warehouse_id,
            statement=request.sql,
            wait_timeout="30s"
        )
        return QueryResponse(
            columns=[col.name for col in result.manifest.schema.columns],
            data=result.result.data_array
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## React Frontend Pattern

### App.tsx
```typescript
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface User {
  user: string;
  display_name: string;
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/current-user')
      .then(res => res.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Welcome, {user?.display_name}</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Logged in as: {user?.user}</p>
        </CardContent>
      </Card>
    </div>
  );
}
```

### API Client Pattern
```typescript
// src/frontend/src/lib/api.ts
const API_BASE = '/api';

export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

// Usage
export const api = {
  getCurrentUser: () => fetchApi<User>('/current-user'),
  executeQuery: (sql: string, warehouse_id: string) => 
    fetchApi<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify({ sql, warehouse_id }),
    }),
};
```

## app.yaml Configuration

```yaml
name: my-databricks-app
description: "My Databricks Application"

# Resources configuration
resources:
  # SQL Warehouse for queries
  sql_warehouse:
    name: "Shared Endpoint"
  
  # Unity Catalog permissions
  grants:
    - principal: "users"
      privileges:
        - "USE_CATALOG"
        - "USE_SCHEMA"

# Environment variables
env:
  LOG_LEVEL: "INFO"
  
# Serving configuration
serve:
  port: 8000
  workers: 4
```

## Development Workflow

### 1. Initialize New Project
```bash
# Create new APX project
uvx --index https://databricks-solutions.github.io/apx/simple apx init my-app

cd my-app
```

### 2. Local Development
```bash
# Start both backend and frontend with hot reload
apx run

# Backend runs on http://localhost:8000
# Frontend runs on http://localhost:5173 with proxy to backend
```

### 3. Add shadcn/ui Components
```bash
# APX uses Bun, so use bunx instead of npx
bunx shadcn-ui@latest add button
bunx shadcn-ui@latest add card
bunx shadcn-ui@latest add table
```

### 4. Deploy to Databricks
```bash
# Deploy the app
apx deploy

# Deploy to specific workspace
apx deploy --workspace https://your-workspace.cloud.databricks.com
```

## Databricks SDK Integration

### Querying Data
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Execute SQL query
result = w.statement_execution.execute_statement(
    warehouse_id="abc123",
    statement="SELECT * FROM catalog.schema.table LIMIT 100"
)

# Get results
for row in result.result.data_array:
    print(row)
```

### Working with MLflow Models
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Query model serving endpoint
response = w.serving_endpoints.query(
    name="my-model-endpoint",
    dataframe_records=[{"feature1": 1.0, "feature2": 2.0}]
)
```

### Unity Catalog Access
```python
# List catalogs
catalogs = w.catalogs.list()

# Get table info
table = w.tables.get("catalog.schema.table")

# Read table as DataFrame (requires cluster)
df = spark.table("catalog.schema.table")
```

## Testing

### Backend Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query():
    response = client.post("/api/query", json={
        "sql": "SELECT 1 as test",
        "warehouse_id": "test-warehouse"
    })
    assert response.status_code == 200
```

### Frontend Tests
```typescript
// src/frontend/src/__tests__/App.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

test('renders welcome message', async () => {
  render(<App />);
  await waitFor(() => {
    expect(screen.getByText(/Welcome/)).toBeInTheDocument();
  });
});
```

## Code Style Guidelines

### Python (Backend)
- Use type hints for all function parameters and returns
- Follow PEP 8 naming conventions
- Use async/await for I/O operations
- Validate all inputs with Pydantic models

### TypeScript (Frontend)
- Use functional components with hooks
- Define interfaces for all API responses
- Use absolute imports with `@/` prefix
- Follow shadcn/ui patterns for components

## Best Practices

1. **Authentication**: APX apps inherit Databricks workspace authentication
2. **Error Handling**: Return proper HTTP status codes and error messages
3. **Environment Variables**: Use `app.yaml` for configuration
4. **Secrets**: Use Databricks secret scopes, never hardcode credentials
5. **Testing**: Write tests for both backend and frontend
6. **Logging**: Use Python logging module, configure via `LOG_LEVEL`

## Key Links
- APX Documentation: https://databricks-solutions.github.io/apx/
- APX GitHub: https://github.com/databricks-solutions/apx
- Databricks Apps: https://docs.databricks.com/en/dev-tools/databricks-apps/
- shadcn/ui: https://ui.shadcn.com/
