"""Input validation functions for Zenith project configuration."""

from __future__ import annotations

import contextlib
import keyword
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from zenith.models import ZenithConfig

PROJECT_SLUG_PATTERN: re.Pattern[str] = re.compile(r"^[-a-zA-Z0-9_]+$")
PACKAGE_NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z][_a-zA-Z0-9]*$")
EMAIL_PATTERN: re.Pattern[str] = re.compile(r"^[^\s@\"\\]+@[^\s@\"\\]+\.[^\s@\"\\]+$")
GITHUB_USERNAME_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$",
)

_FORBIDDEN_TOML_CHARS: tuple[str, ...] = ('"', "\\", "\n", "\r", "\x00")


def validate_output_dir(value: str) -> str | None:
    """Validate the target root directory path.

    Parameters
    ----------
    value : str
        Raw root directory input string. Empty values default to the current
        working directory.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    stripped = value.strip()
    if not stripped:
        return None
    if any(ch in stripped for ch in ("\n", "\r", "\x00")):
        return "Root directory cannot contain line breaks or null characters."
    path = Path(stripped).expanduser()
    with contextlib.suppress(OSError):
        if path.exists() and not path.is_dir():
            return "Root directory path points to an existing file, not a directory."
    return None


def validate_toml_text(value: str, field_label: str) -> str | None:
    """Validate a required single-line string interpolated into TOML files.

    Parameters
    ----------
    value : str
        Input string to validate.
    field_label : str
        Human-readable field label used in error messages.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    stripped = value.strip()
    if not stripped:
        return f"{field_label} cannot be empty."
    if any(ch in stripped for ch in _FORBIDDEN_TOML_CHARS):
        return (
            f'{field_label} cannot contain double quotes ("), '
            "backslashes (\\), or line breaks."
        )
    return None


def validate_project_name(value: str) -> str | None:
    """Validate the human-readable project name.

    Parameters
    ----------
    value : str
        Raw project name input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    return validate_toml_text(value, "Project name")


def validate_project_slug(value: str) -> str | None:
    """Validate the repository and directory slug.

    Parameters
    ----------
    value : str
        Raw project slug input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    stripped = value.strip()
    if not stripped:
        return "Project slug cannot be empty."
    if not PROJECT_SLUG_PATTERN.match(stripped):
        return (
            "Project slug can only contain letters, numbers, "
            "hyphens (-), and underscores (_)."
        )
    return None


def validate_package_name(value: str) -> str | None:
    """Validate the Python import package identifier.

    Parameters
    ----------
    value : str
        Raw package name input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    stripped = value.strip()
    if not stripped:
        return "Package name cannot be empty."
    if not PACKAGE_NAME_PATTERN.match(stripped):
        return (
            "Package name must start with a letter and contain only "
            "letters, numbers, and underscores (_)."
        )
    if keyword.iskeyword(stripped):
        return f"Package name '{stripped}' is a Python reserved keyword."
    return None


def validate_description(value: str) -> str | None:
    """Validate the short project description.

    Parameters
    ----------
    value : str
        Raw description input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    return validate_toml_text(value, "Description")


def validate_author_name(value: str) -> str | None:
    """Validate the author's full name.

    Parameters
    ----------
    value : str
        Raw author name input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    return validate_toml_text(value, "Author name")


def validate_author_email(value: str) -> str | None:
    """Validate the author's email address.

    Parameters
    ----------
    value : str
        Raw author email input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    stripped = value.strip()
    if not stripped:
        return "Author email cannot be empty."
    if any(ch in stripped for ch in ("\n", "\r", "\x00")) or not EMAIL_PATTERN.match(
        stripped
    ):
        return "Author email must be a valid email address (e.g. name@example.com)."
    return None


def validate_github_username(value: str) -> str | None:
    """Validate the GitHub username or organization name.

    Parameters
    ----------
    value : str
        Raw GitHub username input string.

    Returns
    -------
    str | None
        Error message if invalid, otherwise `None`.

    """
    stripped = value.strip()
    if not stripped:
        return "GitHub username cannot be empty."
    if not GITHUB_USERNAME_PATTERN.match(stripped):
        return (
            "GitHub username may only contain alphanumeric characters or "
            "single hyphens, up to 39 characters."
        )
    return None


def check_prerequisites() -> list[str]:
    """Check whether required external CLI tools are available on `PATH`.

    Returns
    -------
    list[str]
        List of missing tool names (e.g. `["uv", "git"]`).

    """
    return [tool for tool in ("uv", "git") if shutil.which(tool) is None]


def validate_config(config: ZenithConfig) -> list[tuple[str, str]]:
    """Validate all metadata fields of a `ZenithConfig` instance.

    Parameters
    ----------
    config : ZenithConfig
        Configuration instance to validate.

    Returns
    -------
    list[tuple[str, str]]
        List of `(field_name, error_message)` pairs for invalid fields.

    """
    checks: tuple[tuple[str, str, Callable[[str], str | None]], ...] = (
        ("output_dir", config.output_dir, validate_output_dir),
        ("project_name", config.project_name, validate_project_name),
        ("project_slug", config.project_slug, validate_project_slug),
        ("package_name", config.package_name, validate_package_name),
        ("description", config.description, validate_description),
        ("author_name", config.author_name, validate_author_name),
        ("author_email", config.author_email, validate_author_email),
        ("github_username", config.github_username, validate_github_username),
    )
    errors: list[tuple[str, str]] = []
    for field_name, value, validator in checks:
        error = validator(value)
        if error is not None:
            errors.append((field_name, error))
    return errors
