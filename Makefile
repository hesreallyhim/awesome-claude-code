# Makefile for awesome-claude-code resource management
# Use venv python locally, system python in CI/CD
ifeq ($(CI),true)
    PYTHON := python3
else
    PYTHON := venv/bin/python3
endif
SCRIPTS_DIR := ./scripts

.PHONY: help validate validate-single validate-toc test coverage generate generate-toc-assets test-regenerate test-regenerate-no-cleanup test-regenerate-allow-diff test-regenerate-cycle docs-tree docs-tree-check download-resources add_resource add-category sort format format-check generate-resource-id mypy ci clean clean-all

help:
	@echo "Available commands:"
	@echo "  make add-category      - Add a new category to the repository"
	@echo "  make validate          - Validate all links in the resource CSV"
	@echo "  make validate-single URL=<url> - Validate a single resource URL"
	@echo "  make validate-toc      - Validate TOC anchors against GitHub HTML"
	@echo "  make test              - Run validation tests on test CSV"
	@echo "  make coverage          - Run pytest with coverage reports"
	@echo "  make mypy              - Run mypy type checks"
	@echo "  make format            - Check and fix code formatting with ruff"
	@echo "  make format-check      - Check code formatting without fixing"
	@echo "  make ci                - Run format-check, mypy, and tests"
	@echo "  make generate          - Generate README.md from CSV data, and create SVG badges"
	@echo "  make generate-toc-assets - Regenerate subcategory TOC SVGs (after adding subcategories)"
	@echo "  make test-regenerate   - Regenerate READMEs after deletion and fail if diff"
	@echo "  make generate-resource-id - Interactive resource ID generator"
	@echo "  make download-resources - Download active resources from GitHub"
	@echo "  make sort              - Sort resources by category, sub-category, and name"
	@echo "  make clean             - Remove caches and test artifacts"
	@echo "  make clean-all         - Remove caches and test artifacts, plus venv/"
	@echo "  make test-regenerate-no-cleanup - Keep outputs on failure for inspection"
	@echo "  make test-regenerate-allow-diff - Allow diffs after regeneration"
	@echo "  make test-regenerate-cycle - Full root/style-order regeneration cycle test"
	@echo "  make docs-tree         - Update README-GENERATION file tree"
	@echo "  make docs-tree-check   - Fail if README-GENERATION tree is out of date"
	@echo ""
	@echo "Options:"
	@echo "  make add-category      - Interactive mode to add a new category"
	@echo "  make add-category ARGS='--name \"My Category\" --prefix mycat --icon 🎯'"
	@echo "  make validate-github   - Run validation in GitHub Action mode (JSON output)"
	@echo "  make validate MAX_LINKS=N - Limit validation to N links"
	@echo "  make download-resources CATEGORY='Category Name' - Download specific category"
	@echo "  make download-resources LICENSE='MIT' - Download resources with specific license"
	@echo "  make download-resources MAX_DOWNLOADS=N - Limit downloads to N resources"
	@echo "  make download-resources HOSTED_DIR='path' - Custom hosted directory path"
	@echo ""
	@echo "Environment Variables:"
	@echo "  GITHUB_TOKEN - Set to avoid GitHub API rate limiting (export GITHUB_TOKEN=...)"

# Validate all links in the CSV (v2 with override support)
validate:
	@echo "Validating links in THE_RESOURCES_TABLE.csv (with override support)..."
	@if [ -n "$(MAX_LINKS)" ]; then \
		echo "Limiting validation to $(MAX_LINKS) links"; \
		$(PYTHON) -m scripts.validation.validate_links --max-links $(MAX_LINKS); \
	else \
		$(PYTHON) -m scripts.validation.validate_links; \
	fi

# Run validation in GitHub Action mode
validate-github:
	$(PYTHON) -m scripts.validation.validate_links --github-action

# Validate a single resource URL
validate-single:
	@if [ -z "$(URL)" ]; then \
		echo "Error: Please provide a URL to validate"; \
		echo "Usage: make validate-single URL=https://example.com/resource"; \
		exit 1; \
	fi
	@$(PYTHON) -m scripts.validation.validate_single_resource "$(URL)" $(if $(SECONDARY),--secondary "$(SECONDARY)") $(if $(NAME),--name "$(NAME)")

