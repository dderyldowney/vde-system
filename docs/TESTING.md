# VDE Testing Guide

Complete guide for testing the VDE (Virtual Development Environment) system.

## Quick Start

### Run All Tests
```bash
# From repository root
make test
```

### Run Specific Test Suite
```bash
# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Linting only
make lint
```

## Prerequisites

### Required Tools
- **shellcheck** (>=0.8.0): Shell script static analysis
- **shfmt** (>=3.6.0): Shell script formatter
- **yamllint** (>=1.27.0): YAML linting
- **docker** (>=20.10.0): For integration tests

### Installation
```bash
# macOS
brew install shellcheck shfmt yamllint

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y shellcheck zsh

# Install shfmt and yamllint via go/python
go install mvdan.cc/sh/v3/cmd/shfmt@latest
pip install yamllint

# Verify installation
shellcheck --version
shfmt --version
yamllint --version
```

## Test Structure

```
tests/
├── unit/              # Unit tests for libraries
│   ├── test_vm_common.sh
│   ├── test_vde_parser.sh
│   └── test_vde_commands.sh
├── integration/       # Integration tests
│   ├── test_pattern_based_parsing.sh
│   ├── test_mocked_ai_parsing.sh
│   └── test_daily_usage_patterns.sh
├── fixtures/          # Test data
│   └── vm_types_minimal.conf
└── lib/               # Test utilities
    └── test_common.sh
```

## CI/CD Pipeline

### Triggers
- **Pull Requests**: Full test suite + linting
- **Push to main**: Full test suite + linting
- **Nightly (2 AM UTC)**: Full suite + random Docker build + SSH test
- **Manual**: Via GitHub Actions UI with VM selection options

### Jobs
1. **Linting** (~2 min): shellcheck, shfmt, yamllint
2. **Unit Tests** (~3 min): Three-tier library tests
3. **Integration Tests** (~5 min): AI parsing, usage patterns
4. **Docker Build** (~15 min): Random VM build + SSH connectivity test
5. **Summary**: Aggregate results

### Random VM Selection
Each CI run selects ONE random VM from ALL 25 VMs using a rounded number generator:
- **18 Languages**: c, cpp, asm, python, rust, js, csharp, ruby, go, java, kotlin, swift, php, scala, r, lua, flutter, elixir, haskell
- **7 Services**: postgres, redis, mongodb, nginx, couchdb, mysql, rabbitmq

This ensures statistical coverage - every VM has an equal chance of being tested over time.

### SSH Testing
- Generates temporary SSH key pair during CI
- Tests SSH connection to built container
- Verifies: user (devuser), shell (zsh), workspace, sudo access
- Cleans up test artifacts after testing

## Coverage Metrics

| Component | Target Coverage | Status |
|-----------|----------------|--------|
| vm-common | 90% | 🟡 In Progress |
| vde-parser | 85% | 🟡 In Progress |
| vde-commands | 80% | 🟡 In Progress |
| Integration | All intents | 🟡 In Progress |
| Docker | Statistical (100% over ~25 runs) | 🟡 Active |

## Troubleshooting

### Tests Failing Locally
```bash
# Ensure all dependencies are sourced
cd ~/dev
source scripts/lib/vm-common

# Check test file permissions
chmod +x tests/**/*.sh

# Run with verbose output
./tests/unit/test_vm_common.sh -v
```

### Docker Build Tests Failing
```bash
# Check Docker daemon
docker ps

# Clean up old containers
docker system prune -f

# Test specific VM manually
./scripts/create-virtual-for python
./scripts/start-virtual python
```

### SSH Connection Tests Failing
```bash
# Verify SSH key generation
ssh-keygen -t ed25519 -f /tmp/test_key -N ""

# Check container is running
docker ps | grep python-dev

# Test SSH manually
ssh -i /tmp/test_key -p 2200 devuser@localhost hostname
```

### Linting Errors
```bash
# Fix shell formatting issues
shfmt -w scripts/**/*.sh

# Run shellcheck to see specific issues
shellcheck scripts/lib/vm-common
```

## Test Utilities

The `tests/lib/test_common.sh` file provides:

### Assertion Functions
- `assert_equals expected actual message`
- `assert_contains haystack needle message`
- `assert_success exit_code message`
- `assert_file_exists file message`
- `assert_dir_exists dir message`

### Test Suite Functions
- `test_suite_start name` - Start a test suite
- `test_suite_end name` - End a test suite and show results
- `test_section name` - Print a section header
- `setup_test_env` - Setup test environment
- `teardown_test_env` - Cleanup test environment

## Best Practices

1. **Write tests for new features**: All new scripts need unit tests
2. **Run tests before committing**: Use `make test` for full validation
3. **Mock external dependencies**: Don't rely on real Docker in unit tests
4. **Test error paths**: Verify failure modes work correctly
5. **Keep tests fast**: Unit tests should run in seconds, not minutes

## CI Workflow Details

The GitHub Actions workflow (`.github/workflows/vde-ci.yml`) includes:

### 1. Linting Job
- Runs shellcheck on all shell scripts
- Checks formatting with shfmt
- Validates YAML files with yamllint

### 2. Unit Tests Job
- Tests vm-common library (VM discovery, port allocation, name resolution)
- Tests vde-parser library (intent detection, entity extraction, plan generation)
- Tests vde-commands library (VM listing, validation, alias resolution)

### 3. Integration Tests Job
- Tests pattern-based parsing (all 8 supported intents)
- Tests daily usage patterns (VM lifecycle, full stack setup)
- Tests complex multi-VM commands

### 4. Docker Build Job
- Selects ONE random VM from all 25 (18 languages + 7 services)
- Generates test SSH key pair
- Creates VM configuration
- Builds and starts Docker container
- Waits for container to be ready
- Tests SSH connectivity with retries
- Verifies container functionality (user, shell, workspace, sudo)
- Displays container info and cleanup

## Manual CI Testing

You can trigger the CI workflow manually with specific VM selection:

1. Go to GitHub Actions tab
2. Select "VDE CI Pipeline" workflow
3. Click "Run workflow"
4. Optionally specify a VM (e.g., `python`, `postgres`, `go`, `redis`)
5. Click "Run workflow" to start

## Statistical Coverage

With 25 VMs and random selection:
- After ~10 runs: ~33% chance each VM was tested at least once
- After ~25 runs: ~64% chance each VM was tested at least once
- After ~50 runs: ~87% chance each VM was tested at least once
- After ~100 runs: ~98% chance each VM was tested at least once

## Contributing Tests

When adding new features:

1. **Add unit tests** for new functions in appropriate test file
2. **Add integration tests** for new user-facing features
3. **Update this document** if test structure changes
4. **Run `make test`** before committing to ensure all tests pass
