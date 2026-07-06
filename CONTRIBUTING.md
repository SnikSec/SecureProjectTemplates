# Contributing

## Current Status

This repo is part of a personal security-engineering research portfolio (the SecEng program),
currently solo-authored and privately hosted. There is no formal external-contributor workflow yet
-- issues and pull requests are welcome for discussion, but expect a slower, informal review process
rather than a maintained open-source project's usual cadence.

## Before Opening a Pull Request

- Run `make lint` (flake8) and `make test` locally; both must pass.
- If your change alters behavior, architecture, tooling, or component boundaries, update
  `README.md` and `DESIGN_DECISIONS.md` as part of the same change -- see `AGENTS.md` for why this
  matters here specifically.
- `DESIGN_DECISIONS.md` is a changelog: add a new dated entry, don't rewrite past ones, even to
  correct something.
- Changes to `templates/python-secure/` affect every project this repo generates going forward --
  if you change its governance files or CI wiring, verify the generated output still passes its own
  `make validate` end to end, not just this repo's own tests.

## Reporting Vulnerabilities

Do not open a public issue for a security vulnerability -- see `SECURITY.md` for the private
reporting process.

## Code Style

- Python, `flake8` with `max-line-length = 100` (see `.flake8`).
- Tests use `unittest`, not `pytest`.
