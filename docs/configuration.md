# Configuration

Config is optional. Defaults work for most projects.

## Config file locations

Config is loaded (in order, later overrides earlier):

1. Defaults
2. `.glassworm.toml` (searched upward from CWD)
3. `[tool.glassworm]` in `pyproject.toml`

## Options

### `severity`

Control exit behavior when findings are present.

| Value | Behavior |
|-------|----------|
| `error` | Exit 1 — blocks commit / CI |
| `warning` | Exit 0 — prints warning, allows commit |

```toml
[tool.glassworm]
severity = "error"
```

### `include`

Glob patterns for files to scan. Defaults:

```toml
[tool.glassworm]
include = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.json", "*.yaml", "*.yml", "*.md", "*.txt", "*.sh", "*.bash", "*.html", "*.css", "*.xml", "*.toml", "*.ini", "*.cfg", "*.env*"]
```

### `exclude`

Glob patterns for paths to skip. Defaults:

```toml
[tool.glassworm]
exclude = ["vendor/", "node_modules/", "*.min.js"]
```

## Example: `.glassworm.toml`

```toml
[tool.glassworm]
severity = "warning"
exclude = ["vendor/", "node_modules/", "*.min.js", "dist/", "build/"]
```

## Example: `pyproject.toml`

```toml
[tool.glassworm]
severity = "error"
include = ["*.py", "*.js", "*.ts", "*.json", "*.md"]
exclude = ["vendor/", "node_modules/", "*.min.js", "docs/"]
```

## CLI override

`--severity` overrides config:

```bash
glassworm --severity warning .    # Always warn, never block
glassworm --severity error .      # Always block on findings
```

### `--config`

`--config` locates the config root; it does not read a single file. Behavior:

- **File path** (e.g. `--config /project/pyproject.toml`): Uses the **parent directory** as the config root, then loads both `.glassworm.toml` and `pyproject.toml` from that directory (whichever exist).
- **Directory path** (e.g. `--config /project`): Uses that directory directly as the config root.

```bash
glassworm --config . src/                     # Current dir as config root
glassworm --config /project/.glassworm.toml src/   # /project as config root
```
