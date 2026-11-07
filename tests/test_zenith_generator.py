"""Unit tests for Zenith programmatic Cookiecutter generator."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from zenith.generator import generate_project
from zenith.models import ZenithConfig

if TYPE_CHECKING:
    from pathlib import Path


def test_generate_project_calls_cookiecutter(tmp_path: Path) -> None:
    """Verify that generate_project invokes cookiecutter with resolved context."""
    config = ZenithConfig(project_name="My Cool App", project_slug="my-cool-app")
    fake_template = tmp_path / "template"
    fake_template.mkdir()

    with (
        patch("zenith.generator.get_template_path", return_value=fake_template),
        patch(
            "zenith.generator.cookiecutter",
            return_value=str(tmp_path / "my-cool-app"),
        ) as mock_cc,
    ):
        result = generate_project(config, output_dir=tmp_path)
        assert result == tmp_path / "my-cool-app"
        mock_cc.assert_called_once_with(
            template=str(fake_template),
            extra_context=config.to_cookiecutter_context(),
            no_input=True,
            output_dir=str(tmp_path),
            overwrite_if_exists=False,
        )


def test_generate_project_raises_on_collision(tmp_path: Path) -> None:
    """Verify FileExistsError when output project directory exists and is not empty."""
    config = ZenithConfig(project_slug="existing-project")
    target_dir = tmp_path / "existing-project"
    target_dir.mkdir()
    (target_dir / "somefile.txt").write_text("hello", encoding="utf-8")

    with pytest.raises(
        FileExistsError, match=r"Target directory .* already exists and is not empty"
    ):
        generate_project(config, output_dir=tmp_path, overwrite=False)


def test_generate_project_allows_overwrite(tmp_path: Path) -> None:
    """Verify generation proceeds when overwrite=True even if target exists."""
    config = ZenithConfig(project_slug="existing-project")
    target_dir = tmp_path / "existing-project"
    target_dir.mkdir()
    (target_dir / "somefile.txt").write_text("hello", encoding="utf-8")
    fake_template = tmp_path / "template"
    fake_template.mkdir()

    with (
        patch("zenith.generator.get_template_path", return_value=fake_template),
        patch(
            "zenith.generator.cookiecutter",
            return_value=str(target_dir),
        ) as mock_cc,
    ):
        result = generate_project(config, output_dir=tmp_path, overwrite=True)
        assert result == target_dir
        mock_cc.assert_called_once_with(
            template=str(fake_template),
            extra_context=config.to_cookiecutter_context(),
            no_input=True,
            output_dir=str(tmp_path),
            overwrite_if_exists=True,
        )
