# Docker-Required Test Remediation Plan

**Project:** VDE (Virtual Development Environment)  
**Document Version:** 1.0  
**Date:** 2026-01-27  
**Status:** Planning Phase

---

## Executive Summary

This document outlines a comprehensive remediation plan for the VDE docker-required test suite. Analysis of the test codebase has revealed extensive use of fake testing patterns that violate the project's Fake Test Prohibition rules. The remediation will be executed in three phases, addressing 13 major tasks across infrastructure, core VM operations, and SSH/networking functionality.

### Key Findings

- **24 feature files** in [`tests/features/docker-required/`](tests/features/docker-required/)
- **300+ instances** of fake test patterns identified
- **Primary violations:**
  - Context flag settings (`context.xxx = True/False`) instead of real verification
  - Pass statements in step definitions
  - No actual Docker container state verification
  - Missing SSH connection validation
  - Simulated operations instead of real command execution

### Remediation Scope

- **Phase 1:** Infrastructure & Test Framework (6 tasks)
- **Phase 2:** Core VM Operations (3 tasks)  
- **Phase 3:** SSH & Networking (4 tasks)
- **Total Tasks:** 13

---

## Problem Analysis

### Current State

The docker-required test suite was designed to validate VDE's Docker-based VM orchestration, SSH configuration, and container management. However, the current implementation uses fake testing patterns that provide no actual verification of system behavior.

### Violation Categories

#### 1. Context Flag Fake Tests

**Pattern:**
```python
@given('VM "{vm_name}" is running')
def step_vm_running(context, vm_name):
    context.vm_running = True  # ❌ FAKE TEST
```

**Required:**
```python
@given('VM "{vm_name}" is running')
def step_vm_running(context, vm_name):
    result = subprocess.run(['docker', 'ps', '--filter', f'name={vm_name}-dev'], 
                          capture_output=True, text=True)
    assert f'{vm_name}-dev' in result.stdout, f"VM {vm_name} is not running"
    context.vm_running = True  # ✅ REAL VERIFICATION
```

**Affected Files:**
- [`tests/features/steps/vm_state_verification_steps.py`](tests/features/steps/vm_state_verification_steps.py) - 15+ violations
- [`tests/features/steps/ssh_vm_steps.py`](tests/features/steps/ssh_vm_steps.py) - 20+ violations
- [`tests/features/steps/ssh_git_steps.py`](tests/features/steps/ssh_git_steps.py) - 25+ violations
- [`tests/features/steps/cache_steps.py`](tests/features/steps/cache_steps.py) - 30+ violations
- [`tests/features/steps/vm_creation_steps.py`](tests/features/steps/vm_creation_steps.py) - 10+ violations

#### 2. Pass Statement Violations

**Pattern:**
```python
@given('SSH agent is running')
def step_ssh_agent_running(context):
    pass  # ❌ FAKE TEST - Does nothing
```

**Required:**
```python
@given('SSH agent is running')
def step_ssh_agent_running(context):
    result = subprocess.run(['pgrep', '-f', 'ssh-agent'], 
                          capture_output=True)
    assert result.returncode == 0, "SSH agent is not running"
```

**Affected Files:**
- [`tests/features/steps/ssh_agent_steps.py`](tests/features/steps/ssh_agent_steps.py) - 10+ violations
- [`tests/features/steps/ssh_config_steps.py`](tests/features/steps/ssh_config_steps.py) - 5+ violations

#### 3. Missing Docker Verification

**Pattern:**
```python
@then('the VM should start')
def step_vm_starts(context):
    context.vm_started = True  # ❌ No Docker verification
```

**Required:**
```python
@then('the VM should start')
def step_vm_starts(context):
    vm_name = context.created_vm
    result = subprocess.run(['docker', 'inspect', '--format', '{{.State.Running}}', 
                           f'{vm_name}-dev'], capture_output=True, text=True)
    assert result.stdout.strip() == 'true', f"VM {vm_name} did not start"
```

**Affected Files:**
- [`tests/features/steps/vm_operations_steps.py`](tests/features/steps/vm_operations_steps.py) - 8+ violations
- [`tests/features/steps/vm_docker_service_steps.py`](tests/features/steps/vm_docker_service_steps.py) - 12+ violations

