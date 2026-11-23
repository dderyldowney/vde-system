#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests for Pillar IV of the spine check when ~/.ssh/vde/agent.sock is a
# DIRECTORY (Signet #616). Docker creates that directory, as root, when a Spoke
# starts before the VDE agent is listening. The check used to report it as a
# socket-path-length problem; it must name the real cause and the real fix.
#
# The real script runs against a scratch HOME in CI mode (no Docker probe).

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
test_pass()  { echo -e "${GREEN}[PASS]${RESET} $1"; ((TESTS_PASSED++)); return 0; }
test_fail()  { echo -e "${RED}[FAIL]${RESET} $1: $2"; ((TESTS_FAILED++)); return 0; }

typeset SPINE="${VDE_ROOT_DIR}/bin/vde-spine-check.zsh"
typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "mktemp failed"; exit 1; }

# Kill any agent the spine check started inside the scratch HOME, then clean up.
cleanup() {
    pkill -u "${UID}" -f -- "ssh-agent -s -a ${SCRATCH}/" 2>/dev/null
    rm -rf -- "${SCRATCH}"
}
trap cleanup EXIT

# Run the spine check with HOME=$1; sets spine_out and spine_rc.
typeset spine_out spine_rc
run_spine() {
    spine_rc=0
    spine_out=$(env HOME="$1" VDE_CI_MODE=1 zsh "${SPINE}" 2>&1) || spine_rc=$?
}

#-------------------------------------------------------------------------------
test_start "a NON-EMPTY directory at agent.sock fails Pillar IV and names the directory as the cause"
typeset h1="${SCRATCH}/h1"
mkdir -p "${h1}/.ssh/vde/agent.sock"; print x > "${h1}/.ssh/vde/agent.sock/keep"
run_spine "${h1}"
if (( spine_rc != 0 )) \
    && [[ "${spine_out}" == *"${h1}/.ssh/vde/agent.sock"* && "${spine_out}" == *"directory"* ]] \
    && [[ "${spine_out}" != *"characters; unix socket paths"* ]] \
    && [[ -f "${h1}/.ssh/vde/agent.sock/keep" ]]; then
    test_pass "fails, names the directory, no path-length red herring, contents kept"
else
    test_fail "non-empty directory" "rc=${spine_rc} out=${spine_out}"
fi

#-------------------------------------------------------------------------------
test_start "a regular file at agent.sock fails Pillar IV and is not deleted"
typeset h2="${SCRATCH}/h2"
mkdir -p "${h2}/.ssh/vde"; print x > "${h2}/.ssh/vde/agent.sock"
run_spine "${h2}"
if (( spine_rc != 0 )) && [[ "${spine_out}" == *"not a socket"* ]] && [[ -f "${h2}/.ssh/vde/agent.sock" ]]; then
    test_pass "fails, says not a socket, file kept"
else
    test_fail "regular file" "rc=${spine_rc} out=${spine_out}"
fi

#-------------------------------------------------------------------------------
test_start "an EMPTY user-owned directory at agent.sock is cleared and the agent starts there"
typeset h3="${SCRATCH}/h3"
mkdir -p "${h3}/.ssh/vde/agent.sock"
run_spine "${h3}"
# The identity step fails later (no vde_student key in the scratch HOME); what
# matters is that the directory is gone and a real socket took its place.
if [[ -S "${h3}/.ssh/vde/agent.sock" \
    && "${spine_out}" == *"Removed the empty directory at ${h3}/.ssh/vde/agent.sock"* \
    && "${spine_out}" != *"characters; unix socket paths"* ]]; then
    test_pass "directory replaced by a live agent socket, and the check said what it did"
else
    test_fail "empty directory" "rc=${spine_rc} socket=$([[ -e ${h3}/.ssh/vde/agent.sock ]] && echo present-not-socket || echo absent) out=${spine_out}"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
