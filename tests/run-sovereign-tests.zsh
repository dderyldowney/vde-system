#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# VDE Sovereign Test Runner (1.3.0)
# This script runs all CI-safe tests (Unit Tests + Image Logic).
# It STRICTLY EXCLUDES any tests that require running containers (DinD).
#
# Unit suites are DISCOVERED, not listed (Signet #630): every tests/unit/*.test.zsh runs, except the
# suites named in tests/ci-unit-exclusions.txt ("<suite> <reason>" per line; # comments and blank
# lines allowed). An exclusion with no reason, or one naming a suite that does not exist, is an
# error. `--list` prints the plan ("run  <suite>" / "skip <suite> :: <reason>") and exits 0 before
# the audit and before running anything.
typeset _ZSH_PURE=${(%):-%x}

# Determine VDE root directory
VDE_ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export VDE_ROOT_DIR

# The suites run against their own scratch Projects base, never the caller's.
source "${VDE_ROOT_DIR}/lib/vde-test-env" || { echo "ERROR: cannot load lib/vde-test-env" >&2; exit 1; }
vde_test_env_enter || { echo "ERROR: cannot create a scratch Projects base" >&2; exit 1; }

# Colors for high-fidelity output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

# --- Unit suite discovery (Signet #630) -------------------------------------------------------
typeset EXCLUSIONS_FILE="${VDE_ROOT_DIR}/tests/ci-unit-exclusions.txt"
typeset -a UNIT_TESTS=()
typeset -A UNIT_EXCLUDED=()

