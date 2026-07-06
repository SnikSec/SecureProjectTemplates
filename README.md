# SecEng-CoreTemplates

Purpose:
- Generate secure project scaffolding for Python, Rust, and IaC repositories.
- Bake in governance controls as required CI jobs (Harness, PolicyEngine, DevilsAdvocate).
- Provide baseline security configuration for all SecEng child repos.

## MVP Scope

This bootstrap MVP focuses on:
- Python, Rust, and Terraform (IaC) secure template generators.
- Every template includes mission.yaml, workflow.yaml, policy.yaml.
- Generated .github/workflows with embedded security checks.
- Makefile with validate, test, lint targets wired to governance tools (language-appropriate
  commands per template: `pip`/`flake8`/`unittest` for Python, `cargo` for Rust, `terraform` for IaC).

Planned next capabilities:
- Template versioning and upgrade paths.

## Repository Layout

- `src/seceng_templates/`: Python package for template generation logic and CLI. Language-agnostic:
  adding a new language template requires no code changes here beyond the CLI's `--language`
  choices list, unless the language needs an extra project-name substitution target (see
  `_update_metadata`'s file list -- `Cargo.toml` for Rust, `variables.tf` for Terraform, alongside
  the universal mission.yaml/policy.yaml/workflow.yaml/README.md).
- `templates/python-secure/`: Reference Python template (its own mission.yaml/policy.yaml/workflow.yaml are scaffold content shipped to generated projects, not this repo's self-hosting files).
- `templates/rust-secure/`: Reference Rust template (Cargo.toml, src/main.rs, and a
  `tests/governance_files.rs` integration test using `serde_yaml` to validate the governance files
  -- a Rust equivalent of `templates/python-secure/tests/test_template.py`, so a generated Rust
  project has no Python dependency).
- `templates/terraform-secure/`: Reference Terraform (IaC) template. `main.tf` intentionally
  provisions nothing (no resources, no provider requirement) until real infrastructure is added;
  `variables.tf`/`outputs.tf` expose the governance files' key fields so
  `tests/governance_files.tftest.hcl` (Terraform's native `terraform test` framework, 1.6+) can
  assert on them via `output.*` references.
- `tools/`: Operational scripts and wrappers.
- `mission.yaml`, `policy.yaml`, `workflow.yaml` (repo root): This repo's own self-hosted governance files, risk_tier `low` (static scaffolding, no gating authority).
- `SECURITY.md`, `LICENSE`, `CONTRIBUTING.md` (repo root): Required by `SecEng-PROrchestrator`'s documentation gate (`REQUIRED_FILES`). `LICENSE` is MIT. Distinct from anything shipped inside `templates/python-secure/` -- generated projects do not currently receive their own copies of these.
- `tests/`: Real unit tests for `TemplateGenerator` itself (this repo's own generation logic). Run with `make test`. Distinct from `templates/python-secure/tests/`, which ships to every generated project and now asserts real governance-file structure instead of `assertTrue(True)`.
- `.github/workflows/security-scan.yml`: Gitleaks (secret scanning) and Semgrep (SAST, `p/default` ruleset) run on every push/PR against this repo; fails on any Gitleaks hit or ERROR-severity Semgrep finding.
- `templates/python-secure/.github/workflows/seceng-gate.yml`: now also runs Gitleaks and Semgrep in every generated project, matching this repo's own MVP-scope claim of "embedded security checks."
- `.github/workflows/validate.yml`: `lint` (`make lint`, flake8), `test` (`make test`), and `self-check` (Harness validates this repo's own mission.yaml, plus an informational PolicyEngine decision). **Requires a GitHub App installed on SnikSec/SecEng-Harness, SecEng-PolicyEngine, and SecEng-Contracts** (Contents: Read-only) with `SIBLING_APPS_APP_ID` / `SIBLING_APPS_PRIVATE_KEY` secrets — see SecEng-Harness's README for the same note.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Generate a project (`--language` is `python`, `rust`, or `terraform`):

```bash
python tools/generate.py generate --language python --project-name my-secure-project --output-dir ./my-project
python tools/generate.py generate --language rust --project-name my-secure-rust-project --output-dir ./my-project
python tools/generate.py generate --language terraform --project-name my-secure-iac-project --output-dir ./my-project
```

3. Navigate to generated project and run validation:

```bash
cd my-project
make validate
```

## Generated Project Features

- Pre-wired mission.yaml for scope enforcement.
- Pre-wired policy.yaml for risk-tier gating.
- CI workflow that runs Harness validation, PolicyEngine gating, and DevilsAdvocate challenges.
- Makefile with targets: install, lint, test, validate (language-appropriate commands per template).
- Python: requirements.txt with security baselines. Rust: Cargo.toml. Terraform: versions.tf pinning
  the minimum Terraform version.

## Contracts and Tool Dependency

- References `../SecEng-Contracts/schemas/` for mission and policy validation.
- Expects `../SecEng-Harness/`, `../SecEng-PolicyEngine/`, `../SecEng-DevilsAdvocate/` as sibling repos for CI integration.

## Status

- Bootstrap created as part of execution-plan step from the strategy repo.
