# Plan 33a: Docker Operations Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Status**: Ready  
**Created**: 2026-02-06  
**Priority**: CRITICAL (Tier 1)

## Overview

Remediate the Docker Operations feature, which is foundational to all VDE VM operations. This feature tests Docker Compose operations including image building, container lifecycle management, error handling, and retry logic.

## Current State

**Feature**: `tests/features/docker-required/docker-operations.feature`  
**Scenarios**: 18 total  
**Undefined Steps**: ~50 (estimated)  
**Tags**: `@user-guide-internal`, `@requires-docker-host`

### Scenarios Breakdown
1. Build Docker image for VM
2. Start container with docker-compose up
3. Stop container with docker-compose down
4. Restart container
5. Rebuild with --build flag
6. Rebuild without cache with --no-cache flag
7. Parse Docker error messages
8. Retry transient failures with exponential backoff
9. Get container status
10. Detect running containers
11. Use correct docker-compose project name
12. Container naming follows convention
13. Volume mounts are created correctly
14. Environment variables are passed to container

### Background Steps
- `Given python VM is started`
- `And postgres VM is started`

## Phase 1: Discovery & Analysis

### Tasks
- [ ] Run `behave --dry-run tests/features/docker-required/docker-operations.feature`
- [ ] Extract all undefined steps
- [ ] Check for existing step definitions in `tests/features/steps/`
- [ ] Identify duplicate/conflicting definitions
- [ ] Document dependencies on `scripts/lib/vm-common`

### Expected Undefined Steps (by category)

#### GIVEN Steps (Setup)
- `Given VM "python" docker-compose.yml exists`
- `Given VM "python" image exists`
- `Given VM "python" is running`
- `Given docker-compose operation fails`
- `Given docker-compose operation fails with transient error`
- `Given VM "python" exists`
- `Given multiple VMs are running`
- `Given language VM "python" is started`
- `Given service VM "postgres" is started`
- `Given VM "python" has env file`

#### WHEN Steps (Actions)
- `When I start VM "python"`
- `When I stop VM "python"`
- `When I restart VM "python"`
- `When I start VM "python" with --rebuild`
- `When I start VM "python" with --rebuild and --no-cache`
- `When stderr is parsed`
- `When operation is retried`
- `When I check VM status`
- `When I get running VMs`
- `When container is started`

#### THEN Steps (Assertions)
- `Then docker-compose build should be executed`
- `Then image should be built successfully`
- `Then docker-compose up -d should be executed`
- `Then container should be running`
- `Then docker-compose down should be executed`
- `Then container should not be running`
- `Then container should have new container ID`
- `Then docker-compose up --build should be executed`
- `Then image should be rebuilt`
- `Then docker-compose up --build --no-cache should be executed`
- `Then "yaml.*mapping.*not allowed" should map to YAML error`
- `Then "yaml.*" should map to YAML error`
- `Then "yaml.*" should map to general error`
- `Then retry should use exponential backoff`
- `Then maximum retries should not exceed 3`
- `Then delay should be capped at 30 seconds`
- `Then status should be one of: "running", "stopped", "not_created", "unknown"`
- `Then all running containers should be listed`
- `Then stopped containers should not be listed`
- `Then docker-compose project should be "vde-python"`
- `Then container should be named "python-dev"`
- `Then container should be named "postgres"`
- `Then projects/python volume should be mounted`
- `Then logs/python volume should be mounted`
- `Then volume should be mounted from host directory`
- `Then env file should be read by docker-compose`
- `Then SSH_PORT variable should be available in container`

## Phase 2: Step Definition Planning

### File Structure
Create/update: `tests/features/steps/docker_operations_steps.py`

### Step Groups

#### Group 1: VM State Setup (GIVEN)
- VM exists checks
- VM running checks
- Docker Compose file existence
- Image existence checks

#### Group 2: Docker Operations (WHEN)
- Start VM (with/without rebuild, no-cache)
- Stop VM
- Restart VM
- Check status
- Get running VMs

#### Group 3: Docker Assertions (THEN)
- Command execution verification
- Container state verification
- Image build verification
- Container ID changes

#### Group 4: Error Handling (GIVEN/WHEN/THEN)
- Error simulation
- Error parsing
- Retry logic
- Exponential backoff

#### Group 5: Configuration Verification (THEN)
- Project naming
- Container naming
- Volume mounts
- Environment variables

### Dependencies
- `scripts/lib/vm-common` - VM operations
- `docker-compose` command
- Docker Python SDK (optional, for advanced checks)
- `tests/features/steps/common_steps.py` - Shared steps

## Phase 3: Implementation

### Implementation Order

