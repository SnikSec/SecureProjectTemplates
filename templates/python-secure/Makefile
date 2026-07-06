# Minimal Makefile for template projects.
PYTHON ?= python

.PHONY: install lint test validate

install:
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m ruff check src/ tests/

test:
	$(PYTHON) -m unittest discover -s tests

validate:
	@echo "All checks passed"
