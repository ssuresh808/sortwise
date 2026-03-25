"""Tests for sortwise.organizer — the core engine."""

from pathlib import Path

import pytest

from sortwise.config import SortWiseConfig
from sortwise.organizer import Organizer


@pytest.fixture
def messy_dir(tmp_path: Path) -> Path:
    """Create a realistic messy directory."""
    (tmp_path / "vacation.jpg").write_text("image")
    (tmp_path / "resume.pdf").write_text("pdf")
    (tmp_path / "budget.xlsx").write_text("spreadsheet")
    (tmp_path / "song.mp3").write_text("audio")
    (tmp_path / "script.py").write_text("print('hello')")
    return tmp_path


class TestOrganizer:
    def test_plan_generates_operations(self, messy_dir: Path) -> None:
        config = SortWiseConfig(strategy="type")
        organizer = Organizer(messy_dir, config)
        plan = organizer.plan()
        assert len(plan) == 5
        categories = {op.category for op in plan}
        assert "Images" in categories
        assert "Documents" in categories

    def test_dry_run_does_not_move(self, messy_dir: Path) -> None:
        config = SortWiseConfig(strategy="type", dry_run=True)
        organizer = Organizer(messy_dir, config)
        result = organizer.run()

        assert result.total_moved == 5
        # Files should still be in original location
        assert (messy_dir / "vacation.jpg").exists()
        assert not (messy_dir / "Images").exists()

    def test_actual_run_moves_files(self, messy_dir: Path) -> None:
        config = SortWiseConfig(strategy="type")
        organizer = Organizer(messy_dir, config)
        result = organizer.run()

        assert result.total_moved == 5
        assert (messy_dir / "Images" / "vacation.jpg").exists()
        assert (messy_dir / "Documents" / "resume.pdf").exists()
        assert (messy_dir / "Spreadsheets" / "budget.xlsx").exists()
        assert not (messy_dir / "vacation.jpg").exists()

    def test_undo_script_generated(self, messy_dir: Path) -> None:
        config = SortWiseConfig(strategy="type")
        organizer = Organizer(messy_dir, config)
        organizer.run()
        assert (messy_dir / ".sortwise_undo.sh").exists()

    def test_no_undo_script_on_dry_run(self, messy_dir: Path) -> None:
        config = SortWiseConfig(strategy="type", dry_run=True)
        organizer = Organizer(messy_dir, config)
        organizer.run()
        assert not (messy_dir / ".sortwise_undo.sh").exists()

    def test_invalid_directory(self, tmp_path: Path) -> None:
        config = SortWiseConfig()
        with pytest.raises(NotADirectoryError):
            Organizer(tmp_path / "nonexistent", config)

    def test_ignores_hidden_files(self, messy_dir: Path) -> None:
        (messy_dir / ".DS_Store").write_text("system")
        config = SortWiseConfig(strategy="type")
        organizer = Organizer(messy_dir, config)
        plan = organizer.plan()
        filenames = {op.source.name for op in plan}
        assert ".DS_Store" not in filenames

    def test_date_strategy_integration(self, messy_dir: Path) -> None:
        config = SortWiseConfig(strategy="date", dry_run=True)
        organizer = Organizer(messy_dir, config)
        result = organizer.run()
        # All files should be categorized under year/month
        for op in result.operations:
            parts = op.category.split("/")
            assert len(parts) == 2
            assert parts[0].isdigit()
