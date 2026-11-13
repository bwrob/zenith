# ruff: ignore[implicit-namespace-package]
"""Pillars 1 and 2 audit checks: packaging and dependency hygiene."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from audit_models import PillarAudit, table_value, tool_table
from harvest_models import IGNORE_DIRS

if TYPE_CHECKING:
    from pathlib import Path

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


def _extract_backend_config(
    pyproject: dict[str, object],
) -> tuple[str, list[str]]:
    """Extract the PEP 517 build backend and build requirements.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        Tuple of ``(backend name, build requirement strings)``.

    """
    build_system = table_value(pyproject, "build-system")
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

    tool = tool_table(pyproject)
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
    project = table_value(pyproject, "project")
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

    tool_uv = tool_table(pyproject).get("uv")
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
