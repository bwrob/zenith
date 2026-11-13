# ruff: ignore[implicit-namespace-package]
"""Pillars 7, 8, and 9 audit checks: CI/CD, governance, and agent skills."""

from __future__ import annotations

import contextlib
import re
from typing import TYPE_CHECKING

from audit_models import PillarAudit, score_level
from harvest_skills import resolve_repo_root

if TYPE_CHECKING:
    from pathlib import Path

    from harvest_skills import HarvestResult

_CI_OS_TARGETS = ("ubuntu", "macos", "windows")
_FULL_OS_MATRIX_COUNT = len(_CI_OS_TARGETS)
_CI_FREE_THREADING_KEYWORDS = ("nogil", "free-threaded", "cp313t")

_PILLAR8_HEALTH_LEVELS = ((3, 4), (2, 3), (1, 2))

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

    level = score_level(found_count, _PILLAR8_HEALTH_LEVELS)
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
