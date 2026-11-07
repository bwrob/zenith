"""Data models, configuration parameters, and presets for Zenith projects."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

ALL_AI_TOOLS: tuple[str, ...] = (
    "claude",
    "cursor",
    "codex",
    "opencode",
    "gemini",
    "copilot",
    "devin",
    "zed",
    "pi",
    "omp",
    "hermes",
    "aider",
    "windsurf",
)

PRESET_ALL: tuple[str, ...] = ALL_AI_TOOLS
PRESET_RECOMMENDED: tuple[str, ...] = (
    "claude",
    "cursor",
    "codex",
    "opencode",
    "gemini",
    "copilot",
)
PRESET_IDE_ONLY: tuple[str, ...] = ("cursor", "windsurf", "zed", "copilot")
PRESET_CLI_ONLY: tuple[str, ...] = (
    "claude",
    "codex",
    "opencode",
    "gemini",
    "devin",
    "pi",
    "omp",
    "hermes",
    "aider",
)
PRESET_NONE: tuple[str, ...] = ()

AI_TOOL_PRESETS: dict[str, tuple[str, ...]] = {
    "all": PRESET_ALL,
    "recommended": PRESET_RECOMMENDED,
    "ide-only": PRESET_IDE_ONLY,
    "cli-only": PRESET_CLI_ONLY,
    "none": PRESET_NONE,
}

AI_TOOL_METADATA: dict[str, tuple[str, str]] = {
    "claude": ("Claude Code", "CLAUDE.md symlink and .claude/settings.json"),
    "cursor": ("Cursor", ".cursorrules symlink and .cursor/rules/zenith.mdc"),
    "codex": ("OpenAI Codex", ".codex/config.toml and project subagents"),
    "opencode": ("OpenCode", "opencode.json and .opencode/agents/"),
    "gemini": (
        "Google Gemini & Antigravity",
        ".gemini/settings.json and subagents",
    ),
    "copilot": ("GitHub Copilot", ".github/copilot-instructions.md"),
    "devin": ("Devin", ".devin/config.json with poe tasks authorized"),
    "zed": ("Zed Editor", ".zed/settings.json and .zed/tasks.json"),
    "pi": ("Pi Coding Assistant", ".pi/settings.json with AGENTS.md injection"),
    "omp": ("Oh My Pi", ".omp/SYSTEM.md symlink"),
    "hermes": ("Hermes Agent", "HERMES.md symlink to AGENTS.md"),
    "aider": ("Aider", ".aider.conf.yml with poe lint and test wiring"),
    "windsurf": ("Windsurf", ".windsurfrules symlink to AGENTS.md"),
}

SUPPORTED_PYTHON_VERSIONS: tuple[str, ...] = ("3.12", "3.13", "3.14", "3.15")

SUPPORTED_LICENSES: tuple[str, ...] = ("MIT", "Apache-2.0", "BSD-3-Clause", "None")


def slugify(value: str, separator: str = "-") -> str:
    """Normalize a string to a valid alphanumeric slug with custom separator.

    Args:
        value: Input string to convert to a slug.
        separator: Character separating words in the slug.

    Returns:
        Lowercased alphanumeric slug.

    """
    cleaned = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s_]+", separator, cleaned)


@dataclass(frozen=True, slots=True)
class ZenithConfig:
    """Configuration parameters for generating a new Zenith project."""

    project_name: str = "My Project"
    project_slug: str = "my-project"
    package_name: str = "my_project"
    description: str = "A modern Python project."
    author_name: str = "Author Name"
    author_email: str = "author@example.com"
    github_username: str = "author"
    version: str = "0.1.0"
    python_version: str = "3.12"
    license: str = "MIT"
    include_cli: bool = True
    include_ci_testing: bool = True
    include_ci_publishing: bool = True
    include_agent_skills: bool = True
    ai_tools: tuple[str, ...] = PRESET_RECOMMENDED

    def to_cookiecutter_context(self) -> dict[str, Any]:
        """Convert configuration to Cookiecutter template context variables.

        Returns:
            Dictionary matching variables expected by cookiecutter.json.

        """
        raw_ai_tools = ",".join(self.ai_tools) if self.ai_tools else "none"
        return {
            "project_name": self.project_name,
            "project_slug": self.project_slug,
            "package_name": self.package_name,
            "description": self.description,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "github_username": self.github_username,
            "version": self.version,
            "python_version": self.python_version,
            "license": self.license,
            "include_cli": self.include_cli,
            "include_ci_testing": self.include_ci_testing,
            "include_ci_publishing": self.include_ci_publishing,
            "include_agent_skills": self.include_agent_skills,
            "ai_tools": raw_ai_tools,
        }
