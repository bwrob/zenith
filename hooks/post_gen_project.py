import json
import os
import re
import shutil
import subprocess

import yaml

PROJECT_DIR = os.path.realpath(os.path.curdir)

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
    os.path.join(".codex", "config.toml"),
    ".aider.conf.yml",
    "cosmic-ray.toml",
]


def remove_file(*filepath_parts: str) -> None:
    path = os.path.join(PROJECT_DIR, *filepath_parts)
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)


def remove_dir(*dirpath_parts: str) -> None:
    path = os.path.join(PROJECT_DIR, *dirpath_parts)
    if os.path.isdir(path):
        shutil.rmtree(path)


def strip_config_headers() -> None:
    """Strip explanatory template comments from generated configuration files."""
    pattern = re.compile(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+")
    for filename in CONFIG_FILES_WITH_HEADERS:
        filepath = os.path.join(PROJECT_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = pattern.sub("", content)
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)


def to_bool(val: object) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "yes", "1", "t", "y", "on")


def _setup_instruction_aliases(agents_path: str) -> None:
    for alias_name in ("CLAUDE.md", ".cursorrules", ".windsurfrules"):
        alias_path = os.path.join(PROJECT_DIR, alias_name)
        if os.path.isfile(agents_path) and not os.path.lexists(alias_path):
            try:
                os.symlink("AGENTS.md", alias_path)
            except (OSError, NotImplementedError):
                shutil.copyfile(agents_path, alias_path)


def _setup_cursor_rules() -> None:
    cursor_rules_dir = os.path.join(PROJECT_DIR, ".cursor", "rules")
    os.makedirs(cursor_rules_dir, exist_ok=True)
    cursor_rule_file = os.path.join(cursor_rules_dir, "zenith.mdc")
    if not os.path.isfile(cursor_rule_file):
        with open(cursor_rule_file, "w", encoding="utf-8") as f:
            f.write(
                "---\n"
                "description: Authoritative project conventions, typing standards, and workflows\n"
                'globs: ["*"]\n'
                "alwaysApply: true\n"
                "---\n\n"
                "# Project Guidelines\n\n"
                "Consult [AGENTS.md](../../AGENTS.md) for authoritative operational guidelines, architectural conventions, and development workflows.\n"
            )


def _setup_gemini_settings() -> None:
    gemini_dir = os.path.join(PROJECT_DIR, ".gemini")
    os.makedirs(gemini_dir, exist_ok=True)
    gemini_settings = os.path.join(gemini_dir, "settings.json")
    if not os.path.isfile(gemini_settings):
        with open(gemini_settings, "w", encoding="utf-8") as f:
            f.write('{\n    "contextFileName": "AGENTS.md"\n}\n')


