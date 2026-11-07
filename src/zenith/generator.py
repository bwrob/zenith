"""Execution of Cookiecutter project generation using programmatic API."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cookiecutter.main import cookiecutter

from zenith.template import get_template_path

if TYPE_CHECKING:
    from zenith.models import ZenithConfig


def generate_project(
    config: ZenithConfig,
    output_dir: Path | str = ".",
    *,
    overwrite: bool = False,
) -> Path:
    """Generate a new Zenith project from the bundled template.

    Args:
        config: Project configuration settings.
        output_dir: Destination directory where project folder will be created.
        overwrite: Whether to overwrite existing files in destination directory.

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

    result = cookiecutter(
        template=str(template_path),
        extra_context=context,
        no_input=True,
        output_dir=str(out_path),
        overwrite_if_exists=overwrite,
    )
    return Path(result)
