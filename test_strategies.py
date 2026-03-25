"""Tests for sortwise.strategies — file categorization logic."""

import json
from pathlib import Path

import pytest

from sortwise.strategies import (
    CustomStrategy,
    DateStrategy,
    TypeStrategy,
    get_strategy,
)


class TestTypeStrategy:
    @pytest.fixture
    def strategy(self) -> TypeStrategy:
        return TypeStrategy()

    @pytest.mark.parametrize("filename,expected", [
        ("photo.jpg", "Images"),
        ("photo.JPEG", "Images"),
        ("report.pdf", "Documents"),
        ("data.csv", "Spreadsheets"),
        ("song.mp3", "Audio"),
        ("movie.mp4", "Videos"),
        ("backup.zip", "Archives"),
        ("app.py", "Code"),
        ("setup.exe", "Applications"),
        ("mystery.xyz", "Other"),
    ])
    def test_categorization(self, strategy: TypeStrategy, filename: str, expected: str) -> None:
        filepath = Path(f"/tmp/{filename}")
        assert strategy.categorize(filepath) == expected

    def test_case_insensitive(self, strategy: TypeStrategy) -> None:
        assert strategy.categorize(Path("FILE.PNG")) == "Images"
        assert strategy.categorize(Path("DOC.PDF")) == "Documents"

    def test_name(self, strategy: TypeStrategy) -> None:
        assert strategy.name == "File Type"


class TestDateStrategy:
    @pytest.fixture
    def strategy(self) -> DateStrategy:
        return DateStrategy()

    def test_categorizes_by_year_month(self, strategy: DateStrategy, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        result = strategy.categorize(test_file)
        # Should be in format "YYYY/MonthName"
        parts = result.split("/")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert len(parts[0]) == 4

    def test_name(self, strategy: DateStrategy) -> None:
        assert strategy.name == "Date Modified"


class TestCustomStrategy:
    @pytest.fixture
    def config_file(self, tmp_path: Path) -> Path:
        config = {
            "categories": {
                "Design": [".psd", ".fig", ".sketch"],
                "Data": [".csv", ".json", ".parquet"],
            },
            "fallback": "Misc",
        }
        path = tmp_path / "rules.json"
        path.write_text(json.dumps(config))
        return path

    def test_custom_mapping(self, config_file: Path) -> None:
        strategy = CustomStrategy(config_file)
        assert strategy.categorize(Path("mockup.psd")) == "Design"
        assert strategy.categorize(Path("data.csv")) == "Data"

    def test_custom_fallback(self, config_file: Path) -> None:
        strategy = CustomStrategy(config_file)
        assert strategy.categorize(Path("unknown.xyz")) == "Misc"

    def test_missing_config_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            CustomStrategy(tmp_path / "nonexistent.json")

    def test_invalid_config(self, tmp_path: Path) -> None:
        bad_config = tmp_path / "bad.json"
        bad_config.write_text('{"not_categories": {}}')
        with pytest.raises(ValueError, match="categories"):
            CustomStrategy(bad_config)


class TestGetStrategy:
    def test_type_strategy(self) -> None:
        assert isinstance(get_strategy("type"), TypeStrategy)

    def test_date_strategy(self) -> None:
        assert isinstance(get_strategy("date"), DateStrategy)

    def test_custom_requires_config(self) -> None:
        with pytest.raises(ValueError, match="config"):
            get_strategy("custom")

    def test_unknown_strategy(self) -> None:
        with pytest.raises(ValueError, match="Unknown"):
            get_strategy("magic")
