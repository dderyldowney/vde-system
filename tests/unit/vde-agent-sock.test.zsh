#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Unit Tests for the VDE agent-socket guard (Signet #616).
#
# If a Spoke starts while the VDE ssh-agent is not listening, Docker creates the
# missing bind-mount source ~/.ssh/vde/agent.sock as an EMPTY, ROOT-OWNED
# DIRECTORY, after which the agent can never bind there. These tests pin:
#   1. vde_agent_sock_blocker: what may be cleared, what is only explained
#   2. vde_preflight_agent_socket: a Spoke start never reaches Docker with the
#      agent socket missing, and never with a directory in its place
#   3. the wiring: `vde start` runs the preflight before `compose up`, and
#      ensure_ssh_agent runs the blocker check

export VDE_TEST_MODE=1
typeset SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
typeset PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export VDE_ROOT_DIR="$PROJECT_ROOT"

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

typeset SCRATCH
SCRATCH=$(mktemp -d) || { echo "mktemp failed"; exit 1; }
trap 'chmod -R u+w -- "${SCRATCH}" 2>/dev/null; rm -rf -- "${SCRATCH}"' EXIT

# A listening unix socket file, left behind when the subshell exits
make_socket() { ( zmodload zsh/net/socket 2>/dev/null && zsocket -l "$1" ) >/dev/null 2>&1 }

# --- the helper under test (absent until the fix lands) -----------------------
if [[ -f "${PROJECT_ROOT}/lib/vde-agent-sock" ]]; then
    source "${PROJECT_ROOT}/lib/vde-agent-sock"
fi
if ! typeset -f vde_agent_sock_blocker >/dev/null; then
    test_start "lib/vde-agent-sock defines vde_agent_sock_blocker"
    test_fail "vde_agent_sock_blocker is not defined" "lib/vde-agent-sock missing or empty"
    echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
    exit 1
fi

typeset out rc

#-------------------------------------------------------------------------------
test_start "blocker: an absent path is clear"
out=$(vde_agent_sock_blocker "${SCRATCH}/absent.sock" 2>&1); rc=$?
[[ $rc -eq 0 && -z "${out}" ]] && test_pass "rc 0, silent" || test_fail "absent path" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "blocker: a real socket is clear and is left alone"
make_socket "${SCRATCH}/live.sock"
out=$(vde_agent_sock_blocker "${SCRATCH}/live.sock" 2>&1); rc=$?
[[ $rc -eq 0 && -S "${SCRATCH}/live.sock" ]] && test_pass "rc 0, socket kept" || test_fail "socket" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "blocker: an EMPTY directory owned by the caller is removed"
mkdir "${SCRATCH}/empty.sock"
out=$(vde_agent_sock_blocker "${SCRATCH}/empty.sock" 2>&1); rc=$?
if [[ $rc -eq 0 && ! -e "${SCRATCH}/empty.sock" && "${out}" == *"${SCRATCH}/empty.sock"* ]]; then
    test_pass "removed, and the notice names the path"
else
    test_fail "empty dir" "rc=${rc} exists=$([[ -e ${SCRATCH}/empty.sock ]] && echo yes || echo no) out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "blocker: a NON-EMPTY directory is never deleted, and the message says why"
mkdir "${SCRATCH}/full.sock"; print x > "${SCRATCH}/full.sock/keep"
out=$(vde_agent_sock_blocker "${SCRATCH}/full.sock" 2>&1); rc=$?
if [[ $rc -ne 0 && -f "${SCRATCH}/full.sock/keep" && "${out}" == *"${SCRATCH}/full.sock"* && "${out}" == *"not empty"* && "${out}" == *"vde ssh-setup start"* ]]; then
    test_pass "refused, contents intact, message names path and the next step"
else
    test_fail "non-empty dir" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "blocker: a hidden file also makes a directory non-empty"
