"""Agent skill harvester: extracts and benchmarks AI agent capabilities."""

import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

# Directories to ignore during recursive filesystem traversal
IGNORE_DIRS: set[str] = {
    ".git",
    ".venv",
    "venv",
    ".tox",
    "node_modules",
    "build",
    "dist",
    "__pycache__",
    ".eggs",
    ".pytest_cache",
    ".ruff_cache",
    ".temp",
}


@dataclass(frozen=True)
class DiscoveredSkill:
    """Represents an agent skill found in a repository."""

    name: str
    location: str
    description: str = ""
    is_novel: bool = True
    triggers: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    kind: str = "skill"  # "skill", "cursor-rule", "mcp-server"


@dataclass(frozen=True)
class HarvestResult:
    """Consolidated harvest analysis of agent skills and instructions."""

    target_name: str
    target_path: Path
    instructions: list[str] = field(default_factory=list)
    instruction_symlinks: list[tuple[str, str]] = field(default_factory=list)
    novel_skills: list[DiscoveredSkill] = field(default_factory=list)
    shared_skills: list[DiscoveredSkill] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)
    ai_policy_present: bool = False
    ai_pr_checklist_present: bool = False
    agent_directives: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def extract_skill_metadata(skill_path: Path) -> tuple[str, str, list[str], list[str]]:
    """Extract skill name, description, triggers, and helper scripts from a SKILL.md or directory."""
    skill_md = skill_path if skill_path.is_file() else (skill_path / "SKILL.md")
    name = skill_path.parent.name if skill_path.is_file() else skill_path.name
    desc = ""
    triggers: list[str] = []
    scripts: list[str] = []

    # Check for helper scripts
    script_dir = skill_path if skill_path.is_dir() else skill_path.parent
    scripts_path = script_dir / "scripts"
    if scripts_path.is_dir():
        scripts = sorted(
            p.name
            for p in scripts_path.iterdir()
            if p.is_file() and not p.name.startswith(".")
        )

    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            # Parse YAML frontmatter if present
            frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            fm_text = frontmatter_match.group(1) if frontmatter_match else content

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
                desc = " ".join(line.strip() for line in raw_desc.splitlines()).strip(
                    "'\""
                )

            # Look for triggers or activation patterns
            triggers_match = re.search(
                r"(?:triggers|keywords|when to use):\s*([^\n]+)", fm_text, re.IGNORECASE
            )
            if triggers_match:
                triggers = [
                    t.strip().strip("'\"")
                    for t in triggers_match.group(1).split(",")
                    if t.strip()
                ]
        except OSError:
            pass

    return name, desc, triggers, scripts


