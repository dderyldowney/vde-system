# Test Remediation Plan v2 - 9 Failing Tests

## Current Status
- **100 scenarios passed**, 9 failed
- **Root cause fixed**: Log output pollution in parser test wrappers

---

## Failing Tests by Criticality

### CRITICAL (Blocking - Infrastructure)

#### 1. Error-Path: Empty VM Name
- **File**: `tests/features/docker-free/error-path-testing.feature:42`
- **Issue**: `vde create ''` (empty string) returns exit code 0 instead of failing
- **Root Cause**: No input validation in `scripts/create-virtual-for`
- **Fix**: Add validation to reject empty/whitespace-only VM names

**Remediation Steps:**
1. Add validation in `create-virtual-for`:
   ```zsh
   # After VM_NAME="$1" assignment, add:
   if [[ -z "$VM_NAME" || -z "${VM_NAME// }" ]]; then
       echo "Error: VM name cannot be empty" >&2
       exit 1
   fi
   ```

---

### HIGH (Complex Multi-VM Scenarios)

#### 2. Start Both Python and PostgreSQL
- **File**: `documented-development-workflows.feature:22`
- **Issue**: Multi-VM startup test failing

#### 3. Full-Stack JavaScript with Redis  
- **File**: `documented-development-workflows.feature:43`
- **Issue**: JavaScript VM + Redis service combo

#### 4. Microservices Architecture Setup
- **File**: `documented-development-workflows.feature:57`
- **Issue**: Multiple language VMs + multiple service VMs

#### 5. Start All Microservice VMs
- **File**: `documented-development-workflows.feature:64`
- **Issue**: Starting multiple VMs simultaneously

#### 6. Daily Workflow - Morning Setup
- **File**: `documented-development-workflows.feature:81`
- **Issue**: Complex workflow with multiple VMs

**Common Root Cause for #2-6**: These tests require actual Docker container operations. Likely issues:
1. Docker networking (vde-testing network not properly configured for multi-container)
2. Container startup timing/ready checks
3. Service dependency resolution

**Remediation Steps:**
1. Check Docker network configuration in test environment
2. Add wait/retry logic for container health checks
3. Verify `vde-testing` network is properly created/external
4. Check container logs for startup failures

---

### MEDIUM (Single VM / Simpler)

#### 7. New Project Setup - Choose Full Stack
- **File**: `documented-development-workflows.feature:137`
- **Issue**: Likely parser/filtering issue with "full stack" keyword

#### 8. Listing Only Service VMs
- **File**: `vm-information-and-discovery.feature:22`
- **Issue**: Parser filter for "show all services" not extracting correct VMs

**Remediation Steps:**
1. Test parser extraction: `extract_filter "show all services"`
2. Verify SERVICE_VMS list is populated correctly
3. Check VM categories in vm-types.json

---

### LOW (Performance/Timing)

#### 9. Performance - Quick Plan Generation
- **File**: `documented-development-workflows.feature:224`
- **Issue**: Expects <500ms but likely taking longer due to config loading

**Remediation Steps:**
1. Add caching to avoid repeated config loads
2. Or adjust test threshold to 2000ms

---

## Execution Order

```
Phase 1: Fix Critical (1 test)
├── 1. Add empty VM name validation in create-virtual-for

Phase 2: Debug High-Priority Multi-VM (5 tests)
├── 2. Check Docker networking for multi-container tests
├── 3. Add container health check wait logic
├── 4. Debug JavaScript + Redis scenario first (simpler)
├── 5. Fix Python + PostgreSQL scenario
└── 6. Fix remaining microservices scenarios

Phase 3: Fix Medium Priority (2 tests)
├── 7. Debug "show all services" filter
└── 8. Debug "full stack" keyword handling

Phase 4: Fix Low Priority (1 test)
└── 9. Adjust performance threshold or optimize
```

---

## Verification Command
```bash
behave tests/features/docker-free/ --format=progress
```

**Target**: Reduce from 9 failures to 0
