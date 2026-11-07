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
from zenith.ui.app import FeaturesScreen, MetadataScreen, ZenithApp


def test_zenith_app_metadata_screen_initial_state() -> None:
    """Verify that MetadataScreen initializes with expected defaults."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            assert isinstance(app.screen, MetadataScreen)
            assert app.screen.query_one("#project-name", Input).value == "My Project"
            assert app.screen.query_one("#project-slug", Input).value == "my-project"
            assert app.screen.query_one("#package-name", Input).value == "my_project"
            assert app.screen.query_one("#python-version", Select).value == "3.13"
            assert app.screen.query_one("#license", Select).value == "MIT"
            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_slugify_reactive() -> None:
    """Verify that typing project name automatically updates slug and package name."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            name_input = app.screen.query_one("#project-name", Input)
            name_input.value = "Super Fantastic Tool"
            await pilot.pause()

            assert (
                app.screen.query_one("#project-slug", Input).value
                == "super-fantastic-tool"
            )
            assert (
                app.screen.query_one("#package-name", Input).value
                == "super_fantastic_tool"
            )
            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_navigation_and_features_screen() -> None:
    """Verify forward navigation from MetadataScreen to FeaturesScreen."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.click("#next-btn")
            await pilot.pause()
            assert isinstance(app.screen, FeaturesScreen)

            assert app.screen.query_one("#include-cli", Checkbox).value is True
            assert app.screen.query_one("#include-ci-testing", Checkbox).value is True
            assert (
                app.screen.query_one("#include-ci-publishing", Checkbox).value is True
            )
            assert app.screen.query_one("#include-agent-skills", Checkbox).value is True

            ai_list = app.screen.query_one("#ai-tools-list", SelectionList)
            assert set(ai_list.selected) == set(PRESET_RECOMMENDED)
            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_preset_buttons() -> None:
    """Verify that preset buttons on FeaturesScreen update the SelectionList."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.click("#next-btn")
            await pilot.pause()
            assert isinstance(app.screen, FeaturesScreen)
            ai_list = app.screen.query_one("#ai-tools-list", SelectionList)

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


def test_zenith_app_back_navigation_preserves_state() -> None:
    """Verify backward navigation preserves edited metadata and feature selections."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            # Edit metadata on Screen 1
            author_input = app.screen.query_one("#author-name", Input)
            author_input.value = "Ada Lovelace"
            await pilot.pause()

            # Advance to Screen 2
            await pilot.click("#next-btn")
            await pilot.pause()
            assert isinstance(app.screen, FeaturesScreen)

            # Modify a feature and preset on Screen 2
            await pilot.click("#preset-ide-only")

            # Navigate back to Screen 1
            await pilot.click("#back-btn")
            await pilot.pause()
            assert isinstance(app.screen, MetadataScreen)
            assert app.screen.query_one("#author-name", Input).value == "Ada Lovelace"

            # Advance to Screen 2 again and verify preserved state
            await pilot.click("#next-btn")
            await pilot.pause()
            assert isinstance(app.screen, FeaturesScreen)
            ai_list = app.screen.query_one("#ai-tools-list", SelectionList)
            assert set(ai_list.selected) == set(PRESET_IDE_ONLY)

            await pilot.exit(None)

    asyncio.run(run())


def test_zenith_app_submit() -> None:
    """Verify that clicking submit on FeaturesScreen collects config and exits."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            name_input = app.screen.query_one("#project-name", Input)
            name_input.value = "My Nova"
            await pilot.pause()

            await pilot.click("#next-btn")
            await pilot.pause()
            await pilot.click("#preset-ide-only")
            await pilot.click("#submit-btn")

            assert app.result is not None
            assert app.result.project_name == "My Nova"
            assert app.result.project_slug == "my-nova"
            assert set(app.result.ai_tools) == set(PRESET_IDE_ONLY)

    asyncio.run(run())


def test_zenith_app_cancel_on_metadata_screen() -> None:
    """Verify that clicking cancel on MetadataScreen exits with None."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.click("#cancel-btn")
            assert app.result is None

    asyncio.run(run())


def test_zenith_app_cancel_on_features_screen() -> None:
    """Verify that clicking cancel on FeaturesScreen exits with None."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.click("#next-btn")
            await pilot.pause()
            await pilot.click("#cancel-btn")
            assert app.result is None

    asyncio.run(run())


def test_zenith_app_escape_key_cancels() -> None:
    """Verify that pressing Escape triggers action_cancel and exits with None."""

    async def run() -> None:
        app = ZenithApp()
        async with app.run_test(size=(120, 100)) as pilot:
            await pilot.press("escape")
            assert app.result is None

    asyncio.run(run())
