# ruff: ignore[implicit-namespace-package]
# Standalone root-only skill script; not part of an installed package.
# Git subprocess commands run against user-supplied remotes and cached clones
# in .temp/ only, never shell-interpolated.
"""Agent skill harvester: extracts and benchmarks AI agent capabilities."""

from __future__ import annotations

import contextlib
import json
import re
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
from typing import TYPE_CHECKING

from harvest_metadata import (
    extract_cursor_rule_metadata,
    extract_skill_metadata,
    register_skill,
    resolve_zenith_skills,
)
from harvest_models import (
    IGNORE_DIRS,
    INSTRUCTION_FILENAMES,
    PR_AI_CHECKLIST_KEYWORDS,
    PR_TEMPLATE_NAMES,
    SKILL_RULE_SUFFIXES,
    DiscoveredSkill,
    HarvestResult,
)
from harvest_report import ensure_target_dir, format_harvest_markdown
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

console = Console(highlight=False, markup=False, emoji=False, soft_wrap=True)
error_console = Console(
    stderr=True, highlight=False, markup=False, emoji=False, soft_wrap=True
)

USAGE = (
    "Usage: uv run python "
    ".agents/skills/inspect-module-setup/scripts/harvest_skills.py "
    "<target_path_or_repo> [--refresh]"
)


def _record_instruction_symlink(
    p: Path, rel: str, symlinks: list[tuple[str, str]]
) -> None:
    """Append a symlink target mapping for an instruction file if readable.

    Args:
        p: Candidate instruction file path.
        rel: Repository-relative location of the file.
        symlinks: Mutable accumulator for ``(rel, target)`` pairs.

    """
    if p.is_symlink():
        with contextlib.suppress(OSError):
            symlinks.append((rel, str(p.readlink())))


def _collect_nested_instructions(
    root: Path,
    found: list[str],
    symlinks: list[tuple[str, str]],
) -> None:
    """Deep recursive search for nested instruction files, mutating accumulators.

    Args:
        root: Repository root to walk.
        found: Mutable accumulator for repository-relative instruction paths.
        symlinks: Mutable accumulator for symlink target mappings.

    """
    for p in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.relative_to(root).parts):
            continue
        if p.name in INSTRUCTION_FILENAMES:
            rel = str(p.relative_to(root))
            if rel not in found:
                found.append(rel)
                _record_instruction_symlink(p, rel, symlinks)


