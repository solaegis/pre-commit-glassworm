"""Command-line interface for glassworm."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

from glassworm import __version__
from glassworm.config import get_default_config, load_config
from glassworm.scanner import Finding, scan_content, scan_file


def _matches_include(path: Path, patterns: list[str]) -> bool:
    """Return True if path (filename) matches any include pattern."""
    name = path.name
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def _matches_exclude(path: Path, patterns: list[str]) -> bool:
    """Return True if path should be excluded."""
    name = path.name
    parts = path.parts
    for pat in patterns:
        if pat.endswith("/"):
            # Directory pattern: exclude if path contains this directory
            dirname = pat.rstrip("/")
            if dirname in parts:
                return True
        elif fnmatch.fnmatch(name, pat):
            return True
    return False


def _collect_files(
    paths: list[Path],
    *,
    config: dict,
    verbose: bool = False,
) -> list[Path]:
    """Expand directories to individual files, recursively, applying include/exclude.

    For explicit file paths (from user or pre-commit), only exclude is applied.
    For directory recursion, both include and exclude are applied.
    """
    include = config.get("include", [])
    exclude = config.get("exclude", [])
    collected: list[Path] = []

    for p in paths:
        if not p.exists():
            if verbose:
                print(f"glassworm: skipped (not found): {p}", file=sys.stderr)
            continue
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if not f.is_file() or f.name.startswith("."):
                    continue
                if _matches_exclude(f, exclude):
                    continue
                if not _matches_include(f, include):
                    continue
                collected.append(f)
        else:
            # Explicit file path: apply exclude (so pre-commit skips fixtures)
            if _matches_exclude(p, exclude):
                continue
            collected.append(p)
    return collected


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="glassworm",
        description="Detect GlassWorm-style invisible Unicode attacks in source files.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Files or directories to scan (default: read from stdin)",
    )
    parser.add_argument(
        "--severity",
        choices=("error", "warning"),
        default=None,
        help="Override config: error=exit 1 on findings, warning=exit 0",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config file (pyproject.toml or .glassworm.toml)",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Use defaults only, ignore project config (for testing)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show per-file summary",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Summary only, no per-finding output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Run the glassworm CLI and return an exit code.

    Parameters
    ----------
    argv:
        Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        0 if no findings or severity is ``warning``, 1 if findings with
        severity ``error``.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = get_default_config() if args.no_config else load_config(args.config)
    severity = args.severity or config.get("severity", "error")

    files = args.files
    if not files:
        # Pre-commit passes filenames; if none, read content from stdin and scan it
        content = sys.stdin.read()
        all_findings = scan_content(content, path="(stdin)")
    else:
        file_list = _collect_files(files, config=config, verbose=args.verbose)
        all_findings: list[Finding] = []
        for path in file_list:
            findings = scan_file(path)
            all_findings.extend(findings)

    # --- Output ---------------------------------------------------------
    if args.output_format == "json":
        json.dump([f.to_dict() for f in all_findings], sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        if all_findings and not args.quiet:
            for f in all_findings:
                print(f"{f.path}:{f.line}:{f.column}: {f.hex_repr} {f.name} [{f.category}]")

        # Summary always prints to stderr when there are findings
        if all_findings:
            affected = len({f.path for f in all_findings})
            print(
                f"\nFound {len(all_findings)} dangerous character(s) in {affected} file(s)",
                file=sys.stderr,
            )

    if all_findings and severity == "error":
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    """Entry point — calls :func:`run` and exits."""
    sys.exit(run(argv))
