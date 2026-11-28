#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
# Test runs use their own scratch Projects base (lib/vde-test-env), never the caller's.
source "${0:A:h:h:h}/lib/vde-test-env" && vde_test_env_enter || exit 1

# Unit Tests: the flake rerun of the Sovereign runner (Signet #779, step A).
#
# A suite that fails is rerun once. A pass on the rerun is reported FLAKY (never as a plain pass), counts as passed,
# is listed in the summary with its first exit code, and the run exits 0. A failure on the rerun is a real failure:
# the run exits 1. VDE_FLAKE_RERUN=0 turns the rerun off, =1 turns it on, any other value exits 2 before anything
# runs; an empty value is unset, so the default (on) applies.
#
# This file runs a copy of the real runner in a stub fixture (stub audit, stub integration suite, stub docker on
# PATH, no containers, no network). Each stub suite counts its own runs in a file under RP_STATE, so a case can see
# exactly how many times the runner executed it. Both the serial path (VDE_TEST_JOBS=1) and the pool are covered.

# GIT_* scrub (Signet #656): the variables that select a repository would make the fixture write into the enclosing one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
unset VDE_TEST_JOBS VDE_TEST_TIMING_FILE VDE_DOCKER_EVENTS_TIMEOUT VDE_POL_STAMP_TTL

