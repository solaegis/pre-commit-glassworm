# Installation

## Option 1: Pre-commit hook (recommended)

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/solaegis/pre-commit-glassworm
    rev: v0.1.0  # pin to tag for reproducible installs
    hooks:
      - id: glassworm
```

Then install the hook:

```bash
pre-commit install
```

The hook runs automatically when you commit. It only scans **staged files**, so it stays fast.

### Try before installing

Test the hook on your repo without installing:

```bash
pre-commit try-repo . glassworm --all-files
```

## Option 2: Standalone CLI

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv add pre-commit-glassworm
```

Or with pip:

```bash
pip install pre-commit-glassworm
```

Then run:

```bash
glassworm path/to/file.py path/to/dir/
```

Or pipe from stdin:

```bash
cat somefile.js | glassworm
```

## Option 3: Dev dependency only

For projects that want the CLI but not the pre-commit hook:

```bash
uv add --dev pre-commit-glassworm
```

## Requirements

- Python 3.11+
- [pre-commit](https://pre-commit.com/) (if using the hook)
