# CLAUDE.md — awesome-claude-code

This file provides guidance for AI assistants (Claude Code and similar) working in this repository.

## Project Overview

**awesome-claude-code** is a production-grade, automated resource curation platform that maintains a curated list of Claude Code tools, extensions, and resources. The canonical resource database lives in a single CSV file (`THE_RESOURCES_TABLE.csv`), and all rendered README files are generated from it via a Python-based template system.

- **Version**: 2.0.1
- **Python requirement**: 3.11+
- **License**: MIT
- **Key principle**: `THE_RESOURCES_TABLE.csv` is the single source of truth. `README.md` is a **generated file** — never edit it directly.

---

## Repository Structure

```
awesome-claude-code/
├── THE_RESOURCES_TABLE.csv      # Single source of truth for all resources
├── acc-config.yaml              # README style config (root style, style selector order)
├── Makefile                     # All development commands (30+ targets)
├── pyproject.toml               # Python package config, ruff/mypy/pytest settings
├── .pre-commit-config.yaml      # Pre-commit hooks (ruff, tests, README regeneration check)
├── .python-version              # Python 3.11+
├── README.md                    # GENERATED — do not edit directly
├── README_ALTERNATIVES/         # GENERATED — 44+ alternative README variants
├── assets/                      # Badges, SVGs, images (some generated)
├── data/                        # Repository ticker stats (JSON)
├── docs/                        # Contributing guides and documentation
├── resources/                   # Cached CLAUDE.md files from listed projects
├── scripts/                     # All automation scripts (see below)
├── templates/                   # README templates, categories.yaml, SVG templates
├── tests/                       # pytest test suite (21 files)
├── tools/                       # Utility tools (readme_tree)
└── .claude/commands/            # Claude Code slash-command definitions
```

### `scripts/` Directory

The automation heart of the project, organized into submodules:

| Submodule | Purpose |
|-----------|---------|
| `scripts/readme/` | README generation (4 styles: awesome, classic, extra, flat) |
| `scripts/readme/generators/` | Per-style generator classes |
| `scripts/readme/helpers/` | Config, assets, paths, utility helpers |
| `scripts/readme/markup/` | Markup generation per style |
| `scripts/readme/svg_templates/` | SVG header, badge, TOC, divider generation |
| `scripts/resources/` | CSV utilities, PR creation, resource parsing, sorting, downloading |
| `scripts/validation/` | Link validation (bulk and single), GitHub API integration |
| `scripts/categories/` | Category manager, interactive category addition tool |
| `scripts/ids/` | Resource ID generation |
| `scripts/badges/` | Badge notification logic for merged resources |
| `scripts/ticker/` | GitHub repo stats fetcher and animated SVG ticker generator |
| `scripts/graphics/` | Branding SVG asset generation |
| `scripts/utils/` | Shared git utilities, GitHub API helpers, repo root resolver |
| `scripts/maintenance/` | Repository health checks |
| `scripts/testing/` | TOC anchor validation, full regeneration cycle tests |

### `templates/` Directory

| File | Purpose |
|------|---------|
| `templates/categories.yaml` | **Single source of truth** for all categories and subcategories |
| `templates/*.md` | README style templates with placeholder markers |
| `templates/svg/` | SVG templates for headers, TOC sections, dividers |

---

## Development Workflow

### Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Locally, all `make` targets use `venv/bin/python3`. In CI (`CI=true`), they use system `python3`.

### Key Commands

```bash
# Generate all README files from CSV (always run after editing CSV)
make generate

# Sort CSV by category hierarchy (also runs automatically before generate)
make sort

# Run the full test suite
make test

# Run tests with coverage
make coverage

# Type checking
make mypy

# Format code (ruff check + fix)
make format

# Check formatting without fixing
make format-check

# Run all CI checks locally (format-check + mypy + test + docs-tree-check)
make ci

# Validate all resource URLs (requires GITHUB_TOKEN for full API access)
make validate

# Validate a single URL
make validate-single URL=https://github.com/example/repo

# Validate TOC anchors against GitHub HTML
make validate-toc

# Regenerate READMEs from scratch and fail if output changes (clean-tree test)
make test-regenerate

# Full regeneration cycle test (tests root style swaps and style-order changes)
make test-regenerate-cycle

# Generate a new resource ID interactively
make generate-resource-id

# Add a new category interactively
make add-category

# Regenerate subcategory TOC SVGs (after adding subcategories to categories.yaml)
make generate-toc-assets

# Update the docs/README-GENERATION file tree
make docs-tree

# Check that the file tree is up to date (fails in CI if stale)
make docs-tree-check

# Clean all build artifacts
make clean

# Clean including venv
make clean-all
```

---

## Running Scripts

All scripts are Python modules. Always run them from the **repository root** using `-m`:

```bash
python -m scripts.readme.generate_readme
python -m scripts.resources.sort_resources
python -m scripts.validation.validate_links
python -m scripts.validation.validate_single_resource "https://example.com"
python -m scripts.ids.generate_resource_id
python -m scripts.categories.add_category
```

