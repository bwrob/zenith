"""Transition benchmark modules between candidates.log and inspected.log."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

DEFAULT_SKILL_DIR = Path(__file__).resolve().parent.parent


def _read_lines(path: Path) -> list[str]:
    """Read non-empty stripped lines from a log file."""
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
    """Move a target module from candidates.log to inspected.log.

    Ensures the target module is recorded in inspected.log and removed from
    candidates.log within the skill directory without duplicate entries or
    blank lines.
    """
    clean_module = module.strip()
    if not clean_module:
        raise ValueError("Module name cannot be empty.")

    skill_dir.mkdir(parents=True, exist_ok=True)
    inspected_log = skill_dir / "inspected.log"
    candidates_log = skill_dir / "candidates.log"

    inspected = _read_lines(inspected_log)
    if clean_module not in inspected:
        inspected.append(clean_module)
        _write_lines(inspected_log, inspected)
        print(f"Recorded '{clean_module}' in {inspected_log}")
    else:
        print(f"'{clean_module}' was already recorded in {inspected_log}")

    if candidates_log.exists():
        candidates = _read_lines(candidates_log)
        if clean_module in candidates:
            updated_candidates = [c for c in candidates if c != clean_module]
            _write_lines(candidates_log, updated_candidates)
            print(f"Removed '{clean_module}' from {candidates_log}")


def requeue_module(module: str, skill_dir: Path = DEFAULT_SKILL_DIR) -> None:
    """Move a module from inspected.log back to candidates.log."""
    clean_module = module.strip()
    if not clean_module:
        raise ValueError("Module name cannot be empty.")

    skill_dir.mkdir(parents=True, exist_ok=True)
    inspected_log = skill_dir / "inspected.log"
    candidates_log = skill_dir / "candidates.log"

    candidates = _read_lines(candidates_log)
    if clean_module not in candidates:
        candidates.append(clean_module)
        _write_lines(candidates_log, candidates)
        print(f"Re-queued '{clean_module}' in {candidates_log}")

    if inspected_log.exists():
        inspected = _read_lines(inspected_log)
        if clean_module in inspected:
            updated_inspected = [m for m in inspected if m != clean_module]
            _write_lines(inspected_log, updated_inspected)
            print(f"Removed '{clean_module}' from {inspected_log}")


def requeue_all_modules(skill_dir: Path = DEFAULT_SKILL_DIR) -> None:
    """Move all modules from inspected.log back to candidates.log."""
    skill_dir.mkdir(parents=True, exist_ok=True)
    inspected_log = skill_dir / "inspected.log"
    candidates_log = skill_dir / "candidates.log"

    inspected = _read_lines(inspected_log)
    if not inspected:
        print("inspected.log is already empty.")
        return

    candidates = _read_lines(candidates_log)
    added_count = 0
    for mod in inspected:
        if mod not in candidates:
            candidates.append(mod)
            added_count += 1

    _write_lines(candidates_log, candidates)
    _write_lines(inspected_log, [])
    print(
        f"Moved {len(inspected)} module(s) from {inspected_log.name} back to "
        f"{candidates_log.name} ({added_count} newly appended)."
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for module transition."""
    parser = argparse.ArgumentParser(
        description="Transition benchmark modules between candidates.log and inspected.log."
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
        if args.requeue_all:
            requeue_all_modules()
        elif args.requeue:
            requeue_module(args.requeue)
        elif args.module and args.module.strip():
            transition_module(args.module)
        else:
            parser.print_help(sys.stderr)
            return 1
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
