# Awesome Claude Code — list generation.
#
# THE_RESOURCES_TABLE_NEW.csv is the single source of truth. `make generate`
# renders it (plus config.yaml + templates/README.template.md) into README.md.
# Generation is idempotent (re-running yields a byte-identical README.md) and
# fails closed if an Active entry has a Category missing from config.yaml.

PYTHON := venv/bin/python
DEPS_STAMP := venv/.deps-stamp

.PHONY: help deps generate readme add-category move-category remove-category add-resource sync-form install-hooks test ticker ticker-data ticker-svg recently-added clean

venv: ## Set up the venv
	python3 -m venv venv

help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

deps: $(DEPS_STAMP) ## Install dev dependencies (requirements-dev.txt) into the venv.

# Stamp file: pip runs only when the stamp is missing or older than the requirements
# files (i.e. when the dependency list changes). venv is an order-only prereq so its
# mtime churn (from writing caches) never re-triggers the install.
$(DEPS_STAMP): requirements.txt requirements-dev.txt | venv
	$(PYTHON) -m pip install -r requirements-dev.txt
	@touch $(DEPS_STAMP)

# Full local regeneration: every artifact derived from config.yaml / the CSV, in one
# command so nothing is forgotten. The ticker is intentionally excluded — it fetches
# remote data and needs GITHUB_TOKEN (run `make ticker` separately).
generate: sync-form recently-added readme ## Regenerate everything local: issue-form dropdown, carousel SVGs, and README.

readme: $(DEPS_STAMP) ## Render README.md from the CSV + config (idempotent, fail-closed).
	$(PYTHON) generate_readme.py

# Category management: edit config.yaml, sync the recommend-resource issue-form
# dropdown (category-level edits only), then regenerate README.md. All three take
# CATEGORY= (required) and optional SUB_CATEGORY= to target a sub-category.
#   make add-category    CATEGORY="Testing & QA" PREFIX=testing
#   make add-category    CATEGORY="Security" SUB_CATEGORY="Secrets Scanning" ORDER=2
#   make move-category   CATEGORY="Meta-Skills" ORDER=15
#   make remove-category CATEGORY="Linting"
add-category: $(DEPS_STAMP) ## Add a category/sub-category (CATEGORY=, [SUB_CATEGORY=], [ORDER=], [PREFIX=], [DESCRIPTION=]).
	@test -n "$(CATEGORY)" || { echo "usage: make add-category CATEGORY=\"Name\" [SUB_CATEGORY=\"Name\"] [ORDER=N] [PREFIX=p] [DESCRIPTION=\"...\"]"; exit 2; }
	$(PYTHON) scripts/manage_categories.py add --category "$(CATEGORY)" $(if $(SUB_CATEGORY),--subcategory "$(SUB_CATEGORY)") $(if $(ORDER),--order "$(ORDER)") $(if $(PREFIX),--prefix "$(PREFIX)") $(if $(DESCRIPTION),--description "$(DESCRIPTION)")
	$(PYTHON) generate_readme.py

move-category: $(DEPS_STAMP) ## Move a category/sub-category to a new position (CATEGORY=, ORDER=, [SUB_CATEGORY=]).
	@test -n "$(CATEGORY)" -a -n "$(ORDER)" || { echo "usage: make move-category CATEGORY=\"Name\" ORDER=N [SUB_CATEGORY=\"Name\"]"; exit 2; }
	$(PYTHON) scripts/manage_categories.py move --category "$(CATEGORY)" --order "$(ORDER)" $(if $(SUB_CATEGORY),--subcategory "$(SUB_CATEGORY)")
	$(PYTHON) generate_readme.py

remove-category: $(DEPS_STAMP) ## Remove a category/sub-category (CATEGORY=, [SUB_CATEGORY=], [FORCE=1]).
	@test -n "$(CATEGORY)" || { echo "usage: make remove-category CATEGORY=\"Name\" [SUB_CATEGORY=\"Name\"] [FORCE=1]"; exit 2; }
	$(PYTHON) scripts/manage_categories.py remove --category "$(CATEGORY)" $(if $(SUB_CATEGORY),--subcategory "$(SUB_CATEGORY)") $(if $(FORCE),--force)
	$(PYTHON) generate_readme.py

# Add a single resource to the CSV: mint its opaque ID, validate the Category against
# config.yaml, dedupe by link, append, then regenerate README.md. DISPLAY_NAME,
# CATEGORY, and LINK are required; AUTHOR/AUTHOR_LINK/SUBCATEGORY/DESCRIPTION optional.
#   make add-resource DISPLAY_NAME="cctop" CATEGORY="Session Monitors" \
#       LINK="https://github.com/stefanprodan/cctop" AUTHOR="stefanprodan" \
#       AUTHOR_LINK="https://github.com/stefanprodan" DESCRIPTION="..."
add-resource: $(DEPS_STAMP) ## Add one resource to the CSV (DISPLAY_NAME=, CATEGORY=, LINK=; optional AUTHOR=, AUTHOR_LINK=, SUBCATEGORY=, DESCRIPTION=).
	@test -n "$(DISPLAY_NAME)" -a -n "$(CATEGORY)" -a -n "$(LINK)" || { echo 'usage: make add-resource DISPLAY_NAME="Name" CATEGORY="Category" LINK="https://..." [AUTHOR="..."] [AUTHOR_LINK="https://..."] [SUBCATEGORY="..."] [DESCRIPTION="..."]'; exit 2; }
	$(PYTHON) resources/add_resource.py --display-name "$(DISPLAY_NAME)" --category "$(CATEGORY)" --link "$(LINK)" $(if $(AUTHOR),--author-name "$(AUTHOR)") $(if $(AUTHOR_LINK),--author-link "$(AUTHOR_LINK)") $(if $(SUBCATEGORY),--subcategory "$(SUBCATEGORY)") $(if $(DESCRIPTION),--description "$(DESCRIPTION)")
	$(PYTHON) generate_readme.py

sync-form: $(DEPS_STAMP) ## Regenerate the recommend-resource category dropdown from config.yaml.
	$(PYTHON) scripts/sync_issue_form.py

install-hooks: $(DEPS_STAMP) ## Install the local pre-commit git hooks (run once per clone).
	$(PYTHON) -m pre_commit install

test: $(DEPS_STAMP) ## Run the test suite.
	$(PYTHON) -m pytest -q

ticker-data: $(DEPS_STAMP) ## Fetch GitHub "claude code" repos -> data/repo-ticker.csv (needs GITHUB_TOKEN).
	$(PYTHON) ticker/fetch_repo_ticker_data.py

ticker-svg: $(DEPS_STAMP) ## Render the awesome-style ticker SVG from data/repo-ticker.csv into assets/.
	$(PYTHON) ticker/generate_ticker_svg.py

ticker: ticker-data ticker-svg ## Refresh ticker data and regenerate the SVG.

recently-added: $(DEPS_STAMP) ## Render the "Recently Added" carousel SVGs (dark+light) from the CSV into assets/.
	$(PYTHON) ticker/generate_recently_added_svg.py

clean: ## Remove Python caches (prunes __INTERNAL__ and venv; never touches tracked files).
	find . -path ./venv -prune -o -path ./__INTERNAL__ -prune -o -path ./.git -prune -o -name '__pycache__' -type d -print -exec rm -rf {} +
	find . -path ./venv -prune -o -path ./__INTERNAL__ -prune -o -path ./.git -prune -o -name '*.py[co]' -type f -print -exec rm -f {} +
	rm -rf .pytest_cache .mypy_cache
