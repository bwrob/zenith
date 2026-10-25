# Standalone maintenance script; the scripts directory is not a package.
"""Render template variants and audit each rendered project with ruff.

Renders the cookiecutter template into the sandboxed .temp directory with the
combinations most likely to expose render-dependent lint drift (CLI on/off,
short and long project slugs), then runs `ruff check` and
`ruff format --check` from *inside* each rendered project so that its own
ruff.toml and relative per-file-ignores apply exactly as they do in
generated-project CI.
"""

from __future__ import annotations

import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from cookiecutter.main import cookiecutter
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Generator

console = Console(highlight=False)
error_console = Console(stderr=True, highlight=False)

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
RENDER_ROOT = TEMPLATE_ROOT / ".temp" / "rendered-lint"

VARIANTS: tuple[tuple[str, dict[str, str]], ...] = (
    (
        "cli-on",
        {
            "project_name": "Demo Lint",
            "python_version": "3.13",
            "include_cli": "true",
        },
    ),
    (
        "cli-off",
        {
            "project_name": "Demo Lint",
            "python_version": "3.13",
            "include_cli": "false",
        },
    ),
    (
        "long-slug",
        {
            "project_name": "Some Really Extremely Long Demo Project Name",
            "python_version": "3.13",
            "include_cli": "false",
        },
    ),
)

RUFF_CHECK_ARGS = ("ruff", "check", ".")
RUFF_FORMAT_ARGS = ("ruff", "format", "--check", ".")


def single_project_dir(output_dir: Path) -> Path:
    """Return the sole rendered project directory inside an output directory.

    Args:
        output_dir: Cookiecutter output directory for one variant.

    Returns:
        Path of the rendered project directory.

    Raises:
        RuntimeError: If the render produced no project directory.

    """
    entries = [p for p in output_dir.iterdir() if p.is_dir()]
    if not entries:
        msg = f"Render '{output_dir}' produced no project directory."
        raise RuntimeError(msg)
    return entries[0]


@contextmanager
def render_variants() -> Generator[list[Path], None, None]:
    """Render every configured template variant into a fresh scratch root.

    Yields:
        Path of the rendered project root of each variant, in order.

    """
    shutil.rmtree(RENDER_ROOT, ignore_errors=True)
    RENDER_ROOT.mkdir(parents=True, exist_ok=True)
    project_dirs: list[Path] = []
    try:
        for variant_name, context in VARIANTS:
            output_dir = RENDER_ROOT / variant_name
            shutil.rmtree(output_dir, ignore_errors=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            cookiecutter(
                str(TEMPLATE_ROOT),
                no_input=True,
                extra_context=context,
                output_dir=str(output_dir),
                overwrite_if_exists=True,
            )
            rendered = single_project_dir(output_dir)
            project_dirs.append(rendered)
        yield project_dirs
    finally:
        shutil.rmtree(RENDER_ROOT, ignore_errors=True)


def find_uv() -> str:
    """Locate the `uv` executable or fail with a diagnostic.

    Returns:
        Absolute path to the uv executable.

    Raises:
        RuntimeError: If uv is not on PATH.

    """
    uv_bin = shutil.which("uv")
    if uv_bin is None:
        msg = "uv executable not found on PATH"
        raise RuntimeError(msg)
    return uv_bin


def run_in_dir(uv_bin: str, project_dir: Path) -> list[str]:
    """Execute both ruff gates inside a rendered project directory.

    Args:
        uv_bin: Resolved uv executable path.
        project_dir: Rendered project root used as the invocation cwd.

    Returns:
        Diagnostic string for every gate that reported a violation; empty
        when the project is clean.

    """
    errors: list[str] = []
    for label, args in (
        ("check", RUFF_CHECK_ARGS),
        ("format", RUFF_FORMAT_ARGS),
    ):
        gate = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
            # Repo-owned tooling invoked through uv on repo-controlled paths.
            [uv_bin, "run", *args],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if gate.returncode != 0:
            errors.append(f"{label}: {gate.stdout.strip() or gate.stderr.strip()}")
    return errors


def audit_variants(uv_bin: str) -> list[tuple[str, list[str]]]:
    """Render every variant and record the ruff-gate failures of each.

    Args:
        uv_bin: Resolved uv executable path used for both ruff gates.

    Returns:
        Tuple of rendered-variant names with their failure diagnostics
        (empty list when the variant is clean).

    """
    audit_results: list[tuple[str, list[str]]] = []
    with render_variants() as project_dirs:
        for project_dir in project_dirs:
            console.print(f"[bold cyan]Auditing {project_dir}...[/]")
            failures = run_in_dir(uv_bin, project_dir)
            for failure in failures:
                error_console.print(f"[red]✗ {failure}[/]")
            audit_results.append((project_dir.name, failures))
    return audit_results


def audit_rendered() -> int:
    """Render and audit every configured template variant in place.

    Returns:
        Process exit code: 0 when every rendered project is clean, 1 when any
        gate fails or an environment/render error occurs.

    """
    try:
        uv_bin = find_uv()
        audit_results = audit_variants(uv_bin)
    except (RuntimeError, subprocess.SubprocessError, OSError) as exc:
        error_console.print(f"[bold red]ERROR:[/] {exc}")
        return 1
    if any(failures for _, failures in audit_results):
        error_console.print("[bold red]❌ Rendered-project lint audit failed.[/]")
        return 1
    console.print("[bold green]✅ All rendered projects lint clean.[/]")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit_rendered())
