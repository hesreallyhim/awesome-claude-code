# Makefile for awesome-claude-code resource management
PYTHON := python3
SCRIPTS_DIR := .myob/scripts

.PHONY: help process validate update clean

help:
	@echo "Available commands:"
	@echo "  make process   - Extract resources from README.md and create/update CSV"
	@echo "  make validate  - Validate all links in the resource CSV"
	@echo "  make update    - Run both process and validate"
	@echo "  make clean     - Remove generated files"
	@echo ""
	@echo "Options:"
	@echo "  make validate-github - Run validation in GitHub Action mode (JSON output)"

# Extract resources from README.md and create/update CSV
process:
	@echo "Processing README.md to extract resources..."
	@cd $(SCRIPTS_DIR) && $(PYTHON) process_resources_to_csv.py

# Validate all links in the CSV
validate:
	@echo "Validating links in resource-metadata.csv..."
	@cd $(SCRIPTS_DIR) && $(PYTHON) validate_links.py

# Run validation in GitHub Action mode
validate-github:
	@cd $(SCRIPTS_DIR) && $(PYTHON) validate_links.py --github-action

# Update: process resources then validate links
update: process validate
	@echo "Update complete!"

# Clean generated files (preserves scripts)
clean:
	@echo "Cleaning generated files..."
	@rm -f .myob/scripts/resource-metadata.csv
	@echo "Clean complete!"

# Install required Python packages
install:
	@echo "Installing required Python packages..."
	@pip install requests
	@echo "Installation complete!"