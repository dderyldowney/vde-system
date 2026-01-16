#!/usr/bin/env zsh
# VDE BDD Test Runner
# Runs BDD feature tests inside the dedicated test container
#
# Usage:
#   ./tests/run-bdd-tests.sh              # Run all BDD tests
#   ./tests/run-bdd-tests.sh vm-lifecycle # Run specific feature
#   ./tests/run-bdd-tests.sh --no-build   # Skip container rebuild
#   ./tests/run-bdd-tests.sh --shell      # Drop into container shell

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Container configuration
BDD_CONTAINER_NAME="vde-bdd-test"
BDD_IMAGE_NAME="vde-bdd-tester"
BDD_DOCKERFILE="$PROJECT_ROOT/tests/docker/bdd-test/Dockerfile"

# Test configuration
REBUILD_CONTAINER=true
SPECIFIC_FEATURE=""
DROP_IN_SHELL=false
VERBOSE_OUTPUT=false
# Default: skip @requires-docker-host tests since they can't pass in Docker-in-Docker
# These are tested by the shell suite (tests/integration/docker-vm-lifecycle.test.sh)
BEHAVE_TAGS="--tags=~requires-docker-host"

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    BOLD=''
    RESET=''
fi

# =============================================================================
# USAGE
# =============================================================================

