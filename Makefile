
DOCKER_RUN_CMD = docker-compose run --rm --user `id -u` tester

default: help

.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    %-20s%s\n", $$1, $$2}'

.PHONY: docker-build
docker-build: ## Build docker images used to run automated tests
	docker build --target test --tag geocat/bridgehub-tester ./docker

.PHONY: build
build: ## Build everything
build: docker-build

.PHONY: servers
qgis: ## Run QGIS desktop
	docker-compose run --rm --user `id -u` servers


.PHONY: check
check: ## Run linters
	$(DOCKER_RUN_CMD) make -f docker.mk check

.PHONY: black
black: ## Run black formatter
	$(DOCKER_RUN_CMD) make -f docker.mk black

.PHONY: test
test: ## Run the automated tests suite
test:
	$(DOCKER_RUN_CMD) make -f docker.mk nosetests

.PHONY: bash
bash: ## Run bash in tests container
	$(DOCKER_RUN_CMD) bash

