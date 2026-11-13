"""Screen 2 of the Zenith Textual setup wizard: features and AI integrations."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast, override

from textual import on
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Label,
    SelectionList,
)
from textual.widgets.selection_list import Selection

from zenith.models import (
    AI_TOOL_METADATA,
    AI_TOOL_PRESETS,
    ALL_AI_TOOLS,
    ZenithConfig,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult

    from zenith.ui.app import ZenithApp


class FeaturesScreen(Screen[object]):
    """Screen 2: Project Features and AI Integrations."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+s", "submit", "Scaffold Project"),
    ]

    @override
    def compose(self) -> ComposeResult:
        """Compose the features and AI tool integration widgets.

        Yields:
            Widgets comprising the features and AI integrations screen.

        """
        cfg = self.zenith_app.config_state
        target_path = (Path(cfg.output_dir).expanduser() / cfg.project_slug).resolve()
        summary_text = (
            f"Target: {target_path} · Package: {cfg.package_name} · "
            f"Python {cfg.python_version} · {cfg.license}"
        )
        yield Header()
        with VerticalScroll():
            yield Label("Zenith Project Initializer", classes="brand-title")
            yield Label(
                "Step 2 of 2: Features & AI Assistant Tooling",
                classes="brand-subtitle",
            )
            yield Label(summary_text, id="step1-summary", classes="step-summary")

            yield Label("Core Project Features", classes="section-title")
            yield Checkbox(
                "Include Typer/Rich command-line interface",
                value=cfg.include_cli,
                id="include-cli",
            )
            yield Checkbox(
                "Include documentation website (docs/ & zensical.toml)",
                value=cfg.include_docs,
                id="include-docs",
            )
            yield Checkbox(
                "Include mutation testing tooling (cosmic-ray & mutmut)",
                value=cfg.include_mutation_testing,
                id="include-mutation-testing",
            )
            yield Checkbox(
                "Generate GitHub Actions CI testing workflows",
                value=cfg.include_ci_testing,
                id="include-ci-testing",
            )
            yield Checkbox(
                "Generate GitHub Actions publishing workflows",
                value=cfg.include_ci_publishing,
                id="include-ci-publishing",
            )
            yield Checkbox(
                "Include agent skills suite (.agents/)",
                value=cfg.include_agent_skills,
                id="include-agent-skills",
            )

            yield Label("Project Setup & Automation", classes="section-title")
            yield Checkbox(
                "Initialize Git repository (git init)",
                value=cfg.init_git,
                id="init-git",
            )
            yield Checkbox(
                "Run uv sync after scaffolding",
                value=cfg.run_uv_sync,
                id="run-uv-sync",
            )
            yield Checkbox(
                "Install Git hooks (prek install)",
                value=cfg.install_git_hooks and cfg.init_git,
                disabled=not cfg.init_git,
                id="install-git-hooks",
            )

            yield Label(
                f"AI Assistant Integrations "
                f"({len(cfg.ai_tools)} / {len(ALL_AI_TOOLS)} selected)",
                id="ai-tools-heading",
                classes="section-title",
            )
            with Horizontal(classes="preset-bar"):
                yield Button(
                    "Recommended",
                    id="preset-recommended",
                    variant="primary",
                )
                yield Button("All", id="preset-all")
                yield Button("IDE Only", id="preset-ide-only")
                yield Button("CLI Only", id="preset-cli-only")
                yield Button("None", id="preset-none")

            selections = [
                Selection(
                    f"{AI_TOOL_METADATA[tool_id][0]}  ({AI_TOOL_METADATA[tool_id][1]})",
                    tool_id,
                    tool_id in cfg.ai_tools,
                )
                for tool_id in ALL_AI_TOOLS
            ]
            yield SelectionList[str](*selections, id="ai-tools-list")

            with Horizontal(classes="actions-bar"):
                yield Button("← Back", id="back-btn")
                yield Button(
                    "Scaffold Project",
                    id="submit-btn",
                    variant="success",
                )
                yield Button("Cancel", id="cancel-btn", variant="error")
        yield Footer()

    @property
    def zenith_app(self) -> ZenithApp:
        """Typed reference to parent ZenithApp."""
        return cast("ZenithApp", self.app)

    def on_mount(self) -> None:
        """Synchronize AI tool counter and active preset highlight on mount."""
        self._sync_ai_tools_status()

    def _sync_ai_tools_status(self) -> None:
        """Update the AI tools selection count and active preset button style."""
        ai_list = self.query_one("#ai-tools-list", SelectionList)
        selected_set = set(ai_list.selected)
        heading = self.query_one("#ai-tools-heading", Label)
        heading.update(
            f"AI Assistant Integrations "
            f"({len(selected_set)} / {len(ALL_AI_TOOLS)} selected)"
        )
        for preset_name, preset_tools in AI_TOOL_PRESETS.items():
            btn = self.query_one(f"#preset-{preset_name}", Button)
            btn.variant = "primary" if selected_set == set(preset_tools) else "default"

    @on(SelectionList.SelectedChanged, "#ai-tools-list")
    def on_ai_tools_changed(self) -> None:
        """Refresh AI tools counter and preset highlight when selection changes."""
        self._sync_ai_tools_status()

    def _apply_tool_preset(self, tools: Sequence[str]) -> None:
        """Update selection list checkboxes to match specified tool sequence.

        Args:
            tools: Sequence of tool identifier strings to activate.

        """
        tool_set = set(tools)
        ai_list = self.query_one("#ai-tools-list", SelectionList)
        ai_list.deselect_all()
        for tool_id in ALL_AI_TOOLS:
            if tool_id in tool_set:
                ai_list.select(tool_id)

    @on(Button.Pressed, "#preset-all")
    def on_preset_all(self) -> None:
        """Select all AI tool configurations."""
        self.query_one("#ai-tools-list", SelectionList).select_all()

    @on(Button.Pressed, "#preset-none")
    def on_preset_none(self) -> None:
        """Deselect all AI tool configurations."""
        self.query_one("#ai-tools-list", SelectionList).deselect_all()

    @on(Button.Pressed, "#preset-recommended")
    def on_preset_recommended(self) -> None:
        """Select recommended AI tools preset."""
        self._apply_tool_preset(AI_TOOL_PRESETS["recommended"])

    @on(Button.Pressed, "#preset-ide-only")
    def on_preset_ide_only(self) -> None:
        """Select IDE-only AI tools preset."""
        self._apply_tool_preset(AI_TOOL_PRESETS["ide-only"])

    @on(Button.Pressed, "#preset-cli-only")
    def on_preset_cli_only(self) -> None:
        """Select CLI-only AI tools preset."""
        self._apply_tool_preset(AI_TOOL_PRESETS["cli-only"])

    @on(Checkbox.Changed, "#init-git")
    def on_init_git_changed(self, event: Checkbox.Changed) -> None:
        """Enable or disable Git hooks checkbox based on Git initialization.

        Args:
            event: Checkbox change event for `#init-git`.

        """
        hooks_box = self.query_one("#install-git-hooks", Checkbox)
        hooks_box.disabled = not event.value
        if not event.value:
            hooks_box.value = False

    def _collect_features(self) -> ZenithConfig:
        """Collect feature checkboxes and AI tool selections into ZenithConfig.

        Returns:
            Updated ZenithConfig instance.

        """
        ai_list = self.query_one("#ai-tools-list", SelectionList)
        init_git = self.query_one("#init-git", Checkbox).value
        return replace(
            self.zenith_app.config_state,
            include_cli=self.query_one("#include-cli", Checkbox).value,
            include_docs=self.query_one("#include-docs", Checkbox).value,
            include_mutation_testing=self.query_one(
                "#include-mutation-testing",
                Checkbox,
            ).value,
            include_ci_testing=self.query_one(
                "#include-ci-testing",
                Checkbox,
            ).value,
            include_ci_publishing=self.query_one(
                "#include-ci-publishing",
                Checkbox,
            ).value,
            include_agent_skills=self.query_one(
                "#include-agent-skills",
                Checkbox,
            ).value,
            init_git=init_git,
            run_uv_sync=self.query_one("#run-uv-sync", Checkbox).value,
            install_git_hooks=(
                init_git and self.query_one("#install-git-hooks", Checkbox).value
            ),
            ai_tools=tuple(ai_list.selected),
        )

    @on(Button.Pressed, "#back-btn")
    def action_back(self) -> None:
        """Persist current feature selections and return to MetadataScreen."""
        self.zenith_app.config_state = self._collect_features()
        self.zenith_app.pop_screen()

    @on(Button.Pressed, "#submit-btn")
    def action_submit(self) -> None:
        """Collect features, finalize ZenithConfig, and exit successfully."""
        self.zenith_app.config_state = self._collect_features()
        self.zenith_app.finish()

    @on(Button.Pressed, "#cancel-btn")
    def action_cancel(self) -> None:
        """Abort the wizard and exit without scaffolding."""
        self.zenith_app.abort()
