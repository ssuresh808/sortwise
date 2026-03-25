"""Configuration file loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SortWiseConfig:
    """Application configuration with sensible defaults."""

    strategy: str = "type"
    recursive: bool = False
    dry_run: bool = False
    verbose: bool = False
    config_path: Path | None = None
    ignore_patterns: list[str] = field(default_factory=lambda: [".DS_Store", "Thumbs.db", ".sortwise_undo.sh"])

    def should_ignore(self, filename: str) -> bool:
        """Check if a file should be skipped during organization."""
        return filename in self.ignore_patterns or filename.startswith(".")


def load_custom_rules(path: Path) -> dict:
    """Load and validate a custom rules JSON file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config structure is invalid.
        json.JSONDecodeError: If JSON is malformed.
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        config = json.load(f)

    _validate_config(config)
    return config


def _validate_config(config: dict) -> None:
    """Ensure the config has the required structure."""
    if not isinstance(config, dict):
        raise ValueError("Config must be a JSON object")

    if "categories" not in config:
        raise ValueError("Config must contain a 'categories' key")

    categories = config["categories"]
    if not isinstance(categories, dict):
        raise ValueError("'categories' must be a mapping of name → extensions")

    for name, extensions in categories.items():
        if not isinstance(extensions, list):
            raise ValueError(f"Category '{name}' must map to a list of extensions")
        for ext in extensions:
            if not isinstance(ext, str):
                raise ValueError(f"Extensions in '{name}' must be strings, got {type(ext)}")
