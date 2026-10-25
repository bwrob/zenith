"""Pre-generation hook: validate project slug and package name viability."""

from __future__ import annotations

import keyword
import re
import sys

from rich.console import Console

error_console = Console(stderr=True, highlight=False)

PACKAGE_REGEX = r"^[a-zA-Z][_a-zA-Z0-9]*$"
package_name = "{{ cookiecutter.package_name }}"

if not re.match(PACKAGE_REGEX, package_name) or keyword.iskeyword(package_name):
    error_console.print(
        f"[bold red]ERROR:[/] The package name '{package_name}' is not a "
        "valid Python package name. "
        "It must start with a letter, contain only alphanumeric characters "
        "and underscores, "
        "and must not be a Python reserved keyword."
    )
    sys.exit(1)

PROJECT_SLUG_REGEX = r"^[-a-zA-Z0-9_]+$"
project_slug = "{{ cookiecutter.project_slug }}"

if not re.match(PROJECT_SLUG_REGEX, project_slug):
    error_console.print(
        f"[bold red]ERROR:[/] The project slug '{project_slug}' is invalid. "
        "It can only contain alphanumeric characters, dashes, and underscores."
    )
    sys.exit(1)
