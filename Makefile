.PHONY: help test

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

build: ## build collection localy
	ansible-galaxy collection build

install: ## install collection localy
	ansible-galaxy collection install markuman*

remove: ## remove collection localy
	rm -rf markuman* ~/.ansible/collections/ansible_collections/markuman/

syntax: ## test compile
	python -m py_compile plugins/lookup/passwords.py
	python -m py_compile plugins/module_utils/nextcloud.py
	python -m py_compile plugins/modules/*.py

round: ## remove, build install
	$(MAKE) syntax
	$(MAKE) remove
	$(MAKE) build
	$(MAKE) install
	$(MAKE) test

test: ## run integration tests
	$(MAKE) integration -C tests/integration/targets