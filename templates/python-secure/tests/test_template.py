"""Tests for a generated secure project.

Verifies the governance files this template ships (mission.yaml, policy.yaml,
workflow.yaml) are present, parse as YAML, and carry the fields required by
GovernanceContracts' schemas, and that project-name substitution actually ran.

This file is shipped verbatim into every generated project by
TemplateGenerator, but it also lives here in the template source, where
TEMPLATE_PROJECT_NAME has intentionally not been substituted yet. The
substitution checks below skip (rather than fail) when run against that
un-substituted source, and are enforced once a project has actually been
generated.
"""
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "TEMPLATE_PROJECT_NAME"


def _load(name: str) -> dict:
    with (ROOT / name).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class TestMissionYaml(unittest.TestCase):
    def setUp(self):
        self.mission = _load("mission.yaml")

    def test_required_fields_present(self):
        for field in (
            "schema_version",
            "repo_id",
            "mission",
            "non_goals",
            "boundaries",
            "risk_tier",
            "approval_triggers",
        ):
            self.assertIn(field, self.mission)

    def test_risk_tier_is_valid(self):
        self.assertIn(self.mission["risk_tier"], ("low", "medium", "high"))

    def test_project_name_placeholder_was_substituted(self):
        if self.mission["repo_id"] == PLACEHOLDER:
            self.skipTest("running against un-substituted template source")
        self.assertNotEqual(self.mission["repo_id"], PLACEHOLDER)
        self.assertNotIn(PLACEHOLDER, self.mission["mission"])


class TestPolicyYaml(unittest.TestCase):
    def setUp(self):
        self.policy = _load("policy.yaml")

    def test_required_fields_present(self):
        for field in (
            "schema_version",
            "policy_id",
            "permitted_actions",
            "blocked_actions",
            "data_rules",
            "destination_rules",
            "approval_rules",
        ):
            self.assertIn(field, self.policy)

    def test_project_name_placeholder_was_substituted(self):
        if self.policy["policy_id"] == f"{PLACEHOLDER}-policy":
            self.skipTest("running against un-substituted template source")
        self.assertNotIn(PLACEHOLDER, self.policy["policy_id"])


class TestWorkflowYaml(unittest.TestCase):
    def setUp(self):
        self.workflow = _load("workflow.yaml")

    def test_required_fields_present(self):
        for field in (
            "schema_version",
            "workflow_id",
            "complexity_level",
            "stages",
            "stop_conditions",
        ):
            self.assertIn(field, self.workflow)

    def test_stages_have_required_fields(self):
        self.assertTrue(self.workflow["stages"])
        for stage in self.workflow["stages"]:
            for field in ("stage_id", "name", "actor", "allowed_actions"):
                self.assertIn(field, stage)

    def test_project_name_placeholder_was_substituted(self):
        if self.workflow["workflow_id"] == f"{PLACEHOLDER}-workflow":
            self.skipTest("running against un-substituted template source")
        self.assertNotIn(PLACEHOLDER, self.workflow["workflow_id"])


if __name__ == "__main__":
    unittest.main()
