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
