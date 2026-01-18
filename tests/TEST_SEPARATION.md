# VDE Test Separation for CI/CD

## Overview

VDE tests are separated into two categories:

### Docker-Free Tests (Fast)
- **Location:** `/Users/dderyldowney/dev/tests/features/docker-free/`
- **Runner:** `./tests/run-bdd-fast.sh`
- **Duration:** ~1 second for all tests
- **Use Case:** CI/CD pipelines, quick validation, PR checks
- **Requirements:** None (no Docker needed)

### Docker-Required Tests (Slow)
- **Location:** `/Users/ddeyldowney/dev/tests/features/docker-required/`
- **Runner:** `./tests/run-bdd-tests.sh` (includes Docker)
- **Duration:** Several minutes (requires Docker containers)
- **Use Case:** Full integration testing, local development validation
- **Requirements:** Docker engine, Docker socket access

## Docker-Free Features (5)

1. **cache-system.feature** (15 scenarios)
   - Cache VM types, invalidation, persistence, lazy loading

2. **documented-development-workflows.feature** (30 scenarios)
   - Example workflows, daily workflows, troubleshooting examples

3. **vm-information-and-discovery.feature** (7 scenarios)
   - Listing VMs, checking VM existence, discovering VMs by alias

4. **natural-language-parser.feature** (22 scenarios)
   - Intent detection, VM name extraction, alias resolution

5. **shell-compatibility.feature** (16 scenarios)
   - Shell detection, associative arrays, script portability

**Total: 94 scenarios, 371 steps**

## Docker-Required Features (26)

All other features require Docker. These include:
- VM lifecycle management
- SSH configuration and key management
- Docker operations
- Container management
- Network operations
- Volume mounts
- Port allocation
- Template rendering with Docker
- SSH agent forwarding
- Productivity features

**Total: 418 scenarios, 1936+ steps**

## Running Tests Locally

### Run Docker-Free Tests (Fast)
```bash
cd /Users/dderyldowney/dev
./tests/run-bdd-fast.sh                    # All Docker-free tests
./tests/run-bdd-fast.sh cache-system      # Specific feature
./tests/run-bdd-fast.sh --verbose        # Verbose output
```

### Run Docker-Required Tests (Slow)
```bash
cd /Users/ddynedowney/dev
./tests/run-bdd-tests.sh                 # All tests (includes Docker setup)
./tests/run-bdd-tests.sh ssh-configuration  # Specific feature
./tests/run-bdd-tests.sh --include-docker # Include Docker-required tests
```

## CI/CD Integration

### GitHub Actions (Example)

```yaml
# Fast checks - run on every PR
name: Quick validation (Docker-free)
run: ./tests/run-bdd-fast.sh

# Full tests - run on merge to main
name: Full test suite (with Docker)
run: ./tests/run-bdd-tests.sh
```

### GitLab CI (Example)

```yaml
# Fast checks
docker-free-tests:
  stage: test
  script:
    - ./tests/run-bdd-fast.sh
  tags:
    - docker-free

# Full tests
docker-required-tests:
  stage: test
  script:
    - ./tests/run-bdd-tests.sh
  tags:
    - docker-required
```

## Tag Reference

Features use these tags for additional categorization:

- `@requires-docker-host` - Needs Docker daemon and container access
- `@requires-docker-ssh` - Needs SSH agent forwarding with Docker containers

## Test Organization Benefits

1. **Fast Feedback Loop:** Docker-free tests run in ~1 second, enabling quick PR validation
2. **Clear Separation:** Physical directory separation makes Docker requirements explicit
3. **CI/CD Optimization:** Docker-free tests can run in parallel without Docker-in-Docker issues
4. **Local Development:** Fast iteration on parsing/config logic without Docker overhead
5. **User Guide Preservation:** Features remain intact for documentation generation

## Status

- **Docker-Free Tests:** ✓ All passing (5 features, 94 scenarios, 371 steps)
- **Docker-Required Tests:** Ready to run (26 features, 418 scenarios, 1936+ steps)

## Notes

- The fast test runner (`run-bdd-fast.sh`) does NOT use tag filtering anymore - it only tests the `docker-free/` directory
- Docker-required tests are run with `run-bdd-tests.sh` with Docker support
- Tests can be run from within Docker containers with appropriate mounts and Docker socket access

## Local Testing Infrastructure

### Complete Local Testing

**Three test runners available for different needs:**

#### 1. Fast Tests (Config Only)
```bash
./tests/run-bdd-fast.sh
```
- Tests: Configuration, parsing, templates, shell compatibility
- Duration: ~1 second
- Touches: Nothing (doesn't run Docker)
- Use: Quick validation, PR checks, CI/CD

#### 2. Full Local Tests (Config + Docker)
```bash
./tests/run-local-bdd.sh
```
- Tests: ALL docker-required features
- Duration: ~5-15 minutes
- Touches: Test VMs (e2e-test-go, e2e-test-minio only)
- Preserves: Your VMs, configs, SSH keys
- Use: Full local verification before pushing code

#### 3. E2E User Journey (Complete User Experience)
```bash
./tests/run-e2e-with-ssh-backup.sh
```
- Tests: Complete user journey from "bare metal" through VM usage
- Touches: Your SSH keys (moved to ~/.ssh-vde-test-backup/, then restored)
- Preserves: Your existing VMs, configs
- Use: Verify complete user experience end-to-end

---

## Docker-in-Docker Limitation

### Why Some Tests Have @requires-docker-host Tag

**Problem:** GitHub Actions runners can't test these scenarios
- Docker-in-Dinner container → Host Docker path mismatch
- Container path: `/vde/projects/python`
- Host path: `/Users/dderyldowney/dev/projects/python`

**Solution:** These tests run locally on your Mac (or self-hosted runner)

---

## Config Preservation Mechanism

### Detection Logic

The test code uses `VDE_ROOT_DIR` environment variable:

**In Docker Container:**
```python
VDE_ROOT_DIR = "/vde"
IN_CONTAINER = True
```

**Locally (Your Mac):**
```python
VDE_ROOT_DIR = "/Users/dderyldowney/dev"
IN_CONTAINER = False
```

### Config Deletion Gating

**In Container:**
```python
if IN_CONTAINER:
    # OK to delete (these are copies in the container)
    delete docker-compose.yml
```

**Locally:**
```python
if IN_CONTAINER:
    # Skip deletion (preserve user's actual configs)
    pass
```

This ensures your configs are never deleted when running tests locally.
