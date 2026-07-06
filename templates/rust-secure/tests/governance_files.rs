//! Validates the governance files this template ships (mission.yaml, policy.yaml,
//! workflow.yaml) parse as YAML, carry the fields required by SecEng-Contracts'
//! schemas, and that project-name substitution actually ran.
//!
//! Mirrors templates/python-secure/tests/test_template.py's checks, written in
//! Rust so a generated Rust project has no Python dependency. This file is
//! shipped verbatim into every generated project by TemplateGenerator, but it
//! also lives here in the template source, where TEMPLATE_PROJECT_NAME has
//! intentionally not been substituted yet -- the placeholder-substitution
//! checks below print a notice and return early (no Rust equivalent of
//! unittest's skipTest) when run against that un-substituted source, and are
//! enforced once a project has actually been generated.

use std::fs;
use std::path::Path;

use serde_yaml::Value;

const PLACEHOLDER: &str = "TEMPLATE_PROJECT_NAME";

fn load_yaml(name: &str) -> Value {
    let path = Path::new(env!("CARGO_MANIFEST_DIR")).join(name);
    let content =
        fs::read_to_string(&path).unwrap_or_else(|_| panic!("failed to read {}", path.display()));
    serde_yaml::from_str(&content).unwrap_or_else(|_| panic!("failed to parse {} as YAML", name))
}

#[test]
fn mission_yaml_has_required_fields() {
    let mission = load_yaml("mission.yaml");
    for field in [
        "schema_version",
        "repo_id",
        "mission",
        "non_goals",
        "boundaries",
        "risk_tier",
        "approval_triggers",
    ] {
        assert!(mission.get(field).is_some(), "missing field: {}", field);
    }
}

#[test]
fn mission_yaml_risk_tier_is_valid() {
    let mission = load_yaml("mission.yaml");
    let risk_tier = mission["risk_tier"].as_str().unwrap();
    assert!(["low", "medium", "high"].contains(&risk_tier));
}

#[test]
fn mission_yaml_project_name_placeholder_was_substituted() {
    let mission = load_yaml("mission.yaml");
    let repo_id = mission["repo_id"].as_str().unwrap();
    if repo_id == PLACEHOLDER {
        eprintln!("skipping: running against un-substituted template source");
        return;
    }
    assert_ne!(repo_id, PLACEHOLDER);
    let mission_text = mission["mission"].as_str().unwrap();
    assert!(!mission_text.contains(PLACEHOLDER));
}

#[test]
fn policy_yaml_has_required_fields() {
    let policy = load_yaml("policy.yaml");
    for field in [
        "schema_version",
        "policy_id",
        "permitted_actions",
        "blocked_actions",
        "data_rules",
        "destination_rules",
        "approval_rules",
    ] {
        assert!(policy.get(field).is_some(), "missing field: {}", field);
    }
}

#[test]
fn policy_yaml_project_name_placeholder_was_substituted() {
    let policy = load_yaml("policy.yaml");
    let policy_id = policy["policy_id"].as_str().unwrap();
    let placeholder_id = format!("{}-policy", PLACEHOLDER);
    if policy_id == placeholder_id {
        eprintln!("skipping: running against un-substituted template source");
        return;
    }
    assert!(!policy_id.contains(PLACEHOLDER));
}

#[test]
fn workflow_yaml_has_required_fields() {
    let workflow = load_yaml("workflow.yaml");
    for field in [
        "schema_version",
        "workflow_id",
        "complexity_level",
        "stages",
        "stop_conditions",
    ] {
        assert!(workflow.get(field).is_some(), "missing field: {}", field);
    }
}

#[test]
fn workflow_yaml_stages_have_required_fields() {
    let workflow = load_yaml("workflow.yaml");
    let stages = workflow["stages"].as_sequence().unwrap();
    assert!(!stages.is_empty());
    for stage in stages {
        for field in ["stage_id", "name", "actor", "allowed_actions"] {
            assert!(stage.get(field).is_some(), "stage missing field: {}", field);
        }
    }
}

#[test]
fn workflow_yaml_project_name_placeholder_was_substituted() {
    let workflow = load_yaml("workflow.yaml");
    let workflow_id = workflow["workflow_id"].as_str().unwrap();
    let placeholder_id = format!("{}-workflow", PLACEHOLDER);
    if workflow_id == placeholder_id {
        eprintln!("skipping: running against un-substituted template source");
        return;
    }
    assert!(!workflow_id.contains(PLACEHOLDER));
}
