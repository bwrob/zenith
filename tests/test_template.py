"""Tests for the Zenith template."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from cookiecutter.exceptions import FailedHookException
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


# ---------------------------------------------------------------------------
# Config Inventory & Agent Tooling Tests (full_project)
# ---------------------------------------------------------------------------


def test_core_configs_exist(full_project: Path) -> None:
    """Verify all core tooling and quality configuration files exist."""
    assert full_project.exists()
    assert (full_project / "pyproject.toml").exists()
    assert (full_project / "poe_tasks.toml").exists()
    assert (full_project / "ruff.toml").exists()
    assert (full_project / "pyrefly.toml").exists()
    assert (full_project / "complexipy.toml").exists()
    assert (full_project / "zensical.toml").exists()
    assert (full_project / "rumdl.toml").exists()
    assert (full_project / "tach.toml").exists()
    assert (full_project / "typos.toml").exists()
    assert (full_project / "pytest.ini").exists()
    assert (full_project / ".coveragerc").exists()
    assert (full_project / ".gitattributes").exists()
    assert (full_project / ".editorconfig").exists()
    assert (full_project / "cosmic-ray.toml").exists()


def test_agent_instruction_configs_exist(full_project: Path) -> None:
    """Verify AI assistant instruction files and configuration profiles."""
    assert (full_project / "AGENTS.md").exists()
    assert (full_project / "CLAUDE.md").exists()
    assert (full_project / "AI_POLICY.md").exists()
    assert (full_project / ".cursorrules").exists()
    assert (full_project / ".windsurfrules").exists()
    assert (full_project / ".claude" / "settings.json").exists()
    assert (full_project / ".codex" / "config.toml").exists()
    assert (full_project / ".aider.conf.yml").exists()
    assert (full_project / ".cursor" / "rules" / "zenith.mdc").exists()
    assert (full_project / ".github" / "copilot-instructions.md").exists()
    gemini_settings = (full_project / ".gemini" / "settings.json").read_text()
    assert '"contextFileName": "AGENTS.md"' in gemini_settings


def test_prek_hooks_configured(full_project: Path) -> None:
    """Verify prek hook configuration and prettier integration."""
    assert (full_project / "prek.toml").exists()
    assert (full_project / ".prettierrc.yaml").exists()
    prek_text = (full_project / "prek.toml").read_text()
    assert "prettier" in prek_text
    assert "prettier-css" in prek_text
    assert "pyrefly-coverage" in prek_text
    assert "uv-lock" in prek_text


def test_governance_and_security_files_exist(full_project: Path) -> None:
    """Verify repository governance and security metadata files."""
    assert (full_project / ".zizmor.yml").exists()
    assert (full_project / "SECURITY.md").exists()
    assert (full_project / "CONTRIBUTING.md").exists()
    assert (full_project / "CODE_OF_CONDUCT.md").exists()
    assert (full_project / ".vscode" / "extensions.json").exists()
    assert not (full_project / ".vscode" / "settings.json").exists()
    assert (full_project / ".github" / "codecov.yml").exists()


# ---------------------------------------------------------------------------
# Agent Skills & Subagents Tests (full_project)
# ---------------------------------------------------------------------------


def test_agent_skills_present(full_project: Path) -> None:
    """Verify all bundled agent skills exist in the rendered project."""
    skills = [
        "workflow-adr",
        "workflow-changelog",
        "workflow-code-review",
        "workflow-git",
        "sdd",
        "sdd-implement",
        "sdd-plan",
        "sdd-review",
        "sdd-spec",
        "workflow-setup",
        "workflow-skill-creator",
        "guide-python",
        "guide-ste100",
        "tool-complexipy",
        "tool-poethepoet",
        "tool-prettier",
        "tool-pyrefly",
        "tool-pytest",
        "tool-ruff",
        "tool-rumdl",
        "tool-tach",
        "tool-taplo",
        "tool-termynal",
        "tool-typer",
        "tool-typos",
        "tool-typst",
        "tool-uv",
        "tool-zensical",
        "tool-zizmor",
    ]
    for skill in skills:
        assert (full_project / ".agents" / "skills" / skill / "SKILL.md").exists()

    setup_skill = (
        full_project / ".agents" / "skills" / "workflow-setup" / "SKILL.md"
    ).read_text()
    assert "disable-model-invocation: true" in setup_skill
    assert "fail_under = 100" in (full_project / ".coveragerc").read_text()


def test_pytest_skill_references_exist(full_project: Path) -> None:
    """Verify tool-pytest reference documentation exists."""
    for ref in [
        "hypothesis.md",
        "pytest-cov.md",
        "pytest-randomly.md",
        "pytest-sugar.md",
        "pytest-xdist.md",
        "syrupy.md",
        "mutation_testing.md",
    ]:
        assert (
            full_project / ".agents" / "skills" / "tool-pytest" / "references" / ref
        ).exists()


def test_workflow_skill_templates_exist(full_project: Path) -> None:
    """Verify workflow skill templates and documentation references exist."""
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-changelog"
        / "templates"
        / "changelog.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-code-review"
        / "templates"
        / "review_output.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-skill-creator"
        / "templates"
        / "SKILL_TEMPLATE.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "tool-typer"
        / "examples"
        / "cli_recipe.py"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "tool-poethepoet"
        / "references"
        / "declarative_primitives.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "tool-zensical"
        / "templates"
        / "zensical.toml"
    ).exists()
    assert (
        full_project / ".agents" / "skills" / "workflow-adr" / "templates" / "adr.md"
    ).exists()


def test_sdd_skill_assets_exist(full_project: Path) -> None:
    """Verify Spec-Driven Development (SDD) templates and scripts exist."""
    assert (
        full_project / ".agents" / "skills" / "sdd-spec" / "templates" / "spec.md"
    ).exists()
    assert (
        full_project / ".agents" / "skills" / "sdd-plan" / "templates" / "plan.md"
    ).exists()
    assert (
        full_project / ".agents" / "skills" / "sdd-review" / "templates" / "review.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "sdd-review"
        / "scripts"
        / "check_public_api.py"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "sdd-review"
        / "scripts"
        / "check_traceability.py"
    ).exists()
    assert (
        full_project / ".agents" / "skills" / "sdd-spec" / "scripts" / "check_spec.py"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "sdd-spec"
        / "references"
        / "clarification-matrix.md"
    ).exists()
    assert (
        full_project / ".agents" / "skills" / "sdd" / "scripts" / "archive_feature.py"
    ).exists()
    assert (
        full_project / ".agents" / "skills" / "sdd" / "scripts" / "revert_task.py"
    ).exists()


def test_subagent_definitions_and_tool_symlinks(full_project: Path) -> None:
    """Verify agent subagents mirror the template across tool configurations."""
    for subagent in [
        "sdd-specifier.md",
        "sdd-planner.md",
        "sdd-implementer.md",
        "sdd-reviewer.md",
    ]:
        assert (full_project / ".agents" / "subagents" / subagent).exists()
        for tool_dir in (".claude", ".gemini", ".cursor"):
            generated_agent = full_project / tool_dir / "agents" / subagent
            template_agent = TEMPLATE_ROOT / tool_dir / "agents" / subagent
            assert generated_agent.exists()
            assert template_agent.exists()
            assert generated_agent.read_text() == template_agent.read_text()

        agent_name = Path(subagent).stem
        generated_codex_agent = (
            full_project / ".codex" / "agents" / f"{agent_name}.toml"
        )
        template_codex_agent = (
            TEMPLATE_ROOT / ".codex" / "agents" / f"{agent_name}.toml"
        )
        assert generated_codex_agent.exists()
        assert template_codex_agent.exists()
        generated_codex_config = tomllib.loads(generated_codex_agent.read_text())
        template_codex_config = tomllib.loads(template_codex_agent.read_text())
        assert generated_codex_config == template_codex_config
        assert {"name", "description", "developer_instructions"} <= set(
            generated_codex_config
        )
        assert generated_codex_config["name"] == agent_name

        source_text = (full_project / ".agents" / "subagents" / subagent).read_text()
        _, delimiter, instructions = source_text.partition("\n---\n")
        assert delimiter
        assert generated_codex_config["developer_instructions"] == instructions.strip()
        assert not (full_project / ".codex" / "agents" / subagent).exists()


# ---------------------------------------------------------------------------
# Project Layout Tests (full_project)
# ---------------------------------------------------------------------------


def test_project_source_and_adr_layout(full_project: Path) -> None:
    """Verify skill lint assets, ADR directory, and package source layout."""
    assert (
        full_project / ".agents" / "skills" / "guide-ste100" / "scripts" / "ste-lint.py"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "guide-ste100"
        / "references"
        / "writing-rules.md"
    ).exists()
    assert (full_project / "docs" / "adr" / "index.md").exists()
    assert (full_project / "docs" / "adr" / "template.md").exists()
    assert (
        full_project / "docs" / "adr" / "0001-record-architecture-decisions.md"
    ).exists()
    assert (full_project / "scripts" / "check_skills.py").exists()
    assert (full_project / "src" / "demo_app" / "__init__.py").exists()
    assert (full_project / "src" / "demo_app" / "_lazy.py").exists()
    assert (full_project / "src" / "demo_app" / "cli.py").exists()
    assert (full_project / "src" / "demo_app" / "__main__.py").exists()


def test_project_lazy_import_wiring(full_project: Path) -> None:
    """Verify PEP 562 lazy loading setup in package __init__.py."""
    init_text = (full_project / "src" / "demo_app" / "__init__.py").read_text()
    assert "_lazy" in init_text
    assert "lazy_getattr" in init_text
    assert (
        'lazy_getattr(globals(), {"app": ".cli", "get_greeting": ".core"})' in init_text
    )
    assert "lazy_dir(globals())" in init_text
    assert (
        full_project
        / "src"
        / "demo_app"
        / ".agents"
        / "skills"
        / "demo-app"
        / "SKILL.md"
    ).exists()


def test_project_tests_and_docs_layout(full_project: Path) -> None:
    """Verify test suites, snapshot assets, and documentation stylesheets."""
    assert (full_project / "tests" / "test_core.py").exists()
    assert (full_project / "tests" / "__snapshots__" / "test_core.ambr").exists()
    assert (full_project / "tests" / "test_cli.py").exists()
    assert (full_project / "docs" / "index.md").exists()
    docs_index_text = (full_project / "docs" / "index.md").read_text()
    assert "https://github.com/bwrob/zenith" in docs_index_text
    assert "https://bwrob.dev" in docs_index_text
    assert "Built with the <a href=" in docs_index_text
    assert (full_project / "docs" / "changelog.md").exists()
    assert (full_project / "docs" / "javascripts" / "mathjax.js").exists()
    assert (full_project / "docs" / "javascripts" / "termynal.js").exists()
    assert (full_project / "docs" / "stylesheets" / "palette.css").exists()
    assert (full_project / "docs" / "stylesheets" / "custom.css").exists()
    assert (full_project / "docs" / "stylesheets" / "termynal.css").exists()
    assert (full_project / "docs" / "assets" / "python-logo.svg").exists()
    assert (full_project / "docs" / "assets" / "python-logo.typ").exists()
    assert (full_project / "scripts" / "verify_wheel.py").exists()


# ---------------------------------------------------------------------------
# Workflows & Dependabot Tests (full_project)
# ---------------------------------------------------------------------------


def test_github_workflows_and_dependabot(full_project: Path) -> None:
    """Verify GitHub workflows, dependabot, and issue templates."""
    assert (full_project / ".github" / "workflows" / "python_tests.yaml").exists()
    assert (full_project / ".github" / "workflows" / "guard-dependencies.yaml").exists()
    guard_text = (
        full_project / ".github" / "workflows" / "guard-dependencies.yaml"
    ).read_text()
    assert "timeout-minutes: 5" in guard_text
    assert (full_project / ".github" / "workflows" / "docs.yaml").exists()
    assert (full_project / ".github" / "workflows" / "publish.yaml").exists()
    assert (full_project / ".github" / "workflows" / "test_redistribute.yaml").exists()
    assert (
        full_project / ".github" / "workflows" / "dependabot-automerge.yaml"
    ).exists()
    publish_text = (full_project / ".github" / "workflows" / "publish.yaml").read_text()
    assert "UV_EXCLUDE_NEWER" in publish_text
    assert "python scripts/verify_wheel.py" in publish_text
    redist_text = (
        full_project / ".github" / "workflows" / "test_redistribute.yaml"
    ).read_text()
    assert "scripts/verify_wheel.py" in redist_text

    dependabot_text = (full_project / ".github" / "dependabot.yml").read_text()
    assert 'package-ecosystem: "uv"' in dependabot_text
    assert '"github_actions"' in dependabot_text
    assert '"python"' in dependabot_text
    assert (full_project / ".github" / "PULL_REQUEST_TEMPLATE.md").exists()
    assert (full_project / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml").exists()
    assert (
        full_project / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
    ).exists()
    assert (full_project / ".github" / "ISSUE_TEMPLATE" / "config.yml").exists()


# ---------------------------------------------------------------------------
# Poe Tasks Surface Tests (full_project)
# ---------------------------------------------------------------------------


def test_poe_tasks_core_definitions(full_project: Path) -> None:
    """Verify core Poe task definitions in poe_tasks.toml."""
    poe_text = (full_project / "poe_tasks.toml").read_text()
    assert "[tasks.zizmor]" in poe_text
    assert '"zizmor"' in poe_text
    zizmor_cmd = (
        "zizmor --config .zizmor.yml --pedantic "
        "--min-severity informational .github/workflows"
    )
    assert zizmor_cmd in poe_text
    assert "[tasks.format-toml]" in poe_text
    assert "[tasks.format-check-toml]" in poe_text
    assert "[tasks.format-yaml]" in poe_text
    assert "[tasks.format-css]" in poe_text
    assert '"format-check-toml"' in poe_text
    assert '"taplo format"' in poe_text
    assert "[tasks.sdd-new]" in poe_text
    assert "[tasks.sdd-plan]" in poe_text
    assert "[tasks.sdd-review]" in poe_text
    assert "[tasks.sdd-verify]" in poe_text
    assert "[tasks.sdd-archive]" in poe_text
    assert "[tasks.sdd-revert]" in poe_text


def test_poe_task_surface_and_ci_steps(full_project: Path) -> None:
    """Verify the full Poe task surface and CI workflow steps."""
    poe_text = (full_project / "poe_tasks.toml").read_text()
    assert "tasks.precommit" not in poe_text
    assert '"precommit"' not in poe_text
    assert "tasks.format-check" in poe_text
    assert "tasks.format-yaml" in poe_text
    assert "tasks.format-css" in poe_text
    assert "tasks.test-fast" in poe_text
    assert "--dist=worksteal --max-worker-restart=0" in poe_text
    assert "tasks.test-lowest" in poe_text
    assert "tasks.test-sdist" in poe_text
    assert "tasks.verify-wheel" in poe_text
    assert "python scripts/verify_wheel.py" in poe_text
    assert "tasks.test-snapshot-update" in poe_text
    assert "tasks.test-mutation" in poe_text
    assert "tasks.test-mutation-cosmic" in poe_text
    assert "tasks.type-coverage" in poe_text
    assert '"type-coverage"' in poe_text
    assert "tasks.check-skills" in poe_text
    assert "tasks.repl" in poe_text
    assert '"check-skills"' in poe_text
    assert "tasks.zizmor" in poe_text
    assert "tasks.audit" in poe_text
    assert "uv audit" in poe_text
    assert "tasks.check-api" in poe_text
    assert "griffe check demo_app --search src" in poe_text
    assert '"deptry src"' in poe_text
    assert "tach check-external" not in poe_text
    assert "deptry>=0.25.1" in (full_project / "pyproject.toml").read_text()
    assert "tasks.sync-skills" in poe_text
    assert "tasks.docs-logo" in poe_text
    assert "tasks.clean" in poe_text
    assert "tasks._clean-dist" in poe_text
    assert "tasks._clean-mutation" in poe_text
    assert "tasks._clean-cosmic" in poe_text

    python_tests_yaml = (
        full_project / ".github" / "workflows" / "python_tests.yaml"
    ).read_text()
    assert "codecov/codecov-action@v7" in python_tests_yaml
    assert "griffe check" in python_tests_yaml


# ---------------------------------------------------------------------------
# Pyproject Surface Tests (full_project)
# ---------------------------------------------------------------------------


def test_pyproject_dependencies_and_groups(full_project: Path) -> None:
    """Verify pyproject.toml dependencies, default groups, and optional groups."""
    pyproject_text = (full_project / "pyproject.toml").read_text()
    assert re.search(r'license\s*=\s*"MIT"', pyproject_text) is not None
    assert (
        re.search(r'license-files\s*=\s*\[\s*"LICENSE"\s*\]', pyproject_text)
        is not None
    )
    assert "griffe-warnings-deprecated>=" in pyproject_text
    assert "griffe>=" in pyproject_text
    assert "mutation" in pyproject_text
    assert "mutmut>=" in pyproject_text
    assert "cosmic-ray>=" in pyproject_text
    assert "[tool.mutmut]" in pyproject_text
    assert "markdown-exec" in pyproject_text
    assert "Programming Language :: Python :: 3.15" in pyproject_text
    assert "Typing :: Typed" in pyproject_text
    assert "hypothesis" in pyproject_text
    assert "pytest-randomly" in pyproject_text
    assert "pytest-sugar" in pyproject_text
    assert "pytest-xdist" in pyproject_text
    assert "syrupy" in pyproject_text
    assert "typos" in pyproject_text
    assert "typst" in pyproject_text
    assert "zizmor" in pyproject_text
    assert "rich>=" in pyproject_text
    assert "typer>=" in pyproject_text
    assert 'dependencies = ["rich>=15.0.0", "typer>=0.16.0"]' in pyproject_text
    assert 'demo-app = "demo_app.__main__:main"' in pyproject_text
    assert "default-groups = [" in pyproject_text
    assert "test = [" in pyproject_text
    assert "lint = [" in pyproject_text
    assert "docs = [" in pyproject_text
    assert "mkdocstrings[python]" in pyproject_text
    assert "source-include = [" in pyproject_text


# ---------------------------------------------------------------------------
# Zensical Configuration Tests (full_project)
# ---------------------------------------------------------------------------


def test_zensical_plugins_and_validation(full_project: Path) -> None:
    """Verify zensical plugin activations and validation options."""
    zensical_text = (full_project / "zensical.toml").read_text()
    assert "markdown_exec.validator" in zensical_text
    assert "[project.validation]" in zensical_text
    assert "invalid_links" in zensical_text
    assert "invalid_link_anchors" in zensical_text
    assert "[project.plugins.mkdocstrings]" in zensical_text
    assert "navigation.instant.preview" in zensical_text
    assert "search.suggest" in zensical_text
    assert "toc.follow" in zensical_text
    assert re.search(r"signature_crossrefs\s*=\s*true", zensical_text) is not None
    assert re.search(r'members_order\s*=\s*"source"', zensical_text) is not None
    assert (
        re.search(r"pymdownx\.snippets\.check_paths\s*=\s*true", zensical_text)
        is not None
    )
    assert (
        re.search(r"pymdownx\.snippets\.dedent_subsections\s*=\s*true", zensical_text)
        is not None
    )
    assert (
        re.search(
            r'zensical\.extensions\.preview\.targets\.include\s*=\s*\[\s*"\*"\s*\]',
            zensical_text,
        )
        is not None
    )
    assert "[project.plugins.gh-admonitions]" in zensical_text
    assert "[project.plugins.markdown-exec]" in zensical_text
    assert "[project.plugins.llmstxt]" in zensical_text
    assert re.search(r'full_output\s*=\s*"llms-full.txt"', zensical_text) is not None
    assert "changelog.md" in zensical_text


def test_zensical_mkdocstrings_options(full_project: Path) -> None:
    """Verify mkdocstrings options and crossref configuration in zensical.toml."""
    zensical_text = (full_project / "zensical.toml").read_text()
    assert (
        re.search(
            r'inventories\s*=\s*\[\s*"https://docs\.python\.org/3/objects\.inv"\s*\]',
            zensical_text,
        )
        is not None
    )
    assert re.search(r'options\.backlinks\s*=\s*"tree"', zensical_text) is not None
    assert (
        re.search(
            r'options\.extensions\s*=\s*\[\s*"griffe_warnings_deprecated"\s*\]',
            zensical_text,
        )
        is not None
    )
    assert re.search(r"options\.line_length\s*=\s*88", zensical_text) is not None
    assert (
        re.search(r"options\.relative_crossrefs\s*=\s*true", zensical_text) is not None
    )
    assert re.search(r"options\.scoped_crossrefs\s*=\s*true", zensical_text) is not None
    assert (
        re.search(r"options\.show_inheritance_diagram\s*=\s*true", zensical_text)
        is not None
    )
    assert (
        re.search(r"options\.show_signature_type_parameters\s*=\s*true", zensical_text)
        is not None
    )
    assert re.search(r"options\.summary\s*=\s*true", zensical_text) is not None
    assert (
        re.search(r"options\.type_parameter_headings\s*=\s*true", zensical_text)
        is not None
    )
    assert (
        re.search(r"options\.show_symbol_type_heading\s*=\s*true", zensical_text)
        is not None
    )
    assert (
        re.search(r"options\.show_symbol_type_toc\s*=\s*true", zensical_text)
        is not None
    )
    assert (
        re.search(r"options\.parameter_headings\s*=\s*true", zensical_text) is not None
    )
    assert (
        re.search(
            r"options\.docstring_options\.ignore_init_summary\s*=\s*true",
            zensical_text,
        )
        is not None
    )
    assert (
        re.search(r'options\.annotations_path\s*=\s*"brief"', zensical_text) is not None
    )
    assert re.search(r"options\.show_bases\s*=\s*true", zensical_text) is not None


def test_zensical_assets_and_navigation(full_project: Path) -> None:
    """Verify zensical stylesheets, scripts, and navigation entries."""
    zensical_text = (full_project / "zensical.toml").read_text()
    assert "stylesheets/palette.css" in zensical_text
    assert "stylesheets/custom.css" in zensical_text
    assert "stylesheets/termynal.css" in zensical_text
    assert "javascripts/termynal.js" in zensical_text
    assert "javascripts/mathjax.js" in zensical_text
    assert '{ name = "tree"' in zensical_text
    assert "navigation.indexes" in zensical_text
    assert '"adr/index.md"' in zensical_text


# ---------------------------------------------------------------------------
# Policy Files & Documentation Reference Tests (full_project)
# ---------------------------------------------------------------------------


def test_agents_and_coverage_policies(full_project: Path) -> None:
    """Verify AGENTS.md stewardship and coverage policy rules."""
    agents_text = (full_project / "AGENTS.md").read_text()
    assert "## Project Stewardship" in agents_text
    assert "never double backticks" in agents_text
    assert "Reproduce-First Bug Scoping" in agents_text
    assert "Complexity Reset Rule" in agents_text

    coveragerc_text = (full_project / ".coveragerc").read_text()
    assert "tests" in coveragerc_text
    assert "*/__snapshots__/*" in coveragerc_text
    assert "tests/*" not in coveragerc_text
    assert "core = sysmon" in coveragerc_text
    assert "skip_empty = true" in coveragerc_text
    assert "patch =\n    subprocess\n    _exit" in coveragerc_text
    assert r"return NotImplemented\b" in coveragerc_text
    assert r"(typing\.)?assert_never" in coveragerc_text


def test_pytest_and_linter_policies(full_project: Path) -> None:
    """Verify pytest.ini, pyrefly, and ruff policies."""
    pytest_ini_text = (full_project / "pytest.ini").read_text()
    assert "-q" in pytest_ini_text
    assert "-ra" in pytest_ini_text
    assert "--durations=3" in pytest_ini_text
    assert "--snapshot-warn-unused" in pytest_ini_text
    assert "empty_parameter_set_mark = fail_at_collect" in pytest_ini_text
    assert "faulthandler_timeout   = 60" in pytest_ini_text
    assert "default::EncodingWarning" in pytest_ini_text
    assert "error::EncodingWarning:demo_app.*" in pytest_ini_text
    assert "minversion             = 9.0" in pytest_ini_text
    assert "strict                 = true" in pytest_ini_text
    assert "log_level              = DEBUG" in pytest_ini_text
    assert "DONT_ACCEPT_TRUE_FOR_1" in pytest_ini_text

    pyrefly_text = (full_project / "pyrefly.toml").read_text()
    pyrefly_config = tomllib.loads(pyrefly_text)
    assert pyrefly_config["enabled-ignores"] == ["pyrefly"]

    ruff_toml_text = (full_project / "ruff.toml").read_text()
    assert "combine-as-imports = true" in ruff_toml_text
    assert "extend-immutable-calls" in ruff_toml_text
    assert "required-imports" in ruff_toml_text
    assert "future-annotations = true" in ruff_toml_text


def test_docs_reference_and_diagrams(full_project: Path) -> None:
    """Verify docs reference pages, zensical build tasks, and publish workflows."""
    ref_text = (full_project / "docs" / "reference.md").read_text()
    assert "::: demo_app.core" in ref_text
    assert "::: demo_app.cli" in ref_text
    assert "site/llms.txt" in ref_text
    index_text = (full_project / "docs" / "index.md").read_text()
    assert 'class="termy"' in index_text
    assert '=== "uv (Recommended)"' in index_text
    assert "```tree" in index_text
    getting_started_text = (full_project / "docs" / "getting-started.md").read_text()
    assert 'class="termy"' in getting_started_text
    assert "???+ tip" in getting_started_text
    assert "- [x]" in getting_started_text
    assert "sequenceDiagram" in getting_started_text
    assert "stateDiagram-v2" in getting_started_text

    poe_text = (full_project / "poe_tasks.toml").read_text()
    assert 'cmd  = "zensical serve"' in poe_text
    assert "zensical build --strict" in poe_text
    docs_yaml_text = (full_project / ".github" / "workflows" / "docs.yaml").read_text()
    assert "zensical build --clean --strict" in docs_yaml_text
    assert "uv sync --group docs" in docs_yaml_text

    publish_yaml_text = (
        full_project / ".github" / "workflows" / "publish.yaml"
    ).read_text()
    assert "attestations: write" in publish_yaml_text
    assert "actions/attest-build-provenance@v4" in publish_yaml_text
    assert "attestations: true" in publish_yaml_text


def test_ci_matrix_and_tools_integration(full_project: Path) -> None:
    """Verify CI workflow matrix split, prek typos, and Tach layer setup."""
    rumdl_text = (full_project / "rumdl.toml").read_text()
    assert '"py"' in rumdl_text
    assert '"ruff:check"' in rumdl_text

    ci_text = (full_project / ".github" / "workflows" / "python_tests.yaml").read_text()
    assert "concurrency:" in ci_text
    assert "cancel-in-progress: true" in ci_text
    assert "quality:" in ci_text
    assert "test:" in ci_text
    assert "test-lowest:" in ci_text
    assert "test-dist:" in ci_text
    assert "uv sync --frozen --group test" in ci_text
    assert "uv sync --group test --resolution lowest-direct" in ci_text
    assert "poe format-check" in ci_text
    assert "poe typos" in ci_text
    assert "UV_EXCLUDE_NEWER" in ci_text
    assert (
        "UV_EXCLUDE_NEWER"
        in (
            full_project / ".github" / "workflows" / "test_redistribute.yaml"
        ).read_text()
    )
    assert "GITHUB_STEP_SUMMARY" in ci_text
    assert "uv run poe fix" in ci_text
    assert "uv run poe test-lowest" in ci_text
    assert (
        "GITHUB_STEP_SUMMARY"
        in (full_project / ".github" / "workflows" / "docs.yaml").read_text()
    )
    assert "exclude-newer" in (full_project / "pyproject.toml").read_text()
    assert (
        "uv run poe test-lowest"
        in (
            full_project / ".agents" / "skills" / "tool-pytest" / "SKILL.md"
        ).read_text()
    )
    assert (
        "exclude-newer"
        in (full_project / ".agents" / "skills" / "tool-uv" / "SKILL.md").read_text()
    )

    prek_text = (full_project / "prek.toml").read_text()
    assert "crate-ci/typos" in prek_text

    tach_text = (full_project / "tach.toml").read_text()
    tach_config = tomllib.loads(tach_text)
    assert tach_config["source_roots"] == ["src"]
    assert 'path       = "demo_app"' in tach_text
    assert 'path       = "demo_app.__main__"' in tach_text
    assert "ignore_type_checking_imports = true" in tach_text


def test_hardened_configs_and_ai_disclosure(full_project: Path) -> None:
    """Verify hardened test configurations and AI policy disclosures."""
    pytest_text = (full_project / "pytest.ini").read_text()
    assert "--import-mode=importlib" in pytest_text
    assert "--strict-config" in pytest_text
    assert "--strict-markers" in pytest_text
    assert "xfail_strict" in pytest_text
    assert "filterwarnings" in pytest_text

    ruff_text = (full_project / "ruff.toml").read_text()
    assert 'ban-relative-imports = "all"' in ruff_text
    assert "keep-runtime-typing = true" in ruff_text
    assert '"tests/**/*" = ["assert"]' in ruff_text
    assert '"scripts/*" = ["suspicious-subprocess-import"]' in ruff_text
    assert '"COM",' not in ruff_text
    assert '"too-many-branches",' not in ruff_text

    coverage_text = (full_project / ".coveragerc").read_text()
    assert "@overload" in coverage_text

    ai_policy_text = (full_project / "AI_POLICY.md").read_text()
    assert "Human-in-the-Loop" in ai_policy_text
    assert (TEMPLATE_ROOT / "AI_POLICY.md").exists()

    pr_template_text = (
        full_project / ".github" / "PULL_REQUEST_TEMPLATE.md"
    ).read_text()
    assert "AI Assistance Disclosure" in pr_template_text


def test_readme_and_agent_symlinks(full_project: Path) -> None:
    """Verify README content, elevator pitch, and instruction symlinks."""
    readme_text = (full_project / "README.md").read_text()
    assert "Elevator Pitch" in readme_text
    assert "Elevator Pitch" in (TEMPLATE_ROOT / "README.md").read_text()
    assert "CLI Layer" in readme_text
    assert "license-MIT" in readme_text
    assert "Verify Wheel" in readme_text
    assert "https://github.com/bwrob/zenith" in readme_text
    assert "https://bwrob.dev" in readme_text
    assert "Built with the <a href=" in readme_text

    agents_text = (full_project / "AGENTS.md").read_text()
    assert "uv run poe --help" in agents_text
    assert "Use **Typer** exclusively for any command-line interfaces" in agents_text
    assert "`cli` -> `core` -> external dependencies" in agents_text
    assert ".temp/" in agents_text
    assert ".temp/" in (full_project / ".gitignore").read_text()
    assert ".specs/" in (full_project / ".gitignore").read_text()
    assert (full_project / "CLAUDE.md").read_text() == agents_text
    assert (full_project / ".cursorrules").read_text() == agents_text
    assert (full_project / ".windsurfrules").read_text() == agents_text
    if (full_project / "CLAUDE.md").is_symlink():  # pragma: no branch
        assert (full_project / "CLAUDE.md").readlink() == Path("AGENTS.md")
        assert (full_project / ".cursorrules").readlink() == Path("AGENTS.md")
        assert (full_project / ".windsurfrules").readlink() == Path("AGENTS.md")

    assert "uv run poe:*" in (full_project / ".claude" / "settings.json").read_text()
    assert "workspace-write" in (full_project / ".codex" / "config.toml").read_text()
    assert "AGENTS.md" in (full_project / ".aider.conf.yml").read_text()
    copilot_text = (full_project / ".github" / "copilot-instructions.md").read_text()
    assert "AGENTS.md" in copilot_text
    assert "comment: off" in (full_project / ".github" / "codecov.yml").read_text()


# ---------------------------------------------------------------------------
# Integration Tests (full_project)
# ---------------------------------------------------------------------------


def test_rendered_docs_pass_strict_build(full_project: Path) -> None:
    """Verify that rendered docs pass Zensical strict build and Rumdl markdown lint."""
    adr_text = (full_project / "docs" / "adr" / "index.md").read_text()
    assert (
        "https://github.com/zenith-template-tests/demo-app/blob/main/"
        ".agents/skills/workflow-adr/SKILL.md" in adr_text
    )

    zensical = shutil.which("zensical")
    assert zensical is not None
    build = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [zensical, "build", "--clean", "--strict"],
        capture_output=True,
        check=False,
        cwd=full_project,
        text=True,
    )
    assert build.returncode == 0, f"{build.stdout}\n{build.stderr}"

    rumdl = shutil.which("rumdl")
    assert rumdl is not None
    markdown_check = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [rumdl, "check", "docs/adr/index.md"],
        capture_output=True,
        check=False,
        cwd=full_project,
        text=True,
    )
    assert markdown_check.returncode == 0, (
        f"{markdown_check.stdout}\n{markdown_check.stderr}"
    )


def test_native_booleans_and_dynamic_year(full_project: Path) -> None:
    """Test dynamic year injection into LICENSE."""
    current_year = str(datetime.now(UTC).year)
    license_text = (full_project / "LICENSE").read_text()
    assert f"Copyright (c) {current_year}" in license_text


def test_generated_toml_formatting_with_taplo(full_project: Path) -> None:
    """Test that every generated TOML file adheres to Taplo formatting."""
    taplo_bin = shutil.which("taplo")
    assert taplo_bin is not None, (
        "taplo executable must be available in dev environment"
    )

    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [taplo_bin, "format", "--check"],
        cwd=str(full_project),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, (
        f"Taplo format check failed on generated files:\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_lazy_load_behavior(full_project: Path) -> None:
    """Test that PEP 562 lazy loading prevents eager submodule imports."""
    verify_code = """
