"""Pytest fixtures and test configuration."""

from __future__ import annotations

import pytest
{%- if cookiecutter.include_cli in [True, "yes", "true", "True", "1"] %}
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    """Provide a Typer CLI runner fixture without ANSI color escapes.

    Returns
    -------
    CliRunner
        A configured CLI runner instance.

    """
    return CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})
{%- endif %}


@pytest.fixture
def sample_name() -> str:
    """Provide a sample name for testing.

    Returns
    -------
    str
        A sample user name used across tests.

    """
    return "Antigravity"
