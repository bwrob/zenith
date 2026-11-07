"""Unit tests for Zenith configuration models and presets."""

from __future__ import annotations

from zenith.models import (
    AI_TOOL_METADATA,
    AI_TOOL_PRESETS,
    ALL_AI_TOOLS,
    PRESET_ALL,
    PRESET_CLI_ONLY,
    PRESET_IDE_ONLY,
    PRESET_NONE,
    PRESET_RECOMMENDED,
    SUPPORTED_LICENSES,
    SUPPORTED_PYTHON_VERSIONS,
    ZenithConfig,
    slugify,
)


def test_slugify_conversions() -> None:
    """Verify that slugify handles spaces, special characters, and custom separators."""
    assert slugify("My Cool Project") == "my-cool-project"
    assert slugify("My Cool Project", separator="_") == "my_cool_project"
    assert slugify("Project @ 2026!!!") == "project-2026"
    assert slugify("   trimmed   ") == "trimmed"


def test_presets_completeness() -> None:
    """Verify that AI tool presets are subsets of ALL_AI_TOOLS."""
    assert set(PRESET_ALL) == set(ALL_AI_TOOLS)
    assert set(PRESET_RECOMMENDED).issubset(set(ALL_AI_TOOLS))
    assert set(PRESET_IDE_ONLY).issubset(set(ALL_AI_TOOLS))
    assert set(PRESET_CLI_ONLY).issubset(set(ALL_AI_TOOLS))
    assert PRESET_NONE == ()

    assert AI_TOOL_PRESETS["all"] == PRESET_ALL
    assert AI_TOOL_PRESETS["recommended"] == PRESET_RECOMMENDED
    assert AI_TOOL_PRESETS["ide-only"] == PRESET_IDE_ONLY
    assert AI_TOOL_PRESETS["cli-only"] == PRESET_CLI_ONLY
    assert AI_TOOL_PRESETS["none"] == PRESET_NONE


def test_metadata_covers_all_tools() -> None:
    """Verify that every tool in ALL_AI_TOOLS has human-readable metadata."""
    for tool_id in ALL_AI_TOOLS:
        assert tool_id in AI_TOOL_METADATA
        name, desc = AI_TOOL_METADATA[tool_id]
        assert name
        assert desc


def test_supported_python_versions_and_licenses() -> None:
    """Verify baseline supported Python versions and licenses."""
    assert "3.13" in SUPPORTED_PYTHON_VERSIONS
    assert "3.12" in SUPPORTED_PYTHON_VERSIONS
    assert "MIT" in SUPPORTED_LICENSES


def test_default_config_to_cookiecutter_context() -> None:
    """Verify default ZenithConfig conversion to Cookiecutter context."""
    config = ZenithConfig()
    context = config.to_cookiecutter_context()

    assert context["project_name"] == "My Project"
    assert context["project_slug"] == "my-project"
    assert context["package_name"] == "my_project"
    assert context["include_cli"] is True
    assert context["include_ci_testing"] is True
    assert context["include_agent_skills"] is True
    assert context["python_version"] == "3.13"
    assert context["license"] == "MIT"
    assert "claude" in context["ai_tools"]
    assert "cursor" in context["ai_tools"]


def test_custom_config_to_cookiecutter_context() -> None:
    """Verify customized ZenithConfig conversion to Cookiecutter context."""
    config = ZenithConfig(
        project_name="Custom API",
        project_slug="custom-api",
        package_name="custom_api",
        description="A custom fast API service",
        author_name="Alice Smith",
        author_email="alice@example.com",
        github_username="alice",
        version="0.2.0",
        python_version="3.12",
        license="Apache-2.0",
        include_cli=False,
        include_ci_testing=False,
        include_ci_publishing=False,
        include_agent_skills=False,
        ai_tools=(),
    )
    context = config.to_cookiecutter_context()

    assert context["project_name"] == "Custom API"
    assert context["project_slug"] == "custom-api"
    assert context["package_name"] == "custom_api"
    assert context["python_version"] == "3.12"
    assert context["license"] == "Apache-2.0"
    assert context["include_cli"] is False
    assert context["ai_tools"] == "none"