def scan_agent_instructions(root: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Detect root and nested instruction files and agent configuration entrypoints.

    Args:
        root: Repository root to scan.

    Returns:
        Tuple of ``(sorted instruction paths, symlink target mappings)``.

    """
    candidate_roots = [
        "AGENTS.md",
        "CLAUDE.md",
        ".cursorrules",
        ".windsurfrules",
        ".clinerules",
        ".github/copilot-instructions.md",
        ".claude/settings.json",
        ".codex/config.toml",
        ".gemini/settings.json",
        ".aider.conf.yml",
        "COPILOT.md",
        "CONVENTIONS.md",
    ]
    found: list[str] = []
    symlinks: list[tuple[str, str]] = []

    for rel_path in candidate_roots:
        p = root / rel_path
        if p.exists():
            found.append(rel_path)
            _record_instruction_symlink(p, rel_path, symlinks)

    # Deep recursive search for nested instructions (e.g. tests/AGENTS.md)
    with contextlib.suppress(OSError):
        _collect_nested_instructions(root, found, symlinks)

    return sorted(found), symlinks


def _build_skill(
    name: str,
    rel_loc: str,
    known_skills: set[str],
    meta: tuple[str, list[str], list[str]],
) -> DiscoveredSkill:
    """Build a :class:`DiscoveredSkill` tagged novel or shared by name.

    Args:
        name: Skill name from frontmatter or directory name.
        rel_loc: Repository-relative location of the skill.
        known_skills: Names present in the Zenith skill library.
        meta: Tuple of ``(description, triggers, helper scripts)``.

    Returns:
        The constructed skill record.

    """
    desc, triggers, scripts = meta
    return DiscoveredSkill(
        name=name,
        location=rel_loc,
        description=desc,
        is_novel=name not in known_skills,
        triggers=triggers,
        scripts=scripts,
        kind="skill",
    )


def _scan_standard_skill_dirs(
    root: Path,
    known_skills: set[str],
    seen_names: set[str],
    novel: list[DiscoveredSkill],
    shared: list[DiscoveredSkill],
) -> None:
    """Scan conventional skill directories, mutating the accumulators.

    Args:
        root: Repository root used to compute relative locations.
        known_skills: Names present in the Zenith skill library.
        seen_names: Mutable set of already-seen skill names.
        novel: Mutable bucket for novel skills.
        shared: Mutable bucket for shared skills.

    """
    skill_dirs = [
        root / ".agents" / "skills",
        root / ".agent" / "skills",
        root / ".cursor" / "skills",
        root / ".cursor" / "rules",
        root / ".gemini" / "skills",
        root / ".claude" / "skills",
        root / ".github" / "skills",
        root / ".vscode" / "skills",
        root / "skills",
    ]

    # 1. Scan standard skill directories
    for base_dir in skill_dirs:
        if not base_dir.is_dir():
            continue

        for item in base_dir.iterdir():
            if item.name.startswith("."):
                continue

            rel_loc = str(item.relative_to(root))

            # Handle Cursor .mdc / .md rules
            if item.suffix in SKILL_RULE_SUFFIXES and base_dir.name == "rules":
                rule = extract_cursor_rule_metadata(item)
                register_skill(
                    DiscoveredSkill(
                        name=rule.name,
                        location=rel_loc,
                        description=rule.description,
                        is_novel=rule.name not in known_skills,
                        kind="cursor-rule",
                    ),
                    seen_names,
                    novel,
                    shared,
                )
                continue

            name, desc, triggers, scripts = extract_skill_metadata(item)
            register_skill(
                _build_skill(name, rel_loc, known_skills, (desc, triggers, scripts)),
                seen_names,
                novel,
                shared,
            )


def _scan_recursive_skill_files(
    root: Path,
    known_skills: set[str],
    seen_names: set[str],
    novel: list[DiscoveredSkill],
    shared: list[DiscoveredSkill],
) -> None:
    """Deep recursive search for any SKILL.md anywhere in the repository.

    Mutates the accumulators in place; tolerates filesystem errors.

    Args:
        root: Repository root to walk.
        known_skills: Names present in the Zenith skill library.
        seen_names: Mutable set of already-seen skill names.
        novel: Mutable bucket for novel skills.
        shared: Mutable bucket for shared skills.

    """
    with contextlib.suppress(OSError):
        for skill_file in root.rglob("SKILL.md"):
            if any(part in IGNORE_DIRS for part in skill_file.relative_to(root).parts):
                continue
            skill_dir = skill_file.parent
            rel_loc = str(skill_dir.relative_to(root))
            name, desc, triggers, scripts = extract_skill_metadata(skill_dir)
            register_skill(
                _build_skill(name, rel_loc, known_skills, (desc, triggers, scripts)),
                seen_names,
                novel,
                shared,
            )


def scan_agent_skills(
    root: Path, known_skills: set[str]
) -> tuple[list[DiscoveredSkill], list[DiscoveredSkill]]:
    """Deep scan for agent skills, instructions, and rules.

    Covers standard directories and the full repository tree.

    Args:
        root: Repository root to scan.
        known_skills: Names present in the Zenith skill library.

    Returns:
        Tuple of ``(novel skills, shared skills)``.

    """
    novel: list[DiscoveredSkill] = []
    shared: list[DiscoveredSkill] = []
    seen_names: set[str] = set()

    _scan_standard_skill_dirs(root, known_skills, seen_names, novel, shared)

    # 2. Deep recursive search for any SKILL.md anywhere in the repository
    _scan_recursive_skill_files(root, known_skills, seen_names, novel, shared)

    return novel, shared


def _scan_mcp_file(path: Path, root: Path) -> list[str]:
    """Extract MCP server summaries from a single JSON configuration file.

    Args:
        path: Candidate ``mcp.json`` file.
        root: Repository root used for relative display paths.

    Returns:
        Server summary strings, or a fallback note when unreadable.

    """
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        srvs = data.get("mcpServers", {})
    except (json.JSONDecodeError, OSError):
        return [f"Config found at `{path.relative_to(root)}`"]

    if not isinstance(srvs, dict):
        return []

    rel_path = str(path.relative_to(root))
    summaries: list[str] = []
    for name, cfg in srvs.items():
        cmd = cfg.get("command", "") if isinstance(cfg, dict) else ""
        summaries.append(f"`{name}` ({cmd or 'stdio'}) in `{rel_path}`")
    return summaries


def scan_mcp_servers(root: Path) -> list[str]:
    """Detect Model Context Protocol (MCP) server definitions and configurations.

    Args:
        root: Repository root to scan.

    Returns:
        Human-readable MCP server summary strings.

    """
    servers: list[str] = []
    mcp_files = [
        root / "mcp.json",
        root / ".cursor" / "mcp.json",
        root / ".vscode" / "mcp.json",
    ]

    for f in mcp_files:
        if f.is_file():
            servers.extend(_scan_mcp_file(f, root))

    # Check for dedicated MCP server scripts or folders
    if (root / "mcp_server.py").is_file():
        servers.append("Dedicated server script: `mcp_server.py`")
    if (root / "src" / "mcp").is_dir():
        servers.append("Native MCP package implementation in `src/mcp/`")

    return servers


def extract_agent_directives(root: Path, instructions: list[str]) -> list[str]:
    """Extract operational rules, prohibitions, and testing mandates.

    Scans instruction files for mandate patterns.

    Args:
        root: Repository root containing the instruction files.
        instructions: Repository-relative instruction file paths.

    Returns:
        Up to ten directive strings prefixed by their source file.

    """
    directives: list[str] = []
    patterns = [
        r"(?:FORBIDDEN|Forbidden|forbidden):\s*([^\n]+)",
        r"(?:ONLY use|Only use|MUST use)\s+([^\n.]+)",
        r"(?:NEVER use|Never use|DO NOT use)\s+([^\n.]+)",
        r"(fail_under\s*=\s*100[^\n]*)",
        r"(strict-no-cover[^\n]*)",
        r"(?:Note for AI Agents|note for AI agents):\s*([^\n]+)",
        r"(?:All imports go at the top[^\n]*)",
    ]

    for rel in instructions:
        p = root / rel
        if not p.is_file() or p.is_symlink():
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            for pat in patterns:
                for match in re.finditer(pat, content):
                    text = match.group(0).strip().rstrip(".")
                    if text and text not in directives:
                        directives.append(f"[{rel}] {text}")
        except OSError:
            pass

    return directives[:10]  # Cap at top 10 most relevant directives


def resolve_repo_root(target_path: Path) -> Path:
    """Return the monorepo parent if target_path is a subdirectory of a clone.

    Falls back to target_path when no repository parent is evident.

    Args:
        target_path: Candidate target directory.

    Returns:
        The resolved repository root.

    """
    if (target_path / ".git").exists():
        return target_path
    parent = target_path.parent
    if (
        parent.exists()
        and parent.name != ".temp"
        and ((parent / ".git").exists() or parent.name.startswith("inspect-"))
    ):
        return parent
    return target_path


def _scan_ai_policy(target_path: Path, repo_root: Path) -> bool:
    """Detect an AI contribution policy file in target or repository roots.

    Args:
        target_path: Primary target directory.
        repo_root: Parent repository root for subdirectory targets.

    Returns:
        True when ``AI_POLICY.md`` (any casing) is present.

    """
    search_roots = (
        (target_path, target_path / ".github", repo_root, repo_root / ".github")
        if repo_root != target_path
        else (target_path, target_path / ".github")
    )
    return any(
        (p / name).exists()
        for p in search_roots
        for name in ("AI_POLICY.md", "ai_policy.md")
    )


def _scan_pr_checklist(target_path: Path, repo_root: Path) -> bool:
    """Detect AI contribution checklists in PR templates.

    Args:
        target_path: Primary target directory.
        repo_root: Parent repository root for subdirectory targets.

    Returns:
        True when a PR template mentions AI tooling or disclosure keywords.

    """
    github_dirs = (
        (target_path / ".github", repo_root / ".github")
        if repo_root != target_path
        else (target_path / ".github",)
    )
    for github_dir in github_dirs:
        for name in PR_TEMPLATE_NAMES:
            tmpl = github_dir / name
            if tmpl.exists():
                try:
                    pr_text = tmpl.read_text(encoding="utf-8", errors="ignore").lower()
                except OSError:
                    continue
                if any(k in pr_text for k in PR_AI_CHECKLIST_KEYWORDS):
                    return True
    return False


def harvest_repo(target_path: Path) -> HarvestResult:
    """Run full, exhaustive agent skill harvest on a target directory.

    Args:
        target_path: Repository or subdirectory to harvest.

    Returns:
        The consolidated :class:`HarvestResult`.

    """
    known_zenith_skills = resolve_zenith_skills()
    instructions, symlinks = scan_agent_instructions(target_path)
    novel_skills, shared_skills = scan_agent_skills(target_path, known_zenith_skills)
    mcp_servers = scan_mcp_servers(target_path)

    # Fallback to parent repository root only for monorepo subdirectories
    repo_root = resolve_repo_root(target_path)
    if not instructions and repo_root != target_path:
        p_inst, p_sym = scan_agent_instructions(repo_root)
        instructions.extend(p_inst)
        symlinks.extend(p_sym)

    ai_policy_present = _scan_ai_policy(target_path, repo_root)
    ai_pr_checklist = _scan_pr_checklist(target_path, repo_root)
    agent_directives = extract_agent_directives(target_path, instructions)

    notes = [f"Symlink `{src}` -> `{target}`" for src, target in symlinks]

    clean_name = target_path.name.removeprefix("inspect-")
    if target_path.parent.name.startswith("inspect-"):
        clean_name = target_path.parent.name.removeprefix("inspect-")

    return HarvestResult(
        target_name=clean_name,
        target_path=target_path,
        instructions=instructions,
        instruction_symlinks=symlinks,
        novel_skills=novel_skills,
        shared_skills=shared_skills,
        mcp_servers=mcp_servers,
        ai_policy_present=ai_policy_present,
        ai_pr_checklist_present=ai_pr_checklist,
        agent_directives=agent_directives,
        notes=notes,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for skill harvesting.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code; 0 on success, 1 on usage or runtime error.

    """
    args = sys.argv[1:] if argv is None else argv
    if not args or not args[0].strip():
        error_console.print(USAGE)
        return 1

    refresh = "--refresh" in args
    target = next(a for a in args if not a.startswith("--"))

    try:
        target_dir = ensure_target_dir(target, refresh=refresh)
        result = harvest_repo(target_dir)
        console.print(format_harvest_markdown(result))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        error_console.print(f"Error harvesting skills: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
