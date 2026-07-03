# Awesome Claude Code — list generation.
#
# THE_RESOURCES_TABLE_NEW.csv is the single source of truth. `make generate`
# renders it (plus config.yaml + templates/README.template.md) into README.md.
# Generation is idempotent (re-running yields a byte-identical README.md) and
# fails closed if an Active entry has a Category missing from config.yaml.

PYTHON := venv/bin/python
DEPS_STAMP := venv/.deps-stamp

.PHONY: help deps generate test ticker ticker-data ticker-svg clean

venv: ## Set up the venv
	python3 -m venv venv

help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

deps: $(DEPS_STAMP) ## Install generation/test dependencies (pyyaml, pytest, requests) into the venv.

# Stamp file: pip runs only when the stamp is missing or older than this Makefile
# (i.e. when the pinned dependency list below changes). venv is an order-only
# prereq so its mtime churn (from writing caches) never re-triggers the install.
$(DEPS_STAMP): Makefile | venv
	$(PYTHON) -m pip install pyyaml pytest requests
	@touch $(DEPS_STAMP)

generate: $(DEPS_STAMP) ## Generate README.md from the CSV source of truth (idempotent, fail-closed).
	$(PYTHON) generate_readme.py

test: $(DEPS_STAMP) ## Run the test suite.
	$(PYTHON) -m pytest -q

ticker-data: $(DEPS_STAMP) ## Fetch GitHub "claude code" repos -> data/repo-ticker.csv (needs GITHUB_TOKEN).
	$(PYTHON) ticker/fetch_repo_ticker_data.py

ticker-svg: $(DEPS_STAMP) ## Render the awesome-style ticker SVG from data/repo-ticker.csv into assets/.
	$(PYTHON) ticker/generate_ticker_svg.py

ticker: ticker-data ticker-svg ## Refresh ticker data and regenerate the SVG.

clean: ## Remove Python caches (prunes __INTERNAL__ and venv; never touches tracked files).
	find . -path ./venv -prune -o -path ./__INTERNAL__ -prune -o -path ./.git -prune -o -name '__pycache__' -type d -print -exec rm -rf {} +
	find . -path ./venv -prune -o -path ./__INTERNAL__ -prune -o -path ./.git -prune -o -name '*.py[co]' -type f -print -exec rm -f {} +
	rm -rf .pytest_cache .mypy_cache
