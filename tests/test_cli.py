"""Tests for the glassworm CLI."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from glassworm.cli import run

# --no-config bypasses project config so fixtures (in exclude) are scanned
_FIXTURE_ARGS = ["--no-config"]


class TestRunUnit:
    """Test the ``run()`` function directly."""

    def test_clean_file_exit_zero(self, fixtures_dir: Path) -> None:
        code = run([*_FIXTURE_ARGS, str(fixtures_dir / "clean.txt")])
        assert code == 0

    def test_dangerous_file_exit_one(self, fixtures_dir: Path) -> None:
        code = run([*_FIXTURE_ARGS, str(fixtures_dir / "variation_selector.py")])
        assert code == 1

    def test_severity_warning_exit_zero(self, fixtures_dir: Path) -> None:
        code = run(
            [*_FIXTURE_ARGS, "--severity", "warning", str(fixtures_dir / "variation_selector.py")]
        )
        assert code == 0

    def test_quiet_still_exits_nonzero(self, fixtures_dir: Path) -> None:
        code = run([*_FIXTURE_ARGS, "-q", str(fixtures_dir / "variation_selector.py")])
        assert code == 1

    def test_json_output(self, fixtures_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        run([*_FIXTURE_ARGS, "--format", "json", str(fixtures_dir / "variation_selector.py")])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "codepoint" in data[0]
        assert "char" not in data[0]  # char excluded from JSON

    def test_json_clean_file(self, fixtures_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        run([*_FIXTURE_ARGS, "--format", "json", str(fixtures_dir / "clean.txt")])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data == []

    def test_directory_scanning(self, fixtures_dir: Path) -> None:
        """Passing a directory should recurse and find findings."""
        code = run([*_FIXTURE_ARGS, str(fixtures_dir)])
        assert code == 1  # fixtures contain dangerous files

    def test_nonexistent_file_skipped(
        self, fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = run(["-v", str(fixtures_dir / "nonexistent.py")])
        assert code == 0
        captured = capsys.readouterr()
        assert "skipped" in captured.err

    def test_quiet_suppresses_per_finding(
        self, fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run([*_FIXTURE_ARGS, "-q", str(fixtures_dir / "variation_selector.py")])
        captured = capsys.readouterr()
        # Per-finding lines should NOT appear in stdout
        assert "U+FE00" not in captured.out
        # Summary still in stderr
        assert "Found" in captured.err

    def test_text_output_contains_category(
        self, fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run([*_FIXTURE_ARGS, str(fixtures_dir / "variation_selector.py")])
        captured = capsys.readouterr()
        assert "GlassWorm" in captured.out  # human-readable reason, not "Mn"

    def test_empty_stdin_exit_zero(self) -> None:
        """Empty stdin should return 0 (no findings)."""
        with patch.object(sys, "stdin", io.StringIO("")):
            code = run([])
        assert code == 0

    def test_include_exclude_filtering(self, tmp_path: Path) -> None:
        """Directory scan respects include/exclude from config."""
        # Create layout: a.py (scan), b.dat (excluded by include), node_modules/x.py (excluded)
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "b.dat").write_text("data\n")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "x.py").write_text("x = 1\u200b\n")  # has ZWSP
        (tmp_path / "pyproject.toml").write_text(
            '[tool.glassworm]\ninclude = ["*.py"]\nexclude = ["node_modules/"]\n'
        )
        code = run(["--config", str(tmp_path / "pyproject.toml"), str(tmp_path)])
        # a.py is clean, b.dat skipped (include), node_modules/x.py skipped (exclude)
        assert code == 0


# ---------------------------------------------------------------------------
# Integration tests — subprocess (validates entrypoint + exit codes)
# ---------------------------------------------------------------------------


class TestCLISubprocess:
    """Integration tests that shell out to the CLI."""

    @staticmethod
    def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "glassworm", *args],
            capture_output=True,
            text=True,
            cwd=cwd or Path(__file__).parent.parent,
        )

    def test_help(self) -> None:
        result = self._run("--help")
        assert result.returncode == 0
        assert "glassworm" in result.stdout.lower()

    def test_version(self) -> None:
        result = self._run("--version")
        assert result.returncode == 0
        assert "glassworm" in result.stdout

    def test_clean_file(self, fixtures_dir: Path) -> None:
        result = self._run("--no-config", str(fixtures_dir / "clean.txt"))
        assert result.returncode == 0

    def test_dangerous_file(self, fixtures_dir: Path) -> None:
        result = self._run("--no-config", str(fixtures_dir / "variation_selector.py"))
        assert result.returncode == 1

    def test_severity_warning(self, fixtures_dir: Path) -> None:
        result = self._run(
            "--no-config", "--severity", "warning", str(fixtures_dir / "variation_selector.py")
        )
        assert result.returncode == 0

    def test_json_output(self, fixtures_dir: Path) -> None:
        result = self._run(
            "--no-config", "--format", "json", str(fixtures_dir / "variation_selector.py")
        )
        data = json.loads(result.stdout)
        assert len(data) >= 1

    def test_invalid_args_exit_2(self) -> None:
        """Invalid arguments produce exit code 2."""
        result = self._run("--invalid-flag")
        assert result.returncode == 2
