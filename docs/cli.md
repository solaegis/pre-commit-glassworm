# CLI Reference

## Synopsis

```
glassworm [OPTIONS] [FILES...]
```

If no files are given, reads from stdin. Directories are scanned recursively.

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--severity` | | Override config: `error` or `warning` |
| `--config` | | Path to config file or directory (locates project root for `.glassworm.toml` / `pyproject.toml`) |
| `--format` | | Output format: `text` (default) or `json` |
| `--verbose` | `-v` | Per-file summary |
| `--quiet` | `-q` | Summary only, minimal output |
| `--version` | | Show version and exit |
| `--help` | `-h` | Show help and exit |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | No findings, or `severity=warning` with findings |
| 1 | Findings with `severity=error` (default) |
| 2 | Invalid usage (argparse errors) |

## Examples

### Scan specific files

```bash
glassworm src/main.py tests/test_foo.py
```

### Scan directory

```bash
glassworm src/
```

### Stdin (pre-commit compatible)

```bash
cat script.py | glassworm
```

When pre-commit runs the hook, it passes filenames as arguments. When no args are given, the CLI reads stdin so `glassworm` can be used in pipe chains.

### JSON output

```bash
glassworm --format json src/
```

Returns a JSON array of finding objects for CI integration:

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

### Force warning mode

```bash
glassworm --severity warning .   # Never block, just warn
```

### Custom config

```bash
glassworm --config project/.glassworm.toml project/
```

The `--config` path identifies the project root (or pass a directory directly). Glassworm loads both `.glassworm.toml` and `pyproject.toml` from that directory; the given path itself is not read.

### Verbose output

```bash
glassworm -v src/
# Prints per-file summaries
```

### Quiet output

```bash
glassworm -q src/
# Suppresses per-finding lines, still prints summary count
```
