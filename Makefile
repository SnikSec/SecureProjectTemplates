PYTHON ?= python

.PHONY: install generate-example test lint check

install:
	$(PYTHON) -m pip install -r requirements.txt

check:
	$(PYTHON) ../ComplianceRunner/tools/vscode_agent.py evaluate --repo-path .

generate-example:
	$(PYTHON) tools/generate.py generate --language python --project-name example-secure-app --output-dir ./generated

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

lint:
	$(PYTHON) -m ruff check src/ tests/