typeset ROOT="${0:A:h:h:h}"
typeset RUNNER_SRC="${ROOT}/tests/run-sovereign-tests.zsh"
typeset LIBENV_SRC="${ROOT}/lib/vde-test-env"
typeset -g OUT='' RC=0 FWHY='' TSECS=none RUNS=0 SER_OUT='' POOL_OUT=''
typeset TESTS_PASSED=0 TESTS_FAILED=0
if [[ -t 1 ]]; then
    typeset GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[0;33m' RESET='\033[0m'
else
    typeset GREEN='' RED='' YELLOW='' RESET=''
fi
test_start() { print -P "${YELLOW}[TEST]${RESET} $1"; }
# not ((x++)): that returns 1 when x was 0 and would trip the `&& pass || fail` pattern
test_pass()  { print -P "${GREEN}[PASS]${RESET} $1"; TESTS_PASSED=$(( TESTS_PASSED + 1 )); }
test_fail()  { print -n -P "${RED}[FAIL]${RESET} "; print -r -- "$1: $2"; TESTS_FAILED=$(( TESTS_FAILED + 1 )); }

typeset SCRATCH
SCRATCH="$(vde_test_env_dir)" && [[ -n "${SCRATCH}" ]] || exit 1
SCRATCH="$(mktemp -d "${SCRATCH}/runner-flaky.XXXXXX")" || exit 1
trap 'rm -rf -- "${SCRATCH}"' EXIT

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

new_fixture() {  # new_fixture NAME -> SCRATCH/NAME: the REAL runner and lib, a stub audit, a stub integration suite, a stub docker; no unit suites yet
    local f="${SCRATCH}/$1"
    mkdir -p "${f}/tests/unit" "${f}/tests/integration" "${f}/tests/features/core-infrastructure" \
        "${f}/bin" "${f}/lib" "${f}/stubs" "${f}/callerhome" "${f}/state" "${f}/tmproot" || return 1
    cp "${RUNNER_SRC}" "${f}/tests/run-sovereign-tests.zsh" || return 1
    cp "${LIBENV_SRC}" "${f}/lib/vde-test-env" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/bin/vde-enforce-uap.zsh" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/tests/integration/vm-lifecycle-integration.test.zsh" || return 1
    print -l -- '@forge' 'Feature: stub' > "${f}/tests/features/core-infrastructure/proof-of-life-the-contract.feature" || return 1
    print -l -- '#!/usr/bin/env zsh' 'exit 0' > "${f}/stubs/docker" || return 1
    print -l -- '# Serial unit suites (fixture): header only' > "${f}/tests/serial-unit-suites.txt" || return 1
    chmod +x "${f}/bin/vde-enforce-uap.zsh" "${f}/tests/integration/vm-lifecycle-integration.test.zsh" \
        "${f}/stubs/docker" || return 1
}

write_suite() {  # write_suite FILE: the suite body arrives on stdin; the file is made executable
    cat > "$1" && chmod +x "$1"
}

count_suite() {  # count_suite FILE FIRST LATER: a stub suite that counts its runs in RP_STATE/run-count.<suite>, exits FIRST on its first run and LATER after
    {
        print -r -- '#!/usr/bin/env zsh'
        print -r -- "typeset -i first_rc=$2 later_rc=$3"
        cat <<'STUB'
# runner-flaky fixture: counts its runs in RP_STATE, exits first_rc on the first run and later_rc after it
typeset f="${RP_STATE}/run-count.${0:t}" n=0
[[ -f "${f}" ]] && n="$(<"${f}")"
n=$(( n + 1 ))
print -r -- "${n}" > "${f}"
print -r -- "FLAKE-STUB ${0:t} run ${n}"
(( n == 1 )) && exit ${first_rc}
exit ${later_rc}
STUB
    } > "$1" && chmod +x "$1"
}

run_par() {  # run_par FIXTURE [NAME=value ...] -> OUT (colour codes removed) and RC (the runner's exit status); clean environment
    setopt localoptions extendedglob
    local fix="$1" raw
    shift
    raw="$(cd "${fix}" && timeout 120 env -i HOME="${fix}/callerhome" PATH="${fix}/stubs:${PATH}" \
        TMPDIR="${fix}/tmproot" RP_STATE="${fix}/state" FIXTURE_CALLER_HOME="${fix}/callerhome" \
        "$@" zsh tests/run-sovereign-tests.zsh 2>&1; print -r -- "RC=$?")"
    RC="${raw##*RC=}"
    OUT="${raw%RC=*}"
    OUT="${OUT//$'\e'\[[0-9\;]#m/}"
}

has_line() {  # has_line TEXT: status 0 when a line of OUT contains TEXT literally
    local line
    for line in "${(@f)OUT}"; do
        [[ "${line}" == *"$1"* ]] && return 0
    done
    return 1
}

run_count() {  # run_count STATEDIR SUITE -> RUNS: how many times the stub ran (0 when it never ran)
    local f="$1/run-count.$2"
    RUNS=0
    [[ -f "${f}" ]] && RUNS="$(<"${f}")"
}

timing_seconds() {  # timing_seconds TEXT NAME -> TSECS: the seconds cell of NAME's row in the SUITE TIMING table of TEXT, or "none"
    local text="$1" line
    local -a w
    local -i on=0
    TSECS=none
    for line in "${(@f)text}"; do
        [[ "${line}" == *'SUITE TIMING'* ]] && on=1
        (( on )) || continue
        w=( ${(z)line} )
        if [[ "${w[1]:-}" == "$2" ]]; then TSECS="${w[2]:-}"; return 0; fi
    done
}

timing_has_comma() {  # timing_has_comma TEXT: status 0 when a line of the SUITE TIMING section of TEXT (header through the Total line) has a comma
    local text="$1" line
    local -i on=0
    for line in "${(@f)text}"; do
        [[ "${line}" == *'SUITE TIMING'* ]] && on=1
        (( on )) || continue
        [[ "${line}" == *,* ]] && return 0
        [[ "${line}" == *'Total suite time'* ]] && break
    done
    return 1
}

flaky_findings() {  # flaky_findings STATEDIR SUITE -> FWHY: the checks of a suite that failed (exit 7), was rerun and passed (empty when all hold)
    local st="$1" s="$2"
    FWHY=''
    run_count "${st}" "${s}"
    (( RUNS == 2 )) || FWHY+=" runs=${RUNS}(want 2)"
    has_line "${s} FLAKY: failed (exit code: 7), then passed on the rerun" || FWHY+=" no FLAKY result line"
    has_line "${s} passed (" && FWHY+=" a plain 'passed (' line is present"
    has_line 'WARNING: 1 FLAKY suite(s)' || FWHY+=" no FLAKY warning in the summary"
    has_line "FLAKY: ${s} (first run: exit code 7)" || FWHY+=" no 'FLAKY: ... (first run: exit code 7)' summary entry"
    has_line "FLAKE-STUB ${s} run 2" || FWHY+=" the rerun's output is missing"
    [[ "${RC}" == 0 ]] || FWHY+=" rc=${RC}(want 0)"
}

twice_findings() {  # twice_findings STATEDIR SUITE -> FWHY: the checks of a suite that failed (exit 3) on the run and again on the rerun (empty when all hold)
    local st="$1" s="$2"
    FWHY=''
    run_count "${st}" "${s}"
    (( RUNS == 2 )) || FWHY+=" runs=${RUNS}(want 2)"
    has_line "${s} failed (exit code: 3) and failed again on the rerun (exit code: 3)" || FWHY+=" no 'failed again on the rerun' line"
    has_line "${s} FLAKY" && FWHY+=" a FLAKY line is present"
    has_line 'FAIL: 1 test suites failed' || FWHY+=" no 'FAIL: 1 test suites failed' line"
    [[ "${OUT}" == *'Failed Suites:'*"${s}"* ]] || FWHY+=" not listed under Failed Suites"
    [[ "${RC}" == 1 ]] || FWHY+=" rc=${RC}(want 1)"
}

once_findings() {  # once_findings STATEDIR SUITE -> FWHY: a suite that passed was executed exactly once, and nothing in the run is FLAKY or reruns (empty when all hold)
    local st="$1" s="$2"
    FWHY=''
    run_count "${st}" "${s}"
    (( RUNS == 1 )) || FWHY+=" ${s} runs=${RUNS}(want 1)"
    has_line 'FLAKY' && FWHY+=" a FLAKY word is in the output"
    has_line 'rerunning once' && FWHY+=" a rerun was started"
}

off_findings() {  # off_findings STATEDIR SUITE -> FWHY: a failing suite with the rerun switched off runs once, fails with RC 1, and prints no rerun text (empty when all hold)
    local st="$1" s="$2"
    FWHY=''
    run_count "${st}" "${s}"
    (( RUNS == 1 )) || FWHY+=" runs=${RUNS}(want 1)"
    has_line "${s} failed (exit code: 7) (" || FWHY+=" no plain 'failed (exit code: 7)' line"
    has_line 'rerun' && FWHY+=" rerun text is in the output"
    has_line 'FLAKY' && FWHY+=" a FLAKY word is in the output"
    [[ "${RC}" == 1 ]] || FWHY+=" rc=${RC}(want 1)"
}

# ---------------------------------------------------------------------------
# F1: serial, a suite that fails then passes is rerun once, reported FLAKY, listed in the summary, and the run exits 0
# ---------------------------------------------------------------------------

test_start "F1 serial: a suite that fails then passes is rerun once: FLAKY line, no plain pass line, listed in the summary, RC 0"
new_fixture f1s || exit 1
typeset FIX1S="${SCRATCH}/f1s"
count_suite "${FIX1S}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
run_par "${FIX1S}" VDE_TEST_JOBS=1
SER_OUT="${OUT}"
flaky_findings "${FIX1S}/state" fl-flaky.test.zsh
if [[ -z "${FWHY}" ]]; then
    test_pass "F1 serial: FLAKY line, 2 runs, RC 0, summary lists it with first run exit code 7"
else
    test_fail "F1 serial: fail-then-pass is FLAKY, runs twice, RC 0" "${FWHY# }"
fi

# ---------------------------------------------------------------------------
# F2: pool (VDE_TEST_JOBS=3, two always-pass suites alongside), the same result as F1
# ---------------------------------------------------------------------------

test_start "F2 pool (VDE_TEST_JOBS=3, two passing suites alongside): fail-then-pass is FLAKY, the passing suites pass once, RC 0"
new_fixture f2p || exit 1
typeset FIX2P="${SCRATCH}/f2p"
count_suite "${FIX2P}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
count_suite "${FIX2P}/tests/unit/ok-a.test.zsh" 0 0 || exit 1
count_suite "${FIX2P}/tests/unit/ok-b.test.zsh" 0 0 || exit 1
run_par "${FIX2P}" VDE_TEST_JOBS=3
POOL_OUT="${OUT}"
flaky_findings "${FIX2P}/state" fl-flaky.test.zsh
typeset WHY2="${FWHY}"
for s in ok-a.test.zsh ok-b.test.zsh; do
    run_count "${FIX2P}/state" "${s}"
    (( RUNS == 1 )) || WHY2+=" ${s} runs=${RUNS}(want 1)"
    has_line "${s} passed (" || WHY2+=" no plain 'passed (' line for ${s}"
done
if [[ -z "${WHY2// /}" ]]; then
    test_pass "F2 pool: FLAKY line, 2 runs, RC 0, summary lists it; the two passing suites ran once each"
else
    test_fail "F2 pool: fail-then-pass is FLAKY, runs twice, RC 0; passing suites run once" "${WHY2# }"
fi

# ---------------------------------------------------------------------------
# F3: serial and pool, a suite that fails on the run and on the rerun: rerun once, RC 1, Failed Suites lists it
# ---------------------------------------------------------------------------

test_start "F3 serial and pool: a suite that fails on the run and on the rerun is run twice, RC 1, listed under Failed Suites"
new_fixture f3s || exit 1
typeset FIX3S="${SCRATCH}/f3s"
count_suite "${FIX3S}/tests/unit/ft-twice.test.zsh" 3 3 || exit 1
run_par "${FIX3S}" VDE_TEST_JOBS=1
twice_findings "${FIX3S}/state" ft-twice.test.zsh
typeset WHY3=''
[[ -n "${FWHY}" ]] && WHY3+=" serial:[${FWHY# }]"
new_fixture f3p || exit 1
typeset FIX3P="${SCRATCH}/f3p"
count_suite "${FIX3P}/tests/unit/ft-twice.test.zsh" 3 3 || exit 1
count_suite "${FIX3P}/tests/unit/ok-a.test.zsh" 0 0 || exit 1
run_par "${FIX3P}" VDE_TEST_JOBS=3
twice_findings "${FIX3P}/state" ft-twice.test.zsh
[[ -n "${FWHY}" ]] && WHY3+=" pool:[${FWHY# }]"
if [[ -z "${WHY3}" ]]; then
    test_pass "F3 serial and pool: failed again on the rerun, 2 runs, RC 1, listed under Failed Suites"
else
    test_fail "F3 failure on the rerun is a real failure in both modes" "${WHY3# }"
fi

# ---------------------------------------------------------------------------
# F4: a passing suite is executed exactly once, in both modes, and nothing is FLAKY
# ---------------------------------------------------------------------------

test_start "F4 serial and pool: a passing suite is executed exactly once, RC 0, no FLAKY anywhere"
new_fixture f4s || exit 1
typeset FIX4S="${SCRATCH}/f4s"
count_suite "${FIX4S}/tests/unit/ok-once.test.zsh" 0 0 || exit 1
run_par "${FIX4S}" VDE_TEST_JOBS=1
typeset WHY4=''
[[ "${RC}" == 0 ]] || WHY4+=" serial rc=${RC}(want 0)"
once_findings "${FIX4S}/state" ok-once.test.zsh
[[ -n "${FWHY}" ]] && WHY4+=" serial:[${FWHY# }]"
new_fixture f4p || exit 1
typeset FIX4P="${SCRATCH}/f4p"
count_suite "${FIX4P}/tests/unit/ok-a.test.zsh" 0 0 || exit 1
count_suite "${FIX4P}/tests/unit/ok-b.test.zsh" 0 0 || exit 1
run_par "${FIX4P}" VDE_TEST_JOBS=3
[[ "${RC}" == 0 ]] || WHY4+=" pool rc=${RC}(want 0)"
for s in ok-a.test.zsh ok-b.test.zsh; do
    once_findings "${FIX4P}/state" "${s}"
    [[ -n "${FWHY}" ]] && WHY4+=" pool:[${FWHY# }]"
done
if [[ -z "${WHY4}" ]]; then
    test_pass "F4 serial and pool: every passing suite ran once, RC 0, no FLAKY"
else
    test_fail "F4 a passing suite runs once and nothing is FLAKY, in both modes" "${WHY4# }"
fi

# ---------------------------------------------------------------------------
# F5: VDE_FLAKE_RERUN=0 turns the rerun off: a failing suite runs once, RC 1, no rerun text (serial and pool)
# ---------------------------------------------------------------------------

test_start "F5 VDE_FLAKE_RERUN=0 (serial and pool): a failing suite runs once, RC 1, no rerun text"
new_fixture f5s || exit 1
typeset FIX5S="${SCRATCH}/f5s"
count_suite "${FIX5S}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
run_par "${FIX5S}" VDE_TEST_JOBS=1 VDE_FLAKE_RERUN=0
typeset WHY5=''
off_findings "${FIX5S}/state" fl-flaky.test.zsh
[[ -n "${FWHY}" ]] && WHY5+=" serial:[${FWHY# }]"
new_fixture f5p || exit 1
typeset FIX5P="${SCRATCH}/f5p"
count_suite "${FIX5P}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
count_suite "${FIX5P}/tests/unit/ok-a.test.zsh" 0 0 || exit 1
run_par "${FIX5P}" VDE_TEST_JOBS=3 VDE_FLAKE_RERUN=0
off_findings "${FIX5P}/state" fl-flaky.test.zsh
[[ -n "${FWHY}" ]] && WHY5+=" pool:[${FWHY# }]"
if [[ -z "${WHY5}" ]]; then
    test_pass "F5 VDE_FLAKE_RERUN=0 in both modes: one run, RC 1, no rerun text"
else
    test_fail "F5 VDE_FLAKE_RERUN=0 disables the rerun in both modes" "${WHY5# }"
fi

# ---------------------------------------------------------------------------
# F6: VDE_FLAKE_RERUN=2 exits 2 with the error line before any suite runs; the empty string is unset (rerun on)
# ---------------------------------------------------------------------------

test_start "F6 VDE_FLAKE_RERUN=2 exits 2 with the error line and no suite runs; VDE_FLAKE_RERUN= (empty) is unset, so the rerun is on"
new_fixture f6a || exit 1
typeset FIX6A="${SCRATCH}/f6a"
count_suite "${FIX6A}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
run_par "${FIX6A}" VDE_TEST_JOBS=1 VDE_FLAKE_RERUN=2
typeset WHY6=''
[[ "${RC}" == 2 ]] || WHY6+=" value 2: rc=${RC}(want 2)"
has_line "ERROR: VDE_FLAKE_RERUN must be 0 or 1, not '2'" || WHY6+=" value 2: no error line"
typeset -a RCF6A=( "${FIX6A}/state"/run-count.*(N) )
(( ${#RCF6A} == 0 )) || WHY6+=" value 2: a suite ran (${#RCF6A} counter files)"
has_line 'Running:' && WHY6+=" value 2: a suite was announced"
new_fixture f6b || exit 1
typeset FIX6B="${SCRATCH}/f6b"
count_suite "${FIX6B}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
run_par "${FIX6B}" VDE_TEST_JOBS=1 VDE_FLAKE_RERUN=
flaky_findings "${FIX6B}/state" fl-flaky.test.zsh
[[ -n "${FWHY}" ]] && WHY6+=" empty value:[${FWHY# }]"
if [[ -z "${WHY6}" ]]; then
    test_pass "F6 value 2: exit 2, error line, no suite ran; empty value: unset, rerun on (FLAKY, 2 runs, RC 0)"
else
    test_fail "F6 VDE_FLAKE_RERUN=2 exits 2 before any suite; empty runs with the rerun on" "${WHY6# }"
fi

# ---------------------------------------------------------------------------
# F7: SUITE TIMING has the original row and a '<suite>[rerun]' row for a rerun, serial and pool, each with a seconds value
# ---------------------------------------------------------------------------

test_start "F7 SUITE TIMING has rows for fl-flaky.test.zsh and fl-flaky.test.zsh[rerun], serial and pool, each with a seconds value"
typeset WHY7=''
typeset -a MODES7=( serial pool )
typeset m7 text7 row7
for m7 in "${MODES7[@]}"; do
    if [[ "${m7}" == serial ]]; then text7="${SER_OUT}"; else text7="${POOL_OUT}"; fi
    for row7 in 'fl-flaky.test.zsh' 'fl-flaky.test.zsh[rerun]'; do
        timing_seconds "${text7}" "${row7}"
        [[ "${TSECS}" == <->.<->s ]] || WHY7+=" ${m7} ${row7}=${TSECS}"
    done
done
if [[ -z "${WHY7}" ]]; then
    test_pass "F7 both rows present in serial and pool, each with a seconds value"
else
    test_fail "F7 SUITE TIMING has the original and the [rerun] row, serial and pool" "${WHY7# }"
fi

# ---------------------------------------------------------------------------
# F8: the same results under a decimal-comma locale (en_DK.utf8), and the timing row keeps its dot
# ---------------------------------------------------------------------------

typeset LOC_PROBE=''
LOC_PROBE="$(LC_ALL=en_DK.utf8 zsh -c 'printf "%.1f" 1.5' 2>/dev/null)"
if [[ "${LOC_PROBE}" != '1,5' ]]; then
    print -r -- "[SKIP] F8: no decimal-comma locale (en_DK.utf8) on this host; install the locales package and run locale-gen. F8 did not run and is not counted."
else
    test_start "F8 LC_ALL=en_DK.utf8 (serial and pool): F1's results hold, the [rerun] timing row keeps a dot, no comma in SUITE TIMING"
    typeset WHY8=''
    new_fixture f8s || exit 1
    typeset FIX8S="${SCRATCH}/f8s"
    count_suite "${FIX8S}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
    run_par "${FIX8S}" VDE_TEST_JOBS=1 LC_ALL=en_DK.utf8
    typeset TXT8S="${OUT}"
    flaky_findings "${FIX8S}/state" fl-flaky.test.zsh
    [[ -n "${FWHY}" ]] && WHY8+=" serial:[${FWHY# }]"
    timing_seconds "${TXT8S}" 'fl-flaky.test.zsh[rerun]'
    [[ "${TSECS}" == <->.<->s ]] || WHY8+=" serial [rerun] seconds=${TSECS}"
    timing_has_comma "${TXT8S}" && WHY8+=" serial: a comma in SUITE TIMING"
    new_fixture f8p || exit 1
    typeset FIX8P="${SCRATCH}/f8p"
    count_suite "${FIX8P}/tests/unit/fl-flaky.test.zsh" 7 0 || exit 1
    count_suite "${FIX8P}/tests/unit/ok-a.test.zsh" 0 0 || exit 1
    run_par "${FIX8P}" VDE_TEST_JOBS=3 LC_ALL=en_DK.utf8
    typeset TXT8P="${OUT}"
    flaky_findings "${FIX8P}/state" fl-flaky.test.zsh
    [[ -n "${FWHY}" ]] && WHY8+=" pool:[${FWHY# }]"
    timing_seconds "${TXT8P}" 'fl-flaky.test.zsh[rerun]'
    [[ "${TSECS}" == <->.<->s ]] || WHY8+=" pool [rerun] seconds=${TSECS}"
    timing_has_comma "${TXT8P}" && WHY8+=" pool: a comma in SUITE TIMING"
    if [[ -z "${WHY8}" ]]; then
        test_pass "F8 en_DK.utf8 in both modes: FLAKY results hold, [rerun] seconds has a dot, no comma in SUITE TIMING"
    else
        test_fail "F8 under LC_ALL=en_DK.utf8 the results and the dot-decimal timing hold" "${WHY8# }"
    fi
fi

# ---------------------------------------------------------------------------
# F9: the real runner declares VDE_FLAKE_RERUN_DEFAULT=1 exactly once, at column 1
# ---------------------------------------------------------------------------

test_start "F9 the real runner declares VDE_FLAKE_RERUN_DEFAULT=1 exactly once"
typeset -a RUNNER_LINES=( "${(@f)$(<"${RUNNER_SRC}")}" )
typeset -i decl9=0 exact9=0
typeset ln9
for ln9 in "${RUNNER_LINES[@]}"; do
    [[ "${ln9}" == *'VDE_FLAKE_RERUN_DEFAULT=1'* ]] && decl9+=1
    [[ "${ln9}" == 'typeset -ri VDE_FLAKE_RERUN_DEFAULT=1' ]] && exact9+=1
done
if (( decl9 == 1 && exact9 == 1 )); then
    test_pass "F9 the runner declares typeset -ri VDE_FLAKE_RERUN_DEFAULT=1 exactly once"
else
    test_fail "F9 VDE_FLAKE_RERUN_DEFAULT=1 declared exactly once" "lines mentioning it: ${decl9}, exact declaration lines: ${exact9}"
fi

print -r -- "Passed: ${TESTS_PASSED}  Failed: ${TESTS_FAILED}"
(( TESTS_FAILED == 0 )) || exit 1
exit 0
