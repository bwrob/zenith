# ruff: ignore[implicit-namespace-package]
"""Markdown scorecard and discovery formatter for repository audits."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harvest_skills import format_harvest_markdown

if TYPE_CHECKING:
    from audit_models import AuditReport, PillarAudit

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