#### Iteration 1: Basic VM Operations (Steps 1-10)
1. Implement VM state setup steps (GIVEN)
2. Implement basic start/stop/restart operations (WHEN)
3. Implement basic assertions (THEN)
4. Test with scenarios 1-6

#### Iteration 2: Error Handling (Steps 11-20)
1. Implement error simulation steps (GIVEN)
2. Implement error parsing steps (WHEN/THEN)
3. Implement retry logic steps (THEN)
4. Test with scenarios 7-8

#### Iteration 3: Status and Discovery (Steps 21-30)
1. Implement status check steps (WHEN/THEN)
2. Implement running VM detection (WHEN/THEN)
3. Test with scenarios 9-10

#### Iteration 4: Configuration Verification (Steps 31-50)
1. Implement naming verification steps (THEN)
2. Implement volume mount verification (THEN)
3. Implement environment variable verification (THEN)
4. Test with scenarios 11-14

### Key Implementation Notes

#### Real Docker Operations
- Use actual `docker-compose` commands via subprocess
- Verify container states with `docker ps`
- Check images with `docker images`
- Parse real docker-compose output

#### No Fake Tests
- ❌ `assert True` patterns
- ❌ `context.docker_installed = True` flags
- ✅ Real subprocess calls
- ✅ Actual Docker state verification

#### Error Handling
- Capture stderr from docker-compose
- Parse real error messages
- Test retry logic with actual failures (if possible)
- Use timeouts for long operations

## Phase 4: Validation

### Test Execution
```bash
# Run just this feature
behave tests/features/docker-required/docker-operations.feature

# Expected results after implementation
- 0 undefined steps
- 0 AmbiguousStep errors
- ≥14/18 scenarios passing (78%)
```

### Validation Checklist
- [ ] All undefined steps implemented
- [ ] No fake test patterns
- [ ] Real Docker operations used
- [ ] Proper error handling
- [ ] Cleanup after tests
- [ ] No conflicts with existing steps

## Phase 5: Integration Testing

### Full Suite Test
```bash
# Run all non-WIP tests
behave --tags=-wip

# Check for regressions
- No new failures in other features
- Docker Operations scenarios passing
- Overall pass rate improved
```

### Integration Checklist
- [ ] No regressions in other features
- [ ] Docker Operations passing
- [ ] Test execution time acceptable (<5 min)
- [ ] No resource leaks (containers, images)

## Phase 6: Completion

### Deliverables
- [ ] `tests/features/steps/docker_operations_steps.py` created/updated
- [ ] All 18 scenarios passing or documented as skipped
- [ ] Plan 33a moved to `plans/completed/`
- [ ] Plan 33 master plan updated with results

### Success Metrics
- ✅ 0 undefined steps (down from ~50)
- ✅ ≥14/18 scenarios passing (≥78%)
- ✅ No fake test patterns
- ✅ Real Docker operations verified

## Estimated Effort

- **Phase 1**: 30 minutes (discovery)
- **Phase 2**: 1 hour (planning)
- **Phase 3**: 4-6 hours (implementation in 4 iterations)
- **Phase 4**: 1 hour (validation)
- **Phase 5**: 30 minutes (integration)
- **Phase 6**: 30 minutes (completion)

**Total**: 7.5-9.5 hours

## Risks and Mitigation

### Risk 1: Docker Daemon Availability
- **Impact**: Tests fail if Docker not running
- **Mitigation**: Add prerequisite checks, clear error messages

### Risk 2: Port Conflicts
- **Impact**: Container startup failures
- **Mitigation**: Use VDE port allocation system

### Risk 3: Image Build Time
- **Impact**: Slow test execution
- **Mitigation**: Use cached images where possible, skip rebuild tests if needed

### Risk 4: Cleanup Failures
- **Impact**: Resource leaks between test runs
- **Mitigation**: Implement robust cleanup in step definitions

## Dependencies

### External
- Docker daemon running
- docker-compose installed
- VDE base images built

### Internal
- `scripts/lib/vm-common` library
- `tests/features/steps/common_steps.py`
- Port registry system

## Next Steps

1. Execute Phase 1 (Discovery & Analysis)
2. Create `docker_operations_steps.py` file
3. Implement steps in 4 iterations
4. Validate and integrate
5. Update Plan 33 master plan

## References

- [Plan 33: Master Plan](33-comprehensive-test-remediation-plan.md)
- [Plan 32: SSH Configuration](completed/32-ssh-configuration-remediation-plan-detailed.md) (template)
- Feature file: `tests/features/docker-required/docker-operations.feature`
- VM Common library: `scripts/lib/vm-common`
