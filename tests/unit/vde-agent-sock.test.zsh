#!/usr/bin/env zsh
# @armor (Engine Core)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

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
test_start "blocker: a symlink to a LIVE socket is refused (it could be someone else's agent) and is not deleted"
make_socket "${SCRATCH}/real-agent.sock"
ln -s "${SCRATCH}/real-agent.sock" "${SCRATCH}/linked.sock"
out=$(vde_agent_sock_blocker "${SCRATCH}/linked.sock" 2>&1); rc=$?
if [[ $rc -ne 0 && -L "${SCRATCH}/linked.sock" && -S "${SCRATCH}/real-agent.sock" && "${out}" == *"symbolic link"* ]]; then
    test_pass "refused, link and target kept, message says symbolic link"
else
    test_fail "symlink to a live socket" "rc=${rc} out=${out}"
fi

#-------------------------------------------------------------------------------
test_start "blocker: a REAL root-owned empty directory (created by Docker, as in the bug) is removed without sudo"
# This is the exact artifact of Signet #616: Docker makes the directory as root inside
# a folder the user owns. Needs a local alpine image; skipped, never pulled, otherwise.
if ! command -v docker >/dev/null 2>&1 || ! docker image inspect alpine >/dev/null 2>&1; then
    test_pass "skipped: docker or a local alpine image is not available"
else
    mkdir -p "${SCRATCH}/rootparent"
    if docker run --rm -v "${SCRATCH}/rootparent:/m" alpine mkdir /m/agent.sock >/dev/null 2>&1 \
        && [[ "$(stat -c %U "${SCRATCH}/rootparent/agent.sock" 2>/dev/null)" == "root" ]]; then
        out=$(vde_agent_sock_blocker "${SCRATCH}/rootparent/agent.sock" 2>&1); rc=$?
        if [[ $rc -eq 0 && ! -e "${SCRATCH}/rootparent/agent.sock" ]]; then
            test_pass "root-owned directory removed by an unprivileged user"
        else
            test_fail "root-owned directory" "rc=${rc} out=${out}"
        fi
    else
        test_pass "skipped: could not create a root-owned directory through docker"
    fi
fi

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
typeset gate
gate=$(grep -vE '^[[:space:]]*#' "${PROJECT_ROOT}/lib/vde-agent-sock" | grep -E '(\[\[ +-[OG] |\bstat\b|\bzstat\b|\$\{?E?UID\}?|\bid -u\b|\bwhoami\b)')
if [[ -n "${gate}" ]]; then
    test_fail "ownership gate present" "lib/vde-agent-sock inspects ownership or the caller: ${gate}"
else
    test_pass "no ownership/identity gate anywhere in the helper (the real root-owned case is exercised above when docker is available)"
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

# Line number of the first EXECUTABLE line of FILE matching PATTERN (zsh expansion, no cut).
first_line_no() {
    local hit
    hit=$(exec_lines "$1" | grep -m1 -- "$2") || return 1
    print -r -- "${hit%%:*}"
}

# Executable lines of the function NAME in FILE, up to its closing brace in column 0.
fn_body() {
    local line in_fn=0
    for line in "${(@f)$(<"$1")}"; do
        if (( ! in_fn )); then
            [[ "${line}" == "$2() {"* ]] && in_fn=1
            continue
        fi
        [[ "${line}" == "}" ]] && break
        [[ "${line}" =~ '^[[:space:]]*(#|$)' ]] || print -r -- "${line}"
    done
}

test_start "wiring: vde start orders image check/rebuild < preflight < socket discovery < compose up"
# The preflight must come AFTER the image check, which can trigger a rebuild lasting
# minutes (a long gap between "agent is up" and "compose mounts it" is where a stopped
# agent would let Docker create the directory), and BEFORE discovery and compose up.
typeset actions="${PROJECT_ROOT}/lib/vde-actions"
typeset rebuild_line pre_line disc_line up_line
rebuild_line=$(first_line_no "${actions}" 'bin/vde-rebuild')
pre_line=$(first_line_no "${actions}" 'vde_preflight_agent_socket')
disc_line=$(first_line_no "${actions}" 'vde_get_host_ssh_sock)')
up_line=$(first_line_no "${actions}" 'compose_up_cmd+=(up -d)')
if [[ -n "${rebuild_line}" && -n "${pre_line}" && -n "${disc_line}" && -n "${up_line}" \
    && ${rebuild_line} -lt ${pre_line} && ${pre_line} -lt ${disc_line} && ${disc_line} -lt ${up_line} ]]; then
    test_pass "rebuild (${rebuild_line}) < preflight (${pre_line}) < discovery (${disc_line}) < 'up -d' (${up_line})"
else
    test_fail "start wiring" "rebuild='${rebuild_line}' preflight='${pre_line}' discovery='${disc_line}' up='${up_line}'"
fi

test_start "wiring: the preflight's output is captured and printed only after the spinner stops"
typeset pf_block
pf_block=$(exec_lines "${actions}" | grep -A8 'preflight_out=\$(vde_preflight_agent_socket')
typeset before_stop="${pf_block%%vde_progress_spinner_stop*}"
typeset before_print="${pf_block%%print -r -- *preflight_out*}"
if [[ "${pf_block}" == *"vde_progress_spinner_stop"* && "${pf_block}" == *"print -r -- "*"preflight_out"* ]] \
    && (( ${#before_stop} < ${#before_print} )); then
    test_pass "spinner_stop precedes the print of the captured output"
else
    test_fail "spinner ordering" "${pf_block}"
fi

test_start "wiring: a failed preflight releases the Spoke lock and skips ignition"
# The failure branch must release the lock it just claimed, or the next start waits on it.
typeset branch
branch=$(exec_lines "${actions}" | grep -A6 'if (( preflight_rc != 0 ))')
if [[ "${branch}" == *"release_lock"* && "${branch}" == *"continue"* ]]; then
    test_pass "release_lock then continue"
else
    test_fail "failure branch" "${branch}"
fi

test_start "wiring: the pre-commit hook shows the spine check's output when it fails"
# Capturing the output is not enough: it must also be PRINTED, or it is still discarded.
if exec_lines "${PROJECT_ROOT}/githooks/pre-commit" | grep -q 'spine_out=\$(' \
    && exec_lines "${PROJECT_ROOT}/githooks/pre-commit" | grep -qE 'print .*\$\{spine_out\}'; then
    test_pass "failure output is captured and printed"
else
    test_fail "pre-commit hook" "spine output is not both captured and printed"
fi

test_start "wiring: ensure_ssh_agent ITSELF checks the socket path before starting an agent"
# Inside the function body, not merely somewhere in the library: the preflight also
# calls the blocker, so a whole-file match would survive its removal from ensure_ssh_agent.
if fn_body "${PROJECT_ROOT}/lib/vde-ssh" ensure_ssh_agent | grep -q 'vde_agent_sock_blocker'; then
    test_pass "ensure_ssh_agent calls vde_agent_sock_blocker"
else
    test_fail "ensure_ssh_agent wiring" "no executable call to vde_agent_sock_blocker inside ensure_ssh_agent"
fi

test_start "wiring: the preflight itself calls the blocker first"
if fn_body "${PROJECT_ROOT}/lib/vde-ssh" vde_preflight_agent_socket | grep -q 'vde_agent_sock_blocker'; then
    test_pass "vde_preflight_agent_socket calls vde_agent_sock_blocker"
else
    test_fail "preflight wiring" "no executable call to vde_agent_sock_blocker inside vde_preflight_agent_socket"
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
