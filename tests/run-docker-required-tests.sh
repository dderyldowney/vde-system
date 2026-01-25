#!/usr/bin/env zsh
# VDE Docker-Required Tests Runner
# Runs Docker-required BDD tests (container lifecycle, SSH, etc.) locally on your host
# Preserves your VM configurations while testing functionality
#
# Usage:
#   ./tests/run-docker-required-tests.sh        # Run all Docker-required tests
#   ./tests/run-docker-required-tests.sh vm-lifecycle  # Run specific feature
#   ./tests/run-docker-required-tests.sh --status       # Check test setup
#   ./tests/run-docker-required-tests.sh --json         # Run with JSON output
#   ./tests/run-docker-required-tests.sh --json -o FILE # JSON output to file
#
# IMPORTANT: This script tests on your LOCAL Docker Desktop
# Your VM configurations will NOT be deleted or modified.

set -e

# Project root can be set via environment variable
if [[ -n "$VDE_PROJECT_ROOT" ]]; then
    PROJECT_ROOT="$VDE_PROJECT_ROOT"
else
    # Auto-detect: script is in tests/, so root is one level up
    SCRIPT_DIR="$(dirname "$0")"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
fi

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
# PYTHON CACHE CLEARING
# =============================================================================

# Clear Python bytecode cache after tests complete
# This prevents stale code from persisting between test runs
# while allowing cache usage during test execution for speed
clear_python_cache() {
    local cache_cleared=0
    for pycache in $(find tests/features -name "__pycache__" -type d 2>/dev/null); do
        rm -rf "$pycache" 2>/dev/null && cache_cleared=$((cache_cleared + 1))
    done
    for pyc in $(find tests/features -name "*.pyc" 2>/dev/null); do
        rm -f "$pyc" 2>/dev/null && cache_cleared=$((cache_cleared + 1))
    done
    [[ $cache_cleared -gt 0 ]] && echo -e "${YELLOW}Cleared $cache_cleared Python cache entries${RESET}"
    return 0
}

# Ensure cache is cleared on exit (success or failure)
trap 'clear_python_cache' EXIT

# =============================================================================
# CHECKS
# =============================================================================

check_setup() {
    echo -e "${BLUE}Checking local test setup...${RESET}"

    local errors=0

    # Check if we're in the right directory
    if [[ ! -d "$PROJECT_ROOT/scripts" ]]; then
        echo -e "${RED}Error: Not in VDE project root${RESET}"
        ((errors++))
    fi

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running${RESET}"
        echo "Please start Docker Desktop and try again"
        ((errors++))
    else
        echo -e "${GREEN}✓ Docker is running${RESET}"
    fi

    # Check if Python 3 is available
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}Error: Python 3 not found${RESET}"
        ((errors++))
    else
        echo -e "${GREEN}✓ Python 3 available${RESET}"
    fi

    # Check if behave is installed
    if ! command -v behave >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Behave not installed${RESET}"
        echo "Installing behave..."
        pip3 install --user behave || {
            echo -e "${RED}Error: Failed to install behave${RESET}"
            echo "Try: pip3 install behave"
            ((errors++))
        }
    else
        echo -e "${GREEN}✓ Behave installed${RESET}"
    fi

    # Check if zsh is available
    if ! command -v zsh >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Zsh not found (recommended but not required)${RESET}"
    fi

    # Check for protected config files
    echo ""
    echo -e "${BLUE}Checking VM configurations...${RESET}"
    local config_count=$(find "$PROJECT_ROOT/configs/docker" -name "docker-compose.yml" 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ Found $config_count VM configurations${RESET}"
    echo -e "${BLUE}  Your VMs will be PRESERVED during testing${RESET}"

    if [[ $errors -gt 0 ]]; then
        echo ""
        echo -e "${RED}Setup check failed with $errors error(s)${RESET}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}✓ Setup check complete${RESET}"
    echo ""
}

# =============================================================================
# USAGE
# =============================================================================

