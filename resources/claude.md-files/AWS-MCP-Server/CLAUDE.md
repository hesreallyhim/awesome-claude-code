# AWS MCP Server Development Guide

## Build & Test Commands

### Using uv (recommended)
- Install dependencies: `uv pip install --system -e .`
- Install dev dependencies: `uv pip install --system -e ".[dev]"`
- Update lock file: `uv pip compile --system pyproject.toml -o uv.lock`
- Install from lock file: `uv pip sync --system uv.lock`

### Using pip (alternative)
- Install dependencies: `pip install -e .`
- Install dev dependencies: `pip install -e ".[dev]"`

### Running the server
- Run server: `python -m aws_mcp_server`
- Run server with SSE transport: `AWS_MCP_TRANSPORT=sse python -m aws_mcp_server`
- Run with MCP CLI: `mcp run src/aws_mcp_server/server.py`

### Testing and linting
- Run tests: `pytest`
- Run single test: `pytest tests/path/to/test_file.py::test_function_name -v`
- Run tests with coverage: `python -m pytest --cov=src/aws_mcp_server tests/`
- Run linter: `ruff check src/ tests/`
- Format code: `ruff format src/ tests/`

## Technical Stack

- **Python version**: Python 3.13+
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `uv` for faster, more reliable dependency management with lock file
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Version management**: Use `setuptools_scm` for automatic versioning from Git tags
- **Linting**: `ruff` for style and error checking
- **Type checking**: Use VS Code with Pylance for static type checking
- **Project layout**: Organize code with `src/` layout

## Code Style Guidelines

- **Formatting**: Black-compatible formatting via `ruff format`
- **Imports**: Sort imports with `ruff` (stdlib, third-party, local)
- **Type hints**: Use native Python type hints (e.g., `list[str]` not `List[str]`)
- **Documentation**: Google-style docstrings for all modules, classes, functions
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Function length**: Keep functions short (< 30 lines) and single-purpose
- **PEP 8**: Follow PEP 8 style guide (enforced via `ruff`)

## Python Best Practices

- **File handling**: Prefer `pathlib.Path` over `os.path`
- **Debugging**: Use `logging` module instead of `print`
- **Error handling**: Use specific exceptions with context messages and proper logging
- **Data structures**: Use list/dict comprehensions for concise, readable code
- **Function arguments**: Avoid mutable default arguments
- **Data containers**: Leverage `dataclasses` to reduce boilerplate
- **Configuration**: Use environment variables (via `python-dotenv`) for configuration
- **AWS CLI**: Validate all commands before execution (must start with "aws")
- **Security**: Never store/log AWS credentials, set command timeouts

## Development Patterns & Best Practices

- **Favor simplicity**: Choose the simplest solution that meets requirements
- **DRY principle**: Avoid code duplication; reuse existing functionality
- **Configuration management**: Use environment variables for different environments
- **Focused changes**: Only implement explicitly requested or fully understood changes
- **Preserve patterns**: Follow existing code patterns when fixing bugs
- **File size**: Keep files under 300 lines; refactor when exceeding this limit
- **Test coverage**: Write comprehensive unit and integration tests with `pytest`; include fixtures
- **Test structure**: Use table-driven tests with parameterization for similar test cases
- **Mocking**: Use unittest.mock for external dependencies; don't test implementation details
- **Modular design**: Create reusable, modular components
- **Logging**: Implement appropriate logging levels (debug, info, error)
- **Error handling**: Implement robust error handling for production reliability
- **Security best practices**: Follow input validation and data protection practices
- **Performance**: Optimize critical code sections when necessary
- **Dependency management**: Add libraries only when essential
  - When adding/updating dependencies, update `pyproject.toml` first
  - Regenerate the lock file with `uv pip compile --system pyproject.toml -o uv.lock`
  - Install the new dependencies with `uv pip sync --system uv.lock`

## Development Workflow

- **Version control**: Commit frequently with clear messages
- **Versioning**: Use Git tags for versioning (e.g., `git tag -a 1.2.3 -m "Release 1.2.3"`)
  - For releases, create and push a tag
  - For development, let `setuptools_scm` automatically determine versions
- **Impact assessment**: Evaluate how changes affect other codebase areas
- **Documentation**: Keep documentation up-to-date for complex logic and features
- **Dependencies**: When adding dependencies, always update the `uv.lock` file
- **CI/CD**: All changes should pass CI checks (tests, linting, etc.) before merging
