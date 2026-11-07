"""Command-line interface entry points for Zenith."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel

from zenith import __version__
from zenith.generator import generate_project
from zenith.models import (
    AI_TOOL_PRESETS,
    PRESET_RECOMMENDED,
    SUPPORTED_LICENSES,
    SUPPORTED_PYTHON_VERSIONS,
    ZenithConfig,
    slugify,
)
from zenith.ui.app import ZenithApp

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

console = Console()


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for Zenith.

    Returns:
        Configured ArgumentParser instance.

    """
    parser = argparse.ArgumentParser(
        prog="zenith-template",
        description="Scaffold modern Python 3.12+ projects with Zenith.",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Directory where the new project folder will be created (default: .)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir_opt",
        default=None,
        help="Directory where the new project folder will be created.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version number and exit.",
    )
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="Do not prompt for parameters; use configuration defaults or flags.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite destination directory contents if it already exists.",
    )
    parser.add_argument(
        "--name",
        dest="project_name",
        default=None,
        help="Project Name (human-readable title).",
    )
    parser.add_argument(
        "--slug",
        dest="project_slug",
        default=None,
        help="Project Slug (directory and package name).",
    )
    parser.add_argument(
        "--package",
        dest="package_name",
        default=None,
        help="Python Package Name (import identifier).",
    )
    parser.add_argument(
        "--description",
        dest="description",
        default=None,
        help="Short project description.",
    )
    parser.add_argument(
        "--author",
        dest="author_name",
        default=None,
        help="Author full name.",
    )
    parser.add_argument(
        "--email",
        dest="author_email",
        default=None,
        help="Author email address.",
    )
    parser.add_argument(
        "--github",
        dest="github_username",
        default=None,
        help="GitHub username or organization.",
    )
    parser.add_argument(
        "--python-version",
        choices=SUPPORTED_PYTHON_VERSIONS,
        default="3.13",
        help="Target Python version (default: 3.13).",
    )
    parser.add_argument(
        "--license",
        choices=SUPPORTED_LICENSES,
        default="MIT",
        help="Open source license identifier (default: MIT).",
    )
    parser.add_argument(
        "--ai-tools",
        dest="ai_tools",
        default=None,
        help=(
            "AI tool preset name (all, recommended, ide-only, cli-only, none)"
            " or comma-separated tool names."
        ),
    )
    parser.add_argument(
        "--include-cli",
        "--cli",
        dest="include_cli",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Generate Typer command-line interface.",
    )
    parser.add_argument(
        "--include-ci",
        "--ci",
        dest="include_ci",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Generate GitHub Actions workflows for testing and publishing.",
    )
    parser.add_argument(
        "--include-skills",
        "--skills",
        dest="include_skills",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include Zenith agent skills suite (.agents/).",
    )
    return parser


def _resolve_ai_tools(raw: str | None) -> tuple[str, ...]:
    """Parse raw string or preset into a tuple of AI tool identifiers.

    Args:
        raw: Raw preset name or comma-separated tool keys.

    Returns:
        Tuple of active tool identifiers.

    """
    if raw is None:
        return PRESET_RECOMMENDED

    normalized = raw.strip().lower()
    if normalized in AI_TOOL_PRESETS:
        return AI_TOOL_PRESETS[normalized]

    items = [t.strip() for t in normalized.replace(";", ",").split(",") if t.strip()]
    return tuple(items)


def _config_from_args(args: argparse.Namespace) -> ZenithConfig:
    """Build a ZenithConfig dataclass instance from parsed command-line arguments.

    Args:
        args: Parsed command-line namespace.

    Returns:
        Populated ZenithConfig instance.

    """
    defaults = ZenithConfig()
    name = args.project_name or defaults.project_name
    fallback_slug = slugify(name) if args.project_name else defaults.project_slug
    slug = args.project_slug or fallback_slug
    fallback_pkg = (
        slugify(name, separator="_") if args.project_name else defaults.package_name
    )
    package = args.package_name or fallback_pkg

    return ZenithConfig(
        project_name=name,
        project_slug=slug,
        package_name=package,
        description=args.description or defaults.description,
        author_name=args.author_name or defaults.author_name,
        author_email=args.author_email or defaults.author_email,
        github_username=args.github_username or defaults.github_username,
        python_version=args.python_version,
        license=args.license,
        include_cli=args.include_cli,
        include_ci_testing=args.include_ci,
        include_ci_publishing=args.include_ci,
        include_agent_skills=args.include_skills,
        ai_tools=_resolve_ai_tools(args.ai_tools),
    )


def _render_summary(project_dir: Path, config: ZenithConfig) -> None:
    """Print a success confirmation card with next steps.

    Args:
        project_dir: Path to the generated project directory.
        config: Configuration used to render the project.

    """
    tools_str = ", ".join(config.ai_tools) if config.ai_tools else "None"
    summary_text = (
        f"[bold green]✨ Project successfully scaffolded at:[/bold green]\n"
        f"  [cyan]{project_dir.resolve()}[/cyan]\n\n"
        f"[bold]Active AI Tool Integrations:[/bold]\n"
        f"  [dim]{tools_str}[/dim]\n\n"
        f"[bold]Next Steps:[/bold]\n"
        f"  1. [yellow]cd {config.project_slug}[/yellow]\n"
        f"  2. [yellow]uv sync[/yellow]\n"
        f"  3. [yellow]uv run poe test[/yellow]\n"
        f"  4. [yellow]uv run poe code-quality[/yellow]"
    )
    panel = Panel(summary_text, title="Zenith Scaffold Complete", border_style="green")
    console.print(panel)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Zenith CLI entry point.

    Args:
        argv: Optional command-line argument vector.

    Returns:
        Process exit status code.

    """
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.no_input and sys.stdin.isatty():
        initial = _config_from_args(args)
        app = ZenithApp(initial_config=initial)
        app.run()
        if app.result is None:
            console.print("[yellow]Project generation cancelled.[/yellow]")
            return 130
        config = app.result
    else:
        config = _config_from_args(args)

    target_dir = args.output_dir_opt or args.output_dir
    try:
        project_dir = generate_project(
            config,
            output_dir=target_dir,
            overwrite=args.overwrite,
        )
    except (FileExistsError, FileNotFoundError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation aborted by user.[/yellow]")
        return 130
    else:
        _render_summary(project_dir, config)
        return 0


if __name__ == "__main__":
    sys.exit(main())
