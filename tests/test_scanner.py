"""Tests for the glassworm scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from glassworm.scanner import (
    _is_dangerous,
    scan_content,
    scan_file,
    scan_files,
)

# ---------------------------------------------------------------------------
# _is_dangerous
# ---------------------------------------------------------------------------


class TestIsDangerous:
    """Unit tests for the _is_dangerous helper."""

    @pytest.mark.parametrize(
        "cp",
        [0xFE00, 0xFE0F, 0xFE07],
        ids=["VS1", "VS16", "VS8"],
    )
    def test_variation_selectors(self, cp: int) -> None:
        ok, reason = _is_dangerous(cp)
        assert ok
        assert "GlassWorm" in reason

    @pytest.mark.parametrize(
        "cp",
        [0xE0100, 0xE01EF],
        ids=["VS17", "VS256"],
    )
    def test_variation_selectors_supplement(self, cp: int) -> None:
        ok, reason = _is_dangerous(cp)
        assert ok
        assert "supplement" in reason.lower()

    @pytest.mark.parametrize(
        "cp",
        [0x202A, 0x202E, 0x2066, 0x2069],
        ids=["LRE", "RLO", "LRI", "PDI"],
    )
    def test_bidi_control(self, cp: int) -> None:
        ok, reason = _is_dangerous(cp)
        assert ok
        assert "bidi" in reason.lower()

    @pytest.mark.parametrize(
        "cp",
        [0x200B, 0x200D, 0x200F, 0x2060, 0x2064],
        ids=["ZWSP", "ZWJ", "RLM", "WJ", "INVISIBLE_PLUS"],
    )
    def test_zero_width(self, cp: int) -> None:
        ok, reason = _is_dangerous(cp)
        assert ok
        assert "zero-width" in reason.lower()

    def test_mongolian_vowel(self) -> None:
        ok, reason = _is_dangerous(0x180E)
        assert ok
        assert "Mongolian" in reason

    def test_bom(self) -> None:
        ok, reason = _is_dangerous(0xFEFF)
        assert ok
        assert "BOM" in reason

    def test_replacement(self) -> None:
        ok, reason = _is_dangerous(0xFFFD)
        assert ok
        assert "replacement" in reason.lower()

    @pytest.mark.parametrize("char", list("hello 123 A-Z"))
    def test_safe_ascii(self, char: str) -> None:
        ok, _ = _is_dangerous(ord(char))
        assert not ok


# ---------------------------------------------------------------------------
# scan_content
# ---------------------------------------------------------------------------


class TestScanContent:
    def test_clean_content(self) -> None:
        findings = scan_content("def hello():\n    return 42\n", path="test.py")
        assert findings == []

    def test_variation_selector(self) -> None:
        findings = scan_content("x = 1\ufe00\n", path="x.py")
        assert len(findings) == 1
        f = findings[0]
        assert f.codepoint == 0xFE00
        assert f.line == 1
        assert f.column == 6
        assert "GlassWorm" in f.category

    def test_zero_width_space(self) -> None:
        findings = scan_content("hello\u200bworld\n", path="x.txt")
        assert len(findings) == 1
        assert findings[0].codepoint == 0x200B
        assert "zero-width" in findings[0].category

    def test_bidi_control(self) -> None:
        findings = scan_content("admin\u202a = True\n", path="x.py")
        assert len(findings) == 1
        assert findings[0].codepoint == 0x202A
        assert "bidi" in findings[0].category

    def test_bom_mid_file(self) -> None:
        findings = scan_content("line1\n\ufeffline2\n", path="x.txt")
        assert len(findings) == 1
        assert findings[0].codepoint == 0xFEFF
        assert findings[0].line == 2

    def test_bom_at_file_start_is_ignored(self) -> None:
        """BOM (U+FEFF) at position (1,1) is a valid UTF-8 BOM — not flagged."""
        findings = scan_content("\ufeffline1\n", path="x.txt")
        assert findings == []

    def test_replacement_char(self) -> None:
        findings = scan_content("bad \ufffd data\n", path="x.txt")
        assert len(findings) == 1
        assert findings[0].codepoint == 0xFFFD

    def test_multiple_findings(self) -> None:
        findings = scan_content("a\u200bb\u200cc\n", path="x.txt")
        assert len(findings) >= 2

    def test_finding_category_is_reason_not_unicode_cat(self) -> None:
        """category field should hold the human-readable reason, not 'Cf'."""
        findings = scan_content("x\ufe00y\n", path="t.py")
        assert len(findings) == 1
        assert findings[0].category != "Mn"
        assert "GlassWorm" in findings[0].category

    def test_finding_unicode_category_field(self) -> None:
        findings = scan_content("x\ufe00y\n", path="t.py")
        assert findings[0].unicode_category == "Mn"

    def test_finding_to_dict(self) -> None:
        findings = scan_content("x\ufe00y\n", path="t.py")
        d = findings[0].to_dict()
        assert "char" not in d
        assert d["codepoint"] == 0xFE00

    def test_finding_to_json(self) -> None:
        import json

        findings = scan_content("x\ufe00y\n", path="t.py")
        parsed = json.loads(findings[0].to_json())
        assert parsed["hex_repr"] == "U+FE00"


# ---------------------------------------------------------------------------
# scan_file / scan_files
# ---------------------------------------------------------------------------


class TestScanFile:
    def test_nonexistent(self) -> None:
        assert scan_file(Path("/nonexistent/foo.py")) == []

    def test_clean(self, fixtures_dir: Path) -> None:
        assert scan_file(fixtures_dir / "clean.txt") == []

    def test_variation_selector(self, fixtures_dir: Path) -> None:
        findings = scan_file(fixtures_dir / "variation_selector.py")
        assert len(findings) >= 1
        assert any(f.codepoint == 0xFE00 for f in findings)

    def test_bidi(self, fixtures_dir: Path) -> None:
        findings = scan_file(fixtures_dir / "bidi_control.py")
        assert len(findings) >= 1

    def test_zero_width(self, fixtures_dir: Path) -> None:
        findings = scan_file(fixtures_dir / "zero_width.js")
        assert len(findings) >= 1

    def test_scan_files_combines(self, fixtures_dir: Path) -> None:
        paths = [fixtures_dir / "variation_selector.py", fixtures_dir / "zero_width.js"]
        findings = scan_files(paths)
        assert len(findings) >= 2
        found_paths = {f.path for f in findings}
        assert len(found_paths) == 2
