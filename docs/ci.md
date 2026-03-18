# CI Integration

## pre-commit / prek in CI

Run the hook on the entire repo in CI:

```bash
pre-commit run --all-files
```

If you use [prek](https://prek.j178.dev/) instead of pre-commit, use `prek run --all-files` instead. Both tools use the same configuration.

This runs every configured hook (including glassworm) on all tracked files. Use it in your GitHub Actions, GitLab CI, or other pipelines.

## Example: GitHub Actions

```yaml
# .github/workflows/pre-commit.yaml
name: pre-commit

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit
        run: pre-commit run --all-files
```

## Example: GitLab CI

```yaml
# .gitlab-ci.yaml
pre-commit:
  image: python:3.11
  script:
    - pip install pre-commit
    - pre-commit run --all-files
```

## Example: standalone glassworm in CI

If you want **only** glassworm (not other pre-commit hooks) in CI:

```yaml
- name: Install glassworm
  run: pip install pre-commit-glassworm

- name: Scan for dangerous Unicode
  run: glassworm .
```

## Updating the hook

To update the hook version in `.pre-commit-config.yaml`:

```bash
pre-commit autoupdate
```

Review the diff before committing; newer versions may change behavior.
