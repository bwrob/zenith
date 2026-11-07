"""Packaging and distribution invariant tests for zenith-template."""

from __future__ import annotations

import zipfile
from pathlib import Path

from zenith import __version__


def test_package_metadata() -> None:
    """Verify package version is defined."""
    assert __version__ == "0.2.0"


def test_wheel_contents() -> None:
    """Verify that built wheel contains template files and console scripts (REQ-001)."""
    dist_dir = Path("dist")
    wheels = list(dist_dir.glob("zenith_template-*.whl"))
    assert wheels, "No wheel found in dist/ directory"

    wheel_path = wheels[0]
    with zipfile.ZipFile(wheel_path) as z:
        names = z.namelist()
        assert "zenith/__init__.py" in names
        assert "zenith/cli.py" in names
        assert "zenith/template/cookiecutter.json" in names
        assert "zenith/template/hooks/post_gen_project.py" in names
        assert any(
            name.startswith("zenith/template/{{cookiecutter.project_slug}}")
            for name in names
        )

        entry_points = [n for n in names if "entry_points.txt" in n]
        assert entry_points
        ep_content = z.read(entry_points[0]).decode("utf-8")
        assert "zenith = zenith.cli:main" in ep_content
        assert "zenith-template = zenith.cli:main" in ep_content
