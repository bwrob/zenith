# ruff: ignore[implicit-namespace-package]
# Standalone root-only skill script; not part of an installed package.
# The subprocess import stays for the ``SubprocessError`` exception family
# raised by repository cloning in ``harvest_skills.ensure_target_dir``.
"""Automated 9-Pillar Repository Auditor and Maturity Scorecard Engine.

Exhaustively benchmarks Python projects against Zenith's 9 pillars of modern
engineering.
"""

from __future__ import annotations

import argparse
import contextlib
import re
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from harvest_skills import (
    IGNORE_DIRS,
    HarvestResult,
    ensure_target_dir,
    format_harvest_markdown,
    harvest_repo,
    resolve_repo_root,
)
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Sequence

console = Console(highlight=False, markup=False, emoji=False, soft_wrap=True)
error_console = Console(
    stderr=True, highlight=False, markup=False, emoji=False, soft_wrap=True
)

_MODERN_BUILD_BACKENDS = (
    "hatchling",
    "flit_core",
    "maturin",
    "scikit_build_core",
    "mesonpy",
    "poetry.core",
)

_DYNAMIC_VERSION_PLUGINS = (
    "hatch-vcs",
    "setuptools_scm",
    "versioningit",
    "flit-scm",
    "uv-dynamic-versioning",
)

_MAX_SHOWN_ENTRY_POINTS = 3
_MAX_SHOWN_RUFF_RULES = 8
_ENCAPSULATION_NAMES = {"_internal", "_vendor", "_compat"}

_FREE_THREADING_MARKERS = ("Free-threaded", "cp313t")
_CI_OS_TARGETS = ("ubuntu", "macos", "windows")
_FULL_OS_MATRIX_COUNT = len(_CI_OS_TARGETS)
_CI_FREE_THREADING_KEYWORDS = ("nogil", "free-threaded", "cp313t")

# Maturity-level lookup tables: ``(threshold, reached level)``.
_PILLAR3_SCORE_LEVELS = ((5, 4), (3, 3), (1, 2))
_PILLAR8_HEALTH_LEVELS = ((3, 4), (2, 3), (1, 2))

_COVERAGE_FAIL_UNDER_FULL = 100
_DOCTEST_KEYWORDS = (
    "--doctest-modules",
    "--doctest-glob",
    "xdoctest",
    "pytest-markdown-docs",
)

_SPHINX_FALLBACK_GAP = (
    "No dedicated documentation configuration found (e.g. Zensical or MkDocs)"
)

_ZENSICAL_INHERITANCE_STRENGTH = (
    "Automated class inheritance diagrams (`show_inheritance_diagram = true`)"
)
_ZENSICAL_PREVIEW_STRENGTH = (
    "Instant internal link hover previews (`zensical.extensions.preview`)"
)
_ZENSICAL_SNIPPETS_STRENGTH = (
    "Tested external code snippet embedding (`pymdownx.snippets`)"
)
_MKDOCS_SVG_STRENGTH = (
    "Dynamic SVG terminal application documentation rendering (`format_svg`)"
)
_MKDOCS_LLMSTXT_STRENGTH = (
    "AI/LLM-optimized documentation indexing (`llms.txt` / `llmstxt`)"
)
_MKDOCS_TABS_STRENGTH = (
    "Content tabs for multi-language/variant examples (`pymdownx.tabbed`)"
)
_MKDOCS_FENCES_STRENGTH = "SuperFences with Mermaid and custom code formatters"

# Arbitrary content markers that unlock Level 4 for Material-based docs.
_MATERIAL_ADVANCED_MARKERS = (
    "mkdocstrings",
    "markdown-exec",
    "mike",
    "strict: true",
    "llmstxt",
    "format_svg",
)

_GOV_HEALTH_CHECKS: tuple[tuple[str, tuple[str, ...], str], ...] = (
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
)

_GOV_METADATA_FILES = ("CITATION.cff", "AUTHORS.md", "CHANGELOG.md", "ROADMAP.md")

