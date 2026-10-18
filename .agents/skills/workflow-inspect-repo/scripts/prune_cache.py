"""Cache cleanup and disk budgeting manager for benchmark clones."""

import argparse
import os
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

DEFAULT_TEMP_DIR = Path(".temp")


def get_dir_size_mb(path: Path) -> float:
    """Calculate total size of directory in megabytes."""
    total_bytes = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if not os.path.islink(fp):
                    try:
                        total_bytes += os.path.getsize(fp)
                    except OSError:
                        pass
    except OSError:
        pass
    return total_bytes / (1024 * 1024)


def get_cached_dirs(
    temp_dir: Path = DEFAULT_TEMP_DIR,
) -> list[tuple[Path, float, float]]:
    """List all inspect-* directories sorted by modification time (oldest first)."""
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

    return sorted(cached, key=lambda x: x[2])


def print_status(cached: list[tuple[Path, float, float]]) -> None:
    """Print status table of cached repository clones."""
    if not cached:
        print("No cached inspect-* directories found in .temp/")
        return

    print("\n| Cached Clone Directory | Size (MB) |")
    print("| :--- | :---: |")
    total_mb = 0.0
    for path, size, _ in sorted(cached, key=lambda x: x[1], reverse=True):
        print(f"| `{path.name}` | {size:.1f} MB |")
        total_mb += size
    print(
        f"\nTotal Cache Size: **{total_mb:.1f} MB** across {len(cached)} repositories.\n"
    )


def prune_cache(
    temp_dir: Path = DEFAULT_TEMP_DIR,
    target: str = "",
    max_size_mb: float = 0.0,
    all_clones: bool = False,
    dry_run: bool = False,
) -> None:
    """Prune cached repository clones according to constraints."""
    cached = get_cached_dirs(temp_dir)
    if not cached:
        print("Cache is empty; nothing to prune.")
        return

    # Delete specific target
    if target:
        clean_target = target.removeprefix("inspect-")
        match = [
            p for p, _, _ in cached if p.name in (target, f"inspect-{clean_target}")
        ]
        if match:
            for p in match:
                if dry_run:
                    print(f"[DRY-RUN] Would delete: {p}")
                else:
                    shutil.rmtree(p, ignore_errors=True)
                    print(f"Deleted cached clone: {p}")
        else:
            print(f"Target '{target}' not found in cache.", file=sys.stderr)
        return

    # Delete all clones
    if all_clones:
        for p, size, _ in cached:
            if dry_run:
                print(f"[DRY-RUN] Would delete {p} ({size:.1f} MB)")
            else:
                shutil.rmtree(p, ignore_errors=True)
                print(f"Deleted {p} ({size:.1f} MB)")
        return

    # Enforce disk budget
    if max_size_mb > 0.0:
        total_mb = sum(size for _, size, _ in cached)
        if total_mb <= max_size_mb:
            print(
                f"Cache size ({total_mb:.1f} MB) is within budget ({max_size_mb:.1f} MB). No pruning needed."
            )
            return

        print(
            f"Current cache size ({total_mb:.1f} MB) exceeds budget ({max_size_mb:.1f} MB). Pruning oldest..."
        )
        # Oldest first
        for p, size, _ in cached:
            if total_mb <= max_size_mb:
                break
            if dry_run:
                print(f"[DRY-RUN] Would delete oldest: {p} ({size:.1f} MB)")
            else:
                shutil.rmtree(p, ignore_errors=True)
                print(f"Deleted oldest: {p} ({size:.1f} MB)")
            total_mb -= size


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
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
    """CLI entrypoint."""
    args = parse_arguments(argv)
    cached = get_cached_dirs()

    if args.status or (not args.target and not args.all and args.max_size_mb == 0.0):
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
