# What It Detects

pre-commit-glassworm flags Unicode characters that are invisible or visually deceptive and can be used in supply-chain attacks.

## Detection categories

### Variation Selectors (U+FE00–U+FE0F)

**GlassWorm primary technique.** These characters are typically invisible in code editors and can hide malicious logic by "attaching" to a visible character.

| Codepoint | Name |
|-----------|------|
| U+FE00 | VARIATION SELECTOR-1 |
| … | … |
| U+FE0F | VARIATION SELECTOR-16 |

### Variation Selectors Supplement (U+E0100–U+E01EF)

Extended variation selectors; same risk as above.

### Bidirectional control (Trojan Source)

**CVE-2021-42574.** These characters reverse or override the logical order of text, so code can appear to say one thing while executing another.

| Codepoint | Name |
|-----------|------|
| U+202A | LEFT-TO-RIGHT EMBEDDING (LRE) |
| U+202B | RIGHT-TO-LEFT EMBEDDING (RLE) |
| U+202C | POP DIRECTIONAL FORMATTING (PDF) |
| U+202D | LEFT-TO-RIGHT OVERRIDE (LRO) |
| U+202E | RIGHT-TO-LEFT OVERRIDE (RLO) |
| U+2066 | LEFT-TO-RIGHT ISOLATE (LRI) |
| U+2067 | RIGHT-TO-LEFT ISOLATE (RLI) |
| U+2068 | FIRST STRONG ISOLATE (FSI) |
| U+2069 | POP DIRECTIONAL ISOLATE (PDI) |

### Zero-width and invisible

| Codepoint | Name |
|-----------|------|
| U+200B | ZERO WIDTH SPACE |
| U+200C | ZERO WIDTH NON-JOINER |
| U+200D | ZERO WIDTH JOINER |
| U+200E | LEFT-TO-RIGHT MARK |
| U+200F | RIGHT-TO-LEFT MARK |
| U+2060 | WORD JOINER |
| U+2061 | FUNCTION APPLICATION |
| U+2062 | INVISIBLE TIMES |
| U+2063 | INVISIBLE SEPARATOR |
| U+2064 | INVISIBLE PLUS |
| U+180E | MONGOLIAN VOWEL SEPARATOR |

### BOM mid-file (U+FEFF)

The byte order mark (BOM) is valid at the start of a UTF-8 file and is **not flagged** at line 1, column 1. When it appears **anywhere else** in a file, it may indicate corruption or manipulation and is flagged.

### Replacement character (U+FFFD)

Used when decoding fails. Its presence in scanned content suggests unsafe or corrupted decoding.

### Other Format characters (Cf)

Any character with `unicodedata.category(c) == "Cf"` not already covered above is flagged as a catch-all for invisible format characters.

## Out of scope

The following are **not** detected (by design):

- **Homoglyphs / confusables** — e.g. Cyrillic `а` vs Latin `a`. Complex, many false positives in i18n.
- **Auto-fix** — Dangerous characters require manual review per security guidance.
- **Binary analysis** — Only text files are scanned.

## File types scanned

By default, the scanner runs on common source and config files:

`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.json`, `.yaml`, `.yml`, `.md`, `.txt`, `.sh`, `.bash`, `.html`, `.css`, `.xml`, `.toml`, `.ini`, `.cfg`, `.env*`

Binary files are skipped (UTF-8 decode failure or null bytes).

Customize via `[tool.glassworm]` `include` and `exclude` — see [Configuration](configuration.md).