# Validate TOC anchors against GitHub HTML (requires .claude/root-readme-html-article-body.html)
validate-toc:
	@echo "Validating TOC anchors against GitHub HTML..."
	@$(PYTHON) -m scripts.testing.validate_toc_anchors

# Run all tests using pytest
test:
	@echo "Running all tests..."
	@$(PYTHON) -m pytest tests/ -v

# Run tests with coverage reporting
coverage:
	@echo "Running tests with coverage..."
	@$(PYTHON) -m pytest tests/ --cov=scripts --cov-report=term-missing --cov-report=html --cov-report=xml

# Run mypy type checks
mypy:
	@echo "Running mypy..."
	@$(PYTHON) -m mypy scripts tests

# Format code with ruff (check and fix)
format:
	@echo "Checking and fixing code formatting with ruff..."
	@$(PYTHON) -m ruff check scripts/ tests/ --fix || true
	@$(PYTHON) -m ruff format scripts/ tests/
	@echo "✅ Code formatting complete!"

# Check code formatting without fixing
format-check:
	@echo "Checking code formatting..."
	@$(PYTHON) -m ruff check scripts/ tests/
	@$(PYTHON) -m ruff format scripts/ tests/ --check
	@if $(PYTHON) -m ruff check scripts/ tests/ --quiet && $(PYTHON) -m ruff format scripts/ tests/ --check --quiet; then \
		echo "✅ Code formatting check passed!"; \
	else \
		echo "❌ Code formatting issues found. Run 'make format' to fix."; \
		exit 1; \
	fi

# Run CI checks locally
ci: format-check mypy test docs-tree-check

# Remove caches and test artifacts
clean:
	@echo "Cleaning caches and test artifacts..."
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov
	@rm -rf .eggs *.egg-info build dist .tox .nox
	@echo "✅ Clean complete."

# Remove caches, test artifacts, and virtual environment
clean-all: clean
	@echo "Removing venv/..."
	@rm -rf venv
	@echo "✅ Clean-all complete."

# Sort resources by category, sub-category, and name
sort:
	@echo "Sorting resources in THE_RESOURCES_TABLE.csv..."
	$(PYTHON) -m scripts.resources.sort_resources

# Regenerate subcategory TOC SVGs from categories.yaml
generate-toc-assets:
	@echo "Regenerating subcategory TOC SVGs..."
	$(PYTHON) -m scripts.readme.helpers.generate_toc_assets

# Generate README.md from CSV data using template system
generate: sort
	@echo "Generating README.md from CSV data using template system..."
	$(PYTHON) -m scripts.readme.generate_readme

