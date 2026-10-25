"""Repository-wide lint-contract tests.

Encoding hard-won policy invariants as tests: suppression directives must use
the Ruff ignore form (never noqa), and the root and template Ruff ignore
lists must never drift apart.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "{{cookiecutter.project_slug}}"


def _python_files() -> list[Path]:
    """Collect every Python file subject to the repo lint contract.

    Returns:
        All tracked-ish ``.py`` files under the repo root, the hooks and
        scripts trees, and the Jinja template tree (excluding virtualenvs,
        caches, and the rendered-project sandbox directories).

    """
    scan_roots = (
        REPO_ROOT,
        REPO_ROOT / "hooks",
        REPO_ROOT / "scripts",
        REPO_ROOT / "tests",
        REPO_ROOT / "{{cookiecutter.project_slug}}",
    )
    skip_parts = {".venv", ".temp", ".ruff_cache", "__pycache__", "site", "dist"}
    files: list[Path] = []
    for root in scan_roots:
        for path in root.rglob("*.py"):
            if not skip_parts.isdisjoint(path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def test_no_noqa_directives_anywhere() -> None:
    """Reach every Python file with a ruff ignore directive, never a noqa.

    The replacement directive was introduced after the noqa ban; this scan
    prevents any regressions to the legacy comment style.
    """
    offenders: list[str] = []
    this_file = Path(__file__).resolve()
    for path in _python_files():
        if not path.is_file() or path.resolve() == this_file:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if "# noqa" in line:
                offenders.append(f"{path}:{number}")
    assert not offenders


def test_no_noqa_directives_detects_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that legacy noqa comments are detected and reported."""
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("x = 1  # noqa: E501\n", encoding="utf-8")
    monkeypatch.setattr("tests.test_repo_conventions._python_files", lambda: [bad_file])
    with pytest.raises(AssertionError):
        test_no_noqa_directives_anywhere()


def test_no_noqa_skips_non_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that non-file paths in scan roots are safely skipped."""
    non_file = tmp_path / "dir.py"
    non_file.mkdir()
    monkeypatch.setattr("tests.test_repo_conventions._python_files", lambda: [non_file])
    test_no_noqa_directives_anywhere()


def _ignore_list(config_path: Path) -> list[str]:
    """Read the Ruff global ignore list from a ruff.toml configuration file.

    Args:
        config_path: Path of the ruff.toml to parse.

    Returns:
        The configured ``lint.ignore`` list.

    """
    text = config_path.read_text(encoding="utf-8")
    config = tomllib.loads(text)
    return config["lint"]["ignore"]


def test_root_and_template_ignore_lists_match() -> None:
    """Hold root and template global Ruff ignore lists to exact parity.

    The rule lists were unified after surviving two divergent policies; this
    census fails on the first rule that flips on only one side, so drift is
    visible in tests instead of in surprise render-lint failures.
    """
    assert _ignore_list(REPO_ROOT / "ruff.toml") == _ignore_list(
        TEMPLATE_ROOT / "ruff.toml"
    )
