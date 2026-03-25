"""File operation helpers and duplicate resolution."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class FileOperation:
    """Represents a planned file move operation."""

    source: Path
    destination: Path
    category: str

    def __str__(self) -> str:
        return f"{self.source.name} → {self.category}/{self.destination.name}"


@dataclass
class OrganizeResult:
    """Summary of an organization run."""

    operations: list[FileOperation] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def total_moved(self) -> int:
        return len(self.operations)

    @property
    def categories_used(self) -> set[str]:
        return {op.category for op in self.operations}


def resolve_duplicate(destination: Path) -> Path:
    """Generate a unique filename if the destination already exists.

    Appends _2, _3, etc. before the file extension until a free name is found.

    >>> # If 'photo.jpg' exists, returns 'photo_2.jpg'
    """
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 2

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        candidate = parent / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def safe_move(source: Path, destination: Path, dry_run: bool = False) -> Path:
    """Move a file safely, creating parent directories as needed.

    Returns the actual destination path (may differ if duplicate resolved).
    """
    final_dest = resolve_duplicate(destination)

    if not dry_run:
        final_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(final_dest))

    return final_dest


def generate_undo_script(operations: list[FileOperation], output_dir: Path) -> Path:
    """Create a bash script that reverses all file moves."""
    script_path = output_dir / ".sortwise_undo.sh"
    lines = ["#!/bin/bash", "# SortWise undo script", f"# Generated {datetime.now().isoformat()}", ""]

    for op in reversed(operations):
        lines.append(f'mv "{op.destination}" "{op.source}"')

    # Clean up empty category directories
    dirs_to_remove = {op.destination.parent for op in operations}
    for d in dirs_to_remove:
        lines.append(f'rmdir --ignore-fail-on-non-empty "{d}" 2>/dev/null')

    lines.append("")
    script_path.write_text("\n".join(lines))
    os.chmod(script_path, 0o755)
    return script_path


def collect_files(directory: Path, recursive: bool = False) -> list[Path]:
    """Gather all files in a directory, optionally recursing into subdirs."""
    if recursive:
        return [p for p in directory.rglob("*") if p.is_file() and not p.name.startswith(".")]
    return [p for p in directory.iterdir() if p.is_file() and not p.name.startswith(".")]
