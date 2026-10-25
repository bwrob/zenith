"""Pre-prompt validation hook executed before any questions are asked.

Validates that system prerequisites (Python version, uv, and git) are installed.
"""

from __future__ import annotations

import shutil
import sys

from rich.console import Console

error_console = Console(stderr=True, highlight=False)

MIN_PYTHON_VERSION = (3, 12)


def main() -> None:
    """Abort generation when required tooling (Python, uv, git) is missing."""
    if sys.version_info < MIN_PYTHON_VERSION:
        version_str = f"{sys.version_info.major}.{sys.version_info.minor}"
        error_console.print(
            "[bold red]ERROR:[/] Zenith requires Python "
            f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ "
            f"to generate projects. Current version: {version_str}",
        )
        sys.exit(1)

    if shutil.which("uv") is None:
        error_console.print(
            "[bold red]ERROR:[/] Zenith projects require 'uv' for "
            "dependency management and builds.\n"
            "Please install uv before continuing: "
            "https://docs.astral.sh/uv/getting-started/installation/",
        )
        sys.exit(1)

    if shutil.which("git") is None:
        error_console.print(
            "[bold red]ERROR:[/] Zenith projects require 'git' to be "
            "installed and available in PATH.",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
