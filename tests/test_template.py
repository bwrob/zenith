"""Tests for the Zenith template."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.xdist_group(name="template")


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
    assert "stylesheets/termynal.css" not in zensical_text
    assert "javascripts/termynal.js" not in zensical_text
    assert re.search(r"termynal\.include_assets\s*=\s*true", zensical_text) is not None
    assert (
        re.search(
            r'termynal\.prompt_literal_start\s*=\s*\[\s*"\$"\s*,\s*">>>"\s*\]',
            zensical_text,
        )
        is not None
    )
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
    assert "<!-- termynal -->" in index_text
    assert '=== "uv (Recommended)"' in index_text
    assert "```tree" in index_text
    getting_started_text = (full_project / "docs" / "getting-started.md").read_text()
    assert "<!-- termynal -->" in getting_started_text
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
    assert (full_project / "HERMES.md").read_text() == agents_text
    if (full_project / "CLAUDE.md").is_symlink():  # pragma: no branch
        assert (full_project / "CLAUDE.md").readlink() == Path("AGENTS.md")
        assert (full_project / ".cursorrules").readlink() == Path("AGENTS.md")
        assert (full_project / ".windsurfrules").readlink() == Path("AGENTS.md")
        assert (full_project / "HERMES.md").readlink() == Path("AGENTS.md")
        assert (full_project / ".pi" / "APPEND_SYSTEM.md").readlink() == Path(
            "../AGENTS.md"
        )
        assert (full_project / ".omp" / "SYSTEM.md").readlink() == Path("../AGENTS.md")

    assert "uv run poe:*" in (full_project / ".claude" / "settings.json").read_text()
    assert "uv run poe *" in (full_project / "opencode.json").read_text()
    assert "uv run poe:*" in (full_project / ".devin" / "config.json").read_text()
    assert "uv" in (full_project / ".zed" / "settings.json").read_text()
    assert "uv run poe test" in (full_project / ".zed" / "tasks.json").read_text()
    assert "bash" in (full_project / ".pi" / "settings.json").read_text()
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
