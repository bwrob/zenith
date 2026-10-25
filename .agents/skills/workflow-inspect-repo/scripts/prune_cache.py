# ruff: ignore[implicit-namespace-package]
# Standalone root-only skill script; not part of an installed package.
"""Cache cleanup and disk budgeting manager for benchmark clones."""

from __future__ import annotations

import argparse
import contextlib
import math
import operator
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

console = Console(highlight=False, markup=False, emoji=False, soft_wrap=True)
error_console = Console(
    stderr=True, highlight=False, markup=False, emoji=False, soft_wrap=True
)

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_TEMP_DIR = Path(".temp")
BYTES_PER_MB = 1024 * 1024


def get_dir_size_mb(path: Path) -> float:
    """Calculate total size of directory in megabytes.

    Args:
        path: Directory to measure recursively.

    Returns:
        Total file size in megabytes (symlinks excluded).

    """
    total_bytes = 0
    with contextlib.suppress(OSError):
        for root, _, files in os.walk(path):
            for file_name in files:
                file_path = Path(root) / file_name
                if not file_path.is_symlink():
                    with contextlib.suppress(OSError):
                        total_bytes += file_path.stat().st_size
    return total_bytes / BYTES_PER_MB


def get_cached_dirs(
    temp_dir: Path = DEFAULT_TEMP_DIR,
) -> list[tuple[Path, float, float]]:
    """List all inspect-* directories sorted by modification time (oldest first).

    Args:
        temp_dir: Cache directory holding ``inspect-*`` clones.

    Returns:
        Tuples of ``(path, size in MB, mtime)`` sorted by mtime.

    """
    if not temp_dir.is_dir():
        return []

    cached: list[tuple[Path, float, float]] = []
    for item in temp_dir.iterdir():
        if item.is_dir() and item.name.startswith("inspect-"):
            try:
                mtime = item.stat().st_mtime
                size = get_dir_size_mb(item)
                cached.append((item, size, mtime))
            except OSError:
                pass

    return sorted(cached, key=operator.itemgetter(2))


def print_status(cached: list[tuple[Path, float, float]]) -> None:
    """Print status table of cached repository clones.

    Args:
        cached: Cached clone records as ``(path, size in MB, mtime)``.

    """
    if not cached:
        console.print("No cached inspect-* directories found in .temp/")
        return

    console.print("\n| Cached Clone Directory | Size (MB) |")
    console.print("| :--- | :---: |")
    total_mb = 0.0
    for path, size, _ in sorted(cached, key=operator.itemgetter(1), reverse=True):
        console.print(f"| `{path.name}` | {size:.1f} MB |")
        total_mb += size
    console.print(
        f"\nTotal Cache Size: **{total_mb:.1f} MB** "
        f"across {len(cached)} repositories.\n"
    )


def _delete_target_clones(
    cached: list[tuple[Path, float, float]], target: str, *, dry_run: bool
) -> None:
    """Delete or report a specific cached clone matching the target name.

    Args:
        cached: Cached clone records as ``(path, size in MB, mtime)``.
        target: Clone name with or without the ``inspect-`` prefix.
        dry_run: When True, only report the planned deletion.

    """
    clean_target = target.removeprefix("inspect-")
    match = [p for p, _, _ in cached if p.name in {target, f"inspect-{clean_target}"}]
    if not match:
        error_console.print(f"Target '{target}' not found in cache.")
        return

    for p in match:
        if dry_run:
            console.print(f"[DRY-RUN] Would delete: {p}")
        else:
            shutil.rmtree(p, ignore_errors=True)
            console.print(f"Deleted cached clone: {p}")


def _delete_all_clones(
    cached: list[tuple[Path, float, float]], *, dry_run: bool
) -> None:
    """Delete or report every cached clone.

    Args:
        cached: Cached clone records as ``(path, size in MB, mtime)``.
        dry_run: When True, only report planned deletions.

    """
    for p, size, _ in cached:
        if dry_run:
            console.print(f"[DRY-RUN] Would delete {p} ({size:.1f} MB)")
        else:
            shutil.rmtree(p, ignore_errors=True)
            console.print(f"Deleted {p} ({size:.1f} MB)")


def _enforce_budget(
    cached: list[tuple[Path, float, float]], max_size_mb: float, *, dry_run: bool
) -> None:
    """Delete oldest clones until the total cache fits the size budget.

    Args:
        cached: Cached clone records sorted oldest first.
        max_size_mb: Maximum allowed total cache size in MB.
        dry_run: When True, only report planned deletions.

    """
    total_mb = sum(size for _, size, _ in cached)
    if total_mb <= max_size_mb:
        console.print(
            f"Cache size ({total_mb:.1f} MB) is within budget "
            f"({max_size_mb:.1f} MB). No pruning needed."
        )
        return

    console.print(
        f"Current cache size ({total_mb:.1f} MB) exceeds budget "
        f"({max_size_mb:.1f} MB). Pruning oldest..."
    )
    # Oldest first
    for p, size, _ in cached:
        if total_mb <= max_size_mb:
            break
        if dry_run:
            console.print(f"[DRY-RUN] Would delete oldest: {p} ({size:.1f} MB)")
        else:
            shutil.rmtree(p, ignore_errors=True)
            console.print(f"Deleted oldest: {p} ({size:.1f} MB)")
        total_mb -= size


def prune_cache(
    temp_dir: Path = DEFAULT_TEMP_DIR,
    target: str = "",
    max_size_mb: float = 0.0,
    *,
    all_clones: bool = False,
    dry_run: bool = False,
) -> None:
    """Prune cached repository clones according to constraints.

    Args:
        temp_dir: Cache directory holding ``inspect-*`` clones.
        target: Specific clone name (or suffix) to delete.
        max_size_mb: Disk budget in MB; prunes oldest clones when exceeded.
        all_clones: Delete every cached clone.
        dry_run: Only report planned deletions.

    """
    cached = get_cached_dirs(temp_dir)
    if not cached:
        console.print("Cache is empty; nothing to prune.")
        return

    # Delete specific target
    if target:
        _delete_target_clones(cached, target, dry_run=dry_run)
        return

    # Delete all clones
    if all_clones:
        _delete_all_clones(cached, dry_run=dry_run)
        return

    # Enforce disk budget
    if max_size_mb > 0.0:
        _enforce_budget(cached, max_size_mb, dry_run=dry_run)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        The parsed argument namespace.

    """
    parser = argparse.ArgumentParser(
        description="Inspect and prune cached repository clones in .temp/."
    )
    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Show current cache usage and cached clones",
    )
    parser.add_argument(
        "--target",
        "-t",
        help="Delete a specific cached clone (e.g. inspect-<repo> or <repo>)",
    )
    parser.add_argument(
        "--max-size-mb",
        "-m",
        type=float,
        default=0.0,
        help="Maximum cache size budget in MB; prunes oldest when exceeded",
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="Delete all cached inspect-* clones"
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be pruned without deleting",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code; 0 on success.

    """
    args = parse_arguments(argv)
    cached = get_cached_dirs()
    no_budget = math.isclose(args.max_size_mb, 0.0)

    if args.status or (not args.target and not args.all and no_budget):
        print_status(cached)
        return 0

    prune_cache(
        target=args.target or "",
        max_size_mb=args.max_size_mb,
        all_clones=args.all,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
