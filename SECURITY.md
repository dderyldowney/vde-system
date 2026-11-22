# SECURITY
<!-- @shared-law (Security Policy Documentation) -->

## Sovereign Baseline: 1.5.7

This is the security policy of the **Virtualized Development Environment (VDE)**: which versions are supported, how to report a vulnerability, what happens after you report it, and how fixes are announced. The maintainers' full procedure is in [`docs/governance/security-process.md`](docs/governance/security-process.md).

---

## Supported Versions

Security fixes are made for the latest release only. There are no backports to older releases: the fix for an older version is to upgrade (`vde upgrade`).

| Version | Supported | Notes |
|---------|-----------|-------|
| 1.5.7 | ✅ Yes | Latest release (2026-11-21; on `stable` and `main`) |
| Older than 1.5.7 | ❌ No | Upgrade to the latest release |
| `stable` branch | ✅ Yes | Always the latest release plus pending stable updates |
| `develop` branch | ⚠️ Development | Integration branch, not for production; reports about it are still welcome |

To install the supported version:
```zsh
git clone -b stable https://github.com/dderyldowney/vde-system.git VDE
```

---

## Reporting a Vulnerability

**Do NOT open a public issue, pull request or discussion for a security vulnerability.**

Report it privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**, or go directly to <https://github.com/dderyldowney/vde-system/security/advisories/new>. Only the maintainer and you can see the report.

Please include:

- What the problem is and which component it affects
- Steps to reproduce (the VDE version or commit, your OS and Docker version)
- What an attacker could do with it
- A proof of concept, if you have one
- A suggested fix, if you have one

---

## Response Targets

VDE is maintained by one person, so these targets are realistic rather than aggressive. Times are counted from the report (acknowledgement, triage) or from triage (fix).

| Step | Target |
|------|--------|
| Acknowledge your report | 3 business days |
| Triage (reproduce, decide, score) | 7 days |
| Fix a **Critical** vulnerability | 7 days, shipped as its own patch release |
| Fix a **High** vulnerability | 30 days |
| Fix a **Medium** vulnerability | 90 days |
| Fix a **Low** vulnerability | The next planned release |

Severity is scored with CVSS v4.0 and confirmed by the maintainer. You will hear back at each step, including when a target slips and why.

---

## Coordinated Disclosure

VDE follows coordinated disclosure (ISO/IEC 29147 and 30111, and the OpenSSF guide for open-source projects):

1. Your report becomes a private draft GitHub Security Advisory. The details stay there.
2. The fix is developed privately, in the advisory's temporary private fork. Until the fix ships, the only public trace is a neutrally worded tracking issue ("security hardening").
3. The fix ships in a patch release; it is merged to the public branches only as part of that patch release. On the same day the advisory is published, a CVE is requested through GitHub for every vulnerability of Medium severity or higher, and you are credited (unless you prefer not to be).
4. Disclosure happens no later than 90 days after the report, even if a fix is not ready; it happens sooner if the problem is being exploited or becomes public. In that case the advisory publishes what is known plus a workaround.

Please keep the details private until the advisory is published.

---

## Scope and Threat Model

**In scope**: anything that lets one of these attackers cross a boundary:

- code or content running inside a Spoke (container) reaching the host, other Spokes or secrets it should not see
- a peer on the local network reaching a Spoke or a service it publishes
- a hostile repository, registry entry (`data/vm-types.*`) or contribution getting code executed
- a compromised upstream (base image, installer, GitHub Action) affecting VDE users or the project's CI

**Out of scope**:

- the logged-in user passing unusual arguments to their own `vde` commands (that is the user's own account; such defects are fixed as hardening, without an advisory)
- attacks that already require control of the user's host account or Docker daemon
- vulnerabilities in third-party software itself; report those to the upstream project (and tell us if VDE is affected)

---

## Safe Harbor

We will not take legal action against, or ask anyone to take action against, research done in good faith that follows this policy. Good faith means: test only systems and data you own, do not degrade or destroy anything, do not access other people's data, report promptly and privately, and give us the time above to fix the problem before you disclose.

---

## Advisories and Alerts

- Published advisories are listed on the repository's [Security tab](https://github.com/dderyldowney/vde-system/security/advisories) and in [`docs/security/advisories.md`](docs/security/advisories.md). They also appear in the GitHub Advisory Database and the OSV database.
- Every security release has a **Security** section in its [release notes](https://github.com/dderyldowney/vde-system/releases).
- To be notified: on the repository page choose **Watch → Custom** and tick **Releases** and **Security alerts**.
- VDE is not a package that Dependabot tracks, so you will not get an automatic Dependabot alert; watch the repository instead.

---

## Automated Security Checks

| Check | What it does |
|-------|--------------|
| GitHub secret scanning with push protection | Blocks pushes that contain known secret formats |
| Dependabot | Weekly updates for Python dependencies and GitHub Actions |
| CodeQL | Code scanning for the GitHub Actions workflows and Python code |
| `bin/vde-security-audit.zsh` | Fails on open High/Critical CodeQL alerts, absolute-path leaks, and the known database password passed as a Docker build argument |
| `bin/vde-enforce-uap.zsh` | Runs the security audit, requires the mandatory project files (including this policy) and sweeps every zsh file |
| Pre-commit hook | Blocks staged lines that look like hard-coded `API_KEY`, `SECRET` or `PASSWORD` assignments |
| Pre-push hook | Runs the Proof of Life (full lifecycle test) and the audits before code leaves the machine |

---

## Security Architecture

### Identity Isolation

- **Dedicated SSH identity**: the `vde_student` key (ed25519) lives in `~/.ssh/vde/`, separate from your personal SSH configuration.
- **Revocation**: delete `~/.ssh/vde/` to remove all VDE SSH access in one step.

### Container Access

| Feature | Implementation |
|---------|---------------|
| **SSH authentication** | Key-based only; password authentication is disabled |
| **Root login over SSH** | Disabled; you log in as `devuser` |
| **Labels** | Every VDE container carries the `vde.managed=true` label |
| **Network** | Spokes join the dedicated Docker network `vde-net` and reach each other by container name |

### Sensitive Files

| Path | Mode |
|------|------|
| `env-files/` | `0700` |
| `env-files/*.env` | `0600` |
| `~/.ssh/vde/` | `0700` |
| SSH identity and SSH config | `0600` |

---

## Security Best Practices

### For Students

- Never commit `.env` files or secrets to `projects/`
- Use `$HOME/workspace/` inside Spokes for persistent code storage
- Report suspicious behavior to your instructor

### For Operators (Administrators)

- Keep Docker updated to the latest stable version
- Rebuild containers periodically with `vde rebuild --no-cache <alias>`
- Restrict host firewall rules for the ports VDE publishes if the machine is on a shared network
- Review `scripts/setup/` hydration scripts before introducing new VM types
- Watch the repository for releases and security alerts (see above)

### Secret Management

- Use `env-files/` for environment-specific configuration
- Never commit credentials, API keys or tokens to any VDE directory

---

## Dependency Security

| Dependency | Role | Update Strategy |
|------------|------|----------------|
| **Docker** | Container runtime | Keep updated; monitor advisories |
| **Base images** | Official language images | Rebuild periodically |
| **Zsh** | Shell runtime | Minimum 5.0 |
| **OpenSSH** | Connections to Spokes | System-managed |

---

## Acknowledgments

Reporters are credited in the advisory for the problem they found. Thank you to everyone who reports privately and helps keep VDE users safe.
