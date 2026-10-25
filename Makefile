.PHONY: help build install remove sanity lint test test-role fullround round

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

SANITY_TMP ?= /tmp/markuman.nextcloud-sanity

build: ## build collection localy
	ansible-galaxy collection build -f

install: ## install collection localy
	ansible-galaxy collection install -f markuman-nextcloud-*.tar.gz

remove: ## remove collection localy
	rm -rf markuman-nextcloud-*.tar.gz ~/.ansible/collections/ansible_collections/markuman/nextcloud

sanity: ## ansible-test sanity (needs the collection below ansible_collections/markuman/nextcloud)
	rm -rf $(SANITY_TMP)
	mkdir -p $(SANITY_TMP)/ansible_collections/markuman/nextcloud
	git ls-files -z --cached --others --exclude-standard | xargs -0 cp --parents -t $(SANITY_TMP)/ansible_collections/markuman/nextcloud
	cd $(SANITY_TMP)/ansible_collections/markuman/nextcloud && git init -q && git add -A && ansible-test sanity --local

lint: ## ansible-lint
	ansible-lint

test: ## run module integration tests (podman)
	$(MAKE) integration -C tests/integration/targets

test-role: ## run the install role in a debian 13 container and the module tests against it (podman)
	$(MAKE) test -C tests/role

fullround: ## everything
	$(MAKE) remove
	$(MAKE) build
	$(MAKE) install
	$(MAKE) sanity
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) test-role

round: ## short round
	$(MAKE) remove
	$(MAKE) build
	$(MAKE) install
