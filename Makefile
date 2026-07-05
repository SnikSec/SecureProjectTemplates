PYTHON ?= python

.PHONY: install generate-example test lint

install:
	$(PYTHON) -m pip install -r requirements.txt

generate-example:
	$(PYTHON) tools/generate.py generate --language python --project-name example-secure-project --output-dir ./generated-example

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

lint:
	$(PYTHON) -m flake8 src/
