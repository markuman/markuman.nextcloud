.PHONY: help integration

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# run against the working copy, not against whatever is installed in ~/.ansible
COLLECTIONS_TMP ?= /tmp/markuman.nextcloud-collections
COLLECTION_ROOT := $(abspath ../../..)
NEXTCLOUD_VERSION ?= 35-apache

integration: ## run integration tests (podman)
	mkdir -p $(COLLECTIONS_TMP)/ansible_collections/markuman
	ln -sfn $(COLLECTION_ROOT) $(COLLECTIONS_TMP)/ansible_collections/markuman/nextcloud
	ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_TMP):$(HOME)/.ansible/collections:/usr/share/ansible/collections \
		ansible-playbook -i localhost, localhost.yml -e nextcloud_version=$(NEXTCLOUD_VERSION)
