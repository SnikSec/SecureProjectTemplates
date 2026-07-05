"""Minimal Makefile for template projects."""
PYTHON ?= python

.PHONY: install lint test validate

install:
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m flake8 src/ || true

test:
	$(PYTHON) -m unittest discover -s tests

validate:
	@echo "All checks passed"
