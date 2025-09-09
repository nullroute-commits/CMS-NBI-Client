# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

To report a security vulnerability, please email security@example.com with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within 48 hours and will work on a fix as soon as possible.

## Security Practices

### GitHub Actions

All GitHub Actions in this repository are pinned to specific commit SHAs rather than version tags. This practice ensures:

1. **Immutability**: Actions cannot be changed without updating our workflows
2. **Security**: Protection against supply chain attacks
3. **Reproducibility**: Workflows always use the exact same action code

Example:
```yaml
# Good - SHA pinned
- uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744 # v3.6.0

# Avoid - Version tag
- uses: actions/checkout@v3
```

### Dependency Management

- Dependencies are managed through Poetry with locked versions
- Dependabot monitors for security updates
- All Docker base images use specific digests
- Security scanning is performed in CI/CD pipeline

### Docker Security

- Alpine Linux base images for minimal attack surface
- Non-root user execution
- No unnecessary packages installed
- Regular vulnerability scanning with Trivy

### Code Security

- Pre-commit hooks include security checks (bandit)
- Type checking with mypy
- XML parsing uses defusedxml
- Credentials stored securely using system keyring
- HTTPS connections with certificate validation

## Security Updates

Security updates are released as patch versions and announced through:
- GitHub Security Advisories
- Release notes
- PyPI package updates

Users are encouraged to update to the latest patch version as soon as possible.