---

## Remediation Strategy

### Guiding Principles

1. **Real Verification Only:** Every test must verify actual system state
2. **Docker-First:** Use Docker commands to verify container state
3. **SSH Validation:** Test actual SSH connectivity, not configuration files
4. **Incremental Progress:** Complete one phase before moving to the next
5. **No Regressions:** Maintain passing tests while fixing violations

### Phase Approach

Each phase builds on the previous:
- **Phase 1** establishes the testing infrastructure
- **Phase 2** implements core VM operation tests
- **Phase 3** adds complex SSH and networking tests

---

## Phase 1: Infrastructure & Test Framework

**Goal:** Establish robust testing infrastructure and helper functions for real Docker/SSH verification.

### Task 1.1: Create Docker Verification Helpers

**File:** [`tests/features/steps/docker_helpers.py`](tests/features/steps/docker_helpers.py)

**Functions to Implement:**

```python
def verify_container_running(container_name: str) -> bool:
    """Verify a Docker container is running."""
    result = subprocess.run(
        ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
        capture_output=True, text=True, timeout=10
    )
    return container_name in result.stdout

def verify_container_state(container_name: str, expected_state: str) -> bool:
    """Verify container is in expected state (running, exited, paused, etc.)."""
    result = subprocess.run(
        ['docker', 'inspect', '--format', '{{.State.Status}}', container_name],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout.strip() == expected_state

def get_container_port(container_name: str, internal_port: int) -> Optional[int]:
    """Get the host port mapped to a container's internal port."""
    result = subprocess.run(
        ['docker', 'port', container_name, str(internal_port)],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and result.stdout:
        # Parse "0.0.0.0:2200" -> 2200
        return int(result.stdout.split(':')[-1].strip())
    return None

def verify_container_network(container_name: str, network_name: str) -> bool:
    """Verify container is connected to specified network."""
    result = subprocess.run(
        ['docker', 'inspect', '--format', '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}} {{end}}', 
         container_name],
        capture_output=True, text=True, timeout=10
    )
    return network_name in result.stdout

def wait_for_container_healthy(container_name: str, timeout: int = 60) -> bool:
    """Wait for container to become healthy or running."""
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        if verify_container_running(container_name):
            return True
        time.sleep(2)
    return False
```

**Acceptance Criteria:**
- [ ] All functions implemented with proper error handling
- [ ] Functions use subprocess.run with timeout
- [ ] Functions return boolean or typed values
- [ ] Unit tests for each helper function
- [ ] Documentation with usage examples

**Dependencies:** None

---

### Task 1.2: Create SSH Verification Helpers

**File:** [`tests/features/steps/ssh_verification_helpers.py`](tests/features/steps/ssh_verification_helpers.py)

**Functions to Implement:**

```python
def verify_ssh_agent_running() -> bool:
    """Verify SSH agent is running."""
    result = subprocess.run(['pgrep', '-f', 'ssh-agent'], 
                          capture_output=True, timeout=5)
    return result.returncode == 0

def verify_ssh_keys_loaded() -> bool:
    """Verify SSH keys are loaded in agent."""
    result = subprocess.run(['ssh-add', '-l'], 
                          capture_output=True, text=True, timeout=5)
    return result.returncode == 0 and len(result.stdout.strip()) > 0

def verify_ssh_connection(host: str, port: int, user: str = 'devuser', 
                         timeout: int = 10) -> bool:
    """Verify SSH connection to host:port."""
    result = subprocess.run(
        ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
         '-p', str(port), f'{user}@localhost', 'echo', 'connected'],
        capture_output=True, text=True, timeout=timeout
    )
    return result.returncode == 0 and 'connected' in result.stdout

def verify_ssh_config_entry(host: str) -> bool:
    """Verify SSH config contains entry for host."""
    ssh_config = Path.home() / '.ssh' / 'config'
    if not ssh_config.exists():
        return False
    content = ssh_config.read_text()
    return f'Host {host}' in content

def verify_ssh_key_forwarding(vm_name: str) -> bool:
    """Verify SSH agent forwarding is configured for VM."""
    ssh_config = Path.home() / '.ssh' / 'config'
    if not ssh_config.exists():
        return False
    content = ssh_config.read_text()
    # Check for ForwardAgent yes in the VM's config block
    in_vm_block = False
    for line in content.split('\n'):
        if f'Host {vm_name}' in line:
            in_vm_block = True
        elif line.startswith('Host ') and in_vm_block:
            break
        elif in_vm_block and 'ForwardAgent yes' in line:
            return True
    return False
```

