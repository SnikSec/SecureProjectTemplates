PYTHON ?= python

.PHONY: install generate-example

install:
	$(PYTHON) -m pip install -r requirements.txt

generate-example:
	$(PYTHON) tools/generate.py generate --language python --project-name example-secure-project --output-dir ./generated-example
