#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# Medium Integration Test: the Sovereign runner's containers column against the REAL docker daemon (Signet #774)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# A MEDIUM test: it uses the real docker daemon, so the containers column of the runner's SUITE TIMING table is
# checked against what docker really recorded. It is NOT run by the Sovereign runner (it is not in its suite list).
# It never starts a container: the fixture suite only runs `docker create` (two containers, label vde.test=true,
# image alpine:latest, never started) and `docker rm` on them. The runner in the fixture is the REAL current runner,
# run with PATH unchanged and HOME set to a scratch caller home. Rule K is untouched.
# Without a docker daemon or the alpine:latest image it prints one [SKIP] line and exits 0 WITHOUT counting a pass.
# DAEMON-WIDE COUNT: the containers column counts every container CREATE event the daemon reports inside a suite's
# time window, not only this test's containers. On a shared daemon other clients can add to it, so the assertions
# check lower bounds and ordering (creates >= 2; empty < creates), never an exact value.
# SIGNALS: an EXIT trap does not run when zsh is killed by a signal, so INT and TERM run the same cleanup first.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_POL_STAMP_TTL VDE_TEST_TIMING_FILE VDE_DOCKER_EVENTS_TIMEOUT

typeset ROOT="${0:A:h:h:h}"
typeset RUNNER_SRC="${ROOT}/tests/run-sovereign-tests.zsh"
typeset LIBENV_SRC="${ROOT}/lib/vde-test-env"
typeset -g OUT='' RC=0
typeset -g REAL_HOME="${HOME}"
typeset -g REAL_DOCKER_CONFIG="${DOCKER_CONFIG:-${REAL_HOME}/.docker}"
typeset -i PASSED=0 FAILED=0
typeset -a BOUND=()
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { print -P "${YELLOW}[TEST]${RESET} $1"; }
# not ((x++)): that returns 1 when x was 0 and would trip the `&& pass || fail` pattern
test_pass()  { print -P "${GREEN}[PASS]${RESET} $1"; PASSED=$(( PASSED + 1 )); }
test_fail()  { print -n -P "${RED}[FAIL]${RESET} "; print -r -- "$1: $2"; FAILED=$(( FAILED + 1 )); }
test_skip()  { print -r -- "[SKIP] $1; this medium test needs a docker daemon and the alpine image"; exit 0; }

# ---------------------------------------------------------------------------
# Precheck: docker answers, the alpine image exists locally, and every docker call is bounded
# ---------------------------------------------------------------------------

if command -v timeout >/dev/null 2>&1; then BOUND=( timeout 30 )
elif command -v gtimeout >/dev/null 2>&1; then BOUND=( gtimeout 30 )
else test_skip "neither timeout nor gtimeout is on PATH"
fi
"${BOUND[@]}" docker version >/dev/null 2>&1 || test_skip "the docker daemon does not answer docker version (or docker is missing)"
"${BOUND[@]}" docker image inspect alpine:latest >/dev/null 2>&1 || test_skip "the alpine:latest image is not present locally"

typeset SCRATCH
SCRATCH="$(vde_test_env_dir)" && [[ -n "${SCRATCH}" ]] || exit 1
SCRATCH="$(mktemp -d "${SCRATCH}/runner-timing-docker.XXXXXX")" || exit 1

# ---------------------------------------------------------------------------
# Containers: only the ones this test names; never a container it did not create
# ---------------------------------------------------------------------------

list_test_containers() {  # prints the names of the vde.test=true containers (all states); status 1 when docker ps fails
    local out
    out="$("${BOUND[@]}" docker ps -a --filter label=vde.test=true --format '{{.Names}}' 2>/dev/null)" || return 1
    print -r -- "${out}"
    return 0
}

cleanup_containers() {  # removes every vde-timing-test-* container carrying the test label (never any other)
    local name
    for name in ${(f)"$(list_test_containers)"}; do
        [[ "${name}" == vde-timing-test-* ]] && "${BOUND[@]}" docker rm -f -- "${name}" >/dev/null 2>&1
    done
    return 0
}

cleanup_all() {  # the one cleanup: test containers, the scratch Projects base, the scratch directory
    cleanup_containers
    vde_test_env_leave 2>/dev/null
    rm -rf -- "${SCRATCH}"
    return 0
}

trap 'cleanup_all' EXIT
# These replace the library's TRAPINT/TRAPTERM (lib/vde-test-env defines them only when absent), so a kill also
# removes the containers. The EXIT trap is cleared first so the exit does not run the cleanup twice.
TRAPINT()  { emulate -L zsh; cleanup_all; trap - EXIT; exit 130; }
TRAPTERM() { emulate -L zsh; cleanup_all; trap - EXIT; exit 143; }
# SIGHUP (a closed terminal) has no handler in the library: measured, a container was left behind without this.
TRAPHUP()  { emulate -L zsh; cleanup_all; trap - EXIT; exit 129; }

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

