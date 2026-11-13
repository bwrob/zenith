# ruff: ignore[implicit-namespace-package]
# Standalone root-only skill script; not part of an installed package.
# The subprocess import stays for the ``SubprocessError`` exception family
# raised by repository cloning in ``harvest_skills.ensure_target_dir``.
"""Automated 9-Pillar Repository Auditor and Maturity Scorecard Engine."""

from __future__ import annotations

import argparse
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from audit_models import AuditReport, load_toml
from audit_pillars_docs import audit_pillar_5_testing, audit_pillar_6_docs
from audit_pillars_ops import (
    audit_pillar_7_cicd,
    audit_pillar_8_governance,
    audit_pillar_9_agent_skills,
)
from audit_pillars_pkg import audit_pillar_1_packaging, audit_pillar_2_dependencies
from audit_pillars_quality import (
    audit_pillar_3_static_analysis,
    audit_pillar_4_task_runner,
)
from audit_report import format_audit_markdown
from harvest_skills import IGNORE_DIRS, ensure_target_dir, harvest_repo
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Sequence

console = Console(highlight=False, markup=False, emoji=False, soft_wrap=True)
error_console = Console(
    stderr=True, highlight=False, markup=False, emoji=False, soft_wrap=True
)


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
