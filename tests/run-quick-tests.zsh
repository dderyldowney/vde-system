#!/usr/bin/env zsh
# VDE Quick Test Runner - Docker-free tests only
# Fast execution without Docker dependency

set -e

SCRIPT_DIR="$(cd "$(dirname "${0:a}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

export VDE_ROOT_DIR="${PROJECT_ROOT}"
export PYTHONDONTWRITEBYTECODE=1

if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    CYAN=''
    BOLD=''
    RESET=''
fi

clear_python_cache() {
    local cache_cleared=0
    for pycache in $(find tests/features -name "__pycache__" -type d 2>/dev/null); do
        rm -rf "${pycache}" 2>/dev/null && cache_cleared=$((cache_cleared + 1))
    done
    for pyc in $(find tests/features -name "*.pyc" 2>/dev/null); do
        rm -f "${pyc}" 2>/dev/null && cache_cleared=$((cache_cleared + 1))
    done
    [[ ${cache_cleared} -gt 0 ]] && echo "Cleared ${cache_cleared} Python cache entries"
    return 0
}

trap 'clear_python_cache' EXIT

show_usage() {
    cat <<EOF
${BOLD}VDE Quick Test Runner${RESET}

Usage: run-quick-tests.zsh [FEATURE] [OPTIONS]

${BOLD}Arguments:${RESET}
  FEATURE    Specific feature to test (e.g., 'cache-system', 'parser')

${BOLD}Options:${RESET}
  -v, --verbose   Enable verbose output
  -h, --help      Show this help message

${BOLD}Examples:${RESET}
  run-quick-tests.zsh                    # Run all docker-free tests
  run-quick-tests.zsh cache-system        # Run specific feature
  run-quick-tests.zsh parser --verbose    # Run with verbose output
EOF
}

VERBOSE_OUTPUT=false
QUIET_OUTPUT=false
SPECIFIC_FEATURE=""

while [[ ${#} -gt 0 ]]; do
    case "${1}" in
        -v|--verbose)
            VERBOSE_OUTPUT=true
            shift
            ;;
        -q|--quiet)
            QUIET_OUTPUT=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            SPECIFIC_FEATURE="${1}"
            shift
            ;;
    esac
done

BEHAVE_CMD="behave"
if ! command -v behave &> /dev/null; then
    if python3 -m behave --version &> /dev/null; then
        BEHAVE_CMD="python3 -m behave"
    else
        echo -e "${RED}Error: 'behave' not installed${RESET}"
        exit 1
    fi
fi

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}Running Fast BDD Tests (No Docker Required)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo ""

mkdir -p projects/{python,rust,js,csharp,ruby,go,java}
mkdir -p data/{postgres,mongodb,redis}
mkdir -p logs/nginx
mkdir -p public-ssh-keys
mkdir -p .cache .locks

behave_args="--format pretty --no-color"
[[ "${VERBOSE_OUTPUT}" == "true" ]] && behave_args="${behave_args} --verbose"
[[ "${QUIET_OUTPUT}" == "true" ]] && behave_args="${behave_args} --quiet"

if [[ -n "${SPECIFIC_FEATURE}" ]]; then
    echo -e "${CYAN}Running: ${SPECIFIC_FEATURE}${RESET}"
    if [[ -f "tests/features/core-infrastructure/${SPECIFIC_FEATURE}.feature" ]]; then
        behave_args="${behave_args} tests/features/core-infrastructure/${SPECIFIC_FEATURE}.feature"
    else
        matched_file=$(find tests/features/core-infrastructure -name "${SPECIFIC_FEATURE}*.feature" | head -1)
        if [[ -n "${matched_file}" ]]; then
            behave_args="${behave_args} ${matched_file}"
        else
            echo -e "${RED}Feature '${SPECIFIC_FEATURE}' not found${RESET}"
            ls tests/features/core-infrastructure/*.feature | xargs -I {} basename {} .feature | sed 's/^/  - /'
            exit 1
        fi
    fi
else
    echo -e "${CYAN}Running all docker-free features${RESET}"
    [[ -n "${CI}" ]] && behave_args="${behave_args} tests/features/core-infrastructure/ --tags=~@user-guide-internal" || behave_args="${behave_args} tests/features/core-infrastructure/"
fi

echo ""
echo -e "${CYAN}Command: ${BEHAVE_CMD} ${behave_args}${RESET}"
echo ""

if eval ${BEHAVE_CMD} ${behave_args}; then
    echo ""
    echo -e "${GREEN}✓ All fast BDD tests passed!${RESET}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some BDD tests failed${RESET}"
    exit 1
fi
