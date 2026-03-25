"""Core organization engine — coordinates strategies, file ops, and reporting."""

from __future__ import annotations

from pathlib import Path

from .config import SortWiseConfig
from .strategies import Strategy, get_strategy
from .utils import (
    FileOperation,
    OrganizeResult,
    collect_files,
    generate_undo_script,
    safe_move,
)


class Organizer:
    """Main engine that plans and executes file organization.

    Usage:
        organizer = Organizer(Path("~/Downloads"), config)
        result = organizer.run()
    """

    def __init__(self, target_dir: Path, config: SortWiseConfig) -> None:
        self.target_dir = target_dir.expanduser().resolve()
        self.config = config
        self.strategy: Strategy = get_strategy(config.strategy, config.config_path)

        if not self.target_dir.is_dir():
            raise NotADirectoryError(f"Target is not a directory: {self.target_dir}")

    def plan(self) -> list[FileOperation]:
        """Generate a list of planned moves without executing them."""
        files = collect_files(self.target_dir, recursive=self.config.recursive)
        operations: list[FileOperation] = []

        for filepath in sorted(files):
            if self.config.should_ignore(filepath.name):
                continue

            category = self.strategy.categorize(filepath)
            destination = self.target_dir / category / filepath.name

            operations.append(FileOperation(
                source=filepath,
                destination=destination,
                category=category,
            ))

        return operations

    def run(self) -> OrganizeResult:
        """Plan and execute the file organization.

        In dry-run mode, plans operations but doesn't move any files.
        Always generates an undo script (unless dry run).
        """
        result = OrganizeResult()
        planned = self.plan()

        for op in planned:
            try:
                actual_dest = safe_move(op.source, op.destination, dry_run=self.config.dry_run)
                # Update destination in case it was renamed for dedup
                executed = FileOperation(
                    source=op.source,
                    destination=actual_dest,
                    category=op.category,
                )
                result.operations.append(executed)

            except PermissionError:
                result.errors.append(f"Permission denied: {op.source.name}")
            except OSError as e:
                result.errors.append(f"Error moving {op.source.name}: {e}")

        # Generate undo script for actual (non-dry) runs
        if not self.config.dry_run and result.operations:
            generate_undo_script(result.operations, self.target_dir)

        return result
