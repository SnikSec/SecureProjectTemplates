# Example-Secure-App

Secure Python project scaffolded by SecEng-CoreTemplates.

## Project Structure

- `src/`: Application source code.
- `tests/`: Unit and integration tests.
- `mission.yaml`: Project mission, scope, and boundaries.
- `workflow.yaml`: CI/CD workflow definition.
- `policy.yaml`: Governance and approval rules.
- `Makefile`: Build, test, and validation targets.
- `.github/workflows/`: GitHub Actions CI configuration.

## Quick Start

```bash
make install
make test
make validate
```

## Governance

This project is governed by SecEng controls:
- Harness validates mission alignment.
- PolicyEngine enforces risk-tier gating.
- DevilsAdvocate challenges recommendations.

All changes must pass these gates before merge.
