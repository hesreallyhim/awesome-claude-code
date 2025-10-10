# CLAUDE.md - Basic Memory Project Guide

## Project Overview

Basic Memory is a local-first knowledge management system built on the Model Context Protocol (MCP). It enables
bidirectional communication between LLMs (like Claude) and markdown files, creating a personal knowledge graph that can
be traversed using links between documents.

## CODEBASE DEVELOPMENT

### Project information

See the [README.md](README.md) file for a project overview.

### Build and Test Commands

- Install: `make install` or `pip install -e ".[dev]"`
- Run tests: `uv run pytest -p pytest_mock -v` or `make test`
- Single test: `pytest tests/path/to/test_file.py::test_function_name`
- Lint: `make lint` or `ruff check . --fix`
- Type check: `make type-check` or `uv run pyright`
- Format: `make format` or `uv run ruff format .`
- Run all code checks: `make check` (runs lint, format, type-check, test)
- Create db migration: `make migration m="Your migration message"`
- Run development MCP Inspector: `make run-inspector`

**Note:** Project supports Python 3.10+

### Code Style Guidelines

- Line length: 100 characters max
- Python 3.12+ with full type annotations
- Format with ruff (consistent styling)
- Import order: standard lib, third-party, local imports
- Naming: snake_case for functions/variables, PascalCase for classes
- Prefer async patterns with SQLAlchemy 2.0
- Use Pydantic v2 for data validation and schemas
- CLI uses Typer for command structure
- API uses FastAPI for endpoints
- Follow the repository pattern for data access
- Tools communicate to api routers via the httpx ASGI client (in process)

### Codebase Architecture

- `/alembic` - Alembic db migrations
- `/api` - FastAPI implementation of REST endpoints
- `/cli` - Typer command-line interface
- `/markdown` - Markdown parsing and processing
- `/mcp` - Model Context Protocol server implementation
- `/models` - SQLAlchemy ORM models
- `/repository` - Data access layer
- `/schemas` - Pydantic models for validation
- `/services` - Business logic layer
- `/sync` - File synchronization services

### Development Notes

- MCP tools are defined in src/basic_memory/mcp/tools/
- MCP prompts are defined in src/basic_memory/mcp/prompts/
- MCP tools should be atomic, composable operations
- Use `textwrap.dedent()` for multi-line string formatting in prompts and tools
- MCP Prompts are used to invoke tools and format content with instructions for an LLM
- Schema changes require Alembic migrations
- SQLite is used for indexing and full text search, files are source of truth
- Testing uses pytest with asyncio support (strict mode)
- Test database uses in-memory SQLite
- Avoid creating mocks in tests in most circumstances.
- Each test runs in a standalone environment with in memory SQLite and tmp_file directory

### Async Client Pattern (Important!)

**All MCP tools and CLI commands use the context manager pattern for HTTP clients:**

```python
from basic_memory.mcp.async_client import get_client

async def my_mcp_tool():
    async with get_client() as client:
        # Use client for API calls
        response = await call_get(client, "/path")
        return response
```

**Do NOT use:**
- ❌ `from basic_memory.mcp.async_client import client` (deprecated module-level client)
- ❌ Manual auth header management
- ❌ `inject_auth_header()` (deleted)

**Key principles:**
- Auth happens at client creation, not per-request
- Proper resource management via context managers
- Supports three modes: Local (ASGI), CLI cloud (HTTP + auth), Cloud app (factory injection)
- Factory pattern enables dependency injection for cloud consolidation

**For cloud app integration:**
```python
from basic_memory.mcp import async_client

# Set custom factory before importing tools
async_client.set_client_factory(your_custom_factory)
```

See SPEC-16 for full context manager refactor details.

## BASIC MEMORY PRODUCT USAGE

### Knowledge Structure

- Entity: Any concept, document, or idea represented as a markdown file
- Observation: A categorized fact about an entity (`- [category] content`)
- Relation: A directional link between entities (`- relation_type [[Target]]`)
- Frontmatter: YAML metadata at the top of markdown files
- Knowledge representation follows precise markdown format:
    - Observations with [category] prefixes
    - Relations with WikiLinks [[Entity]]
    - Frontmatter with metadata

### Basic Memory Commands

**Local Commands:**
- Sync knowledge: `basic-memory sync` or `basic-memory sync --watch`
- Import from Claude: `basic-memory import claude conversations`
- Import from ChatGPT: `basic-memory import chatgpt`
- Import from Memory JSON: `basic-memory import memory-json`
- Check sync status: `basic-memory status`
- Tool access: `basic-memory tools` (provides CLI access to MCP tools)
    - Guide: `basic-memory tools basic-memory-guide`
    - Continue: `basic-memory tools continue-conversation --topic="search"`

**Cloud Commands (requires subscription):**
- Authenticate: `basic-memory cloud login`
- Logout: `basic-memory cloud logout`
- Bidirectional sync: `basic-memory cloud sync`
- Integrity check: `basic-memory cloud check`
- Mount cloud storage: `basic-memory cloud mount`
- Unmount cloud storage: `basic-memory cloud unmount`