discover_unit_tests() {
    local line name reason f
    local -a w
    UNIT_TESTS=()
    UNIT_EXCLUDED=()
    if [[ -f "${EXCLUSIONS_FILE}" ]]; then
        while IFS= read -r line || [[ -n "${line}" ]]; do
            [[ "${line}" =~ '^[[:space:]]*(#|$)' ]] && continue
            w=( ${=line} )
            name="${w[1]}"
            reason="${(j: :)w[2,-1]}"
            if [[ "${name}" != *.test.zsh ]]; then
                echo "ERROR: ${name}: not a unit suite (an exclusion must name a *.test.zsh file)" >&2
                return 1
            fi
            if [[ "${name}" == */* ]]; then
                echo "ERROR: ${name}: an exclusion names a suite by its file name only, not a path" >&2
                return 1
            fi
            if [[ -z "${reason}" || "${reason}" == \#* ]]; then
                echo "ERROR: ${name}: an exclusion with no reason in tests/ci-unit-exclusions.txt (an inline # comment is not a reason)" >&2
                return 1
            fi
            if [[ ! -f "${VDE_ROOT_DIR}/tests/unit/${name}" ]]; then
                echo "ERROR: ${name}: stale exclusion, no such suite in tests/unit/" >&2
                return 1
            fi
            if (( ${+UNIT_EXCLUDED[${name}]} )); then
                echo "ERROR: ${name}: listed twice in tests/ci-unit-exclusions.txt" >&2
                return 1
            fi
            UNIT_EXCLUDED[${name}]="${reason}"
        done < "${EXCLUSIONS_FILE}"
    fi
    for f in "${VDE_ROOT_DIR}"/tests/unit/*.test.zsh(N); do
        (( ${+UNIT_EXCLUDED[${f:t}]} )) || UNIT_TESTS+=( "${f}" )
    done
    return 0
}

if [[ "${1:-}" == --list ]]; then
    discover_unit_tests || exit 1
    for f in "${UNIT_TESTS[@]}"; do print -r -- "run  ${f:t}"; done
    for name in ${(ko)UNIT_EXCLUDED}; do print -r -- "skip ${name} :: ${UNIT_EXCLUDED[$name]}"; done
    exit 0
fi

# --- Timing (Signet #774): every run is timed, always ----------------------------------------
# Each suite is announced with a wall-clock time and reports its duration; a SUITE TIMING table
# (slowest first) is printed before the summary. The "containers" column is the number of
# containers CREATED while the suite ran, read from `docker events` for the suite's time window
# (it is "n/a" when docker is missing or the query fails, and never changes the exit code).
# VDE_TEST_TIMING_FILE, when set, also receives one "<seconds> <containers> <suite>" line per row.
zmodload zsh/datetime
typeset -a TIMING_ROWS=()

# _vde_fmt1 <number>: one decimal place with a DOT, whatever locale the caller has set. LC_ALL overrides
# LC_NUMERIC, so both are pinned, and only for this one printf: the suites and the docker call run in the
# caller's own locale.
_vde_fmt1() {
    local LC_ALL=C LC_NUMERIC=C
    printf '%.1f' "$1"
}

# _vde_container_creates <t0> <t1>: prints the container-create count for the window, or n/a.
_vde_container_creates() {
    local out secs="${VDE_DOCKER_EVENTS_TIMEOUT:-10}"
    local -a ids bound
    command -v docker >/dev/null 2>&1 || { print -r -- "n/a"; return 0; }
    # A hung docker daemon must not stall the run (and with it the push gate): the query is bounded.
    [[ "${secs}" == <-> ]] || secs=10
    if command -v timeout >/dev/null 2>&1; then bound=( timeout "${secs}" )
    elif command -v gtimeout >/dev/null 2>&1; then bound=( gtimeout "${secs}" ); fi
    out="$("${bound[@]}" docker events --filter type=container --filter event=create --since "$1" --until "$2" --format '{{.Actor.ID}}' </dev/null 2>/dev/null)" || { print -r -- "n/a"; return 0; }
    # An explicit array: ${#${(f)out}} of ONE line would be that line's length, not 1.
    ids=( ${(f)out} )
    print -r -- "${#ids}"
}

# _vde_record_timing <name> <t0> <t1>: stores one timing row ("<seconds>|<name>|<containers>").
_vde_record_timing() {
    local secs containers
    secs="$(_vde_fmt1 $(( $3 - $2 )))"
    containers="$(_vde_container_creates "$2" "$3")"
    TIMING_ROWS+=( "${secs}|${1}|${containers}" )
}

# _vde_print_timing: the SUITE TIMING table, slowest first, then the optional machine-readable file.
_vde_print_timing() {
    local row secs name containers total=0
    local -a sorted
    sorted=( "${(@f)$(printf '%s\n' "${TIMING_ROWS[@]}" | LC_ALL=C sort -t'|' -k1,1 -rn)}" )
    echo -e "\n${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BLUE}${BOLD}  SUITE TIMING${RESET}"
    echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    printf '%-60s %8s %s\n' "suite" "seconds" "containers"
    for row in "${sorted[@]}"; do
        [[ -n "${row}" ]] || continue
        secs="${row%%|*}"; name="${${row#*|}%%|*}"; containers="${row##*|}"
        printf '%-60s %7ss %s\n' "${name}" "${secs}" "${containers}"
        total="$(_vde_fmt1 $(( total + secs )))"
        [[ -n "${VDE_TEST_TIMING_FILE:-}" ]] && print -r -- "${secs} ${containers} ${name}" >> "${VDE_TEST_TIMING_FILE}"
    done
    echo "Total suite time: ${total}s (${#TIMING_ROWS} suites)"
}
[[ -n "${VDE_TEST_TIMING_FILE:-}" ]] && : > "${VDE_TEST_TIMING_FILE}"

# Mandatory Sovereign Audit (Rule A)
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}${BOLD}  VDE SOVEREIGN AUDIT (Rule A)${RESET}"
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
typeset -F AUDIT_T0=${EPOCHREALTIME}
"${VDE_ROOT_DIR}/bin/vde-enforce-uap.zsh" || exit 1
_vde_record_timing "sovereign-audit" "${AUDIT_T0}" "${EPOCHREALTIME}"

# Initialize test counters
TOTAL_PASSED=0
TOTAL_FAILED=0
FAILED_TESTS=()

# Function to run a test file
run_test_file() {
    local test_file="${1}"
    local test_name=$(basename "${test_file}")
    local -F t0 t1
    local dur

    echo -e "\n${YELLOW}${BOLD}➤ Running: ${test_name} [$(strftime '%H:%M:%S' ${EPOCHSECONDS})]${RESET}"

    # Execute the test and capture exit code
    t0=${EPOCHREALTIME}
    zsh "${test_file}"
    local rc=$?
    t1=${EPOCHREALTIME}
    _vde_record_timing "${test_name}" "${t0}" "${t1}"
    dur="$(_vde_fmt1 $(( t1 - t0 )))s"

    if [[ ${rc} -eq 0 ]]; then
        echo -e "${GREEN}✓ ${test_name} passed (${dur})${RESET}"
        ((TOTAL_PASSED++))
    else
        echo -e "${RED}✗ ${test_name} failed (exit code: ${rc}) (${dur})${RESET}"
        ((TOTAL_FAILED++))
        FAILED_TESTS+=("${test_name}")
    fi
}

# =============================================================================
# PHASE 1: Unit Tests
# =============================================================================
echo -e "\n${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}${BOLD}  PHASE 1: Unit Tests${RESET}"
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Ensure test-tmp directory exists
mkdir -p "${VDE_ROOT_DIR}/.test-tmp"

discover_unit_tests || exit 1
for name in ${(ko)UNIT_EXCLUDED}; do
    echo -e "${YELLOW}⚠ Excluded from CI: ${name} :: ${UNIT_EXCLUDED[$name]}${RESET}"
done

for test in "${UNIT_TESTS[@]}"; do
    if [[ -f "${test}" ]]; then
        run_test_file "${test}"
    else
        echo -e "${RED}⚠ Missing test file: ${test}${RESET}"
        ((TOTAL_FAILED++))
        FAILED_TESTS+=("$(basename ${test}) [MISSING]")
    fi
done

# =============================================================================
# PHASE 2: Integration Tests (Sovereign-Safe)
# =============================================================================
echo -e "\n${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}${BOLD}  PHASE 2: Integration Tests (Sovereign-Safe)${RESET}"
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Only run integration tests that don't call docker run/start
INTEGRATION_TESTS=(
    "${VDE_ROOT_DIR}/tests/integration/vm-lifecycle-integration.test.zsh"
)

# Set environment variable to signal we are in CI mode (skip container starts)
export VDE_CI_MODE=1

for test in "${INTEGRATION_TESTS[@]}"; do
    if [[ -f "${test}" ]]; then
        run_test_file "${test}"
    fi
done

# =============================================================================
# PHASE 3: BDD Feature Verification (Metadata Only)
# =============================================================================
echo -e "\n${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}${BOLD}  PHASE 3: BDD Feature Verification (Metadata)${RESET}"
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Verify all feature files follow the standard
if command -v grep &>/dev/null; then
    MISSING_TAGS=$(grep -L "@" tests/features/core-infrastructure/*.feature)
    if [[ -n "${MISSING_TAGS}" ]]; then
        echo -e "${RED}✗ The following features are missing tags:${RESET}"
        echo "${MISSING_TAGS}"
        ((TOTAL_FAILED++))
        FAILED_TESTS+=("BDD-Metadata")
    else
        echo -e "${GREEN}✓ All core features are properly tagged.${RESET}"
        ((TOTAL_PASSED++))
    fi
fi

# =============================================================================
# SUITE TIMING + FINAL SUMMARY
# =============================================================================
_vde_print_timing

echo -e "\n${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}${BOLD}  VDE TEST SUMMARY${RESET}"
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if [[ ${TOTAL_FAILED} -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}PASS: ${TOTAL_PASSED} test suites completed successfully.${RESET}"
    echo -e "\n${GREEN}The Sovereign Baseline is intact.${RESET}"
    exit 0
else
    echo -e "${RED}${BOLD}FAIL: ${TOTAL_FAILED} test suites failed.${RESET}"
    echo -e "${YELLOW}Passed: ${TOTAL_PASSED}${RESET}"
    echo -e "\n${RED}Failed Suites:${RESET}"
    # ZSH-native shibboleth: Newline joining
    echo -e "${(j:\n:)FAILED_TESTS}"
    exit 1
fi
