#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE Coverage Script
# Runs test suite with code coverage using kcov

# Note: Don't use set -e here as we need to handle kcov exit codes explicitly

# Colors for output

# ZSH-native logic demonstration (UAP Mandate 1)
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Configuration
# The root MUST be absolute. CI exports VDE_ROOT_DIR at job level and every child test
# inherits it; the old relative "." (from ${0:h:h}) clobbered it for every child test.
VDE_ROOT_DIR="${0:A:h:h}"
COVERAGE_DIR="${VDE_ROOT_DIR}/coverage"
COVERAGE_MERGED="${COVERAGE_DIR}/merged"

# Source directories to measure coverage
SOURCE_DIRS=(
    "${VDE_ROOT_DIR}/lib"
    "${VDE_ROOT_DIR}/scripts"
)

# Names of tests that failed; main turns a non-empty list into a non-zero exit status
typeset -a FAILED_TESTS=()

# Excluded tests: path relative to tests/ (e.g. integration/x.test.zsh) -> reason
typeset -A COVERAGE_EXCLUDED=()

# Read tests/ci-coverage-exclusions.txt. Every error exits before anything is cleaned or run.
load_exclusions() {
    local exclusions_file="${VDE_ROOT_DIR}/tests/ci-coverage-exclusions.txt"
    local line name reason

    COVERAGE_EXCLUDED=()
    [[ -f "${exclusions_file}" ]] || return 0

    while IFS= read -r line || [[ -n "${line}" ]]; do
        [[ "${line}" =~ '^[[:space:]]*(#|$)' ]] && continue
        read -r name reason <<< "${line}"

        if [[ "${name}" != (unit|integration)/*.test.zsh || "${name#*/}" == */* ]]; then
            print -r -- "ERROR: ${name}: an exclusion must name tests/unit/<file>.test.zsh or tests/integration/<file>.test.zsh (no further slashes)" >&2
            exit 1
        fi
        if [[ -z "${reason//[[:space:]]/}" || "${reason}" == \#* ]]; then
            print -r -- "ERROR: ${name}: an exclusion with no reason in tests/ci-coverage-exclusions.txt (a reason is mandatory and must not begin with #)" >&2
            exit 1
        fi
        if [[ ! -f "${VDE_ROOT_DIR}/tests/${name}" ]]; then
            print -r -- "ERROR: ${name}: stale exclusion, no such test file under tests/" >&2
            exit 1
        fi
        if (( ${+COVERAGE_EXCLUDED[${name}]} )); then
            print -r -- "ERROR: ${name}: listed twice in tests/ci-coverage-exclusions.txt" >&2
            exit 1
        fi
        COVERAGE_EXCLUDED[${name}]="${reason}"
    done < "${exclusions_file}"
}

# Clean previous coverage data
clean_coverage() {
    print -P "${BLUE}Cleaning previous coverage data...${NC}"
    rm -rf "${COVERAGE_DIR}"
    mkdir -p "${COVERAGE_DIR}"
}

# Run a single test under kcov
run_test_with_coverage() {
    local test_file="${1}"
    local test_name
    test_name="$(basename "${test_file}" .sh)"
    local coverage_out="${COVERAGE_DIR}/${test_name}"
    local rel="${test_file#"${VDE_ROOT_DIR}/tests/"}"
    local pre_out pre_rc

    if (( ${+COVERAGE_EXCLUDED[${rel}]} )); then
        print -P "${YELLOW}Excluded: ${rel//\%/%%} :: ${COVERAGE_EXCLUDED[${rel}]//\%/%%}${NC}"
        return 0
    fi

    if [[ ! -f "${test_file}" ]]; then
        print -P "${RED}✗ Test file not found: ${rel//\%/%%}${NC}"
        FAILED_TESTS+=("${test_name}")
        return 1
    fi

    print -P "${BLUE}Running: ${test_name//\%/%%}${NC}"

    # Verify test passes first. Keep its output so a failure's cause shows in the CI log.
    pre_out="$(zsh "${test_file}" </dev/null 2>&1)"
    pre_rc=$?
    if (( pre_rc != 0 )); then
        print -P "${RED}✗ Test failed: ${test_name//\%/%%}${NC}"
        print -r -- "${pre_out}"
        FAILED_TESTS+=("${test_name}")
        return 1
    fi

    # Use set -o noglob to prevent glob expansion of patterns
    # Run with kcov - ignore exit code since test already passed
    set -o localoptions -o noglob
    kcov \
        --exclude-pattern=/usr/*,/opt/* \
        --exclude-region=TEST:END_TEST \
        --path-strip-level=2 \
        "${coverage_out}" \
        zsh "${test_file}" || true

    return 0
}

# Run all tests in a directory
run_directory_with_coverage() {
    local dir="${1}"
    local test_count=0

    # Use setopt for null_glob behavior (zsh-specific)
    setopt local_options null_glob
    for test_file in "${dir}"/*.zsh(N); do
        if [[ -f "${test_file}" ]] ; then
            # A failure is recorded in FAILED_TESTS; keep going so every test still runs
            run_test_with_coverage "${test_file}" || true
            ((test_count++))
        fi
    done

    print -P "${GREEN}✓ Ran ${test_count} test(s) from ${dir//\%/%%}${NC}"
}

# Merge coverage reports
merge_coverage() {
    print -P "${BLUE}Merging coverage reports...${NC}"

    # Collect the per-test coverage directories BEFORE the output directory exists,
    # and never include the output directory itself.
    local -a kcov_dirs=()
    local d
    for d in "${COVERAGE_DIR}"/*(N/); do
        [[ "${d}" == "${COVERAGE_MERGED}" ]] || kcov_dirs+=("${d}")
    done

    if [[ ${#kcov_dirs[@]} -eq 0 ]] ; then
        print -P "${RED}✗ No coverage data found to merge${NC}"
        return 1
    fi

    mkdir -p "${COVERAGE_MERGED}"

    # Work in a dot directory directly under coverage/: never under merged/, and the glob above ignores it
    local merge_tmp="${COVERAGE_DIR}/.merge-tmp"
    rm -rf "${merge_tmp}"
    mkdir -p "${merge_tmp}"

    # Copy the first coverage as base, then merge the rest into it in one kcov call
    cp -r "${kcov_dirs[1]}/." "${merge_tmp}/"

    if (( ${#kcov_dirs[@]} > 1 )); then
        if ! kcov --merge "${merge_tmp}" "${(@)kcov_dirs[2,-1]}"; then
            local -a merge_names=()
            for d in "${(@)kcov_dirs[2,-1]}"; do
                merge_names+=("${d:t}")
            done
            print -P "${YELLOW}⚠ kcov --merge failed for: ${(j:, :)merge_names//\%/%%} (the merged report may be incomplete)${NC}"
        fi
    fi

    # Move the merged result to its final location, dot-files included
    mv "${merge_tmp}"/*(DN) "${COVERAGE_MERGED}/"
    rm -rf "${merge_tmp}"

    print -P "${GREEN}✓ Coverage reports merged${NC}"
}

# Generate coverage summary
generate_summary() {
    print -P "${BLUE}Generating coverage summary...${NC}"

    local index_file="${COVERAGE_MERGED}/index.html"

    if [[ ! -f "${index_file}" ]] ; then
        print -P "${RED}✗ Coverage report not found at ${index_file//\%/%%}${NC}"
        return 1
    fi

    # Extract coverage percentage from index.html
    local coverage
    coverage=$(grep -oP 'covered"[^>]*>\K[0-9.]+' "${index_file}" 2>/dev/null | head -1)

    if [[ -n "${coverage}" ]] ; then
        print -P "\n${GREEN}================================${NC}"
        print -P "${GREEN}Coverage Report Generated${NC}"
        print -P "${GREEN}================================${NC}"
        print -P "Total Coverage: ${GREEN}${coverage}%${NC}"
        print -P "Report: ${BLUE}file://${index_file//\%/%%}${NC}"
        print -P "${GREEN}================================${NC}\n"
    else
        print -P "${YELLOW}⚠ Could not extract coverage percentage${NC}"
        print -P "View full report at: file://${index_file//\%/%%}"
    fi
}

# Main
main() {
    local test_type="${1:-all}"
    local merge_status=0
    local failed

    load_exclusions

    case "${test_type}" in
        unit)
            print -P "${YELLOW}Running unit tests with coverage...${NC}"
            clean_coverage
            run_directory_with_coverage "${VDE_ROOT_DIR}/tests/unit"
            ;;
        integration)
            print -P "${YELLOW}Running integration tests with coverage...${NC}"
            clean_coverage
            run_directory_with_coverage "${VDE_ROOT_DIR}/tests/integration"
            ;;
        comprehensive)
            print -P "${YELLOW}Running comprehensive tests with coverage...${NC}"
            clean_coverage
            # Each named file is a test in its own right; a missing one is a counted failure
            run_test_with_coverage "${VDE_ROOT_DIR}/tests/unit/test_vde_parser_comprehensive.sh" || true
            run_test_with_coverage "${VDE_ROOT_DIR}/tests/unit/test_vde_commands_comprehensive.sh" || true
            run_test_with_coverage "${VDE_ROOT_DIR}/tests/integration/test_integration_comprehensive.sh" || true
            ;;
        all)
            print -P "${YELLOW}Running all tests with coverage...${NC}"
            clean_coverage
            run_directory_with_coverage "${VDE_ROOT_DIR}/tests/unit"
            run_directory_with_coverage "${VDE_ROOT_DIR}/tests/integration"
            ;;
        *)
            print -P "${RED}Unknown test type: ${test_type//\%/%%}${NC}"
            print -P "Usage: ${0//\%/%%} [all|unit|integration|comprehensive]"
            exit 1
            ;;
    esac

    merge_coverage || merge_status=$?
    generate_summary

    if (( ${#FAILED_TESTS[@]} > 0 )); then
        print -P "${RED}✗ ${#FAILED_TESTS[@]} test(s) failed:${NC}"
        for failed in "${FAILED_TESTS[@]}"; do
            print -P "${RED}  ${failed//\%/%%}${NC}"
        done
        exit 1
    fi

    if (( merge_status != 0 )); then
        exit 1
    fi

    exit 0
}

main "${@}"
