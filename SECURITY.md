# Security Policy

## Supported Versions

The following versions of VDE are currently receiving security updates:

| Version | Supported          |
|---------|--------------------|
| main    | :white_check_mark: Yes |

For production deployments, we recommend using the latest stable release from the main branch.

## Reporting a Vulnerability

If you discover a security vulnerability in VDE, please report it responsibly.

### How to Report

**Do NOT** open a public issue for security vulnerabilities.

Instead, please send an email to:

- **Email**: 133974812+dderyldowney@users.noreply.github.com
- **PGP Key**: [Available on keyserver] (optional - add if you have one)

### What to Include

Please include as much of the following information as possible:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Proof-of-concept or exploit code (if applicable)
- Suggested mitigation or fix (if known)

### Response Timeline

- **Initial response**: Within 48 hours
- **Detailed response**: Within 7 days
- **Patch release**: As soon as feasible, based on severity

### Expected Process

1. **Confirmation**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate the issue and determine severity
3. **Coordination**: We will work with you on a timeline for disclosure
4. **Fix Development**: We will develop a patch for the vulnerability
5. **Release**: We will release the fix and coordinate public disclosure

### Coordination

We appreciate coordinated disclosure and will work with you to determine an appropriate timeline for publishing the vulnerability information. Our goal is to protect users while recognizing your contribution.

## Security Best Practices for Users

### SSH Key Management

- Use strong SSH keys (ed25519 or RSA 4096+)
- Protect private keys with strong passphrases
- Rotate SSH keys periodically
- Never commit private keys to repositories

### Container Security

- Keep Docker images updated
- Use `--rebuild` when pulling updated base images
- Review Dockerfiles before building
- Run containers as non-root users (VDE uses `devuser`)

### Network Exposure

- SSH ports are exposed on localhost only by default
- Be cautious when modifying port bindings
- Use firewall rules to restrict access if needed
- Consider using VPNs or SSH bastion hosts for remote access

### Environment Variables

- Never commit `.env` files or secrets to repositories
- Use `env-files/` directory for environment-specific configuration
- Review `env-files/` before sharing configurations
- Be cautious with API keys and credentials

## Security Features

VDE includes several security features by design:

- **Non-root user**: All containers run as `devuser` with passwordless sudo
- **SSH key authentication**: Password authentication disabled
- **Isolated environments**: Each VM runs in separate containers
- **Isolated network**: All containers run on a dedicated `vde-net` Docker bridge network with automatic drift correction
- **Persistent data**: Data volumes separated from containers
- **Strict directory permissions**: Sensitive directories (`data/`, `logs/`, `.cache/`, `.locks/`, `.docker-state/`, `env-files/`) are set to `0700`; credential files (`*.env`, SSH keys, SSH config) are set to `0600`
- **SSH isolation**: All VDE SSH assets (`~/.ssh/vde/`) are isolated from the user's personal SSH configuration
- **Unified naming**: All containers and SSH aliases use the `vde-` prefix for clear identification

### Automated Security Enforcement (`vde-security` library)

VDE includes a dedicated security library ([`scripts/lib/vde-security`](scripts/lib/vde-security)) that
automatically enforces security policies at startup. It is invoked by `vde-init`,
`ensure_vde_ssh_environment`, and `build-and-start`.

**Directory and File Permissions:**

| Path | Mode | Rationale |
|------|------|-----------|
| `.cache/`, `.docker-state/`, `.locks/` | `0700` | Internal state — owner only |
| `data/`, `logs/` | `0700` | Service data and logs — owner only |
| `env-files/` | `0700` | May contain credentials |
| `env-files/*.env` | `0600` | Credential files — owner read/write only |
| `~/.ssh/vde/` | `0700` | SSH directory — owner only |
| SSH identity, config, known_hosts | `0600` | SSH files — owner read/write only |
| `scripts/` and script files | `0755` | Must be executable |

**Network Isolation:**

```zsh
# vde_security_ensure_network creates the network if absent:
docker network create --driver bridge --label "vde.managed=true" vde-net

# vde_security_enforce_network_isolation re-attaches drifted containers:
docker network connect vde-net <container>
```

**SSH Isolation (`~/.ssh/vde/`):**

All VDE SSH assets are stored in `~/.ssh/vde/` — completely separate from the
user's personal `~/.ssh/`. This means:
- VDE SSH operations never modify the user's `~/.ssh/config` or `~/.ssh/known_hosts`
- Revoking all VDE SSH access requires only deleting `~/.ssh/vde/`
- VDE container host keys are tracked in `~/.ssh/vde/known_hosts` only

## Vulnerability Severity Classification

We classify vulnerabilities using the following severity levels:

| Severity | Description                           | Response Time |
|----------|---------------------------------------|---------------|
| Critical | Remote code execution, data breach    | 48 hours      |
| High     | Privilege escalation, data exposure   | 7 days        |
| Medium   | Local exploit, minor data leak        | 30 days       |
| Low      | Information disclosure, edge cases    | 90 days       |

## Security Audits

VDE has not undergone a formal security audit. We welcome security researchers to review the codebase and report any vulnerabilities they discover.

## Dependency Security

VDE relies on several third-party dependencies:

- **Docker**: Container runtime
- **Base images**: Official language images (python, rust, node, etc.)
- **System packages**: Installed via apt/apk in containers

Users should:
- Keep Docker updated
- Regularly rebuild containers with `--rebuild`
- Monitor security advisories for base images

## Disclosure Policy

### Security Advisories

When security vulnerabilities are fixed, we will:

1. Publish a GitHub Security Advisory
2. Include details of the vulnerability
3. Credit the reporter (if desired)
4. Provide upgrade instructions
5. Assign CVE numbers when appropriate

### Public Disclosure

We will publicly disclose vulnerabilities:

- After a fix is released
- Coordinated with the reporter
- In accordance with responsible disclosure practices

## Security Contact Information

For general security questions or concerns:

- **Email**: 133974812+dderyldowney@users.noreply.github.com
- **GitHub Security**: Use the "Report a vulnerability" button on this repository

## Acknowledgments

We thank all security researchers who help keep VDE secure by reporting vulnerabilities responsibly.

---

**Remember**: If you discover a security vulnerability, please report it privately rather than opening a public issue.