### MCP Capabilities

- Basic Memory exposes these MCP tools to LLMs:

  **Content Management:**
    - `write_note(title, content, folder, tags)` - Create/update markdown notes with semantic observations and relations
    - `read_note(identifier, page, page_size)` - Read notes by title, permalink, or memory:// URL with knowledge graph awareness
    - `read_content(path)` - Read raw file content (text, images, binaries) without knowledge graph processing
    - `view_note(identifier, page, page_size)` - View notes as formatted artifacts for better readability
    - `edit_note(identifier, operation, content)` - Edit notes incrementally (append, prepend, find/replace, replace_section)
    - `move_note(identifier, destination_path)` - Move notes to new locations, updating database and maintaining links
    - `delete_note(identifier)` - Delete notes from the knowledge base

  **Knowledge Graph Navigation:**
    - `build_context(url, depth, timeframe)` - Navigate the knowledge graph via memory:// URLs for conversation continuity
    - `recent_activity(type, depth, timeframe)` - Get recently updated information with specified timeframe (e.g., "1d", "1 week")
    - `list_directory(dir_name, depth, file_name_glob)` - Browse directory contents with filtering and depth control

  **Search & Discovery:**
    - `search_notes(query, page, page_size, search_type, types, entity_types, after_date)` - Full-text search across all content with advanced filtering options

  **Project Management:**
    - `list_memory_projects()` - List all available projects with their status
    - `create_memory_project(project_name, project_path, set_default)` - Create new Basic Memory projects
    - `delete_project(project_name)` - Delete a project from configuration
    - `get_current_project()` - Get current project information and stats
    - `sync_status()` - Check file synchronization and background operation status

  **Visualization:**
    - `canvas(nodes, edges, title, folder)` - Generate Obsidian canvas files for knowledge graph visualization

- MCP Prompts for better AI interaction:
    - `ai_assistant_guide()` - Guidance on effectively using Basic Memory tools for AI assistants
    - `continue_conversation(topic, timeframe)` - Continue previous conversations with relevant historical context
    - `search(query, after_date)` - Search with detailed, formatted results for better context understanding
    - `recent_activity(timeframe)` - View recently changed items with formatted output
    - `json_canvas_spec()` - Full JSON Canvas specification for Obsidian visualization

### Cloud Features (v0.15.0+)

Basic Memory now supports cloud synchronization and storage (requires active subscription):

**Authentication:**
- JWT-based authentication with subscription validation
- Secure session management with token refresh
- Support for multiple cloud projects

**Bidirectional Sync:**
- rclone bisync integration for two-way synchronization
- Conflict resolution and integrity verification
- Real-time sync with change detection
- Mount/unmount cloud storage for direct file access

**Cloud Project Management:**
- Create and manage projects in the cloud
- Toggle between local and cloud modes
- Per-project sync configuration
- Subscription-based access control

**Security & Performance:**
- Removed .env file loading for improved security
- .gitignore integration (respects gitignored files)
- WAL mode for SQLite performance
- Background relation resolution (non-blocking startup)
- API performance optimizations (SPEC-11)

## AI-Human Collaborative Development

Basic Memory emerged from and enables a new kind of development process that combines human and AI capabilities. Instead
of using AI just for code generation, we've developed a true collaborative workflow:

1. AI (LLM) writes initial implementation based on specifications and context
2. Human reviews, runs tests, and commits code with any necessary adjustments
3. Knowledge persists across conversations using Basic Memory's knowledge graph
4. Development continues seamlessly across different AI sessions with consistent context
5. Results improve through iterative collaboration and shared understanding

This approach has allowed us to tackle more complex challenges and build a more robust system than either humans or AI
could achieve independently.

## GitHub Integration

Basic Memory has taken AI-Human collaboration to the next level by integrating Claude directly into the development workflow through GitHub:

### GitHub MCP Tools

Using the GitHub Model Context Protocol server, Claude can now:

- **Repository Management**:
  - View repository files and structure
  - Read file contents
  - Create new branches
  - Create and update files

- **Issue Management**:
  - Create new issues
  - Comment on existing issues
  - Close and update issues
  - Search across issues

- **Pull Request Workflow**:
  - Create pull requests
  - Review code changes
  - Add comments to PRs

This integration enables Claude to participate as a full team member in the development process, not just as a code generation tool. Claude's GitHub account ([bm-claudeai](https://github.com/bm-claudeai)) is a member of the Basic Machines organization with direct contributor access to the codebase.

### Collaborative Development Process

With GitHub integration, the development workflow includes:

1. **Direct code review** - Claude can analyze PRs and provide detailed feedback
2. **Contribution tracking** - All of Claude's contributions are properly attributed in the Git history
3. **Branch management** - Claude can create feature branches for implementations
4. **Documentation maintenance** - Claude can keep documentation updated as the code evolves

This level of integration represents a new paradigm in AI-human collaboration, where the AI assistant becomes a full-fledged team member rather than just a tool for generating code snippets.
