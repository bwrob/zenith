"""Unit tests for Zenith programmatic Cookiecutter generator."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from zenith.generator import generate_project, run_cmd
from zenith.models import ZenithConfig

if TYPE_CHECKING:
    from pathlib import Path

MIN_COMMAND_COUNT = 2


def test_generate_project_calls_cookiecutter(tmp_path: Path) -> None:
    """Verify generate_project calls cookiecutter with context (REQ-005)."""
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


def test_generate_project_runs_post_scaffold_automation(tmp_path: Path) -> None:
    """Verify generate_project runs lifecycle commands when enabled (REQ-008)."""
    config = ZenithConfig(
        project_slug="automated-project",
        init_git=True,
        run_uv_sync=True,
        install_git_hooks=True,
    )
    fake_template = tmp_path / "template"
    fake_template.mkdir()
    target_dir = tmp_path / "automated-project"

    def fake_cookiecutter(**_kwargs: object) -> str:
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / ".git").mkdir(parents=True, exist_ok=True)
        return str(target_dir)

    steps: list[str] = []
    with (
        patch("zenith.generator.get_template_path", return_value=fake_template),
        patch("zenith.generator.cookiecutter", side_effect=fake_cookiecutter),
        patch("zenith.generator.run_cmd") as mock_cmd,
    ):
        result = generate_project(config, output_dir=tmp_path, on_step=steps.append)
        assert result == target_dir
        called_cmds = [call.args[0] for call in mock_cmd.call_args_list]
        assert ["uv", "sync"] in called_cmds
        assert ["uv", "run", "taplo", "format"] in called_cmds
        assert ["uv", "run", "prek", "install"] in called_cmds
        assert any("Scaffolding project template" in s for s in steps)
        assert any("uv sync" in s for s in steps)
        assert any("taplo format" in s for s in steps)
        assert any("prek install" in s for s in steps)


def test_generate_project_runs_git_init_when_git_missing(tmp_path: Path) -> None:
    """Verify that git init is executed when .git does not exist."""
    config = ZenithConfig(
        project_slug="fresh-git-project",
        init_git=True,
        run_uv_sync=False,
        install_git_hooks=True,
    )
    fake_template = tmp_path / "template"
    fake_template.mkdir()
    target_dir = tmp_path / "fresh-git-project"

    def fake_cookiecutter(**_kwargs: object) -> str:
        target_dir.mkdir(parents=True, exist_ok=True)
        return str(target_dir)

    with (
        patch("zenith.generator.get_template_path", return_value=fake_template),
        patch("zenith.generator.cookiecutter", side_effect=fake_cookiecutter),
        patch("zenith.generator.run_cmd") as mock_cmd,
    ):
        result = generate_project(config, output_dir=tmp_path)
        assert result == target_dir
        called_cmds = [call.args[0] for call in mock_cmd.call_args_list]
        assert ["git", "init"] in called_cmds
        # Since .git was never created, prek install shouldn't run
        assert ["uv", "run", "prek", "install"] not in called_cmds


def test_generate_project_skips_post_scaffold_when_disabled(
    tmp_path: Path,
) -> None:
    """Verify that generate_project skips lifecycle commands when disabled."""
    config = ZenithConfig(
        project_slug="no-automation-project",
        init_git=False,
        run_uv_sync=False,
        install_git_hooks=False,
    )
    fake_template = tmp_path / "template"
    fake_template.mkdir()
    target_dir = tmp_path / "no-automation-project"
    target_dir.mkdir()

    with (
        patch("zenith.generator.get_template_path", return_value=fake_template),
        patch("zenith.generator.cookiecutter", return_value=str(target_dir)),
        patch("zenith.generator.run_cmd") as mock_cmd,
    ):
        result = generate_project(config, output_dir=tmp_path)
        assert result == target_dir
        mock_cmd.assert_not_called()


def test_run_cmd_handles_exceptions(tmp_path: Path) -> None:
    """Verify run_cmd safely suppresses subprocess errors."""
    # Calling a nonexistent command should be cleanly suppressed
    run_cmd(["nonexistent-command-xyz-123"], cwd=tmp_path)


def test_generate_project_expands_tilde_in_output_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Expand tilde home shortcuts in generate_project output directories.

    Bug: ``generate_project`` resolved ``~/...`` relative to the current
    working directory, bypassing collision checks and creating a literal
    ``./~`` folder instead of using the user's home directory.
    Root cause: ``validate_output_dir`` and UI previews called
    ``.expanduser()``, while ``generate_project`` called ``.resolve()`` alone.
    Fix: Call ``.expanduser().resolve()`` in ``generate_project`` and
    ``_build_feature_flags``.
    """
    fake_home = tmp_path / "home"
    fake_cwd = tmp_path / "cwd"
    fake_home.mkdir()
    fake_cwd.mkdir()

    existing_target = fake_home / "projects" / "my-app"
    existing_target.mkdir(parents=True)
    (existing_target / "existing.txt").write_text("do not overwrite", encoding="utf-8")

    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    monkeypatch.chdir(fake_cwd)

    colliding = ZenithConfig(
        project_slug="my-app",
        output_dir="~/projects",
        init_git=False,
        run_uv_sync=False,
        install_git_hooks=False,
    )
    with (
        patch("zenith.generator.cookiecutter") as mock_cc,
        pytest.raises(FileExistsError),
    ):
        generate_project(colliding, output_dir="~/projects", overwrite=False)
    mock_cc.assert_not_called()

    fresh = ZenithConfig(
        project_slug="fresh-app",
        output_dir="~/projects",
        init_git=False,
        run_uv_sync=False,
        install_git_hooks=False,
    )
    fake_template = tmp_path / "template"
    fake_template.mkdir()
    expected_out = fake_home / "projects"
    with (
        patch("zenith.generator.get_template_path", return_value=fake_template),
        patch(
            "zenith.generator.cookiecutter",
            return_value=str(expected_out / "fresh-app"),
        ) as mock_cc,
    ):
        result = generate_project(fresh, output_dir="~/projects", overwrite=False)
        assert result == expected_out / "fresh-app"
        assert mock_cc.call_args.kwargs["output_dir"] == str(expected_out)


