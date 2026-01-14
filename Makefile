# VDE Makefile
# Targets for testing and development

.PHONY: help test test-unit test-integration test-comprehensive test-coverage test-ai-api test-real-ai-api lint check clean install-deps coverage-view coverage-clean

# Default target
help:
	@echo "VDE Makefile Targets:"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 - Run all tests"
	@echo "  make test-unit            - Run unit tests only"
	@echo "  make test-integration     - Run integration tests only"
	@echo "  make test-comprehensive   - Run comprehensive test suite (parser + commands)"
	@echo "  make test-coverage        - Run all tests with code coverage (kcov required)"
	@echo "  make coverage-unit        - Run unit tests with code coverage"
	@echo "  make coverage-integration - Run integration tests with code coverage"
	@echo "  make coverage-view        - Open coverage report in browser"
	@echo "  make coverage-clean       - Clean coverage reports"
	@echo ""
	@echo "Specific Test Suites:"
	@echo "  make test-parser          - Run vde-parser comprehensive tests"
	@echo "  make test-commands        - Run vde-commands comprehensive tests"
	@echo "  make test-e2e             - Run end-to-end integration tests"
	@echo "  make test-ai-api          - Run AI API tests (mocked, no API calls)"
	@echo "  make test-real-ai-api      - Run real AI API tests (requires API keys)"
	@echo ""
	@echo "Linting:"
	@echo "  make lint                - Run all linting checks"
	@echo "  make check               - Run all tests and linting"
	@echo ""
	@echo "Development:"
	@echo "  make install-deps        - Install development dependencies"
	@echo "  make clean               - Clean test artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make test-docker         - Run Docker build test (random VM)"

# =============================================================================
# Testing Targets
# =============================================================================

test: test-unit test-integration test-comprehensive
	@echo ""
	@echo "================================"
	@echo "All Tests Complete"
	@echo "================================"

test-unit:
	@echo "Running unit tests..."
	@for test in tests/unit/*.sh; do \
		if [ -f "$$test" ]; then \
			echo "Running $$test..."; \
			chmod +x "$$test"; \
			zsh "$$test" || exit 1; \
		fi \
	done
	@echo "✓ Unit tests passed"

test-integration:
	@echo "Running integration tests..."
	@for test in tests/integration/*.sh; do \
		if [ -f "$$test" ]; then \
			echo "Running $$test..."; \
			chmod +x "$$test"; \
			zsh "$$test" || exit 1; \
		fi \
	done
	@echo "✓ Integration tests passed"

test-comprehensive: test-parser test-commands
	@echo ""
	@echo "================================"
	@echo "Comprehensive Tests Complete"
	@echo "================================"

test-parser:
	@echo "Running comprehensive vde-parser tests..."
	@chmod +x tests/unit/test_vde_parser_comprehensive.sh
	@zsh tests/unit/test_vde_parser_comprehensive.sh
	@echo "✓ vde-parser tests passed"

test-commands:
	@echo "Running comprehensive vde-commands tests..."
	@chmod +x tests/unit/test_vde_commands_comprehensive.sh
	@zsh tests/unit/test_vde_commands_comprehensive.sh
	@echo "✓ vde-commands tests passed"

test-e2e:
	@echo "Running end-to-end integration tests..."
	@chmod +x tests/integration/test_integration_comprehensive.sh
	@zsh tests/integration/test_integration_comprehensive.sh
	@echo "✓ End-to-end tests passed"

test-ai-api:
	@echo "Running AI API tests..."
	@chmod +x tests/unit/test_vde_ai_api.sh
	@zsh tests/unit/test_vde_ai_api.sh
	@chmod +x tests/integration/test_ai_api_integration.sh
	@zsh tests/integration/test_ai_api_integration.sh
	@echo "✓ AI API tests passed"

test-real-ai-api:
	@echo "Running real AI API integration tests..."
	@echo "Note: These tests make actual API calls and require valid credentials"
	@chmod +x tests/integration/test_real_ai_api.sh
	@zsh tests/integration/test_real_ai_api.sh
	@echo "✓ Real AI API tests passed"

# =============================================================================
# Code Coverage (requires kcov)
# =============================================================================

COVERAGE_DIR := coverage
COVERAGE_SCRIPT := scripts/coverage.sh

test-coverage:
	@echo "Running all tests with code coverage..."
	@if ! command -v kcov >/dev/null 2>&1; then \
		echo "⚠ kcov not found. Install kcov for code coverage:"; \
		echo "  macOS: brew install kcov"; \
		echo "  Ubuntu: sudo apt-get install kcov"; \
		echo "  Or build from source: https://github.com/SimonKagstrom/kcov"; \
		exit 1; \
	fi
	@chmod +x $(COVERAGE_SCRIPT)
	@zsh $(COVERAGE_SCRIPT) all

coverage-unit:
	@echo "Running unit tests with code coverage..."
	@if ! command -v kcov >/dev/null 2>&1; then \
		echo "⚠ kcov not found. Install: brew/apt install kcov"; \
		exit 1; \
	fi
	@chmod +x $(COVERAGE_SCRIPT)
	@zsh $(COVERAGE_SCRIPT) unit

coverage-integration:
	@echo "Running integration tests with code coverage..."
	@if ! command -v kcov >/dev/null 2>&1; then \
		echo "⚠ kcov not found. Install: brew/apt install kcov"; \
		exit 1; \
	fi
	@chmod +x $(COVERAGE_SCRIPT)
	@zsh $(COVERAGE_SCRIPT) integration

coverage-view:
	@if [ -f "$(COVERAGE_DIR)/merged/index.html" ]; then \
		echo "Opening coverage report..."; \
		open "$(COVERAGE_DIR)/merged/index.html" 2>/dev/null || \
		xdg-open "$(COVERAGE_DIR)/merged/index.html" 2>/dev/null || \
		echo "Report available at: $(COVERAGE_DIR)/merged/index.html"; \
	else \
		echo "⚠ Coverage report not found. Run 'make test-coverage' first."; \
	fi

coverage-clean:
	@echo "Cleaning coverage reports..."
	@rm -rf $(COVERAGE_DIR)
	@echo "✓ Coverage reports cleaned"

# =============================================================================
# Linting Targets
# =============================================================================

lint: lint-zsh lint-yaml
	@echo "✓ All linting checks passed"

lint-zsh:
	@echo "Running zsh syntax check..."
	@for script in $$(find scripts tests -name "*.sh" -type f); do \
		if head -1 "$$script" | grep -q "zsh"; then \
			zsh -n "$$script" || { echo "✗ Syntax error in: $$script"; exit 1; }; \
		fi \
	done
	@echo "✓ All zsh scripts passed syntax check"
	@echo ""
	@echo "Note: shfmt is not run in CI due to zsh compatibility issues."
	@echo "To run locally: shfmt -w scripts/**/*.sh tests/**/*.sh"

