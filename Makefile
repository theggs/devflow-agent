PYTHON ?= .venv/bin/python

.PHONY: help run test lint

help:
	@printf "Targets: help run test lint\n"
	@printf "Using PYTHON=%s\n" "$(PYTHON)"

run:
	$(PYTHON) -m app.main

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m compileall app tests
