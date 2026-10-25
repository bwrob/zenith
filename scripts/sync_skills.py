"""Synchronize repository agent skills with template skills as relative symlinks.

The template skills directory (`{{cookiecutter.project_slug}}/.agents/skills/`)
serves as the canonical single source of truth. This script ensures every shared
skill in `.agents/skills/` is a relative symlink pointing directly to its template
counterpart.

Repository-specific skills that only exist in ``.agents/skills/`` (e.g.
``workflow-inspect-repo``, ``tool-cookiecutter``, ``workflow-update-tools``,
and ``workflow-example-sync``) are preserved untouched.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from rich.console import Console

console = Console(highlight=False)
error_console = Console(stderr=True, highlight=False)

DEFAULT_SOURCE = Path("{{cookiecutter.project_slug}}/.agents/skills")
DEFAULT_TARGET = Path(".agents/skills")


def _handle_symlink(
    tgt_skill: Path, rel_target: str, skill_name: str, *, check_only: bool
) -> str | None:
    """Handle an existing symlink in the target directory.

    Args:
        tgt_skill: Existing symlink path.
        rel_target: Expected relative symlink target.
        skill_name: Display name of the skill.
        check_only: Whether to report drift instead of repairing it.

    Returns:
        None when the symlink is correct, an error message on drift, or an
        empty string when the symlink was replaced.

    """
    current_target = tgt_skill.readlink().as_posix()
    if current_target == rel_target:
        return None
    if check_only:
        return (
            f"{skill_name}: symlink points to '{current_target}', "
            f"expected '{rel_target}'"
        )
    tgt_skill.unlink()
    return ""


def _handle_existing(
    tgt_skill: Path, rel_target: str, skill_name: str, *, check_only: bool
) -> str | None:
    """Handle an existing non-symlink path in the target directory.

    Args:
        tgt_skill: Existing regular file or directory.
        rel_target: Expected relative symlink target.
        skill_name: Display name of the skill.
        check_only: Whether to report drift instead of repairing it.

    Returns:
        An error message in check mode, otherwise an empty string after
        removal.

    """
    if check_only:
        return (
            f"{skill_name}: expected symlink to '{rel_target}', "
            "but found directory/file"
        )
    if tgt_skill.is_dir():
        shutil.rmtree(tgt_skill)
    else:
        tgt_skill.unlink()
    return ""


def _sync_skill(
    src_skill: Path,
    target_dir: Path,
    tgt_resolved: Path,
    *,
    check_only: bool,
) -> str | None:
    """Synchronize one skill directory into the target as a relative symlink.

    Args:
        src_skill: Canonical skill directory.
        target_dir: Target skills directory.
        tgt_resolved: Resolved target directory for relative links.
        check_only: Whether to report drift instead of repairing it.

    Returns:
        None on success, an error message on drift, or an empty string
        when repaired.

    """
    skill_name = src_skill.name
    tgt_skill = target_dir / skill_name
    rel_target = os.path.relpath(src_skill, tgt_resolved)

    if tgt_skill.is_symlink():
        res = _handle_symlink(tgt_skill, rel_target, skill_name, check_only=check_only)
        if res is None or check_only:
            return res
    elif tgt_skill.exists():
        res = _handle_existing(tgt_skill, rel_target, skill_name, check_only=check_only)
        if check_only:
            return res
    elif check_only:
        return f"{skill_name}: missing symlink in {target_dir}"

    tgt_skill.symlink_to(rel_target)
    return None


def sync_skills(
    source_dir: Path,
    target_dir: Path,
    *,
    check_only: bool = False,
) -> list[str]:
    """Ensure skills in target_dir are relative symlinks to source_dir.

    Args:
        source_dir: Canonical template skills directory.
        target_dir: Repository skills directory to verify or repair.
        check_only: Whether to only report drift.

    Returns:
        A list of drift or failure messages; empty when synchronized.

    """
    errors: list[str] = []

    src_resolved = source_dir.resolve()
    tgt_resolved = target_dir.resolve()

    if not src_resolved.is_dir():
        return [f"Source directory not found: {source_dir}"]
    if not tgt_resolved.is_dir():
        return [f"Target directory not found: {target_dir}"]

    source_skills = sorted(
        [d for d in src_resolved.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    for src_skill in source_skills:
        err = _sync_skill(src_skill, target_dir, tgt_resolved, check_only=check_only)
        if err:
            errors.append(err)

    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for skill synchronization.

    Args:
        argv: Command-line arguments; defaults to ``sys.argv`` when None.

    Returns:
        Process exit code: 0 on success, 1 on failure.

    """
    parser = argparse.ArgumentParser(
        description=("Synchronize repository skills with template skills via symlinks.")
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to source template skills directory.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Path to target repository skills directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify symlinks without modifying disk; exit non-zero if drift is found.",
    )

    args = parser.parse_args(argv)

    action_label = "Checking" if args.check else "Synchronizing"
    console.print(
        f"[bold cyan]🔄 {action_label} skills: {args.target} -> {args.source}...[/]"
    )

    errors = sync_skills(args.source, args.target, check_only=args.check)

    if errors:
        prefix = "❌ Verification failed" if args.check else "❌ Synchronization failed"
        error_console.print(f"\n[bold red]{prefix}:[/]")
        for err in errors:
            error_console.print(f"  [red]✗ {err}[/]")
        return 1

    success_label = (
        "All skills properly symlinked to template source of truth!"
        if args.check
        else "Successfully synchronized all skills with template source of truth!"
    )
    console.print(f"[bold green]✅ {success_label}[/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
