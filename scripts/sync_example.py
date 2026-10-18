"""Synchronize the zenith-example showcase repository with the instantiated template."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cookiecutter.main import cookiecutter

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

SHOWCASE_CONTEXT: dict[str, Any] = {
    "project_name": "Zenith Example",
    "project_slug": "zenith-example",
    "package_name": "zenith_example",
    "description": "Demonstration and showcase repository instantiated from the Zenith template.",
    "author_name": "bwrob",
    "author_email": "contact@bwrob.dev",
    "github_username": "bwrob",
    "version": "0.1.0",
    "python_version": "3.13",
    "license": "MIT",
    "include_cli": True,
    "include_ci_testing": True,
    "include_ci_publishing": True,
}


def sync_example(target_dir: Path, *, lock: bool = True) -> Path:
    """Render the Zenith template into target_dir, preserving its .git directory."""
    resolved_target = target_dir.resolve()
    resolved_target.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Scaffolding Zenith showcase into temporary staging: {tmpdir}")
        rendered_path = Path(
            cookiecutter(
                str(TEMPLATE_ROOT),
                no_input=True,
                output_dir=tmpdir,
                extra_context=SHOWCASE_CONTEXT,
            )
        )

        print(f"Synchronizing rendered files to target: {resolved_target}")
        # Remove old files in target except .git
        for item in resolved_target.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        # Copy new files from rendered project into target
        for item in rendered_path.iterdir():
            if item.name == ".git":
                continue
            dest = resolved_target / item.name
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest, follow_symlinks=False)

    sub_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}

    if lock:
        print(f"Generating uv.lock in {resolved_target}...")
        subprocess.run(["uv", "lock"], cwd=resolved_target, env=sub_env, check=True)

    print(f"Formatting rendered files in {resolved_target}...")
    subprocess.run(
        ["uv", "run", "poe", "fix"], cwd=resolved_target, env=sub_env, check=True
    )

    print(f"Showcase successfully synchronized at: {resolved_target}")
    return resolved_target


def main() -> None:
    """Parse arguments and execute template synchronization."""
    parser = argparse.ArgumentParser(
        description="Sync Zenith template showcase repository with instantiated template."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=Path("../zenith-example"),
        type=Path,
        help="Target directory for the showcase repo (defaults to ../zenith-example)",
    )
    parser.add_argument(
        "--no-lock",
        action="store_true",
        help="Skip generating uv.lock in target repository.",
    )
    args = parser.parse_args()
    sync_example(args.target, lock=not args.no_lock)


if __name__ == "__main__":
    main()