mkdir "${SCRATCH}/hidden.sock"; print x > "${SCRATCH}/hidden.sock/.dot"
out=$(vde_agent_sock_blocker "${SCRATCH}/hidden.sock" 2>&1); rc=$?
[[ $rc -ne 0 && -f "${SCRATCH}/hidden.sock/.dot" ]] && test_pass "refused, dotfile kept" || test_fail "hidden" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "blocker: a regular file is never deleted"
print x > "${SCRATCH}/file.sock"
out=$(vde_agent_sock_blocker "${SCRATCH}/file.sock" 2>&1); rc=$?
if [[ $rc -ne 0 && -f "${SCRATCH}/file.sock" && "${out}" == *"not a socket"* ]]; then
    test_pass "refused, file kept"
else
    test_fail "regular file" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "blocker: a dangling symlink is never deleted"
ln -s "${SCRATCH}/nowhere" "${SCRATCH}/link.sock"
out=$(vde_agent_sock_blocker "${SCRATCH}/link.sock" 2>&1); rc=$?
[[ $rc -ne 0 && -L "${SCRATCH}/link.sock" ]] && test_pass "refused, link kept" || test_fail "symlink" "rc=${rc} out=${out}"

#-------------------------------------------------------------------------------
test_start "blocker: an empty directory that cannot be removed gets the exact sudo command, path quoted"
if (( EUID == 0 )); then
    test_pass "skipped: running as root"
else
    mkdir -p "${SCRATCH}/ro parent/stuck.sock"
    chmod a-w "${SCRATCH}/ro parent"
    typeset stuck="${SCRATCH}/ro parent/stuck.sock"
    out=$(vde_agent_sock_blocker "${stuck}" 2>&1); rc=$?
    chmod u+w "${SCRATCH}/ro parent"
    if [[ $rc -ne 0 && -d "${stuck}" && "${out}" == *"sudo rmdir ${(q)stuck}"* && "${out}" == *"vde ssh-setup start"* ]]; then
        test_pass "refused, message carries: sudo rmdir ${(q)stuck}"
    else
        test_fail "unremovable empty dir" "rc=${rc} out=${out}"
    fi
fi

#-------------------------------------------------------------------------------
test_start "blocker: an UNREADABLE non-empty directory is never deleted and is never called 'safe to rmdir' unconditionally"
if (( EUID == 0 )); then
    test_pass "skipped: running as root"
else
    mkdir -p "${SCRATCH}/dark.sock"; print x > "${SCRATCH}/dark.sock/keep"
    chmod 000 "${SCRATCH}/dark.sock"
    out=$(vde_agent_sock_blocker "${SCRATCH}/dark.sock" 2>&1); rc=$?
    chmod 700 "${SCRATCH}/dark.sock"
    # The directory lists as empty to this user, so the message must hedge ("If it is empty")
    # rather than assert it is empty, and the contents must survive.
    if [[ $rc -ne 0 && -f "${SCRATCH}/dark.sock/keep" && "${out}" == *"If it is empty"* ]]; then
        test_pass "refused, contents intact, message hedges"
    else
        test_fail "unreadable directory" "rc=${rc} out=${out}"
    fi
fi

#-------------------------------------------------------------------------------
test_start "blocker: removal does NOT depend on who owns the directory, only on rmdir succeeding (a root-owned dir in the user's own ~/.ssh/vde)"
# Docker's directory is root-owned but sits in a directory the user owns; rmdir
# needs write access to the PARENT only. An ownership test would block exactly
# that case, so the helper must not contain one.
if grep -vE '^[[:space:]]*#' "${PROJECT_ROOT}/lib/vde-agent-sock" | grep -qE '\[\[ +-O '; then
    test_fail "ownership gate present" "lib/vde-agent-sock tests [[ -O ]] before rmdir"
else
    test_pass "no ownership gate before rmdir"
fi

