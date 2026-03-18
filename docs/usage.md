# Quick Start

## Pre-commit workflow

1. Add the hook to `.pre-commit-config.yaml` (see [Installation](installation.md)).
2. Run `pre-commit install`.
3. Commit as usual. The hook runs on staged files automatically.

If dangerous Unicode is found, the commit is blocked and findings are printed:

```
tests/fixtures/variation_selector.py:1:5: U+FE00 VARIATION SELECTOR-1 [variation selector (GlassWorm)]
```

Fix or remove the problematic characters, then try again.

## CLI usage

### Scan specific files

```bash
glassworm src/main.py src/utils.js
```

### Scan a directory

```bash
glassworm src/
```

Directories are scanned recursively. Hidden files (starting with `.`) are skipped.

### Read from stdin

```bash
cat script.py | glassworm
```

### Override severity

```bash
glassworm --severity warning .   # Warn but don't exit 1
glassworm --severity error .    # Block on findings (default)
```

### JSON output

```bash
glassworm --format json src/
```

Returns a JSON array of finding objects — useful for CI pipelines, SARIF integration, or custom tooling:

```json
[
  {
    "path": "src/main.py",
    "line": 5,
    "column": 12,
    "codepoint": 65024,
    "name": "VARIATION SELECTOR-1",
    "hex_repr": "U+FE00",
    "category": "variation selector (GlassWorm)",
    "unicode_category": "Mn"
  }
]
```

### Verbose mode

```bash
glassworm -v src/   # Per-file summary
```

### Quiet mode

```bash
glassworm -q src/   # Suppresses per-finding lines, still prints summary count
```

### Version

```bash
glassworm --version
```

## Integration with other tools

### With ruff, black, etc.

Add glassworm alongside your existing hooks:

```yaml
repos:
  - repo: https://github.com/solaegis/pre-commit-glassworm
    rev: v0.1.0
    hooks:
      - id: glassworm

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.0
    hooks:
      - id: ruff
```

### With Commitizen

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for conventional commits. Install the commit-msg hook:

```bash
pre-commit install --hook-type commit-msg
```