_DISCOVERY_KEYWORDS = (
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
        """Compute the maturity score as a percentage of the maximum score."""
        return (self.total_score / self.max_score) * 100


def load_toml(path: Path) -> dict[str, object]:
    """Safely parse a TOML file if it exists.

    Args:
        path: TOML file path to parse.

    Returns:
        Parsed mapping, or an empty mapping when absent or unparsable.

    """
    if not path.is_file():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _table_value(data: dict[str, object], key: str) -> dict[str, object]:
    """Fetch a mapping-valued TOML table, defaulting to an empty mapping.

    Args:
        data: Parent TOML mapping.
        key: Table key to fetch.

    Returns:
        The nested mapping, or an empty mapping when absent or not a mapping.

    """
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def _tool_table(pyproject: dict[str, object]) -> dict[str, object]:
    """Fetch the ``[tool]`` table from a pyproject mapping.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        The ``tool`` table, or an empty mapping when absent or invalid.

    """
    return _table_value(pyproject, "tool")


# -----------------------------------------------------------------------------
# Pillar 1: Packaging & Build System
# -----------------------------------------------------------------------------


def _extract_backend_config(
    pyproject: dict[str, object],
) -> tuple[str, list[str]]:
    """Extract the PEP 517 build backend and build requirements.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Tuple of ``(backend name, build requirement strings)``.

    """
    build_system = _table_value(pyproject, "build-system")
    if not build_system:
        return "", []

    backend = str(build_system.get("build-backend", ""))
    raw_reqs = build_system.get("requires", [])
    requires = [str(r) for r in raw_reqs] if isinstance(raw_reqs, list) else []
    return backend, requires


def _backend_level(backend: str) -> int:
    """Score a PEP 517 build backend on the 1-4 maturity scale.

    Args:
        backend: Declared ``build-backend`` value.

    Returns:
        Maturity level for the backend.

    """
    if "uv_build" in backend:
        return 4
    if any(b in backend for b in _MODERN_BUILD_BACKENDS):
        return 3
    return 2


def _dynamic_versioning_strengths(requires: list[str]) -> list[str]:
    """Detect dynamic versioning plugins among the build requirements.

    Args:
        requires: PEP 517 ``requires`` requirement strings.

    Returns:
        Strength entries describing any detected versioning plugin.

    """
    dyn_plugins = [
        plug for req in requires for plug in _DYNAMIC_VERSION_PLUGINS if plug in req
    ]
    if not dyn_plugins:
        return []
    names = ", ".join(f"`{p}`" for p in dyn_plugins)
    return [f"Dynamic versioning plugin: {names}"]


def _project_metadata_findings(
    project: dict[str, object],
) -> tuple[list[str], list[str]]:
    """Derive strengths/details from the PEP 621 ``[project]`` table.

    Args:
        project: The parsed ``[project]`` table.

    Returns:
        Tuple of ``(strength entries, detail entries)``.

    """
    p_strengths = ["PEP 621 `[project]` metadata table standard"]
    p_details: list[str] = []

    scripts = project.get("scripts")
    if isinstance(scripts, dict) and scripts:
        script_names = list(scripts.keys())[:_MAX_SHOWN_ENTRY_POINTS]
        names = ", ".join(f"`{s}`" for s in script_names)
        extra = (
            f" (+{len(scripts) - _MAX_SHOWN_ENTRY_POINTS} more)"
            if len(scripts) > _MAX_SHOWN_ENTRY_POINTS
            else ""
        )
        p_strengths.append(f"Console entry points: {names}{extra}")

    entry_points = project.get("entry-points")
    if isinstance(entry_points, dict) and entry_points:
        groups = ", ".join(f"`{g}`" for g in entry_points)
        p_strengths.append(f"Plugin entry point groups: {groups}")

    req_py = str(project.get("requires-python", ""))
    if req_py:
        p_details.append(f"Requires Python: `{req_py}`")

    classifiers = project.get("classifiers", [])
    if isinstance(classifiers, list) and _has_free_threading(classifiers):
        p_strengths.append("PEP 703 Free-threaded (nogil) classifier support")

    lic = project.get("license")
    if isinstance(lic, str):
        p_strengths.append(f"SPDX license identifier: `{lic}` (PEP 639)")
    elif isinstance(lic, dict):
        p_details.append("Legacy license dictionary table")

    return p_strengths, p_details


def _has_free_threading(classifiers: list[object]) -> bool:
    """Check whether classifier strings advertise free-threaded support.

    Args:
        classifiers: Raw classifier string values.

    Returns:
        True when a free-threaded runtime classifier is present.

    """
    return any(
        any(marker in str(c) for marker in _FREE_THREADING_MARKERS) for c in classifiers
    )


def _py_typed_present(root: Path) -> bool:
    """Locate a ``py.typed`` marker outside ignored directories.

    Args:
        root: Target repository root.

    Returns:
        True when a PEP 561 ``py.typed`` marker exists.

    """
    with contextlib.suppress(OSError):
        return any(
            p.name == "py.typed"
            for p in root.rglob("py.typed")
            if not any(part in IGNORE_DIRS for part in p.relative_to(root).parts)
        )
    return False


def _layout_findings(root: Path) -> tuple[list[str], list[str]]:
    """Assess source layout and typed-package markers.

    Args:
        root: Target repository root.

    Returns:
        Tuple of ``(strength entries, gap entries)``.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    if (root / "src").is_dir():
        strengths.append("Strict `src/` layout prevents accidental import collisions")
    elif (root / "python").is_dir():
        strengths.append(
            "Dedicated `python/` source layout (Maturin / mixed Rust-Python project)"
        )
    else:
        gaps.append("Flat package layout instead of recommended `src/` layout")

    if _py_typed_present(root):
        strengths.append("PEP 561 `py.typed` marker present for static consumers")
    else:
        gaps.append("No PEP 561 `py.typed` marker found")

    return strengths, gaps


def _extension_findings(root: Path) -> tuple[list[str], int]:
    """Detect native extension modules and their maturity contribution.

    Args:
        root: Target repository root.

    Returns:
        Tuple of ``(strength entries, minimum level from extensions)``.

    """
    strengths: list[str] = []
    level = 1
    if (root / "Cargo.toml").is_file():
        strengths.append("Rust / PyO3 extension (`Cargo.toml`)")
        level = max(level, 3)
    if bool(list(root.glob("*.c")) or list(root.glob("src/**/*.c"))):
        strengths.append("Native C/C++ extension modules")
        level = max(level, 3)
    return strengths, level


def _encapsulation_details(root: Path) -> list[str]:
    """Detect private encapsulation namespaces under ``src/``.

    Args:
        root: Target repository root.

    Returns:
        Detail entries describing internal namespaces, if any.

    """
    if not (root / "src").is_dir():
        return []
    internal_dirs = [
        p.name
        for p in (root / "src").rglob("*")
        if p.is_dir() and p.name in _ENCAPSULATION_NAMES
    ]
    if not internal_dirs:
        return []
    names = ", ".join(f"`{d}`" for d in set(internal_dirs))
    return [f"Internal encapsulation namespaces: {names}"]


def audit_pillar_1_packaging(root: Path, pyproject: dict[str, object]) -> PillarAudit:
    """Benchmark pillar 1: Packaging & Build System.

    Args:
        root: Target repository root.
        pyproject: Parsed ``pyproject.toml`` mapping (empty when absent).

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []

    backend, requires = _extract_backend_config(pyproject)
    if backend:
        strengths.append(f"PEP 517 build backend: `{backend}`")
        level = _backend_level(backend)
    else:
        level = 1
        gaps.append("No declarative PEP 517 build backend found in pyproject.toml")

    strengths.extend(_dynamic_versioning_strengths(requires))

    if isinstance(project := pyproject.get("project"), dict):
        proj_strengths, proj_details = _project_metadata_findings(project)
        strengths.extend(proj_strengths)
        details.extend(proj_details)
    else:
        gaps.append("Missing PEP 621 `[project]` table")

    layout_strengths, layout_gaps = _layout_findings(root)
    strengths.extend(layout_strengths)
    gaps.extend(layout_gaps)

    extension_strengths, extension_level = _extension_findings(root)
    strengths.extend(extension_strengths)
    level = max(level, extension_level)

    tool = _tool_table(pyproject)
    if "cibuildwheel" in tool or bool(
        list((root / ".github" / "workflows").glob("*wheel*"))
    ):
        strengths.append("Multi-platform binary wheel building (`cibuildwheel`)")

    details.extend(_encapsulation_details(root))

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


def _lockfile_findings(root: Path) -> tuple[list[str], list[str], int]:
    """Assess committed lockfile coverage.

    Args:
        root: Target repository root.

    Returns:
        Tuple of ``(strength entries, gap entries, level from lockfile)``.

    """
    has_uv_lock = (root / "uv.lock").exists()
    if has_uv_lock:
        return (
            ["Committed `uv.lock` for lightning-fast reproducible environments"],
            [],
            4,
        )

    lock_names = [
        ("Poetry", "poetry.lock"),
        ("PDM", "pdm.lock"),
        ("Pixi", "pixi.lock"),
    ]
    for lock_type, lock_name in lock_names:
        if (root / lock_name).exists():
            return ([f"Committed lockfile present (`{lock_type}`)"], [], 3)

    return [], ["No committed lockfile found (`uv.lock`)"], 1


def _pinning_details(pyproject: dict[str, object]) -> list[str]:
    """Summarize dependency pinning strategy from runtime dependencies.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Detail entries describing the pinning strategy, if any.

    """
    project = _table_value(pyproject, "project")
    runtime_deps = project.get("dependencies", [])
    if not isinstance(runtime_deps, list) or not runtime_deps:
        return []

    reqs = [str(d) for d in runtime_deps]
    gte_count = sum(">=" in r for r in reqs)
    strict_count = sum("==" in r for r in reqs)
    upper_count = sum("<" in r for r in reqs)
    total = len(reqs)
    prefix = "Dependency Pinning: "

    if upper_count > 0:
        detail = (
            f"{prefix}Restrictive upper bounds (`<`) present "
            f"in {upper_count}/{total} dependencies"
        )
    elif strict_count > 0:
        detail = (
            f"{prefix}Exact pins (`==`) present in {strict_count}/{total} dependencies"
        )
    elif gte_count == total:
        detail = (
            f"{prefix}Pure open lower bounds (`>=`) across all {total} dependencies"
        )
    else:
        return []

    return [detail]


def _dependency_group_findings(
    pyproject: dict[str, object],
) -> tuple[list[str], list[str], int]:
    """Assess PEP 735 dependency groups and ``[tool.uv]`` workspaces.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Tuple of ``(strength entries, gap entries, level from groups)``.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    level = 1

    dep_groups = pyproject.get("dependency-groups")
    if isinstance(dep_groups, dict):
        names = ", ".join(f"`{g}`" for g in dep_groups)
        strengths.append(f"PEP 735 `[dependency-groups]`: {names}")
        level = max(level, 4)
    else:
        gaps.append(
            "Lacks PEP 735 `[dependency-groups]`; uses legacy dev extras "
            "or unstructured dependencies"
        )

    tool_uv = _tool_table(pyproject).get("uv")
    if isinstance(tool_uv, dict):
        strengths.append("Configured `[tool.uv]` settings and defaults")
        if "workspace" in tool_uv:
            strengths.append("Modern `uv workspace` monorepo configuration")
            level = 4

    return strengths, gaps, level


def _update_automation_strengths(root: Path) -> list[str]:
    """Detect automated dependency-update bot configuration.

    Args:
        root: Target repository root.

    Returns:
        Strength entries for Dependabot or Renovate configuration.

    """
    if (root / ".github" / "dependabot.yml").exists():
        return ["GitHub Dependabot automated updates configured"]
    if (root / "renovate.json").exists() or (
        root / ".github" / "renovate.json"
    ).exists():
        return ["Renovate Bot automated updates configured"]
    return []


def audit_pillar_2_dependencies(
    root: Path, pyproject: dict[str, object]
) -> PillarAudit:
    """Benchmark pillar 2: Dependency & Environment Management.

    Args:
        root: Target repository root.
        pyproject: Parsed ``pyproject.toml`` mapping (empty when absent).

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []

    lock_strengths, lock_gaps, level = _lockfile_findings(root)
    strengths.extend(lock_strengths)
    gaps.extend(lock_gaps)

    group_strengths, group_gaps, group_level = _dependency_group_findings(pyproject)
    strengths.extend(group_strengths)
    gaps.extend(group_gaps)
    level = max(level, group_level)

    details = _pinning_details(pyproject)
    strengths.extend(_update_automation_strengths(root))

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


def _ruff_findings(
    root: Path, tool: dict[str, object]
) -> tuple[list[str], list[str], list[str], int]:
    """Assess Ruff configuration and selected rule families.

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Tuple of ``(strengths, gaps, details, score contribution)``.

    """
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
    elif isinstance(tool.get("ruff"), dict):
        has_ruff = True
        ruff_cfg = tool["ruff"]

    if not has_ruff:
        return [], ["Ruff not configured"], [], 0

    strengths = ["Ruff configured for high-performance linting and formatting"]
    details = _ruff_rule_details(ruff_cfg)
    return strengths, [], details, 2


def _ruff_rule_details(ruff_cfg: dict[str, object]) -> list[str]:
    """Summarize selected Ruff rule families.

    Args:
        ruff_cfg: Parsed Ruff configuration mapping.

    Returns:
        Detail entries listing selected rule families, if any.

    """
    lint_cfg = ruff_cfg.get("lint", ruff_cfg)
    if not isinstance(lint_cfg, dict):
        return []
    select_rules = lint_cfg.get("select", [])
    if not isinstance(select_rules, list) or not select_rules:
        return []
    shown = select_rules[:_MAX_SHOWN_RUFF_RULES]
    rules_summary = ", ".join(f"`{r}`" for r in shown)
    if len(select_rules) > _MAX_SHOWN_RUFF_RULES:
        rules_summary += f" (+{len(select_rules) - _MAX_SHOWN_RUFF_RULES} more)"
    return [f"Ruff selected rule families: {rules_summary}"]


def _checker_configured(
    root: Path,
    tool: dict[str, object],
    tool_name: str,
    config_paths: tuple[str, ...],
    bare_names: tuple[str, ...] = (),
) -> bool:
    """Check whether a static-analysis tool has configuration present.

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.
        tool_name: ``[tool.<name>]`` key to probe.
        config_paths: Relative standalone config file paths.
        bare_names: Dotfile names to look for directly under root.

    Returns:
        True when the tool configuration is detectable.

    """
    if any((root / rel).exists() for rel in config_paths):
        return True
    if any(any(p.name == name for p in root.iterdir()) for name in bare_names):
        return True
    return tool_name in tool


def _pyright_strict_details(tool: dict[str, object]) -> list[str]:
    """Summarize Pyright strict-mode enablement.

    Args:
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Detail entries for strict type checking, if enabled.

    """
    pyright_cfg = _table_value(tool, "pyright")
    if pyright_cfg.get("typeCheckingMode") == "strict":
        return ["Pyright strict mode enabled (`typeCheckingMode = 'strict'`)"]
    return []


def _mypy_strict_details(tool: dict[str, object]) -> list[str]:
    """Summarize mypy strict-mode enablement.

    Args:
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Detail entries for strict type checking, if enabled.

    """
    mypy_cfg = _table_value(tool, "mypy")
    if mypy_cfg.get("strict") is True:
        return ["Mypy strict mode enabled (`strict = true`)"]
    return []


def _type_checker_findings(
    root: Path, tool: dict[str, object]
) -> tuple[list[str], list[str], list[str], int]:
    """Assess installed static type checkers.

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Tuple of ``(strengths, gaps, details, score contribution)``.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    type_checkers: list[str] = []
    score = 0

    if _checker_configured(root, tool, "pyrefly", ("pyrefly.toml",)):
        type_checkers.append("pyrefly")
        score += 2
        strengths.append("Pyrefly next-gen strict static type checker")

    ty_paths = ("ty.toml", "config/ty.toml")
    if _checker_configured(root, tool, "ty", ty_paths):
        type_checkers.append("ty")
        score += 2
        strengths.append("Astral `ty` Rust-based static type checker")

    if _checker_configured(root, tool, "pyright", ("pyrightconfig.json",)):
        type_checkers.append("pyright")
        score += 1
        # Check strictness
        details.extend(_pyright_strict_details(tool))

    mypy_paths = ("mypy.ini", "config/mypy.ini")
    if _checker_configured(root, tool, "mypy", mypy_paths, bare_names=(".mypy.ini",)):
        type_checkers.append("mypy")
        score += 1
        details.extend(_mypy_strict_details(tool))

    if type_checkers:
        names = ", ".join(f"`{t}`" for t in type_checkers)
        strengths.append(f"Static type checking: {names}")
    else:
        gaps.append("No dedicated static type checker configuration detected")

    return strengths, gaps, details, score


def _boundary_findings(
    root: Path, tool: dict[str, object]
) -> tuple[list[str], list[str], int]:
    """Assess modular boundary enforcement tooling.

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Tuple of ``(strengths, gaps, score contribution)``.

    """
    if _checker_configured(root, tool, "tach", ("tach.toml",)):
        return (
            ["Tach modular architecture boundary enforcement (`tach.toml`)"],
            [],
            2,
        )
    if _checker_configured(root, tool, "importlinter", (".importlinter",)):
        return (["Import-linter modular dependency boundary enforcement"], [], 1)
    return ([], ["Lacks architectural layer/module boundary enforcement (`tach`)"], 0)


def _complexity_findings(
    root: Path, tool: dict[str, object]
) -> tuple[list[str], list[str], int]:
    """Assess cognitive complexity gating.

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Tuple of ``(strengths, gaps, score contribution)``.

    """
    complexipy_files = bool(list(root.glob("*.complexipy*")))
    if "complexipy" in tool or complexipy_files:
        return ["Complexipy cognitive complexity limits configured"], [], 1
    return ([], ["Lacks cognitive complexity threshold gates (`complexipy`)"], 0)


def _asset_linter_strengths(root: Path, tool: dict[str, object]) -> list[str]:
    """Detect asset and non-code static checks (typos, rumdl, zizmor).

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Strength entries for detected asset checkers.

    """
    strengths: list[str] = []
    if _checker_configured(
        root, tool, "typos", ("typos.toml", ".typos.toml", "_typos.toml")
    ):
        strengths.append("Typos Rust-based source code spell checker")

    if _checker_configured(root, tool, "rumdl", ("rumdl.toml", ".rumdl.toml")):
        strengths.append("Rumdl Markdown linter and formatter")

    if _checker_configured(root, tool, "zizmor", (".zizmor.yml",)):
        strengths.append("Zizmor GitHub Actions workflow security static analyzer")

    return strengths


def _hook_runner_strengths(root: Path) -> list[str]:
    """Detect Git hook runner configuration.

    Args:
        root: Target repository root.

    Returns:
        Strength entries for prek or pre-commit configuration.

    """
    if (root / "prek.toml").exists() or (root / ".prek.toml").exists():
        return ["Prek native fast Git hooks runner (`prek.toml`)"]
    if (root / ".pre-commit-config.yaml").exists():
        return ["Pre-commit git hooks configured (`.pre-commit-config.yaml`)"]
    return []


def _score_level(score: int, thresholds: tuple[tuple[int, int], ...]) -> int:
    """Map a running score to a maturity level using threshold pairs.

    Args:
        score: Accumulated pillar score.
        thresholds: ``(minimum score, level)`` pairs in descending order.

    Returns:
        The reached maturity level.

    """
    for threshold, level_value in thresholds:
        if score >= threshold:
            return level_value
    return 1


def audit_pillar_3_static_analysis(
    root: Path, pyproject: dict[str, object]
) -> PillarAudit:
    """Benchmark pillar 3: Linting, Formatting, & Static Analysis.

    Args:
        root: Target repository root.
        pyproject: Parsed ``pyproject.toml`` mapping (empty when absent).

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    score = 0
    tool = _tool_table(pyproject)

    for s, g, d, contribution in (
        _ruff_findings(root, tool),
        _type_checker_findings(root, tool),
    ):
        strengths.extend(s)
        gaps.extend(g)
        details.extend(d)
        score += contribution

    for s, g, contribution in (
        _boundary_findings(root, tool),
        _complexity_findings(root, tool),
    ):
        strengths.extend(s)
        gaps.extend(g)
        score += contribution

    strengths.extend(_asset_linter_strengths(root, tool))
    strengths.extend(_hook_runner_strengths(root))

    level = _score_level(score, _PILLAR3_SCORE_LEVELS)
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
    """Benchmark pillar 4: Task Runner & Developer Workflows.

    Args:
        root: Target repository root.
        pyproject: Parsed ``pyproject.toml`` mapping (empty when absent).

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    tool = _tool_table(pyproject)

    # Poe the Poet
    has_poe = (root / "poe_tasks.toml").exists() or "poe" in tool
    if has_poe:
        level = 4
        strengths.append("Poe the Poet (`poethepoet`) orchestrates developer workflows")

        # Extract tasks
        poe_cfg = (
            load_toml(root / "poe_tasks.toml")
            if (root / "poe_tasks.toml").exists()
            else _table_value(tool, "poe")
        )
        tasks = poe_cfg.get("tasks", {})
        if isinstance(tasks, dict) and tasks:
            task_list = ", ".join(f"`{t}`" for t in list(tasks.keys())[:8])
            details.append(f"Poe tasks defined: {task_list}")
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


def _test_dir_findings(root: Path) -> tuple[list[str], list[str], int]:
    """Detect dedicated test directories.

    Args:
        root: Target repository root.

    Returns:
        Tuple of ``(strengths, gaps, level from test directories)``.

    """
    test_dirs = [
        d for d in ("tests", "test", "testing", "python/tests") if (root / d).is_dir()
    ]
    if test_dirs:
        names = ", ".join(f"`{d}`" for d in test_dirs)
        return ([f"Dedicated test directory: {names}"], [], 2)
    return [], ["No test directory found"], 1


def _pytest_findings(root: Path, tool: dict[str, object]) -> tuple[list[str], int]:
    """Assess pytest configuration and warning policy.

    Args:
        root: Target repository root.
        tool: ``[tool]`` mapping from ``pyproject.toml``.

    Returns:
        Tuple of ``(strength entries, minimum level from pytest)``.

    """
    has_pytest = (
        (root / "pytest.ini").exists()
        or (root / "config" / "pytest.ini").exists()
        or "pytest" in tool
    )
    if not has_pytest:
        return [], 1

    strengths = ["Pytest test framework configuration"]
    level = 3

    # Inspect pytest warning policy
    pytest_cfg = _table_value(_table_value(tool, "pytest"), "ini_options")
    filter_warnings = pytest_cfg.get("filterwarnings", [])
    if isinstance(filter_warnings, list) and "error" in filter_warnings:
        strengths.append("Strict warning policy: `filterwarnings = ['error']`")

    return strengths, level


def _paradigm_findings(pyproject: dict[str, object]) -> tuple[list[str], int]:
    """Detect property/snapshot/arity paradigms from declared dependencies.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Tuple of ``(strength entries, maximum level from paradigms)``.

    """
    dep_str = str(pyproject)
    strengths: list[str] = []
    level = 1

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

    return strengths, level


def _execution_findings(pyproject: dict[str, object]) -> list[str]:
    """Detect parallel execution, mutation, and benchmark testing options.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Strength entries for execution-level testing tooling.

    """
    dep_str = str(pyproject)
    strengths: list[str] = []

    # 6. Parallel execution
    if "pytest-xdist" in dep_str:
        strengths.append("Parallel test execution with `pytest-xdist`")

    # 7. Mutation testing & benchmarks
    if "mutmut" in dep_str:
        strengths.append("Mutation testing engine (`mutmut`)")
    if "codspeed" in dep_str or "pytest-benchmark" in dep_str:
        strengths.append("Continuous performance benchmarking in tests")

    return strengths


def _coverage_findings(
    root: Path, pyproject: dict[str, object]
) -> tuple[list[str], list[str]]:
    """Assess coverage tooling and enforcement gates.

    Args:
        root: Target repository root.
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Tuple of ``(coverage strengths, strict enforcement gate strengths)``
        in emission order (strict gate precedes the summary entry).

    """
    tool = _tool_table(pyproject)
    cov_cfg = _table_value(tool, "coverage")
    report_cfg = _table_value(cov_cfg, "report")
    run_cfg = _table_value(cov_cfg, "run")
    dep_str = str(pyproject)

    fail_under = report_cfg.get("fail_under")
    branch = run_cfg.get("branch")

    has_coverage = (
        "pytest-cov" in dep_str
        or (root / ".coveragerc").exists()
        or (root / "config" / "coverage.ini").exists()
        or bool(cov_cfg)
    )
    if not has_coverage:
        return [], []

    strict_gate: list[str] = []
    cov_info = "Coverage tracking configured"
    if fail_under:
        cov_info += f" (`fail_under = {fail_under}%`)"
        if fail_under == _COVERAGE_FAIL_UNDER_FULL:
            strict_gate.append("Strict 100% test coverage enforcement gate")
    if branch is True:
        cov_info += " with branch coverage"
    return [cov_info], strict_gate


def audit_pillar_5_testing(root: Path, pyproject: dict[str, object]) -> PillarAudit:
    """Benchmark pillar 5: Testing Architecture & Quality Assurance.

    Args:
        root: Target repository root.
        pyproject: Parsed ``pyproject.toml`` mapping (empty when absent).

    Returns:
        The pillar audit result.

    """
    tool = _tool_table(pyproject)
    details: list[str] = []

    dir_strengths, gaps, level = _test_dir_findings(root)

    pytest_strengths, pytest_level = _pytest_findings(root, tool)
    level = max(level, pytest_level)

    paradigm_strengths, paradigm_level = _paradigm_findings(pyproject)
    strict_cov_strengths, cov_strengths = _coverage_findings(root, pyproject)
    execution_strengths = _execution_findings(pyproject)
    level = max(level, paradigm_level)

    strengths = [
        *dir_strengths,
        *pytest_strengths,
        *paradigm_strengths,
        *strict_cov_strengths,
        *cov_strengths,
        *execution_strengths,
    ]

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


def _zensical_validation_strengths(proj: dict[str, object], zen_text: str) -> list[str]:
    """Assess Zensical build-time validation strictness.

    Args:
        proj: ``[project]`` table of the Zensical configuration.
        zen_text: Raw Zensical configuration text.

    Returns:
        Strength entries for strict validation gates.

    """
    val = _table_value(proj, "validation")
    active_val = [k for k, v in val.items() if v is True]
    if active_val:
        return [
            (
                "Strict build-time validation ([project.validation] "
                f"with {len(active_val)} rules)"
            )
        ]
    if "strict = true" in zen_text:
        return ["Strict documentation build gate (`strict = true`)"]
    return []


def _zensical_plugin_strengths(plugins: dict[str, object], zen_text: str) -> list[str]:
    """Assess Zensical documentation plugins.

    Args:
        plugins: ``[project.plugins]`` mapping.
        zen_text: Raw Zensical configuration text.

    Returns:
        Strength entries for configured plugins.

    """
    strengths: list[str] = []
    if "mkdocstrings" in plugins:
        strengths.append("Docstring API reference generator (`mkdocstrings`)")
        if "objects.inv" in zen_text:
            strengths.append("Inter-sphinx inventory cross-linking (`objects.inv`)")
        if "show_inheritance_diagram = true" in zen_text:
            strengths.append(_ZENSICAL_INHERITANCE_STRENGTH)
        if "backlinks" in zen_text:
            strengths.append("API reference symbol backlinks (`backlinks`)")
    if "markdown-exec" in plugins or "markdown_exec" in zen_text:
        strengths.append("Executable documentation snippets (`markdown-exec`)")
    if "macros" in plugins:
        strengths.append("Dynamic Jinja2 documentation templating (`macros`)")
    if "redirects" in plugins:
        strengths.append("URL redirect management (`redirects`)")
    return strengths


def _zensical_content_strengths(proj: dict[str, object], zen_text: str) -> list[str]:
    """Assess Zensical Markdown/JS content extensions.

    Args:
        proj: ``[project]`` table of the Zensical configuration.
        zen_text: Raw Zensical configuration text.

    Returns:
        Strength entries for content extensions.

    """
    strengths: list[str] = []
    fences_str = str(proj.get("markdown_extensions", {}))
    js_css_str = str(proj.get("extra_javascript", [])) + str(proj.get("extra_css", []))
    if "mermaid" in fences_str:
        strengths.append("Native Mermaid diagramming support")
    if "snippets" in fences_str or "pymdownx.snippets" in zen_text:
        strengths.append(_ZENSICAL_SNIPPETS_STRENGTH)
    if "zensical.extensions.preview" in zen_text:
        strengths.append(_ZENSICAL_PREVIEW_STRENGTH)
    if "termynal" in js_css_str:
        strengths.append("Terminal CLI session animation (`termynal`)")
    if "mathjax" in js_css_str.lower():
        strengths.append("Client-side LaTeX mathematics (`MathJax`)")
    return strengths


def _zensical_detailed_strengths(path: Path) -> list[str]:
    """Parse a Zensical config and derive detailed strength entries.

    Args:
        path: Path to ``zensical.toml``.

    Returns:
        Ordered strength entries from the configuration.

    """
    zen_text = path.read_text(encoding="utf-8")
    zen_data = tomllib.loads(zen_text)
    proj = _table_value(zen_data, "project")

    strengths = _zensical_validation_strengths(proj, zen_text)
    plugins = _table_value(proj, "plugins")
    strengths.extend(_zensical_plugin_strengths(plugins, zen_text))
    strengths.extend(_zensical_content_strengths(proj, zen_text))
    return strengths


def _zensical_findings(
    root: Path, repo_root: Path
) -> tuple[list[str], list[Path], int]:
    """Assess Zensical documentation engine adoption.

    Args:
        root: Target repository root.
        repo_root: Parent repository root for subdirectory targets.

    Returns:
        Tuple of ``(strengths, found zensical configs, level)``.

    """
    strengths: list[str] = []
    files: list[Path] = []
    level = 1

    candidates = [root / "zensical.toml", repo_root / "zensical.toml"]
    zensical_file = next((f for f in candidates if f.is_file()), None)

    if zensical_file is None:
        return strengths, files, level

    files.append(zensical_file)
    level = 4
    strengths.append("Zensical TOML-native static documentation engine")
    with contextlib.suppress(tomllib.TOMLDecodeError, OSError):
        strengths.extend(_zensical_detailed_strengths(zensical_file))

    return strengths, files, level


def _collect_mkdocs_files(root: Path, repo_root: Path) -> list[Path]:
    """Collect MkDocs configuration files at standard and nested locations.

    Args:
        root: Target repository root.
        repo_root: Parent repository root for subdirectory targets.

    Returns:
        Deduplicated list of MkDocs configuration file paths.

    """
    candidates = [
        root / "mkdocs.yml",
        root / "mkdocs.yaml",
        root / "mkdocs.toml",
        root / "docs" / "mkdocs.yml",
        root / "docs" / "mkdocs.yaml",
        root / "docs" / "en" / "mkdocs.yml",
        root / "docs" / "en" / "mkdocs.yaml",
        repo_root / "mkdocs.yml",
        repo_root / "mkdocs.yaml",
    ]
    files: list[Path] = []
    for cand in candidates:
        if cand.is_file() and cand not in files:
            files.append(cand)

    with contextlib.suppress(OSError):
        for found in sorted(root.glob("**/mkdocs*.y*ml")):
            if found.is_file() and found not in files:
                files.append(found)
    return files


def _read_mkdocs_content(mkdocs_files: list[Path]) -> str:
    """Concatenate MkDocs configuration content, skipping unreadable files.

    Args:
        mkdocs_files: MkDocs configuration file paths.

    Returns:
        Combined configuration text.

    """
    parts: list[str] = []
    for mf in mkdocs_files:
        with contextlib.suppress(OSError):
            parts.append(mf.read_text(encoding="utf-8", errors="ignore") + "\n")
    return "".join(parts)


def _mkdocs_core_strengths(mk_content: str, *, is_material: bool) -> list[str]:
    """Assess core MkDocs theme and API documentation features.

    Args:
        mk_content: Combined MkDocs configuration text.
        is_material: Whether the Material theme is configured.

    Returns:
        Strength entries for theme and mkdocstrings features.

    """
    strengths: list[str] = []
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

    return strengths


def _mkdocs_feature_strengths(mk_content: str) -> list[str]:
    """Assess advanced MkDocs capability plugins.

    Args:
        mk_content: Combined MkDocs configuration text.

    Returns:
        Strength entries for advanced plugin features.

    """
    strengths: list[str] = []
    if "markdown-exec" in mk_content or "markdown_exec" in mk_content:
        strengths.append("Executable documentation snippets (`markdown-exec`)")
    if "format_svg" in mk_content:
        strengths.append(_MKDOCS_SVG_STRENGTH)
    if "llmstxt" in mk_content or "mkdocs-llmstxt" in mk_content:
        strengths.append(_MKDOCS_LLMSTXT_STRENGTH)
    if "provider: mike" in mk_content or (
        "mike" in mk_content and "plugins:" in mk_content
    ):
        strengths.append("Multi-version documentation management (`mike`)")
    if "pymdownx.snippets" in mk_content:
        strengths.append("Tested external code snippet embedding (`pymdownx.snippets`)")
    if "pymdownx.superfences" in mk_content:
        strengths.append(_MKDOCS_FENCES_STRENGTH)
    if "pymdownx.tabbed" in mk_content:
        strengths.append(_MKDOCS_TABS_STRENGTH)
    if "redirects" in mk_content:
        strengths.append("URL redirect management (`mkdocs-redirects`)")
    return strengths


def _mkdocs_findings(root: Path, repo_root: Path) -> tuple[list[str], list[Path], int]:
    """Assess MkDocs/Material ecosystem adoption.

    Args:
        root: Target repository root.
        repo_root: Parent repository root for subdirectory targets.

    Returns:
        Tuple of ``(strengths, found config files, level)``.

    """
    strengths: list[str] = []
    level = 1
    mkdocs_files = _collect_mkdocs_files(root, repo_root)
    if not mkdocs_files:
        return strengths, mkdocs_files, level

    mk_content = _read_mkdocs_content(mkdocs_files)
    is_material = "material" in mk_content and (
        "theme:" in mk_content or "name: material" in mk_content
    )
    strengths.extend(_mkdocs_core_strengths(mk_content, is_material=is_material))
    strengths.extend(_mkdocs_feature_strengths(mk_content))

    # MkDocs with material + advanced capabilities reaches Level 4 maturity
    if is_material and any(k in mk_content for k in _MATERIAL_ADVANCED_MARKERS):
        level = 4
    else:
        level = 3

    return strengths, mkdocs_files, level


def _doctest_strengths(root: Path) -> list[str]:
    """Detect doctest verification in the test configuration.

    Args:
        root: Target repository root.

    Returns:
        Strength entry when doctest verification is configured.

    """
    parts: list[str] = []
    for cfg in (root / "pyproject.toml", root / "pytest.ini"):
        if cfg.is_file():
            with contextlib.suppress(OSError):
                parts.append(cfg.read_text(encoding="utf-8", errors="ignore") + "\n")
    test_cfg_text = "".join(parts)

    if any(keyword in test_cfg_text for keyword in _DOCTEST_KEYWORDS):
        return [
            (
                "Automated doctest verification in test suite "
                "(`--doctest-modules` / `xdoctest`)"
            )
        ]
    return []


def _sphinx_findings(root: Path) -> tuple[list[str], list[str], int]:
    """Assess Sphinx pipeline availability as a documentation fallback.

    Args:
        root: Target repository root.

    Returns:
        Tuple of ``(strengths, gaps, level)``.

    """
    if (root / "docs" / "conf.py").exists() or (root / "conf.py").exists():
        return ["Sphinx documentation pipeline"], [], 3
    if (root / "docs").is_dir():
        return ["Docs directory with Markdown files"], [], 2
    return [], [_SPHINX_FALLBACK_GAP], 1


def _changelog_findings(root: Path) -> tuple[list[str], int]:
    """Assess fragment-based changelog management tooling.

    Args:
        root: Target repository root.

    Returns:
        Tuple of ``(strength entries, level from changelog tooling)``.

    """
    if (root / "changelog.d").is_dir():
        return (
            ["Fragment-based changelog management with Scriv (`changelog.d/`)"],
            4,
        )
    if (root / "newsfragments").is_dir():
        return ["Towncrier newsfragments changelog workflow"], 1
    return [], 1


def audit_pillar_6_docs(root: Path) -> PillarAudit:
    """Benchmark pillar 6: Documentation & Specification Engineering.

    Args:
        root: Target repository root.

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    level = 1
    repo_root = resolve_repo_root(root)

    platform_files: list[Path] = []
    for found_strengths, configs, platform_level in (
        _zensical_findings(root, repo_root),
        _mkdocs_findings(root, repo_root),
    ):
        strengths.extend(found_strengths)
        platform_files.extend(configs)
        level = max(level, platform_level)

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

    strengths.extend(_doctest_strengths(root))

    # 6. Sphinx Documentation Pipeline
    if not platform_files:
        sphinx_strengths, sph_gaps, sph_level = _sphinx_findings(root)
        strengths.extend(sphinx_strengths)
        gaps.extend(sph_gaps)
        level = max(level, sph_level)

    # Typst Vector Layouts
    with contextlib.suppress(OSError):
        if list(root.glob("**/*.typ")):
            strengths.append("Typst vector layout engine for docs/logos")

    # Changelog Tooling (Scriv / Towncrier)
    changelog_strengths, changelog_level = _changelog_findings(root)
    strengths.extend(changelog_strengths)
    level = max(level, changelog_level)

    return PillarAudit(
        name="Documentation & Specification Engineering",
        number=6,
        level=level,
        strengths=strengths,
        gaps=gaps,
        details=[],
    )


# -----------------------------------------------------------------------------
# Pillar 7: CI/CD & Supply Chain Security
# -----------------------------------------------------------------------------


def _combined_workflow_content(workflows: list[Path]) -> str:
    """Concatenate workflow file contents, skipping unreadable files.

    Args:
        workflows: GitHub Actions workflow file paths.

    Returns:
        Combined YAML text across all workflows.

    """
    parts: list[str] = []
    for wf in workflows:
        with contextlib.suppress(OSError):
            parts.append(wf.read_text(encoding="utf-8", errors="ignore") + "\n")
    return "".join(parts)


def _cicd_strengths(root: Path, content: str) -> list[str]:
    """Collect CI/CD strength entries from combined workflow content.

    Args:
        root: Target repository root (for local config probes).
        content: Combined GitHub Actions YAML text.

    Returns:
        Ordered strength entries for CI capabilities.

    """
    strengths: list[str] = []

    # High-velocity uv caching
    if "astral-sh/setup-uv" in content:
        strengths.append("Astral `setup-uv` high-velocity action with caching")

    # Matrix Testing: Python & OS
    if any(k in content for k in _CI_FREE_THREADING_KEYWORDS):
        strengths.append("CI matrix tests Python 3.13+ Free-threaded (nogil) runtime")

    os_matches = [
        os_name
        for os_name in _CI_OS_TARGETS
        if f"{os_name}-latest" in content or f"{os_name}-" in content
    ]
    if len(os_matches) >= _FULL_OS_MATRIX_COUNT:
        strengths.append("Full cross-platform CI matrix (Linux, macOS, Windows)")

    # Supply Chain Security: OIDC & Provenance
    if "id-token: write" in content and "pypa/gh-action-pypi-publish" in content:
        strengths.append("PyPI Trusted Publishing via OIDC cryptographic tokens")

    if "attest-build-provenance" in content:
        strengths.append("PEP 740 build provenance attestations")

    # Security Static Analyzer
    if "zizmor" in content or (root / ".zizmor.yml").exists():
        strengths.append("Zizmor GitHub Actions security static analyzer")

    # Benchmarks in CI
    if "CodSpeedHQ/action" in content:
        strengths.append(
            "Continuous performance benchmarking in CI (`CodSpeedHQ/action`)"
        )

    return strengths


def _cicd_details(content: str) -> list[str]:
    """Extract CI matrix detail entries from combined workflow content.

    Args:
        content: Combined GitHub Actions YAML text.

    Returns:
        Detail entries describing tested Python versions.

    """
    py_versions = sorted(
        set(re.findall(r'["\']?(3\.(?:1[0-9]|2[0-9]))(?:-dev)?["\']?', content))
    )
    if py_versions:
        names = ", ".join(f"`{v}`" for v in py_versions)
        return [f"CI Python version matrix: {names}"]
    return []


def _workflow_level(content: str, root: Path) -> int:
    """Score CI/CD capability from combined workflow content.

    Args:
        content: Combined GitHub Actions YAML text.
        root: Target repository root (for local config probes).

    Returns:
        Maturity level for CI/CD capabilities.

    """
    level = 3 if "astral-sh/setup-uv" in content else 2
    if any(k in content for k in _CI_FREE_THREADING_KEYWORDS):
        level = 4
    if "id-token: write" in content and "pypa/gh-action-pypi-publish" in content:
        level = max(level, 4)
    if "attest-build-provenance" in content:
        level = max(level, 4)
    if "zizmor" in content or (root / ".zizmor.yml").exists():
        level = max(level, 4)
    return level


def audit_pillar_7_cicd(root: Path) -> PillarAudit:
    """Benchmark pillar 7: CI/CD & Supply Chain Security.

    Args:
        root: Target repository root.

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    repo_root = resolve_repo_root(root)
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.is_dir() and (repo_root / ".github" / "workflows").is_dir():
        workflows_dir = repo_root / ".github" / "workflows"

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

    workflows = sorted(
        list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    )
    strengths.append(f"{len(workflows)} GitHub Actions workflow(s) detected")

    content = _combined_workflow_content(workflows)
    strengths.extend(_cicd_strengths(root, content))
    details.extend(_cicd_details(content))
    level = _workflow_level(content, root)

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


def _governance_file_findings(
    root: Path, repo_root: Path
) -> tuple[list[str], list[str], int]:
    """Assess community health files (license, security, conduct).

    Args:
        root: Target repository root.
        repo_root: Parent repository root for subdirectory targets.

    Returns:
        Tuple of ``(strengths, gaps, level from health files)``.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    found_count = 0
    for canonical, candidates, desc in _GOV_HEALTH_CHECKS:
        if any((root / c).exists() or (repo_root / c).exists() for c in candidates):
            found_count += 1
            strengths.append(desc)
        else:
            gaps.append(f"Missing `{canonical}`")

    level = _score_level(found_count, _PILLAR8_HEALTH_LEVELS)
    return strengths, gaps, level


def _template_findings(github_dir: Path) -> list[str]:
    """Detect PR and issue templates in the .github directory.

    Args:
        github_dir: Resolved ``.github`` directory.

    Returns:
        Strength entries for available templates.

    """
    strengths: list[str] = []
    pr_templates = ("PULL_REQUEST_TEMPLATE.md", "pull_request_template.md")
    if any((github_dir / name).exists() for name in pr_templates):
        strengths.append("PR template with contributor checklist")
    if (github_dir / "ISSUE_TEMPLATE").is_dir():
        strengths.append("Issue template schemas")
    return strengths


def audit_pillar_8_governance(root: Path) -> PillarAudit:
    """Benchmark pillar 8: Governance, Security, & Open Source Health.

    Args:
        root: Target repository root.

    Returns:
        The pillar audit result.

    """
    repo_root = resolve_repo_root(root)

    strengths, gaps, level = _governance_file_findings(root, repo_root)
    details: list[str] = []

    # Secondary health assets
    details.extend(
        f"Repository metadata file present: `{opt_file}`"
        for opt_file in _GOV_METADATA_FILES
        if (root / opt_file).exists() or (repo_root / opt_file).exists()
    )

    github_dir = (
        root / ".github" if (root / ".github").is_dir() else repo_root / ".github"
    )
    strengths.extend(_template_findings(github_dir))

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


def audit_pillar_9_agent_skills(_root: Path, harvest: HarvestResult) -> PillarAudit:
    """Benchmark pillar 9: Agent Skills & AI Development Workflows.

    Args:
        _root: Target repository root (unused; harvest covers its scan).
        harvest: Consolidated skill/instruction harvest for the target.

    Returns:
        The pillar audit result.

    """
    strengths: list[str] = []
    gaps: list[str] = []
    details: list[str] = []
    level = 1

    # Instruction files
    if harvest.instructions:
        level = 3
        names = ", ".join(f"`{i}`" for i in harvest.instructions)
        strengths.append(f"Agent instructions: {names}")
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
            "Model Context Protocol (MCP) integrations: "
            f"{len(harvest.mcp_servers)} detected"
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
            f"Extracted {len(harvest.agent_directives)} explicit "
            "operational directives/constraints for AI agents"
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
    """Execute complete 9-pillar benchmark audit.

    Args:
        target_path: Repository or subdirectory to audit.

    Returns:
        The consolidated :class:`AuditReport`.

    """
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
    """Extract novel, high-signal architectural patterns for Zenith.

    Args:
        report: Completed audit report.

    Returns:
        Deduplicated discovery strings across pillars and novel skills.

    """
    novel_takeaways: list[str] = []

    for p in report.pillars:
        for s in p.strengths:
            for kw in _DISCOVERY_KEYWORDS:
                if kw.lower() in s.lower() and s not in novel_takeaways:
                    novel_takeaways.append(s)

    for s in report.harvest.novel_skills:
        item = f"Novel Agent Skill: `{s.name}` ({s.description})"
        if item not in novel_takeaways:
            novel_takeaways.append(item)

    return novel_takeaways


def _scorecard_row(audit: PillarAudit) -> str:
    """Render one maturity-scorecard markdown table row.

    Args:
        audit: A single pillar audit result.

    Returns:
        A GitHub-flavored markdown table row.

    """
    s_bullets = (
        "<br>".join(f"• {s}" for s in audit.strengths) if audit.strengths else "None"
    )
    g_bullets = "<br>".join(f"• {g}" for g in audit.gaps) if audit.gaps else "None"
    if audit.details:
        detail_lines = "<br>".join(f"- {d}" for d in audit.details)
        s_bullets += "<br><i>Details:</i><br>" + detail_lines

    pillar_cell = f"**Pillar {audit.number}: {audit.name}**"
    levels = f"**L{audit.level} / 4** | **L4 / 4**"
    return f"| {pillar_cell} | {levels} | {s_bullets} | {g_bullets} |"


def format_audit_markdown(report: AuditReport) -> str:
    """Format audit results and gap analysis into GitHub-flavored markdown.

    Args:
        report: Completed audit report.

    Returns:
        The rendered GitHub-flavored markdown document.

    """
    score = (
        f"- **Maturity Score**: **{report.total_score} / {report.max_score}**"
        f" ({report.percentage:.1f}%)"
    )
    lines: list[str] = [
        f"# 9-Pillar Benchmark Deep Audit: `{report.target_name}`",
        "",
        score,
        f"- **Target Directory**: `{report.target_path}`",
        "",
        "## 1. 9-Pillar Maturity Scorecard & Gap Radar",
        "",
        (
            "| Pillar | Target Level | Zenith Baseline "
            "| Discovered Strengths | Gaps vs. Zenith |"
        ),
        "| :--- | :---: | :---: | :--- | :--- |",
    ]

    lines.extend(_scorecard_row(p) for p in report.pillars)

    lines.extend(("", "---", "", "## 2. Agent Skills & AI Workflow Breakdown", ""))
    lines.append(format_harvest_markdown(report.harvest))

    novel_takeaways = extract_high_leverage_discoveries(report)

    if novel_takeaways:
        lines.extend(
            (
                "",
                "---",
                "",
                "## 3. High-Leverage Discoveries & Patterns for Zenith",
                "",
            )
        )
        lines.extend(f"- **{t}**" for t in novel_takeaways)
        lines.append("")

    return "\n".join(lines)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        The parsed argument namespace.

    """
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


def _resolve_target_dir(target: str, subpath: str | None, *, refresh: bool) -> Path:
    """Resolve the effective audit target directory from CLI arguments.

    Args:
        target: Local directory path or GitHub URL/slug (org/repo).
        subpath: Optional subdirectory path within the target repository.
        refresh: Refresh cached clones before auditing.

    Returns:
        The resolved target directory.

    """
    target_dir = ensure_target_dir(target, refresh=refresh)
    if subpath:
        return target_dir / subpath
    if (target_dir / "pyproject.toml").exists():
        return target_dir

    sub_pyprojects = sorted(
        p.parent
        for p in target_dir.glob("*/pyproject.toml")
        if p.parent.name not in IGNORE_DIRS
    )
    if sub_pyprojects:
        error_console.print(
            f"Auto-detected Python subpackage at: {sub_pyprojects[0].name}"
        )
        return sub_pyprojects[0]
    return target_dir


def _emit_report(markdown: str, output: str | None) -> None:
    """Write or print the rendered audit report.

    Args:
        markdown: Rendered markdown report.
        output: Optional output markdown file path.

    """
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        console.print(f"Audit report saved to: {out_path}")
    else:
        console.print(markdown)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code; 0 on success, 1 on failure.

    """
    args = parse_arguments(argv)
    try:
        target_dir = _resolve_target_dir(
            args.target, args.subpath, refresh=args.refresh
        )
        report = run_full_audit(target_dir)
        markdown = format_audit_markdown(report)
        _emit_report(markdown, args.output)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        error_console.print(f"Error executing audit: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
