# ruff: ignore[implicit-namespace-package]
"""Pillars 3 and 4 audit checks: static analysis and task runners."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit_models import PillarAudit, load_toml, score_level, table_value, tool_table

if TYPE_CHECKING:
    from pathlib import Path

_MAX_SHOWN_RUFF_RULES = 8
_ENCAPSULATION_NAMES = {"_internal", "_vendor", "_compat"}
_PILLAR3_SCORE_LEVELS = ((5, 4), (3, 3), (1, 2))
_PILLAR8_HEALTH_LEVELS = ((3, 4), (2, 3), (1, 2))


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
    pyright_cfg = table_value(tool, "pyright")
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
    mypy_cfg = table_value(tool, "mypy")
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
    tool = tool_table(pyproject)

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

    level = score_level(score, _PILLAR3_SCORE_LEVELS)
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

    tool = tool_table(pyproject)

    # Poe the Poet
    has_poe = (root / "poe_tasks.toml").exists() or "poe" in tool
    if has_poe:
        level = 4
        strengths.append("Poe the Poet (`poethepoet`) orchestrates developer workflows")

        # Extract tasks
        poe_cfg = (
            load_toml(root / "poe_tasks.toml")
            if (root / "poe_tasks.toml").exists()
            else table_value(tool, "poe")
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