**Acceptance Criteria:**
- [ ] All functions implemented with proper error handling
- [ ] SSH connection tests use real SSH commands
- [ ] Timeout handling for all network operations
- [ ] Unit tests for each helper function
- [ ] Documentation with usage examples

**Dependencies:** None

---

### Task 1.3: Fix VM State Verification Steps

**File:** [`tests/features/steps/vm_state_verification_steps.py`](tests/features/steps/vm_state_verification_steps.py)

**Steps to Fix:**

1. **`@given('"python" VM is running')`** (line 23)
   - Replace `context.python_running = True` with Docker verification
   - Use `verify_container_running('python-dev')`

2. **`@given('a VM is running')`** (line 33)
   - Replace context flag with real Docker check
   - Verify at least one VDE container is running

3. **`@given('a VM has crashed')`** (line 45)
   - Replace simulation with real crash detection
   - Check Docker container exit code and status

4. **`@given('a VM is being built')`** (line 75)
   - Verify actual Docker build process
   - Check for docker-compose build in progress

5. **`@given('a VM is not working correctly')`** (line 87)
   - Check actual container health status
   - Verify container is in 'exited' or 'unhealthy' state

**Acceptance Criteria:**
- [ ] All 15+ fake test violations fixed
- [ ] Real Docker state verification in all steps
- [ ] Proper error messages when assertions fail
- [ ] Tests pass with actual VMs running
- [ ] No context flag fake tests remain

**Dependencies:** Task 1.1 (Docker helpers)

---

### Task 1.4: Fix VM Creation Steps

**File:** [`tests/features/steps/vm_creation_steps.py`](tests/features/steps/vm_creation_steps.py)

**Steps to Fix:**

1. **`@given('VM "{vm_name}" has been created')`** (line 59)
   - Verify docker-compose.yml exists
   - Verify container can be inspected
   - Check SSH config entry exists

2. **`@given('VM "{vm_name}" is not created')`** (line 79)
   - Verify docker-compose.yml does NOT exist
   - Verify container does NOT exist in Docker
   - Verify SSH config entry does NOT exist

3. **`@given('a non-VDE process is listening on port "{port}"')`** (line 131)
   - Actually start a process on the port (e.g., `nc -l`)
   - Store process PID for cleanup
   - Verify port is actually in use with `lsof` or `netstat`

4. **`@given('a Docker container is bound to host port "{port}"')`** (line 151)
   - Start an actual Docker container bound to the port
   - Store container ID for cleanup
   - Verify port binding with `docker port`

5. **`@when('I create language VM "{vm_name}"')`** (line 234)
   - Execute actual VDE create command
   - Verify command exit code
   - Check that docker-compose.yml was created

**Acceptance Criteria:**
- [ ] All 10+ fake test violations fixed
- [ ] Real VM creation verification
- [ ] Proper cleanup of test resources
- [ ] Tests pass with actual VM creation
- [ ] Port conflict tests use real ports

**Dependencies:** Task 1.1 (Docker helpers)

---

### Task 1.5: Fix Port Management Steps

**File:** [`tests/features/steps/port_management_steps.py`](tests/features/steps/port_management_steps.py)

**Steps to Fix:**

1. **`@given('VM "{vm_name}" is allocated port "{port}"')`** (line 24)
   - Verify port registry file contains the allocation
   - Verify docker-compose.yml has correct port mapping
   - Check actual port binding if VM is running

2. **`@given('two processes try to allocate ports simultaneously')`** (line 51)
   - Actually spawn two concurrent processes
   - Use multiprocessing to simulate race condition
   - Verify atomic port allocation

3. **`@then('Atomic port reservation prevents race conditions')`** (line 130)
   - Test actual concurrent port allocation
   - Verify no duplicate ports assigned
   - Check port registry consistency

