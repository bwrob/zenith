# ruff: ignore[implicit-namespace-package]
"""Pillars 5 and 6 audit checks: testing and documentation."""

from __future__ import annotations

import contextlib
import tomllib
from typing import TYPE_CHECKING

from audit_models import PillarAudit, table_value, tool_table
from harvest_skills import resolve_repo_root

if TYPE_CHECKING:
    from pathlib import Path

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
    pytest_cfg = table_value(table_value(tool, "pytest"), "ini_options")
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
    tool = tool_table(pyproject)
    cov_cfg = table_value(tool, "coverage")
    report_cfg = table_value(cov_cfg, "report")
    run_cfg = table_value(cov_cfg, "run")
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
    tool = tool_table(pyproject)
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
    val = table_value(proj, "validation")
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
    proj = table_value(zen_data, "project")

    strengths = _zensical_validation_strengths(proj, zen_text)
    plugins = table_value(proj, "plugins")
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
