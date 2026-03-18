"""Tests for the glassworm config module."""

from __future__ import annotations

from pathlib import Path

import pytest

from glassworm.config import find_config_dir, load_config


class TestFindConfigDir:
    def test_finds_pyproject(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        result = find_config_dir(tmp_path)
        assert result == tmp_path

    def test_finds_glassworm_toml(self, tmp_path: Path) -> None:
        (tmp_path / ".glassworm.toml").write_text("[tool.glassworm]\nseverity='warning'\n")
        result = find_config_dir(tmp_path)
        assert result == tmp_path

    def test_returns_none_when_missing(self, tmp_path: Path) -> None:
        subdir = tmp_path / "deep" / "nested"
        subdir.mkdir(parents=True)
        result = find_config_dir(subdir)
        assert result is None


class TestLoadConfig:
    def test_defaults(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert config["severity"] == "error"
        assert isinstance(config["include"], list)
        assert isinstance(config["exclude"], list)

    def test_pyproject_override(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('[tool.glassworm]\nseverity = "warning"\n')
        config = load_config(tmp_path / "pyproject.toml")
        assert config["severity"] == "warning"

    def test_glassworm_toml_override(self, tmp_path: Path) -> None:
        (tmp_path / ".glassworm.toml").write_text('[tool.glassworm]\nseverity = "warning"\n')
        config = load_config(tmp_path / ".glassworm.toml")
        assert config["severity"] == "warning"

    def test_pyproject_wins_over_glassworm_toml(self, tmp_path: Path) -> None:
        (tmp_path / ".glassworm.toml").write_text('[tool.glassworm]\nseverity = "warning"\n')
        (tmp_path / "pyproject.toml").write_text('[tool.glassworm]\nseverity = "error"\n')
        config = load_config(tmp_path / "pyproject.toml")
        assert config["severity"] == "error"

    def test_config_with_directory(self, tmp_path: Path) -> None:
        """When --config points to a directory, load from that directory."""
        (tmp_path / "pyproject.toml").write_text('[tool.glassworm]\nseverity = "warning"\n')
        config = load_config(tmp_path)  # pass directory, not file
        assert config["severity"] == "warning"

    def test_config_parse_error_fallback_to_defaults(self, tmp_path: Path) -> None:
        """Corrupt TOML falls back to defaults gracefully."""
        (tmp_path / "pyproject.toml").write_text("invalid toml {{{")
        config = load_config(tmp_path / "pyproject.toml")
        assert config["severity"] == "error"  # default