#-------------------------------------------------------------------------------
# Preflight: source the real libraries, then stub the two collaborators so no
# agent is ever started by the test.
unset _VDE_SHELL_COMPAT_LOADED _VDE_CONSTANTS_LOADED _VDE_CORE_GUARD_LOADED _VDE_SSH_LOADED _VDE_ERRORS_LOADED 2>/dev/null
export HOME="${SCRATCH}/home" VDE_HOME_DIR="${SCRATCH}/home"
mkdir -p "${HOME}/.ssh/vde"
source "${PROJECT_ROOT}/lib/vde-shell-compat"
source "${PROJECT_ROOT}/lib/vde-constants"
source "${PROJECT_ROOT}/lib/vde-core"
source "${PROJECT_ROOT}/lib/vde-ssh"

typeset -g STUB_ENSURE_CALLS=0 STUB_READY_RC=1 STUB_ENSURE_RC=0 STUB_ENSURE_MAKES_SOCKET=1
ensure_ssh_agent() {
    (( STUB_ENSURE_CALLS++ ))
    (( STUB_ENSURE_MAKES_SOCKET )) && make_socket "${VDE_SSH_AGENT_SOCK}"
    return ${STUB_ENSURE_RC}
}
_vde_ssh_agent_ready() { return ${STUB_READY_RC} }

reset_preflight() {
    rm -rf -- "${SCRATCH}/agent.sock"
    VDE_SSH_AGENT_SOCK="${SCRATCH}/agent.sock"
    STUB_ENSURE_CALLS=0 STUB_READY_RC=1 STUB_ENSURE_RC=0 STUB_ENSURE_MAKES_SOCKET=1
}

test_start "preflight is defined"
if typeset -f vde_preflight_agent_socket >/dev/null; then
    test_pass "vde_preflight_agent_socket exists"
else
    test_fail "vde_preflight_agent_socket is not defined" "lib/vde-ssh"
fi

if typeset -f vde_preflight_agent_socket >/dev/null; then
    #---------------------------------------------------------------------------
    test_start "preflight: no agent and no socket -> starts the agent, then succeeds"
    reset_preflight
    out=$(vde_preflight_agent_socket 2>&1); rc=$?
    # ensure_ssh_agent ran in the $(...) subshell, so judge by the socket it made
    [[ $rc -eq 0 && -S "${SCRATCH}/agent.sock" ]] && test_pass "agent started, socket present" || test_fail "start path" "rc=${rc} out=${out}"

    #---------------------------------------------------------------------------
    test_start "preflight: a healthy agent is not restarted"
    reset_preflight; make_socket "${SCRATCH}/agent.sock"; STUB_READY_RC=0
    vde_preflight_agent_socket >/dev/null 2>&1; rc=$?
    [[ $rc -eq 0 && ${STUB_ENSURE_CALLS} -eq 0 ]] && test_pass "ensure_ssh_agent not called" || test_fail "healthy agent" "rc=${rc} calls=${STUB_ENSURE_CALLS}"

    #---------------------------------------------------------------------------
    test_start "preflight: a non-empty directory at the socket path refuses and never starts an agent"
    reset_preflight; mkdir "${SCRATCH}/agent.sock"; print x > "${SCRATCH}/agent.sock/keep"
    vde_preflight_agent_socket >/dev/null 2>&1; rc=$?
    [[ $rc -ne 0 && ${STUB_ENSURE_CALLS} -eq 0 && -f "${SCRATCH}/agent.sock/keep" ]] && test_pass "refused before any agent start" || test_fail "dir blocker" "rc=${rc} calls=${STUB_ENSURE_CALLS}"

    #---------------------------------------------------------------------------
    test_start "preflight: an empty user-owned directory is cleared, then the agent starts"
    reset_preflight; mkdir "${SCRATCH}/agent.sock"
    out=$(vde_preflight_agent_socket 2>&1); rc=$?
    [[ $rc -eq 0 && -S "${SCRATCH}/agent.sock" ]] && test_pass "directory replaced by a socket" || test_fail "empty dir" "rc=${rc} out=${out}"

    #---------------------------------------------------------------------------
    test_start "preflight: the agent cannot start -> refuses"
    reset_preflight; STUB_ENSURE_RC=1 STUB_ENSURE_MAKES_SOCKET=0
    vde_preflight_agent_socket >/dev/null 2>&1; rc=$?
    [[ $rc -ne 0 ]] && test_pass "non-zero" || test_fail "agent start failed" "rc=${rc}"

    #---------------------------------------------------------------------------
    test_start "preflight: ensure_ssh_agent succeeds but no socket exists -> refuses (Docker would create a directory)"
    reset_preflight; STUB_ENSURE_MAKES_SOCKET=0
    out=$(vde_preflight_agent_socket 2>&1); rc=$?
    [[ $rc -ne 0 && "${out}" == *"${SCRATCH}/agent.sock"* ]] && test_pass "refused, message names the path" || test_fail "no socket" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