# Regenerate READMEs from a clean tree and ensure outputs do not change
test-regenerate:
	@if [ "$${ALLOW_DIRTY:-0}" -ne 1 ] && [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: working tree must be clean for test-regenerate"; \
		exit 1; \
	fi
	@echo "Note: If the local date changes during this run (near midnight), regenerated READMEs may differ."
	@backup_dir=$$(mktemp -d 2>/dev/null || mktemp -d -t acc-readme-backup); \
	keep_outputs="$${KEEP_README_OUTPUTS:-0}"; \
	allow_diff="$${ALLOW_DIFF:-0}"; \
	restore() { \
		if [ -f "$$backup_dir/README.md" ]; then \
			cp "$$backup_dir/README.md" README.md; \
		else \
			rm -f README.md; \
		fi; \
		if [ -d "$$backup_dir/README_ALTERNATIVES" ]; then \
			rm -rf README_ALTERNATIVES; \
			cp -R "$$backup_dir/README_ALTERNATIVES" README_ALTERNATIVES; \
		else \
			rm -rf README_ALTERNATIVES; \
		fi; \
	}; \
	if [ -f README.md ]; then cp README.md "$$backup_dir/README.md"; fi; \
	if [ -d README_ALTERNATIVES ]; then cp -R README_ALTERNATIVES "$$backup_dir/"; fi; \
	echo "Removing README outputs..."; \
	rm -f README.md; \
	rm -rf README_ALTERNATIVES; \
	if ! $(MAKE) generate; then \
		echo "Error: README generation failed; restoring outputs"; \
		if [ "$$keep_outputs" -eq 1 ]; then \
			echo "Keeping outputs for inspection (backup at $$backup_dir)"; \
		else \
			echo "Tip: Run 'make test-regenerate-no-cleanup' to inspect the generated outputs without restoring."; \
			restore; \
			rm -rf "$$backup_dir"; \
		fi; \
		exit 1; \
	fi; \
	failure=""; \
	if [ ! -f README.md ]; then \
		failure="README.md not regenerated"; \
	elif [ ! -d README_ALTERNATIVES ] || [ -z "$$(ls -A README_ALTERNATIVES 2>/dev/null)" ]; then \
		failure="README_ALTERNATIVES is empty after regeneration"; \
	elif [ -n "$$(git status --porcelain)" ]; then \
		if [ "$$allow_diff" -eq 1 ]; then \
			echo "Diff allowed; skipping clean-tree enforcement."; \
		else \
			failure="working tree is dirty after regeneration; make generate may be out of sync"; \
		fi; \
	fi; \
	if [ -n "$$failure" ]; then \
		echo "Error: $$failure"; \
		if [ "$$keep_outputs" -eq 1 ]; then \
			echo "Keeping outputs for inspection (backup at $$backup_dir)"; \
		else \
			echo "Tip: Run 'make test-regenerate-no-cleanup' to inspect the generated outputs without restoring."; \
			restore; \
			rm -rf "$$backup_dir"; \
		fi; \
		exit 1; \
	fi; \
	rm -rf "$$backup_dir"; \
	echo "✅ Regeneration produced a clean working tree."

# Run test-regenerate but keep outputs on failure for inspection
test-regenerate-no-cleanup:
	@KEEP_README_OUTPUTS=1 $(MAKE) test-regenerate

# Run test-regenerate but allow diffs and dirty tree
test-regenerate-allow-diff:
	@ALLOW_DIRTY=1 ALLOW_DIFF=1 $(MAKE) test-regenerate

# Full regeneration cycle test (root style + selector order changes)
test-regenerate-cycle:
	@$(PYTHON) -m scripts.testing.test_regenerate_cycle

# Update README-GENERATION tree block
docs-tree:
	@$(PYTHON) -m tools.readme_tree.update_readme_tree

# Verify README-GENERATION tree block is up to date
# defaults
DOCS_TREE_CHECK ?= 1
DOCS_TREE_DEBUG ?= 0

DOCS_TREE_FLAGS :=
ifeq ($(DOCS_TREE_CHECK),1)
  DOCS_TREE_FLAGS += --check
endif
ifeq ($(DOCS_TREE_DEBUG),1)
  DOCS_TREE_FLAGS += --debug
endif

docs-tree-check:
	@$(PYTHON) -m tools.readme_tree.update_readme_tree $(DOCS_TREE_FLAGS)

# Download resources from GitHub
download-resources:
	@echo "Downloading resources from GitHub..."
	@ARGS=""; \
	if [ -n "$(CATEGORY)" ]; then ARGS="$$ARGS --category '$(CATEGORY)'"; fi; \
	if [ -n "$(LICENSE)" ]; then ARGS="$$ARGS --license '$(LICENSE)'"; fi; \
	if [ -n "$(MAX_DOWNLOADS)" ]; then ARGS="$$ARGS --max-downloads $(MAX_DOWNLOADS)"; fi; \
	if [ -n "$(OUTPUT_DIR)" ]; then ARGS="$$ARGS --output-dir '$(OUTPUT_DIR)'"; fi; \
	if [ -n "$(HOSTED_DIR)" ]; then ARGS="$$ARGS --hosted-dir '$(HOSTED_DIR)'"; fi; \
	eval $(PYTHON) -m scripts.resources.download_resources $$ARGS

# Interactive resource ID generator
generate-resource-id:
	@$(PYTHON) -m scripts.ids.generate_resource_id

# Install required Python packages
install:
	@echo "Installing required Python packages..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -e ".[dev]"
	@echo "Installation complete!"

# Add a new category to the repository
add-category:
	@echo "Starting category addition tool..."
	@$(PYTHON) -m scripts.categories.add_category $(ARGS)
