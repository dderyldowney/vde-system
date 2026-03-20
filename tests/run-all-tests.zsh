#!/usr/bin/env zsh
# VDE Complete Test Suite Runner
# Runs full BDD test suite with Docker support

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${0:a}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_DIR="test-logs"
RESULTS_DIR="tests"

cleanup_ssh_agents() {
    source tests/setup-ssh-agent.zsh --cleanup 2>/dev/null || true
    pkill -f "ssh-agent.*VDE" 2>/dev/null || true
}

trap cleanup_ssh_agents EXIT INT TERM

BEHAVE_CMD="${BEHAVE_CMD:-$(command -v behave 2>/dev/null || echo 'python3 -m behave')}"

if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
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
    [[ ${cache_cleared} -gt 0 ]] && echo -e "${YELLOW}Cleared ${cache_cleared} Python cache entries${RESET}"
    return 0
}

trap 'clear_python_cache' EXIT

declare -A phase_results

show_usage() {
    cat <<EOF
${BOLD}VDE Complete Test Suite Runner${RESET}

Usage: run-all-tests.zsh [OPTIONS] [FEATURE]

${BOLD}Options:${RESET}
  --check         Check test setup without running tests
  --json          Output test results in JSON format
  -o FILE         Write JSON output to FILE (requires --json)
  -v, --verbose   Enable verbose output
  -h, --help      Show this help message

${BOLD}Arguments:${RESET}
  FEATURE         Specific feature to test (runs all if omitted)

${BOLD}Examples:${RESET}
  run-all-tests.zsh                        # Run full test suite
  run-all-tests.zsh vm-lifecycle           # Run specific feature
  run-all-tests.zsh --check                # Check environment
EOF
}

check_setup() {
    echo -e "${BLUE}Checking test setup...${RESET}"
    local errors=0

    if [[ ! -d "${PROJECT_ROOT}/bin" ]]; then
        echo -e "${RED}Error: Not in VDE project root${RESET}"
        ((errors++))
    fi

    if ! docker info >/dev/null 2>&1; then
        echo -e "${YELLOW}Warning: Docker not running${RESET}"
    else
        echo -e "${GREEN}Docker is running${RESET}"
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}Error: Python 3 not found${RESET}"
        ((errors++))
    else
        echo -e "${GREEN}Python 3 available${RESET}"
    fi

    if [[ ${errors} -gt 0 ]]; then
        echo -e "${RED}Setup check failed${RESET}"
        exit 1
    fi

    echo -e "${GREEN}Setup OK${RESET}"
}

CHECK_ONLY=false
VERBOSE_OUTPUT=false
JSON_OUTPUT=false
SPECIFIC_FEATURE=""

