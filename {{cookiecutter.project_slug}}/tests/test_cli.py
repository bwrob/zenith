"""Unit tests for the command-line interface."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

import {{ cookiecutter.package_name }}
from {{ cookiecutter.package_name }}.__main__ import main as module_main
from {{ cookiecutter.package_name }}.cli import app, main

runner = CliRunner()


def test_cli_help() -> None:
    """Test CLI help flag outputs command information."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout or "Options:" in result.stdout


def test_cli_version() -> None:
    """Test CLI version option outputs version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "{{ cookiecutter.project_slug }}" in result.stdout


def test_cli_greet() -> None:
    """Test CLI greet subcommand."""
    result = runner.invoke(app, ["greet", "Developer"])
    assert result.exit_code == 0
    assert "Hello, Developer!" in result.stdout


def test_cli_greet_default() -> None:
    """Test CLI greet subcommand with default argument."""
    result = runner.invoke(app, ["greet"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_cli_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main entry point invocation."""
    monkeypatch.setattr("sys.argv", ["{{ cookiecutter.project_slug }}", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_cli_module_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test module invocation via python -m {{ cookiecutter.package_name }}."""
    monkeypatch.setattr("sys.argv", ["{{ cookiecutter.project_slug }}", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        module_main()
    assert exc_info.value.code == 0


def test_lazy_dunder_lookup() -> None:
    """Test accessing dunders raises AttributeError directly."""
    with pytest.raises(AttributeError, match="has no attribute '__unknown__'"):
        _ = {{ cookiecutter.package_name }}.__unknown__


def test_lazy_unknown_attribute() -> None:
    """Test accessing unknown attributes raises AttributeError."""
    with pytest.raises(AttributeError, match="has no attribute 'nonexistent_symbol'"):
        _ = {{ cookiecutter.package_name }}.nonexistent_symbol


def test_lazy_foreign_module_error() -> None:
    """Test re-raising ModuleNotFoundError when error is from internal dependency."""
    with (
        patch("importlib.import_module", side_effect=ModuleNotFoundError("unrelated")),
        pytest.raises(ModuleNotFoundError, match="unrelated"),
    ):
        _ = {{ cookiecutter.package_name }}.some_mod


def test_lazy_member_caching() -> None:
    """Test lazy member resolution caches the member in module globals."""
    resolved = {{ cookiecutter.package_name }}.get_greeting
    assert resolved("Template") == "Hello, Template!"
    assert vars({{ cookiecutter.package_name }})["get_greeting"] is resolved


def test_lazy_dir_exposes_all_members() -> None:
    """Test module_dir lists __all__ exports before they are imported."""
    names = dir({{ cookiecutter.package_name }})
    assert "get_greeting" in names
    assert "app" in names


def test_lazy_dir_without_all_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test module_dir when __all__ is not a list or tuple."""
    monkeypatch.setattr({{ cookiecutter.package_name }}, "__all__", None)
    names = dir({{ cookiecutter.package_name }})
    assert "__version__" in names
    assert "lazy_getattr" in names
