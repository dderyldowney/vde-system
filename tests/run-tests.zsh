#!/usr/bin/env zsh
#===============================================================================
# VDE Test Runner - Industry Standard Tiered Testing
#
# Usage:
#   ./run-tests.zsh unit        # Fast unit tests (parser)
#   ./run-tests.zsh integration # CLI integration tests
#   ./run-tests.zsh e2e        # Full Docker/VM tests
#   ./run-tests.zsh all        # All tests
#===============================================================================

set -e

SCRIPT_DIR="${0:a:h}"
cd "${SCRIPT_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

run_unit() {
    echo -e "${GREEN}Running UNIT tests (parser, libraries)...${NC}"
    python3 -m behave \
        --tags=@unit \
        --tags=~@wip \
	--tags=~rebuild \
	--tags=~@requires-docker-host \
	--tags=~@docker-required \
        --format=pretty \
        features/core-infrastructure/parser.feature
}

run_integration() {
    echo -e "${GREEN}Running INTEGRATION tests (vde CLI, ssh-setup)...${NC}"
    python3 -m behave \
        --tags=@integration \
        --tags=~@wip \
	--tags=~@rebuild
	--tags=~@requires-docker-host \
	--tags=~@docker-required \
        --format=pretty \
        features/core-infrastructure/vde-ssh-commands.feature
}

run_e2e() {
    echo -e "${GREEN}Running E2E tests (Docker/VM workflows)...${NC}"
    python3 -m behave \
        --tags=@docker \
        --tags=~@wip \
	--tags=~@rebuild \
        --format=pretty \
        features/core-infrastructure/
}

run_all() {
    echo -e "${GREEN}Running ALL tests...${NC}"
    python3 -m behave \
        --tags=~@wip \
        --format=pretty \
        features/core-infrastructure/
}

# Main
case "${1:-all}" in
    unit)
        run_unit
        ;;
    integration)
        run_integration
        ;;
    e2e)
        run_e2e
        ;;
    all)
        run_all
        ;;
    *)
        echo "Usage: ${0} {unit|integration|e2e|all}"
        exit 1
        ;;
esac