4. **`@then('Port registry updates when VM is removed')`** (line 199)
   - Execute actual VM removal
   - Verify port is removed from registry
   - Check port becomes available for reuse

**Acceptance Criteria:**
- [ ] All port management violations fixed
- [ ] Real port registry verification
- [ ] Concurrent allocation tests work
- [ ] Port cleanup verified
- [ ] No race conditions in tests

**Dependencies:** Task 1.1 (Docker helpers)

---

### Task 1.6: Create Test Cleanup Framework

**File:** [`tests/features/steps/test_cleanup.py`](tests/features/steps/test_cleanup.py)

**Purpose:** Ensure all test resources are properly cleaned up after each scenario.

**Functions to Implement:**

```python
def cleanup_test_containers(context):
    """Remove all test containers created during scenario."""
    if hasattr(context, 'test_containers'):
        for container_id in context.test_containers:
            subprocess.run(['docker', 'rm', '-f', container_id], 
                         capture_output=True, timeout=30)
        context.test_containers = []

def cleanup_test_ports(context):
    """Kill processes bound to test ports."""
    if hasattr(context, 'test_port_processes'):
        for pid in context.test_port_processes:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        context.test_port_processes = []

def cleanup_test_vms(context):
    """Remove test VMs created during scenario."""
    if hasattr(context, 'test_vms'):
        for vm_name in context.test_vms:
            # Run remove-virtual command
            subprocess.run(['./scripts/remove-virtual', vm_name], 
                         capture_output=True, timeout=60)
        context.test_vms = []

def cleanup_ssh_config_entries(context):
    """Remove test SSH config entries."""
    if hasattr(context, 'test_ssh_entries'):
        ssh_config = Path.home() / '.ssh' / 'config'
        if ssh_config.exists():
            content = ssh_config.read_text()
            for entry in context.test_ssh_entries:
                # Remove the Host block for this entry
                content = remove_ssh_host_block(content, entry)
            ssh_config.write_text(content)
        context.test_ssh_entries = []
```

**Integration with environment.py:**

```python
def after_scenario(context, scenario):
    """Clean up after each scenario."""
    cleanup_test_containers(context)
    cleanup_test_ports(context)
    cleanup_test_vms(context)
    cleanup_ssh_config_entries(context)
```

**Acceptance Criteria:**
- [ ] All cleanup functions implemented
- [ ] Integration with Behave hooks
- [ ] No test resources leak between scenarios
- [ ] Cleanup handles errors gracefully
- [ ] Documentation for adding new cleanup types

**Dependencies:** None

---

## Phase 2: Core VM Operations

**Goal:** Fix fake tests in core VM lifecycle operations (create, start, stop, remove).

### Task 2.1: Fix VM Operations Steps

**File:** [`tests/features/steps/vm_operations_steps.py`](tests/features/steps/vm_operations_steps.py)

**Steps to Fix:**

1. **`@when('I run "start-virtual all"')`** (line 34)
   - Execute actual start-virtual command
   - Verify command exit code
   - Check that containers actually started

2. **`@when('I run "shutdown-virtual all"')`** (line 44)
   - Execute actual shutdown-virtual command
   - Verify containers stopped
   - Check Docker ps output

3. **`@then('all my VMs should start')`** (line 104)
   - Verify all VDE containers are running
   - Check each container's state with Docker
   - Verify SSH ports are accessible

4. **`@then('the VM should start')`** (line 137)
   - Verify specific VM container is running
   - Check container health status
   - Verify SSH connection works

5. **`@then('the VM should stop')`** (line 145)
   - Verify container is stopped
   - Check Docker inspect shows 'exited' state
   - Verify SSH connection fails

**Acceptance Criteria:**
- [ ] All 8+ violations fixed
- [ ] Real command execution
- [ ] Docker state verification
- [ ] SSH connectivity checks
- [ ] Proper error handling

**Dependencies:** Task 1.1, Task 1.2

---

### Task 2.2: Fix VM Docker Service Steps

**File:** [`tests/features/steps/vm_docker_service_steps.py`](tests/features/steps/vm_docker_service_steps.py)

**Steps to Fix:**

