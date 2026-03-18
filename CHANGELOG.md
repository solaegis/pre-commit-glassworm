# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).


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

## v0.1.0 (2026-03-18)
