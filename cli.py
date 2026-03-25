"""CLI entry point for SortWise."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import SortWiseConfig
from .organizer import Organizer
from .utils import OrganizeResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sortwise",
        description="Organize cluttered directories by file type, date, or custom rules.",
    )
    parser.add_argument("directory", type=Path, help="Directory to organize")
    parser.add_argument(
        "--strategy", choices=["type", "date", "custom"], default="type",
        help="Organization strategy (default: type)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    parser.add_argument("--config", type=Path, help="Path to custom rules JSON file")
    parser.add_argument("--recursive", action="store_true", help="Include files in subdirectories")
    parser.add_argument("--verbose", action="store_true", help="Show detailed operation log")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def print_result(result: OrganizeResult, verbose: bool, dry_run: bool) -> None:
    """Format and display the operation results."""
    mode = " (dry run)" if dry_run else ""

    if verbose:
        for op in result.operations:
            print(f"  \u2713 {op}")
        if result.errors:
            print()
            for err in result.errors:
                print(f"  \u2717 {err}")
        print()

    moved_label = "Would move" if dry_run else "Moved"
    categories = len(result.categories_used)
    print(f"Done{mode}! {moved_label} {result.total_moved} files into {categories} categories.")

    if result.errors:
        print(f"Encountered {len(result.errors)} errors.")

    if not dry_run and result.total_moved > 0:
        print("Undo script saved to: .sortwise_undo.sh")


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    config = SortWiseConfig(
        strategy=args.strategy,
        recursive=args.recursive,
        dry_run=args.dry_run,
        verbose=args.verbose,
        config_path=args.config,
    )

    print(f"SortWise v{__version__} \u2014 Organizing files in {args.directory}\n")

    try:
        organizer = Organizer(args.directory, config)
        result = organizer.run()
    except (NotADirectoryError, FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print_result(result, config.verbose, config.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
