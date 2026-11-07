"""Unit tests for Zenith template asset resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from zenith.template import (
    _get_packaged_template,  # ruff: ignore[import-private-name] - direct unit test
    _get_repo_root_template,  # ruff: ignore[import-private-name] - direct unit test
    get_template_path,
)

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

    def fake_joinpath(_sub: object) -> Path:
        return fake_pkg_dir

    with (
        patch("zenith.template._get_repo_root_template", return_value=None),
        patch(
            "zenith.template.importlib.resources.files",
            return_value=MagicMock(joinpath=fake_joinpath),
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


def test_get_repo_root_template_returns_none(tmp_path: Path) -> None:
    """Verify _get_repo_root_template returns None when cookiecutter.json is absent."""
    with patch("zenith.template.Path") as mock_path:
        mock_instance = mock_path.return_value
        mock_instance.resolve.return_value.parents = [tmp_path, tmp_path, tmp_path]
        result = _get_repo_root_template()
        assert result is None


def test_get_packaged_template_missing_cookiecutter(tmp_path: Path) -> None:
    """Verify _get_packaged_template returns None if cookiecutter.json is missing."""
    empty_pkg_dir = tmp_path / "empty_pkg"
    empty_pkg_dir.mkdir()

    def fake_joinpath(_sub: object) -> Path:
        return empty_pkg_dir

    with patch(
        "zenith.template.importlib.resources.files",
        return_value=MagicMock(joinpath=fake_joinpath),
    ):
        assert _get_packaged_template() is None


def test_get_packaged_template_handles_exception() -> None:
    """Verify _get_packaged_template returns None on resource errors."""
    with patch(
        "zenith.template.importlib.resources.files",
        side_effect=ModuleNotFoundError,
    ):
        assert _get_packaged_template() is None
