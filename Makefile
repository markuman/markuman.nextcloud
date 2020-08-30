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

round: ## remove, build install
	$(MAKE) remove
	$(MAKE) build
	$(MAKE) install