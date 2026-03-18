# Security Policy

## Supported Versions

Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in pre-commit-glassworm, please report it responsibly.

**How to report:**

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Email the maintainers or open a private security advisory on GitHub:
   - GitHub: [Security Advisories](https://github.com/solaegis/pre-commit-glassworm/security/advisories/new)
3. Include:
   - A description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested remediation

**What to expect:**

- We will acknowledge receipt within 48 hours.
- We will provide an initial assessment within 5 business days.
- We will keep you informed of progress and coordinate any public disclosure.
- We credit reporters (with their permission) when we fix verified vulnerabilities.

## Security Considerations

pre-commit-glassworm scans files for invisible Unicode characters. It:

- Reads file contents but does not modify them
- Uses no runtime dependencies (stdlib only for core functionality)
- Loads configuration from TOML via `tomllib` (no `eval` or unsafe parsing)
- Accepts file paths from the user; path traversal is not applicable (user controls input)

If you have questions about security, please open a regular issue or contact the maintainers.
