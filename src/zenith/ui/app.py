"""Textual application for interactive project setup."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
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


class ZenithApp(App[ZenithConfig | None]):
    """Interactive Textual TUI wizard for configuring Zenith projects."""

    TITLE = "Zenith Project Initializer"
    SUB_TITLE = "Modern Python 3.12+ Project Scaffolding"

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "cancel", "Cancel / Exit"),
        Binding("ctrl+s", "submit", "Scaffold Project"),
    ]

    CSS = """
    Screen {
        background: $surface;
    }
    VerticalScroll {
        padding: 1 2;
    }
    .section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 1;
    }
    .field-label {
        color: $text-muted;
        margin-top: 1;
    }
    .preset-bar {
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }
    .preset-bar Button {
        margin-right: 1;
    }
    #ai-tools-list {
        height: 14;
        border: solid $accent;
        margin-bottom: 1;
    }
    .actions-bar {
        height: auto;
        margin-top: 2;
        margin-bottom: 2;
    }
    .actions-bar Button {
        margin-right: 2;
    }
    """

    def __init__(self, initial_config: ZenithConfig | None = None) -> None:
        """Initialize ZenithApp with default or provided configuration.

        Args:
            initial_config: Optional baseline configuration defaults.

        """
        super().__init__()
        self.initial_config = initial_config or ZenithConfig()
        self.result: ZenithConfig | None = None

    def compose(self) -> ComposeResult:
        """Compose the interactive wizard interface widgets.

        Yields:
            Textual widgets comprising the application interface.

        """
        yield Header()
        with VerticalScroll():
            yield Label("Project Metadata", classes="section-title")
            yield Label("Project Name:", classes="field-label")
            yield Input(
                value=self.initial_config.project_name,
                placeholder="Zenith",
                id="project-name",
            )

            yield Label("Project Slug (Directory name):", classes="field-label")
            yield Input(
                value=self.initial_config.project_slug,
                placeholder="zenith",
                id="project-slug",
            )

            yield Label(
                "Python Package Name (Import identifier):",
                classes="field-label",
            )
            yield Input(
                value=self.initial_config.package_name,
                placeholder="zenith",
                id="package-name",
            )

            yield Label("Short Description:", classes="field-label")
            yield Input(
                value=self.initial_config.description,
                placeholder="Description...",
                id="description",
            )

            yield Label("Author Full Name:", classes="field-label")
            yield Input(value=self.initial_config.author_name, id="author-name")

            yield Label("Author Email:", classes="field-label")
            yield Input(value=self.initial_config.author_email, id="author-email")

            yield Label("GitHub Username or Organization:", classes="field-label")
            yield Input(
                value=self.initial_config.github_username,
                id="github-username",
            )

            yield Label("Runtime & Licensing", classes="section-title")
            python_options = [(v, v) for v in SUPPORTED_PYTHON_VERSIONS]
            yield Label("Target Python Version:", classes="field-label")
            yield Select(
                python_options,
                value=self.initial_config.python_version,
                id="python-version",
            )

            license_options = [(lic, lic) for lic in SUPPORTED_LICENSES]
            yield Label("Open Source License:", classes="field-label")
            yield Select(
                license_options,
                value=self.initial_config.license,
                id="license",
            )

            yield Label("Project Features", classes="section-title")
            with Vertical():
                yield Checkbox(
                    "Include Typer/Rich command-line interface",
                    value=self.initial_config.include_cli,
                    id="include-cli",
                )
                yield Checkbox(
                    "Generate GitHub Actions CI testing workflows",
                    value=self.initial_config.include_ci_testing,
                    id="include-ci-testing",
                )
                yield Checkbox(
                    "Generate GitHub Actions publishing workflows",
                    value=self.initial_config.include_ci_publishing,
                    id="include-ci-publishing",
                )
                yield Checkbox(
                    "Include Zenith agent skills suite (.agents/)",
                    value=self.initial_config.include_agent_skills,
                    id="include-agent-skills",
                )

            yield Label(
                "AI Assistant Integrations (npx skills style)",
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
                    tool_id in self.initial_config.ai_tools,
                )
                for tool_id in ALL_AI_TOOLS
            ]
            yield SelectionList[str](*selections, id="ai-tools-list")

            with Horizontal(classes="actions-bar"):
                yield Button(
                    "Scaffold Project",
                    id="submit-btn",
                    variant="success",
                )
                yield Button("Cancel", id="cancel-btn", variant="error")
        yield Footer()

    @on(Input.Changed, "#project-name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Synchronize slug and package name when project name is altered.

        Args:
            event: Input alteration event containing the updated value.

        """
        slug_input = self.query_one("#project-slug", Input)
        pkg_input = self.query_one("#package-name", Input)
        slug_input.value = slugify(event.value)
        pkg_input.value = slugify(event.value, separator="_")

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

    @on(Button.Pressed, "#submit-btn")
    def action_submit(self) -> None:
        """Collect form values, construct ZenithConfig, and exit successfully."""
        ai_list = self.query_one("#ai-tools-list", SelectionList)
        selected_tools = tuple(ai_list.selected)

        python_val = self.query_one("#python-version", Select).value
        license_val = self.query_one("#license", Select).value

        self.result = ZenithConfig(
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
            python_version=str(python_val),
            license=str(license_val),
            include_cli=self.query_one("#include-cli", Checkbox).value,
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
            ai_tools=selected_tools,
        )
        self.exit(self.result)

    @on(Button.Pressed, "#cancel-btn")
    def action_cancel(self) -> None:
        """Abort the wizard and exit without creating a project."""
        self.result = None
        self.exit(None)