new_fixture() {  # new_fixture NAME -> SCRATCH/NAME: the REAL runner and lib, stub audit and integration suite, real-docker unit suites
    local f="${SCRATCH}/$1"
    mkdir -p "${f}/tests/unit" "${f}/tests/integration" "${f}/tests/features/core-infrastructure" \
        "${f}/bin" "${f}/lib" "${f}/callerhome" || return 1
    cp "${RUNNER_SRC}" "${f}/tests/run-sovereign-tests.zsh" || return 1
    cp "${LIBENV_SRC}" "${f}/lib/vde-test-env" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/bin/vde-enforce-uap.zsh" || return 1
    print -l -- '#!/usr/bin/env zsh' \
        'docker create --label vde.test=true --name vde-timing-test-one alpine:latest true >/dev/null || exit 1' \
        'docker create --label vde.test=true --name vde-timing-test-two alpine:latest true >/dev/null || exit 1' \
        'zmodload zsh/zselect || exit 1' \
        'zselect -t 200' \
        'docker rm vde-timing-test-one vde-timing-test-two >/dev/null || exit 1' \
        'exit 0' > "${f}/tests/unit/creates.test.zsh" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/tests/unit/empty.test.zsh" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/tests/integration/vm-lifecycle-integration.test.zsh" || return 1
    print -l -- '@forge' 'Feature: stub' > "${f}/tests/features/core-infrastructure/proof-of-life-the-contract.feature" || return 1
    chmod +x "${f}/bin/vde-enforce-uap.zsh" "${f}/tests/unit/"*.test.zsh "${f}/tests/integration/"*.test.zsh
}

run_runner() {  # run_runner FIXTURE TIMINGFILE -> OUT (colour codes removed) and RC (the runner's exit status)
    local fix="$1" timing="$2" raw
    # VDE_TEST_JOBS=1: per-suite container counts exist only in serial mode (parallel unit suites show n/a).
    raw="$(cd "${fix}" && timeout 300 env HOME="${fix}/callerhome" DOCKER_CONFIG="${REAL_DOCKER_CONFIG}" \
        VDE_TEST_TIMING_FILE="${timing}" VDE_TEST_JOBS=1 zsh tests/run-sovereign-tests.zsh 2>&1)"
    RC=$?
    OUT="$(print -r -- "${raw}" | sed 's/\x1b\[[0-9;]*m//g')"
}

row_of() {  # row_of NAME -> the SUITE TIMING row whose first field is NAME (a row has "<n>.<d>s" as its second field); status 1 if none
    local line
    local -a w
    for line in "${(@f)OUT}"; do
        w=( ${(z)line} )
        if [[ "${w[1]:-}" == "$1" && "${w[2]:-}" == *s ]]; then print -r -- "${line}"; return 0; fi
    done
    return 1
}

# ---------------------------------------------------------------------------
# Case 1: the real runner runs two real-docker suites (creates 2 containers, empty creates none)
# ---------------------------------------------------------------------------

cleanup_containers
new_fixture real-docker || exit 1
typeset FIX="${SCRATCH}/real-docker" TIMING="${SCRATCH}/timing.txt"
run_runner "${FIX}" "${TIMING}"

test_start "1a: the fixture runner exits 0 (the audit, both unit suites and the integration stub pass)"
if [[ "${RC}" == 0 ]]; then
    test_pass "1a the fixture runner exits 0"
else
    test_fail "1a the fixture runner exits 0" "rc=${RC} out: ${OUT[1,400]//$'\n'/ | }"
fi

test_start "1b the SUITE TIMING row for creates.test.zsh reports at least 2 containers (daemon-wide count)"
typeset ROW='' CREATES_COUNT=''
ROW="$(row_of creates.test.zsh)" || ROW=''
typeset -a W=( ${(z)ROW} )
CREATES_COUNT="${W[-1]:-}"
if [[ -n "${ROW}" && "${CREATES_COUNT}" == <-> ]] && (( CREATES_COUNT >= 2 )); then
    test_pass "1b creates.test.zsh row: ${ROW}"
else
    test_fail "1b the SUITE TIMING row for creates.test.zsh reports at least 2 containers" "row='${ROW}' out: ${OUT[1,400]//$'\n'/ | }"
fi

test_start "1c the SUITE TIMING row for empty.test.zsh (creates nothing) reports a count strictly below the creates row"
typeset EMPTY_ROW='' EMPTY_COUNT=''
EMPTY_ROW="$(row_of empty.test.zsh)" || EMPTY_ROW=''
typeset -a EW=( ${(z)EMPTY_ROW} )
EMPTY_COUNT="${EW[-1]:-}"
if [[ -n "${EMPTY_ROW}" && "${EMPTY_COUNT}" == <-> && "${CREATES_COUNT}" == <-> ]] && (( EMPTY_COUNT < CREATES_COUNT )); then
    test_pass "1c empty.test.zsh row: ${EMPTY_ROW}"
else
    test_fail "1c the SUITE TIMING row for empty.test.zsh reports a count strictly below the creates row" "row='${EMPTY_ROW}' creates=${CREATES_COUNT:-none} out: ${OUT[1,400]//$'\n'/ | }"
fi

test_start "1d no vde-timing-test-* container carrying vde.test=true remains after the run"
typeset ALL_NAMES='' LEFT='' name
if ALL_NAMES="$(list_test_containers)"; then
    for name in ${(f)ALL_NAMES}; do
        [[ "${name}" == vde-timing-test-* ]] && LEFT+="${name} "
    done
    if [[ -z "${LEFT}" ]]; then
        test_pass "1d no vde-timing-test-* container is left behind"
    else
        test_fail "1d no vde-timing-test-* container remains" "left: ${LEFT}"
    fi
else
    test_fail "1d no vde-timing-test-* container remains" "docker ps -a failed after the run"
fi

# ---------------------------------------------------------------------------
# Cleanup and the final line
# ---------------------------------------------------------------------------

print -r -- "Passed: ${PASSED}  Failed: ${FAILED}"
if (( FAILED )); then exit 1; fi
exit 0
