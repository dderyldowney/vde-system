# Implementation Plan: Phase 24 Bucket 1 - Configuration Management Hardening
<!-- @shared-law (Forge Component) -->

**Objective:** Replace placeholder and "fake" logic in `tests/features/steps/configuration_management_steps.py` with real behavioral verification for all scenarios in `configuration-management.feature`.

## Key Files & Context
- `tests/features/core-infrastructure/configuration-management.feature`: The BDD feature file.
- `tests/features/steps/configuration_management_steps.py`: The step definitions needing hardening.
- `bin/vde`: The canonical entrypoint for all operations.
- `data/vm-types.json`: The authoritative VM registry.

## Implementation Steps

### 1. Hardening: Custom Port Verification
- **Scenario:** `Override default port ranges`
- **Current:** Only checks `vm-types.json`.
- **Harden:** Start the VM and verify the host-mapped port matches the custom range using a socket connection check from the host.

### 2. Hardening: DNS Resolution Verification
- **Scenario:** `Configure DNS resolution for VMs`
- **Current:** Only checks the `docker-compose.yml` content.
- **Harden:** Start a VM with custom DNS and use `vde exec <vm> cat /etc/resolv.conf` or `nslookup` to verify the DNS settings are active inside the container.

### 3. Hardening: Volume Mounts Verification
- **Scenario:** `Configure volume mounts for VM`
- **Current:** Only checks `docker-compose.yml`.
- **Harden:** Use `vde exec <vm> touch /vde/workspace/test-file` and verify existence on the host, or vice-versa, to prove the mount is functional.

### 4. Hardening: Environment Variables Verification
- **Scenario:** `Configure environment variables for VM`
- **Current:** Checks `env-files/myapp.env` and `docker-compose.yml`.
- **Harden:** Use `vde exec <vm> env` to verify the variable is actually present and has the correct value inside the running container.

### 5. Hardening: UID/GID Verification
- **Scenario:** `Configure custom UID/GID for container user`
- **Current:** Checks `docker-compose.yml` build args.
- **Harden:** Use `vde exec <vm> id` to verify the `devuser` UID and GID match the expected custom values.

### 6. Hardening: Resource Limits Verification
- **Scenario:** `Configure container resource limits`
- **Current:** Uses `docker inspect`. (This is actually good, but let's ensure it's robust).
- **Verify:** Confirm `mem_limit` is correctly reflected in `docker inspect` and potentially check `/sys/fs/cgroup/memory/memory.limit_in_bytes` inside the container.

### 7. Hardening: Logging Configuration Verification
- **Scenario:** `Configure log output for VM`
- **Current:** Checks `docker-compose.yml` and `vde logs --help`.
- **Harden:** Start a VM, generate some output, and verify the log file exists in the expected location with the correct driver settings using `docker inspect`.

### 8. Hardening: Restart Policy Verification
- **Scenario:** `Configure restart policy`
- **Current:** Checks `docker-compose.yml`.
- **Harden:** Use `docker inspect` to verify the `RestartPolicy` is set to `always` or as configured.

### 9. Hardening: Health Check Verification
- **Scenario:** `Configure health check for VM`
- **Current:** Checks `docker-compose.yml` and `vde health`.
- **Harden:** Start a VM and wait for the status to become `healthy` using `vde_wait_for_container_healthy` logic or `docker inspect`.

## Verification & Testing
- Run the specific feature file: `python3 -m behave tests/features/core-infrastructure/configuration-management.feature`.
- Ensure all 27 scenarios pass with real behavioral evidence.
- Run the Enforcer: `bin/vde-enforce-uap.zsh` to ensure no "fake tests" or `sleep` calls were introduced.
