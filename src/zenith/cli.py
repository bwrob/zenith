"""Command-line interface entry points for Zenith."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Run the Zenith CLI entry point.

    Args:
        argv: Command-line argument vector.

    Returns:
        Process exit code.

    """
    _ = argv or sys.argv[1:]
    return 0


if __name__ == "__main__":
    sys.exit(main())
