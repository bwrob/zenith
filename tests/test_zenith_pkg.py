"""Packaging and distribution invariant tests for zenith-template."""

from __future__ import annotations

import subprocess
import zipfile
from typing import TYPE_CHECKING

from zenith import __version__

if TYPE_CHECKING:
    from pathlib import Path


def test_package_metadata() -> None:
    """Verify package version is defined."""
    assert __version__ == "0.2.0"


def test_wheel_contents(tmp_path: Path) -> None:
    """Verify that built wheel contains template files and console scripts (REQ-001)."""
    subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] -- fixed uv build argument list
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],  # ruff: ignore[start-process-with-partial-path] -- uv resolved on standard PATH
        check=True,
        capture_output=True,
    )
    wheels = list(tmp_path.glob("zenith_template-*.whl"))
    assert wheels, "No wheel found in output directory"

    wheel_path = wheels[0]
    with zipfile.ZipFile(wheel_path) as z:
        names = z.namelist()
        assert "zenith/__init__.py" in names
        assert "zenith/cli.py" in names
        assert "zenith/template/cookiecutter.json" in names
        assert "zenith/template/hooks/post_gen_project.py" in names
        assert "zenith/template/templates/licenses/_mit.txt" in names
        assert any(
            name.startswith("zenith/template/{{cookiecutter.project_slug}}")
            for name in names
        )

        entry_points = [n for n in names if "entry_points.txt" in n]
        assert entry_points
        ep_content = z.read(entry_points[0]).decode("utf-8")
        assert "zenith = zenith.cli:main" in ep_content
        assert "zenith-template = zenith.cli:main" in ep_content
