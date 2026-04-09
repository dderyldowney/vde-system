# VDE Remediation Strike Plan (v1.1.0 Hardening)

## OVERVIEW
This plan outlines the surgical strikes required to remediate the vulnerabilities identified in the 2026-04-09 Audit.

## STRIKE 1: Path Traversal Shielding (CRITICAL)
**Target**: `lib/vde-cluster-utils`, `lib/vde-docker`, `lib/vde-docker-state`, `lib/vm-lock`
**Strategy**: Force all `name` and `vm_name` variables through `vde_normalize_name` before path construction.
**Verification**: Run `tests/security/test_cluster_traversal.zsh` and ensure it fails to exploit.

## STRIKE 2: Command Injection Purge (HIGH)
**Target**: `bin/vde-exec`, `lib/vde-shell-compat`
**Strategy**: 
- Refactor `bin/vde-exec` to pass arguments individually to `docker exec` instead of joining them into a string for `zsh -c`.
- Audit and harden `eval` calls in `lib/vde-shell-compat` to ensure they only operate on internally defined variable names.
**Verification**: Run `tests/security/test_exec_injection.zsh` and ensure it fails to exploit.

## STRIKE 3: Secret Scrubbing (MEDIUM)
**Target**: `env-files/jupyterlab.env`
**Strategy**:
- Remove `DATABASE_URL` and `JUPYTER_TOKEN` from the committed `.env` file.
- Create `env-files/jupyterlab.env.template` with instructions for users to set their own secrets.
**Verification**: Ensure `git grep` for the old secrets returns zero results.

## STRIKE 4: Dead Code Pruning (LOW)
**Target**: `lib/vde-audit:vde_audit_wrap`, `lib/vde-log:vde_log_to_file`
**Strategy**: Remove unused functions containing `eval` or unvalidated path sinks.
**Verification**: `bin/vde-enforce-uap.zsh` must yield `[UAP-SUCCESS]`.
