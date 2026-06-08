.DEFAULT_GOAL := help
SHELL := /bin/bash
COLLECTION_NS := malpanez
COLLECTION_NAME := security
UV := uv run --no-project

.PHONY: help lint sanity test molecule build changelog docs precommit install-local

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

lint: ## Run ansible-lint (production) and yamllint
	$(UV) --with ansible-core --with ansible-lint -- ansible-lint --profile production
	$(UV) --with yamllint -- yamllint -c .yamllint.yml .

sanity: ## Run ansible-test sanity from a temporary collection tree
	@work=$$(mktemp -d); dest="$$work/ansible_collections/$(COLLECTION_NS)/$(COLLECTION_NAME)"; \
	mkdir -p "$$dest"; \
	rsync -a --exclude '.git' --exclude '.venv' --exclude 'ansible_collections' \
		--exclude '.ansible' --exclude '__pycache__' --exclude '*.tar.gz' ./ "$$dest/"; \
	cd "$$dest" && $(UV) --with ansible-core --with ansible-lint --with pyyaml -- \
		ansible-test sanity --venv --color; rc=$$?; rm -rf "$$work"; exit $$rc

test: ## Run molecule for a role:  make test ROLE=firewall
	@test -n "$(ROLE)" || { echo "Usage: make test ROLE=<role>"; exit 2; }
	cd roles/$(ROLE) && $(UV) --with molecule --with 'molecule-plugins[docker]' \
		--with ansible-core --with pytest-testinfra -- molecule test

molecule: ## Run the default top-level molecule scenario
	$(UV) --with molecule --with 'molecule-plugins[docker]' --with ansible-core -- \
		molecule test -s default

build: ## Build the collection artifact
	$(UV) --with ansible-core -- ansible-galaxy collection build --force

changelog: ## Lint changelog fragments
	$(UV) --with antsibull-changelog -- antsibull-changelog lint

docs: ## Render the antsibull-docs site locally
	$(UV) --with ansible-core --with antsibull-docs --with sphinx --with sphinx-ansible-theme -- \
		antsibull-docs sphinx-init --use-current --squash-hierarchy \
		--dest-dir built_docs $(COLLECTION_NS).$(COLLECTION_NAME)

precommit: ## Run all pre-commit hooks
	pre-commit run --all-files

install-local: ## Install the collection into ./.collections for manual testing
	rm -rf .collections
	mkdir -p .collections
	$(UV) --with ansible-core -- ansible-galaxy collection install -p .collections .
