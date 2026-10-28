#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: `vde dns-check` forwards the words as typed (Signet #532).
#
# bin/vde's flag loop consumes "$@" into input_targets before the case
# statement runs, so a `shift` inside dns-check) always died with
# "shift count must be <= $#" and the script never ran. The branch must hand
# the typed words to bin/vde-dns-check.zsh. Drives the canonical entrypoint with
# registered names; it needs no running Spoke (the script's only side effects are
# read-only `docker exec` probes, and the handshake log line carries the args).

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

# run_dns_check ARGS...: combined output of `vde dns-check ARGS` (no Docker
# needed: the log line is printed before any container is touched).
run_dns_check() {
    local -a words=("$@")
    zsh "${VDE_ROOT_DIR}/bin/vde" dns-check "${words[@]}" 2>&1
}

test_start "dns-check with source, target and port reaches vde-dns-check intact, in order"
typeset out="$(run_dns_check python rust 53)"
typeset -a shift_lines=(${(M)${(f)out}:#*shift count*})
if (( ${#shift_lines} )); then
    test_fail "argv shift" "dispatcher died: ${shift_lines[1]}"
elif [[ "${out}" == *"python"*"->"*"rust"*"(Port: 53)"* ]]; then
    test_pass "source, target and port 53 arrived in order"
else
    test_fail "forwarding" "no 'python -> rust (Port: 53)' in: ${out[1,300]}"
fi

test_start "dns-check without a port defaults to 22"
out="$(run_dns_check python rust)"
if [[ "${out}" == *"(Port: 22)"* ]]; then
    test_pass "default port 22"
else
    test_fail "default port" "no '(Port: 22)' in output: ${out[1,200]}"
fi

test_start "dns-check without arguments prints the script usage"
out="$(run_dns_check)"
if [[ "${out}" == *"Usage: vde dns-check"* && "${out}" != *"shift count"* ]]; then
    test_pass "usage reached"
else
    test_fail "usage" "expected script usage, got: ${out[1,200]}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