**Never** run scripts as files (`python scripts/readme/generate_readme.py`) — relative imports will break.

All scripts resolve paths from the repo root using `find_repo_root(Path(__file__))` from `scripts/utils/repo_root.py`.

---

## CSV Data Model

**`THE_RESOURCES_TABLE.csv`** — 20 columns, order matters:

| Column | Notes |
|--------|-------|
| `ID` | Format: `<prefix>-<8char-uuid>` (e.g., `skill-ca8cbc21`) |
| `Display Name` | Human-readable resource name |
| `Category` | Must match a category `name` from `templates/categories.yaml` |
| `Sub-Category` | Must match a subcategory `name` from `templates/categories.yaml` |
| `Primary Link` | Main URL (GitHub repo, documentation, etc.) |
| `Secondary Link` | Optional additional URL |
| `Author Name` | Creator's display name |
| `Author Link` | Creator's profile or website URL |
| `Active` | `TRUE` / `FALSE` |
| `Date Added` | ISO date (`YYYY-MM-DD`) |
| `Last Modified` | ISO date |
| `Last Checked` | ISO date (set by validation script) |
| `License` | SPDX identifier (e.g., `MIT`) or empty |
| `Description` | One-line resource description |
| `Removed From Origin` | `TRUE` if original URL no longer exists |
| `Stale` | `TRUE` if resource appears unmaintained |
| `Repo Created` | GitHub repo creation date |
| `Latest Release` | Date of latest GitHub release |
| `Release Version` | Latest version tag |
| `Release Source` | Source of release data |

**Rules:**
- Always run `make sort` before `make generate` (or just `make generate`, which runs sort automatically)
- Do not manually reorder CSV headers — scripts depend on header-aligned column order
- `Active=FALSE` rows are excluded from generated READMEs

---

## Category System

**`templates/categories.yaml`** is the single source of truth for categories. Changes here automatically propagate to all scripts and generated files — no code edits needed.

Category ID prefixes used in resource IDs:

| Category | Prefix |
|----------|--------|
| Agent Skills | `skill` |
| Workflows & Knowledge Guides | `wf` |
| Tooling | `tool` |
| Status Lines | `status` |
| Hooks | `hook` |
| Slash-Commands | `cmd` |
| CLAUDE.md Files | `claude` |
| Alternative Clients | `client` |
| Official Documentation | `doc` |

To add a new category:
```bash
make add-category
# or with args:
make add-category ARGS='--name "My Category" --prefix mycat --icon 🎯'
```

After adding subcategories, regenerate TOC SVG assets:
```bash
make generate-toc-assets
make generate
```

---

## README Generation System

`make generate` runs `make sort` then `python -m scripts.readme.generate_readme`, which produces:

- `README.md` — root README (style controlled by `acc-config.yaml` → `readme.root_style`)
- `README_ALTERNATIVES/README_CLASSIC.md`
- `README_ALTERNATIVES/README_EXTRA.md`
- `README_ALTERNATIVES/README_AWESOME.md`
- `README_ALTERNATIVES/README_FLAT_<CATEGORY>_<SORT>.md` — 44 variants (11 categories × 4 sort orders: AZ, UPDATED, CREATED, RELEASES)

**Style configuration** lives in `acc-config.yaml`:
- `readme.root_style`: which style is `README.md` (options: `awesome`, `classic`, `extra`, `flat`)
- `styles`: badge filename, highlight color, and output filename per style
- `style_order`: left-to-right order in the style selector badge row

**Never edit `README.md` directly** — changes will be overwritten on the next `make generate`.

---

## Code Quality Standards

| Tool | Command | Config |
|------|---------|--------|
| Ruff (lint + format) | `make format` / `make format-check` | `pyproject.toml [tool.ruff]` |
| mypy | `make mypy` | `pyproject.toml [tool.mypy]` |
| pytest | `make test` | `pyproject.toml [tool.pytest.ini_options]` |
| pre-commit | Auto on `git commit` | `.pre-commit-config.yaml` |

**Ruff rules enforced**: `E`, `W`, `F` (pyflakes), `I` (isort), `N` (naming), `UP` (pyupgrade), `B` (bugbear), `C4` (comprehensions), `SIM` (simplify).

- Line length: **100 characters**
- `scripts/archive/` is excluded from linting
- `__init__.py` files may have unused imports (`F401` ignored)
- `scripts/*` files may have long lines (`E501` ignored)

**Pre-commit hooks** (run automatically on `git commit`):
1. Standard checks: large files, merge conflicts, YAML/JSON validity, private keys, EOF, line endings
2. Ruff lint + format (auto-fix)
3. `make test` — all tests must pass
4. README regeneration check: runs `make generate` and fails if `README.md` differs from committed version

---

## Testing

```bash
make test         # Run all tests
make coverage     # Run with coverage (HTML report in htmlcov/)
```

Test files live in `tests/` (21 files, 300+ test cases). A `conftest.py` provides shared fixtures (dummy GitHub API objects for mocking).

