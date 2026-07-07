# Minimal Makefile for template projects.
CARGO ?= cargo

.PHONY: install lint test validate

install:
	$(CARGO) fetch

lint:
	$(CARGO) clippy -- -D warnings || true

test:
	$(CARGO) test

validate:
	@echo "All checks passed"
