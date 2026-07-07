# Validates the governance files this template ships (mission.yaml, policy.yaml,
# workflow.yaml) parse as YAML and carry the fields required by SecEng-Contracts'
# schemas. Uses Terraform's native test framework (`terraform test`, 1.6+) via
# outputs.tf's exposed values, since assertions can only reference module
# outputs, not locals directly.
#
# Unlike the Python and Rust template test suites, this file intentionally does
# not check whether TEMPLATE_PROJECT_NAME was substituted -- `run` blocks have
# no per-test skip mechanism the way unittest's skipTest or a Rust early-return
# does, and the placeholder is still present when this test runs against the
# raw template source (before a project is generated), so a real check here
# would always fail against that source.

run "mission_yaml_has_required_fields" {
  command = plan

  assert {
    condition     = output.mission_repo_id != null
    error_message = "mission.yaml is missing repo_id"
  }

  assert {
    condition     = contains(["low", "medium", "high"], output.mission_risk_tier)
    error_message = "mission.yaml risk_tier must be one of low, medium, high"
  }
}

run "policy_yaml_has_required_fields" {
  command = plan

  assert {
    condition     = output.policy_id != null
    error_message = "policy.yaml is missing policy_id"
  }

  assert {
    condition     = output.policy_destination_rules_count > 0
    error_message = "policy.yaml must declare at least one destination_rules entry"
  }
}

run "workflow_yaml_has_required_fields" {
  command = plan

  assert {
    condition     = output.workflow_id != null
    error_message = "workflow.yaml is missing workflow_id"
  }

  assert {
    condition     = output.workflow_stages_count > 0
    error_message = "workflow.yaml must declare at least one stage"
  }
}