def _setup_claude_settings() -> None:
    claude_dir = os.path.join(PROJECT_DIR, ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    claude_settings = os.path.join(claude_dir, "settings.json")
    if not os.path.isfile(claude_settings):
        with open(claude_settings, "w", encoding="utf-8") as f:
            f.write(
                "{\n"
                '    "permissions": {\n'
                '        "allow": [\n'
                '            "Bash(uv run poe:*)",\n'
                '            "Bash(uv run pytest:*)",\n'
                '            "Bash(uv run ruff:*)",\n'
                '            "Bash(uv run pyrefly:*)",\n'
                '            "Bash(uv run complexipy:*)",\n'
                '            "Bash(uv run tach:*)",\n'
                '            "Bash(uv run rumdl:*)",\n'
                '            "Bash(uv run typos:*)",\n'
                '            "Bash(uv run taplo:*)",\n'
                '            "Bash(uv run zizmor:*)",\n'
                '            "Bash(uv run prek:*)"\n'
                "        ],\n"
                '        "deny": [\n'
                '            "Bash(rm -rf /*)",\n'
                '            "Bash(git push --force:*)"\n'
                "        ]\n"
                "    }\n"
                "}\n"
            )


def _setup_codex_config() -> None:
    codex_dir = os.path.join(PROJECT_DIR, ".codex")
    os.makedirs(codex_dir, exist_ok=True)
    codex_config = os.path.join(codex_dir, "config.toml")
    if not os.path.isfile(codex_config):
        with open(codex_config, "w", encoding="utf-8") as f:
            f.write(
                'approval_policy                = "on-request"\n'
                'project_doc_fallback_filenames = [ "AGENTS.md", "CLAUDE.md" ]\n'
                'sandbox_mode                   = "workspace-write"\n'
            )


def _link_subagents_to_dir(tool_dir: str, subagents_src: str) -> None:
    os.makedirs(tool_dir, exist_ok=True)
    for agent_filename in sorted(os.listdir(subagents_src)):
        if not agent_filename.endswith(".md"):
            continue
        src_agent_file = os.path.join(subagents_src, agent_filename)
        target_agent_file = os.path.join(tool_dir, agent_filename)
        if not os.path.lexists(target_agent_file):
            rel_src = os.path.relpath(src_agent_file, tool_dir)
            try:
                os.symlink(rel_src, target_agent_file)
            except (OSError, NotImplementedError):
                shutil.copyfile(src_agent_file, target_agent_file)


def _codex_subagent_definition(agent_path: str) -> tuple[str, str, str]:
    with open(agent_path, "r", encoding="utf-8") as agent_file:
        content = agent_file.read()

    frontmatter_match = re.match(
        r"\A---\r?\n(?P<metadata>.*?)\r?\n---\r?\n(?P<instructions>.*)\Z",
        content,
        re.DOTALL,
    )
    if frontmatter_match is None:
        raise ValueError(f"Subagent file is missing YAML front matter: {agent_path}")

    metadata: object = yaml.safe_load(frontmatter_match.group("metadata"))
    if not isinstance(metadata, dict):
        raise TypeError(f"Subagent front matter must be a mapping: {agent_path}")

    name: object = metadata.get("name")
    description: object = metadata.get("description")
    instructions = frontmatter_match.group("instructions").strip()
    if not isinstance(name, str) or not isinstance(description, str):
        raise TypeError(f"Subagent name and description must be strings: {agent_path}")
    if not instructions:
        raise ValueError(f"Subagent metadata is incomplete: {agent_path}")

    return name, description, instructions


def _setup_codex_subagents(subagents_src: str) -> None:
    codex_agents_dir = os.path.join(PROJECT_DIR, ".codex", "agents")
    os.makedirs(codex_agents_dir, exist_ok=True)

    for agent_filename in sorted(os.listdir(subagents_src)):
        if not agent_filename.endswith(".md"):
            continue

        agent_path = os.path.join(subagents_src, agent_filename)
        agent_name, description, instructions = _codex_subagent_definition(agent_path)
        codex_agent_path = os.path.join(
            codex_agents_dir,
            f"{os.path.splitext(agent_filename)[0]}.toml",
        )
        if os.path.lexists(codex_agent_path):
            continue

        with open(codex_agent_path, "w", encoding="utf-8") as codex_agent_file:
            codex_agent_file.write(
                f"name = {json.dumps(agent_name, ensure_ascii=False)}\n"
                f"description = {json.dumps(description, ensure_ascii=False)}\n"
                "developer_instructions = "
                f"{json.dumps(instructions, ensure_ascii=False)}\n"
            )


def _setup_subagents(subagents_src: str) -> None:
    if not os.path.isdir(subagents_src):
        return
    for tool_name in (".claude", ".gemini", ".cursor"):
        tool_dir = os.path.join(PROJECT_DIR, tool_name, "agents")
        _link_subagents_to_dir(tool_dir, subagents_src)
    _setup_codex_subagents(subagents_src)


def setup_agent_instructions() -> None:
    """Ensure agent instruction symlinks and configuration directories exist for all AI tools."""
    agents_path = os.path.join(PROJECT_DIR, "AGENTS.md")
    _setup_instruction_aliases(agents_path)
    _setup_cursor_rules()
    _setup_gemini_settings()
    _setup_claude_settings()
    _setup_codex_config()
    _setup_subagents(os.path.join(PROJECT_DIR, ".agents", "subagents"))


def main() -> None:
    include_cli = to_bool("{{ cookiecutter.include_cli }}")
    include_ci_testing = to_bool("{{ cookiecutter.include_ci_testing }}")
    include_ci_publishing = to_bool("{{ cookiecutter.include_ci_publishing }}")
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

    setup_agent_instructions()
    format_toml_files()
    init_prek()


def format_toml_files() -> None:
    """Format generated TOML files with Taplo if available in PATH."""
    taplo_bin = shutil.which("taplo")
    if taplo_bin:
        try:
            subprocess.run(
                [taplo_bin, "format"],
                cwd=PROJECT_DIR,
                check=False,
                capture_output=True,
            )
        except (OSError, subprocess.SubprocessError):
            pass


def init_prek() -> None:
    """Initialize git repository and install prek git hooks if tools are available."""
    git_bin = shutil.which("git")
    if not git_bin:
        return
    git_dir = os.path.join(PROJECT_DIR, ".git")
    if not os.path.isdir(git_dir):
        try:
            subprocess.run(
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
        try:
            subprocess.run(
                cmd,
                cwd=PROJECT_DIR,
                check=False,
                capture_output=True,
            )
        except (OSError, subprocess.SubprocessError):
            pass


if __name__ == "__main__":
    main()
