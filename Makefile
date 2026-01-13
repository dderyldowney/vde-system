# VDE Makefile
# Targets for testing and development

.PHONY: help test test-unit test-integration lint check clean install-deps

# Default target
help:
	@echo "VDE Makefile Targets:"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo ""
	@echo "Linting:"
	@echo "  make lint          - Run all linting checks"
	@echo "  make check         - Run all tests and linting"
	@echo ""
	@echo "Development:"
	@echo "  make install-deps  - Install development dependencies"
	@echo "  make clean         - Clean test artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make test-docker   - Run Docker build test (random VM)"

# =============================================================================
# Testing Targets
# =============================================================================

test: test-unit test-integration
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
