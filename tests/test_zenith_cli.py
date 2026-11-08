"""Unit tests for the Zenith command-line interface entry points."""

from __future__ import annotations

import shlex
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from zenith.cli import (
    build_parser,
    build_reproduce_command,
    config_from_args,
    main,
    render_summary,
)
from zenith.models import PRESET_RECOMMENDED, ZenithConfig

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
    """Verify that --no-input bypasses TUI and executes generate_project (REQ-006)."""

    def fake_generate(
        _config: ZenithConfig,
        output_dir: Path | str = ".",
        *,
        overwrite: bool = False,
        on_step: object = None,
    ) -> Path:
        assert overwrite is False
        assert output_dir == str(tmp_path)
        assert callable(on_step)
        on_step("Scaffolding...")
        return tmp_path / "zenith"

    with (
        patch(
            "zenith.cli.generate_project",
            side_effect=fake_generate,
        ) as mock_gen,
        patch("zenith.cli.ZenithApp") as mock_app,
    ):
        exit_code = main(["--no-input", "--output-dir", str(tmp_path)])
        assert exit_code == 0
        mock_app.assert_not_called()
        mock_gen.assert_called_once()
        config = mock_gen.call_args.args[0]
        assert isinstance(config, ZenithConfig)


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
                "--no-docs",
                "--no-mutation",
                "--no-git",
                "--sync",
                "--hooks",
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
        assert config.include_docs is False
        assert config.include_mutation_testing is False
        assert config.init_git is False
        assert config.run_uv_sync is True
        assert config.install_git_hooks is True


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
    """Verify user cancellation in interactive mode exits with code 130 (REQ-007)."""
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


def test_build_reproduce_command_roundtrip() -> None:
    """Verify that build_reproduce_command generates valid reproducible CLI flags."""
    config = ZenithConfig(
        output_dir="/custom/output",
        project_name="Custom Galaxy",
        project_slug="custom-galaxy",
        package_name="custom_galaxy",
        description="A bespoke interstellar app",
        author_name="Ada Lovelace",
        author_email="ada@example.com",
        github_username="adalovelace",
        python_version="3.12",
        license="Apache-2.0",
        include_cli=False,
        include_docs=False,
        include_mutation_testing=False,
        include_ci_testing=False,
        include_ci_publishing=False,
        include_agent_skills=False,
        init_git=False,
        run_uv_sync=True,
        install_git_hooks=True,
        ai_tools=("cursor", "zed"),
    )

    cmd = build_reproduce_command(config)
    assert cmd.startswith("uvx zenith-template --no-input")
    assert "--output-dir /custom/output" in cmd
    assert "--name 'Custom Galaxy'" in cmd
    assert "--no-cli" in cmd
    assert "--no-docs" in cmd
    assert "--no-mutation" in cmd
    assert "--no-ci" in cmd
    assert "--no-skills" in cmd
    assert "--no-git" in cmd
    assert "--sync" in cmd
    assert "--hooks" in cmd
    assert "--ai-tools cursor,zed" in cmd

    # Verify parser roundtrip
    args = build_parser().parse_args(shlex.split(cmd)[2:])
    reconstructed = config_from_args(args)
    assert reconstructed.output_dir == config.output_dir
    assert reconstructed.project_name == config.project_name
    assert reconstructed.project_slug == config.project_slug
    assert reconstructed.package_name == config.package_name
    assert reconstructed.description == config.description
    assert reconstructed.author_name == config.author_name
    assert reconstructed.author_email == config.author_email
    assert reconstructed.github_username == config.github_username
    assert reconstructed.python_version == config.python_version
    assert reconstructed.license == config.license
    assert reconstructed.include_cli is False
    assert reconstructed.include_docs is False
    assert reconstructed.include_mutation_testing is False
    assert reconstructed.include_ci_testing is False
    assert reconstructed.include_ci_publishing is False
    assert reconstructed.include_agent_skills is False
    assert reconstructed.init_git is False
    assert reconstructed.run_uv_sync is True
    assert reconstructed.install_git_hooks is True
    assert reconstructed.ai_tools == ("cursor", "zed")


def test_build_reproduce_command_presets() -> None:
    """Verify that build_reproduce_command maps presets and empty tools."""
    rec_config = ZenithConfig(ai_tools=PRESET_RECOMMENDED)
    assert "--ai-tools recommended" in build_reproduce_command(rec_config)

    none_config = ZenithConfig(ai_tools=())
    assert "--ai-tools none" in build_reproduce_command(none_config)


def test_render_summary_prints_recreate_command(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify that render_summary outputs recreation command and steps (REQ-009)."""
    config = ZenithConfig(project_name="Test Tool", run_uv_sync=False)
    render_summary(tmp_path / "test-tool", config)
    captured = capsys.readouterr()
    assert "Zenith Project Initialized" in captured.out
    assert "Recreate via CLI:" in captured.out
    assert "uvx zenith-template --no-input" in captured.out
    assert "uv sync" in captured.out

    # When run_uv_sync is True, uv sync step should not be printed
    synced_config = ZenithConfig(project_name="Test Tool", run_uv_sync=True)
    render_summary(tmp_path / "test-tool", synced_config)
    captured_synced = capsys.readouterr()
    assert "uv sync" not in captured_synced.out
