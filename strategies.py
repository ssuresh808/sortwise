"""Organization strategies using the Strategy pattern.

Each strategy takes a file path and returns the category (subfolder name)
that file should be sorted into.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

# Default extension-to-category mapping
TYPE_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images", ".svg": "Images",
    ".webp": "Images", ".ico": "Images", ".tiff": "Images",
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".md": "Documents", ".tex": "Documents",
    # Spreadsheets
    ".xls": "Spreadsheets", ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets", ".tsv": "Spreadsheets",
    # Videos
    ".mp4": "Videos", ".avi": "Videos", ".mkv": "Videos",
    ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos", ".webm": "Videos",
    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    ".aac": "Audio", ".ogg": "Audio", ".wma": "Audio",
    # Archives
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".rar": "Archives", ".7z": "Archives", ".bz2": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code",
    ".css": "Code", ".java": "Code", ".cpp": "Code", ".c": "Code",
    ".go": "Code", ".rs": "Code", ".rb": "Code", ".php": "Code",
    # Applications
    ".exe": "Applications", ".msi": "Applications",
    ".dmg": "Applications", ".app": "Applications",
    ".deb": "Applications", ".rpm": "Applications",
}

FALLBACK_CATEGORY = "Other"


class Strategy(ABC):
    """Base class for file organization strategies."""

    @abstractmethod
    def categorize(self, filepath: Path) -> str:
        """Return the category folder name for a given file."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name."""


class TypeStrategy(Strategy):
    """Organize files by their extension into type-based folders."""

    @property
    def name(self) -> str:
        return "File Type"

    def categorize(self, filepath: Path) -> str:
        ext = filepath.suffix.lower()
        return TYPE_MAP.get(ext, FALLBACK_CATEGORY)


class DateStrategy(Strategy):
    """Organize files by their last-modified date into year/month folders."""

    @property
    def name(self) -> str:
        return "Date Modified"

    def categorize(self, filepath: Path) -> str:
        mtime = filepath.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)
        return f"{dt.year}/{dt.strftime('%B')}"


class CustomStrategy(Strategy):
    """Organize files using a user-defined JSON configuration.

    Config format:
    {
        "categories": {
            "Category Name": [".ext1", ".ext2"]
        },
        "fallback": "Other"
    }
    """

    def __init__(self, config_path: Path) -> None:
        self._config = self._load_config(config_path)
        self._lookup = self._build_lookup()
        self._fallback = self._config.get("fallback", FALLBACK_CATEGORY)

    @property
    def name(self) -> str:
        return "Custom Rules"

    def categorize(self, filepath: Path) -> str:
        ext = filepath.suffix.lower()
        return self._lookup.get(ext, self._fallback)

    def _load_config(self, path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path) as f:
            config = json.load(f)

        if "categories" not in config:
            raise ValueError("Config must contain a 'categories' key")

        return config

    def _build_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        for category, extensions in self._config["categories"].items():
            for ext in extensions:
                normalized = ext if ext.startswith(".") else f".{ext}"
                lookup[normalized.lower()] = category
        return lookup


def get_strategy(name: str, config_path: Path | None = None) -> Strategy:
    """Factory function to create the appropriate strategy.

    Args:
        name: One of 'type', 'date', or 'custom'.
        config_path: Required if name is 'custom'.

    Returns:
        An initialized Strategy instance.

    Raises:
        ValueError: If strategy name is unknown or config missing for custom.
    """
    strategies = {
        "type": lambda: TypeStrategy(),
        "date": lambda: DateStrategy(),
        "custom": lambda: CustomStrategy(config_path) if config_path else None,
    }

    if name not in strategies:
        valid = ", ".join(strategies.keys())
        raise ValueError(f"Unknown strategy '{name}'. Choose from: {valid}")

    if name == "custom" and config_path is None:
        raise ValueError("Custom strategy requires a --config path")

    strategy = strategies[name]()
    if strategy is None:
        raise ValueError("Failed to initialize strategy")

    return strategy
