.PHONY: help test prepare converge idempotence verify destroy

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# run against the working copy, not against whatever is installed in ~/.ansible
COLLECTIONS_TMP ?= /tmp/markuman.nextcloud-collections
COLLECTION_ROOT := $(abspath ../..)
export ANSIBLE_COLLECTIONS_PATH := $(COLLECTIONS_TMP):$(HOME)/.ansible/collections:/usr/share/ansible/collections
PLAYBOOK := ansible-playbook -i inventory.yml

test: prepare converge idempotence verify destroy ## full role test in a debian 13 systemd container (podman)

link:
	mkdir -p $(COLLECTIONS_TMP)/ansible_collections/markuman
	ln -sfn $(COLLECTION_ROOT) $(COLLECTIONS_TMP)/ansible_collections/markuman/nextcloud

prepare: link ## build and start the container
	$(PLAYBOOK) prepare.yml

converge: link ## apply the role
	$(PLAYBOOK) converge.yml

idempotence: link ## apply the role again, nothing must change
	$(PLAYBOOK) converge.yml | tee /dev/stderr | grep -qE 'nextcloud-role-test\s+:.*changed=0\s+unreachable=0\s+failed=0'

verify: link ## run the module integration tests against the role
	$(PLAYBOOK) verify.yml

destroy: ## remove the container
	podman rm -f nextcloud-role-test
