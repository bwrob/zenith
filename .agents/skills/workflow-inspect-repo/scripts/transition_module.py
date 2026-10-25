# ruff: ignore[implicit-namespace-package]
# Standalone maintenance script; the scripts directory is not a package.
"""Transition benchmark modules between candidates.log and inspected.log."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_SKILL_DIR = Path(__file__).resolve().parent.parent

console = Console(highlight=False)
error_console = Console(stderr=True, highlight=False)


def _read_lines(path: Path) -> list[str]:
    """Read non-empty stripped lines from a log file.

    Args:
        path: Log file path. Missing files read as empty.

    Returns:
        Stripped, non-empty lines in file order.

    """
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_lines(path: Path, lines: Sequence[str]) -> None:
    """Write lines to a log file with trailing newline."""
    content = "\n".join(lines) + "\n" if lines else ""
    path.write_text(content, encoding="utf-8")


def transition_module(module: str, skill_dir: Path = DEFAULT_SKILL_DIR) -> None:
    """Record a target module in inspected.log.

    Ensures the target module is recorded in inspected.log and removed from
    candidates.log within the skill directory without duplicate entries or
    blank lines.

    Args:
        module: Module name from candidates.log.
        skill_dir: Skill directory holding both logs.

    Raises:
        ValueError: If the module name is empty.

    """
    clean_module = module.strip()
    if not clean_module:
        msg = "Module name cannot be empty."
        raise ValueError(msg)

    skill_dir.mkdir(parents=True, exist_ok=True)
    inspected_log = skill_dir / "inspected.log"
    candidates_log = skill_dir / "candidates.log"

    inspected = _read_lines(inspected_log)
    if clean_module not in inspected:
        inspected.append(clean_module)
        _write_lines(inspected_log, inspected)
        console.print(f"Recorded '{clean_module}' in {inspected_log}")
    else:
        console.print(f"'{clean_module}' was already recorded in {inspected_log}")

    if candidates_log.exists():
        candidates = _read_lines(candidates_log)
        if clean_module in candidates:
            updated_candidates = [m for m in candidates if m != clean_module]
            _write_lines(candidates_log, updated_candidates)
            console.print(f"Removed '{clean_module}' from {candidates_log}")


def requeue_module(module: str, skill_dir: Path = DEFAULT_SKILL_DIR) -> None:
    """Move a module from inspected.log back to candidates.log.

    Args:
        module: Module name to requeue.
        skill_dir: Skill directory holding both logs.

    Raises:
        ValueError: If the module name is empty.

    """
    clean_module = module.strip()
    if not clean_module:
        msg = "Module name cannot be empty."
        raise ValueError(msg)

    skill_dir.mkdir(parents=True, exist_ok=True)
    inspected_log = skill_dir / "inspected.log"
    candidates_log = skill_dir / "candidates.log"

    candidates = _read_lines(candidates_log)
    if clean_module not in candidates:
        candidates.append(clean_module)
        _write_lines(candidates_log, candidates)
        console.print(f"Re-queued '{clean_module}' in {candidates_log}")

    if inspected_log.exists():
        inspected = _read_lines(inspected_log)
        if clean_module in inspected:
            updated_inspected = [m for m in inspected if m != clean_module]
            _write_lines(inspected_log, updated_inspected)
            console.print(f"Removed '{clean_module}' from {inspected_log}")


def requeue_all_modules(skill_dir: Path = DEFAULT_SKILL_DIR) -> None:
    """Move all modules from inspected.log back to candidates.log.

    Args:
        skill_dir: Skill directory holding both logs.

    """
    skill_dir.mkdir(parents=True, exist_ok=True)
    inspected_log = skill_dir / "inspected.log"
    candidates_log = skill_dir / "candidates.log"

    inspected = _read_lines(inspected_log)
    if not inspected:
        console.print("inspected.log is already empty.")
        return

    existing = set(_read_lines(candidates_log))
    candidates = _read_lines(candidates_log)
    seen = set(existing)
    added_count = 0
    for mod in inspected:
        if mod not in seen:
            candidates.append(mod)
            seen.add(mod)
            added_count += 1

    _write_lines(candidates_log, candidates)
    _write_lines(inspected_log, [])
    console.print(
        f"Moved {len(inspected)} module(s) from {inspected_log.name} back to "
        f"{candidates_log.name} ({added_count} newly appended)."
    )


def _run_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """Run the transition mode selected by parsed CLI arguments.

    Args:
        args: Parsed arguments from the CLI parser.
        parser: Parser used to print help when no mode matches.

    Returns:
        Process exit code: 0 on success, 1 when no mode was selected.

    """
    if args.requeue_all:
        requeue_all_modules()
    elif args.requeue:
        requeue_module(args.requeue)
    elif args.module and args.module.strip():
        transition_module(args.module)
    else:
        parser.print_help(sys.stderr)
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for module transition.

    Args:
        argv: Optional argument vector override for tests.

    Returns:
        Process exit code.

    """
    parser = argparse.ArgumentParser(
        description=(
            "Transition benchmark modules between candidates.log and inspected.log."
        )
    )
    parser.add_argument(
        "module",
        nargs="?",
        help="Module name to transition from candidates.log to inspected.log",
    )
    parser.add_argument(
        "--requeue",
        "-r",
        metavar="MODULE",
        help="Move a specific module from inspected.log back to candidates.log",
    )
    parser.add_argument(
        "--requeue-all",
        action="store_true",
        help="Move all modules from inspected.log back to candidates.log",
    )
    args = parser.parse_args(argv)

    try:
        return _run_mode(args, parser)
    except (ValueError, OSError) as exc:
        error_console.print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
