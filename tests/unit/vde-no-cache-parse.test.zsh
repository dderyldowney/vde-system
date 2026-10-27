#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for bin/vde --no-cache parsing (Signet #556).
#
# Proves that `vde rebuild --no-cache <vm>` treats --no-cache as a FLAG, not a
# VM target, and still delivers it to the build. Uses `vde function-trace`,
# which resolves targets and records the final docker command WITHOUT running
# a build, so no Docker image is touched.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0

if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi

test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); }

# Run `vde function-trace <args>` and capture ANSI-stripped output.
_trace() {
    VDE_QUIET=1 zsh "${VDE_ROOT_DIR}/bin/vde" function-trace "$@" 2>&1 \
        | sed $'s/\x1b\\[[0-9;]*m//g'
}

# Fields extracted from a trace.
_targets_line() { print -r -- "$1" | grep -m1 'Targets:'; }
_final_cmd()    { print -r -- "$1" | grep -A1 'Final Command:' | tail -n1; }

check_flag() {
    local label="$1"; shift
    test_start "${label}"
    local out; out="$(_trace "$@")"
    local tl fc; tl="$(_targets_line "${out}")"; fc="$(_final_cmd "${out}")"
    if [[ "${tl}" == *"--no-cache"* ]]; then
        test_fail "${label}" "--no-cache leaked into target list: ${tl}"
    elif [[ "${tl}" != *"python"* ]]; then
        test_fail "${label}" "python target missing: ${tl}"
    elif [[ "${fc}" != *"build --no-cache"* ]]; then
        test_fail "${label}" "--no-cache not delivered to build: ${fc}"
    else
        test_pass "${label}"
    fi
}

check_flag "rebuild --no-cache python: flag is not a target and reaches build" rebuild --no-cache python
check_flag "rebuild python --no-cache: flag order is irrelevant"               rebuild python --no-cache

test_start "rebuild python (no flag): build is cached"
out="$(_trace rebuild python)"
fc="$(_final_cmd "${out}")"
if [[ "${fc}" == *"--no-cache"* ]]; then
    test_fail "rebuild python (no flag)" "unexpected --no-cache: ${fc}"
elif [[ "${fc}" != *"build"* ]]; then
    test_fail "rebuild python (no flag)" "no build command captured: ${fc}"
else
    test_pass "rebuild python (no flag): build is cached"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
