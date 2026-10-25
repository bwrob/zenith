"""Synchronize the zenith-example showcase with the instantiated template."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cookiecutter.main import cookiecutter
from rich.console import Console

console = Console(highlight=False)

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

SHOWCASE_CONTEXT: dict[str, Any] = {
    "project_name": "Zenith Example",
    "project_slug": "zenith-example",
    "package_name": "zenith_example",
    "description": (
        "Demonstration and showcase repository instantiated from the Zenith template."
    ),
    "author_name": "bwrob",
    "author_email": "contact@bwrob.dev",
    "github_username": "bwrob",
    "version": "0.1.0",
    "python_version": "3.13",
    "license": "MIT",
    "include_cli": True,
    "include_ci_testing": True,
    "include_ci_publishing": True,
}


def _clean_target_dir(target_dir: Path) -> None:
    """Remove all files and directories in target_dir except .git."""
    for item in target_dir.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _copy_rendered_files(rendered_path: Path, target_dir: Path) -> None:
    """Copy all files and directories from rendered_path into target_dir except .git."""
    for item in rendered_path.iterdir():
        if item.name == ".git":
            continue
        dest = target_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, symlinks=True)
        else:
            shutil.copy2(item, dest, follow_symlinks=False)


def sync_example(target_dir: Path, *, lock: bool = True) -> Path:
    """Render the Zenith template into target_dir, preserving its .git directory.

    Args:
        target_dir: Showcase repository to refresh.
        lock: Whether to regenerate ``uv.lock`` in the target.

    Returns:
        The resolved target directory.

    """
    resolved_target = target_dir.resolve()
    resolved_target.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        console.print(
            f"[bold cyan]Scaffolding Zenith showcase into "
            f"temporary staging: {tmpdir}[/]"
        )
        rendered_path = Path(
            cookiecutter(
                str(TEMPLATE_ROOT),
                no_input=True,
                output_dir=tmpdir,
                extra_context=SHOWCASE_CONTEXT,
            )
        )

        console.print(
            f"[bold cyan]Synchronizing rendered files to target: {resolved_target}[/]"
        )
        _clean_target_dir(resolved_target)
        _copy_rendered_files(rendered_path, resolved_target)

    run_tool = shutil.which("uv")
    if run_tool is None:
        sys.exit(1)

    sub_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}

    if lock:
        console.print(f"[bold cyan]Generating uv.lock in {resolved_target}...[/]")
        subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
            [run_tool, "lock"], cwd=resolved_target, env=sub_env, check=True
        )

    console.print(f"[bold cyan]Formatting rendered files in {resolved_target}...[/]")
    subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [run_tool, "run", "poe", "fix"], cwd=resolved_target, env=sub_env, check=True
    )

    console.print(
        f"[bold green]✅ Showcase successfully synchronized at: {resolved_target}[/]"
    )
    return resolved_target


def main() -> None:
    """Parse arguments and execute template synchronization."""
    parser = argparse.ArgumentParser(
        description=(
            "Sync Zenith template showcase repository with instantiated template."
        )
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=Path("../zenith-example"),
        type=Path,
        help="Target directory for the showcase repo (defaults to ../zenith-example)",
    )
    parser.add_argument(
        "--no-lock",
        action="store_true",
        help="Skip generating uv.lock in target repository.",
    )
    args = parser.parse_args()
    sync_example(args.target, lock=not args.no_lock)


if __name__ == "__main__":
    main()
