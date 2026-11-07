"""Unit tests for the Zenith Textual setup wizard and AI tools picker."""

from __future__ import annotations

import asyncio

from textual.widgets import Checkbox, Input, Select, SelectionList

from zenith.models import (
    ALL_AI_TOOLS,
    PRESET_CLI_ONLY,
    PRESET_IDE_ONLY,
    PRESET_RECOMMENDED,
)
from zenith.ui.app import ZenithApp


def test_zenith_app_initial_state() -> None:
    """Verify that ZenithApp initializes with recommended defaults."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            assert app.query_one("#project-name", Input).value == "Zenith"
            assert app.query_one("#project-slug", Input).value == "zenith"
            assert app.query_one("#package-name", Input).value == "zenith"
            assert app.query_one("#python-version", Select).value == "3.13"
            assert app.query_one("#license", Select).value == "MIT"

            assert app.query_one("#include-cli", Checkbox).value is True
            assert app.query_one("#include-ci-testing", Checkbox).value is True
            assert app.query_one("#include-ci-publishing", Checkbox).value is True
            assert app.query_one("#include-agent-skills", Checkbox).value is True

            ai_list = app.query_one("#ai-tools-list", SelectionList)
            assert set(ai_list.selected) == set(PRESET_RECOMMENDED)
            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_preset_buttons() -> None:
    """Verify that preset buttons update the SelectionList selections."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            ai_list = app.query_one("#ai-tools-list", SelectionList)

            # Test 'none' preset
            await pilot.click("#preset-none")
            assert len(ai_list.selected) == 0

            # Test 'all' preset
            await pilot.click("#preset-all")
            assert set(ai_list.selected) == set(ALL_AI_TOOLS)

            # Test 'ide-only' preset
            await pilot.click("#preset-ide-only")
            assert set(ai_list.selected) == set(PRESET_IDE_ONLY)

            # Test 'cli-only' preset
            await pilot.click("#preset-cli-only")
            assert set(ai_list.selected) == set(PRESET_CLI_ONLY)

            # Test 'recommended' preset
            await pilot.click("#preset-recommended")
            assert set(ai_list.selected) == set(PRESET_RECOMMENDED)

            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_slugify_reactive() -> None:
    """Verify that typing project name automatically updates slug and package name."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            name_input = app.query_one("#project-name", Input)
            name_input.value = "Super Fantastic Tool"
            await pilot.pause()

            assert app.query_one("#project-slug", Input).value == "super-fantastic-tool"
            assert app.query_one("#package-name", Input).value == "super_fantastic_tool"
            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_submit() -> None:
    """Verify that clicking submit collects configuration and exits cleanly."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.click("#preset-ide-only")
            await pilot.click("#submit-btn")
            assert app.result is not None
            assert set(app.result.ai_tools) == set(PRESET_IDE_ONLY)
            assert app.result.project_name == "Zenith"

    asyncio.run(run())


def test_zenith_app_cancel() -> None:
    """Verify that clicking cancel or pressing escape exits with no result."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.click("#cancel-btn")
            assert app.result is None

    asyncio.run(run())
