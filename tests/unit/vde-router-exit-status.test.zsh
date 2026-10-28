#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: bin/vde router exit statuses (Signet #582).
#
# An unknown command used to print to stdout and exit 0, and a bare `vde`
# died on `shift` before any usage was shown. Both must report invalid input:
# exit VDE_ERR_INVALID_INPUT (2), diagnostics on stderr, usage for a bare `vde`.

if [[ -z "${VDE_ROOT_DIR}" ]]; then
    export VDE_ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "${VDE_ROOT_DIR}" || exit 1

typeset TESTS_PASSED=0
typeset TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { echo -e "${YELLOW}[TEST]${RESET} $1"; }
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}

# run_vde ARGS...: sets rc, so_text (stdout) and se_text (stderr) for `vde ARGS`.
typeset rc so_text se_text
typeset _err_file="$(mktemp)"
trap 'rm -f "${_err_file}"' EXIT
run_vde() {
    so_text="$(zsh "${VDE_ROOT_DIR}/bin/vde" "$@" 2>"${_err_file}")"
    rc=$?
    se_text="$(<"${_err_file}")"
}

test_start "unknown command exits 2"
run_vde definitely-not-a-command
if (( rc == 2 )); then
    test_pass "exit 2"
else
    test_fail "unknown exit status" "expected 2, got ${rc}"
fi

test_start "unknown command reports on stderr, not stdout"
if [[ "${se_text}" == *"Unknown command 'definitely-not-a-command'"* && "${so_text}" != *"Unknown command"* ]]; then
    test_pass "stderr carries the diagnostic"
else
    test_fail "unknown stream" "stdout=[${so_text[1,120]}] stderr=[${se_text[1,120]}]"
fi

test_start "bare vde prints usage and exits 2"
run_vde
if (( rc == 2 )) && [[ "${so_text}" == *"Usage"* || "${so_text}" == *"usage"* ]]; then
    test_pass "usage shown, exit 2"
else
    test_fail "bare vde" "rc=${rc} stdout=[${so_text[1,120]}] stderr=[${se_text[1,120]}]"
fi

test_start "function-trace with no subcommand prints usage and exits 2"
run_vde function-trace
if (( rc == 2 )) && [[ "${so_text}" == *"Usage"* || "${so_text}" == *"usage"* ]] && [[ "${so_text}" != *"Command: vde help"* ]]; then
    test_pass "usage shown, exit 2, no trace report"
else
    test_fail "bare function-trace" "rc=${rc} stdout=[${so_text[1,120]}] stderr=[${se_text[1,120]}]"
fi

test_start "vde help still exits 0"
run_vde help
if (( rc == 0 )); then
    test_pass "help exit 0"
else
    test_fail "help exit status" "expected 0, got ${rc}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
