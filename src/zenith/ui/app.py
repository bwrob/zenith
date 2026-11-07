"""Textual application for interactive project setup."""

from __future__ import annotations

import textual


def get_version() -> str:
    """Return the textual library version.

    Returns:
        The installed version string of textual.

    """
    return str(textual.__version__)
