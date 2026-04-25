# Security Remediation Plan: 1.4.0 Baseline Strike
<!-- @forge (Governance Sentinel) -->

## Objective
To remediate critical security vulnerabilities identified during the 1.4.0 Baseline Strike.

## 1. Identified Vulnerabilities

### ID: VULN-001
- **Vulnerability**: Sensitive Information Leakage in Logs
- **Severity**: Critical
- **Location**: `rebuild_debug.log`
- **Description**: Real API keys (Google, Gemini, OpenRouter, etc.) were written to a plain-text log file during a debug run.
- **Remediation**:
  1. Purge `rebuild_debug.log` immediately.
  2. Add `*.log` to `.gitignore` if not already present.
  3. Ensure `rebuild_debug.log` is removed from the git history (if committed).

### ID: VULN-002
- **Vulnerability**: Potential Command Injection in SQL Execution
- **Severity**: High
- **Location**: `scripts/setup/postgres-init.zsh`
- **Description**: Using `${pg_dev_pass}` directly in a shell command passed to `su` and `psql` without sanitization.
- **Remediation**: 
  1. Use environment variables within `psql` or pass the password securely via a heredoc or pipe.
  2. Sanitize the password variable or enforce strict character sets.

## 2. Implementation Steps

1. **Step 1: Purge the Poison**: Delete `rebuild_debug.log`.
2. **Step 2: Update .gitignore**: Verify and add `*.log` to prevent future leaks.
3. **Step 3: Harden Postgres Hydration**: Modify `scripts/setup/postgres-init.zsh` to pass the password securely using `psql` environment variables (`PGPASSWORD`).
4. **Step 4: Audit Loop**: Run a fresh `grep` scan to ensure no other secrets are lingering.

## 3. Verification
- Verify `rebuild_debug.log` no longer exists.
- Verify `postgres-init.zsh` correctly hydrates a Postgres Spoke without shell injection risk.
- Proof of Life Heartbeat certification.