show_usage() {
    cat <<EOF
${BOLD}VDE BDD Test Runner${RESET}

Run BDD feature tests inside the dedicated test container.

${BOLD}Usage:${RESET}
  $0 [OPTIONS] [FEATURE]

${BOLD}Arguments:${RESET}
  FEATURE         Specific feature file to test (e.g., vm-lifecycle, port-management)
                  If omitted, runs all feature files

${BOLD}Options:${RESET}
  --no-build      Skip rebuilding the container
  --rebuild       Force rebuild the container (default)
  --include-docker Include @requires-docker-host scenarios (will fail in Docker-in-Docker)
  --shell         Drop into container shell instead of running tests
  -v, --verbose   Enable verbose output
  -h, --help      Show this help message

${BOLD}Examples:${RESET}
  $0                        # Run BDD tests (Docker host tests skipped by default)
  $0 vm-lifecycle            # Run only vm-lifecycle.feature
  $0 --no-build              # Skip container rebuild
  $0 --shell                 # Drop into container shell

${BOLD}Available Features:${RESET}
EOF
    # List all feature files
    for feature in "$SCRIPT_DIR/features"/*.feature(N); do
        if [[ -f "$feature" ]]; then
            local name="${feature:t:r}"
            echo "  $name"
        fi
    done
    cat <<EOF

${BOLD}Environment Variables:${RESET}
  VDE_BDD_IMAGE    Override Docker image name
  VDE_BDD_NO_CACHE Set to '1' to use cached Docker build

${BOLD}Tags:${RESET}
  @requires-docker-host  Scenarios needing real Docker host (SKIPPED by default)
                        These are tested by tests/integration/docker-vm-lifecycle.test.sh
                        Use --include-docker to attempt running them (will fail in Docker-in-Docker)

EOF
}

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-build)
                REBUILD_CONTAINER=false
                shift
                ;;
            --rebuild)
                REBUILD_CONTAINER=true
                shift
                ;;
            --include-docker)
                BEHAVE_TAGS=""
                echo -e "${YELLOW}Note: Including @requires-docker-host tests${RESET}"
                echo -e "${YELLOW}      These will FAIL in Docker-in-Docker but are tested by shell suite${RESET}"
                shift
                ;;
            --shell)
                DROP_IN_SHELL=true
                shift
                ;;
            -v|--verbose)
                VERBOSE_OUTPUT=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                echo -e "${RED}Error: Unknown option: $1${RESET}" >&2
                echo ""
                show_usage
                exit 1
                ;;
            *)
                SPECIFIC_FEATURE="$1"
                shift
                ;;
        esac
    done
}

# =============================================================================
# DOCKER FUNCTIONS
# =============================================================================

build_container() {
    echo -e "${BLUE}Building BDD test container...${RESET}"

    local build_args=""
    if [[ "${VDE_BDD_NO_CACHE:-}" == "1" ]]; then
        build_args="--no-cache"
    fi

    if docker build -t "$BDD_IMAGE_NAME" \
        -f "$BDD_DOCKERFILE" \
        $build_args \
        --build-arg "VDE_ROOT=/vde" \
        "$PROJECT_ROOT" 2>&1 | tee /tmp/vde-bdd-build.log; then
        echo -e "${GREEN}✓ Container built successfully${RESET}"
        return 0
    else
        echo -e "${RED}✗ Container build failed${RESET}"
        echo "Check /tmp/vde-bdd-build.log for details"
        return 1
    fi
}

ensure_container_image() {
    if ! docker image inspect "$BDD_IMAGE_NAME" &>/dev/null; then
        echo -e "${YELLOW}Container image not found. Building...${RESET}"
        build_container
    elif [[ "$REBUILD_CONTAINER" == "true" ]]; then
        echo -e "${YELLOW}Rebuilding container (use --no-build to skip)...${RESET}"
        build_container
    else
        echo -e "${GREEN}Using existing container image${RESET}"
    fi
}

run_tests() {
    echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}Running VDE BDD Tests${RESET}"
    echo -e "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
    echo ""

    local behave_args=""
    if [[ -n "$SPECIFIC_FEATURE" ]]; then
        echo -e "${BLUE}Running specific feature: ${SPECIFIC_FEATURE}${RESET}"
        behave_args="tests/features/${SPECIFIC_FEATURE}.feature"
    else
        echo -e "${BLUE}Running all features${RESET}"
        behave_args="tests/features/"
    fi

    # Run behave in container
    local run_cmd="behave --format pretty --no-color"

    if [[ "$VERBOSE_OUTPUT" == "true" ]]; then
        run_cmd="$run_cmd --verbose"
    fi

    # Add tag filters if specified
    if [[ -n "$BEHAVE_TAGS" ]]; then
        run_cmd="$run_cmd $BEHAVE_TAGS"
    fi

    run_cmd="$run_cmd $behave_args"

    echo ""
    # IMPORTANT: We do NOT mount configs/, scripts/, or tests/ to protect host files.
    # The Dockerfile COPYs these into the image, so tests use the copied versions.
    # Any "deletions" only affect the container's copies, not the host.
    # We only mount docker socket for container tests and a test workspace.
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$PROJECT_ROOT/tests/workspace:/vde/tests/workspace" \
        -e VDE_ROOT_DIR=/vde \
        -e PYTHONUNBUFFERED=1 \
        --network host \
        "$BDD_IMAGE_NAME" \
        zsh -lc "cd /vde && $run_cmd"

    local exit_code=$?

    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ All BDD tests passed!${RESET}"
    else
        echo -e "${RED}${BOLD}✗ Some BDD tests failed${RESET}"
    fi

    return $exit_code
}

drop_into_shell() {
    echo -e "${BLUE}Dropping into BDD test container shell...${RESET}"
    echo -e "Type ${BOLD}exit${RESET} to leave the shell"
    echo ""

    # Use copied files from image to protect host configs
    docker run --rm -it \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$PROJECT_ROOT/tests/workspace:/vde/tests/workspace" \
        -e VDE_ROOT_DIR=/vde \
        --network host \
        "$BDD_IMAGE_NAME" \
        zsh -i
}

cleanup() {
    # Remove any stopped test containers
    docker ps -a --filter "name=${BDD_CONTAINER_NAME}" --format '{{.Names}}' | \
        xargs -r docker rm -f &>/dev/null || true
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    parse_args "$@"

    # Trap to ensure cleanup
    trap cleanup EXIT

    # Ensure container image exists
    if ! ensure_container_image; then
        echo -e "${RED}Failed to prepare container image${RESET}"
        exit 1
    fi

    # Either drop into shell or run tests
    if [[ "$DROP_IN_SHELL" == "true" ]]; then
        drop_into_shell
    else
        if ! run_tests; then
            exit 1
        fi
    fi
}

main "$@"