show_usage() {
    cat <<EOF
${BOLD}VDE BDD Test Runner - Local Execution${RESET}

Run ALL BDD tests (including Docker operations) on your local machine.
Your VM configurations are preserved - tests verify functionality without
destroying your work.

${BOLD}Usage:${RESET}
  $0 [OPTIONS] [FEATURE]

${BOLD}Arguments:${RESET}
  FEATURE         Specific feature file to test (e.g., vm-lifecycle, ssh-configuration)
                  If omitted, runs all features

${BOLD}Options:${RESET}
  --check         Check test setup without running tests
  --no-build      Skip rebuilding test container (not used for local tests)
  --json          Output test results in JSON format
  -o FILE         Write JSON output to FILE (requires --json)
  -v, --verbose   Enable verbose output
  -h, --help      Show this help message

${BOLD}Examples:${RESET}
  $0                        # Run all tests locally
  $0 vm-lifecycle            # Run only VM lifecycle tests
  $0 ssh-configuration       # Run only SSH tests
  $0 --check                 # Check if environment is ready
  $0 --json                  # Run tests with JSON output
  $0 --json -o results.json  # Run tests, save JSON to file

${BOLD}What gets tested:${RESET}
  - Configuration parsing and generation
  - Natural language command processing
  - VM creation (using create-virtual-for)
  - VM start/stop operations
  - SSH agent setup and forwarding
  - Docker container operations
  - Port allocation and management
  - Shell compatibility (zsh, bash)

${BOLD}What is PRESERVED:${RESET}
  - Your VM configurations (docker-compose.yml files)
  - Your SSH configuration
  - Your project directories
  - Your Docker images

${BOLD}Environment Variables:${RESET}
  VDE_TEST_MODE=1           Set automatically for testing
  VDE_ROOT_DIR              Set automatically to project root

EOF
}

# =============================================================================
# MAIN
# =============================================================================

# Parse arguments
CHECK_ONLY=false
VERBOSE_OUTPUT=false
SPECIFIC_FEATURE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            CHECK_ONLY=true
            shift
            ;;
        --no-build)
            # Not used for local tests, but accepted for compatibility
            shift
            ;;
        -v|--verbose)
            VERBOSE_OUTPUT=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -o)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                JSON_OUTPUT_FILE="$2"
                shift 2
            else
                echo -e "${RED}Error: -o requires a filename argument${RESET}" >&2
                exit 1
            fi
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: Unknown option: $1${RESET}" >&2
            show_usage
            exit 1
            ;;
        *)
            SPECIFIC_FEATURE="$1"
            shift
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

# Run setup check
check_setup

if [[ "$CHECK_ONLY" == "true" ]]; then
    exit 0
fi

# Set up environment for local testing
export VDE_ROOT_DIR="$PROJECT_ROOT"
export VDE_TEST_MODE=1
export PATH="$PROJECT_ROOT/scripts:$PATH"

echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}Running VDE BDD Tests (LOCAL)${RESET}"
echo -e "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
echo ""

# Determine what to run
local behave_args="features/"
local feature_name="all features"

