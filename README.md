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
- `generated/`: Local-only output of `make generate-example` (a full example project for manual/CI-less sanity checks, e.g. before verifying template changes against `make validate` per `CONTRIBUTING.md`). Gitignored, not committed -- regenerate it locally rather than relying on a checked-in copy; see "Generated Project Features" below for what it contains.
- `tools/`: Operational scripts and wrappers.
- `mission.yaml`, `policy.yaml`, `workflow.yaml` (repo root): This repo's own self-hosted governance files, risk_tier `low` (static scaffolding, no gating authority).
- `SECURITY.md`, `LICENSE`, `CONTRIBUTING.md`, `NOTICE.md`, `CODEOWNERS` (repo root): Required by `SecEng-PROrchestrator`'s documentation gate (`REQUIRED_FILES`). `LICENSE` is MIT. `NOTICE.md` carries this program's ORPHEUS attribution boilerplate. Distinct from anything shipped inside `templates/python-secure/` -- generated projects do not currently receive their own copies of these.
- `tests/`: Real unit tests for `TemplateGenerator` itself (this repo's own generation logic). Run with `make test`. Distinct from `templates/python-secure/tests/`, which ships to every generated project and now asserts real governance-file structure instead of `assertTrue(True)`.
- `.github/workflows/security-scan.yml`: Gitleaks (secret scanning) and Semgrep (SAST, `p/default` ruleset) run on every push/PR against this repo; fails on any Gitleaks hit or ERROR-severity Semgrep finding.
- `templates/python-secure/.github/workflows/seceng-gate.yml`: now also runs Gitleaks and Semgrep in every generated project, matching this repo's own MVP-scope claim of "embedded security checks."
- `.github/workflows/validate.yml`: `lint` (`make lint`, Ruff -- this repo's own root lint tooling;
  the generated Python template's own `make lint` still uses flake8, see MVP Scope above) and `test`
  (`make test`). No `self-check` job here -- this repo is on the public-release track, and
  `self-check` depended on a private GitHub App token and on checking out a private sibling repo
  (SecEng-Contracts), neither of which belongs in a public repo's CI (see `SecEng-Harness`'s
  DESIGN_DECISIONS.md 2026-07-06 entry, "Remove self-check from public CI"). The equivalent
  cross-repo validation this repo's own maintainer relies on is `make check` (see "Checking a Real
  Change" below), run manually/privately rather than as a public CI gate.

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

Or run `make generate-example` for a ready-made Python example at `./generated/example-secure-app` (gitignored, local-only -- see "Repository Layout" above).

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
- Contracts compatibility: `contracts-v1` (see `SecEng-Contracts`' own Versioning and Compatibility
  Policy for what a MAJOR/MINOR/PATCH bump on that tag means for this repo).

## Checking a Real Change (`make check`)

`make check` runs `SecEng-VSCodeAgent`'s full evaluate pipeline (Harness + PolicyEngine +
DevilsAdvocate) against this repo itself (not a generated project). It only means something if
`recommendation.yaml` (repo root, gitignored) describes the actual change you're proposing -- copy
`recommendation.yaml.example` to `recommendation.yaml` and fill in real claims/evidence/alternatives
before running it. Without a real `recommendation.yaml`, DevilsAdvocate falls back to its own
generic example recommendation and will predictably report `fail` regardless of what you actually
did -- that fallback isn't a signal about your change, it's a reminder to write the file first.
`make check` is informational only (not wired into a hook or CI gate yet); read the printed run
bundle path for the full evidence/decision log. `SecEng-VSCodeAgent` (the orchestrator this target
calls) is private, so `make check` won't run out of the box for an external fork -- it documents
the author's own real usage habit and the evaluate pipeline's actual behavior; build an equivalent
orchestrator against your own fork of the sibling repos to reproduce it.

## Status

- MVP complete: Python, Rust, and Terraform (IaC) secure template generators, each with a
  governance-file validation test written in its own language, real generator tests (8 tests),
  self-hosted governance files, and CI (lint, test) running for real.
- Next planned capability: template versioning and upgrade paths (see MVP Scope above).
