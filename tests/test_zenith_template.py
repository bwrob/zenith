"""Unit tests for Zenith template asset resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from zenith.template import get_template_path

if TYPE_CHECKING:
    from pathlib import Path


def test_get_template_path_from_repo_root() -> None:
    """Verify get_template_path locates the local repo root."""
    path = get_template_path()
    assert path.is_dir()
    assert (path / "cookiecutter.json").is_file()
    assert (path / "{{cookiecutter.project_slug}}").is_dir()


def test_get_template_path_from_package_resources(tmp_path: Path) -> None:
    """Verify fallback to package resources when repo root is missing template."""
    fake_pkg_dir = tmp_path / "zenith" / "template"
    fake_pkg_dir.mkdir(parents=True)
    (fake_pkg_dir / "cookiecutter.json").write_text("{}", encoding="utf-8")

    with (
        patch("zenith.template._get_repo_root_template", return_value=None),
        patch(
            "zenith.template.importlib.resources.files",
            return_value=MagicMock(joinpath=lambda _sub: fake_pkg_dir),
        ),
    ):
        resolved = get_template_path()
        assert resolved == fake_pkg_dir


def test_get_template_path_raises_when_missing() -> None:
    """Verify FileNotFoundError is raised if template cannot be located anywhere."""
    with (
        patch("zenith.template._get_repo_root_template", return_value=None),
        patch("zenith.template._get_packaged_template", return_value=None),
        pytest.raises(
            FileNotFoundError, match="Could not locate Zenith Cookiecutter template"
        ),
    ):
        get_template_path()