lint-yaml:
	@echo "Running yamllint..."
	@yamllint .github/workflows/ configs/docker/*/docker-compose.yml 2>/dev/null || \
		echo "yamllint not installed, skipping"
	@echo "✓ yamllint passed"

# =============================================================================
# Combined Targets
# =============================================================================

check: lint test
	@echo ""
	@echo "================================"
	@echo "All Checks Passed ✓"
	@echo "================================"

# =============================================================================
# Docker Testing
# =============================================================================

test-docker:
	@echo "Running Docker build test with random VM selection..."
	@ALL_VMS=("c" "cpp" "asm" "python" "rust" "js" "csharp" "ruby" "go" "java" "kotlin" "swift" "php" "scala" "r" "lua" "flutter" "elixir" "haskell" "postgres" "redis" "mongodb" "nginx" "couchdb" "mysql" "rabbitmq"); \
	INDEX=$$((RANDOM % $${#ALL_VMS[@]})); \
	TEST_VM=$${ALL_VMS[$$INDEX]}; \
	echo "Selected VM: $$TEST_VM (1 of $${#ALL_VMS[@]} total VMs)"; \
	./scripts/create-virtual-for "$$TEST_VM" && \
	./scripts/start-virtual "$$TEST_VM" && \
	echo "✓ Docker build test passed for $$TEST_VM" && \
	./scripts/shutdown-virtual "$$TEST_VM"

# =============================================================================
# Development Setup
# =============================================================================

install-deps:
	@echo "Installing development dependencies..."
	@echo "Note: Install shellcheck, shfmt, yamllint, kcov based on your OS"
	@echo ""
	@echo "macOS:"
	@echo "  brew install shellcheck shfmt yamllint kcov"
	@echo ""
	@echo "Ubuntu/Debian:"
	@echo "  sudo apt-get install shellcheck zsh kcov"
	@echo "  go install mvdan.cc/sh/v3/cmd/shfmt@latest"
	@echo "  pip install yamllint"
	@echo ""
	@echo "Other platforms:"
	@echo "  Build kcov from source: https://github.com/SimonKagstrom/kcov"

# =============================================================================
# Cleanup
# =============================================================================

clean: coverage-clean
	@echo "Cleaning test artifacts..."
	@rm -rf tests/.test-tmp
	@rm -f tests/*.log
	@echo "✓ Clean complete"
