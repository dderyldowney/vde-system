#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)

# Unit Tests: setup scripts run devuser commands with sudo -H (Signet #555).
#
# `sudo -u devuser` alone does not guarantee HOME is devuser's home, so tools
# that install under ~ (pyenv, rustup, SDKMAN, PlatformIO, ...) can target the
# wrong directory. Every sudo that runs as devuser in scripts/setup/*.zsh must
# pass -H (elixir fix, defcb672). Static scan only; no Docker, no writes.

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

test_start "every devuser sudo in scripts/setup/*.zsh passes -H"
typeset -a offenders
typeset f line n
for f in scripts/setup/*.zsh; do
    n=0
    while IFS= read -r line; do
        (( n++ ))
        [[ "${line}" =~ '^[[:space:]]*#' ]] && continue
        # a sudo invocation that targets devuser (literal or ${DEVUSER}) ...
        # (strip the compliant "sudo -H -u" forms first so a second, piped
        # sudo on the same line is still caught)
        if [[ "${line//sudo -H -u/ok}" =~ 'sudo[^|;&]*-u[[:space:]]+"?(devuser|\$\{DEVUSER\})' ]]; then
            offenders+=("${f}:${n}")
        fi
    done < "${f}"
done
if (( ${#offenders} == 0 )); then
    test_pass "all devuser sudo calls use -H"
else
    test_fail "sudo -u without -H (${#offenders})" "${(j:, :)offenders}"
fi

echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