# Wiring pins. Match EXECUTABLE lines only: a comment must not satisfy them.
exec_lines() { grep -nvE '^[[:space:]]*(#|$)' "$1" }

test_start "wiring: vde start runs the preflight before the spinner opens and before compose up"
typeset actions="${PROJECT_ROOT}/lib/vde-actions"
typeset pre_line spin_line up_line
pre_line=$(exec_lines "${actions}" | grep -m1 'vde_preflight_agent_socket' | cut -d: -f1)
spin_line=$(exec_lines "${actions}" | grep -m1 'vde_progress_spinner_start "Igniting' | cut -d: -f1)
up_line=$(exec_lines "${actions}" | grep -m1 'compose_up_cmd+=(up -d)' | cut -d: -f1)
if [[ -n "${pre_line}" && -n "${spin_line}" && -n "${up_line}" && ${pre_line} -lt ${spin_line} && ${spin_line} -lt ${up_line} ]]; then
    test_pass "preflight (line ${pre_line}) < spinner (line ${spin_line}) < 'up -d' (line ${up_line})"
else
    test_fail "start wiring" "preflight='${pre_line}' spinner='${spin_line}' up='${up_line}'"
fi

test_start "wiring: a failed preflight releases the Spoke lock and skips ignition"
# The failure branch must release the lock it just claimed, or the next start waits on it.
typeset branch
branch=$(exec_lines "${actions}" | grep -A5 'if ! vde_preflight_agent_socket' )
if [[ "${branch}" == *"release_lock"* && "${branch}" == *"continue"* ]]; then
    test_pass "release_lock then continue"
else
    test_fail "failure branch" "${branch}"
fi

test_start "wiring: the pre-commit hook shows the spine check's output when it fails"
if exec_lines "${PROJECT_ROOT}/githooks/pre-commit" | grep -q 'spine_out'; then
    test_pass "failure output is surfaced"
else
    test_fail "pre-commit hook" "spine output is still discarded"
fi

test_start "wiring: ensure_ssh_agent checks the socket path before starting an agent"
if exec_lines "${PROJECT_ROOT}/lib/vde-ssh" | grep -q 'vde_agent_sock_blocker'; then
    test_pass "lib/vde-ssh calls vde_agent_sock_blocker"
else
    test_fail "ensure_ssh_agent wiring" "no executable call to vde_agent_sock_blocker in lib/vde-ssh"
fi

test_start "wiring: the spine check shares the same helper"
if exec_lines "${PROJECT_ROOT}/bin/vde-spine-check.zsh" | grep -q 'vde-agent-sock'; then
    test_pass "bin/vde-spine-check.zsh sources lib/vde-agent-sock"
else
    test_fail "spine wiring" "bin/vde-spine-check.zsh does not source lib/vde-agent-sock"
fi

echo ""
echo "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 ))
