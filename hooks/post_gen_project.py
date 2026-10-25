"""Post-generation hook: prune conditional files and wire agent tooling."""

from __future__ import annotations

import contextlib
import json
import os
import pathlib
import re
import shutil
import subprocess

import yaml

PROJECT_DIR = pathlib.Path.cwd().resolve()

CONFIG_FILES_WITH_HEADERS = [
    "pyproject.toml",
    "poe_tasks.toml",
    "ruff.toml",
    "pyrefly.toml",
    "complexipy.toml",
    "zensical.toml",
    "rumdl.toml",
    "tach.toml",
    ".coveragerc",
    "pytest.ini",
    ".taplo.toml",
    "typos.toml",
    "prek.toml",
    ".prettierrc.yaml",
    ".editorconfig",
    ".zizmor.yml",
    ".codex/config.toml",
    ".aider.conf.yml",
    "cosmic-ray.toml",
]


def remove_file(*filepath_parts: str) -> None:
    """Remove a file or symbolic link within the generated project directory.

    Args:
        *filepath_parts: Path segments relative to the project root.

    """
    path = PROJECT_DIR.joinpath(*filepath_parts)
    if path.is_file() or path.is_symlink():
        path.unlink()


def remove_dir(*dirpath_parts: str) -> None:
    """Recursively remove a directory within the generated project directory.

    Args:
        *dirpath_parts: Path segments relative to the project root.

    """
    path = PROJECT_DIR.joinpath(*dirpath_parts)
    if path.is_dir():
        shutil.rmtree(path)


