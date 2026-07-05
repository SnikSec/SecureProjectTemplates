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
