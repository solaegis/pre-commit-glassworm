# pre-commit-glassworm

A [pre-commit](https://pre-commit.com/) hook that detects **GlassWorm-style supply-chain attacks**: invisible Unicode characters, variation selectors, Trojan Source ([CVE-2021-42574](https://nvd.nist.gov/vuln/detail/CVE-2021-42574)), and zero-width characters that can hide malicious code from reviewers and many automated scanners.

## Why This Matters

Attackers can embed invisible Unicode characters in source code to:

- **Hide malicious logic** behind seemingly innocuous lines
- **Bypass human code review** by making harmful code invisible or reordered
- **Evade static analysis tools** that don't inspect raw Unicode

[GlassWorm](https://coesecurity.com/glassworm-invisible-code-visible-damage/) and Trojan Source are real-world examples. This hook catches those techniques before code enters your repository.

## What It Catches

| Category | Unicode Range | Description |
|----------|---------------|-------------|
| **Variation Selectors** | U+FE00–U+FE0F | GlassWorm primary technique; invisible in most editors |
| **Variation Selectors Supplement** | U+E0100–U+E01EF | Extended variation selectors |
| **Bidi control** (Trojan Source) | U+202A–202E, U+2066–2069 | Reverses logical order (CVE-2021-42574) |
| **Zero-width** | U+200B–200F, U+2060–2064, U+180E | Invisible joiner/space/non-joiner |
| **BOM mid-file** | U+FEFF | Byte order mark outside start of file (valid at line 1, col 1) |
| **Replacement char** | U+FFFD | Indicates corrupted/unsafe decoding |
| **Other Cf (format)** | `unicodedata.category == "Cf"` | Additional invisible format characters |

## Quick Start

### As a pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/solaegis/pre-commit-glassworm
    rev: v0.1.0
    hooks:
      - id: glassworm
```

```bash
pre-commit install
```

### Standalone CLI

```bash
uv add pre-commit-glassworm

# Scan files
glassworm path/to/file.py path/to/other.js

# Scan a directory recursively
glassworm src/

# JSON output for CI integration
glassworm --format json src/
```

## Exit Behavior

- **`severity=error`** (default): Exit 1 on findings → blocks commit
- **`severity=warning`**: Exit 0, prints warning → allows commit

## Next Steps

- [Installation](installation.md) — Install via pre-commit or standalone
- [Configuration](configuration.md) — `[tool.glassworm]` options
- [CLI Reference](cli.md) — All command-line options