1. **`@given('I create a PostgreSQL VM')`** (line 27)
   - Execute actual create command
   - Verify PostgreSQL container created
   - Check port 5432 is mapped

2. **`@when('it starts')`** (line 48)
   - Start the PostgreSQL VM
   - Verify container is running
   - Test PostgreSQL connection

3. **`@then('both Python and PostgreSQL VMs should start')`** (line 80)
   - Verify both containers running
   - Check network connectivity between them
   - Test actual database connection from Python VM

4. **`@then('I can connect to MySQL from other VMs')`** (line 150)
   - Execute actual MySQL connection test
   - Run query from another VM
   - Verify result is correct

**Acceptance Criteria:**
- [ ] All 12+ violations fixed
- [ ] Real service VM verification
- [ ] Database connectivity tests
- [ ] Network communication verified
- [ ] Service-specific checks (PostgreSQL, MySQL, Redis)

**Dependencies:** Task 1.1, Task 1.2

---

### Task 2.3: Fix VM Docker Build Steps

**File:** [`tests/features/steps/vm_docker_build_steps.py`](tests/features/steps/vm_docker_build_steps.py)

**Steps to Fix:**

1. **`@given('I rebuild a language VM')`** (line 25)
   - Execute actual rebuild command
   - Verify docker-compose build runs
   - Check build logs for success

2. **`@then('docker-compose build should be executed')`** (line 75)
   - Verify build command was run
   - Check Docker build cache
   - Verify new image was created

3. **`@then('the build should use multi-stage Dockerfile')`** (line 111)
   - Parse Dockerfile
   - Verify multi-stage structure
   - Check intermediate images

4. **`@then('the rebuild should use the latest base images')`** (line 140)
   - Check Docker image pull logs
   - Verify base image is latest
   - Compare image digests

**Acceptance Criteria:**
- [ ] All build-related violations fixed
- [ ] Real Docker build verification
- [ ] Build cache tests work
- [ ] Multi-stage build validation
- [ ] Image verification

**Dependencies:** Task 1.1

---

## Phase 3: SSH & Networking

**Goal:** Fix fake tests in SSH configuration, agent forwarding, and VM-to-VM communication.

### Task 3.1: Fix SSH VM Steps

**File:** [`tests/features/steps/ssh_vm_steps.py`](tests/features/steps/ssh_vm_steps.py)

**Steps to Fix:**

1. **`@given('I create a Python VM for my API')`** (line 50)
   - Actually create Python VM
   - Verify container running
   - Check SSH config entry

2. **`@when('I SSH into the Go VM')`** (line 123)
   - Execute actual SSH connection
   - Verify connection succeeds
   - Store SSH session for cleanup

3. **`@when('I run "ssh python-dev" from within the Go VM')`** (line 130)
   - Execute VM-to-VM SSH command
   - Verify agent forwarding works
   - Check command output

4. **`@then('I should connect to the Python VM')`** (line 240)
   - Verify SSH connection established
   - Check we're in correct VM
   - Verify user is devuser

5. **`@then('I should be authenticated using my host\'s SSH keys')`** (line 250)
   - Verify SSH agent forwarding
   - Check no keys copied to VM
   - Verify authentication method

**Acceptance Criteria:**
- [ ] All 20+ violations fixed
- [ ] Real SSH connections tested
- [ ] Agent forwarding verified
- [ ] VM-to-VM communication works
- [ ] No keys stored in containers

**Dependencies:** Task 1.2, Task 2.1

---

### Task 3.2: Fix SSH Config Steps

**File:** [`tests/features/steps/ssh_config_steps.py`](tests/features/steps/ssh_config_steps.py)

**Steps to Fix:**

1. **`@given('SSH keys exist in ~/.ssh/')`** (line 37)
   - Verify actual SSH keys exist
   - Check key permissions
   - Verify key types (ed25519, rsa, etc.)

2. **`@when('I run any VDE command that requires SSH')`** (line 44)
   - Execute actual VDE command
   - Verify SSH setup runs
   - Check agent starts if needed

3. **`@then('SSH agent should be started')`** (line 54)
   - Verify SSH agent process running
   - Check SSH_AUTH_SOCK is set
   - Verify agent is accessible

