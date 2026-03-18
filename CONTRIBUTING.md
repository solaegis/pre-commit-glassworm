# Contributing

Thanks for your interest in contributing to pre-commit-glassworm!

## Setup

```bash
git clone https://github.com/solaegis/pre-commit-glassworm
cd pre-commit-glassworm
uv sync
pre-commit install
pre-commit install --hook-type commit-msg
```

## Development workflow

```bash
task test    # run tests
task lint   # run ruff check
task format # run ruff format
task docs   # serve docs locally
```

## Commit messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/) via Commitizen:

```bash
uv run cz commit
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.

## Pull requests

1. Fork the repo and create a feature branch
2. Write tests for new functionality
3. Ensure `task test` and `task lint` pass
4. Use conventional commit messages
5. Open a PR against `main`

## Adding detection patterns

New dangerous Unicode ranges go in `src/glassworm/scanner.py`:

- Add to `_DANGEROUS_RANGES` (for ranges) or `_DANGEROUS_SINGLES` (for individual codepoints)
- Add a test in `tests/test_scanner.py`
- Add a fixture file in `tests/fixtures/` if applicable
- Document in `docs/detection.md`

## Reporting false positives

If glassworm flags a character that's legitimate in your use case, please open an issue with:

- The file type and context
- The codepoint(s) flagged
- Why the character is intentional
