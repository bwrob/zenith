"""Textual application for interactive project setup."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, ClassVar, cast, override

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Select,
    SelectionList,
)
from textual.widgets.selection_list import Selection

from zenith.models import (
    AI_TOOL_METADATA,
    AI_TOOL_PRESETS,
    ALL_AI_TOOLS,
    SUPPORTED_LICENSES,
    SUPPORTED_PYTHON_VERSIONS,
    ZenithConfig,
    slugify,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


ZENITH_CSS = """
Screen {
    background: #020408;
    color: #e0f2fe;
}
Header {
    background: #0f172a;
    color: #38bdf8;
}
Footer {
    background: #0f172a;
}
VerticalScroll {
    padding: 1 2;
    background: #020408;
}
.brand-title {
    text-style: bold;
    color: #38bdf8;
    margin-top: 1;
    margin-bottom: 0;
}
.brand-subtitle {
    color: #94a3b8;
    margin-bottom: 1;
}
.section-title {
    text-style: bold;
    color: #38bdf8;
    margin-top: 1;
    margin-bottom: 1;
}
.field-label {
    color: #94a3b8;
    margin-top: 1;
}
Input {
    background: #1e293b;
    border: tall #334155;
    color: #e0f2fe;
}
Input:focus {
    border: tall #38bdf8;
}
Select {
    background: #1e293b;
    border: tall #334155;
    color: #e0f2fe;
}
Select:focus {
    border: tall #38bdf8;
}
Checkbox {
    color: #e0f2fe;
    margin-top: 0;
    margin-bottom: 0;
}
.preset-bar {
    height: auto;
    margin-top: 1;
    margin-bottom: 1;
}
.preset-bar Button {
    margin-right: 1;
    background: #1e293b;
    color: #e0f2fe;
    border: solid #334155;
}
.preset-bar Button:hover {
    border: solid #38bdf8;
    color: #38bdf8;
}
#preset-recommended {
    border: solid #0284c7;
    color: #38bdf8;
}
#ai-tools-list {
    height: 14;
    border: solid #0284c7;
    background: #0f172a;
    color: #e0f2fe;
    margin-bottom: 1;
}
#ai-tools-list:focus {
    border: solid #38bdf8;
}
.actions-bar {
    height: auto;
    margin-top: 2;
    margin-bottom: 2;
}
.actions-bar Button {
    margin-right: 2;
}
#next-btn {
    background: #0284c7;
    color: #ffffff;
    border: solid #38bdf8;
}
#back-btn {
    background: #1e293b;
    color: #e0f2fe;
    border: solid #334155;
}
#submit-btn {
    background: #0ea5e9;
    color: #ffffff;
    border: solid #38bdf8;
}
#cancel-btn {
    background: #1e293b;
    color: #f43f5e;
    border: solid #f43f5e;
}
"""


class MetadataScreen(Screen[object]):
    """Screen 1: Project Identity and Runtime Licensing."""

    @override
    def compose(self) -> ComposeResult:
        """Compose the metadata configuration widgets.

        Yields:
            Widgets comprising the metadata configuration screen.

        """
        cfg = self.zenith_app.config_state
        yield Header()
        with VerticalScroll():
            yield Label("Zenith Project Initializer", classes="brand-title")
            yield Label(
                "Step 1 of 2: Project Identity & Licensing",
                classes="brand-subtitle",
            )

            yield Label("Project Name:", classes="field-label")
            yield Input(
                value=cfg.project_name,
                placeholder="My Project",
                id="project-name",
            )

            yield Label("Project Slug (Directory name):", classes="field-label")
            yield Input(
                value=cfg.project_slug,
                placeholder="my-project",
                id="project-slug",
            )

            yield Label(
                "Python Package Name (Import identifier):",
                classes="field-label",
            )
            yield Input(
                value=cfg.package_name,
                placeholder="my_project",
                id="package-name",
            )

            yield Label("Short Description:", classes="field-label")
            yield Input(
                value=cfg.description,
                placeholder="A modern Python project...",
                id="description",
            )

            yield Label("Author Full Name:", classes="field-label")
            yield Input(
                value=cfg.author_name,
                placeholder="Author Name",
                id="author-name",
            )

            yield Label("Author Email:", classes="field-label")
            yield Input(
                value=cfg.author_email,
                placeholder="author@example.com",
                id="author-email",
            )

            yield Label(
                "GitHub Username or Organization:",
                classes="field-label",
            )
            yield Input(
                value=cfg.github_username,
                placeholder="username",
                id="github-username",
            )

            yield Label("Runtime & Licensing", classes="section-title")
            python_options = [(v, v) for v in SUPPORTED_PYTHON_VERSIONS]
            yield Label("Target Python Version:", classes="field-label")
            yield Select(
                python_options,
                value=cfg.python_version,
                id="python-version",
            )

            license_options = [(lic, lic) for lic in SUPPORTED_LICENSES]
            yield Label("Open Source License:", classes="field-label")
            yield Select(license_options, value=cfg.license, id="license")

            with Horizontal(classes="actions-bar"):
                yield Button(
                    "Next: Features & Integrations →",
                    id="next-btn",
                    variant="primary",
                )
                yield Button("Cancel", id="cancel-btn", variant="error")
        yield Footer()

    @property
    def zenith_app(self) -> ZenithApp:
        """Typed reference to parent ZenithApp."""
        return cast("ZenithApp", self.app)

    @on(Input.Changed, "#project-name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Synchronize slug and package name when project name is altered.

        Args:
            event: Input change event with updated string.

        """
        slug_input = self.query_one("#project-slug", Input)
        pkg_input = self.query_one("#package-name", Input)
        slug_input.value = slugify(event.value)
        pkg_input.value = slugify(event.value, separator="_")

    @on(Button.Pressed, "#next-btn")
    def action_next(self) -> None:
        """Collect Screen 1 form fields and navigate to Screen 2."""
        py_val = str(self.query_one("#python-version", Select).value)
        lic_val = str(self.query_one("#license", Select).value)
        self.zenith_app.config_state = replace(
            self.zenith_app.config_state,
            project_name=self.query_one("#project-name", Input).value.strip(),
            project_slug=self.query_one("#project-slug", Input).value.strip(),
            package_name=self.query_one("#package-name", Input).value.strip(),
            description=self.query_one("#description", Input).value.strip(),
            author_name=self.query_one("#author-name", Input).value.strip(),
            author_email=self.query_one("#author-email", Input).value.strip(),
            github_username=self.query_one(
                "#github-username",
                Input,
            ).value.strip(),
            python_version=py_val,
            license=lic_val,
        )
        self.zenith_app.push_screen(FeaturesScreen())

    @on(Button.Pressed, "#cancel-btn")
    def action_cancel(self) -> None:
        """Abort the wizard and exit without scaffolding."""
        self.zenith_app.abort()


