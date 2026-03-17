PYTHON ?= python3

.PHONY: help run test lint

help:
	@printf "Targets: help run test lint\n"

run:
	$(PYTHON) -m app.main

test:
	pytest

lint:
	python -m compileall app
