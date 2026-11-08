"""Resolution and discovery of bundled Cookiecutter template assets."""

from __future__ import annotations

import importlib.resources
from pathlib import Path


def _get_repo_root_template() -> Path | None:
    """Inspect local repository root for development/editable checkouts.

    Returns:
        Path to repo root if cookiecutter.json exists, otherwise None.

    """
    candidate = Path(__file__).resolve().parents[2]
    if (candidate / "cookiecutter.json").is_file():
        return candidate
    return None


def _get_packaged_template() -> Path | None:
    """Inspect installed package resources for packaged template files.

    Returns:
        Path to template directory if found, otherwise None.

    """
    try:
        pkg_dir = importlib.resources.files("zenith").joinpath("template")
        candidate = Path(str(pkg_dir))
        if (candidate / "cookiecutter.json").is_file():
            return candidate
    except (TypeError, FileNotFoundError, ModuleNotFoundError):
        return None
    return None


def get_template_path() -> Path:
    """Resolve the filesystem path to the Zenith Cookiecutter template.

    Checks the local repository root first (for development), followed by
    packaged distribution resources.

    Returns:
        Absolute Path to the directory containing cookiecutter.json.

    Raises:
        FileNotFoundError: If the template directory cannot be located.

    """
    repo_template = _get_repo_root_template()
    if repo_template is not None:
        return repo_template

    packaged_template = _get_packaged_template()
    if packaged_template is not None:
        return packaged_template

    msg = (
        "Could not locate Zenith Cookiecutter template in repository or"
        " installed package."
    )
    raise FileNotFoundError(msg)
