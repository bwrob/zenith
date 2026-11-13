# ruff: ignore[implicit-namespace-package]
# Git subprocess commands run against user-supplied remotes and cached clones
# in .temp/ only, never shell-interpolated.
"""Markdown reporting and repository cloning helpers for skill harvesting."""

from __future__ import annotations

import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import]
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    from harvest_models import DiscoveredSkill, HarvestResult

error_console = Console(
    stderr=True, highlight=False, markup=False, emoji=False, soft_wrap=True
)


def _novel_skill_row(skill: DiscoveredSkill) -> str:
    """Render one novel-skill markdown table row.

    Args:
        skill: Novel skill to render.

    Returns:
        A single GitHub-flavored markdown table row.

    """
    desc = skill.description or "No description provided in frontmatter"
    if skill.triggers:
        triggers = ", ".join(f"`{t}`" for t in skill.triggers)
        desc += f"<br><i>Triggers:</i> {triggers}"
    scripts_str = (
        ", ".join(f"`{sc}`" for sc in skill.scripts) if skill.scripts else "None"
    )
    name_cell = f"**`{skill.name}`**"
    return (
        f"| {name_cell} | `{skill.kind}` | `{skill.location}` "
        f"| {desc} | {scripts_str} |"
    )


def format_harvest_markdown(result: HarvestResult) -> str:
    """Format deep harvest results into clean GitHub-flavored markdown.

    Args:
        result: Harvest analysis to render.

    Returns:
        The rendered markdown document.

    """
    ai_policy = (
        "✅ Present (`AI_POLICY.md`)"
        if result.ai_policy_present
        else "❌ None detected"
    )
    pr_checklist = (
        "✅ Present" if result.ai_pr_checklist_present else "❌ None detected"
    )
    instructions = (
        ", ".join(f"`{i}`" for i in result.instructions)
        if result.instructions
        else "None detected"
    )
    lines: list[str] = [
        f"### Agent Skills & AI Workflow Deep Harvest: `{result.target_name}`",
        "",
        f"- **AI Policy**: {ai_policy}",
        f"- **PR Template AI Checklist**: {pr_checklist}",
        f"- **Agent Instructions**: {instructions}",
    ]

    if result.mcp_servers:
        lines.append(f"- **MCP Servers**: {', '.join(result.mcp_servers)}")

    lines.append("")

    if result.novel_skills:
        lines.extend(_format_novel_skills_table(result))
    else:
        lines.extend(
            (
                "> [!NOTE]",
                (
                    "> No novel agent skills detected beyond "
                    "Zenith's existing skill library."
                ),
                "",
            )
        )

    if result.shared_skills:
        lines.extend(_format_shared_skills(result))

    if result.agent_directives:
        lines.extend(_format_agent_directives(result))

    if result.notes:
        lines.append("#### Structural Notes")
        lines.extend(f"- {note}" for note in result.notes)
        lines.append("")

    return "\n".join(lines)


def _format_novel_skills_table(result: HarvestResult) -> list[str]:
    """Render the novel skills markdown table section.

    Args:
        result: Harvest analysis containing novel skills.

    Returns:
        Markdown lines for the novel skills section.

    """
    lines = [
        "#### Novel Skills Discovered (Potential Zenith Additions)",
        (
            "| Skill / Rule Name | Kind | Location "
            "| Description & Triggers | Helper Scripts |"
        ),
        "| :--- | :---: | :--- | :--- | :--- |",
    ]
    lines.extend(_novel_skill_row(s) for s in result.novel_skills)
    lines.append("")
    return lines


def _format_shared_skills(result: HarvestResult) -> list[str]:
    """Render the shared/overlapping skills markdown section.

    Args:
        result: Harvest analysis containing shared skills.

    Returns:
        Markdown lines for the shared skills section.

    """
    lines = ["#### Shared / Overlapping Skills"]
    lines.extend(f"- `{s.name}` (`{s.location}`)" for s in result.shared_skills)
    lines.append("")
    return lines


def _format_agent_directives(result: HarvestResult) -> list[str]:
    """Render the extracted agent directives markdown section.

    Args:
        result: Harvest analysis containing directives.

    Returns:
        Markdown lines for the directives section.

    """
    lines = ["#### Extracted Agent Operational Directives & Mandates"]
    lines.extend(f"- {d}" for d in result.agent_directives)
    lines.append("")
    return lines


def _resolve_git() -> str:
    """Locate the git executable on PATH.

    Returns:
        Absolute path to the ``git`` executable.

    Raises:
        FileNotFoundError: If git is not installed or not on PATH.

    """
    git_path = shutil.which("git")
    if git_path is None:
        msg = "git executable not found on PATH"
        raise FileNotFoundError(msg)
    return git_path


def ensure_target_dir(target_arg: str, *, refresh: bool = False) -> Path:
    """Resolve target path or clone shallow repo into .temp/ if remote.

    Args:
        target_arg: Local directory path, GitHub slug, or HTTPS URL.
        refresh: Pull latest changes when the clone is already cached.

    Returns:
        The resolved target directory.

    """
    path = Path(target_arg)
    if path.exists():
        return path

    url = target_arg
    if not url.startswith(("https://", "git@")):
        url = f"https://github.com/{target_arg.strip('/')}.git"

    repo_name = target_arg.rstrip("/").split("/")[-1].removesuffix(".git")
    dest = Path(".temp") / f"inspect-{repo_name}"

    if dest.exists():
        if refresh:
            git_path = _resolve_git()
            error_console.print(f"Refreshing {dest}...")
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                # git pull on repo-controlled cached clone paths only.
                [git_path, "-C", str(dest), "pull", "--ff-only"],
                check=False,
            )
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    git_path = _resolve_git()
    cmd = [
        git_path,
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.process=",
        "-c",
        "filter.lfs.required=false",
        "clone",
        "--depth",
        "1",
        url,
        str(dest),
    ]
    error_console.print(f"Cloning {url} into {dest}...")
    subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        # Shallow clone of user-supplied remote into the repo .temp/ cache.
        cmd,
        check=True,
    )
    return dest
