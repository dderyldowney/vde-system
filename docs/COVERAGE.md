# Code Coverage

VDE uses **kcov** for code coverage reporting of its shell scripts. Kcov instruments code without modification and generates detailed HTML reports.

## Quick Start

### Install kcov

```bash
# macOS
brew install kcov

# Ubuntu/Debian
sudo apt-get install kcov

# From source (other platforms)
git clone https://github.com/SimonKagstrom/kcov.git
cd kcov
cmake .
make
sudo make install
```

### Run Coverage

```bash
# Run all tests with coverage
make test-coverage

# Run unit tests only with coverage
make coverage-unit

# Run integration tests only with coverage
make coverage-integration

# View coverage report in browser
make coverage-view

# Clean coverage reports
make coverage-clean
```

## Coverage Directory Structure

After running `make test-coverage`, the following structure is created:

```
coverage/
├── test_vde_parser_comprehensive/
│   ├── index.html          # Individual test coverage
│   └── ...
├── test_vde_commands_comprehensive/
│   ├── index.html
│   └── ...
├── test_integration_comprehensive/
│   ├── index.html
│   └── ...
└── merged/
    ├── index.html          # Combined coverage report
    ├── vm-common.zsh.html   # Per-file coverage
    ├── vde-parser.zsh.html
    └── vde-commands.zsh.html
```

## Viewing Reports

### Command Line

```bash
# Open merged report in default browser
make coverage-view

# Or open directly
open coverage/merged/index.html        # macOS
xdg-open coverage/merged/index.html   # Linux
```

### HTML Report Contents

The merged report shows:
- **Overall coverage percentage**
- **Per-file coverage breakdown**
- **Line-by-line coverage highlighting**
  - Green: Covered
  - Red: Not covered
  - Yellow: Partially covered

## CI Integration

Coverage runs automatically in GitHub Actions CI:

- **Job**: `coverage`
- **Artifacts**: Coverage reports uploaded as `coverage-report` (retained 30 days)
- **Summary**: Coverage percentage displayed in CI output

### CI Output Example

```
╔════════════════════════════════════════════════════════════╗
║                  Code Coverage Report                       ║
╚════════════════════════════════════════════════════════════╝

Total Coverage: 87.5%
```

## Coverage Targets

| Component        | Target | Status |
|------------------|--------|--------|
| vm-common        | 90%    | 🟡     |
| vde-parser       | 85%    | 🟡     |
| vde-commands     | 80%    | 🟡     |
| **Overall**      | 85%    | 🟡     |

## Excluding Code from Coverage

Mark sections to exclude using `# TEST:END_TEST` comments:

```bash
# TEST:START_TEST - This section is excluded from coverage
some_test_helper_function() {
    # Test-only code
}
# TEST:END_TEST
```

## Filtering Coverage

The coverage script automatically excludes:
- `/usr/*` - System libraries
- `/opt/*` - Optional packages
- TEST:END_TEST regions - Test-only code

## Troubleshooting

### kcov not found

```bash
# Install kcov
brew install kcov        # macOS
sudo apt-get install kcov  # Ubuntu
```

### Coverage not merging

```bash
# Clean and retry
make coverage-clean
make test-coverage
```

### Permission denied on coverage script

```bash
chmod +x scripts/coverage.sh
```

### High memory usage during coverage

Reduce test scope:
```bash
# Run only unit tests with coverage
make coverage-unit
```

## Advanced Usage

### Running Coverage Script Directly

```bash
# All tests
./scripts/coverage.sh all

# Unit tests only
./scripts/coverage.sh unit

# Integration tests only
./scripts/coverage.sh integration

# Comprehensive tests only
./scripts/coverage.sh comprehensive
```

### Extracting Coverage from CI Artifacts

1. Go to Actions → Latest workflow run
2. Download `coverage-report` artifact
3. Extract and open `index.html`

## References

- **kcov GitHub**: https://github.com/SimonKagstrom/kcov
- **kcov Documentation**: https://simonkagstrom.github.io/kcov/