if [[ -n "$SPECIFIC_FEATURE" ]]; then
    # Check docker-required first, then docker-free
    if [[ -f "tests/features/docker-required/${SPECIFIC_FEATURE}.feature" ]]; then
        behave_args="tests/features/docker-required/${SPECIFIC_FEATURE}.feature"
        feature_name="$SPECIFIC_FEATURE (docker-required)"
    elif [[ -f "tests/features/docker-free/${SPECIFIC_FEATURE}.feature" ]]; then
        behave_args="tests/features/docker-free/${SPECIFIC_FEATURE}.feature"
        feature_name="$SPECIFIC_FEATURE (docker-free)"
    else
        echo -e "${RED}Error: Feature '${SPECIFIC_FEATURE}' not found${RESET}"
        echo "Available features in docker-required/:"
        ls tests/features/docker-required/*.feature 2>/dev/null | xargs -I {} basename {} .feature | sed 's/^/  - /' || echo "  (none)"
        echo "Available features in docker-free/:"
        ls tests/features/docker-free/*.feature 2>/dev/null | xargs -I {} basename {} .feature | sed 's/^/  - /' || echo "  (none)"
        exit 1
    fi
else
    echo -e "${BLUE}Running ALL features (docker-required + docker-free)${RESET}"
    behave_args="tests/features/"
    feature_name="all features"
fi

echo -e "${BLUE}Running: ${feature_name}${RESET}"
echo ""

# Save the feature path for later use
local feature_path="$behave_args"

# Add verbose flag if requested
if [[ "$VERBOSE_OUTPUT" == "true" ]]; then
    VERBOSE_FLAG="--verbose"
else
    VERBOSE_FLAG=""
fi

# Configure output format
local output_format="pretty"
if [[ "$JSON_OUTPUT" == "true" ]]; then
    output_format="json"
    # Set default JSON output file if not specified
    if [[ -z "$JSON_OUTPUT_FILE" ]]; then
        JSON_OUTPUT_FILE="$PROJECT_ROOT/tests/behave-results.json"
    fi
    echo -e "${BLUE}JSON output will be written to:${RESET} $JSON_OUTPUT_FILE"
    echo ""
fi

# Run behave directly on host
echo -e "${YELLOW}Note: Running directly on host (not in container)${RESET}"
echo -e "${YELLOW}      VM configurations will be preserved${RESET}"
echo ""

local start_time=$(date +%s)
# Use python3 -m behave to avoid PATH issues in subprocess
# Build command carefully to handle arguments correctly
if [[ "$JSON_OUTPUT" == "true" ]]; then
    # JSON mode: JSON to file, progress to console
    # Use correct behave syntax: --format json -o output_file
    if [[ -n "$VERBOSE_FLAG" ]]; then
        python3 -m behave --format json -o "$JSON_OUTPUT_FILE" --format progress $VERBOSE_FLAG "$feature_path"
    else
        python3 -m behave --format json -o "$JSON_OUTPUT_FILE" --format progress "$feature_path"
    fi
else
    # Normal mode: pretty output to console
    if [[ -n "$VERBOSE_FLAG" ]]; then
        python3 -m behave --format "$output_format" $VERBOSE_FLAG "$feature_path"
    else
        python3 -m behave --format "$output_format" "$feature_path"
    fi
fi
local exit_code=$?
local end_time=$(date +%s)
local duration=$((end_time - start_time))

echo ""
echo -e "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
echo ""

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}✓ All BDD tests passed!${RESET}"
    echo -e "${GREEN}Completed in ${duration} seconds${RESET}"
else
    echo -e "${RED}${BOLD}✗ Some BDD tests failed${RESET}"
    echo ""
    echo -e "${YELLOW}Tip: Run with -v for more details: $0 -v${RESET}"
fi

# If JSON output was requested, show the results
if [[ "$JSON_OUTPUT" == "true" && -f "$JSON_OUTPUT_FILE" ]]; then
    echo ""
    echo -e "${BLUE}JSON results written to:${RESET} $JSON_OUTPUT_FILE"
    # Show quick summary from JSON if python3 is available
    if command -v python3 >/dev/null 2>&1; then
        local passed=$(python3 -c "import json; data = json.load(open('$JSON_OUTPUT_FILE')); print(sum(1 for s in data.get('elements', []) if s.get('status') != 'failed' and s.get('status') != 'skipped'))" 2>/dev/null || echo "N/A")
        local failed=$(python3 -c "import json; data = json.load(open('$JSON_OUTPUT_FILE')); print(sum(1 for s in data.get('elements', []) if s.get('status') == 'failed'))" 2>/dev/null || echo "N/A")
        echo -e "${BLUE}Summary: ${passed} passed, ${failed} failed${RESET}"
    fi
fi

exit $exit_code