class FeaturesScreen(Screen[object]):
    """Screen 2: Project Features and AI Integrations."""

    @override
    def compose(self) -> ComposeResult:
        """Compose the features and AI tool integration widgets.

        Yields:
            Widgets comprising the features and AI integrations screen.

        """
        cfg = self.zenith_app.config_state
        yield Header()
        with VerticalScroll():
            yield Label("Zenith Project Initializer", classes="brand-title")
            yield Label(
                "Step 2 of 2: Features & AI Assistant Tooling",
                classes="brand-subtitle",
            )

            yield Label("Core Project Features", classes="section-title")
            with Vertical():
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
            with Vertical():
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
                    value=cfg.install_git_hooks,
                    id="install-git-hooks",
                )

            yield Label(
                "AI Assistant Integrations",
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

    @on(Button.Pressed, "#back-btn")
    def action_back(self) -> None:
        """Persist current feature selections and return to MetadataScreen."""
        ai_list = self.query_one("#ai-tools-list", SelectionList)
        self.zenith_app.config_state = replace(
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
            init_git=self.query_one("#init-git", Checkbox).value,
            run_uv_sync=self.query_one("#run-uv-sync", Checkbox).value,
            install_git_hooks=self.query_one("#install-git-hooks", Checkbox).value,
            ai_tools=tuple(ai_list.selected),
        )
        self.zenith_app.pop_screen()

    @on(Button.Pressed, "#submit-btn")
    def action_submit(self) -> None:
        """Collect features, finalize ZenithConfig, and exit successfully."""
        ai_list = self.query_one("#ai-tools-list", SelectionList)
        self.zenith_app.config_state = replace(
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
            init_git=self.query_one("#init-git", Checkbox).value,
            run_uv_sync=self.query_one("#run-uv-sync", Checkbox).value,
            install_git_hooks=self.query_one("#install-git-hooks", Checkbox).value,
            ai_tools=tuple(ai_list.selected),
        )
        self.zenith_app.finish()

    @on(Button.Pressed, "#cancel-btn")
    def action_cancel(self) -> None:
        """Abort the wizard and exit without scaffolding."""
        self.zenith_app.abort()


class ZenithApp(App[ZenithConfig | None]):
    """Interactive Textual TUI wizard for configuring Zenith projects."""

    TITLE = "Zenith Project Initializer"
    SUB_TITLE = "Modern Python 3.12+ Scaffolding"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel / Exit"),
    ]

    CSS = ZENITH_CSS

    def __init__(self, initial_config: ZenithConfig | None = None) -> None:
        """Initialize ZenithApp with default or provided configuration.

        Args:
            initial_config: Optional baseline configuration defaults.

        """
        super().__init__()
        self.initial_config = initial_config or ZenithConfig()
        self.config_state = self.initial_config
        self.result: ZenithConfig | None = None

    @override
    def get_default_screen(self) -> Screen[object]:
        """Return the default root screen for the application.

        Returns:
            The default root screen instance.

        """
        return MetadataScreen()

    def finish(self) -> None:
        """Finalize configuration and exit successfully."""
        self.result = self.config_state
        self.exit(self.result)

    def abort(self) -> None:
        """Abort wizard and exit cleanly without result."""
        self.result = None
        self.exit(None)

    def action_cancel(self) -> None:
        """Handle escape keybinding cancellation."""
        self.abort()
