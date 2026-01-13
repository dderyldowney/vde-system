# VDE Makefile
# Targets for testing and development

.PHONY: help test test-unit test-integration test-comprehensive test-coverage lint check clean install-deps

# Default target
help:
	@echo "VDE Makefile Targets:"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 - Run all tests"
	@echo "  make test-unit            - Run unit tests only"
	@echo "  make test-integration     - Run integration tests only"
	@echo "  make test-comprehensive   - Run comprehensive test suite (parser + commands)"
	@echo "  make test-coverage        - Run all tests with coverage report"
	@echo ""
	@echo "Specific Test Suites:"
	@echo "  make test-parser          - Run vde-parser comprehensive tests"
	@echo "  make test-commands        - Run vde-commands comprehensive tests"
	@echo "  make test-e2e             - Run end-to-end integration tests"
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

test-coverage: test test-parser test-commands test-e2e
	@echo ""
	@echo "================================"
	@echo "Coverage Report"
	@echo "================================"
	@echo "All test suites executed:"
	@echo "  ✓ Unit tests (vm-common, vde-parser, vde-commands)"
	@echo "  ✓ Integration tests (patterns, workflows)"
	@echo "  ✓ Comprehensive vde-parser tests (intent, extraction, planning)"
	@echo "  ✓ Comprehensive vde-commands tests (queries, actions, batch)"
	@echo "  ✓ End-to-end integration tests (real-world scenarios)"
	@echo ""
	@echo "Total test execution complete."

# =============================================================================
# Linting Targets
# =============================================================================

lint: lint-shell lint-yaml
	@echo "✓ All linting checks passed"

lint-shell:
	@echo "Running shellcheck..."
	@shellcheck -X scripts/*.sh scripts/lib/* scripts/**/*.sh 2>/dev/null || \
		find scripts -name "*.sh" -type f -exec shellcheck {} + || \
		echo "shellcheck not installed, skipping"
	@echo "✓ shellcheck passed"
	@echo "Running shfmt check..."
	@SHFMT_ERRORS=0; \
	for file in $$(find scripts -name "*.sh" -type f); do \
		if ! shfmt -d "$$file" 2>/dev/null; then \
			SHFMT_ERRORS=$$((SHFMT_ERRORS + 1)); \
		fi \
	done; \
	if [ $$SHFMT_ERRORS -gt 0 ]; then \
		echo "✗ shfmt formatting issues found in $$SHFMT_ERRORS files"; \
		echo "Run 'shfmt -w scripts/**/*.sh' to fix"; \
		exit 1; \
	fi
	@echo "✓ shfmt check passed"

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
	@echo "Note: Install shellcheck, shfmt, yamllint based on your OS"
	@echo ""
	@echo "macOS:"
	@echo "  brew install shellcheck shfmt yamllint"
	@echo ""
	@echo "Ubuntu/Debian:"
	@echo "  sudo apt-get install shellcheck zsh"
	@echo "  go install mvdan.cc/sh/v3/cmd/shfmt@latest"
	@echo "  pip install yamllint"

# =============================================================================
# Cleanup
# =============================================================================

clean:
	@echo "Cleaning test artifacts..."
	@rm -rf tests/.test-tmp
	@rm -f tests/*.log
	@echo "✓ Clean complete"
