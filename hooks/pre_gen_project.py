"""Pre-generation hook: validate prerequisites, project slug, and package name."""

from __future__ import annotations

import keyword
import re
import shutil
import sys

from rich.console import Console

error_console = Console(stderr=True, highlight=False)

MIN_PYTHON_VERSION = (3, 12)

if sys.version_info < MIN_PYTHON_VERSION:
    version_str = f"{sys.version_info.major}.{sys.version_info.minor}"
    error_console.print(
        "[bold red]ERROR:[/] Zenith requires Python "
        f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ "
        f"to generate projects. Current version: {version_str}",
    )
    sys.exit(1)

if shutil.which("uv") is None:
    error_console.print(
        "[bold red]ERROR:[/] Zenith projects require 'uv' for "
        "dependency management and builds.\n"
        "Please install uv before continuing: "
        "https://docs.astral.sh/uv/getting-started/installation/",
    )
    sys.exit(1)

if shutil.which("git") is None:
    error_console.print(
        "[bold red]ERROR:[/] Zenith projects require 'git' to be "
        "installed and available in PATH.",
    )
    sys.exit(1)

PACKAGE_REGEX = r"^[a-zA-Z][_a-zA-Z0-9]*$"
package_name = "{{ cookiecutter.package_name }}"

if not re.match(PACKAGE_REGEX, package_name) or keyword.iskeyword(package_name):
    error_console.print(
        f"[bold red]ERROR:[/] The package name '{package_name}' is not a "
        "valid Python package name. "
        "It must start with a letter, contain only alphanumeric characters "
        "and underscores, "
        "and must not be a Python reserved keyword."
    )
    sys.exit(1)

PROJECT_SLUG_REGEX = r"^[-a-zA-Z0-9_]+$"
project_slug = "{{ cookiecutter.project_slug }}"

if not re.match(PROJECT_SLUG_REGEX, project_slug):
    error_console.print(
        f"[bold red]ERROR:[/] The project slug '{project_slug}' is invalid. "
        "It can only contain alphanumeric characters, dashes, and underscores."
    )
    sys.exit(1)

VALID_PRESETS = {"all", "recommended", "ide-only", "cli-only", "minimal", "none"}
VALID_TOOLS = {
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
}
TOOL_ALIASES = {
    "antigravity": "gemini",
    "google-gemini": "gemini",
    "claude-code": "claude",
    "openai-codex": "codex",
    "github-copilot": "copilot",
    "oh-my-pi": "omp",
    "hermes-agent": "hermes",
}

raw_ai_tools = "{{ cookiecutter.ai_tools }}".strip().lower()
tokens = [t.strip() for t in raw_ai_tools.replace(";", ",").split(",") if t.strip()]

if not tokens:
    error_console.print(
        "[bold red]ERROR:[/] 'ai_tools' cannot be empty. "
        "Specify 'all', 'recommended', 'ide-only', 'cli-only', 'minimal', 'none', "
        "or a comma-separated list of tools."
    )
    sys.exit(1)

if not (len(tokens) == 1 and tokens[0] in VALID_PRESETS):
    invalid_tokens: list[str] = []
    for token in tokens:
        resolved = TOOL_ALIASES.get(token, token)
        if resolved not in VALID_TOOLS and token not in VALID_PRESETS:
            invalid_tokens.append(token)
    if invalid_tokens:
        valid_presets_str = ", ".join(sorted(VALID_PRESETS))
        valid_tools_str = ", ".join(sorted(VALID_TOOLS))
        unknown_str = ", ".join(invalid_tokens)
        error_console.print(
            f"[bold red]ERROR:[/] Unknown AI tool or preset in 'ai_tools': "
            f"{unknown_str}\n"
            f"Valid presets: {valid_presets_str}\n"
            f"Valid tool identifiers: {valid_tools_str}"
        )
        sys.exit(1)
