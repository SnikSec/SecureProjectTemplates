output "project_name" {
  description = "The project name this module was scaffolded for."
  value       = var.project_name
}

output "mission_repo_id" {
  description = "mission.yaml's repo_id, exposed for governance-file validation in tests/."
  value       = local.mission_config.repo_id
}

output "mission_risk_tier" {
  description = "mission.yaml's risk_tier, exposed for governance-file validation in tests/."
  value       = local.mission_config.risk_tier
}

output "policy_id" {
  description = "policy.yaml's policy_id, exposed for governance-file validation in tests/."
  value       = local.policy_config.policy_id
}

output "policy_destination_rules_count" {
  description = "Number of destination_rules entries in policy.yaml, exposed for tests/."
  value       = length(local.policy_config.destination_rules)
}

output "workflow_id" {
  description = "workflow.yaml's workflow_id, exposed for governance-file validation in tests/."
  value       = local.workflow_config.workflow_id
}

output "workflow_stages_count" {
  description = "Number of stages in workflow.yaml, exposed for tests/."
  value       = length(local.workflow_config.stages)
}
