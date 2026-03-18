# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `--format json` flag for machine-readable output
- `--version` flag
- Directory scanning support (recursive)
- `Finding.to_dict()` and `Finding.to_json()` serialisation methods
- `unicode_category` field on `Finding` (raw Unicode category like `Cf`, `Mn`)
- BOM-at-file-start exemption (U+FEFF at line 1, col 1 is a valid UTF-8 BOM)
- `py.typed` marker for PEP 561 typing support
- `LICENSE` file (MIT)
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- CI workflow for tests and linting across Python 3.11–3.13
- Config test suite (`test_config.py`)

### Changed
- `Finding.category` now holds the human-readable reason (e.g. "variation selector (GlassWorm)") instead of the raw Unicode category
- `--quiet` flag now suppresses per-finding lines but still shows the summary count on stderr
- `cli.main()` refactored to `cli.run()` returning an exit code; `main()` is a thin wrapper
- Scanner uses a declarative lookup table instead of chained if/elif
- `Finding` dataclass is now `frozen=True, slots=True`
- Expanded ruff lint rules: added B, S, SIM, PTH, RUF
- Removed dead `tomli` fallback (Python ≥3.11 guarantees `tomllib`)
- Removed unused scanner constants (`_ZERO_WIDTH_JOINER`, etc.)

### Fixed
- `--quiet` no longer suppresses the summary line
- BOM at file start no longer triggers a false positive
- Passing a directory no longer silently skips it

## [0.1.0] - 2025-01-01

### Added
- Initial release
- Variation selector detection (U+FE00–FE0F, U+E0100–E01EF)
- Bidi control detection (Trojan Source CVE-2021-42574)
- Zero-width character detection
- BOM mid-file detection
- Replacement character detection
- Format character (Cf) catch-all
- Pre-commit hook integration
- Standalone CLI with `--severity`, `--config`, `-v`, `-q`
- Configuration via `pyproject.toml` or `.glassworm.toml`
- MkDocs documentation site
