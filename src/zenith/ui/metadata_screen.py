"""Screen 1 of the Zenith Textual setup wizard: metadata and licensing."""

from __future__ import annotations

import contextlib
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast, override

from textual import on
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.validation import ValidationResult, Validator
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Select,
)

from zenith.models import (
    SUPPORTED_LICENSES,
    SUPPORTED_PYTHON_VERSIONS,
    slugify,
)
from zenith.ui.features_screen import FeaturesScreen
from zenith.validation import (
    check_prerequisites,
    validate_author_email,
    validate_author_name,
    validate_description,
    validate_github_username,
    validate_output_dir,
    validate_package_name,
    validate_project_name,
    validate_project_slug,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult

    from zenith.ui.app import ZenithApp


class CallableValidator(Validator):
    """Textual Validator adapter wrapping a pure validation function."""

    def __init__(self, check: Callable[[str], str | None]) -> None:
        """Initialize the validator with a pure check callable.

        Args:
            check: Callable returning an error message string or `None` when valid.

        """
        super().__init__()
        self._check = check

    @override
    def validate(self, value: str) -> ValidationResult:
        """Validate `value` using the wrapped callable.

        Args:
            value: Field string value to validate.

        Returns:
            ValidationResult indicating success or failure with description.

        """
        error = self._check(value)
        if error is not None:
            return self.failure(error)
        return self.success()


METADATA_FIELD_VALIDATORS: dict[str, Callable[[str], str | None]] = {
    "output-dir": validate_output_dir,
    "project-name": validate_project_name,
    "project-slug": validate_project_slug,
    "package-name": validate_package_name,
    "description": validate_description,
    "author-name": validate_author_name,
    "author-email": validate_author_email,
    "github-username": validate_github_username,
}


def _first_error(result: ValidationResult | None) -> str | None:
    """Extract the first failure message from a Textual ValidationResult.

    Args:
        result: ValidationResult returned by a Textual Input, or `None`.

    Returns:
        First failure description string, or `None` when valid.

    """
    if result is None or result.is_valid:
        return None
    return next((str(desc) for desc in result.failure_descriptions), "Invalid value.")


def format_target_preview(output_dir: str, project_slug: str) -> tuple[str, bool]:
    """Compute the resolved destination path label and collision warning state.

    Args:
        output_dir: Root directory input string.
        project_slug: Project directory slug string.

    Returns:
        Tuple of `(formatted_label_text, has_collision_warning)`.

    """
    base_raw = output_dir.strip() or str(Path.cwd())
    slug_raw = project_slug.strip() or "my-project"
    target_path = (Path(base_raw).expanduser() / slug_raw).resolve()
    has_collision = False
    with contextlib.suppress(OSError):
        has_collision = target_path.is_dir() and any(target_path.iterdir())
    if has_collision:
        return (
            f"⚠ Target directory exists and is not empty: {target_path}",
            True,
        )
    return (f"✦ Target: {target_path}", False)


class MetadataScreen(Screen[object]):
    """Screen 1: Project Identity and Runtime Licensing."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+n", "next", "Next Step"),
    ]

    @override
    def compose(self) -> ComposeResult:
        """Compose the metadata configuration widgets.

        Yields:
            Widgets comprising the metadata configuration screen.

        """
        cfg = self.zenith_app.config_state
        missing_tools = check_prerequisites()
        prereq_msg = (
            f"⚠ Missing required tool(s) on PATH: {', '.join(missing_tools)}. "
            "Scaffolding will fail until installed."
            if missing_tools
            else ""
        )
        prereq_classes = "prereq-warning visible" if missing_tools else "prereq-warning"
        yield Header()
        with VerticalScroll():
            yield Label("Zenith Project Initializer", classes="brand-title")
            yield Label(
                "Step 1 of 2: Project Identity & Licensing",
                classes="brand-subtitle",
            )
            yield Label(prereq_msg, id="prereq-warning", classes=prereq_classes)

            yield Label("Root Directory:", classes="field-label")
            yield Input(
                value=cfg.output_dir,
                placeholder=str(Path.cwd()),
                validators=[CallableValidator(METADATA_FIELD_VALIDATORS["output-dir"])],
                id="output-dir",
            )
            yield Label("", id="output-dir-error", classes="field-error")

            yield Label("Project Name:", classes="field-label")
            yield Input(
                value=cfg.project_name,
                placeholder="My Project",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["project-name"])
                ],
                id="project-name",
            )
            yield Label("", id="project-name-error", classes="field-error")

            yield Label("Project Slug (Directory & PyPI name):", classes="field-label")
            yield Input(
                value=cfg.project_slug,
                placeholder="my-project",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["project-slug"])
                ],
                id="project-slug",
            )
            yield Label("", id="project-slug-error", classes="field-error")
            preview_text, is_warning = format_target_preview(
                cfg.output_dir,
                cfg.project_slug,
            )
            preview_classes = (
                "target-preview target-warning" if is_warning else "target-preview"
            )
            yield Label(preview_text, id="target-preview", classes=preview_classes)
            overwrite_classes = (
                "overwrite-checkbox visible" if is_warning else "overwrite-checkbox"
            )
            yield Checkbox(
                "Overwrite existing files in target directory",
                value=self.zenith_app.overwrite,
                id="overwrite-target",
                classes=overwrite_classes,
            )

            yield Label(
                "Python Package Name (Import identifier):",
                classes="field-label",
            )
            yield Input(
                value=cfg.package_name,
                placeholder="my_project",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["package-name"])
                ],
                id="package-name",
            )
            yield Label("", id="package-name-error", classes="field-error")

            yield Label("Short Description:", classes="field-label")
            yield Input(
                value=cfg.description,
                placeholder="A modern Python project...",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["description"])
                ],
                id="description",
            )
            yield Label("", id="description-error", classes="field-error")

            yield Label("Author Full Name:", classes="field-label")
            yield Input(
                value=cfg.author_name,
                placeholder="Author Name",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["author-name"])
                ],
                id="author-name",
            )
            yield Label("", id="author-name-error", classes="field-error")

            yield Label("Author Email:", classes="field-label")
            yield Input(
                value=cfg.author_email,
                placeholder="author@example.com",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["author-email"])
                ],
                id="author-email",
            )
            yield Label("", id="author-email-error", classes="field-error")

            yield Label(
                "GitHub Username or Organization:",
                classes="field-label",
            )
            yield Input(
                value=cfg.github_username,
                placeholder="username",
                validators=[
                    CallableValidator(METADATA_FIELD_VALIDATORS["github-username"])
                ],
                id="github-username",
            )
            yield Label("", id="github-username-error", classes="field-error")

            yield Label("Runtime & Licensing", classes="section-title")
            python_options = [(v, v) for v in SUPPORTED_PYTHON_VERSIONS]
            yield Label("Target Python Version:", classes="field-label")
            yield Select(
                python_options,
                value=cfg.python_version,
                allow_blank=False,
                id="python-version",
            )

            license_options = [(lic, lic) for lic in SUPPORTED_LICENSES]
            yield Label("Open Source License:", classes="field-label")
            yield Select(
                license_options,
                value=cfg.license,
                allow_blank=False,
                id="license",
            )

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

    def on_mount(self) -> None:
        """Initialize auto-sync tracking and validate initial field values."""
        cfg = self.zenith_app.config_state
        self._last_auto_slug: str = slugify(cfg.project_name)
        self._last_auto_pkg: str = slugify(cfg.project_name, separator="_")
        self._validate_all_fields(focus_first=False)

    def _set_field_error(self, input_id: str, error: str | None) -> None:
        """Update inline error label visibility and message for a field.

        Args:
            input_id: DOM ID of the validated Input widget.
            error: Error message string or `None` when valid.

        """
        error_label = self.query_one(f"#{input_id}-error", Label)
        error_label.update(error or "")
        error_label.set_class(error is not None, "visible")

    def _validate_all_fields(self, *, focus_first: bool = True) -> bool:
        """Validate all metadata inputs and update inline error indicators.

        Args:
            focus_first: Whether to focus the first invalid input widget.

        Returns:
            `True` when all metadata fields are valid, `False` otherwise.

        """
        first_invalid: Input | None = None
        for input_id in METADATA_FIELD_VALIDATORS:
            input_widget = self.query_one(f"#{input_id}", Input)
            error = _first_error(input_widget.validate(input_widget.value))
            self._set_field_error(input_id, error)
            if error is not None and first_invalid is None:
                first_invalid = input_widget

        if first_invalid is not None:
            if focus_first:
                first_invalid.focus()
                first_invalid.scroll_visible()
            return False
        return True

    @on(Input.Changed)
    def on_any_input_changed(self, event: Input.Changed) -> None:
        """Update inline validation error message when any input changes.

        Args:
            event: Input change event carrying the validation result.

        """
        input_id = event.input.id
        if input_id not in METADATA_FIELD_VALIDATORS:
            return
        self._set_field_error(input_id, _first_error(event.validation_result))

    @on(Input.Changed, "#project-name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Synchronize non-customized slug and package name with project name.

        Args:
            event: Input change event with updated string.

        """
        new_slug = slugify(event.value)
        new_pkg = slugify(event.value, separator="_")
        slug_input = self.query_one("#project-slug", Input)
        pkg_input = self.query_one("#package-name", Input)
        if slug_input.value == self._last_auto_slug:
            slug_input.value = new_slug
        if pkg_input.value == self._last_auto_pkg:
            pkg_input.value = new_pkg
        self._last_auto_slug = new_slug
        self._last_auto_pkg = new_pkg

    @on(Input.Changed, "#output-dir, #project-slug")
    def on_target_inputs_changed(self) -> None:
        """Update the live destination preview and collision warning label."""
        out_val = self.query_one("#output-dir", Input).value
        slug_val = self.query_one("#project-slug", Input).value
        preview_text, is_warning = format_target_preview(out_val, slug_val)
        preview_label = self.query_one("#target-preview", Label)
        preview_label.update(preview_text)
        preview_label.set_class(is_warning, "target-warning")
        overwrite_box = self.query_one("#overwrite-target", Checkbox)
        overwrite_box.set_class(is_warning, "visible")

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Advance focus on Enter, or proceed to Step 2 from the last input.

        Args:
            event: Input submission event triggered by pressing Enter.

        """
        if event.input.id == "github-username":
            self.action_next()
            return
        self.focus_next()

    @on(Button.Pressed, "#next-btn")
    def action_next(self) -> None:
        """Validate Screen 1 fields and navigate to Screen 2 when valid."""
        if not self._validate_all_fields(focus_first=True):
            return
        out_dir = self.query_one("#output-dir", Input).value.strip() or str(Path.cwd())
        slug_val = self.query_one("#project-slug", Input).value.strip()
        _, has_collision = format_target_preview(out_dir, slug_val)
        overwrite_checked = self.query_one("#overwrite-target", Checkbox).value
        if has_collision and not overwrite_checked:
            self._set_field_error(
                "project-slug",
                "Target directory is not empty. "
                "Change slug/directory or enable overwrite.",
            )
            overwrite_box = self.query_one("#overwrite-target", Checkbox)
            overwrite_box.focus()
            overwrite_box.scroll_visible()
            return
        self.zenith_app.overwrite = overwrite_checked
        py_val = str(self.query_one("#python-version", Select).value)
        lic_val = str(self.query_one("#license", Select).value)
        self.zenith_app.config_state = replace(
            self.zenith_app.config_state,
            output_dir=out_dir,
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
