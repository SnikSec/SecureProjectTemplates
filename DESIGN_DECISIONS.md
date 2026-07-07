# DESIGN_DECISIONS

Some entries below cite `SecEng-Strategy/EXECUTION_PLAN.md`, an internal planning document kept in
a private companion repo -- those citations won't resolve for external readers. The substantive
rationale each citation points to is restated inline in the entry itself; the citation is there for
this program's own cross-repo traceability, not as a required external reference.

## 2026-07-07 - Fix the shipped seceng-gate.yml: it never actually worked against private siblings
- Status: accepted
- Area: governance
- Decision: All three templates' (python-secure, rust-secure, terraform-secure) `seceng-gate.yml` --
  plus the already-generated `generated/example-secure-app/` copy -- had three real bugs, found
  while auditing the portfolio for public-release readiness: (1) `repository: SecEng-Harness` (and
  PolicyEngine/DevilsAdvocate) had no org prefix and no auth token, so the checkout step would fail
  outright against a private sibling repo -- the same class of bug already found and fixed in
  AlignmentHarness/ComplianceRunner's own CI; (2) `policy-gate` hardcoded `--risk-tier low`
  regardless of the generated project's actual declared risk_tier in its own mission.yaml; (3)
  `devils-advocate` never called `challenge.py` at all -- it was a no-op `echo` string. Fixed all
  three: added `create-github-app-token` minting (same `SIBLING_APPS_APP_ID`/
  `SIBLING_APPS_PRIVATE_KEY` secrets pattern used elsewhere) with org-prefixed checkouts, added a
  step that reads the real `risk_tier` out of `mission.yaml` and feeds it to `policy-gate`, and
  wired `devils-advocate` to actually run `challenge.py` against the project's own
  `recommendation.yaml` (falling back to DevilsAdvocate's example, same as `make check` elsewhere).
  Also picked up the `gitleaks` job's missing `pull-requests: read` permission, the same fix already
  applied across the other repos' `security-scan.yml`.
- Why: This is the flagship "help others bootstrap governed AI-assisted projects" artifact --
  shipping it with a CI gate that silently no-ops or fails on first use would undercut the entire
  portfolio's credibility the moment someone actually tried it, which nothing had verified until
  now.
- Alternatives considered: Leaving the stale gate and just documenting the gap in a TODO (rejected
  -- these are mechanical, already-solved-elsewhere bugs, not open design questions; fixing them is
  the same amount of work as writing them up); regenerating `generated/example-secure-app/` from
  scratch instead of patching its copy directly (rejected -- the fix is identical either way, and
  patching in place avoids re-running the generator for a one-file change).
- Tradeoffs: `rust-secure`'s corresponding `cargo build/test/clippy` path has still never been run
  end-to-end on this machine (no Rust toolchain available) -- the YAML-level bugs are fixed, but
  full verification of that template's CI remains open.
- Affected components: `templates/python-secure/.github/workflows/seceng-gate.yml`,
  `templates/rust-secure/.github/workflows/seceng-gate.yml`,
  `templates/terraform-secure/.github/workflows/seceng-gate.yml`,
  `generated/example-secure-app/.github/workflows/seceng-gate.yml`.
- Verification: `python -m unittest discover -s tests -p "test_*.py"` -- 8/8 passing, unaffected by
  this change (no test asserted on the old stale content).
- Follow-up: Verify `rust-secure` end-to-end with a real Rust toolchain once one is available on a
  dev machine.

## 2026-07-03 - Bootstrap SecEng-CoreTemplates with Python secure template
- Status: accepted
- Area: architecture
- Decision: Start with Python template that includes pre-wired governance controls and CI workflows.
- Why: Python is fastest to iterate on; baking in checks at template generation time ensures consistency across all child repos.
- Alternatives considered: manual checklist approach or post-generation script.
- Tradeoffs: More scaffolding upfront, but every new project starts secure and aligned with governance.
- External influences / credit: Infrastructure-as-code and secure templates from industry best practices.
- Affected components: Template generator CLI, reference templates, CI workflow generation.
- Follow-up: Add Rust and IaC templates, versioning, and upgrade tooling.

## 2026-07-05 - Self-host mission.yaml, policy.yaml, workflow.yaml at repo root
- Status: accepted
- Area: governance
- Decision: Add root-level mission.yaml, policy.yaml, and workflow.yaml for this repo itself (separate from templates/python-secure/mission.yaml, which is scaffold content shipped to generated projects and still uses the TEMPLATE_PROJECT_NAME placeholder). risk_tier is set to low, the lowest of the six repos in this batch, because CoreTemplates produces static scaffold files and does not itself gate, deploy, or process secrets on behalf of other repos.
- Why: EXECUTION_PLAN.md claims a working bootstrap, but the repo had no self-hosted governance files; the task requires each gating-adjacent repo's own risk_tier to reflect its actual blast radius, and CoreTemplates' is lower than PolicyEngine/DevilsAdvocate's.
- Alternatives considered: risk_tier medium to match VSCodeAgent (rejected: CoreTemplates has no gating authority and its output is static files a human must still wire into CI).
- Tradeoffs: None significant.
- Affected components: repo root (mission.yaml, policy.yaml, workflow.yaml). Does not touch templates/python-secure/.
- Follow-up: The template's own workflow.yaml (templates/python-secure/workflow.yaml) uses a simplified stage format that predates the full SecEng-Contracts workflow.schema.json; reconcile that template output with the current schema in a follow-up change so generated projects also validate cleanly.

## 2026-07-05 - Bring templates/python-secure/policy.yaml and workflow.yaml into schema conformance
- Status: accepted
- Area: tooling
- Decision: Closed the follow-up noted above. Rewrote `templates/python-secure/policy.yaml` to use policy.schema.json's real shape (permitted_actions/blocked_actions/data_rules/destination_rules/approval_rules instead of an ad hoc `rules: [{action_category, decision}]` list), and `templates/python-secure/workflow.yaml` to use workflow.schema.json's shape (stage_id/name/actor/allowed_actions/stop_conditions instead of `stages: [{name, tasks: [{type, command}]}]`). The literal shell commands the old workflow.yaml encoded per stage (`pip install -r requirements.txt`, `make lint`, etc.) are not part of the schema and were not carried over as schema fields — they already live in the template's own Makefile, which is the executable spec; workflow.yaml is the governance-facing declarative one (what actions a stage may take), not a second place to encode how those actions run. Extended `TemplateGenerator._update_metadata` to substitute `TEMPLATE_PROJECT_NAME` in policy.yaml and workflow.yaml as well as mission.yaml. Added `PyYAML` to the template's requirements.txt since the new tests parse these files. Regenerated `generated/example-secure-app` via the actual CLI to keep it in sync, and re-validated all three of its governance files against the live SecEng-Contracts schemas (VALID).
- Why: Writing a real (non-placeholder) test for the template's governance files required deciding what "correct" means for them; the honest answer was to make the shipped files actually conform to the schema they claim to implement, not to write a test that only re-describes the stale ad hoc format.
- Alternatives considered: Leave the old format and write tests against it (rejected: would encode the gap as permanent behavior instead of closing it, and the CLI-embedded `command:` strings were never machine-executed by anything — the actual Makefile is what runs).
- Tradeoffs: Regenerating `generated/example-secure-app` also touched stale `.seceng/evaluations/*.json` run artifacts that had been committed under both `templates/python-secure/.seceng/` and `generated/example-secure-app/.seceng/`; that churn was reverted (`git checkout --`) as unrelated to this change and left for a separate hygiene pass.
- Affected components: templates/python-secure/policy.yaml, templates/python-secure/workflow.yaml, templates/python-secure/requirements.txt, src/seceng_templates/generator.py, generated/example-secure-app/.
- Follow-up: Decide whether `templates/python-secure/.seceng/evaluations/*.json` (stray committed run artifacts) should be removed and gitignored; out of scope for this change.

## 2026-07-05 - Replace assertTrue(True) placeholder with real governance-file tests; add generator tests
- Status: accepted
- Area: tooling
- Decision: Replaced `templates/python-secure/tests/test_template.py`'s single `assertTrue(True)` test with real assertions that mission.yaml/policy.yaml/workflow.yaml carry their schema-required fields, that risk_tier is a valid enum value, and that the `TEMPLATE_PROJECT_NAME` placeholder was actually substituted. This file ships to every generated project, so it is the test suite a new SecEng child repo starts with. The substitution checks skip (via `unittest.skipTest`, not a hardcoded pass) rather than fail when run directly against the un-substituted template source itself, since substitution only happens at generation time; verified both contexts: 8 passed / 0 skipped when run inside `generated/example-secure-app`, 5 passed / 3 skipped when run inside `templates/python-secure` directly. Also added this repo's own `tests/test_generator.py`, testing `TemplateGenerator.validate()`/`.generate()` directly (known vs. unknown language, governance files created, placeholder substitution, and that regenerating an existing project directory overwrites stray files rather than merging with them). Added `test` Makefile targets to both this repo and (implicitly, already present) the template.
- Why: `assertTrue(True)` is not a test — it cannot fail, so a generated project's CI would report a passing test suite regardless of whether generation actually worked. This repo itself also had zero tests of its own generation logic.
- Alternatives considered: Testing only via the CLI subprocess layer (rejected: direct unit tests of `TemplateGenerator` are faster and pinpoint failures more precisely; the CLI is already exercised manually via `make generate-example`); letting the substitution checks fail outright when run against raw template source (rejected: that would make `make test` inside `templates/python-secure/` itself look broken, when un-substituted placeholders there are correct, expected state).
- Tradeoffs: None significant.
- Affected components: templates/python-secure/tests/test_template.py, tests/ (new), Makefile.
- Follow-up: Wire `make test` into CI for both this repo and generated projects' own CI workflow (portfolio task step 4).

## 2026-07-05 - Add real security scanning: Gitleaks + Semgrep (this repo and generated projects)
- Status: accepted
- Area: tooling
- Decision: Two separate changes. (1) This repo's own `.github/workflows/security-scan.yml`: a `gitleaks` job (`gitleaks/gitleaks-action@v2`, `fetch-depth: 0`) and a `semgrep` job (`semgrep scan --config=p/default --severity=ERROR --error`). Added a `security-scan` stage (stage-004) to this repo's own root workflow.yaml. (2) `templates/python-secure/.github/workflows/seceng-gate.yml` (the CI file shipped to every generated project) gained the same two jobs, since this repo's own README/MVP-scope already claimed "Generated .github/workflows with embedded security checks" — a claim that was not actually true before this change (the shipped gate only ran harness/policy/devils-advocate jobs, no scanning at all). Regenerated `generated/example-secure-app` to pick up the updated gate file.
- Why: Closing the claims-vs-reality gap this whole session is about — this repo's own documentation asserted security checks were already baked into generated projects, and they were not.
- Alternatives considered: Only adding scanning to this repo's own CI and leaving the template gate as a separate follow-up (rejected: the template gate was the more consequential gap, since every future generated project inherits it, and the fix was small enough to do in the same pass).
- Tradeoffs: None significant.
- Affected components: .github/workflows/security-scan.yml (new, this repo), templates/python-secure/.github/workflows/seceng-gate.yml, workflow.yaml (this repo's root), generated/example-secure-app/.
- Verification: Ran `semgrep scan --config=p/default --severity=ERROR --error` (isolated venv) against this repo directly: 0 findings, exit code 0. Confirmed the same command/flags exit 1 against a deliberately vulnerable scratch file. Re-validated generated/example-secure-app's mission.yaml/policy.yaml/workflow.yaml against live SecEng-Contracts schemas after regeneration (still VALID). Gitleaks itself was not executed locally (binary execution from a self-chosen download was blocked by this session's safeguards); relying on the official action's documented behavior instead.
- Follow-up: Wire security-scan into the same CI surface as lint/test/self-check for this repo (portfolio task step 4).

## 2026-07-05 - Add lint job and CI parity: .github/workflows/validate.yml (lint, test, harness/policy self-check)
- Status: accepted
- Area: tooling
- Decision: Added `flake8==7.1.1` to requirements.txt, a `.flake8` config (`max-line-length = 100`, excluding `templates/` and `generated/` since those are shipped/generated content, not this repo's own source), and a `make lint` target. Fixed the real findings flake8 turned up in this repo's own `src/` (an f-string with no placeholders, and two unused `typing` imports in generator.py). Added `.github/workflows/validate.yml` with `lint`, `test`, and `self-check` jobs, following the same pattern as the other three repos in this batch (see SecEng-Harness's matching 2026-07-05 entry for the full GitHub App rationale).
- Why: Same as the other three repos in this batch -- closing the CI-parity gap and giving this repo the same lint/test/self-check coverage as its siblings.
- Alternatives considered: same as SecEng-Harness's matching entry.
- Tradeoffs: The self-check job cannot pass in CI until the GitHub App is actually provisioned. Excluding `templates/` from lint means the reference template's own `src/` is not style-checked by this repo's CI; acceptable since the template is scaffold content copied verbatim into generated projects, not code this repo executes directly.
- Affected components: requirements.txt, .flake8 (new), Makefile, src/seceng_templates/cli.py and generator.py (unused import/f-string fixes, no behavior change), .github/workflows/validate.yml (new).
- Verification: `flake8 src/` (isolated venv): 0 findings after the fix (was 3 before). `python -m unittest discover -s tests` (this repo's own generator tests): still 6/6 passing. Simulated the self-check job's directory layout locally and applied the same `--schema` fix documented in SecEng-Harness's DESIGN_DECISIONS.md. Confirmed VALID + NO DRIFT against this repo's own mission.yaml.
- Follow-up: Once the GitHub App is provisioned, re-run this workflow for real and confirm the self-check job goes green end-to-end.

## 2026-07-05 - Fix corrupted SIBLING_APPS_PRIVATE_KEY secret
- Status: accepted
- Area: tooling
- Decision: Same incident and fix as documented in full in SecEng-Harness's matching 2026-07-05 entry: the private key secret, pasted by hand into the GitHub UI, was corrupted and caused `error:1E08010C:DECODER routines::unsupported` when minting the sibling-repo token. Re-set via `gh secret set SIBLING_APPS_PRIVATE_KEY --repo SnikSec/SecEng-CoreTemplates < path/to/key.pem` (piping the file directly, no manual paste).
- Affected components: `SIBLING_APPS_PRIVATE_KEY` secret.
- Verification: `gh run rerun --failed` after the fix: `self-check` passes, with real `VALID`/`NO DRIFT` output and an informational `DECISION: ALLOW`.
- Follow-up: If this key is ever rotated, always use `gh secret set ... < file`, never paste manually -- see SecEng-Harness's DESIGN_DECISIONS.md for the full reasoning.

## 2026-07-06 - Add SECURITY.md (documentation gate expansion, option E)
- Status: accepted
- Area: governance
- Decision: Added a real root-level `SECURITY.md` (scope, supported-versions, GitHub private-vulnerability-reporting instructions, best-effort expectations note). Full rationale for why `SECURITY.md` specifically, and for expanding `SecEng-PROrchestrator`'s `REQUIRED_FILES` to include it, is recorded in `SecEng-PROrchestrator/DESIGN_DECISIONS.md` (2026-07-06 entry) rather than duplicated here. This repo's own root `SECURITY.md` is distinct from `templates/python-secure/`, which does not currently ship a `SECURITY.md` to generated projects.
- Why: This repo's documentation gate compliance now depends on it; adding the file was the mechanical half of that portfolio-wide decision.
- Affected components: SECURITY.md (new, repo root), README.md (Repository Layout bullet).
- Verification: `python tools/orchestrator.py analyze --root-path <portfolio>` (from SecEng-PROrchestrator) reports this repo as `ready`.
- Follow-up: Whether generated projects (`templates/python-secure/`) should also get a `SECURITY.md` template file is a separate, not-yet-decided question -- this change only covers this repo's own root governance files, not what it generates.

## 2026-07-06 - Add LICENSE and CONTRIBUTING.md (documentation gate expansion, repeat of option E)
- Status: accepted
- Area: governance
- Decision: Added a root-level `LICENSE` (MIT, copyright SnikSec) and `CONTRIBUTING.md` (current-status note, pre-PR checklist pointing at `make lint`/`make test`/README+DESIGN_DECISIONS discipline, a pointer to SECURITY.md for vulnerability reports, plus a note that changes to `templates/python-secure/` should be verified against the generated project's own `make validate`). Full rationale for repeating the SECURITY.md pattern with these two files together, and for expanding `SecEng-PROrchestrator`'s `REQUIRED_FILES` to include them, is recorded in `SecEng-PROrchestrator/DESIGN_DECISIONS.md` (2026-07-06 entry) rather than duplicated here. Same as the SECURITY.md entry above, these are this repo's own root files, distinct from anything shipped inside `templates/python-secure/`.
- Why: This repo's documentation gate compliance now depends on it; adding the files was the mechanical half of that portfolio-wide decision.
- Affected components: LICENSE (new, repo root), CONTRIBUTING.md (new, repo root), README.md (Repository Layout bullet).
- Verification: `python tools/orchestrator.py analyze --root-path <portfolio>` (from SecEng-PROrchestrator) reports this repo as `ready`.
- Follow-up: Same open question as the SECURITY.md entry above -- whether generated projects should also receive their own LICENSE/CONTRIBUTING.md is not yet decided.

## 2026-07-06 - Add Rust and Terraform (IaC) secure templates (EXECUTION_PLAN.md Section 10, option D)
- Status: accepted
- Area: architecture
- Decision: Added `templates/rust-secure/` and `templates/terraform-secure/`, following the exact same structural pattern as `templates/python-secure/`: identical `mission.yaml`/`policy.yaml`/`workflow.yaml` content (only the `TEMPLATE_PROJECT_NAME` placeholder differs at generation time), an identical `.github/workflows/seceng-gate.yml` copied byte-for-byte (it checks out and invokes the sibling Harness/PolicyEngine/DevilsAdvocate repos' own Python tooling, plus Gitleaks/Semgrep -- none of it touches the generated project's own toolchain, so it's genuinely language-agnostic and needed no changes), and a Makefile with the same four targets (`install`/`lint`/`test`/`validate`) using language-appropriate commands (`cargo fetch`/`cargo clippy`/`cargo test` for Rust; `terraform init`/`terraform fmt -check`/`terraform test` for Terraform). `TemplateGenerator`/`generate()` needed zero code changes (already language-agnostic by design, per the existing `{language}-secure` directory convention); `_update_metadata`'s substitution file list gained two entries -- `Cargo.toml` (Rust's package `name` field) and `variables.tf` (Terraform's `project_name` variable default) -- since those are real, necessary substitutions (an un-substituted `Cargo.toml` would be a broken crate name, not cosmetic), not template content. The CLI's `--language` choices grew from `["python"]` to `["python", "rust", "terraform"]`.
- Why (governance-file test written natively per language, not shared Python): `templates/python-secure/tests/test_template.py` validates the shipped governance files (required fields, valid risk_tier enum, placeholder substitution) using Python's `unittest` + `PyYAML`. Shipping that same Python test file into a Rust or Terraform project would mean a generated project in one language carries a dependency on a different language's toolchain just to check three YAML files -- inconsistent with the template being a genuine, self-contained `{language}` project. Instead: Rust got `tests/governance_files.rs`, a real Rust integration test using `serde_yaml` (added under `[dev-dependencies]` in `Cargo.toml`, not `[dependencies]`, since it's only needed for this test); Terraform got `tests/governance_files.tftest.hcl`, using Terraform's own native test framework (`terraform test`, available since 1.6) via `main.tf`'s `locals` (`yamldecode(file(...))`, a built-in Terraform function since 0.14) and `outputs.tf` exposing the fields tests need to assert on.
- Why (Terraform's test omits the placeholder-substitution check that Python's and Rust's have): Python's `unittest` has `self.skipTest(...)` and Rust's test can simply `return` early, so both can conditionally skip the "was TEMPLATE_PROJECT_NAME actually replaced" assertion when run directly against the un-substituted template source (rather than a generated project) without that being a real failure. Terraform's `run` blocks in a `.tftest.hcl` file have no equivalent per-test skip mechanism -- omitting this one check was the honest choice, documented in the test file itself, rather than writing an assertion that would always fail against the template source or a fake one that always trivially passes.
- Why (Terraform's `main.tf` provisions nothing): This is a scaffold for a project that doesn't exist yet; declaring real cloud resources would require picking a specific provider and (for anything beyond local-only resources) real credentials, neither of which this template can assume. An empty root module with no `provider` block means `terraform init`/`validate`/`test` all work with zero external dependencies or credentials -- verified for real, not just written and assumed (see Verification below).
- Alternatives considered: Writing the Rust/Terraform governance-file checks as a shared script invoked by both (e.g. a small Python script both Makefiles call) (rejected: reintroduces the same cross-language dependency problem `_update_metadata`'s language-agnostic design was trying to avoid, just moved into the Makefile instead of `tests/`); using Jinja2 templating instead of the existing plain-`.replace()` substitution mechanism, since Jinja2 is already a listed (but unused) dependency in requirements.txt (rejected: the existing substitution mechanism already works correctly for all three languages with only two additional filenames added to a fixed list -- introducing a templating engine is a larger, unnecessary change with no problem it would actually solve here); giving Rust's template a real cloud-facing dependency or IaC-style resource (rejected: out of scope -- this is a language scaffold, not a worked infrastructure example).
- Tradeoffs: None significant.
- Affected components: `templates/rust-secure/` (new: mission.yaml, policy.yaml, workflow.yaml, Cargo.toml, src/main.rs, tests/governance_files.rs, Makefile, README.md, .gitignore, .github/workflows/seceng-gate.yml), `templates/terraform-secure/` (new: mission.yaml, policy.yaml, workflow.yaml, versions.tf, variables.tf, main.tf, outputs.tf, tests/governance_files.tftest.hcl, Makefile, README.md, .gitignore, .github/workflows/seceng-gate.yml), `src/seceng_templates/generator.py` (`_update_metadata`'s substitution file list), `src/seceng_templates/cli.py` (`--language` choices), `tests/test_generator.py` (extended to cover all three languages: template-exists check, governance-file-creation check, and new Cargo.toml/variables.tf substitution tests), `templates/python-secure/Makefile` (see the entry below -- a real bug fixed incidentally while using this file as the pattern to copy).
- Verification: `python -m unittest discover -s tests -p "test_*.py"`: 8/8 passing (2 new). flake8 clean. Generated a real project for each new language via the actual CLI (`python tools/generate.py generate --language rust/terraform ...`) into a scratch directory and confirmed correct file structure and placeholder substitution (`Cargo.toml`'s `name`, `variables.tf`'s `default`, plus the universal mission/policy/workflow/README) for both. For Terraform specifically (the real `terraform` 1.14.9 binary is installed on this dev machine): ran `terraform init`, `terraform fmt -check -recursive`, `terraform validate`, and `terraform test` against both the raw template source and the generated project -- all passed for real, including all 3 `run` blocks in `governance_files.tftest.hcl` (3 passed, 0 failed). For Rust: `rustc`/`cargo` are not installed on this dev machine, so `cargo build`/`cargo test`/`cargo clippy` were not run for real -- the Rust source was written and reviewed carefully by hand instead (same disclosed-limitation pattern as this repo's Gitleaks verification, which also could not be run locally). Test-created scratch directories and `.terraform`/`.terraform.lock.hcl` init artifacts were deleted after verification.
- Follow-up: Rust's `cargo build`/`test`/`clippy` have not been executed for real on this machine -- if/when a Rust toolchain becomes available, re-verify `templates/rust-secure/` end-to-end the same way Terraform was. Template versioning and upgrade paths (the repo's last remaining "planned next capability") is still open.

## 2026-07-06 - Fix a real Makefile bug in templates/python-secure: a Python-style docstring where a Make comment belongs
- Status: accepted
- Area: tooling
- Decision: `templates/python-secure/Makefile`'s first line was `"""Minimal Makefile for template projects."""` -- valid Python docstring syntax, but not a Make comment (Make only recognizes `#`). Running any target (`make validate`, `make test`, etc.) against this file failed immediately with `Makefile:1: *** missing separator. Stop.` before ever reaching a real target. Fixed by replacing the line with `# Minimal Makefile for template projects.`
- Why: Found while using this exact file as the pattern to copy for the new Rust and Terraform templates' own Makefiles (see the entry above) -- running `make -n validate` against the existing Python template to confirm the pattern actually worked surfaced this immediately. Every Python project this generator has ever produced has had a Makefile that couldn't run a single target.
- Alternatives considered: None -- this is an unambiguous syntax error with one obvious fix, not a design decision.
- Tradeoffs: None significant.
- Affected components: `templates/python-secure/Makefile` (one line).
- Verification: `make -n install/lint/test/validate` against the template all correctly print their real commands after the fix (they errored with "missing separator" before it).
- Follow-up: None open. This was not caught by this repo's own test suite (`tests/test_generator.py`/`templates/python-secure/tests/test_template.py`) because neither actually invokes `make` -- worth considering for a future increment, but out of scope here.

## 2026-07-06 - Stop tracking generated/example-secure-app; gitignore it and fix the generate-example Makefile drift
- Status: accepted
- Area: tooling
- Decision: Added `/generated/` to `.gitignore` and ran `git rm -r --cached generated/` (files kept on disk, just untracked). Also fixed a real drift bug in the `generate-example` Makefile target: it was running `--project-name example-secure-project --output-dir ./generated-example`, which does not match the directory that had actually been committed (`generated/example-secure-app`) -- `make generate-example` had not reproduced the tracked example in some time. Changed the target to `--project-name example-secure-app --output-dir ./generated`, so it now reliably regenerates the same path the rest of this file's history refers to.
- Why: `generated/example-secure-app` had been committed since the initial portfolio import and was being manually regenerated and recommitted alongside template/schema changes (see the two 2026-07-05 entries above referencing it) as a form of local end-to-end validation that the generator's output stays schema-valid. `CONTRIBUTING.md` already frames this as a *local* check ("verify the generated output still passes its own `make validate`"), the same way `.seceng/runs/` and `.seceng/evaluations/` (gitignored in the `8252703` commit) are local-only artifacts, not curated repo content. Keeping it tracked meant every template change carried an extra regenerate-and-recommit step and public-facing diff noise for output that `make generate-example` can reproduce on demand; the actual public-facing documentation of what a generated project contains already lives in this README's "Generated Project Features" section and does not depend on a committed copy.
- Alternatives considered: Leaving it tracked as a golden-file/snapshot fixture (rejected: it was drifting from what the Makefile actually produced, which defeats the point of a golden file, and the repeated regenerate-recommit churn was exactly the kind of low-value diff noise `.seceng/runs/` was already gitignored to avoid).
- Tradeoffs: Anyone relying on browsing `generated/example-secure-app` directly in the repo (e.g. on GitHub's web UI) now needs to run `make generate-example` locally instead; mitigated by documenting the command in the README's Quick Start and Repository Layout sections.
- Affected components: `.gitignore`, `Makefile` (`generate-example` target), `generated/` (untracked, not deleted from disk), `README.md` (Repository Layout + Quick Start).
- Verification: `python -m unittest discover -s tests -p "test_*.py"` and `flake8 src/` both still pass (neither depended on `generated/` being tracked; `.flake8` already excluded `generated` from linting). Ran `make generate-example` after the Makefile fix and confirmed it produces `generated/example-secure-app` matching the previously-tracked structure, then `cd generated/example-secure-app && make validate` to confirm the local end-to-end check `CONTRIBUTING.md` describes still works.
- Follow-up: None open.

## 2026-07-06 - Migrate this repo's own lint tooling from flake8 to Ruff
- Status: accepted
- Area: tooling
- Decision: Replaced `.flake8` with `ruff.toml` (`line-length = 100`, same `exclude` list including `templates` -- unchanged, this repo's own root lint still does not check the shipped template sources, `.flake8` never did either -- and `[lint] select = ["E", "W", "F"]` to match flake8's default active checks). `requirements.txt`'s `flake8==7.1.1` became `ruff==0.15.20`. The root Makefile's `lint` target changed to `$(PYTHON) -m ruff check src/`. Full rationale for choosing Ruff is recorded in `SecEng-Harness/DESIGN_DECISIONS.md` (2026-07-06 entry). This is this repo's own root tooling only -- `templates/python-secure/`'s shipped Makefile still uses flake8 for generated projects, deliberately untouched (see below).
- Why (the shipped Python template keeps flake8, not migrated to Ruff): The Rust and Terraform templates added earlier today each use their own language's native tooling (`cargo clippy`, `terraform fmt`), not a shared Python linter -- there was never a plan to make every generated project's lint tool match this repo's own. Migrating the *shipped* Python template's lint tool is a separate, optional decision (whether generated projects should also get Ruff) that weighs differently (it changes what every future generated project ships, not just this repo's own CI) and wasn't part of what was asked; left alone.
- Alternatives considered: See Harness's own entry for the Ruff-vs-flake8 tool-choice alternatives; migrating `templates/python-secure/Makefile`'s `lint` target to Ruff too (rejected for this pass per the "why" above -- a decision about generated-project tooling, not this repo's own).
- Tradeoffs: None significant.
- Affected components: `.flake8` (removed), `ruff.toml` (new), `requirements.txt`, `Makefile` (`lint` target), `README.md` (CI description).
- Verification: `ruff check src/` reports 0 findings. Full 8/8 test suite still passes. CI's `lint` job needed no workflow-file change and was verified green on the pushed commit.
- Follow-up: Whether `templates/python-secure/`'s own shipped Makefile should also move to Ruff (affecting every future generated project, not just this repo) is a separate, not-yet-decided question.

## 2026-07-06 - Wire evaluate into a real, non-blocking usage habit (`make check` + `recommendation.yaml`)
- Status: accepted
- Area: architecture
- Decision: Added `recommendation.yaml.example` (documented template for the fields DevilsAdvocate's CLI actually reads: `id`, `claims`, `assumptions`, `evidence`, `alternatives`), `/recommendation.yaml` to `.gitignore` (per-change working draft, not durable history), and a `check` Makefile target (`python ../SecEng-VSCodeAgent/tools/vscode_agent.py evaluate --repo-path .`), plus README/CONTRIBUTING.md sections explaining the workflow. This is for this repo's own root governance, distinct from anything shipped inside `templates/python-secure/`. Full rationale, including real proof this closes an actual gap, is recorded in `SecEng-Harness/DESIGN_DECISIONS.md` (2026-07-06 entry) rather than duplicated here.
- Why: Same portfolio-wide decision as the other five self-hosted repos, prompted directly by a question about whether any of this tooling is actually being used for real decisions rather than just tested.
- Alternatives considered: See Harness's own entry.
- Tradeoffs: None significant.
- Affected components: `recommendation.yaml.example` (new, repo root), `.gitignore`, `Makefile` (`check` target), `README.md`/`CONTRIBUTING.md` (new section; also fixed a stale flake8 reference in CONTRIBUTING.md's "Code Style" section left behind by the earlier Ruff migration).
- Verification: `make -n check` confirmed correct command substitution.
- Follow-up: None open for this repo.

## 2026-07-06 - Expand this repo's own `make lint` to `tests/`, migrate the shipped `templates/python-secure/` template to Ruff too
- Status: accepted
- Area: tooling
- Decision: Two changes in one pass. (1) This repo's own root `Makefile` `lint` target changed from `ruff check src/` to `ruff check src/ tests/` (`ruff check src/ tests/` was already clean beforehand -- see `SecEng-Harness/DESIGN_DECISIONS.md` for the portfolio-wide version of this change, applied identically here). (2) Found while doing that: `templates/python-secure/Makefile`'s `lint` target ran `flake8 src/ || true`, but `templates/python-secure/requirements.txt` never listed `flake8` as a dependency at all -- every project this repo has ever generated had a `make lint` that silently did nothing (flake8 not installed -> command fails -> `|| true` swallows it) unless a user happened to `pip install flake8` manually themselves. Added `ruff==0.15.20` to the template's own `requirements.txt`, added a `ruff.toml` to the template itself (copied into every generated project), and changed the template's Makefile `lint` target to `ruff check src/ tests/` -- dropping the `|| true`, since `ruff` is now a real, declared dependency and a real lint failure should surface, not be silently masked.
- Why (drop `|| true` in the template): The only reason it existed was to paper over flake8 never actually being installed. With a real dependency in place, a lint failure is a real signal a generated project's user should see.
- Alternatives considered: Leaving the shipped template on flake8 (rejected -- this was explicitly asked for: "move all things templates or otherwise to Ruff"); keeping the silent `|| true` fallback for backward compatibility (rejected -- it only ever existed to hide a missing dependency, and only affects projects generated going forward, not already-generated static snapshots).
- Tradeoffs: None significant.
- Affected components: this repo's own `Makefile` (`lint` target), `templates/python-secure/requirements.txt`, `templates/python-secure/ruff.toml` (new), `templates/python-secure/Makefile` (`lint` target).
- Verification: `ruff check src/ tests/` reports 0 findings both for this repo's own root code and for the template source directly. Generated a real project via the actual CLI (`python tools/generate.py generate --language python --project-name demo-lint-check --output-dir <scratch>`) and confirmed `ruff check src/ tests/` (0 findings) and `python -m unittest discover -s tests` (8/8 passing) both work for real inside the generated project -- the first time `make lint` has ever done something real in a generated Python project. Scratch directory deleted after verification. This repo's own 8/8 test suite still passes.
- Follow-up: A separate, unrelated dead dependency was noticed in the same file (`templates/python-secure/requirements.txt`'s `pytest==7.4.0`, never actually used -- the template's own tests run via `unittest`) and flagged as its own small spun-off task rather than fixed here, to keep this change scoped to the lint-tooling migration.

## 2026-07-06 - Remove dead pytest dependency from templates/python-secure/requirements.txt
- Status: accepted
- Area: tooling
- Decision: Removed `pytest==7.4.0` from `templates/python-secure/requirements.txt`. Confirmed via grep across the entire `templates/python-secure/` tree that `pytest` was not imported or invoked anywhere -- the template's own Makefile `test` target runs `python -m unittest discover -s tests`, not pytest.
- Why: Closes the follow-up flagged in the entry above -- every project generated by this template declared a dependency it never used.
- Alternatives considered: None -- this is an unambiguous unused dependency, not a design tradeoff.
- Tradeoffs: None significant.
- Affected components: `templates/python-secure/requirements.txt`.
- Verification: `python -m unittest discover -s tests -p "test_*.py" -v` (this repo's own test suite, which does not reference the template's requirements.txt): 8/8 passing.
- Follow-up: None open.

## 2026-07-06 - Fix a stale README Status section
- Status: accepted
- Area: documentation
- Decision: The "Status" section still read "Bootstrap created as part of execution-plan step from the strategy repo." Rewrote it to state actual current capability (Python/Rust/Terraform generators, each with a governance-file test written in its own language, 8 tests, CI) and the next planned capability (template versioning and upgrade paths).
- Why: Found during a portfolio-wide README audit requested directly.
- Alternatives considered: None -- factual correction.
- Tradeoffs: None significant.
- Affected components: `README.md`.
- Verification: Test count (8) cross-checked against `portfolio_status.py`'s real output before writing.
- Follow-up: None open.

## 2026-07-06 - Add NOTICE.md and CODEOWNERS (documentation gate's third expansion)
- Status: accepted
- Area: governance
- Decision: Authored `NOTICE.md` (ORPHEUS attribution boilerplate, reused verbatim from `SecEng-Strategy/SECENG_AGENTIC_PROGRAM_DRAFT.md` Section 13) and `CODEOWNERS` (`* @SnikSec`) at repo root -- distinct from anything shipped inside `templates/python-secure/` (generated projects do not currently receive their own copies of these). Full rationale for this expansion (part of the user's comprehensive public-release directive covering all seven governed repos) is in `SecEng-PROrchestrator/DESIGN_DECISIONS.md` (2026-07-06 entry, "Expand the documentation gate a third time").
- Why: This repo is one of the four named to go public in that directive; NOTICE.md and CODEOWNERS are both explicitly required before public release.
- Affected components: `NOTICE.md` (new), `CODEOWNERS` (new), `README.md` (Repository Layout bullet).
- Verification: `analyze --root-path <portfolio>` reports this repo `ready` after authoring both files. `make lint`/`make test` unaffected (docs-only change).
- Follow-up: None open for this repo. Branch protection and visibility flip are tracked separately (PROrchestrator's task list).

## 2026-07-06 - Remove self-check from public CI
- Status: accepted
- Area: governance
- Decision: Removed the `self-check` job from `.github/workflows/validate.yml`, keeping `lint` and `test` unchanged. Full rationale (public repos should be self-contained templates, not live dependents of the author's private GitHub App secrets and a still-private sibling repo) is recorded in `SecEng-Harness/DESIGN_DECISIONS.md` (2026-07-06 entry, "Remove self-check from public CI").
- Why: This repo is on the same public-release track as Harness; the same reasoning applies identically. This repo's own `self-check` job was already the same shared pattern (Harness/PolicyEngine/Contracts checkout via the App token), unaffected by this repo's generated-template content.
- Affected components: `.github/workflows/validate.yml` (`self-check` job removed), `README.md` (CI section, Status section).
- Verification: `lint` and `test` confirmed still passing for real in CI after the push, with `self-check` genuinely absent (not skipped).
- Follow-up: None open for this repo.

## 2026-07-06 - Clean up internal-only / dead-link content ahead of public release
- Status: accepted
- Area: documentation
- Decision: Fixed `NOTICE.md`'s dead link to a private Strategy doc (replaced with a self-contained clean-room statement), added a note to `README.md`'s "Checking a Real Change" section that `make check` depends on the private `SecEng-VSCodeAgent` and won't run out of the box for a fork, and added a disclosure note at the top of `DESIGN_DECISIONS.md` about its `EXECUTION_PLAN.md` citations. Full rationale in `SecEng-Harness/DESIGN_DECISIONS.md` (2026-07-06 entry, "Clean up internal-only / dead-link content ahead of public release").
- Why: This repo is on the same public-release track as Harness and carried the identical copied content (`NOTICE.md`, the Makefile `check` target); the same reasoning applies identically. This repo's own `generated/` directory (gitignored since an earlier 2026-07-06 entry) and `templates/python-secure/` were re-checked and confirmed to carry no stray tracked run artifacts either.
- Affected components: `NOTICE.md`, `README.md`, `DESIGN_DECISIONS.md` (header note).
- Verification: Same checks as Harness's entry, run against this repo directly -- no personal paths, no stray tracked run artifacts, `ruff check`/tests unaffected.
- Follow-up: None open for this repo.

## 2026-07-06 - Release tracking: add `__version__`, tag `v0.1.0`, declare `contracts-v1` compatibility
- Status: accepted
- Area: governance
- Decision: This repo's own `src/seceng_templates/__init__.py` had no `__version__` at all despite Harness/PolicyEngine/DevilsAdvocate already carrying one -- added `__version__ = "0.1.0"` for consistency, then tagged this repo's current `dev` HEAD `v0.1.0` to match. Added a "Contracts compatibility: `contracts-v1`" line to the README's "Contracts and Tool Dependency" section. Full rationale in `SecEng-Strategy/DESIGN_DECISIONS.md` (2026-07-06 entry, "Implement release tracking").
- Why: Same portfolio-wide decision as Harness; this repo was also missing both a `__version__` string and a git tag.
- Affected components: `src/seceng_templates/__init__.py` (`__version__`, new), git tag `v0.1.0` (new), `README.md` (Contracts and Tool Dependency section).
- Verification: `python -m unittest discover -s tests -p "test_*.py"` still 8/8 passing after the `__version__` addition. `git tag -l` and `git ls-remote --tags origin` confirm the tag exists locally and pushed.
- Follow-up: None open for this repo.

## 2026-07-06 - Add THREAT_MODEL_AND_ETHICS.md (documentation gate's fourth expansion)
- Status: accepted
- Area: governance
- Decision: Authored a real, repo-specific `THREAT_MODEL_AND_ETHICS.md` -- covering this repo's actual assets (a generated project's initial security posture) and the amplification risk unique to being a generator tool: a defect or weakened default here doesn't affect one repo, it affects every project generated from the flawed template afterward, silently, until fixed. Also documents the real, historical `flake8 src/ || true` silently-inert-check incident (found and fixed 2026-07-06) as a concrete example of this risk, not a hypothetical. Full rationale for the broader expansion is in `SecEng-PROrchestrator/DESIGN_DECISIONS.md` (2026-07-06 entry, "Expand the documentation gate a fourth time").
- Why: Directly named in the user's public-release directive; this repo is one of the four named to go public.
- Affected components: `THREAT_MODEL_AND_ETHICS.md` (new), `README.md` (governance-files bullet).
- Verification: `analyze --root-path <portfolio>` reports this repo `ready` after authoring the file.
- Follow-up: None open for this repo.

## 2026-07-07 - Fix a real bug: gitleaks job missing `pull-requests: read` permission
- Status: accepted
- Area: tooling
- Decision: Same bug and fix as `SecEng-PolicyEngine`'s matching 2026-07-07 entry: the `gitleaks` job in `.github/workflows/security-scan.yml` failed with a 403 calling the PR-commits API on the first-ever `dev`->`main` PR against this repo, since it had no `permissions:` block. Added `permissions: {contents: read, pull-requests: read}`, matching `SecEng-Harness`'s already-correct config. This is the repo where the failure was first actually observed (`gh pr checks` showed `gitleaks: fail` on a re-run after an initial `pass`), which is what prompted checking all three sibling repos and finding they shared the same gap.
- Why: See PolicyEngine's entry -- this had never been caught because CI here was push-only until today.
- Affected components: `.github/workflows/security-scan.yml` (`gitleaks` job `permissions:` block, added).
- Verification: Re-ran the `gitleaks` check on the open PR after pushing the fix; confirmed it passes for real.
- Follow-up: None open for this repo.
