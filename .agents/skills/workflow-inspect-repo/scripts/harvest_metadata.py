# ruff: ignore[implicit-namespace-package]
"""Skill and Cursor rule frontmatter metadata parsers."""

from __future__ import annotations

import re
from pathlib import Path

from harvest_models import DiscoveredSkill


def register_skill(
    skill: DiscoveredSkill,
    seen_names: set[str],
    novel: list[DiscoveredSkill],
    shared: list[DiscoveredSkill],
) -> None:
    """Deduplicate a skill by name and route it to the novel or shared bucket.

    Args:
        skill: Skill candidate to register.
        seen_names: Mutable set of already-seen skill names.
        novel: Bucket for skills not present in the Zenith library.
        shared: Bucket for skills overlapping the Zenith library.

    """
    if skill.name in seen_names:
        return
    seen_names.add(skill.name)
    if skill.is_novel:
        novel.append(skill)
    else:
        shared.append(skill)


def _parse_skill_frontmatter(fm_text: str) -> tuple[str, str, list[str]]:
    """Parse name, description, and triggers from SKILL.md frontmatter text.

    Args:
        fm_text: Raw YAML frontmatter (or fallback full-document) text.

    Returns:
        Tuple of ``(name, description, triggers)``; name is empty when the
        frontmatter omits it.

    """
    name = ""
    desc = ""
    triggers: list[str] = []

    name_match = re.search(r"^name:\s*([^\n]+)", fm_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip().strip("'\"")

    desc_match = re.search(
        r"^description:\s*(?:>|\|)?\s*\n?([^\n]+(?:\n\s+[^\n]+)*)",
        fm_text,
        re.MULTILINE,
    )
    if desc_match:
        raw_desc = desc_match.group(1).strip()
        desc = " ".join(line.strip() for line in raw_desc.splitlines()).strip("'\"")

    triggers_match = re.search(
        r"(?:triggers|keywords|when to use):\s*([^\n]+)", fm_text, re.IGNORECASE
    )
    if triggers_match:
        triggers = [
            t.strip().strip("'\"")
            for t in triggers_match.group(1).split(",")
            if t.strip()
        ]

    return name, desc, triggers


def extract_skill_metadata(skill_path: Path) -> tuple[str, str, list[str], list[str]]:
    """Extract skill name, description, triggers, and helper scripts.

    Reads a ``SKILL.md`` file or directory and parses its frontmatter.

    Args:
        skill_path: Path to a skill directory or ``SKILL.md`` file.

    Returns:
        Tuple of ``(name, description, triggers, scripts)``.

    """
    skill_md = skill_path if skill_path.is_file() else (skill_path / "SKILL.md")
    name = skill_path.parent.name if skill_path.is_file() else skill_path.name
    desc = ""
    triggers: list[str] = []

    # Check for helper scripts
    script_dir = skill_path if skill_path.is_dir() else skill_path.parent
    scripts_path = script_dir / "scripts"
    scripts = (
        sorted(
            p.name
            for p in scripts_path.iterdir()
            if p.is_file() and not p.name.startswith(".")
        )
        if scripts_path.is_dir()
        else []
    )

    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            # Parse YAML frontmatter if present
            frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            fm_text = frontmatter_match.group(1) if frontmatter_match else content
            parsed_name, desc, triggers = _parse_skill_frontmatter(fm_text)
            name = parsed_name or name
        except OSError:
            pass

    return name, desc, triggers, scripts


def extract_cursor_rule_metadata(rule_path: Path) -> DiscoveredSkill:
    """Extract metadata from modern Cursor .mdc or .md rule files.

    Args:
        rule_path: Path to the rule file.

    Returns:
        A :class:`DiscoveredSkill` of kind ``cursor-rule``.

    """
    name = rule_path.stem
    desc = ""
    globs = ""
    try:
        content = rule_path.read_text(encoding="utf-8", errors="ignore")
        desc, globs = _parse_rule_frontmatter(content)
    except OSError:
        pass

    display_desc = f"{desc} (globs: `{globs}`)" if globs else desc
    return DiscoveredSkill(
        name=name,
        location=str(rule_path),
        description=display_desc,
        is_novel=True,
        kind="cursor-rule",
    )


def _parse_rule_frontmatter(content: str) -> tuple[str, str]:
    """Parse description and globs from a Cursor rule file body.

    Args:
        content: Raw rule file text.

    Returns:
        Tuple of ``(description, globs)``.

    """
    desc = ""
    globs = ""
    desc_match = re.search(r"^description:\s*([^\n]+)", content, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip().strip("'\"")
    globs_match = re.search(r"^globs:\s*([^\n]+)", content, re.MULTILINE)
    if globs_match:
        globs = globs_match.group(1).strip().strip("'\"")
    return desc, globs


def resolve_zenith_skills() -> set[str]:
    """Retrieve known Zenith skill names from .agents/skills.

    Returns:
        Set of directory names under the Zenith skills root.

    """
    zenith_root = Path(__file__).resolve().parent.parent.parent
    if not zenith_root.exists():
        return set()
    return {
        path.name
        for path in zenith_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
