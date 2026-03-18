"""Configuration loading for glassworm."""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

log = logging.getLogger("glassworm")

_DEFAULTS: dict[str, Any] = {
    "severity": "error",
    "include": [
        "*.py",
        "*.js",
        "*.ts",
        "*.jsx",
        "*.tsx",
        "*.json",
        "*.yaml",
        "*.yml",
        "*.md",
        "*.txt",
        "*.sh",
        "*.bash",
        "*.html",
        "*.css",
        "*.xml",
        "*.toml",
        "*.ini",
        "*.cfg",
        "*.env*",
    ],
    "exclude": ["vendor/", "node_modules/", ".venv/", "*.min.js"],
}

_CONFIG_KEYS = ("severity", "include", "exclude")


def get_default_config() -> dict[str, Any]:
    """Return a copy of default config (no file loading)."""
    return dict(_DEFAULTS)


def find_config_dir(start: Path | None = None) -> Path | None:
    """Find directory containing pyproject.toml or .glassworm.toml."""
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / ".glassworm.toml").exists():
            return parent
    return None


def _load_toml_section(filepath: Path) -> dict[str, Any]:
    """Load ``[tool.glassworm]`` from a TOML file, returning an empty dict on failure."""
    try:
        with filepath.open("rb") as f:
            data = tomllib.load(f)
        return data.get("tool", {}).get("glassworm", {})
    except (OSError, tomllib.TOMLDecodeError) as exc:
        log.warning("glassworm: failed to parse %s: %s", filepath, exc)
        return {}


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load glassworm config from pyproject.toml or .glassworm.toml.

    Merge order (later wins): defaults → ``.glassworm.toml`` → ``pyproject.toml``.
    If both files exist, ``pyproject.toml`` takes precedence for overlapping keys.
    """
    config: dict[str, Any] = dict(_DEFAULTS)

    base_dir: Path | None
    if config_path:
        base_dir = config_path if config_path.is_dir() else config_path.parent
    else:
        base_dir = find_config_dir()
    if base_dir is None:
        return config

    glassworm_toml = base_dir / ".glassworm.toml"
    if glassworm_toml.exists():
        section = _load_toml_section(glassworm_toml)
        for key in _CONFIG_KEYS:
            if key in section:
                config[key] = section[key]

    pyproject = base_dir / "pyproject.toml"
    if pyproject.exists():
        section = _load_toml_section(pyproject)
        for key in _CONFIG_KEYS:
            if key in section:
                config[key] = section[key]

    return config
