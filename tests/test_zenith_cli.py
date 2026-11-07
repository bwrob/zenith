"""Unit tests for the Zenith command-line interface entry points."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from zenith.cli import build_parser, main
from zenith.models import ZenithConfig

if TYPE_CHECKING:
    from pathlib import Path

EXIT_ABORTED: int = 130


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that --version displays version and exits cleanly."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "zenith-template" in captured.out or "0.2.0" in captured.out


def test_cli_parser_defaults() -> None:
    """Verify default parser values."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.output_dir == "."
    assert args.no_input is False
    assert args.overwrite is False
    assert args.ai_tools is None


def test_cli_no_input_invokes_generator(tmp_path: Path) -> None:
    """Verify that --no-input bypasses TUI and executes generate_project."""
    with (
        patch(
            "zenith.cli.generate_project",
            return_value=tmp_path / "zenith",
        ) as mock_gen,
        patch("zenith.cli.ZenithApp") as mock_app,
    ):
        exit_code = main(["--no-input", "--output-dir", str(tmp_path)])
        assert exit_code == 0
        mock_app.assert_not_called()
        mock_gen.assert_called_once()
        config = mock_gen.call_args.args[0]
        output_dir = mock_gen.call_args.kwargs.get("output_dir")
        assert isinstance(config, ZenithConfig)
        assert output_dir == str(tmp_path)


def test_cli_no_input_with_custom_flags(tmp_path: Path) -> None:
    """Verify that custom CLI options are propagated to ZenithConfig."""
    with patch(
        "zenith.cli.generate_project",
        return_value=tmp_path / "custom",
    ) as mock_gen:
        exit_code = main(
            [
                "--no-input",
                "--output-dir",
                str(tmp_path),
                "--name",
                "Super App",
                "--slug",
                "super-app",
                "--package",
                "super_app",
                "--ai-tools",
                "claude,cursor",
                "--python-version",
                "3.12",
                "--license",
                "Apache-2.0",
                "--no-cli",
            ]
        )
        assert exit_code == 0
        config = mock_gen.call_args[0][0]
        assert config.project_name == "Super App"
        assert config.project_slug == "super-app"
        assert config.package_name == "super_app"
        assert config.ai_tools == ("claude", "cursor")
        assert config.python_version == "3.12"
        assert config.license == "Apache-2.0"
        assert config.include_cli is False


def test_cli_ai_tools_preset(tmp_path: Path) -> None:
    """Verify that specifying a preset name in --ai-tools maps to the preset tuple."""
    with patch(
        "zenith.cli.generate_project",
        return_value=tmp_path / "zenith",
    ) as mock_gen:
        exit_code = main(["--no-input", "--ai-tools", "ide-only"])
        assert exit_code == 0
        config = mock_gen.call_args[0][0]
        assert config.ai_tools == ("cursor", "windsurf", "zed", "copilot")


def test_cli_interactive_success(tmp_path: Path) -> None:
    """Verify interactive mode launches ZenithApp and generates project on submit."""
    fake_config = ZenithConfig(project_name="Interactive Project")
    mock_app_instance = patch("zenith.cli.ZenithApp").start().return_value
    mock_app_instance.run.return_value = fake_config
    mock_app_instance.result = fake_config

    with (
        patch("zenith.cli.sys.stdin.isatty", return_value=True),
        patch(
            "zenith.cli.generate_project",
            return_value=tmp_path / "interactive",
        ) as mock_gen,
    ):
        exit_code = main([])
        assert exit_code == 0
        mock_gen.assert_called_once()
        assert mock_gen.call_args[0][0] == fake_config


def test_cli_interactive_cancellation() -> None:
    """Verify that user cancellation in interactive mode exits with code 130."""
    mock_app_instance = patch("zenith.cli.ZenithApp").start().return_value
    mock_app_instance.run.return_value = None
    mock_app_instance.result = None

    with (
        patch("zenith.cli.sys.stdin.isatty", return_value=True),
        patch("zenith.cli.generate_project") as mock_gen,
    ):
        exit_code = main([])
        assert exit_code == EXIT_ABORTED
        mock_gen.assert_not_called()


def test_cli_handles_collision_error(tmp_path: Path) -> None:
    """Verify that FileExistsError reports an error and returns code 1."""
    with patch(
        "zenith.cli.generate_project",
        side_effect=FileExistsError("Target directory exists"),
    ):
        exit_code = main(["--no-input", "--output-dir", str(tmp_path)])
        assert exit_code == 1


def test_cli_handles_keyboard_interrupt() -> None:
    """Verify that KeyboardInterrupt exits with code 130."""
    with patch(
        "zenith.cli.generate_project",
        side_effect=KeyboardInterrupt,
    ):
        exit_code = main(["--no-input"])
        assert exit_code == EXIT_ABORTED