def strip_config_headers() -> None:
    """Strip explanatory template comments from generated configuration files."""
    pattern = re.compile(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+")
    for filename in CONFIG_FILES_WITH_HEADERS:
        filepath = PROJECT_DIR / filename
        if not filepath.is_file():
            continue
        content = filepath.read_text(encoding="utf-8")
        new_content = pattern.sub("", content)
        if new_content != content:
            filepath.write_text(new_content, encoding="utf-8")


def to_bool(val: object) -> bool:
    """Interpret a cookiecutter value as a boolean literal.

    Args:
        val: Raw cookiecutter templating value.

    Returns:
        The boolean interpretation of ``val``.

    """
    if isinstance(val, bool):
        return val
    return str(val).lower() in {"true", "yes", "1", "t", "y", "on"}


PRESET_MAP: dict[str, set[str]] = {
    "all": {
        "aider",
        "claude",
        "codex",
        "copilot",
        "cursor",
        "devin",
        "gemini",
        "hermes",
        "omp",
        "opencode",
        "pi",
        "windsurf",
        "zed",
    },
    "recommended": {"claude", "cursor", "codex", "opencode", "gemini", "copilot"},
    "ide-only": {"cursor", "windsurf", "zed", "copilot"},
    "cli-only": {
        "claude",
        "codex",
        "opencode",
        "gemini",
        "devin",
        "pi",
        "omp",
        "hermes",
        "aider",
    },
    "minimal": set(),
    "none": set(),
}

TOOL_ALIASES: dict[str, str] = {
    "antigravity": "gemini",
    "google-gemini": "gemini",
    "claude-code": "claude",
    "openai-codex": "codex",
    "github-copilot": "copilot",
    "oh-my-pi": "omp",
    "hermes-agent": "hermes",
}

TOOL_CONFIG_PATHS: dict[str, list[tuple[str, ...]]] = {
    "claude": [(".claude",), ("CLAUDE.md",)],
    "gemini": [(".gemini",)],
    "codex": [(".codex",)],
    "opencode": [(".opencode",), ("opencode.json",)],
    "cursor": [(".cursor",), (".cursorrules",)],
    "windsurf": [(".windsurfrules",)],
    "copilot": [(".github", "copilot-instructions.md")],
    "devin": [(".devin",)],
    "zed": [(".zed",)],
    "pi": [(".pi",)],
    "omp": [(".omp",)],
    "hermes": [("HERMES.md",)],
    "aider": [(".aider.conf.yml",)],
}


def resolve_active_ai_tools(raw_ai_tools: str) -> set[str]:
    """Resolve raw cookiecutter ai_tools input into a set of active tool keys.

    Args:
        raw_ai_tools: Raw string specification from cookiecutter prompt.

    Returns:
        Set of active normalized tool identifier strings.

    """
    raw = raw_ai_tools.strip().lower()
    tokens = [t.strip() for t in raw.replace(";", ",").split(",") if t.strip()]
    if len(tokens) == 1 and tokens[0] in PRESET_MAP:
        return set(PRESET_MAP[tokens[0]])
    active: set[str] = set()
    for token in tokens:
        if token in PRESET_MAP:
            active.update(PRESET_MAP[token])
        else:
            resolved = TOOL_ALIASES.get(token, token)
            active.add(resolved)
    return active


def _setup_instruction_aliases(
    agents_path: pathlib.Path, active_tools: set[str]
) -> None:
    if not agents_path.is_file():
        return
    aliases: tuple[tuple[pathlib.Path, str, str], ...] = (
        (PROJECT_DIR / "CLAUDE.md", "AGENTS.md", "claude"),
        (PROJECT_DIR / ".cursorrules", "AGENTS.md", "cursor"),
        (PROJECT_DIR / ".windsurfrules", "AGENTS.md", "windsurf"),
        (PROJECT_DIR / "HERMES.md", "AGENTS.md", "hermes"),
        (PROJECT_DIR / ".pi" / "APPEND_SYSTEM.md", "../AGENTS.md", "pi"),
        (PROJECT_DIR / ".omp" / "SYSTEM.md", "../AGENTS.md", "omp"),
    )
    for alias_path, target_rel, tool_key in aliases:
        if tool_key not in active_tools:
            continue
        alias_path.parent.mkdir(exist_ok=True, parents=True)
        if not os.path.lexists(alias_path):
            try:
                alias_path.symlink_to(target_rel)
            except (OSError, NotImplementedError):
                shutil.copyfile(agents_path, alias_path)


def _setup_cursor_rules(active_tools: set[str]) -> None:
    if "cursor" not in active_tools:
        return
    cursor_rule_file = PROJECT_DIR / ".cursor" / "rules" / "zenith.mdc"
    if not cursor_rule_file.is_file():
        cursor_rule_file.parent.mkdir(exist_ok=True, parents=True)
        cursor_rule_file.write_text(
            "---\n"
            "description: Authoritative project conventions, typing standards, "
            "and workflows\n"
            'globs: ["*"]\n'
            "alwaysApply: true\n"
            "---\n\n"
            "# Project Guidelines\n\n"
            "Consult [AGENTS.md](../../AGENTS.md) for authoritative operational "
            "guidelines, architectural conventions, and development workflows.\n",
            encoding="utf-8",
        )


def _link_subagents_to_dir(tool_dir: pathlib.Path, subagents_src: pathlib.Path) -> None:
    tool_dir.mkdir(exist_ok=True, parents=True)
    for agent_path in sorted(subagents_src.iterdir()):
        if not agent_path.name.endswith(".md"):
            continue
        target_agent_path = tool_dir / agent_path.name
        if not os.path.lexists(target_agent_path):
            rel_src = os.path.relpath(agent_path, tool_dir)
            try:
                target_agent_path.symlink_to(rel_src)
            except (OSError, NotImplementedError):
                shutil.copyfile(agent_path, target_agent_path)


def _codex_subagent_definition(agent_path: pathlib.Path) -> tuple[str, str, str]:
    content = agent_path.read_text(encoding="utf-8")

    frontmatter_match = re.match(
        r"\A---\r?\n(?P<metadata>.*?)\r?\n---\r?\n(?P<instructions>.*)\Z",
        content,
        re.DOTALL,
    )
    if frontmatter_match is None:
        msg = f"Subagent file is missing YAML front matter: {agent_path}"
        raise ValueError(msg)

    metadata: object = yaml.safe_load(frontmatter_match.group("metadata"))
    if not isinstance(metadata, dict):
        msg = f"Subagent front matter must be a mapping: {agent_path}"
        raise TypeError(msg)

    name: object = metadata.get("name")
    description: object = metadata.get("description")
    instructions = frontmatter_match.group("instructions").strip()
    if not isinstance(name, str) or not isinstance(description, str):
        msg = f"Subagent name and description must be strings: {agent_path}"
        raise TypeError(msg)
    if not instructions:
        msg = f"Subagent metadata is incomplete: {agent_path}"
        raise ValueError(msg)

    return name, description, instructions


def _setup_codex_subagents(subagents_src: pathlib.Path) -> None:
    codex_agents_dir = PROJECT_DIR / ".codex" / "agents"
    codex_agents_dir.mkdir(exist_ok=True, parents=True)

    for agent_path in sorted(subagents_src.iterdir()):
        if not agent_path.name.endswith(".md"):
            continue

        agent_name, description, instructions = _codex_subagent_definition(agent_path)
        codex_agent_path = codex_agents_dir / f"{agent_path.stem}.toml"
        if os.path.lexists(codex_agent_path):
            continue

        codex_agent_path.write_text(
            f"name = {json.dumps(agent_name, ensure_ascii=False)}\n"
            f"description = {json.dumps(description, ensure_ascii=False)}\n"
            "developer_instructions = "
            f"{json.dumps(instructions, ensure_ascii=False)}\n",
            encoding="utf-8",
        )


def _setup_subagents(subagents_src: pathlib.Path, active_tools: set[str]) -> None:
    if not subagents_src.is_dir():
        return
    tool_map: dict[str, str] = {
        "claude": ".claude",
        "gemini": ".gemini",
        "cursor": ".cursor",
        "opencode": ".opencode",
    }
    for tool_key, tool_dir_name in tool_map.items():
        if tool_key in active_tools:
            tool_dir = PROJECT_DIR / tool_dir_name / "agents"
            _link_subagents_to_dir(tool_dir, subagents_src)
    if "codex" in active_tools:
        _setup_codex_subagents(subagents_src)


def _prune_all_ai_configs() -> None:
    remove_file("AGENTS.md")
    remove_file("AI_POLICY.md")
    for paths in TOOL_CONFIG_PATHS.values():
        for p in paths:
            remove_dir(*p)
            remove_file(*p)


def prune_inactive_ai_tools(active_tools: set[str], *, is_none: bool) -> None:
    """Remove inactive AI tool directories, config files, and context links.

    Args:
        active_tools: Set of active AI tool keys to preserve.
        is_none: Whether AI tooling is entirely disabled.

    """
    if is_none:
        _prune_all_ai_configs()
        return

    for tool_key, paths in TOOL_CONFIG_PATHS.items():
        if tool_key not in active_tools:
            for p in paths:
                remove_dir(*p)
                remove_file(*p)


def setup_agent_instructions(*, include_agent_skills: bool, raw_ai_tools: str) -> None:
    """Ensure agent instruction links and tool config directories exist.

    Args:
        include_agent_skills: Whether to retain skills and wire SDD subagents.
        raw_ai_tools: Raw string specification of AI tools from prompt.

    """
    is_none = raw_ai_tools.strip().lower() == "none"
    active_tools = set() if is_none else resolve_active_ai_tools(raw_ai_tools)

    prune_inactive_ai_tools(active_tools, is_none=is_none)

    if not include_agent_skills or is_none:
        remove_dir(".agents")
        remove_file("scripts", "check_skills.py")

    if is_none:
        return

    agents_path = PROJECT_DIR / "AGENTS.md"
    _setup_instruction_aliases(agents_path, active_tools)
    _setup_cursor_rules(active_tools)
    if include_agent_skills:
        _setup_subagents(PROJECT_DIR / ".agents" / "subagents", active_tools)


def main() -> None:
    """Generate the final project: prune branches, wire agents, format, install prek."""
    include_cli = to_bool("{{ cookiecutter.include_cli }}")
    include_ci_testing = to_bool("{{ cookiecutter.include_ci_testing }}")
    include_ci_publishing = to_bool("{{ cookiecutter.include_ci_publishing }}")
    include_agent_skills = to_bool("{{ cookiecutter.include_agent_skills }}")
    ai_tools = "{{ cookiecutter.ai_tools }}"
    license_type = "{{ cookiecutter.license }}"
    package_name = "{{ cookiecutter.package_name }}"

    # Strip template educational header comments from generated project configs
    strip_config_headers()

    if not include_cli:
        remove_file("src", package_name, "cli.py")
        remove_file("src", package_name, "_lazy.py")
        remove_file("src", package_name, "__main__.py")
        remove_file("tests", "test_cli.py")
        remove_file("docs", "javascripts", "termynal.js")
        remove_file("docs", "stylesheets", "termynal.css")

    if not include_ci_testing:
        remove_file(".github", "workflows", "python_tests.yaml")
        remove_file(".github", "workflows", "test_redistribute.yaml")
        remove_file(".github", "workflows", "guard-dependencies.yaml")
        remove_file(".github", "workflows", "dependabot-automerge.yaml")
        remove_file(".github", "codecov.yml")

    if not include_ci_publishing:
        remove_file(".github", "workflows", "publish.yaml")
        remove_file(".github", "workflows", "docs.yaml")

    if not include_ci_testing and not include_ci_publishing:
        remove_dir(".github")
        remove_file(".zizmor.yml")
        remove_dir(".agents", "skills", "tool-zizmor")

    if license_type.lower() == "none":
        remove_file("LICENSE")

    setup_agent_instructions(
        include_agent_skills=include_agent_skills,
        raw_ai_tools=ai_tools,
    )
    format_toml_files()
    init_prek()


def format_toml_files() -> None:
    """Format generated TOML files with Taplo if available in PATH."""
    taplo_bin = shutil.which("taplo")
    if taplo_bin:
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                [taplo_bin, "format"],
                cwd=PROJECT_DIR,
                check=False,
                capture_output=True,
            )


def init_prek() -> None:
    """Initialize git repository and install prek git hooks if tools are available."""
    git_bin = shutil.which("git")
    if not git_bin:
        return
    if not (PROJECT_DIR / ".git").is_dir():
        try:
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                [git_bin, "init"],
                cwd=PROJECT_DIR,
                check=False,
                capture_output=True,
            )
        except (OSError, subprocess.SubprocessError):
            return

    prek_bin = shutil.which("prek")
    uv_bin = shutil.which("uv")
    cmd: list[str] | None = None
    if prek_bin:
        cmd = [prek_bin, "install"]
    elif uv_bin:
        cmd = [uv_bin, "run", "prek", "install"]

    if cmd:
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                cmd,
                cwd=PROJECT_DIR,
                check=False,
                capture_output=True,
            )


if __name__ == "__main__":
    main()