def extract_cursor_rule_metadata(rule_path: Path) -> DiscoveredSkill:
    """Extract metadata from modern Cursor .mdc or .md rule files."""
    name = rule_path.stem
    desc = ""
    globs = ""
    try:
        content = rule_path.read_text(encoding="utf-8", errors="ignore")
        desc_match = re.search(r"^description:\s*([^\n]+)", content, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip().strip("'\"")
        globs_match = re.search(r"^globs:\s*([^\n]+)", content, re.MULTILINE)
        if globs_match:
            globs = globs_match.group(1).strip().strip("'\"")
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


def resolve_zenith_skills() -> set[str]:
    """Retrieve known Zenith skill names from .agents/skills."""
    zenith_root = Path(__file__).resolve().parent.parent.parent
    if not zenith_root.exists():
        return set()
    return {
        path.name
        for path in zenith_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }


def scan_agent_instructions(root: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Detect root and nested instruction files and agent configuration entrypoints."""
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
            if p.is_symlink():
                try:
                    symlinks.append((rel_path, str(p.readlink())))
                except OSError:
                    pass

    # Deep recursive search for nested instructions (e.g. tests/AGENTS.md or packages/*/CLAUDE.md)
    try:
        for p in root.rglob("*"):
            if any(part in IGNORE_DIRS for part in p.relative_to(root).parts):
                continue
            if p.name in ("AGENTS.md", "CLAUDE.md", ".cursorrules", ".windsurfrules"):
                rel = str(p.relative_to(root))
                if rel not in found:
                    found.append(rel)
                    if p.is_symlink():
                        try:
                            symlinks.append((rel, str(p.readlink())))
                        except OSError:
                            pass
    except OSError:
        pass

    return sorted(found), symlinks


def scan_agent_skills(
    root: Path, known_skills: set[str]
) -> tuple[list[DiscoveredSkill], list[DiscoveredSkill]]:
    """Deep scan for agent skills, instructions, and rules across standard directories and tree."""
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

    novel: list[DiscoveredSkill] = []
    shared: list[DiscoveredSkill] = []
    seen_names: set[str] = set()

    # 1. Scan standard skill directories
    for base_dir in skill_dirs:
        if not base_dir.exists() or not base_dir.is_dir():
            continue

        for item in base_dir.iterdir():
            if item.name.startswith("."):
                continue

            rel_loc = str(item.relative_to(root))

            # Handle Cursor .mdc / .md rules
            if item.suffix in (".mdc", ".md") and base_dir.name == "rules":
                rule = extract_cursor_rule_metadata(item)
                rule = DiscoveredSkill(
                    name=rule.name,
                    location=rel_loc,
                    description=rule.description,
                    is_novel=rule.name not in known_skills,
                    kind="cursor-rule",
                )
                if rule.name not in seen_names:
                    seen_names.add(rule.name)
                    if rule.is_novel:
                        novel.append(rule)
                    else:
                        shared.append(rule)
                continue

            name, desc, triggers, scripts = extract_skill_metadata(item)
            if name in seen_names:
                continue
            seen_names.add(name)

            is_novel = name not in known_skills
            skill = DiscoveredSkill(
                name=name,
                location=rel_loc,
                description=desc,
                is_novel=is_novel,
                triggers=triggers,
                scripts=scripts,
                kind="skill",
            )

            if is_novel:
                novel.append(skill)
            else:
                shared.append(skill)

    # 2. Deep recursive search for any SKILL.md anywhere in the repository
    try:
        for skill_file in root.rglob("SKILL.md"):
            if any(part in IGNORE_DIRS for part in skill_file.relative_to(root).parts):
                continue
            skill_dir = skill_file.parent
            rel_loc = str(skill_dir.relative_to(root))
            name, desc, triggers, scripts = extract_skill_metadata(skill_dir)
            if name in seen_names:
                continue
            seen_names.add(name)

            is_novel = name not in known_skills
            skill = DiscoveredSkill(
                name=name,
                location=rel_loc,
                description=desc,
                is_novel=is_novel,
                triggers=triggers,
                scripts=scripts,
                kind="skill",
            )
            if is_novel:
                novel.append(skill)
            else:
                shared.append(skill)
    except OSError:
        pass

    return novel, shared


def scan_mcp_servers(root: Path) -> list[str]:
    """Detect Model Context Protocol (MCP) server definitions and configurations."""
    servers: list[str] = []
    mcp_files = [
        root / "mcp.json",
        root / ".cursor" / "mcp.json",
        root / ".vscode" / "mcp.json",
    ]

    for f in mcp_files:
        if f.is_file():
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
                srvs = data.get("mcpServers", {})
                if isinstance(srvs, dict):
                    for name, cfg in srvs.items():
                        cmd = cfg.get("command", "") if isinstance(cfg, dict) else ""
                        rel_path = str(f.relative_to(root))
                        servers.append(f"`{name}` ({cmd or 'stdio'}) in `{rel_path}`")
            except (json.JSONDecodeError, OSError):
                servers.append(f"Config found at `{f.relative_to(root)}`")

    # Check for dedicated MCP server scripts or folders
    if (root / "mcp_server.py").is_file():
        servers.append("Dedicated server script: `mcp_server.py`")
    if (root / "src" / "mcp").is_dir():
        servers.append("Native MCP package implementation in `src/mcp/`")

    return servers


def extract_agent_directives(root: Path, instructions: list[str]) -> list[str]:
    """Extract operational rules, prohibitions, and testing mandates from instruction files."""
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
    """Return the monorepo parent if target_path is a subdirectory inside a cloned repo, else target_path."""
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


def harvest_repo(target_path: Path) -> HarvestResult:
    """Run full, exhaustive agent skill harvest on a target directory."""
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

    search_roots = (
        (target_path, target_path / ".github", repo_root, repo_root / ".github")
        if repo_root != target_path
        else (target_path, target_path / ".github")
    )
    ai_policy_present = any(
        (p / name).exists()
        for p in search_roots
        for name in ("AI_POLICY.md", "ai_policy.md")
    )

    # Check for AI checklists in PR templates
    ai_pr_checklist = False
    github_dirs = (
        (target_path / ".github", repo_root / ".github")
        if repo_root != target_path
        else (target_path / ".github",)
    )
    for p in github_dirs:
        for name in ("PULL_REQUEST_TEMPLATE.md", "pull_request_template.md"):
            tmpl = p / name
            if tmpl.exists():
                try:
                    pr_text = tmpl.read_text(encoding="utf-8", errors="ignore").lower()
                    if any(
                        k in pr_text
                        for k in ("ai ", "ai-", "copilot", "llm", "generated by")
                    ):
                        ai_pr_checklist = True
                        break
                except OSError:
                    pass
        if ai_pr_checklist:
            break

    agent_directives = extract_agent_directives(target_path, instructions)
    notes: list[str] = []

    for src, target in symlinks:
        notes.append(f"Symlink `{src}` -> `{target}`")

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


def format_harvest_markdown(result: HarvestResult) -> str:
    """Format deep harvest results into clean GitHub-flavored markdown."""
    lines: list[str] = [
        f"### Agent Skills & AI Workflow Deep Harvest: `{result.target_name}`",
        "",
        f"- **AI Policy**: {'✅ Present (`AI_POLICY.md`)' if result.ai_policy_present else '❌ None detected'}",
        f"- **PR Template AI Checklist**: {'✅ Present' if result.ai_pr_checklist_present else '❌ None detected'}",
        f"- **Agent Instructions**: {', '.join(f'`{i}`' for i in result.instructions) if result.instructions else 'None detected'}",
    ]

    if result.mcp_servers:
        lines.append(f"- **MCP Servers**: {', '.join(result.mcp_servers)}")

    lines.append("")

    if result.novel_skills:
        lines.append("#### Novel Skills Discovered (Potential Zenith Additions)")
        lines.append(
            "| Skill / Rule Name | Kind | Location | Description & Triggers | Helper Scripts |"
        )
        lines.append("| :--- | :---: | :--- | :--- | :--- |")
        for s in result.novel_skills:
            desc = s.description or "No description provided in frontmatter"
            if s.triggers:
                desc += (
                    f"<br><i>Triggers:</i> {', '.join(f'`{t}`' for t in s.triggers)}"
                )
            scripts_str = (
                ", ".join(f"`{sc}`" for sc in s.scripts) if s.scripts else "None"
            )
            lines.append(
                f"| **`{s.name}`** | `{s.kind}` | `{s.location}` | {desc} | {scripts_str} |"
            )
        lines.append("")
    else:
        lines.append("> [!NOTE]")
        lines.append(
            "> No novel agent skills detected beyond Zenith's existing skill library."
        )
        lines.append("")

    if result.shared_skills:
        lines.append("#### Shared / Overlapping Skills")
        for s in result.shared_skills:
            lines.append(f"- `{s.name}` (`{s.location}`)")
        lines.append("")

    if result.agent_directives:
        lines.append("#### Extracted Agent Operational Directives & Mandates")
        for d in result.agent_directives:
            lines.append(f"- {d}")
        lines.append("")

    if result.notes:
        lines.append("#### Structural Notes")
        for note in result.notes:
            lines.append(f"- {note}")
        lines.append("")

    return "\n".join(lines)


def ensure_target_dir(target_arg: str, refresh: bool = False) -> Path:
    """Resolve target path or clone shallow repo into .temp/ if remote."""
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
            print(f"Refreshing {dest}...", file=sys.stderr)
            subprocess.run(["git", "-C", str(dest), "pull", "--ff-only"], check=False)
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "git",
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
    print(f"Cloning {url} into {dest}...", file=sys.stderr)
    subprocess.run(cmd, check=True)
    return dest


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for skill harvesting."""
    args = sys.argv[1:] if argv is None else argv
    if not args or not args[0].strip():
        print(
            "Usage: uv run python .agents/skills/inspect-module-setup/scripts/harvest_skills.py <target_path_or_repo> [--refresh]",
            file=sys.stderr,
        )
        return 1

    refresh = "--refresh" in args
    target = next(a for a in args if not a.startswith("--"))

    try:
        target_dir = ensure_target_dir(target, refresh=refresh)
        result = harvest_repo(target_dir)
        print(format_harvest_markdown(result))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Error harvesting skills: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
