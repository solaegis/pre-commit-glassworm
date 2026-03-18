# pre-commit-glassworm

[![CI](https://github.com/solaegis/pre-commit-glassworm/actions/workflows/ci.yaml/badge.svg)](https://github.com/solaegis/pre-commit-glassworm/actions/workflows/ci.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![PyPI](https://img.shields.io/pypi/v/pre-commit-glassworm)](https://pypi.org/project/pre-commit-glassworm/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pre-commit hook that detects [GlassWorm](https://coesecurity.com/glassworm-invisible-code-visible-damage/)‑style supply-chain attacks: invisible Unicode characters, variation selectors, Trojan Source (CVE-2021-42574), and zero-width characters that can hide malicious code from reviewers and many automated scanners.

## What it catches

- **Variation Selectors** (U+FE00–U+FE0F) – GlassWorm primary technique
- **Variation Selectors Supplement** (U+E0100–U+E01EF)
- **Bidi control** (U+202A–202E, U+2066–2069) – Trojan Source
- **Zero-width** (U+200B–200F, U+2060–2064, U+180E)
- **BOM mid-file** (U+FEFF) – valid at file start, flagged elsewhere
- **Replacement character** (U+FFFD)
- **Other format characters** (Cf category)

## Installation

### As a pre-commit hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/solaegis/pre-commit-glassworm
    rev: v0.1.0  # pin to tag for reproducible installs
    hooks:
      - id: glassworm
```

Then:

```bash
pre-commit install
```

### Standalone

```bash
uv add pre-commit-glassworm
# or: pip install pre-commit-glassworm

glassworm path/to/file.py path/to/other.js
glassworm src/                              # scan directory recursively
cat file.py | glassworm                     # read from stdin
```

## Configuration

Optional config in `pyproject.toml` or `.glassworm.toml`:

```toml
[tool.glassworm]
severity = "error"   # "error" | "warning"
```

- `severity=error` – exit 1 on findings (blocks commit)
- `severity=warning` – exit 0, prints warning (allows commit)

## CLI options

```
glassworm [OPTIONS] [FILES...]
```

| Flag | Description |
|------|-------------|
| `--severity` | Override: `error` or `warning` |
| `--config` | Path to config file |
| `--format` | Output format: `text` (default) or `json` |
| `-v, --verbose` | Per-file summary |
| `-q, --quiet` | Summary only |
| `--version` | Show version and exit |

## JSON output

For CI/SARIF integration:

```bash
glassworm --format json src/
```

Returns a JSON array of finding objects with `path`, `line`, `column`, `codepoint`, `hex_repr`, `name`, `category`, and `unicode_category`.

## CI integration

```bash
pre-commit run --all-files
```

## Commitizen and version bump

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for Conventional Commits:

```bash
pre-commit install --hook-type commit-msg
```

Version bump via Taskfile:

```bash
task bump          # infer from conventional commits since last tag
task bump:patch    # force patch (0.0.X)
task bump:minor    # force minor (0.X.0)
task bump:major    # force major (X.0.0)
```

## Publishing to PyPI

```bash
# 1. Create .env with your PyPI token:
#    UV_PUBLISH_TOKEN=pypi-...

# 2. Or copy from example:
cp .env.example .env
#    Edit .env and add your token

# 3. Build and publish
task publish
```

`.env` is gitignored. `task publish` loads it automatically.

## License

MIT – see [LICENSE](LICENSE).
