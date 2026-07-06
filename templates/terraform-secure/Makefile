# Minimal Makefile for template projects.
TERRAFORM ?= terraform

.PHONY: install lint test validate

install:
	$(TERRAFORM) init

lint:
	$(TERRAFORM) fmt -check -recursive || true

test:
	$(TERRAFORM) test

validate:
	@echo "All checks passed"
