# Test Suite Fixes - Remaining Work

## Completed ✅
- CI/CD timeout extensions (commit `d871661`)
- vde-health library created
- Docker-free tests: 165/165 passing (100%)
- base-dev.Dockerfile oh-my-zsh fix
- YAML import error fix (commit `21547c6`)
- Context attribute fixes (invalid_vm_name, VM name defaults)
- Network name references fixed (vde → dev) (commit `f977f3a`)

## Remaining Issues - Docker-Required Tests

### 1. VM Startup Issues
**Symptom:** Containers not starting after start commands
```
- ASSERT FAILED: VM python is not running (docker ps check failed after 60s)
- ASSERT FAILED: PostgreSQL VM should be running
- ASSERT FAILED: Rust VM should be running
```
**Root Cause:** Containers either failing to build or not starting within timeout
**Files to Check:**
- `configs/docker/*/docker-compose.yml` - VM configurations
- Container logs: `docker logs <container-name>`
- Build process may need verification

### 2. Error Message Content Mismatches
**Symptom:** Tests expecting specific error messages that aren't generated
```
- ASSERT FAILED: Expected 'Cannot connect to Docker daemon' in error message
- ASSERT FAILED: Expected 'no space left on device' in error message
- ASSERT FAILED: No error message available
```
**Root Cause:** Tests simulate error scenarios but real commands don't produce expected messages
**Files to Fix:**
- `tests/features/steps/debugging_steps.py` - Error message assertion steps
- May need to mock error conditions or adjust assertions

### 3. Test State/Setup Issues
**Symptom:** Steps expecting state that wasn't set by previous steps
```
- ASSERT FAILED: docker_command flag was not set by previous step
- ASSERT FAILED: No error message was captured
- ASSERT FAILED: No rebuild output available
```
**Root Cause:** GIVEN steps not setting context flags properly
**Files to Fix:**
- `tests/features/steps/vm_docker_steps.py` - Add context flag initialization
- `tests/features/steps/docker_operations_steps.py` - Add output capture

### 4. Container Creation/Build Failures
**Symptom:** VMs with exit code 100 or 1
```
- rust-dev: Exited (1)
- zig-dev, rabbitmq, couchdb, c-dev: Exited (100)
```
**Root Cause:** Docker build issues, possibly:
- Microsoft apt repos (403/no longer signed) for csharp
- Language-specific installation failures
**Files to Check:**
- `configs/docker/csharp/docker-compose.yml` - Microsoft repo issues
- Language-specific Dockerfiles

### 5. SSH Connection Issues
**Symptom:** SSH not accessible within timeout
**Root Cause:** Containers not healthy or SSH daemon not starting
**Files to Check:**
- `configs/docker/base-dev.Dockerfile` - SSH configuration
- Timeout values in `scripts/lib/vde-constants`

## Quick Fixes Needed

### High Priority (Block Many Tests)
1. **Fix docker_command flag** - Add `context.docker_command = True` in appropriate WHEN step
2. **Fix output capture** - Ensure `context.last_output` and `context.last_error` are always set
3. **Fix container startup** - Debug why python/rust VMs aren't starting

### Medium Priority
4. **Fix error message tests** - Either mock errors or adjust expected messages
5. **Fix Microsoft repos** - Remove or fix csharp configuration

### Lower Priority
6. **Improve test isolation** - Better setup/teardown between scenarios
7. **Add test retry logic** for transient failures

## Test Commands

```bash
# Run specific feature
behave --format pretty tests/features/docker-required/docker-operations.feature

# Check container logs
docker logs <container-name>

# Check what's running
docker ps -a

# Clean slate
docker ps -aq | xargs -r docker rm -f
rm -rf .cache
```

## Recent Commits for Reference
- `d871661` - feat: extend CI/CD timeouts and add container health check library
- `21547c6` - fix: resolve assertion errors in docker-required tests
- `f977f3a` - fix: correct network name references in tests (vde → dev)
