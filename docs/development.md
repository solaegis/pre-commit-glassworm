# Development

## Setup

```bash
git clone https://github.com/solaegis/pre-commit-glassworm
cd pre-commit-glassworm
uv sync
pre-commit install
pre-commit install --hook-type commit-msg
```

## Tasks (Taskfile)

| Task | Description |
|------|-------------|
| `task test` | Run pytest |
| `task lint` | Run ruff check |
| `task format` | Run ruff format |
| `task docs` | Serve MkDocs locally (http://localhost:8000) |
| `task docs:build` | Build MkDocs site to `site/` |
| `task bump` | Bump version via commitizen (from last commit) |
| `task bump:patch` | Force patch bump |
| `task bump:minor` | Force minor bump |
| `task bump:major` | Force major bump |
| `task tag` | Create annotated git tag from pyproject.toml version |
| `task build` | Build sdist + wheel to `dist/` |
| `task publish` | Build + publish to PyPI |
| `task release:check` | Lint, format check, and test (run before release) |
| `task release` | Release (infer bump) — check, bump, tag, publish |
| `task release:patch` | Release patch (0.0.X) |
| `task release:minor` | Release minor (0.X.0) |
| `task release:major` | Release major (X.0.0) |
| `task release:push` | Push commits and tags to origin |
| `task release:gh` | Create GitHub release (requires gh CLI) |

## Project structure

```
pre-commit-glassworm/
├── src/glassworm/
│   ├── __init__.py
│   ├── __main__.py    # python -m glassworm
│   ├── cli.py         # run() → int, main() → sys.exit
│   ├── config.py
│   ├── scanner.py
│   └── py.typed       # PEP 561 marker
├── tests/
│   ├── fixtures/      # Sample files with/without dangerous chars
│   ├── test_cli.py    # Unit (run()) + integration (subprocess)
│   ├── test_config.py
│   └── test_scanner.py
├── docs/
├── mkdocs.yaml
├── pyproject.toml
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Tests

```bash
uv run pytest -v
uv run pytest -v --cov=glassworm --cov-report=term-missing
```

Tests are split into unit tests (calling `run()` directly for speed and coverage) and integration tests (subprocess for entrypoint validation).

Fixtures in `tests/fixtures/` contain real dangerous Unicode (U+FE00, U+202E, U+200B, etc.). They were created programmatically to avoid escape-sequence confusion.

## Linting

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Ruff rules: E, F, I, N, W, UP, B (bugbear), S (bandit), SIM, PTH, RUF.

## Commitizen

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for Conventional Commits:

```bash
pre-commit install --hook-type commit-msg
uv run cz commit   # or  cz c
```

## Version bump

```bash
task bump          # infer from conventional commits since last tag
task bump:patch    # 0.0.X
task bump:minor    # 0.X.0
task bump:major    # X.0.0
```

## Release process

Full flow: **lint → test → bump (commit) → tag → publish → push → GitHub release**.

1. **Commit your work** with conventional commits (`fix:`, `feat:`, etc.).
2. **Run a release task** (runs lint, format check, test, bump, tag, publish):

   ```bash
   task release          # infer bump from commits since last tag
   task release:patch    # force 0.0.X
   task release:minor    # force 0.X.0
   task release:major    # force X.0.0
   ```

3. **Push** commits and tags:

   ```bash
   task release:push
   ```

4. **Create GitHub release** (optional):

   ```bash
   task release:gh       # requires gh CLI; uses --generate-notes
   ```

**Prerequisites**: `UV_PUBLISH_TOKEN` in `.env` for PyPI; `gh auth login` for GitHub releases.
