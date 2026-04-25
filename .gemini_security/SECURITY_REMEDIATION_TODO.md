# REMEDIATION CHECKLIST (From SAST Recon)
<!-- @forge (Governance Sentinel) -->

## 1. Path Traversal & File System Safety
- [x] **lib/vde-cluster-utils**: Sanitize `name` in `vde_cluster_save` (Line 52).
- [x] **lib/vde-cluster-utils**: Sanitize `name` in `vde_cluster_load` (Line 78).
- [x] **lib/vde-cluster-utils**: Sanitize `name` in `vde_cluster_remove` (Line 111).
- [x] **lib/vde-docker**: Sanitize `vm_name` in `allocate_ssh_port` (Line 144).
- [x] **lib/vde-docker**: Sanitize `vm_name` in `vde_port_release` (Line 158).
- [x] **lib/vde-docker-state**: Sanitize `vm` in `save_docker_state` (Line 118).
- [x] **lib/vde-docker-state**: Sanitize `vm` in `load_docker_state` (Line 126).
- [x] **lib/vm-lock**: Sanitize `lock_file` in `claim_lock` (Line 23).

## 2. Command Injection Prevention
- [x] **bin/vde-exec**: Refactor `docker exec` call to avoid `zsh -c` string interpolation (Line 65).
- [x] **lib/**: Harden `eval` calls in associative array helpers (Lines 111-413).
- [x] **lib/vde-audit**: Remove or harden `vde_audit_wrap` `eval` (Line 332).
- [x] **lib/vde-core**: Harden `vde_time_start`/`end` `eval` (Lines 834-845).
- [x] **lib/vde-log**: Harden `vde_log_grep` pattern handling (Line 328).
- [x] **lib/vde-metrics**: Harden `vde_metrics_time_command` (Line 131).

## 3. Secrets & Configuration
- [x] **env-files/jupyterlab.env**: Remove hardcoded PostgreSQL password (Line 3).
- [x] **env-files/jupyterlab.env**: Remove hardcoded JUPYTER_TOKEN (Line 7).
- [x] **env-files/jupyterlab.env**: Create `.template` file.

## 4. Final Certification
- [x] Run `bin/vde-enforce-uap.zsh`.
- [x] Run all security tests in `tests/security/`.
- [x] Run full BDD suite.
