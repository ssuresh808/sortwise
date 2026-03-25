"""Tests for sortwise.utils — file operations and duplicate resolution."""

import os
from pathlib import Path

import pytest

from sortwise.utils import (
    FileOperation,
    OrganizeResult,
    collect_files,
    generate_undo_script,
    resolve_duplicate,
    safe_move,
)


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample files."""
    (tmp_path / "photo.jpg").write_text("fake image")
    (tmp_path / "report.pdf").write_text("fake pdf")
    (tmp_path / "notes.txt").write_text("hello world")
    (tmp_path / ".hidden").write_text("hidden file")
    return tmp_path


class TestResolveDuplicate:
    def test_no_conflict(self, tmp_path: Path) -> None:
        target = tmp_path / "file.txt"
        assert resolve_duplicate(target) == target

    def test_first_conflict(self, tmp_path: Path) -> None:
        existing = tmp_path / "file.txt"
        existing.write_text("exists")
        result = resolve_duplicate(existing)
        assert result == tmp_path / "file_2.txt"

    def test_multiple_conflicts(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").write_text("v1")
        (tmp_path / "file_2.txt").write_text("v2")
        result = resolve_duplicate(tmp_path / "file.txt")
        assert result == tmp_path / "file_3.txt"


class TestSafeMove:
    def test_basic_move(self, tmp_path: Path) -> None:
        src = tmp_path / "source.txt"
        src.write_text("content")
        dest = tmp_path / "subdir" / "source.txt"

        result = safe_move(src, dest)
        assert result == dest
        assert dest.read_text() == "content"
        assert not src.exists()

    def test_dry_run_no_move(self, tmp_path: Path) -> None:
        src = tmp_path / "source.txt"
        src.write_text("content")
        dest = tmp_path / "subdir" / "source.txt"

        result = safe_move(src, dest, dry_run=True)
        assert result == dest
        assert src.exists()  # File should NOT have moved
        assert not dest.exists()

    def test_duplicate_resolution(self, tmp_path: Path) -> None:
        dest_dir = tmp_path / "target"
        dest_dir.mkdir()
        (dest_dir / "file.txt").write_text("existing")

        src = tmp_path / "file.txt"
        src.write_text("new content")

        result = safe_move(src, dest_dir / "file.txt")
        assert result == dest_dir / "file_2.txt"
        assert result.read_text() == "new content"


class TestCollectFiles:
    def test_non_recursive(self, temp_dir: Path) -> None:
        files = collect_files(temp_dir)
        names = {f.name for f in files}
        assert "photo.jpg" in names
        assert "report.pdf" in names
        assert ".hidden" not in names  # Hidden files excluded

    def test_recursive(self, temp_dir: Path) -> None:
        subdir = temp_dir / "nested"
        subdir.mkdir()
        (subdir / "deep.txt").write_text("deep content")

        files = collect_files(temp_dir, recursive=True)
        names = {f.name for f in files}
        assert "deep.txt" in names

    def test_non_recursive_skips_nested(self, temp_dir: Path) -> None:
        subdir = temp_dir / "nested"
        subdir.mkdir()
        (subdir / "deep.txt").write_text("deep content")

        files = collect_files(temp_dir, recursive=False)
        names = {f.name for f in files}
        assert "deep.txt" not in names


class TestGenerateUndoScript:
    def test_creates_executable_script(self, tmp_path: Path) -> None:
        ops = [
            FileOperation(
                source=tmp_path / "file.txt",
                destination=tmp_path / "Documents" / "file.txt",
                category="Documents",
            )
        ]
        script = generate_undo_script(ops, tmp_path)
        assert script.exists()
        assert os.access(script, os.X_OK)
        content = script.read_text()
        assert "mv" in content
        assert "Documents" in content


class TestOrganizeResult:
    def test_empty_result(self) -> None:
        result = OrganizeResult()
        assert result.total_moved == 0
        assert result.categories_used == set()

    def test_with_operations(self, tmp_path: Path) -> None:
        ops = [
            FileOperation(tmp_path / "a.jpg", tmp_path / "Images/a.jpg", "Images"),
            FileOperation(tmp_path / "b.pdf", tmp_path / "Documents/b.pdf", "Documents"),
            FileOperation(tmp_path / "c.jpg", tmp_path / "Images/c.jpg", "Images"),
        ]
        result = OrganizeResult(operations=ops)
        assert result.total_moved == 3
        assert result.categories_used == {"Images", "Documents"}