while [[ ${#} -gt 0 ]]; do
    case "${1}" in
        --check)
            CHECK_ONLY=true
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
            JSON_OUTPUT=true
            JSON_OUTPUT_FILE="${2}"
            shift 2
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

export VDE_ROOT_DIR="${PROJECT_ROOT}"
export VDE_TEST_MODE=1

mkdir -p "${LOG_DIR}"

if [[ "${CHECK_ONLY}" == "true" ]]; then
    check_setup
    exit 0
fi

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}VDE Complete Test Suite${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo ""

if [[ -n "${SPECIFIC_FEATURE}" ]]; then
    check_setup

    local behave_args feature_name
    if [[ -f "tests/features/docker-required/${SPECIFIC_FEATURE}.feature" ]]; then
        behave_args="tests/features/docker-required/${SPECIFIC_FEATURE}.feature"
        feature_name="${SPECIFIC_FEATURE} (docker-required)"
    elif [[ -f "tests/features/core-infrastructure/${SPECIFIC_FEATURE}.feature" ]]; then
        behave_args="tests/features/core-infrastructure/${SPECIFIC_FEATURE}.feature"
        feature_name="${SPECIFIC_FEATURE}"
    else
        echo -e "${RED}Feature '${SPECIFIC_FEATURE}' not found${RESET}"
        exit 1
    fi

    echo -e "${CYAN}Running: ${feature_name}${RESET}"

    local output_format="pretty"
    if [[ "${JSON_OUTPUT}" == "true" ]]; then
        output_format="json"
        JSON_OUTPUT_FILE="${JSON_OUTPUT_FILE:-${PROJECT_ROOT}/tests/behave-results.json}"
        echo -e "${BLUE}JSON output: ${JSON_OUTPUT_FILE}${RESET}"
    fi

    local verbose_flag=""
    [[ "${VERBOSE_OUTPUT}" == "true" ]] && verbose_flag="--verbose"

    local start_time=$(date +%s)
    if [[ "${JSON_OUTPUT}" == "true" ]]; then
        python3 -m behave --format json -o "${JSON_OUTPUT_FILE}" --format progress ${verbose_flag} "${behave_args}"
    else
        python3 -m behave --format ${output_format} ${verbose_flag} "${behave_args}"
    fi
    local exit_code=${?}
    local duration=$(($(date +%s) - start_time))

    if [[ ${exit_code} -eq 0 ]]; then
        echo -e "${GREEN}✓ Tests passed (${duration}s)${RESET}"
    else
        echo -e "${RED}✗ Tests failed (${duration}s)${RESET}"
    fi
    exit ${exit_code}
fi

check_setup

echo "=== Setting up SSH Agent ==="
source tests/setup-ssh-agent.zsh

echo "=== Phase 1: Docker-free BDD Tests ==="
if (cd tests/features && ${BEHAVE_CMD} core-infrastructure/ --format json -o ../behave-results-docker-free.json) \
   > "${LOG_DIR}/docker-free-${TIMESTAMP}.log" 2>&1; then
    phase_results[docker_free]="PASS"
else
    phase_results[docker_free]="FAIL"
fi

echo "=== Phase 2: Unit Tests ==="
if make test-unit > "${LOG_DIR}/unit-${TIMESTAMP}.log" 2>&1; then
    phase_results[unit]="PASS"
else
    phase_results[unit]="FAIL"
fi

echo "=== Phase 3: Integration Tests ==="
if make test-integration > "${LOG_DIR}/integration-${TIMESTAMP}.log" 2>&1; then
    phase_results[integration]="PASS"
else
    phase_results[integration]="FAIL"
fi

echo "=== Phase 4: Core Infrastructure BDD Tests ==="
if docker info >/dev/null 2>&1; then
    if (cd tests/features && ${BEHAVE_CMD} core-infrastructure/ --format json -o ../behave-results-core-infrastructure.json) \
       > "${LOG_DIR}/core-infra-${TIMESTAMP}.log" 2>&1; then
        phase_results[core_infra]="PASS"
    else
        phase_results[core_infra]="FAIL"
    fi
else
    echo "Docker not running, skipping core-infrastructure tests"
    phase_results[core_infra]="SKIP"
fi

echo "=== Phase 5: Docker-required BDD Tests ==="
if docker info >/dev/null 2>&1; then
    if (cd tests/features && ${BEHAVE_CMD} docker-required/ --format json -o ../behave-results-docker-required.json) \
       > "${LOG_DIR}/docker-required-${TIMESTAMP}.log" 2>&1; then
        phase_results[docker_required]="PASS"
    else
        phase_results[docker_required]="FAIL"
    fi
else
    echo "Docker not running, skipping docker-required tests"
    phase_results[docker_required]="SKIP"
fi

cat > "${RESULTS_DIR}/TEST_RESULTS_SUMMARY.json" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "phases": {
    "docker_free": "${phase_results[docker_free]}",
    "unit": "${phase_results[unit]}",
    "integration": "${phase_results[integration]}",
    "core_infra": "${phase_results[core_infra]}",
    "docker_required": "${phase_results[docker_required]}"
  },
  "logs": {
    "docker_free": "${LOG_DIR}/docker-free-${TIMESTAMP}.log",
    "unit": "${LOG_DIR}/unit-${TIMESTAMP}.log",
    "integration": "${LOG_DIR}/integration-${TIMESTAMP}.log",
    "core_infra": "${LOG_DIR}/core-infra-${TIMESTAMP}.log",
    "docker_required": "${LOG_DIR}/docker-required-${TIMESTAMP}.log"
  }
}
EOF

echo ""
echo "=== Test Suite Summary ==="
for phase in docker_free unit integration core_infra docker_required; do
    echo "${phase}: ${phase_results[${phase}]}"
done

source tests/setup-ssh-agent.zsh --cleanup

for result in "${phase_results[@]}"; do
    if [[ "${result}" == "FAIL" ]]; then
        exit 1
    fi
done

exit 0
