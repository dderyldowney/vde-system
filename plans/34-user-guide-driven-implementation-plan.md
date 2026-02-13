# VDE User Guide-Driven Implementation Plan

**Generated:** 2026-02-13  
**Approach:** Use USER_GUIDE.md as source of truth for documented functionality, implement to conform to documented behavior

---

## Executive Summary

The USER_GUIDE.md documents what VDE SHOULD do. Test results show the gap between documented behavior and actual implementation:

| Test Category | Status | Implication |
|---------------|--------|-------------|
| Docker-free (shell/lib code) | MOSTLY PASSING | Core libraries work |
| Docker-required (container ops) | MOSTLY ERROR | VM lifecycle broken |

**Strategy:** Prioritize implementing docker-required features to build working VM lifecycle operations.

---

## Current State Analysis

### PASSING Tests (Working Architecture)

**Docker-free:**
- Daily Development Workflow - 31 scenarios PASSED
- Shell Compatibility Layer - 27 scenarios PASSED  
- VDE SSH Commands - 8 scenarios PASSED
- VM Information and Discovery - 6 scenarios PASSED
- VM Metadata Verification - 11 scenarios PASSED

**Docker-required:**
- VM-to-Host Communication - 1 feature PASSED (port exposure, networking)

### FAILING/ERROR Tests (Needs Implementation)

**Docker-free:**
- Cache System - 3 scenarios FAILED
- Natural Language Parser - 4 scenarios FAILED

**Docker-required (~48 features):**
- VM Creation (language VMs: python, rust, go, etc.)
- VM Start/Stop operations
- VM Removal
- Service VM lifecycle (postgres, redis, mongodb, etc.)
- SSH access to running VMs
- Health checks and status

---

## Implementation Phases

### Phase 1: Core VM Lifecycle (Priority: CRITICAL)

**Goal:** Implement working `vde create` → `vde start` → `vde stop` → `vde remove` workflow

**Features to implement:**
1. `vde create <vm-type>` - Create language VM from docker-compose template
2. `vde start <vm-id>` - Start created VM container
3. `vde stop <vm-id>` - Stop running VM container
4. `vde remove <vm-id>` - Remove VM container and associated files
5. `vde list` - List all VMs with status

**Test files to examine:**
- `tests/docker-required/vm-creation.feature`
- `tests/docker-required/vm-lifecycle.feature`

### Phase 2: Service VMs (Priority: HIGH)

**Goal:** Enable service VMs (PostgreSQL, Redis, MongoDB, Nginx, RabbitMQ, etc.)

**Features to implement:**
1. Service VM creation from `configs/docker/<service>/docker-compose.yml`
2. Service VM start/stop/remove
3. Data persistence for services (volumes)
4. Service health checks

**Test files to examine:**
- `tests/docker-required/service-vm-creation.feature`

### Phase 3: SSH Access (Priority: HIGH)

**Goal:** Enable passwordless SSH into running VMs

**Features to implement:**
1. `vde ssh <vm-id>` - SSH into running VM as devuser
2. SSH key injection during VM creation
3. SSH config management

**Test files to examine:**
- `tests/docker-required/ssh-access.feature`

### Phase 4: Health & Troubleshooting (Priority: MEDIUM)

**Goal:** Enable `vde check` and `vde resolve` commands

**Features to implement:**
1. `vde check <vm-id>` - Verify VM health
2. `vde resolve <vm-id>` - Attempt auto-fix common issues

**Test files to examine:**
- `tests/docker-required/vm-health-checks.feature`

### Phase 5: Docker-Free Fixes (Priority: LOW)

**Goal:** Fix remaining failing docker-free tests

**Features to fix:**
1. Cache System implementation
2. Natural Language Parser implementation

---

## Test Coverage Target

The goal is to make `generate_user_guide.py` include more scenarios by having more tests pass. Each phase should increase the number of "verified scenarios" in USER_GUIDE.md.

---

## Next Steps

1. **Phase 1:** Examine `tests/docker-required/vm-creation.feature` and implement corresponding step definitions
2. **Phase 2:** Examine service VM docker-compose files and implement creation logic
3. **Phase 3:** Implement SSH access using existing shell compatibility layer
4. **Phase 4:** Implement health check commands
5. **Phase 5:** Fix docker-free failing tests

---

## References

- USER_GUIDE.md - Source of truth for documented behavior
- `tests/docker-required/` - Test scenarios requiring Docker
- `tests/docker-free/` - Test scenarios not requiring Docker
- `configs/docker/` - Docker compose templates for all VM types
