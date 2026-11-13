"""Textual application for interactive Zenith project setup."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from textual.app import App
from textual.binding import Binding, BindingType

from zenith.models import ZenithConfig
from zenith.ui.features_screen import FeaturesScreen
from zenith.ui.metadata_screen import MetadataScreen, format_target_preview
from zenith.ui.styles import ZENITH_CSS

if TYPE_CHECKING:
    from textual.screen import Screen

__all__ = [
    "FeaturesScreen",
    "MetadataScreen",
    "ZenithApp",
    "format_target_preview",
]


class ZenithApp(App[ZenithConfig | None]):
    """Interactive Textual TUI wizard for configuring Zenith projects."""

    TITLE = "Zenith Project Initializer"
    SUB_TITLE = "Modern Python 3.12+ Scaffolding"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel / Exit"),
    ]

    CSS = ZENITH_CSS

    def __init__(
        self,
        initial_config: ZenithConfig | None = None,
        *,
        overwrite: bool = False,
    ) -> None:
        """Initialize ZenithApp with default or provided configuration.

        Args:
            initial_config: Optional baseline configuration defaults.
            overwrite: Whether to allow overwriting a non-empty target directory.

        """
        super().__init__()
        self.initial_config = initial_config or ZenithConfig()
        self.config_state = self.initial_config
        self.overwrite = overwrite
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
