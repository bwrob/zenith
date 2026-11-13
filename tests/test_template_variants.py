"""Tests for the Zenith template."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.xdist_group(name="template")


# ---------------------------------------------------------------------------
# Pruning & Negative Tests (minimal_project)
# ---------------------------------------------------------------------------


def test_slugify_special_characters(minimal_project: Path) -> None:
    """Test slugification of special characters and punctuation in minimal_project."""
    assert minimal_project.exists()
    assert minimal_project.name == "zenith-s-cool-tool-v2"
    assert (minimal_project / "src" / "zenith_s_cool_tool_v2" / "__init__.py").exists()
    assert (minimal_project / "src" / "zenith_s_cool_tool_v2" / "core.py").exists()


def test_minimal_python_315_generation(minimal_project: Path) -> None:
    """Test generating a project configured with Python 3.15."""
    pyproject_text = (minimal_project / "pyproject.toml").read_text()
    assert 'requires-python = ">=3.15"' in pyproject_text
    assert "Programming Language :: Python :: 3.12" not in pyproject_text
    assert "Programming Language :: Python :: 3.13" not in pyproject_text
    assert "Programming Language :: Python :: 3.14" not in pyproject_text
    assert "Programming Language :: Python :: 3.15" in pyproject_text

    readme_text = (minimal_project / "README.md").read_text()
    assert "python-3.15+-blue.svg" in readme_text


def test_minimal_excludes_cli_files_and_dependencies(minimal_project: Path) -> None:
    """Test that include_cli=false prunes CLI modules, assets, and dependencies."""
    pkg_dir = minimal_project / "src" / "zenith_s_cool_tool_v2"
    assert (pkg_dir / "core.py").exists()
    assert not (pkg_dir / "cli.py").exists()
    assert not (pkg_dir / "_lazy.py").exists()
    assert not (pkg_dir / "__main__.py").exists()

    init_text = (pkg_dir / "__init__.py").read_text()
    assert "_lazy" not in init_text
    assert "_LAZY_MEMBERS" not in init_text
    assert not (minimal_project / "tests" / "test_cli.py").exists()
    minimal_conftest_text = (minimal_project / "tests" / "conftest.py").read_text()
    assert "runner" not in minimal_conftest_text
    assert "CliRunner" not in minimal_conftest_text
    assert not (minimal_project / "docs" / "javascripts" / "termynal.js").exists()
    assert not (minimal_project / "docs" / "stylesheets" / "termynal.css").exists()
    assert (minimal_project / "docs" / "stylesheets" / "palette.css").exists()
    assert (minimal_project / "docs" / "stylesheets" / "custom.css").exists()

    zensical_text = (minimal_project / "zensical.toml").read_text()
    assert "termynal" not in zensical_text
    assert "stylesheets/palette.css" in zensical_text
    assert "termy" not in (minimal_project / "docs" / "getting-started.md").read_text()
    assert "termy" not in (minimal_project / "docs" / "index.md").read_text()

    pyproject_text = (minimal_project / "pyproject.toml").read_text()
    assert 'dependencies = ["rich>=15.0.0"]' in pyproject_text
    assert "typer" not in pyproject_text
    assert "termynal" not in pyproject_text

    tach_text = (minimal_project / "tach.toml").read_text()
    assert '"cli"' not in tach_text
    assert re.search(r'layers\s*=\s*\[\s*"core"\s*\]', tach_text) is not None

    readme_text = (minimal_project / "README.md").read_text()
    assert "CLI Layer" not in readme_text

    ref_text = (minimal_project / "docs" / "reference.md").read_text()
    assert "::: zenith_s_cool_tool_v2.core" in ref_text
    assert "::: zenith_s_cool_tool_v2.cli" not in ref_text

    agents_text = (minimal_project / "AGENTS.md").read_text()
    assert (minimal_project / "CLAUDE.md").exists()
    assert "Use **Typer** exclusively for any command-line interfaces" in agents_text
    assert "The `core` module must never import from `cli`" not in agents_text
    assert "`core` -> external dependencies" in agents_text


def test_minimal_excludes_github_actions_and_ci(minimal_project: Path) -> None:
    """Test that include_github_actions=false prunes .github workflows and tooling."""
    assert not (minimal_project / ".github").exists()
    assert not (minimal_project / ".zizmor.yml").exists()
    assert not (minimal_project / ".agents" / "skills" / "tool-zizmor").exists()

    poe_text = (minimal_project / "poe_tasks.toml").read_text()
    assert "[tasks.zizmor]" not in poe_text
    assert '"zizmor"' not in poe_text

    readme_text = (minimal_project / "README.md").read_text()
    assert "[![CI]" not in readme_text


def test_minimal_excludes_license_file(minimal_project: Path) -> None:
    """Test that license=none prunes LICENSE file and pyproject declarations."""
    assert not (minimal_project / "LICENSE").exists()

    pyproject_text = (minimal_project / "pyproject.toml").read_text()
    assert "license =" not in pyproject_text
    assert "license-files" not in pyproject_text

    readme_text = (minimal_project / "README.md").read_text()
    assert "badge/license" not in readme_text
    assert "All rights reserved." in readme_text
    assert "[LICENSE](LICENSE)" not in readme_text


# ---------------------------------------------------------------------------
# Pre-Gen Hook Rejection Tests (No rendering)
# ---------------------------------------------------------------------------


def test_package_name_keyword_validation(temp_output_dir: Path) -> None:
    """Test that python keywords are rejected as package names."""
    with pytest.raises(FailedHookException):
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "def",
            },
        )


def test_ai_tools_invalid_preset_validation(temp_output_dir: Path) -> None:
    """Test that invalid AI tool names or presets fail pre-gen validation."""
    with pytest.raises(FailedHookException):
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "Invalid AI Tool Project",
                "ai_tools": "invalid_assistant",
            },
        )


def test_ai_tools_empty_validation(temp_output_dir: Path) -> None:
    """Test that an empty ai_tools string fails pre-gen validation."""
    with pytest.raises(FailedHookException):
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "Empty AI Tool Project",
                "ai_tools": "  ",
            },
        )


def test_ai_tools_none_renders_clean_project(temp_output_dir: Path) -> None:
    """Test that ai_tools=none completely excludes all AI configurations and skills."""
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "No AI Project",
                "ai_tools": "none",
            },
        )
    )
    assert not (rendered / "AGENTS.md").exists()
    assert not (rendered / "AI_POLICY.md").exists()
    assert not (rendered / ".agents").exists()
    assert not (rendered / "scripts" / "check_skills.py").exists()
    assert not (rendered / ".claude").exists()
    assert not (rendered / ".gemini").exists()
    assert not (rendered / ".codex").exists()
    assert not (rendered / ".opencode").exists()
    assert not (rendered / "opencode.json").exists()
    assert not (rendered / ".cursor").exists()
    assert not (rendered / ".cursorrules").exists()
    assert not (rendered / ".windsurfrules").exists()
    assert not (rendered / ".devin").exists()
    assert not (rendered / ".zed").exists()
    assert not (rendered / ".pi").exists()
    assert not (rendered / ".omp").exists()
    assert not (rendered / "HERMES.md").exists()
    assert not (rendered / "CLAUDE.md").exists()
    assert not (rendered / ".aider.conf.yml").exists()
    assert not (rendered / ".github" / "copilot-instructions.md").exists()

    poe_text = (rendered / "poe_tasks.toml").read_text()
    assert "check-skills" not in poe_text
    assert "sync-skills" not in poe_text
    assert "sdd-new" not in poe_text


def test_ai_tools_minimal_renders_context_only(temp_output_dir: Path) -> None:
    """Test that ai_tools=minimal preserves AGENTS.md but excludes tool directories."""
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "Minimal AI Project",
                "ai_tools": "minimal",
            },
        )
    )
    assert (rendered / "AGENTS.md").exists()
    assert (rendered / "AI_POLICY.md").exists()
    assert not (rendered / ".claude").exists()
    assert not (rendered / ".gemini").exists()
    assert not (rendered / ".codex").exists()
    assert not (rendered / ".opencode").exists()
    assert not (rendered / "opencode.json").exists()
    assert not (rendered / ".cursor").exists()
    assert not (rendered / ".cursorrules").exists()
    assert not (rendered / ".windsurfrules").exists()
    assert not (rendered / ".devin").exists()
    assert not (rendered / ".zed").exists()
    assert not (rendered / ".pi").exists()
    assert not (rendered / ".omp").exists()
    assert not (rendered / "HERMES.md").exists()
    assert not (rendered / "CLAUDE.md").exists()
    assert not (rendered / ".aider.conf.yml").exists()
    assert not (rendered / ".github" / "copilot-instructions.md").exists()


def test_ai_tools_custom_subset_rendering(temp_output_dir: Path) -> None:
    """Test that custom comma-separated tools only scaffold the requested assistants."""
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "Custom AI Project",
                "ai_tools": "claude, cursor, zed",
            },
        )
    )
    assert (rendered / "AGENTS.md").exists()
    assert (rendered / ".claude" / "settings.json").exists()
    assert (rendered / "CLAUDE.md").exists()
    assert (rendered / ".cursor" / "rules" / "zenith.mdc").exists()
    assert (rendered / ".cursorrules").exists()
    assert (rendered / ".zed" / "settings.json").exists()

    assert not (rendered / ".gemini").exists()
    assert not (rendered / ".codex").exists()
    assert not (rendered / ".opencode").exists()
    assert not (rendered / "opencode.json").exists()
    assert not (rendered / ".devin").exists()
    assert not (rendered / ".pi").exists()
    assert not (rendered / ".omp").exists()
    assert not (rendered / "HERMES.md").exists()
    assert not (rendered / ".windsurfrules").exists()
    assert not (rendered / ".aider.conf.yml").exists()


def test_include_agent_skills_false_prunes_skills(temp_output_dir: Path) -> None:
    """Test that include_agent_skills=false strips .agents/ while keeping configs."""
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "No Skills Project",
                "include_agent_skills": False,
                "ai_tools": "claude, cursor",
            },
        )
    )
    assert not (rendered / ".agents").exists()
    assert not (rendered / "scripts" / "check_skills.py").exists()
    assert (rendered / ".claude" / "settings.json").exists()
    assert not (rendered / ".claude" / "agents").exists()
    assert (rendered / ".cursor" / "rules" / "zenith.mdc").exists()
    assert not (rendered / ".cursor" / "agents").exists()

    poe_text = (rendered / "poe_tasks.toml").read_text()
    assert "check-skills" not in poe_text
    assert "sdd-new" not in poe_text


def test_include_docs_false_prunes_docs(temp_output_dir: Path) -> None:
    """Test that include_docs=false prunes docs directory and zensical configuration."""
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "No Docs Project",
                "include_docs": False,
            },
        )
    )
    assert not (rendered / "docs").exists()
    assert not (rendered / "zensical.toml").exists()
    assert not (rendered / ".github" / "workflows" / "docs.yaml").exists()


def test_include_mutation_testing_false_prunes_mutation(
    temp_output_dir: Path,
) -> None:
    """Test that include_mutation_testing=false prunes cosmic-ray configuration."""
    rendered = Path(
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(temp_output_dir),
            extra_context={
                "project_name": "No Mutation Project",
                "include_mutation_testing": False,
            },
        )
    )
    assert not (rendered / "cosmic-ray.toml").exists()