Coverage excludes `scripts/archive/` and `scripts/testing/test_regenerate_cycle.py`.

To verify README generation is idempotent (required to pass before merging CSV or template changes):

```bash
make test-regenerate                # Fails if output differs from committed
make test-regenerate-no-cleanup     # Keep outputs on failure for inspection
make test-regenerate-allow-diff     # Allow diffs (for debugging only)
make test-regenerate-cycle          # Full root-style + selector-order cycle test
```

---

## GitHub Integration

### API Access

Set `GITHUB_TOKEN` to avoid rate limiting for link validation and metadata fetching:

```bash
export GITHUB_TOKEN=ghp_...
make validate
```

For workflows that create PRs: `AWESOME_CC_PAT_PUBLIC_REPO` is used.

### Automated Workflows (`.github/workflows/`)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push, PR | format-check, mypy, tests |
| `validate-links.yml` | Daily schedule + manual | Validates all resource URLs; updates CSV metadata |
| `validate-new-issue.yml` | Issue opened | Auto-validates new resource submissions |
| `handle-resource-submission-commands.yml` | PR comment `/approve` | Creates resource PR from approved submission |
| `close-resource-pr.yml` | Issue closed | Auto-closes linked PR |
| `notify-on-merge.yml` | PR merged | Sends notification to merged resource's repo |
| `check-repo-health.yml` | Scheduled | Health checks |
| `update-github-release-data.yml` | Scheduled | Updates release metadata in CSV |
| `update-repo-ticker.yml` | Scheduled | Fetches repo stats; generates ticker SVGs |

### Resource Submission Flow

1. User submits via GitHub Issue form (`.github/ISSUE_TEMPLATE/recommend-resource.yml`)
2. `validate-new-issue.yml` auto-validates the submission
3. Maintainer uses `/approve` comment on the issue
4. `handle-resource-submission-commands.yml` runs `scripts/resources/create_resource_pr.py` to create a PR
5. PR merges → `notify-on-merge.yml` notifies the resource's repository

---

## Important Conventions

### Path Resolution

All scripts use `find_repo_root(Path(__file__))` from `scripts/utils/repo_root.py` to locate the repo root. Never hardcode paths or assume a working directory. All file paths are constructed relative to `REPO_ROOT`.

### Import Style

```python
# Correct — use package-style imports
from scripts.readme.generate_readme import main
from scripts.utils.repo_root import find_repo_root
from scripts.categories.category_utils import CategoryManager

# Incorrect — never use relative file-based imports from scripts directly
```

### Adding a New Resource (manual method)

1. Generate an ID: `make generate-resource-id`
2. Append a row to `THE_RESOURCES_TABLE.csv` with all required fields
3. Ensure `Category` and `Sub-Category` match values in `templates/categories.yaml` exactly
4. Run `make generate` (sorts then regenerates all READMEs)
5. Run `make test` to confirm nothing is broken
6. Commit both the CSV and the regenerated README files

### Adding a New Script

- Place it in the appropriate `scripts/<submodule>/` directory
- Use `find_repo_root` for all file paths
- Add type hints throughout
- Write tests in `tests/test_<script_name>.py`
- Run `make ci` to verify it passes format, type checks, and tests
- Update `scripts/README.md` to document the new script
- Run `make docs-tree` to update the file tree in docs

### Modifying Templates

After modifying `templates/categories.yaml` (adding categories/subcategories):
1. Run `make generate-toc-assets` to regenerate TOC SVGs
2. Run `make generate` to regenerate all READMEs
3. Run `make test-regenerate` to confirm generation is idempotent

After modifying README template `.md` files in `templates/`:
1. Run `make generate`
2. Run `make test-regenerate` to confirm idempotency
3. Run `make test`

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub API access (avoids rate limiting for validation) |
| `AWESOME_CC_PAT_PUBLIC_REPO` | PAT used by CI workflows to create PRs and post comments |
| `CI` | Set to `true` in GitHub Actions; switches Makefile to use system `python3` |

---

## What AI Assistants Should Know

1. **Never edit `README.md` directly** — it is fully generated. Edit the CSV or templates, then run `make generate`.
2. **The CSV column order is fixed** — do not reorder headers; scripts depend on positional column mapping.
3. **`templates/categories.yaml` is the single source for categories** — if you add a category to the CSV, it must already exist in `categories.yaml`.
4. **Run `make ci` before committing** — this catches formatting, type, test, and docs-tree issues that will fail pre-commit hooks and CI.
5. **All scripts run as modules from repo root** — use `python -m scripts.module.path`, not `python scripts/module/path.py`.
6. **Test isolation**: tests mock GitHub API calls using `conftest.py` fixtures — do not make real network calls in tests.
7. **The `resources/` directory** contains cached copies of CLAUDE.md files from listed projects — these are read-only snapshots, not maintained code.
8. **README generation is idempotent** — running `make generate` twice on an unchanged CSV/template must produce identical output. If you modify generation logic, verify with `make test-regenerate`.
