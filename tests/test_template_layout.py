"""Tests for the Zenith template."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.xdist_group(name="template")


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
    assert (full_project / "HERMES.md").exists()
    assert (full_project / ".claude" / "settings.json").exists()
    assert (full_project / "opencode.json").exists()
    assert (full_project / ".codex" / "config.toml").exists()
    assert (full_project / ".devin" / "config.json").exists()
    assert (full_project / ".zed" / "settings.json").exists()
    assert (full_project / ".zed" / "tasks.json").exists()
    assert (full_project / ".pi" / "settings.json").exists()
    assert (full_project / ".pi" / "APPEND_SYSTEM.md").exists()
    assert (full_project / ".omp" / "SYSTEM.md").exists()
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
        "workflow-docs-authoring",
        "workflow-docs-consumers",
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
        / "workflow-docs-authoring"
        / "templates"
        / "page_template.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-docs-authoring"
        / "templates"
        / "troubleshooting_section.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-docs-authoring"
        / "references"
        / "anti-slop-checklist.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-docs-authoring"
        / "references"
        / "diataxis.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-docs-consumers"
        / "templates"
        / "persona_prompt.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-docs-consumers"
        / "templates"
        / "evaluation_report.md"
    ).exists()
    assert (
        full_project
        / ".agents"
        / "skills"
        / "workflow-docs-consumers"
        / "references"
        / "personas.md"
    ).exists()
    for persona_slug in (
        "junior-developer",
        "senior-pythonista",
        "tech-lead",
        "devops-engineer",
        "solo-prototyper",
    ):
        assert (
            full_project
            / ".agents"
            / "skills"
            / "workflow-docs-consumers"
            / "references"
            / f"{persona_slug}.md"
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
        for tool_dir in (".claude", ".gemini", ".cursor", ".opencode"):
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
    assert (full_project / "tests" / "conftest.py").exists()
    conftest_text = (full_project / "tests" / "conftest.py").read_text()
    assert "def runner() -> CliRunner:" in conftest_text
    cli_test_text = (full_project / "tests" / "test_cli.py").read_text()
    assert "def test_cli_help(runner: CliRunner) -> None:" in cli_test_text
    assert "runner = CliRunner()" not in cli_test_text
    assert (full_project / "docs" / "index.md").exists()
    docs_index_text = (full_project / "docs" / "index.md").read_text()
    assert "diataxis: explanation" in docs_index_text
    assert "https://github.com/bwrob/zenith" in docs_index_text
    assert "https://bwrob.dev" in docs_index_text
    assert "Built with the <a href=" in docs_index_text
    assert (full_project / "docs" / "changelog.md").exists()
    assert (full_project / "docs" / "javascripts" / "mathjax.js").exists()
    assert not (full_project / "docs" / "javascripts" / "termynal.js").exists()
    assert (full_project / "docs" / "stylesheets" / "palette.css").exists()
    assert (full_project / "docs" / "stylesheets" / "custom.css").exists()
    assert not (full_project / "docs" / "stylesheets" / "termynal.css").exists()
    assert "termynal>=" in (full_project / "pyproject.toml").read_text()
    assert (full_project / "docs" / "assets" / "python-logo.svg").exists()
    assert (full_project / "docs" / "assets" / "python-logo.typ").exists()
    assert (full_project / "docs" / "assets" / "python-emblem.svg").exists()
    assert (full_project / "docs" / "assets" / "python-banner.svg").exists()
    assert (full_project / "docs" / "assets" / "python-banner.typ").exists()
    assert (full_project / "docs" / "assets" / "python-banner-dark.svg").exists()
    assert (full_project / "docs" / "assets" / "python-banner-dark.typ").exists()
    assert (full_project / "docs" / "assets" / "python-banner-light.svg").exists()
    assert (full_project / "docs" / "assets" / "python-banner-light.typ").exists()
    assert "fontpkg-cinzel>=" in (full_project / "pyproject.toml").read_text()
    assert "python-banner-dark.svg" in (full_project / "README.md").read_text()
    assert "python-banner-light.svg" in (full_project / "README.md").read_text()
    assert "python-banner-dark.svg" in (full_project / "docs" / "index.md").read_text()
    assert "python-banner-light.svg" in (full_project / "docs" / "index.md").read_text()
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
