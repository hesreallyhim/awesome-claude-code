# Clean

Fix all linting, formatting, and type errors in the codebase.

## Behavior

1. **Detect the project's tooling** by checking for config files:

   | Config File | Tools to Run |
   |-------------|-------------|
   | `pyproject.toml`, `setup.cfg`, `.flake8` | ruff, black, isort, mypy, flake8 (whichever are configured) |
   | `package.json`, `.eslintrc*`, `biome.json` | eslint, prettier, biome, tsc (whichever are configured) |
   | `Cargo.toml` | `cargo fmt`, `cargo clippy` |
   | `go.mod` | `go fmt`, `go vet`, `golangci-lint` |
   | `Makefile` / `justfile` | Check for `lint`, `format`, `check` targets |
   | CI config (`.github/workflows/`) | Check what CI runs for hints |

2. **Run formatters first** (auto-fix, low risk):
   - Apply formatting fixes across the codebase
   - These are safe to apply without review

3. **Run linters second** (may need manual judgment):
   - Fix auto-fixable lint issues
   - For issues that can't be auto-fixed, list them with file and line number

4. **Run type checker third** (if configured):
   - Fix type errors where the fix is unambiguous
   - For ambiguous type errors, explain the issue and ask the user

5. **Run tests last** to verify nothing broke:
   - If tests fail after fixes, investigate and fix the regression
   - If a fix caused the failure, revert that specific fix

6. **Report what was done:**
   ```
   Cleaned:
   - Formatted N files (tool: [formatter])
   - Fixed N lint issues (tool: [linter])
   - Fixed N type errors (tool: [type checker])
   - Tests: all passing / N failures (details)
   ```
