# Security Policy - Paryavaran Carbon Footprint Tracker

We take the security of Paryavaran seriously. If you believe you have found a security vulnerability, please report it to us responsibly as detailed below.

## Supported Versions

Only the latest release (and active development branch) receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please do not report security vulnerabilities via public GitHub issues. Instead, report them by emailing the lead maintainers at security@paryavaran-tracker.org (mock contact).

Your report should include:
- A description of the vulnerability, including severity.
- Detailed steps to reproduce (or a proof-of-concept script).
- Potential impact of the vulnerability.

We will acknowledge receipt of your vulnerability report within 48 hours and work with you to coordinate a security patch and public advisory.

## Security Controls Implemented

Paryavaran is designed with high security standards:
- **No Hardcoded Secrets**: Configuration is managed strictly via environment variables.
- **Input Validation**: All APIs use Pydantic for schema-based type-safe validation.
- **Secure Authentication**: User passwords are encrypted using `bcrypt` and authenticated using JWT tokens.
- **Dependency Pinning**: All third-party libraries are pinned to prevent supply chain vulnerabilities.
- **Safe Database Interaction**: SQL injections are prevented by using SQLAlchemy's parameterized queries/ORM models.