def test_generate_project_honors_git_and_hooks_flags(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Honor init_git and install_git_hooks during real post-gen hook execution.

    Bug: `generate_project` omitted `init_git` and `install_git_hooks` from
    the Cookiecutter execution environment, so `post_gen_project.py`
    unconditionally ran `git init` and `prek install`.
    Root cause: `hooks/post_gen_project.py:init_prek` always executed
    `git init` and `prek install` without reading environment overrides from
    `generate_project`.
    Fix: Set `ZENITH_INIT_GIT` and `ZENITH_INSTALL_GIT_HOOKS` inside
    `_temporary_hook_env` around `cookiecutter()` while restoring prior env
    values, and gate `init_prek()` on those flags.
    """
    monkeypatch.delenv("ZENITH_INIT_GIT", raising=False)
    monkeypatch.delenv("ZENITH_INSTALL_GIT_HOOKS", raising=False)

    no_git_config = ZenithConfig(
        project_name="No Git App",
        project_slug="no-git-app",
        package_name="no_git_app",
        init_git=False,
        run_uv_sync=False,
        install_git_hooks=False,
    )
    no_git_dir = generate_project(no_git_config, output_dir=tmp_path)
    assert not (no_git_dir / ".git").exists()
    assert "ZENITH_INIT_GIT" not in os.environ
    assert "ZENITH_INSTALL_GIT_HOOKS" not in os.environ

    monkeypatch.setenv("ZENITH_INIT_GIT", "sentinel-init")
    monkeypatch.setenv("ZENITH_INSTALL_GIT_HOOKS", "sentinel-hooks")

    git_no_hooks_config = ZenithConfig(
        project_name="Git No Hooks App",
        project_slug="git-no-hooks-app",
        package_name="git_no_hooks_app",
        init_git=True,
        run_uv_sync=False,
        install_git_hooks=False,
    )
    git_no_hooks_dir = generate_project(git_no_hooks_config, output_dir=tmp_path)
    assert (git_no_hooks_dir / ".git").is_dir()
    assert not (git_no_hooks_dir / ".git" / "hooks" / "pre-commit").exists()
    assert not (git_no_hooks_dir / ".git" / "hooks" / "pre-push").exists()
    assert os.environ.get("ZENITH_INIT_GIT") == "sentinel-init"
    assert os.environ.get("ZENITH_INSTALL_GIT_HOOKS") == "sentinel-hooks"
