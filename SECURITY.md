# Security Policy

## Scope

SecureProjectTemplates generates secure project scaffolding (Python today; Rust and IaC planned) with
governance controls baked in as required CI jobs. It is part of a personal security-engineering
research portfolio (the SecEng program), not a production service with an SLA. Real
vulnerabilities are still worth reporting; this repo is just not a monitored production system.

## Supported Versions

There is one active line of development: the `dev` branch. No tagged releases exist yet, so there
is nothing older to backport fixes to.

## Reporting a Vulnerability

Please use GitHub's private vulnerability reporting for this repository (Security tab -> "Report a
vulnerability") rather than opening a public issue, so a real finding isn't disclosed before a fix
lands. If that isn't available to you, open an issue with as little sensitive detail as possible
and ask for a private channel.

Do not include exploit code or real secrets in a public issue or PR.

## What to Expect

This is maintained by one person as research/portfolio work, not a funded security team -- there is
no guaranteed response time or bug bounty. Reports will be reviewed and, if valid, addressed on a
best-effort basis.
