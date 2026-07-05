"""Real tests for TemplateGenerator: this repo's own generation logic,
as distinct from the templates/python-secure/tests fixture shipped to
generated projects."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from seceng_templates.generator import TemplateGenerator  # noqa: E402


class TestTemplateGeneratorValidate(unittest.TestCase):
    def test_known_language_template_exists(self):
        gen = TemplateGenerator("python", Path(tempfile.mkdtemp()))
        self.assertTrue(gen.validate())

    def test_unknown_language_template_does_not_exist(self):
        gen = TemplateGenerator("cobol", Path(tempfile.mkdtemp()))
        self.assertFalse(gen.validate())


class TestTemplateGeneratorGenerate(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)

    def test_generate_fails_for_unknown_language(self):
        gen = TemplateGenerator("cobol", self.tmp_dir)
        self.assertFalse(gen.generate("some-project"))

    def test_generate_creates_governance_files(self):
        gen = TemplateGenerator("python", self.tmp_dir)
        self.assertTrue(gen.generate("my-secure-project"))

        project_dir = self.tmp_dir / "my-secure-project"
        for expected in ("mission.yaml", "policy.yaml", "workflow.yaml", "README.md"):
            self.assertTrue(
                (project_dir / expected).exists(), f"missing {expected}"
            )

    def test_generate_substitutes_project_name_placeholder(self):
        gen = TemplateGenerator("python", self.tmp_dir)
        gen.generate("my-secure-project")
        project_dir = self.tmp_dir / "my-secure-project"

        for governance_file in ("mission.yaml", "policy.yaml", "workflow.yaml"):
            content = (project_dir / governance_file).read_text()
            self.assertNotIn("TEMPLATE_PROJECT_NAME", content)
            self.assertIn("my-secure-project", content)

    def test_generate_overwrites_existing_project_directory(self):
        gen = TemplateGenerator("python", self.tmp_dir)
        gen.generate("my-secure-project")

        project_dir = self.tmp_dir / "my-secure-project"
        stray_file = project_dir / "stray-leftover.txt"
        stray_file.write_text("should not survive regeneration")

        gen.generate("my-secure-project")
        self.assertFalse(stray_file.exists())


if __name__ == "__main__":
    unittest.main()
