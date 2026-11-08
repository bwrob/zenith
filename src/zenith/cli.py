"""Command-line interface entry points for Zenith."""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich import box
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
        default="3.12",
        help="Target Python version (default: 3.12).",
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
        "--include-docs",
        "--docs",
        dest="include_docs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include documentation website (docs/ & zensical.toml).",
    )
    parser.add_argument(
        "--include-mutation",
        "--mutation",
        dest="include_mutation_testing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include mutation testing tooling (cosmic-ray & mutmut).",
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
        help="Include agent skills suite (.agents/).",
    )
    parser.add_argument(
        "--init-git",
        "--git",
        dest="init_git",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Initialize Git repository in scaffolded project.",
    )
    parser.add_argument(
        "--run-uv-sync",
        "--sync",
        dest="run_uv_sync",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run uv sync after scaffolding.",
    )
    parser.add_argument(
        "--install-git-hooks",
        "--hooks",
        dest="install_git_hooks",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Install Git hooks (prek install) after scaffolding.",
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


def config_from_args(args: argparse.Namespace) -> ZenithConfig:
    """Build a ZenithConfig dataclass instance from parsed command-line arguments.

    Args:
        args: Parsed command-line namespace.

    Returns:
        Populated ZenithConfig instance.

    """
    defaults = ZenithConfig()
    raw_dir = getattr(args, "output_dir_opt", None) or getattr(
        args,
        "output_dir",
        None,
    )
    output_dir = raw_dir if raw_dir and raw_dir != "." else defaults.output_dir
    name = args.project_name or defaults.project_name
    fallback_slug = slugify(name) if args.project_name else defaults.project_slug
    slug = args.project_slug or fallback_slug
    fallback_pkg = (
        slugify(name, separator="_") if args.project_name else defaults.package_name
    )
    package = args.package_name or fallback_pkg

    return ZenithConfig(
        output_dir=output_dir,
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
        include_docs=getattr(args, "include_docs", defaults.include_docs),
        include_mutation_testing=getattr(
            args,
            "include_mutation_testing",
            defaults.include_mutation_testing,
        ),
        init_git=getattr(args, "init_git", defaults.init_git),
        run_uv_sync=getattr(args, "run_uv_sync", defaults.run_uv_sync),
        install_git_hooks=getattr(
            args,
            "install_git_hooks",
            defaults.install_git_hooks,
        ),
        ai_tools=_resolve_ai_tools(args.ai_tools),
    )


def _build_feature_flags(config: ZenithConfig) -> list[str]:
    """Collect non-default command-line flags for project features and lifecycle.

    Args:
        config: Configuration holding feature toggles.

    Returns:
        List of CLI flag strings.

    """
    has_custom_dir = Path(config.output_dir).resolve() != Path.cwd().resolve()
    flag_conditions = (
        (has_custom_dir, f"--output-dir {shlex.quote(config.output_dir)}"),
        (not config.include_cli, "--no-cli"),
        (not config.include_docs, "--no-docs"),
        (not config.include_mutation_testing, "--no-mutation"),
        (not (config.include_ci_testing or config.include_ci_publishing), "--no-ci"),
        (not config.include_agent_skills, "--no-skills"),
        (not config.init_git, "--no-git"),
        (config.run_uv_sync, "--sync"),
        (config.install_git_hooks, "--hooks"),
    )
    return [flag for condition, flag in flag_conditions if condition]


def _resolve_ai_tools_arg(ai_tools: tuple[str, ...]) -> str:
    """Determine the CLI argument value representing selected AI tools.

    Args:
        ai_tools: Tuple of selected tool identifier strings.

    Returns:
        Preset name or comma-separated list of tools.

    """
    if not ai_tools:
        return "none"
    for preset_name, preset_tools in AI_TOOL_PRESETS.items():
        if set(ai_tools) == set(preset_tools):
            return preset_name
    return ",".join(ai_tools)


def build_reproduce_command(config: ZenithConfig) -> str:
    """Build the exact command to recreate this project via CLI.

    Args:
        config: Configuration used to render the project.

    Returns:
        Shell-quoted CLI command string.

    """
    parts = [
        "uvx zenith-template --no-input",
        f"--name {shlex.quote(config.project_name)}",
        f"--slug {shlex.quote(config.project_slug)}",
        f"--package {shlex.quote(config.package_name)}",
        f"--description {shlex.quote(config.description)}",
        f"--author {shlex.quote(config.author_name)}",
        f"--email {shlex.quote(config.author_email)}",
        f"--github {shlex.quote(config.github_username)}",
        f"--python-version {config.python_version}",
        f"--license {config.license}",
    ]
    parts.extend(_build_feature_flags(config))
    tools_arg = _resolve_ai_tools_arg(config.ai_tools)
    parts.append(f"--ai-tools {tools_arg}")
    return " ".join(parts)


def render_summary(project_dir: Path, config: ZenithConfig) -> None:
    """Print a success confirmation card with next steps.

    Args:
        project_dir: Path to the generated project directory.
        config: Configuration used to render the project.

    """
    tools_str = ", ".join(config.ai_tools) if config.ai_tools else "None"
    recreate_cmd = build_reproduce_command(config)

    next_steps: list[str] = [f"cd {config.project_slug}"]
    if not config.run_uv_sync:
        next_steps.append("uv sync")
    next_steps.extend(["uv run poe test", "uv run poe code-quality"])
    steps_formatted = "\n".join(
        f"  [#38bdf8]{idx}.[/] [#e0f2fe]{step}[/]"
        for idx, step in enumerate(next_steps, 1)
    )

    summary_text = (
        f"[bold #38bdf8]✦ Project successfully scaffolded at:[/]\n"
        f"  [#e0f2fe]{project_dir.resolve()}[/]\n\n"
        f"[bold #38bdf8]✦ Active AI Tool Integrations:[/]\n"
        f"  [dim #94a3b8]{tools_str}[/]\n\n"
        f"[bold #38bdf8]✦ Recreate via CLI:[/]\n"
        f"  [#38bdf8]{recreate_cmd}[/]\n\n"
        f"[bold #38bdf8]✦ Next Steps:[/]\n"
        f"{steps_formatted}"
    )
    panel = Panel(
        summary_text,
        title="[bold #38bdf8]✦ Zenith Project Initialized ✦[/]",
        border_style="#38bdf8",
        box=box.ROUNDED,
        padding=(1, 2),
    )
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
        initial = config_from_args(args)
        app = ZenithApp(initial_config=initial)
        app.run()
        if app.result is None:
            console.print("[yellow]Project generation cancelled.[/yellow]")
            return 130
        config = app.result
    else:
        config = config_from_args(args)

    try:
        project_dir = generate_project(
            config,
            output_dir=config.output_dir,
            overwrite=args.overwrite,
        )
    except (FileExistsError, FileNotFoundError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation aborted by user.[/yellow]")
        return 130
    else:
        render_summary(project_dir, config)
        return 0


if __name__ == "__main__":
    sys.exit(main())