4. **`@then('available SSH keys should be loaded into agent')`** (line 61)
   - Run ssh-add -l
   - Verify keys are listed
   - Check key fingerprints

5. **`@then('SSH config should contain entry for "{host}"')`** (line 256)
   - Read actual SSH config file
   - Parse and verify Host block
   - Check all required fields present

**Acceptance Criteria:**
- [ ] All SSH config violations fixed
- [ ] Real SSH agent verification
- [ ] Config file parsing works
- [ ] Key loading verified
- [ ] Atomic config updates tested

**Dependencies:** Task 1.2

---

### Task 3.3: Fix SSH Agent Steps

**File:** [`tests/features/steps/ssh_agent_steps.py`](tests/features/steps/ssh_agent_steps.py)

**Steps to Fix:**

1. **`@given('Have created multiple VMs')`** (line 383)
   - Actually create multiple VMs
   - Verify all containers running
   - Check SSH config for all

2. **`@given('Use SSH to connect to any VM')`** (line 389)
   - Execute real SSH connection
   - Verify connection works
   - Test with multiple VMs

3. **`@given('Have running VM with SSH configured')`** (line 432)
   - Verify VM is running
   - Check SSH config exists
   - Test SSH connection

4. **`@given('User has multiple SSH key types')`** (line 616)
   - Verify multiple key types exist
   - Check ed25519, rsa, ecdsa
   - Verify all are loaded in agent

**Acceptance Criteria:**
- [ ] All 10+ pass statement violations fixed
- [ ] Real SSH agent tests
- [ ] Multiple VM scenarios work
- [ ] Key type detection verified
- [ ] Agent forwarding tested

**Dependencies:** Task 1.2, Task 3.1

---

### Task 3.4: Fix SSH Git Steps

**File:** [`tests/features/steps/ssh_git_steps.py`](tests/features/steps/ssh_git_steps.py)

**Steps to Fix:**

1. **`@given('GitHub account with SSH keys configured')`** (line 40)
   - Verify SSH keys exist
   - Check GitHub key is loaded
   - Test GitHub SSH connection (ssh -T git@github.com)

2. **`@when('I run "git clone git@github.com:myuser/private-repo.git"')`** (line 190)
   - Execute actual git clone
   - Verify repository cloned
   - Check SSH authentication worked

3. **`@when('I run "git push origin main"')`** (line 204)
   - Execute actual git push
   - Verify push succeeded
   - Check SSH agent was used

4. **`@then('Host\'s SSH keys should be used for authentication')`** (line 342)
   - Verify agent forwarding
   - Check no keys in VM
   - Verify authentication method

5. **`@then('Git commands should use host\'s SSH keys')`** (line 438)
   - Execute git command
   - Verify SSH agent forwarding
   - Check authentication logs

**Acceptance Criteria:**
- [ ] All 25+ violations fixed
- [ ] Real Git operations tested
- [ ] SSH agent forwarding verified
- [ ] Multiple Git hosts supported
- [ ] No keys stored in VMs

**Dependencies:** Task 1.2, Task 3.1

---

## Success Criteria

### Phase 1 Complete

- [ ] All helper functions implemented and tested
- [ ] Docker verification works reliably
- [ ] SSH verification works reliably
- [ ] Test cleanup framework operational
- [ ] No fake tests in infrastructure code

### Phase 2 Complete

- [ ] All VM operation tests use real Docker commands
- [ ] Service VM tests verify actual connectivity
- [ ] Build tests verify actual Docker builds
- [ ] No context flag fake tests in VM operations

### Phase 3 Complete

- [ ] All SSH tests use real connections
- [ ] Agent forwarding verified in tests
- [ ] VM-to-VM communication tested
- [ ] Git operations use real SSH
- [ ] No pass statement violations remain

### Overall Success

- [ ] All 300+ fake test violations fixed
- [ ] Test suite passes with real VMs
- [ ] yume-guardian returns CLEAN
- [ ] code-reviewer approval obtained
- [ ] Documentation updated
- [ ] USER_GUIDE.md regenerated

---

## Risk Mitigation

### Risk 1: Test Execution Time

**Risk:** Real Docker operations may make tests slow.

