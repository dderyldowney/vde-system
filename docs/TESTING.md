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
- **zsh** (>=5.0): Shell interpreter (all scripts use zsh)
- **kcov** (>=40): Code coverage for shell scripts
- **docker** (>=20.10.0): For integration tests
- **jq** (>=1.5): JSON processing for AI API tests

### Optional Tools
- **yamllint** (>=1.27.0): YAML linting
- **shfmt** (>=3.6.0): Shell script formatter (for local use)

### Installation
```bash
# macOS
brew install zsh kcov jq
pip install yamllint
go install mvdan.cc/sh/v3/cmd/shfmt@latest

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y zsh kcov jq

# Install shfmt and yamllint via go/python
go install mvdan.cc/sh/v3/cmd/shfmt@latest
pip install yamllint

# Verify installation
zsh --version
kcov --version
jq --version
yamllint --version  # optional
shfmt --version     # optional
```

### Note on Shell Checking
The VDE codebase uses **zsh-specific syntax** that is not compatible with traditional shellcheck/shfmt tools:
- **ShellCheck** does NOT support zsh - use `zsh -n script.sh` for syntax checking instead
- **shfmt** has limited zsh support - can be run locally for basic formatting but may not handle all zsh features
- CI uses native `zsh -n` for syntax validation (skips test_integration_comprehensive.sh which uses valid multi-line arrays that zsh -n doesn't parse well)

## Code Coverage

For detailed coverage documentation, see [COVERAGE.md](COVERAGE.md).

### Quick Coverage Commands
```bash
# Run all tests with coverage
make test-coverage

# Run unit tests with coverage
make coverage-unit

# Run integration tests with coverage
make coverage-integration

# View coverage report in browser
make coverage-view
```

### Coverage Output
- **Report Location**: `coverage/merged/index.html`
- **Format**: HTML with line-by-line coverage highlighting
- **CI Artifacts**: Uploaded as `coverage-report` (30-day retention)

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
1. **Linting** (~2 min): zsh syntax checking, yamllint
2. **Unit Tests** (~3 min): Three-tier library tests
3. **Integration Tests** (~5 min): AI parsing, usage patterns
4. **Comprehensive Tests** (~20 min): Extended parser, commands, and integration tests
5. **Coverage** (~10 min): Code coverage with kcov
6. **Docker Build** (~15 min): Random VM build + SSH connectivity test
7. **Real AI API** (~2 min): Actual API calls to Anthropic-compatible endpoints (requires credentials)
8. **Summary**: Aggregate results

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

For detailed coverage information and reports, see [COVERAGE.md](COVERAGE.md).

| Component | Target Coverage | Status |
|-----------|----------------|--------|
| vm-common | 90% | 🟡 In Progress |
| vde-parser | 85% | 🟡 In Progress |
| vde-commands | 80% | 🟡 In Progress |
| Integration | All intents | 🟡 In Progress |
| Docker | Statistical (100% over ~25 runs) | 🟡 Active |
| **Overall** | 85% | 🟡 In Progress |

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
# Check zsh script syntax
zsh -n scripts/lib/vm-common

# Fix yamllint issues
yamllint .github/workflows/vde-ci.yml

# Run shfmt locally (optional - for basic formatting)
shfmt -w scripts/**/*.sh tests/**/*.sh
```

### Coverage Issues
```bash
# Run coverage manually to see detailed output
./scripts/coverage.sh all

# Check coverage report
cat coverage/merged/index.html | grep -o 'covered"[^>]*>\\K[0-9.]+'

# View in browser
make coverage-view
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

1. **Follow the style guide**: See [STYLE_GUIDE.md](../STYLE_GUIDE.md) for coding standards
2. **Write tests for new features**: All new scripts need unit tests
3. **Run tests before committing**: Use `make test` for full validation
4. **Mock external dependencies**: Don't rely on real Docker in unit tests
5. **Test error paths**: Verify failure modes work correctly
6. **Keep tests fast**: Unit tests should run in seconds, not minutes

## CI Workflow Details

The GitHub Actions workflow (`.github/workflows/vde-ci.yml`) includes:

### 1. Linting Job
- Runs `zsh -n` on all zsh scripts for syntax validation
- Skips test_integration_comprehensive.sh (valid zsh but zsh -n doesn't handle multi-line arrays well)
- Validates YAML files with yamllint
- Note: shfmt is NOT run in CI due to zsh compatibility issues

### 2. Unit Tests Job
- Tests vm-common library (VM discovery, port allocation, name resolution)
- Tests vde-parser library (intent detection, entity extraction, plan generation)
- Tests vde-commands library (VM listing, validation, alias resolution)
- Tests vde-ai-api library (27 assertions covering env vars, API integration)

### 3. Integration Tests Job
- Tests pattern-based parsing (all 8 supported intents)
- Tests daily usage patterns (VM lifecycle, full stack setup)
- Tests complex multi-VM commands

### 4. Comprehensive Tests Job
- Runs comprehensive vde-parser tests (500+ assertions)
- Runs comprehensive vde-commands tests (400+ assertions)
- Runs end-to-end integration tests (300+ assertions)

### 5. Coverage Job
- Installs kcov from source
- Runs all tests under kcov instrumentation
- Verifies tests pass before running with kcov
- Handles kcov exit codes properly (kcov may return non-zero even when tests pass)
- Generates merged HTML coverage report
- Uploads coverage as CI artifact (30-day retention)

### 6. Docker Build Job
- Selects ONE random VM from all 25 (18 languages + 7 services)
- Generates test SSH key pair
- Creates VM configuration
- Builds and starts Docker container
- Waits for container to be ready
- Tests SSH connectivity with retries (language VMs only)
- Verifies container functionality (user, shell, workspace, sudo)
- Displays container info and cleanup

### 7. Real AI API Job
- Checks for API credentials (ANTHROPIC_AUTH_TOKEN, ANTHROPIC_API_KEY, or CLAUDE_API_KEY)
- If credentials found, runs actual API calls to test AI integration
- Tests: simple commands, create VM, multiple VMs, complex natural language
- Skips gracefully if no credentials configured
- Supports third-party providers (e.g., Zhipu AI with custom BASE_URL and MODEL)

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
