# DESIGN_DECISIONS

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
