"""Core scanner for GlassWorm-style invisible Unicode attacks."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Finding:
    """A single finding of a dangerous Unicode character."""

    path: str
    line: int
    column: int
    codepoint: int
    char: str
    name: str
    hex_repr: str
    category: str
    unicode_category: str

    def to_dict(self) -> dict[str, str | int]:
        """Serialise finding to a JSON-safe dict (excludes raw char)."""
        d = asdict(self)
        del d["char"]
        return d

    def to_json(self) -> str:
        """Serialise finding to a JSON string."""
        return json.dumps(self.to_dict())


# ---------------------------------------------------------------------------
# Dangerous Unicode ranges / codepoints
# ---------------------------------------------------------------------------

# Pattern table: (start, end, reason)
_DANGEROUS_RANGES: list[tuple[int, int, str]] = [
    # Variation Selectors — GlassWorm primary technique
    (0xFE00, 0xFE0F, "variation selector (GlassWorm)"),
    # Variation Selectors Supplement
    (0xE0100, 0xE01EF, "variation selector supplement (GlassWorm)"),
    # Bidi control — Trojan Source CVE-2021-42574
    (0x202A, 0x202E, "bidi control (Trojan Source CVE-2021-42574)"),
    (0x2066, 0x2069, "bidi control (Trojan Source CVE-2021-42574)"),
    # Zero-width and invisible
    (0x200B, 0x200F, "zero-width/invisible"),
    (0x2060, 0x2064, "zero-width/invisible"),
]

# Single codepoints
_DANGEROUS_SINGLES: dict[int, str] = {
    0x180E: "Mongolian vowel separator (Cf)",
    0xFEFF: "BOM mid-file",
    0xFFFD: "replacement character (unsafe decoding)",
}

# BOM codepoint — used for start-of-file exemption
_BOM = 0xFEFF


def _is_dangerous(codepoint: int) -> tuple[bool, str]:
    """Check if a Unicode codepoint is dangerous.

    Returns ``(is_dangerous, reason)``.
    """
    for start, end, reason in _DANGEROUS_RANGES:
        if start <= codepoint <= end:
            return True, reason

    if codepoint in _DANGEROUS_SINGLES:
        return True, _DANGEROUS_SINGLES[codepoint]

    # Cf = Format characters (invisible) — catch-all
    if unicodedata.category(chr(codepoint)) == "Cf":
        return True, "format character (Cf)"

    return False, ""


def scan_content(content: str, path: str = "<stdin>") -> list[Finding]:
    """Scan string content for dangerous Unicode characters.

    Returns a list of findings with line, column, and details.
    """
    findings: list[Finding] = []
    lines = content.splitlines(keepends=True)

    for line_no, line in enumerate(lines, start=1):
        for col_no, char in enumerate(line):
            cp = ord(char)

            # Valid UTF-8 BOM at start of file — skip
            if cp == _BOM and line_no == 1 and col_no == 0:
                continue

            is_dangerous, reason = _is_dangerous(cp)
            if is_dangerous:
                try:
                    name = unicodedata.name(char)
                except ValueError:
                    name = "<unnamed>"
                findings.append(
                    Finding(
                        path=path,
                        line=line_no,
                        column=col_no + 1,
                        codepoint=cp,
                        char=char,
                        name=name,
                        hex_repr=f"U+{cp:04X}" if cp <= 0xFFFF else f"U+{cp:05X}",
                        category=reason,
                        unicode_category=unicodedata.category(char),
                    )
                )

    return findings


def scan_file(filepath: str | Path) -> list[Finding]:
    """Scan a file for dangerous Unicode characters.

    Skips binary files (decode errors). Returns list of findings.
    """
    path = Path(filepath)
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    return scan_content(content, path=str(path))


def scan_files(filepaths: list[str | Path]) -> list[Finding]:
    """Scan multiple files and return combined findings."""
    all_findings: list[Finding] = []
    for fp in filepaths:
        all_findings.extend(scan_file(fp))
    return all_findings
