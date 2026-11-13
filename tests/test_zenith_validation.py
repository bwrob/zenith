"""Unit tests for Zenith input validation functions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from zenith.models import ZenithConfig
from zenith.validation import (
    check_prerequisites,
    validate_author_email,
    validate_author_name,
    validate_config,
    validate_description,
    validate_github_username,
    validate_output_dir,
    validate_package_name,
    validate_project_name,
    validate_project_slug,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_validate_output_dir(tmp_path: Path) -> None:
    """Verify root directory validation accepts dirs and rejects files or nulls."""
    assert validate_output_dir("") is None
    assert validate_output_dir("   ") is None
    assert validate_output_dir(str(tmp_path)) is None
    assert validate_output_dir(str(tmp_path / "does-not-exist")) is None

    file_path = tmp_path / "existing.txt"
    file_path.write_text("data", encoding="utf-8")
    assert validate_output_dir(str(file_path)) is not None
    assert validate_output_dir(str(tmp_path / "bad\x00dir")) is not None
    assert validate_output_dir(str(tmp_path / "bad\ndir")) is not None


@pytest.mark.parametrize(
    ("validator", "valid_value"),
    [
        (validate_project_name, "Zenith App"),
        (validate_description, "A modern Python project."),
        (validate_author_name, "Ada Lovelace"),
    ],
)
def test_validate_toml_text_fields_valid(
    validator: object,
    valid_value: str,
) -> None:
    """Verify TOML text validators accept valid single-line strings."""
    assert callable(validator)
    assert validator(valid_value) is None


@pytest.mark.parametrize(
    "invalid_value",
    ["", "   ", 'has "quote"', "has\\slash", "line1\nline2", "null\x00byte"],
)
def test_validate_toml_text_fields_invalid(invalid_value: str) -> None:
    """Verify TOML text validators reject empty, quoted, slashed, and multiline text."""
    assert validate_project_name(invalid_value) is not None
    assert validate_description(invalid_value) is not None
    assert validate_author_name(invalid_value) is not None


@pytest.mark.parametrize(
    "valid_slug",
    ["my-project", "my_project", "zenith2026", "A-B_C"],
)
def test_validate_project_slug_valid(valid_slug: str) -> None:
    """Verify project slug validator accepts alphanumeric, dashes, and underscores."""
    assert validate_project_slug(valid_slug) is None


@pytest.mark.parametrize(
    "invalid_slug",
    ["", "   ", "my.project", ".", "..", "my project", "my/project"],
)
def test_validate_project_slug_invalid(invalid_slug: str) -> None:
    """Verify project slug validator rejects dots, spaces, slashes, and empty values."""
    assert validate_project_slug(invalid_slug) is not None


@pytest.mark.parametrize(
    "valid_pkg",
    ["my_package", "zenith", "a1", "Pkg_Name"],
)
def test_validate_package_name_valid(valid_pkg: str) -> None:
    """Verify package name validator accepts valid Python identifiers."""
    assert validate_package_name(valid_pkg) is None


@pytest.mark.parametrize(
    "invalid_pkg",
    ["", "   ", "my.package", "my-package", "123app", "_private", "class", "import"],
)
def test_validate_package_name_invalid(invalid_pkg: str) -> None:
    """Verify package name validator rejects dots, hyphens, digits, and keywords."""
    assert validate_package_name(invalid_pkg) is not None


@pytest.mark.parametrize(
    "valid_email",
    ["author@example.com", "ada.lovelace+dev@sub.domain.org"],
)
def test_validate_author_email_valid(valid_email: str) -> None:
    """Verify author email validator accepts well-formed email addresses."""
    assert validate_author_email(valid_email) is None


@pytest.mark.parametrize(
    "invalid_email",
    ["", "   ", "not-an-email", "user@localhost", "a b@example.com", "a@b\n.c"],
)
def test_validate_author_email_invalid(invalid_email: str) -> None:
    """Verify author email validator rejects malformed or empty email addresses."""
    assert validate_author_email(invalid_email) is not None


@pytest.mark.parametrize(
    "valid_user",
    ["bwrob", "my-org", "a", "user123"],
)
def test_validate_github_username_valid(valid_user: str) -> None:
    """Verify GitHub username validator accepts valid usernames and orgs."""
    assert validate_github_username(valid_user) is None


@pytest.mark.parametrize(
    "invalid_user",
    ["", "   ", "my.org", "-leading", "trailing-", "double--hyphen", "a" * 40],
)
def test_validate_github_username_invalid(invalid_user: str) -> None:
    """Verify GitHub username validator rejects dots, bad hyphens, and >39 chars."""
    assert validate_github_username(invalid_user) is not None


def test_check_prerequisites() -> None:
    """Verify check_prerequisites reports missing uv or git binaries."""

    def _missing_uv(name: str) -> str | None:
        return None if name == "uv" else "/usr/bin/git"

    with patch("zenith.validation.shutil.which", return_value="/usr/bin/tool"):
        assert check_prerequisites() == []

    with patch("zenith.validation.shutil.which", side_effect=_missing_uv):
        assert check_prerequisites() == ["uv"]


def test_validate_config() -> None:
    """Verify validate_config validates all ZenithConfig metadata fields."""
    assert validate_config(ZenithConfig()) == []

    bad = ZenithConfig(project_slug="my.app", author_email="bad-email")
    errors = dict(validate_config(bad))
    assert set(errors) == {"project_slug", "author_email"}
