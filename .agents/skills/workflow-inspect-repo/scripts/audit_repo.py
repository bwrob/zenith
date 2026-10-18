"""Automated 9-Pillar Repository Auditor and Maturity Scorecard Engine.

Exhaustively benchmarks Python projects against Zenith's 9 pillars of modern engineering.
"""

import argparse
import re
import subprocess
import sys
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from harvest_skills import (
    IGNORE_DIRS,
    HarvestResult,
    ensure_target_dir,
    format_harvest_markdown,
    harvest_repo,
    resolve_repo_root,
)


@dataclass(frozen=True)
class PillarAudit:
    """Evaluation result for an individual pillar."""

    name: str
    number: int
    level: int  # 1 to 4
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AuditReport:
    """Complete 9-pillar audit scorecard and report."""

    target_name: str
    target_path: Path
    pillars: list[PillarAudit]
    total_score: int
    harvest: HarvestResult
    max_score: int = 36

    @property
    def percentage(self) -> float:
        return (self.total_score / self.max_score) * 100


def load_toml(path: Path) -> dict[str, object]:
    """Safely parse a TOML file if it exists."""
    if not path.is_file():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


# -----------------------------------------------------------------------------
# Pillar 1: Packaging & Build System
# -----------------------------------------------------------------------------


def audit_pillar_1_packaging(root: Path, pyproject: dict[str, object]) -> PillarAudit:
    """Pillar 1: Packaging & Build System."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    build_system = pyproject.get("build-system")
    backend = ""
    requires: list[str] = []
    if isinstance(build_system, dict):
        backend = str(build_system.get("build-backend", ""))
        raw_reqs = build_system.get("requires", [])
        if isinstance(raw_reqs, list):
            requires = [str(r) for r in raw_reqs]

    project = pyproject.get("project")
    tool = pyproject.get("tool", {}) if isinstance(pyproject.get("tool"), dict) else {}

    # Build Backend Analysis
    if backend:
        strengths.append(f"PEP 517 build backend: `{backend}`")
        if "uv_build" in backend:
            level = 4
        elif any(
            b in backend
            for b in (
                "hatchling",
                "flit_core",
                "maturin",
                "scikit_build_core",
                "mesonpy",
                "poetry.core",
            )
        ):
            level = 3
        else:
            level = 2
    else:
        gaps.append("No declarative PEP 517 build backend found in pyproject.toml")

    # Dynamic Versioning Plugins
    dyn_plugins: list[str] = []
    for req in requires:
        for plug in (
            "hatch-vcs",
            "setuptools_scm",
            "versioningit",
            "flit-scm",
            "uv-dynamic-versioning",
        ):
            if plug in req:
                dyn_plugins.append(plug)
    if dyn_plugins:
        strengths.append(
            f"Dynamic versioning plugin: {', '.join(f'`{p}`' for p in dyn_plugins)}"
        )

    # PEP 621 Metadata Standard
    if isinstance(project, dict):
        strengths.append("PEP 621 `[project]` metadata table standard")

        # Entry points
        scripts = project.get("scripts")
        if isinstance(scripts, dict) and scripts:
            script_names = list(scripts.keys())[:3]
            extra = f" (+{len(scripts) - 3} more)" if len(scripts) > 3 else ""
            strengths.append(
                f"Console entry points: {', '.join(f'`{s}`' for s in script_names)}{extra}"
            )

        entry_points = project.get("entry-points")
        if isinstance(entry_points, dict) and entry_points:
            groups = list(entry_points.keys())
            strengths.append(
                f"Plugin entry point groups: {', '.join(f'`{g}`' for g in groups)}"
            )

        # Requires Python & Classifiers
        req_py = str(project.get("requires-python", ""))
        if req_py:
            details.append(f"Requires Python: `{req_py}`")

        classifiers = project.get("classifiers", [])
        if isinstance(classifiers, list):
            for c in classifiers:
                c_str = str(c)
                if "Free-threaded" in c_str or "cp313t" in c_str:
                    strengths.append("PEP 703 Free-threaded (nogil) classifier support")
                    break

        # License format
        lic = project.get("license")
        if isinstance(lic, str):
            strengths.append(f"SPDX license identifier: `{lic}` (PEP 639)")
        elif isinstance(lic, dict):
            details.append("Legacy license dictionary table")
    else:
        gaps.append("Missing PEP 621 `[project]` table")

    # Layout: src/ vs python/ (Maturin) vs flat
    has_src = (root / "src").is_dir()
    has_python_dir = (root / "python").is_dir()
    if has_src:
        strengths.append("Strict `src/` layout prevents accidental import collisions")
    elif has_python_dir:
        strengths.append(
            "Dedicated `python/` source layout (Maturin / mixed Rust-Python project)"
        )
    else:
        gaps.append("Flat package layout instead of recommended `src/` layout")

    # Typing marker: py.typed
    has_pytyped = False
    try:
        has_pytyped = any(
            p.name == "py.typed"
            for p in root.rglob("py.typed")
            if not any(part in IGNORE_DIRS for part in p.relative_to(root).parts)
        )
    except OSError:
        pass

    if has_pytyped:
        strengths.append("PEP 561 `py.typed` marker present for static consumers")
    else:
        gaps.append("No PEP 561 `py.typed` marker found")

    # Compiled extensions & wheel building
    has_rust = (root / "Cargo.toml").is_file()
    has_c = bool(list(root.glob("*.c")) or list(root.glob("src/**/*.c")))
    if has_rust:
        strengths.append("Rust / PyO3 extension (`Cargo.toml`)")
        level = max(level, 3)
    if has_c:
        strengths.append("Native C/C++ extension modules")
        level = max(level, 3)

    if "cibuildwheel" in tool or bool(
        list((root / ".github" / "workflows").glob("*wheel*"))
    ):
        strengths.append("Multi-platform binary wheel building (`cibuildwheel`)")

    # Encapsulation
    if (root / "src").is_dir():
        internal_dirs = [
            p.name
            for p in (root / "src").rglob("*")
            if p.is_dir() and p.name in ("_internal", "_vendor", "_compat")
        ]
        if internal_dirs:
            details.append(
                f"Internal encapsulation namespaces: {', '.join(f'`{d}`' for d in set(internal_dirs))}"
            )

    return PillarAudit(
        name="Packaging & Build System",
        number=1,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 2: Dependency & Environment Management
# -----------------------------------------------------------------------------


def audit_pillar_2_dependencies(
    root: Path, pyproject: dict[str, object]
) -> PillarAudit:
    """Pillar 2: Dependency & Environment Management."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    # Lockfile detection
    has_uv_lock = (root / "uv.lock").exists()
    has_poetry_lock = (root / "poetry.lock").exists()
    has_pdm_lock = (root / "pdm.lock").exists()
    has_pixi_lock = (root / "pixi.lock").exists()

    if has_uv_lock:
        level = 4
        strengths.append(
            "Committed `uv.lock` for lightning-fast reproducible environments"
        )
    elif has_poetry_lock or has_pdm_lock or has_pixi_lock:
        level = 3
        lock_type = "Poetry" if has_poetry_lock else ("PDM" if has_pdm_lock else "Pixi")
        strengths.append(f"Committed lockfile present (`{lock_type}`)")
    else:
        gaps.append("No committed lockfile found (`uv.lock`)")

    # Dependency Groups (PEP 735)
    dep_groups = pyproject.get("dependency-groups")
    if isinstance(dep_groups, dict):
        group_names = list(dep_groups.keys())
        strengths.append(
            f"PEP 735 `[dependency-groups]`: {', '.join(f'`{g}`' for g in group_names)}"
        )
        level = max(level, 4)
    else:
        gaps.append(
            "Lacks PEP 735 `[dependency-groups]`; uses legacy dev extras or unstructured dependencies"
        )

    # Tool UV Configuration & Workspaces
    tool = pyproject.get("tool", {}) if isinstance(pyproject.get("tool"), dict) else {}
    tool_uv = tool.get("uv")
    if isinstance(tool_uv, dict):
        strengths.append("Configured `[tool.uv]` settings and defaults")
        if "workspace" in tool_uv:
            strengths.append("Modern `uv workspace` monorepo configuration")
            level = 4

    # Dependency Pinning Strategy Analysis
    project = (
        pyproject.get("project", {})
        if isinstance(pyproject.get("project"), dict)
        else {}
    )
    runtime_deps = project.get("dependencies", [])
    if isinstance(runtime_deps, list) and runtime_deps:
        gte_count = sum(1 for d in runtime_deps if ">=" in str(d))
        strict_count = sum(1 for d in runtime_deps if "==" in str(d))
        upper_count = sum(1 for d in runtime_deps if "<" in str(d))
        total = len(runtime_deps)

        if upper_count > 0:
            details.append(
                f"Dependency Pinning: Restrictive upper bounds (`<`) present in {upper_count}/{total} dependencies"
            )
        elif strict_count > 0:
            details.append(
                f"Dependency Pinning: Exact pins (`==`) present in {strict_count}/{total} dependencies"
            )
        elif gte_count == total:
            details.append(
                f"Dependency Pinning: Pure open lower bounds (`>=`) across all {total} dependencies"
            )

    # Automated Dependency Updates
    if (root / ".github" / "dependabot.yml").exists():
        strengths.append("GitHub Dependabot automated updates configured")
    elif (root / "renovate.json").exists() or (
        root / ".github" / "renovate.json"
    ).exists():
        strengths.append("Renovate Bot automated updates configured")

    return PillarAudit(
        name="Dependency & Environment Management",
        number=2,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 3: Linting, Formatting, & Static Analysis
# -----------------------------------------------------------------------------


def audit_pillar_3_static_analysis(
    root: Path, pyproject: dict[str, object]
) -> PillarAudit:
    """Pillar 3: Linting, Formatting, & Static Analysis."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    score = 0

    tool = pyproject.get("tool", {}) if isinstance(pyproject.get("tool"), dict) else {}

    # Ruff Configuration & Rule Inspection
    ruff_candidates = (
        root / "ruff.toml",
        root / ".ruff.toml",
        root / "config" / "ruff.toml",
    )
    ruff_file = next((p for p in ruff_candidates if p.exists()), None)
    has_ruff = ruff_file is not None
    ruff_cfg: dict[str, object] = {}
    if ruff_file is not None:
        ruff_cfg = load_toml(ruff_file)
    elif "ruff" in tool and isinstance(tool["ruff"], dict):
        has_ruff = True
        ruff_cfg = tool["ruff"]

    if has_ruff:
        score += 2
        strengths.append("Ruff configured for high-performance linting and formatting")

        # Extract selected rules
        lint_cfg = ruff_cfg.get("lint", ruff_cfg)
        if isinstance(lint_cfg, dict):
            select_rules = lint_cfg.get("select", [])
            if isinstance(select_rules, list) and select_rules:
                rules_summary = ", ".join(f"`{r}`" for r in select_rules[:8])
                if len(select_rules) > 8:
                    rules_summary += f" (+{len(select_rules) - 8} more)"
                details.append(f"Ruff selected rule families: {rules_summary}")
    else:
        gaps.append("Ruff not configured")

    # Static Type Checkers & Strictness Preset
    type_checkers: list[str] = []

    if (root / "pyrefly.toml").exists() or "pyrefly" in tool:
        type_checkers.append("pyrefly")
        score += 2
        strengths.append("Pyrefly next-gen strict static type checker")
    if (
        (root / "ty.toml").exists()
        or (root / "config" / "ty.toml").exists()
        or "ty" in tool
    ):
        type_checkers.append("ty")
        score += 2
        strengths.append("Astral `ty` Rust-based static type checker")
    if (root / "pyrightconfig.json").exists() or "pyright" in tool:
        type_checkers.append("pyright")
        score += 1
        # Check strictness
        p_cfg = tool.get("pyright") if isinstance(tool.get("pyright"), dict) else {}
        if p_cfg.get("typeCheckingMode") == "strict":
            details.append(
                "Pyright strict mode enabled (`typeCheckingMode = 'strict'`)"
            )
    if (
        (root / "mypy.ini").exists()
        or (root / "config" / "mypy.ini").exists()
        or ".mypy.ini" in [p.name for p in root.iterdir()]
        or "mypy" in tool
    ):
        type_checkers.append("mypy")
        score += 1
        m_cfg = tool.get("mypy") if isinstance(tool.get("mypy"), dict) else {}
        if m_cfg.get("strict") is True:
            details.append("Mypy strict mode enabled (`strict = true`)")

    if type_checkers:
        strengths.append(
            f"Static type checking: {', '.join(f'`{t}`' for t in type_checkers)}"
        )
    else:
        gaps.append("No dedicated static type checker configuration detected")

    # Modular Boundaries: Tach / Import-Linter
    if (root / "tach.toml").exists() or "tach" in tool:
        score += 2
        strengths.append("Tach modular architecture boundary enforcement (`tach.toml`)")
    elif (root / ".importlinter").exists() or "importlinter" in tool:
        score += 1
        strengths.append("Import-linter modular dependency boundary enforcement")
    else:
        gaps.append("Lacks architectural layer/module boundary enforcement (`tach`)")

    # Cognitive Complexity
    if "complexipy" in tool or bool(list(root.glob("*.complexipy*"))):
        score += 1
        strengths.append("Complexipy cognitive complexity limits configured")
    else:
        gaps.append("Lacks cognitive complexity threshold gates (`complexipy`)")

    # Asset Linters & Non-code checks
    if (
        (root / ".typos.toml").exists()
        or (root / "_typos.toml").exists()
        or (root / "typos.toml").exists()
        or "typos" in tool
    ):
        strengths.append("Typos Rust-based source code spell checker")

    if (
        (root / ".rumdl.toml").exists()
        or (root / "rumdl.toml").exists()
        or "rumdl" in tool
    ):
        strengths.append("Rumdl Markdown linter and formatter")

    if (root / ".zizmor.yml").exists() or "zizmor" in tool:
        strengths.append("Zizmor GitHub Actions workflow security static analyzer")

    # Git Hooks: pre-commit vs prek
    if (root / ".pre-commit-config.yaml").exists():
        strengths.append("Pre-commit git hooks configured (`.pre-commit-config.yaml`)")
    elif (root / ".prek.toml").exists():
        strengths.append("Prek native fast Git hooks runner")

    level = 4 if score >= 5 else (3 if score >= 3 else (2 if score >= 1 else 1))
    return PillarAudit(
        name="Linting, Formatting, & Static Analysis",
        number=3,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 4: Task Runner & Developer Workflows
# -----------------------------------------------------------------------------


def audit_pillar_4_task_runner(root: Path, pyproject: dict[str, object]) -> PillarAudit:
    """Pillar 4: Task Runner & Developer Workflows."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    tool = pyproject.get("tool", {}) if isinstance(pyproject.get("tool"), dict) else {}

    # Poe the Poet
    has_poe = (root / "poe_tasks.toml").exists() or "poe" in tool
    if has_poe:
        level = 4
        strengths.append("Poe the Poet (`poethepoet`) orchestrates developer workflows")

        # Extract tasks
        poe_cfg = (
            load_toml(root / "poe_tasks.toml")
            if (root / "poe_tasks.toml").exists()
            else (tool.get("poe", {}) if isinstance(tool.get("poe"), dict) else {})
        )
        tasks = poe_cfg.get("tasks", {})
        if isinstance(tasks, dict) and tasks:
            task_list = list(tasks.keys())
            details.append(
                f"Poe tasks defined: {', '.join(f'`{t}`' for t in task_list[:8])}"
            )
    elif (root / "duties.py").exists():
        level = 3
        strengths.append("Duty (`duties.py`) Python task runner")
    elif (
        (root / "Justfile").exists()
        or (root / "justfile").exists()
        or (root / ".justfile").exists()
    ):
        level = 3
        strengths.append("Justfile task orchestrator")
    elif (root / "Makefile").exists() or (root / "makefile").exists():
        level = 2
        strengths.append("Legacy Makefile for task automation")
    elif (root / "noxfile.py").exists() or (root / "tox.ini").exists():
        level = 3
        strengths.append("Matrix testing orchestrator (Nox / Tox)")
    else:
        gaps.append("No unified task runner (e.g. Poe or Just) detected")

    return PillarAudit(
        name="Task Runner & Developer Workflows",
        number=4,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 5: Testing Architecture & Quality Assurance
# -----------------------------------------------------------------------------


def audit_pillar_5_testing(root: Path, pyproject: dict[str, object]) -> PillarAudit:
    """Pillar 5: Testing Architecture & Quality Assurance."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    # Test directories
    test_dirs = [
        d for d in ("tests", "test", "testing", "python/tests") if (root / d).is_dir()
    ]
    if test_dirs:
        level = 2
        strengths.append(
            f"Dedicated test directory: {', '.join(f'`{d}`' for d in test_dirs)}"
        )
    else:
        gaps.append("No test directory found")

    tool = pyproject.get("tool", {}) if isinstance(pyproject.get("tool"), dict) else {}
    has_pytest = (
        (root / "pytest.ini").exists()
        or (root / "config" / "pytest.ini").exists()
        or "pytest" in tool
    )
    if has_pytest:
        level = max(level, 3)
        strengths.append("Pytest test framework configuration")

        # Inspect pytest warning policy
        pytest_cfg = (
            tool.get("pytest", {}).get("ini_options", {})
            if isinstance(tool.get("pytest"), dict)
            else {}
        )
        if isinstance(pytest_cfg, dict):
            filter_warnings = pytest_cfg.get("filterwarnings", [])
            if isinstance(filter_warnings, list) and "error" in filter_warnings:
                strengths.append("Strict warning policy: `filterwarnings = ['error']`")

    # Dependency check for testing paradigms
    dep_str = str(pyproject)

    # 1. Property-based testing
    if "hypothesis" in dep_str:
        strengths.append("Hypothesis property-based testing framework")
        level = 4

    # 2. Snapshot testing: inline vs external
    if "inline-snapshot" in dep_str or "inline_snapshot" in dep_str:
        strengths.append(
            "Inline snapshot testing with AST rewriting (`inline-snapshot`)"
        )
        level = 4
    elif "syrupy" in dep_str:
        strengths.append("Syrupy external snapshot testing library")
        level = 4

    # 3. Declarative assertion helpers
    if "dirty-equals" in dep_str or "dirty_equals" in dep_str:
        strengths.append("Declarative equality testing predicates (`dirty-equals`)")

    # 4. Concurrency & Async
    if "pytest-asyncio" in dep_str:
        strengths.append("Async testing with `pytest-asyncio`")
    if "anyio" in dep_str or "pytest-anyio" in dep_str:
        strengths.append("Structured async testing with AnyIO")

    # 5. Coverage and enforcement
    cov_cfg = tool.get("coverage", {}) if isinstance(tool.get("coverage"), dict) else {}
    report_cfg = cov_cfg.get("report", {}) if isinstance(cov_cfg, dict) else {}
    run_cfg = cov_cfg.get("run", {}) if isinstance(cov_cfg, dict) else {}

    fail_under = report_cfg.get("fail_under") if isinstance(report_cfg, dict) else None
    branch = run_cfg.get("branch") if isinstance(run_cfg, dict) else None

    if (
        "pytest-cov" in dep_str
        or (root / ".coveragerc").exists()
        or (root / "config" / "coverage.ini").exists()
        or cov_cfg
    ):
        cov_info = "Coverage tracking configured"
        if fail_under:
            cov_info += f" (`fail_under = {fail_under}%`)"
            if fail_under == 100:
                strengths.append("Strict 100% test coverage enforcement gate")
        if branch is True:
            cov_info += " with branch coverage"
        strengths.append(cov_info)

    # 6. Parallel execution
    if "pytest-xdist" in dep_str:
        strengths.append("Parallel test execution with `pytest-xdist`")

    # 7. Mutation testing & benchmarks
    if "mutmut" in dep_str:
        strengths.append("Mutation testing engine (`mutmut`)")
    if "codspeed" in dep_str or "pytest-benchmark" in dep_str:
        strengths.append("Continuous performance benchmarking in tests")

    return PillarAudit(
        name="Testing Architecture & Quality Assurance",
        number=5,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 6: Documentation & Specification Engineering
# -----------------------------------------------------------------------------


def audit_pillar_6_docs(root: Path) -> PillarAudit:
    """Pillar 6: Documentation & Specification Engineering."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1
    repo_root = resolve_repo_root(root)

    # 1. Zensical Documentation Engine
    zensical_candidates = [root / "zensical.toml", repo_root / "zensical.toml"]
    zensical_file = next((f for f in zensical_candidates if f.is_file()), None)

    if zensical_file:
        level = 4
        strengths.append("Zensical TOML-native static documentation engine")
        try:
            zen_text = zensical_file.read_text(encoding="utf-8")
            zen_data = tomllib.loads(zen_text)
            proj = (
                zen_data.get("project", {})
                if isinstance(zen_data.get("project"), dict)
                else {}
            )
            val = (
                proj.get("validation", {})
                if isinstance(proj.get("validation"), dict)
                else {}
            )
            active_val = [k for k, v in val.items() if v is True]
            if active_val:
                strengths.append(
                    f"Strict build-time validation ([project.validation] with {len(active_val)} rules)"
                )
            elif "strict = true" in zen_text:
                strengths.append("Strict documentation build gate (`strict = true`)")

            plugins = (
                proj.get("plugins", {}) if isinstance(proj.get("plugins"), dict) else {}
            )
            if "mkdocstrings" in plugins:
                strengths.append("Docstring API reference generator (`mkdocstrings`)")
                if "objects.inv" in zen_text:
                    strengths.append(
                        "Inter-sphinx inventory cross-linking (`objects.inv`)"
                    )
                if "show_inheritance_diagram = true" in zen_text:
                    strengths.append(
                        "Automated class inheritance diagrams (`show_inheritance_diagram = true`)"
                    )
                if "backlinks" in zen_text:
                    strengths.append("API reference symbol backlinks (`backlinks`)")
            if "markdown-exec" in plugins or "markdown_exec" in zen_text:
                strengths.append("Executable documentation snippets (`markdown-exec`)")
            if "macros" in plugins:
                strengths.append("Dynamic Jinja2 documentation templating (`macros`)")
            if "redirects" in plugins:
                strengths.append("URL redirect management (`redirects`)")

            fences_str = str(proj.get("markdown_extensions", {}))
            if "mermaid" in fences_str:
                strengths.append("Native Mermaid diagramming support")
            if "snippets" in fences_str or "pymdownx.snippets" in zen_text:
                strengths.append(
                    "Tested external code snippet embedding (`pymdownx.snippets`)"
                )
            if "zensical.extensions.preview" in zen_text:
                strengths.append(
                    "Instant internal link hover previews (`zensical.extensions.preview`)"
                )

            js_css_str = str(proj.get("extra_javascript", [])) + str(
                proj.get("extra_css", [])
            )
            if "termynal" in js_css_str:
                strengths.append("Terminal CLI session animation (`termynal`)")
            if "mathjax" in js_css_str.lower():
                strengths.append("Client-side LaTeX mathematics (`MathJax`)")
        except (tomllib.TOMLDecodeError, OSError):
            pass

    # 2. MkDocs / MkDocs Material Ecosystem
    mkdocs_files: list[Path] = []
    for cand in [
        root / "mkdocs.yml",
        root / "mkdocs.yaml",
        root / "mkdocs.toml",
        root / "docs" / "mkdocs.yml",
        root / "docs" / "mkdocs.yaml",
        root / "docs" / "en" / "mkdocs.yml",
        root / "docs" / "en" / "mkdocs.yaml",
        repo_root / "mkdocs.yml",
        repo_root / "mkdocs.yaml",
    ]:
        if cand.is_file() and cand not in mkdocs_files:
            mkdocs_files.append(cand)

    try:
        for f in sorted(root.glob("**/mkdocs*.y*ml")):
            if f.is_file() and f not in mkdocs_files:
                mkdocs_files.append(f)
    except OSError:
        pass

    if mkdocs_files:
        mk_content = ""
        for mf in mkdocs_files:
            try:
                mk_content += mf.read_text(encoding="utf-8", errors="ignore") + "\n"
            except OSError:
                pass

        is_material = "material" in mk_content and (
            "theme:" in mk_content or "name: material" in mk_content
        )
        if is_material:
            strengths.append("Material for MkDocs responsive theme (`mkdocs-material`)")
        else:
            strengths.append("MkDocs documentation system")

        if "strict: true" in mk_content or "strict: True" in mk_content:
            strengths.append("Strict documentation build gate (`strict: true`)")

        if "mkdocstrings" in mk_content:
            strengths.append("Docstring API reference generator (`mkdocstrings`)")
            if "griffe" in mk_content:
                strengths.append("Static AST docstring inspection engine (`griffe`)")
            if "signature_crossrefs" in mk_content:
                strengths.append("Type annotation cross-referencing in API docs")
            if "objects.inv" in mk_content:
                strengths.append("Inter-sphinx inventory cross-linking (`objects.inv`)")

        if "markdown-exec" in mk_content or "markdown_exec" in mk_content:
            strengths.append("Executable documentation snippets (`markdown-exec`)")

        if "format_svg" in mk_content:
            strengths.append(
                "Dynamic SVG terminal application documentation rendering (`format_svg`)"
            )

        if "llmstxt" in mk_content or "mkdocs-llmstxt" in mk_content:
            strengths.append(
                "AI/LLM-optimized documentation indexing (`llms.txt` / `llmstxt`)"
            )

        if "provider: mike" in mk_content or (
            "mike" in mk_content and "plugins:" in mk_content
        ):
            strengths.append("Multi-version documentation management (`mike`)")

        if "pymdownx.snippets" in mk_content:
            strengths.append(
                "Tested external code snippet embedding (`pymdownx.snippets`)"
            )

        if "pymdownx.superfences" in mk_content:
            strengths.append("SuperFences with Mermaid and custom code formatters")

        if "pymdownx.tabbed" in mk_content:
            strengths.append(
                "Content tabs for multi-language/variant examples (`pymdownx.tabbed`)"
            )

        if "redirects" in mk_content:
            strengths.append("URL redirect management (`mkdocs-redirects`)")

        # MkDocs with material + advanced capabilities reaches Level 4 maturity
        if is_material and any(
            k in mk_content
            for k in (
                "mkdocstrings",
                "markdown-exec",
                "mike",
                "strict: true",
                "llmstxt",
                "format_svg",
            )
        ):
            level = max(level, 4)
        else:
            level = max(level, 3)

    # 3. LLMs.txt AI Context File
    llm_files = [root / "llms.txt", root / "llms-full.txt", root / "docs" / "llms.txt"]
    if any(f.is_file() for f in llm_files) and not any(
        "llms.txt" in s for s in strengths
    ):
        strengths.append("AI/LLM-optimized documentation context file (`llms.txt`)")

    # 4. Tested Documentation Code Directory (docs_src pattern)
    if (root / "docs_src").is_dir():
        strengths.append(
            "Isolated, test-verified documentation examples directory (`docs_src/`)"
        )

    # 5. Doctest Verification in Test Suite
    pyproject_path = root / "pyproject.toml"
    pytest_ini_path = root / "pytest.ini"
    test_cfg_text = ""
    for cfg in (pyproject_path, pytest_ini_path):
        if cfg.is_file():
            try:
                test_cfg_text += cfg.read_text(encoding="utf-8", errors="ignore") + "\n"
            except OSError:
                pass

    if (
        "--doctest-modules" in test_cfg_text
        or "--doctest-glob" in test_cfg_text
        or "xdoctest" in test_cfg_text
        or "pytest-markdown-docs" in test_cfg_text
    ):
        strengths.append(
            "Automated doctest verification in test suite (`--doctest-modules` / `xdoctest`)"
        )

    # 6. Sphinx Documentation Pipeline
    if not zensical_file and not mkdocs_files:
        if (root / "docs" / "conf.py").exists() or (root / "conf.py").exists():
            level = max(level, 3)
            strengths.append("Sphinx documentation pipeline")
        elif (root / "docs").is_dir():
            level = max(level, 2)
            strengths.append("Docs directory with Markdown files")
        else:
            gaps.append(
                "No dedicated documentation configuration found (e.g. Zensical or MkDocs)"
            )

    # Typst Vector Layouts
    try:
        typ_files = list(root.glob("**/*.typ"))
        if typ_files:
            strengths.append("Typst vector layout engine for docs/logos")
    except OSError:
        pass

    # Changelog Tooling (Scriv / Towncrier)
    if (root / "changelog.d").is_dir():
        strengths.append(
            "Fragment-based changelog management with Scriv (`changelog.d/`)"
        )
        level = max(level, 4)
    elif (root / "newsfragments").is_dir():
        strengths.append("Towncrier newsfragments changelog workflow")

    return PillarAudit(
        name="Documentation & Specification Engineering",
        number=6,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 7: CI/CD & Supply Chain Security
# -----------------------------------------------------------------------------


def audit_pillar_7_cicd(root: Path) -> PillarAudit:
    """Pillar 7: CI/CD & Supply Chain Security."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    repo_root = resolve_repo_root(root)
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.is_dir() and (repo_root / ".github" / "workflows").is_dir():
        workflows_dir = repo_root / ".github" / "workflows"
    level = 1

    if not workflows_dir.is_dir():
        gaps.append("No GitHub Actions workflows found")
        return PillarAudit(
            name="CI/CD & Supply Chain Security",
            number=7,
            level=1,
            strengths=strengths,
            gaps=gaps,
            details=details,
        )

    level = 2
    workflows = sorted(
        list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    )
    strengths.append(f"{len(workflows)} GitHub Actions workflow(s) detected")

    combined_content = ""
    for w in workflows:
        try:
            combined_content += w.read_text(encoding="utf-8", errors="ignore") + "\n"
        except OSError:
            pass

    # High-velocity uv caching
    if "astral-sh/setup-uv" in combined_content:
        strengths.append("Astral `setup-uv` high-velocity action with caching")
        level = max(level, 3)

    # Matrix Testing: Python & OS
    py_versions = sorted(
        set(
            re.findall(r'["\']?(3\.(?:1[0-9]|2[0-9]))(?:-dev)?["\']?', combined_content)
        )
    )
    if py_versions:
        details.append(
            f"CI Python version matrix: {', '.join(f'`{v}`' for v in py_versions)}"
        )

    if any(k in combined_content for k in ("nogil", "free-threaded", "cp313t")):
        strengths.append("CI matrix tests Python 3.13+ Free-threaded (nogil) runtime")
        level = 4

    os_matches: list[str] = []
    for os_name in ("ubuntu", "macos", "windows"):
        if f"{os_name}-latest" in combined_content or f"{os_name}-" in combined_content:
            os_matches.append(os_name)
    if len(os_matches) >= 3:
        strengths.append("Full cross-platform CI matrix (Linux, macOS, Windows)")

    # Supply Chain Security: OIDC & Provenance
    if (
        "id-token: write" in combined_content
        and "pypa/gh-action-pypi-publish" in combined_content
    ):
        strengths.append("PyPI Trusted Publishing via OIDC cryptographic tokens")
        level = 4

    if "attest-build-provenance" in combined_content:
        strengths.append("PEP 740 build provenance attestations")
        level = 4

    # Security Static Analyzer
    if "zizmor" in combined_content or (root / ".zizmor.yml").exists():
        strengths.append("Zizmor GitHub Actions security static analyzer")
        level = 4

    # Benchmarks in CI
    if "CodSpeedHQ/action" in combined_content:
        strengths.append(
            "Continuous performance benchmarking in CI (`CodSpeedHQ/action`)"
        )

    return PillarAudit(
        name="CI/CD & Supply Chain Security",
        number=7,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 8: Governance, Security, & Open Source Health
# -----------------------------------------------------------------------------


def audit_pillar_8_governance(root: Path) -> PillarAudit:
    """Pillar 8: Governance, Security, & Open Source Health."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1
    repo_root = resolve_repo_root(root)

    health_checks: list[tuple[str, tuple[str, ...], str]] = [
        (
            "LICENSE",
            ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"),
            "Open source license file",
        ),
        (
            "SECURITY.md",
            ("SECURITY.md", ".github/SECURITY.md"),
            "Security disclosure policy (`SECURITY.md`)",
        ),
        (
            "CONTRIBUTING.md",
            ("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/contributing.md"),
            "Contributor guidelines (`CONTRIBUTING.md`)",
        ),
        (
            "CODE_OF_CONDUCT.md",
            (
                "CODE_OF_CONDUCT.md",
                ".github/CODE_OF_CONDUCT.md",
                "docs/code_of_conduct.md",
            ),
            "Community code of conduct",
        ),
    ]
    found_count = 0
    for canonical, candidates, desc in health_checks:
        if any((root / c).exists() or (repo_root / c).exists() for c in candidates):
            found_count += 1
            strengths.append(desc)
        else:
            gaps.append(f"Missing `{canonical}`")

    # Secondary health assets
    for opt_file in ("CITATION.cff", "AUTHORS.md", "CHANGELOG.md", "ROADMAP.md"):
        if (root / opt_file).exists() or (repo_root / opt_file).exists():
            details.append(f"Repository metadata file present: `{opt_file}`")

    github_dir = (
        root / ".github" if (root / ".github").is_dir() else repo_root / ".github"
    )
    if (github_dir / "PULL_REQUEST_TEMPLATE.md").exists() or (
        github_dir / "pull_request_template.md"
    ).exists():
        strengths.append("PR template with contributor checklist")
    if (github_dir / "ISSUE_TEMPLATE").is_dir():
        strengths.append("Issue template schemas")

    level = (
        4
        if found_count >= 3
        else (3 if found_count >= 2 else (2 if found_count >= 1 else 1))
    )
    return PillarAudit(
        name="Governance, Security, & Open Source Health",
        number=8,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Pillar 9: Agent Skills & AI Development Workflows
# -----------------------------------------------------------------------------


def audit_pillar_9_agent_skills(root: Path, harvest: HarvestResult) -> PillarAudit:
    """Pillar 9: Agent Skills & AI Development Workflows."""
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    # Instruction files
    if harvest.instructions:
        level = 3
        strengths.append(
            f"Agent instructions: {', '.join(f'`{i}`' for i in harvest.instructions)}"
        )
    else:
        gaps.append(
            "No agent instruction files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`)"
        )

    # Discovered skills & rules
    total_skills = len(harvest.novel_skills) + len(harvest.shared_skills)
    if total_skills > 0:
        level = 4
        strengths.append(
            f"Repository agent skills library ({total_skills} skills/rules found)"
        )
    else:
        gaps.append("No repository agent skills directory (`.agents/skills/`)")

    # MCP servers
    if harvest.mcp_servers:
        strengths.append(
            f"Model Context Protocol (MCP) integrations: {len(harvest.mcp_servers)} detected"
        )
        level = 4

    # AI Governance
    if harvest.ai_policy_present:
        strengths.append("AI contribution policy present (`AI_POLICY.md`)")
        level = max(level, 4)
    else:
        gaps.append("Lacks explicit AI governance policy (`AI_POLICY.md`)")

    if harvest.ai_pr_checklist_present:
        strengths.append("PR template includes explicit AI contribution checklist")

    if harvest.agent_directives:
        details.append(
            f"Extracted {len(harvest.agent_directives)} explicit operational directives/constraints for AI agents"
        )

    return PillarAudit(
        name="Agent Skills & AI Development Workflows",
        number=9,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=details,
    )


# -----------------------------------------------------------------------------
# Full Audit Runner & Markdown Synthesis
# -----------------------------------------------------------------------------


def run_full_audit(target_path: Path) -> AuditReport:
    """Execute complete 9-pillar benchmark audit."""
    pyproject = load_toml(target_path / "pyproject.toml")
    harvest = harvest_repo(target_path)

    pillars = [
        audit_pillar_1_packaging(target_path, pyproject),
        audit_pillar_2_dependencies(target_path, pyproject),
        audit_pillar_3_static_analysis(target_path, pyproject),
        audit_pillar_4_task_runner(target_path, pyproject),
        audit_pillar_5_testing(target_path, pyproject),
        audit_pillar_6_docs(target_path),
        audit_pillar_7_cicd(target_path),
        audit_pillar_8_governance(target_path),
        audit_pillar_9_agent_skills(target_path, harvest),
    ]

    total_score = sum(p.level for p in pillars)
    return AuditReport(
        target_name=harvest.target_name,
        target_path=target_path,
        pillars=pillars,
        total_score=total_score,
        harvest=harvest,
    )


def extract_high_leverage_discoveries(report: AuditReport) -> list[str]:
    """Extract novel, high-signal architectural patterns for Zenith."""
    novel_takeaways: list[str] = []
    keywords = (
        "Scriv",
        "inline-snapshot",
        "dirty-equals",
        "Zizmor",
        "CodSpeed",
        "Free-threaded",
        "AnyIO",
        "strict-no-cover",
        "100% test coverage",
        "Tach",
        "Zensical",
        "Pyrefly",
        "PEP 740",
        "attest-build-provenance",
        "uv_build",
        "uv workspace",
        "llms.txt",
        "llmstxt",
        "mike",
        "docs_src",
        "mkdocstrings",
        "markdown-exec",
        "doctest",
        "Typst",
        "Strict documentation",
        "format_svg",
        "snippets",
        "show_inheritance_diagram",
        "zensical.extensions.preview",
    )
    for p in report.pillars:
        for s in p.strengths:
            for kw in keywords:
                if kw.lower() in s.lower() and s not in novel_takeaways:
                    novel_takeaways.append(s)

    for s in report.harvest.novel_skills:
        item = f"Novel Agent Skill: `{s.name}` ({s.description})"
        if item not in novel_takeaways:
            novel_takeaways.append(item)

    return novel_takeaways


def format_audit_markdown(report: AuditReport) -> str:
    """Format audit results and gap analysis into GitHub-flavored markdown."""
    lines: list[str] = [
        f"# 9-Pillar Benchmark Deep Audit: `{report.target_name}`",
        "",
        f"- **Maturity Score**: **{report.total_score} / {report.max_score}** ({report.percentage:.1f}%)",
        f"- **Target Directory**: `{report.target_path}`",
        "",
        "## 1. 9-Pillar Maturity Scorecard & Gap Radar",
        "",
        "| Pillar | Target Level | Zenith Baseline | Discovered Strengths | Gaps vs. Zenith |",
        "| :--- | :---: | :---: | :--- | :--- |",
    ]

    for p in report.pillars:
        s_bullets = (
            "<br>".join(f"• {s}" for s in p.strengths) if p.strengths else "None"
        )
        g_bullets = "<br>".join(f"• {g}" for g in p.gaps) if p.gaps else "None"
        if p.details:
            s_bullets += "<br><i>Details:</i><br>" + "<br>".join(
                f"- {d}" for d in p.details
            )

        lines.append(
            f"| **Pillar {p.number}: {p.name}** | **L{p.level} / 4** | **L4 / 4** | {s_bullets} | {g_bullets} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Agent Skills & AI Workflow Breakdown")
    lines.append("")
    lines.append(format_harvest_markdown(report.harvest))

    novel_takeaways = extract_high_leverage_discoveries(report)

    if novel_takeaways:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 3. High-Leverage Discoveries & Patterns for Zenith")
        lines.append("")
        for t in novel_takeaways:
            lines.append(f"- **{t}**")
        lines.append("")

    return "\n".join(lines)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Audit a Python repository across the 9 Zenith Pillars."
    )
    parser.add_argument(
        "target", help="Local directory path or GitHub URL/slug (org/repo)"
    )
    parser.add_argument("--output", "-o", help="Optional output markdown file path")
    parser.add_argument(
        "--subpath",
        "-s",
        help="Optional subdirectory path within target repository",
    )
    parser.add_argument(
        "--refresh",
        "-r",
        action="store_true",
        help="Refresh/pull latest git changes if cached",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_arguments(argv)
    try:
        target_dir = ensure_target_dir(args.target, refresh=args.refresh)
        if args.subpath:
            target_dir = target_dir / args.subpath
        elif not (target_dir / "pyproject.toml").exists():
            sub_pyprojects = sorted(
                p.parent
                for p in target_dir.glob("*/pyproject.toml")
                if p.parent.name not in IGNORE_DIRS
            )
            if sub_pyprojects:
                target_dir = sub_pyprojects[0]
                print(
                    f"Auto-detected Python subpackage at: {target_dir.name}",
                    file=sys.stderr,
                )

        report = run_full_audit(target_dir)
        md = format_audit_markdown(report)

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            print(f"Audit report saved to: {out_path}")
        else:
            print(md)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Error executing audit: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
