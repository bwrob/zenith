"""Tests for the Zenith template."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from cookiecutter.main import cookiecutter

if TYPE_CHECKING:
    from collections.abc import Iterator


TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.xdist_group(name="template")


@pytest.fixture
def temp_output_dir() -> Iterator[Path]:
    """Create a temporary directory for cookiecutter output.

    Yields:
        Path: Temporary directory receiving rendered projects.

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="module")
def full_project(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    """Render a full-featured project once with CLI, CI, docs, and MIT license.

    Yields:
        Path: Root directory of the rendered full project.

    """
    tmp_dir = tmp_path_factory.mktemp("full_app")
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(tmp_dir),
            extra_context={
                "project_name": "Demo App",
                "github_username": "zenith-template-tests",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "include_cli": "yes",
                "include_ci_testing": "yes",
                "include_ci_publishing": "yes",
                "include_github_actions": "yes",
                "license": "MIT",
            },
        )
    )
    try:
        yield rendered
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def minimal_project(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    """Render a minimal project once with CLI off, CI off, and no license.

    Yields:
        Path: Root directory of the rendered minimal project.

    """
    tmp_dir = tmp_path_factory.mktemp("minimal_app")
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(tmp_dir),
            extra_context={
                "project_name": "Zenith's Cool Tool (v2)",
                "python_version": "3.15",
                "include_cli": "no",
                "include_ci_testing": "no",
                "include_ci_publishing": "no",
                "include_github_actions": "no",
                "license": "None",
            },
        )
    )
    try:
        yield rendered
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
