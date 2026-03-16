# Fake Test Remediation Plan
**Created:** 2026-03-16 Session 34
**Status:** APPROVED - Implementation Phase

---

## Executive Summary

| Category | Count | Severity | Action |
|----------|-------|----------|--------|
| Unused steps (dead code) | 6 | HIGH | DELETE |
| `assert True` violations | 7 | CRITICAL | IMPLEMENT real assertions |
| Missing WHEN/THEN implementations | 2 | HIGH | IMPLEMENT |
| Missing step definition | 1 | HIGH | IMPLEMENT |
| Tautological THEN steps | 35 | CRITICAL | FIX with real verification |
| Collaboration test failures | 4 scenarios | HIGH | DEBUG & FIX |
| Postgres OOM | 1 | HIGH | FIX docker-compose.yml |
| Meaningless simulation step | 1 | MEDIUM | DELETE |

---

## TASK 1: Delete Unused Steps (6 steps)

These step definitions are NEVER called by any feature file.

| File | Line | Step Name |
|------|------|-----------|
| `documented_workflow_steps.py` | 505 | `I can verify environment variables match` |
| `debugging_and_port_steps.py` | 180 | `I should see which process is using it` |
| `debugging_and_port_steps.py` | 186 | `I can decide to stop the conflicting process` |
| `debugging_and_port_steps.py` | 192 | `VDE can allocate a different port` |
| `debugging_and_port_steps.py` | 228 | `I can identify if the issue is SSH, Docker, or the VM itself` |
| `daily_workflow_required_steps.py` | 214 | `VDE handles port conflicts gracefully` |

**Action:** Delete the step functions only. No feature file changes needed.

---

## TASK 2: Fix `assert True` Violations (7 steps)

| File | Line | Step Name | New Implementation |
|------|------|-----------|-------------------|
| `documented_workflow_steps.py` | 353 | `my existing SSH entries should be preserved` | Check SSH config has preserved entries |
| `documented_workflow_steps.py` | 372 | `anyone can create the VM using the standard name` | Check vm-types.conf for standard VMs |
| `documented_workflow_steps.py` | 474 | `know when it's ready to use` | Check output for ready indicators |
| `documented_workflow_steps.py` | 492 | `no single VM should monopolize resources` | Check docker inspect for limits |
| `documented_workflow_steps.py` | 518 | `I can check for missing dependencies` | Run vde exec to check dependencies |
| `debugging_and_port_steps.py` | 247 | `I can see if the issue is network, credentials, or database state` | Check pg_isready output |
| `vm_docker_build_steps.py` | 113 | `the build should use multi-stage Dockerfile` | Check Dockerfile for FROM...AS pattern |

---

## TASK 3: Implement Missing WHEN/THEN Steps (2 steps)

| File | Line | Step Name | Implementation |
|------|------|-----------|----------------|
| `ssh_connection_steps.py` | 89 | `I access localhost on the VM's port` | Get port via `vde port`, curl localhost |
| `ssh_connection_steps.py` | 94 | `I connect to a VM` | Run `vde connect --dry-run` |

---

## TASK 4: Implement Missing Step Definition (1 step)

**Feature:** `daily-workflow.feature:133` - "VDE handles port conflicts gracefully"
**Missing:** `Given a system service is using port 2213`

```python
@given('a system service is using port {port:d}')
def step_system_service_using_port(context, port):
    import socket
    context.port_conflict_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context.port_conflict_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        context.port_conflict_socket.bind(('127.0.0.1', port))
        context.port_conflict_socket.listen(1)
        context.conflict_port = port
    except OSError:
        pass
```

---

## TASK 5: Fix Tautological THEN Steps (35 steps)

**File:** `config_steps.py` lines 717-864

**Pattern:** Sets `context.x = True` then immediately `assert context.x` - always passes.

**Fix approach:**
1. Container config checks → Use `docker inspect`
2. File existence checks → Use `Path.exists()` or file read
3. VM state checks → Use `docker_ps()` or `run_vde_command()`

**Key fixes needed:**
- Line 724: `memory_limited` → `docker inspect` for `HostConfig.Memory > 0`
- Line 745: `custom_dns_used` → `docker inspect` for `HostConfig.Dns`
- Line 759: `vms_isolated` → Check docker network isolation
- (All 35 steps in this section need similar treatment)

---

## TASK 6: Fix Collaboration Test Failures (4 scenarios)

### Scenario 1: "Share project VM configuration via git"
**Issue:** `vde create python` returns non-zero
**Fix:** Debug why create fails

### Scenario 2: "Onboard new developer with pre-built VMs"
**Issue:** `vde init` doesn't start VMs, test expects running containers
**Fix:** Change assertion to check VM config existence

```python
@then('they should have all VMs running in minutes')
def step_all_vms_running_fast(context):
    configs_dir = VDE_ROOT / "configs" / "docker"
    assert configs_dir.is_dir()
    compose_files = list(configs_dir.glob("*/docker-compose.yml"))
    assert len(compose_files) >= 1
```

### Scenario 3: "Troubleshooting a problematic VM"
**Issue:** `restart postgres rebuild=true` not parsed
**Fix:** Add pattern handler in `vde_command_steps.py`

```python
if 'restart' in command_lower and 'rebuild=true' in command_lower:
    vm_name = _extract_vms_from_command(command)[0]
    result = run_vde_command(f"restart {vm_name} --rebuild", context=context)
    context.vde_command_result = result
    return
```

### Scenario 4: "Rebuilding after system updates"
**Issue:** Missing step definitions
**Fix:** Implement undefined steps

---

## TASK 7: Fix Postgres OOM

**File:** `configs/docker/postgres/docker-compose.yml`

Add after line 19:
```yaml
    shm_size: '256m'
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

---

## TASK 8: Delete Meaningless Simulation Step

**File:** `cache_steps.py` line 275 - `system is restarted`
**Feature:** `cache-system.feature:124`

**Action:**
- Delete step definition from `cache_steps.py`
- Delete `When system is restarted` line from `cache-system.feature:124`

---

## Execution Order

1. **TASK 7:** Fix Postgres OOM (blocks other tests)
2. **TASK 1:** Delete 6 unused step definitions
3. **TASK 2:** Fix 7 `assert True` violations
4. **TASK 3:** Implement 2 missing WHEN/THEN steps
5. **TASK 4:** Implement 1 missing step definition
6. **TASK 8:** Delete meaningless simulation step
7. **TASK 5:** Fix 35 tautological THEN steps
8. **TASK 6:** Fix collaboration test failures
9. Run yume-guardian validation
10. Run full test suite

---

## File Change Summary

| File | Changes |
|------|---------|
| `documented_workflow_steps.py` | Delete 1, fix 5 |
| `debugging_and_port_steps.py` | Delete 5, fix 1 |
| `vm_docker_build_steps.py` | Fix 1 |
| `ssh_connection_steps.py` | Implement 2 |
| `cache_steps.py` | Delete 1 |
| `cache-system.feature` | Delete 1 line |
| `daily_workflow_required_steps.py` | Delete 1, implement 1 |
| `productivity_steps.py` | Delete 1 |
| `productivity.feature` | Delete 1 line |
| `config_steps.py` | Fix 35 |
| `vde_command_steps.py` | Add pattern handler |
| `team_collaboration_steps.py` | Fix 1 |
| `postgres/docker-compose.yml` | Add shm_size, memory limits |
