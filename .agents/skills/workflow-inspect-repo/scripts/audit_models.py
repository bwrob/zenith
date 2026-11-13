# ruff: ignore[implicit-namespace-package]
"""Data models and TOML helpers for the 9-pillar repository auditor."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from harvest_models import HarvestResult


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


def table_value(data: dict[str, object], key: str) -> dict[str, object]:
    """Fetch a mapping-valued TOML table, defaulting to an empty mapping.

    Args:
        data: Parent TOML mapping.
        key: Table key to fetch.

    Returns:
        The nested mapping, or an empty mapping when absent or not a mapping.

    """
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def tool_table(pyproject: dict[str, object]) -> dict[str, object]:
    """Fetch the ``[tool]`` table from a pyproject mapping.

    Args:
        pyproject: Parsed ``pyproject.toml`` mapping.

    Returns:
        The ``tool`` table, or an empty mapping when absent or invalid.

    """
    return table_value(pyproject, "tool")


# -----------------------------------------------------------------------------
# Pillar 1: Packaging & Build System
# -----------------------------------------------------------------------------


def score_level(score: int, thresholds: tuple[tuple[int, int], ...]) -> int:
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
