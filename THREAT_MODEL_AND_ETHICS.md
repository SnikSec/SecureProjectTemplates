# Threat Model and Ethics Summary

Status: v0.1
Date: 2026-07-06

This follows the posture and structure established in `SecEng-Strategy`'s portfolio-wide
`SAFETY_AND_ETHICS_BASELINE.md` and `IDENTITY_AND_AGENT_TRUST_MODEL.md`, specialized to what this
repo actually does and actually processes -- not a generic template.

## What This Tool Does

Generates secure project scaffolding for Python, Rust, and Terraform (IaC) projects: pre-wired
`mission.yaml`/`policy.yaml`/`workflow.yaml`, a CI gate that runs Harness/PolicyEngine/DevilsAdvocate
checks plus Gitleaks/Semgrep scanning, and language-appropriate `Makefile` targets.

## Threat Model

### Assets
- The generated project's initial security posture -- everything a new project inherits from its
  template on day one, before a human has reviewed anything.
- The generator's own source templates (`templates/*-secure/`) -- a compromised or subtly-weakened
  template propagates to every project generated from it afterward.

### Trust Boundaries
- `--project-name` and `--output-dir` are local CLI arguments; no network input, no untrusted
  third-party content parsed.
- The templates themselves are static content authored and reviewed as part of this repo -- a
  generated project inherits exactly what's in `templates/`, verbatim plus name substitution.

### Threats Considered
- **Amplification risk unique to a generator tool**: unlike the other three tools (which evaluate
  one target repo at a time), a defect or weakened default here doesn't affect one repo -- it
  affects every project generated from the flawed template going forward, silently, until the
  template is fixed and existing generated projects are manually updated. This is the single most
  important threat this repo's own design has to account for, and it's why `templates/*-secure/`
  content gets the same governance-file validation tests (`tests/governance_files.*`) as any
  self-hosted repo, in each target language natively (Python `unittest`, Rust's own `serde_yaml`
  integration test, Terraform's native `terraform test`) -- not a lighter bar because it's "just a
  template."
- **Silently-inert checks**: a real historical example, disclosed rather than glossed over --
  `templates/python-secure/Makefile`'s `lint` target ran `flake8 src/ || true` while
  `templates/python-secure/requirements.txt` never actually listed `flake8` as a dependency, so
  every generated project's `make lint` silently did nothing (command fails, `|| true` swallows the
  failure) unless a user happened to install it manually. Found and fixed
  (`DESIGN_DECISIONS.md`, 2026-07-06) by making `ruff` a real declared dependency and dropping the
  swallow -- but the general risk (a scaffolded check that looks present but doesn't actually run)
  is exactly the kind of thing worth a second look whenever this repo's Makefiles change.
- **Supply-chain risk in dependencies**, both this repo's own (`PyYAML`) and what it ships into
  generated projects' `requirements.txt`/`Cargo.toml`/`versions.tf` -- mitigated by Gitleaks +
  Semgrep in both this repo's own CI and the generated project's shipped CI gate.

### Out of Scope
- Not a guarantee that a *generated* project stays secure after generation -- this tool controls
  day-one posture only; whatever a human does to a generated project afterward (removing checks,
  weakening policy.yaml, disabling CI) is outside this repo's reach or responsibility.
- Not a code-execution sandbox -- `make generate-example` and the CLI write files to disk; they
  don't execute generated project code as part of generation.

## Ethics Summary

- **Defensive, not offensive**: exists to give every new project a secure-by-default starting point,
  not to demonstrate exploitation.
- **No PII or end-user data processed**: operates on project names/paths and static template
  content, not real user data.
- **No autonomous write actions beyond its stated job**: writes only to the specified
  `--output-dir`; does not modify this repo's own source or any repo other than the one being
  generated.
- **Known limitation, disclosed rather than hidden**: the amplification risk above is structural to
  what a generator tool *is* -- the mitigation (native per-language governance-file tests, real CI)
  reduces but does not eliminate it; a human reviewing template changes before they ship remains the
  actual backstop, matching `SAFETY_AND_ETHICS_BASELINE.md`'s "preserve human decision rights"
  principle for exactly this kind of leveraged, hard-to-reverse change.
