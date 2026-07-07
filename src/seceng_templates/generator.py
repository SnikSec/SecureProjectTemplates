"""Secure template generation logic."""
from pathlib import Path
import shutil


TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


class TemplateGenerator:
    """Generator for secure project templates."""

    def __init__(self, language: str, output_dir: Path):
        self.language = language
        self.output_dir = output_dir
        self.template_path = TEMPLATES_DIR / f"{language}-secure"

    def validate(self) -> bool:
        """Validate template exists."""
        return self.template_path.exists()

    def generate(self, project_name: str) -> bool:
        """Generate project from template."""
        if not self.validate():
            return False

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Copy template
        project_dir = self.output_dir / project_name
        if project_dir.exists():
            shutil.rmtree(project_dir)

        shutil.copytree(self.template_path, project_dir)

        # Update project metadata
        self._update_metadata(project_dir, project_name)

        return True

    def _update_metadata(self, project_dir: Path, project_name: str):
        """Update project name in configuration files."""
        # Update mission.yaml, policy.yaml, workflow.yaml, and any
        # language-specific manifest that embeds the project name
        # (Cargo.toml's package name, Terraform's variables.tf default).
        for governance_file in (
            "mission.yaml", "policy.yaml", "workflow.yaml", "Cargo.toml", "variables.tf",
        ):
            path = project_dir / governance_file
            if path.exists():
                content = path.read_text()
                content = content.replace("TEMPLATE_PROJECT_NAME", project_name)
                path.write_text(content)

        # Update README
        readme_path = project_dir / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            content = content.replace("Template Project", project_name.title())
            readme_path.write_text(content)
