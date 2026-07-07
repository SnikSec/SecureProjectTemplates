import argparse
from pathlib import Path

from .generator import TemplateGenerator


def generate(
    language: str,
    project_name: str,
    output_dir: Path,
) -> int:
    """Generate a secure project from template."""
    gen = TemplateGenerator(language, output_dir)

    if not gen.validate():
        print(f"ERROR: Template not found for language '{language}'")
        return 1

    if gen.generate(project_name):
        print(f"SUCCESS: Generated '{project_name}' from {language} template")
        print(f"Location: {output_dir / project_name}")
        return 0
    else:
        print("ERROR: Failed to generate project")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SecureProjectTemplates CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_cmd = subparsers.add_parser(
        "generate", help="Generate a secure project from template"
    )
    generate_cmd.add_argument(
        "--language", required=True, choices=["python", "rust", "terraform"]
    )
    generate_cmd.add_argument("--project-name", required=True)
    generate_cmd.add_argument("--output-dir", default=Path("."), type=Path)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "generate":
        return generate(args.language, args.project_name, args.output_dir)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
