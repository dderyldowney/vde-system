# Test Suite Status - March 3, 2026

## Summary
- **Passed**: 134+ scenarios (depends on test run)
- **Failed**: 2 scenarios (test isolation issue in SSH config)
- **Error**: ~31 scenarios (undefined steps - need implementation)
- **Parser Tests**: 46 scenarios (tagged @unit)
- **VDE SSH Commands**: 8 scenarios (tagged @integration) - ALL PASSING

## Test Structure (Tiered - Industry Standard)

### Tier 1: Unit Tests (@unit) - Fast, No Docker
- `parser.feature` - Natural language parser tests (46 scenarios)
- Environment: `environment.unit.py` - Minimal setup

### Tier 2: Integration Tests (@integration) - vde CLI Only
- `vde-ssh-commands.feature` - SSH setup CLI (8 scenarios) ✓ ALL PASSING
- Environment: `environment.integration.py` - Test network only

### Tier 3: Docker Tests (@docker) - Full VM Environment
- `ssh-configuration.feature` - SSH config (30 scenarios)
- `docker-operations.feature` - Docker operations
- `installation-setup.feature` - Installation tests
- Environment: Full Docker cleanup and VM setup

### Deferred (docker-required/)
- All scenarios require running VMs - need step implementations
- Not part of core test suite

## Test Execution

```bash
# Run unit tests only (fast - parser)
python3 -m behave --tags=@unit tests/features/

# Run integration tests (vde CLI)
python3 -m behave --tags=@integration tests/features/

# Run docker tests (full environment)
python3 -m behave --tags=@docker tests/features/

# Run all core tests
python3 -m behave tests/features/core-infrastructure/

# Or use test runner
./tests/run-tests.sh unit|integration|e2e|all
```

---

## FAILED SCENARIOS (2 - Test Isolation)

### SSH Configuration Tests
- "Merge preserves user's custom SSH settings" - Intermittent
- "Create backup of known_hosts before cleanup" - Intermittent

**Fix**: Clean up ~/.ssh/vde/ before running tests

---

## ERROR SCENARIOS (31 total - Undefined Steps)

### Core-Infrastructure
| Feature | Erroring Scenarios | Status |
|---------|-------------------|--------|
| Installation and Initial Setup | First time creation experience | Undefined: "I run vde-create" |
| SSH Configuration | Generate VM-to-VM SSH config entries | Undefined: "I reload VM types" |

### Docker-Required (Not in Core Suite)
- Configuration Management (9)
- SSH Agent Automatic Setup (5)
- SSH Agent External Git Operations (10)
- SSH Agent Forwarding VM-to-VM (10)
- SSH Agent VM-to-Host Communication (12)
- SSH and Remote Access (12)

---

## UNDEFINED STEP PATTERNS (29 total)

See original report for full list. These are primarily needed for docker-required features.

---

## NOTES
- Parser tests are @unit - no Docker overhead
- SSH command tests are @integration - minimal setup
- Core tests should run in <2 minutes with tiered execution
- Original docker-required features deferred to future implementation
