
.PHONY: dev up down test fmt

dev: up

up:
	docker compose up --build

down:
	docker compose down -v

test:
	# Python tests
	docker compose run --rm orchestrator pytest -q

fmt:
	# Placeholder: run formatters/linters in each subproject
	@echo "Run black/flake8 (python), mvn spotless:apply (java), clang-format (c++)"