import sys
import os

sys.path.insert(0, os.path.abspath("src"))
import demo_app

# 1. demo_app.cli and demo_app.__main__ must NOT be imported eagerly on package import
assert "demo_app.cli" not in sys.modules, "demo_app.cli was imported eagerly!"
assert "demo_app.__main__" not in sys.modules, "demo_app.__main__ was imported eagerly!"

# 2. Accessing core function directly via lazy resolution works
greeting = demo_app.get_greeting("Antigravity")
assert greeting == "Hello, Antigravity!"
assert "demo_app.core" in sys.modules
assert "demo_app.cli" not in sys.modules, "demo_app.cli was imported by get_greeting!"

# 3. dir() returns lazily exported members and globals
members = dir(demo_app)
assert "app" in members
assert "get_greeting" in members
assert "__version__" in members

# 4. Unknown attribute raises AttributeError
try:
    demo_app.nonexistent_symbol
except AttributeError:
    pass
else:
    raise AssertionError("AttributeError not raised for missing member")
"""
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [sys.executable, "-c", verify_code],
        cwd=str(full_project),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, (
        f"Lazy loading test failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_verify_wheel_execution(full_project: Path) -> None:
    """Test verify_wheel.py builds the wheel in an isolated venv."""
    verify_script = full_project / "scripts" / "verify_wheel.py"
    assert verify_script.exists()
    subprocess_env = os.environ.copy()
    subprocess_env.pop("COVERAGE_FILE", None)

    # Execute verify_wheel.py directly inside the generated project
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [sys.executable, str(verify_script)],
        cwd=str(full_project),
        env=subprocess_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, (
        f"verify_wheel.py failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "Wheel verification successful" in result.stdout

    # Execute verify_wheel.py with --run-tests to verify test suite against distribution
    result_tests = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [sys.executable, str(verify_script), "--run-tests"],
        cwd=str(full_project),
        env=subprocess_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result_tests.returncode == 0, (
        f"verify_wheel.py --run-tests failed:\n"
        f"STDOUT:\n{result_tests.stdout}\nSTDERR:\n{result_tests.stderr}"
    )
    assert "Distribution test suite passed successfully" in result_tests.stdout


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
