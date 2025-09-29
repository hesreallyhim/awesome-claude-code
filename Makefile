# Makefile for awesome-claude-code resource management
# Use venv python locally, system python in CI/CD
ifeq ($(CI),true)
    PYTHON := python3
else
    PYTHON := venv/bin/python3
endif
SCRIPTS_DIR := ./scripts

.PHONY: help process validate validate-single validate_new_resource update clean test generate download-resources add_resource sort submit submit-resource format format-check

help:
	@echo "Available commands:"
	@echo "  make add_resource      - Interactive tool to add a new resource"
	@echo "  make submit            - One-command submission workflow (entry to PR)"
	@echo "  make process           - Extract resources from README.md and create/update CSV"
	@echo "  make validate          - Validate all links in the resource CSV"
	@echo "  make validate-single URL=<url> - Validate a single resource URL"
	@echo "  make validate_new_resource - Validate new resource (pre-push check)"
	@echo "  make install-hooks    - Install git hooks (including pre-push validation)"
	@echo "  make test              - Run validation tests on test CSV"
	@echo "  make format            - Check and fix code formatting with ruff"
	@echo "  make format-check      - Check code formatting without fixing"
	@echo "  make generate          - Generate README.md from CSV data"
	@echo "  make update            - Run both process and validate"
	@echo "  make download-resources - Download active resources from GitHub"
	@echo "  make sort              - Sort resources by category, sub-category, and name"
	@echo "  make clean             - Remove generated files"
	@echo ""
	@echo "Options:"
	@echo "  make validate-github   - Run validation in GitHub Action mode (JSON output)"
	@echo "  make validate MAX_LINKS=N - Limit validation to N links"
	@echo "  make download-resources CATEGORY='Category Name' - Download specific category"
	@echo "  make download-resources LICENSE='MIT' - Download resources with specific license"
	@echo "  make download-resources MAX_DOWNLOADS=N - Limit downloads to N resources"
	@echo "  make download-resources HOSTED_DIR='path' - Custom hosted directory path"
	@echo ""
	@echo "Environment Variables:"
	@echo "  GITHUB_TOKEN - Set to avoid GitHub API rate limiting (export GITHUB_TOKEN=...)"

# Extract resources from README.md and create/update CSV
process:
	@echo "Processing README.md to extract resources..."
	$(PYTHON) $(SCRIPTS_DIR)/process_resources_to_csv.py

# Validate all links in the CSV (v2 with override support)
validate:
	@echo "Validating links in THE_RESOURCES_TABLE.csv (with override support)..."
	@if [ -n "$(MAX_LINKS)" ]; then \
		echo "Limiting validation to $(MAX_LINKS) links"; \
		$(PYTHON) $(SCRIPTS_DIR)/validate_links.py --max-links $(MAX_LINKS); \
	else \
		$(PYTHON) $(SCRIPTS_DIR)/validate_links.py; \
	fi

# Run validation in GitHub Action mode
validate-github:
	$(PYTHON) $(SCRIPTS_DIR)/validate_links.py --github-action

# Validate a single resource URL
validate-single:
	@if [ -z "$(URL)" ]; then \
		echo "Error: Please provide a URL to validate"; \
		echo "Usage: make validate-single URL=https://example.com/resource"; \
		exit 1; \
	fi
	@$(PYTHON) $(SCRIPTS_DIR)/validate_single_resource.py "$(URL)" $(if $(SECONDARY),--secondary "$(SECONDARY)") $(if $(NAME),--name "$(NAME)")

# Validate only the newest added resource (pre-push hook)
validate_new_resource:
	@echo "Validating new resource (pre-push check)..."
	@$(PYTHON) $(SCRIPTS_DIR)/validate_new_resource.py

# Install git hooks
install-hooks:
	@echo "Installing git hooks..."
	@cp hooks/pre-push .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "Pre-push hook installed successfully!"

# Run all tests using pytest
test:
	@echo "Running all tests..."
	@$(PYTHON) -m pytest tests/ -v

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

# Sort resources by category, sub-category, and name
sort:
	@echo "Sorting resources in THE_RESOURCES_TABLE.csv..."
	$(PYTHON) $(SCRIPTS_DIR)/sort_resources.py

# Generate README.md from CSV data using template system
generate: sort
	@echo "Generating README.md from CSV data using template system..."
	$(PYTHON) $(SCRIPTS_DIR)/generate_readme.py

# Update: process resources then validate links
update: process validate
	@echo "Update complete!"

# Download resources from GitHub
download-resources:
	@echo "Downloading resources from GitHub..."
	@ARGS=""; \
	if [ -n "$(CATEGORY)" ]; then ARGS="$$ARGS --category '$(CATEGORY)'"; fi; \
	if [ -n "$(LICENSE)" ]; then ARGS="$$ARGS --license '$(LICENSE)'"; fi; \
	if [ -n "$(MAX_DOWNLOADS)" ]; then ARGS="$$ARGS --max-downloads $(MAX_DOWNLOADS)"; fi; \
	if [ -n "$(OUTPUT_DIR)" ]; then ARGS="$$ARGS --output-dir '$(OUTPUT_DIR)'"; fi; \
	if [ -n "$(HOSTED_DIR)" ]; then ARGS="$$ARGS --hosted-dir '$(HOSTED_DIR)'"; fi; \
	eval $(PYTHON) $(SCRIPTS_DIR)/download_resources.py $$ARGS

# Clean generated files (preserves scripts)
clean:
	@echo "Cleaning generated files..."
	@rm -f THE_RESOURCES_TABLE.csv
	@rm -rf .myob/downloads
	@echo "Clean complete!"

# Install required Python packages
install:
	@echo "Installing required Python packages..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -e ".[dev]"
	@echo "Installation complete!"

# Add a new resource interactively
add_resource:
	@echo "Starting interactive resource submission..."
	@$(PYTHON) $(SCRIPTS_DIR)/add_resource.py

# One-command submission workflow
submit:
	@echo "Starting resource submission workflow..."
	@$(PYTHON) $(SCRIPTS_DIR)/submit_resource.py $(ARGS)

# Alias for submit
submit-resource: submit
