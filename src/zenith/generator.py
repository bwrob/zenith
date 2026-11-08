"""Execution of Cookiecutter project generation using programmatic API."""

from __future__ import annotations

import contextlib
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- post-scaffold lifecycle automation
from pathlib import Path
from typing import TYPE_CHECKING

from cookiecutter.main import cookiecutter

from zenith.template import get_template_path

if TYPE_CHECKING:
    from collections.abc import Callable

    from zenith.models import ZenithConfig


def _noop_step(_message: str) -> None:
    """Ignore step status notifications when no callback is provided."""


def run_cmd(cmd: list[str], cwd: Path) -> None:
    """Safely run a system command in the generated project directory.

    Args:
        cmd: Command argument vector to execute.
        cwd: Working directory for command execution.

    """
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] -- safe execution with argument list
            cmd,
            cwd=cwd,
            check=False,
            capture_output=True,
        )


def _run_post_scaffold(
    project_dir: Path,
    config: ZenithConfig,
    on_step: Callable[[str], None] = _noop_step,
) -> None:
    """Execute optional post-scaffolding lifecycle automation steps.

    Args:
        project_dir: Path to the generated project directory.
        config: Configuration containing lifecycle flags.
        on_step: Callback invoked with a human-readable description before each step.

    """
    if config.init_git and not (project_dir / ".git").is_dir():
        on_step("Initializing Git repository (git init)...")
        run_cmd(["git", "init"], cwd=project_dir)

    if config.run_uv_sync:
        on_step("Synchronizing Python environment (uv sync)...")
        run_cmd(["uv", "sync"], cwd=project_dir)
        on_step("Formatting TOML files (uv run taplo format)...")
        run_cmd(["uv", "run", "taplo", "format"], cwd=project_dir)

    if config.install_git_hooks and (project_dir / ".git").is_dir():
        on_step("Installing Git hooks (prek install)...")
        run_cmd(["uv", "run", "prek", "install"], cwd=project_dir)


def generate_project(
    config: ZenithConfig,
    output_dir: Path | str = ".",
    *,
    overwrite: bool = False,
    on_step: Callable[[str], None] = _noop_step,
) -> Path:
    """Generate a new Zenith project from the bundled template.

    Args:
        config: Project configuration settings.
        output_dir: Destination directory where project folder will be created.
        overwrite: Whether to overwrite existing files in destination directory.
        on_step: Callback invoked with a human-readable description before each step.

    Returns:
        Path to the scaffolded project directory.

    Raises:
        FileExistsError: If the target directory exists and overwrite is False.

    """
    out_path = Path(output_dir).resolve()
    target_dir = out_path / config.project_slug

    if target_dir.is_dir() and not overwrite and any(target_dir.iterdir()):
        msg = f"Target directory '{target_dir}' already exists and is not empty."
        raise FileExistsError(msg)

    template_path = get_template_path()
    context = config.to_cookiecutter_context()

    on_step(f"Scaffolding project template into {target_dir.name}...")
    result = cookiecutter(
        template=str(template_path),
        extra_context=context,
        no_input=True,
        output_dir=str(out_path),
        overwrite_if_exists=overwrite,
    )
    project_path = Path(result)
    _run_post_scaffold(project_path, config, on_step=on_step)
    return project_path