**Mitigation:**
- Use Docker BuildKit for faster builds
- Implement parallel test execution where safe
- Cache Docker images between test runs
- Use smaller base images for test VMs

### Risk 2: Test Environment Dependencies

**Risk:** Tests require Docker daemon running.

**Mitigation:**
- Document Docker requirements clearly
- Add pre-test Docker availability check
- Provide clear error messages when Docker unavailable
- Create docker-compose for test infrastructure

### Risk 3: Port Conflicts

**Risk:** Tests may conflict with running VMs.

**Mitigation:**
- Use dedicated port range for tests (e.g., 9000-9999)
- Implement robust port cleanup
- Check for port availability before tests
- Document port requirements

### Risk 4: SSH Key Management

**Risk:** Tests may interfere with user's SSH setup.

**Mitigation:**
- Use test-specific SSH config file
- Create temporary SSH keys for tests
- Never modify user's ~/.ssh/config directly
- Document SSH test requirements

### Risk 5: Resource Cleanup

**Risk:** Failed tests may leave containers running.

**Mitigation:**
- Implement comprehensive cleanup hooks
- Use try/finally blocks for resource management
- Add cleanup verification step
- Provide manual cleanup script

---

## Implementation Notes

### Test Execution Order

1. Run Phase 1 tests first (infrastructure)
2. Run Phase 2 tests second (VM operations)
3. Run Phase 3 tests last (SSH/networking)

### Continuous Integration

- Run yume-guardian after each task completion
- Run full test suite after each phase
- Update tracking document after each task
- Commit changes only when yume-guardian is CLEAN

### Documentation Updates

After remediation:
- Update [`docs/TESTING.md`](docs/TESTING.md) with new test patterns
- Regenerate [`USER_GUIDE.md`](USER_GUIDE.md) from passing tests
- Update [`CONTRIBUTING.md`](CONTRIBUTING.md) with test guidelines
- Add examples of proper test implementation

---

## Appendix A: Fake Test Pattern Reference

### Forbidden Patterns

```python
# ❌ FORBIDDEN: Context flag fake test
context.vm_running = True

# ❌ FORBIDDEN: Pass statement
pass

# ❌ FORBIDDEN: Always-true assertion
assert True, "verified"

# ❌ FORBIDDEN: Getattr with True default
getattr(context, 'docker_installed', True)

# ❌ FORBIDDEN: Simulation comment
# Simulate Docker container start
context.container_started = True
```

### Required Patterns

```python
# ✅ REQUIRED: Real Docker verification
result = subprocess.run(['docker', 'ps', '--filter', 'name=python-dev'],
                       capture_output=True, text=True, timeout=10)
assert 'python-dev' in result.stdout, "Container not running"

# ✅ REQUIRED: Real SSH verification
result = subprocess.run(['ssh', '-o', 'ConnectTimeout=5', 
                        'devuser@localhost', '-p', '2200', 'echo', 'test'],
                       capture_output=True, text=True, timeout=10)
assert result.returncode == 0, "SSH connection failed"

# ✅ REQUIRED: Real file verification
ssh_config = Path.home() / '.ssh' / 'config'
assert ssh_config.exists(), "SSH config not found"
content = ssh_config.read_text()
assert 'Host python-dev' in content, "SSH config entry missing"
```

---

## Appendix B: Helper Function Examples

### Docker Helper Usage

```python
from tests.features.steps.docker_helpers import verify_container_running

@then('the VM should be running')
def step_vm_running(context):
    vm_name = context.created_vm
    assert verify_container_running(f'{vm_name}-dev'), \
        f"VM {vm_name} is not running"
```

### SSH Helper Usage

```python
from tests.features.steps.ssh_verification_helpers import verify_ssh_connection

@then('I should be able to SSH into the VM')
def step_can_ssh(context):
    port = context.vm_ssh_port
    assert verify_ssh_connection('localhost', port), \
        f"Cannot SSH to VM on port {port}"
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | Claude Opus 4.5 | Initial comprehensive remediation plan |

---

**Next Steps:**
1. Review and approve this plan
2. Create tracking document
3. Begin Phase 1 implementation
4. Update tracking document as work progresses
